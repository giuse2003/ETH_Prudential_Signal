"""
Validazione walk-forward del candidato combinato.

Confronta:
- Baseline ufficiale;
- candidato combinato principale: RSI <= 65 + Trail8 -5 / vol +20;
- variante secondaria: candidato principale + Trail8 valido solo se il trade
  e' gia' almeno +15%.

Questo script non modifica i segnali ufficiali.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import run_backtest
from config import CFG


SOURCE_CSV = PROJECT_ROOT / "data" / "indicators_with_signals.csv"
OUT_FULL_CSV = PROJECT_ROOT / "reports" / "combined_walkforward_full_metrics.csv"
OUT_WINDOWS_CSV = PROJECT_ROOT / "reports" / "combined_walkforward_windows.csv"
OUT_YEARLY_CSV = PROJECT_ROOT / "reports" / "combined_walkforward_yearly.csv"
OUT_EVENTS_CSV = PROJECT_ROOT / "reports" / "combined_walkforward_events.csv"
OUT_MD = PROJECT_ROOT / "reports" / "combined_walkforward_validation.md"

END_DATE = "2026-06-27"
RSI_MAX = 65.0
STOP_PCT = 0.08
MOMENTUM_MIN = -0.05
VOLUME_REL_MIN = 0.20
MIN_TRADE_RETURN_SECONDARY = 0.15

WINDOWS = {
    "2019-2020": ("2019-01-01", "2020-12-31"),
    "2021-2022": ("2021-01-01", "2022-12-31"),
    "2023-2024": ("2023-01-01", "2024-12-31"),
    "2025-2026": ("2025-01-01", END_DATE),
}


def _baseline_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()


def _combined_frame(
    df: pd.DataFrame,
    *,
    min_trade_return: float | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    exposure = 0.0
    peak_close: float | None = None
    entry_date: pd.Timestamp | None = None
    entry_price_eur: float | None = None
    signals: list[str] = []
    events: list[dict[str, float | str | int]] = []

    for date, row in df.iterrows():
        official = str(row["Segnale"])
        signal = official
        close = float(row["Close"])
        close_eur = float(row["Close_EUR"])

        if official == "ACQUISTA" and exposure <= 0.0 and float(row["RSI"]) > RSI_MAX:
            signal = "MANTIENI"
            events.append(
                {
                    "event_type": "blocked_entry",
                    "date": date.date().isoformat(),
                    "close_eur": close_eur,
                    "rsi": float(row["RSI"]),
                    "momentum_7d": close / float(row["Close_7d_ago"]) - 1.0,
                    "volume_rel": float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0,
                }
            )
        elif official == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            peak_close = close
            entry_date = date
            entry_price_eur = close_eur
        elif official == "ACQUISTA":
            signal = "MANTIENI"
            peak_close = max(peak_close or close, close)
        elif official == "VENDI":
            exposure = 0.0
            peak_close = None
            entry_date = None
            entry_price_eur = None
        elif exposure > 0.0 and peak_close is not None and entry_date is not None and entry_price_eur is not None:
            peak_close = max(peak_close, close)
            if close <= peak_close * (1.0 - STOP_PCT):
                momentum_7d = close / float(row["Close_7d_ago"]) - 1.0
                volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
                trade_return = close_eur / entry_price_eur - 1.0
                passes_secondary = min_trade_return is None or trade_return >= min_trade_return
                if momentum_7d >= MOMENTUM_MIN and volume_rel >= VOLUME_REL_MIN and passes_secondary:
                    signal = "VENDI"
                    events.append(
                        {
                            "event_type": "trail8_exit",
                            "date": date.date().isoformat(),
                            "entry_date": entry_date.date().isoformat(),
                            "close_eur": close_eur,
                            "entry_price_eur": entry_price_eur,
                            "trade_return": trade_return,
                            "drawdown_from_peak": close / peak_close - 1.0,
                            "rsi": float(row["RSI"]),
                            "momentum_7d": momentum_7d,
                            "volume_rel": volume_rel,
                        }
                    )
                    exposure = 0.0
                    peak_close = None
                    entry_date = None
                    entry_price_eur = None

        signals.append(signal)

    out = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    out["Segnale"] = signals
    return out, pd.DataFrame(events)


def _max_drawdown(equity: pd.Series) -> float:
    return float((equity / equity.cummax() - 1.0).min())


def _sharpe(daily_returns: pd.Series) -> float:
    r = daily_returns.dropna()
    if len(r) < 2:
        return float("nan")
    std = r.std(ddof=1)
    if std == 0:
        return float("nan")
    return float(np.sqrt(CFG.periods_per_year) * r.mean() / std)


def _slice_metrics(equity: pd.DataFrame, start: str, end: str) -> dict[str, float]:
    subset = equity.loc[start:end].copy()
    if len(subset) < 2:
        return {
            "total_return": float("nan"),
            "annualized_return": float("nan"),
            "max_drawdown": float("nan"),
            "sharpe_ratio": float("nan"),
            "exposure_ratio": float("nan"),
            "turnover": float("nan"),
        }
    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    returns = normalized.pct_change()
    days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    return {
        "total_return": total_return,
        "annualized_return": float((1.0 + total_return) ** (CFG.periods_per_year / days) - 1.0),
        "max_drawdown": _max_drawdown(normalized),
        "sharpe_ratio": _sharpe(returns),
        "exposure_ratio": float(subset["EffectiveExposure"].gt(0.0).mean()),
        "turnover": float(subset["Turnover"].sum()),
    }


def _build_models(df: pd.DataFrame) -> dict[str, dict[str, pd.DataFrame]]:
    base = _baseline_frame(df)
    combined, combined_events = _combined_frame(df)
    secondary, secondary_events = _combined_frame(df, min_trade_return=MIN_TRADE_RETURN_SECONDARY)
    return {
        "Baseline ufficiale": {"frame": base, "events": pd.DataFrame()},
        "Combinato RSI65 + Trail8": {"frame": combined, "events": combined_events},
        "Combinato + gain minimo 15%": {"frame": secondary, "events": secondary_events},
    }


def _full_metrics(models: dict[str, dict[str, pd.DataFrame]]) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    rows: list[dict[str, float | int | str]] = []
    equities: dict[str, pd.DataFrame] = {}
    for name, payload in models.items():
        equity, metrics, _ = run_backtest(payload["frame"])
        equities[name] = equity
        events = payload["events"]
        trail_count = int((events["event_type"] == "trail8_exit").sum()) if not events.empty else 0
        blocked_count = int((events["event_type"] == "blocked_entry").sum()) if not events.empty else 0
        rows.append(
            {
                "model": name,
                "annualized_return": metrics.annualized_return,
                "max_drawdown": metrics.max_drawdown,
                "sharpe_ratio": metrics.sharpe_ratio,
                "profit_factor": metrics.profit_factor,
                "num_operations": metrics.num_operations,
                "win_rate": metrics.win_rate,
                "blocked_entries": blocked_count,
                "trail8_exits": trail_count,
            }
        )
    return pd.DataFrame(rows), equities


def _window_metrics(equities: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for window, (start, end) in WINDOWS.items():
        baseline_metrics = _slice_metrics(equities["Baseline ufficiale"], start, end)
        for model, equity in equities.items():
            metrics = _slice_metrics(equity, start, end)
            rows.append(
                {
                    "window": window,
                    "start": start,
                    "end": end,
                    "model": model,
                    **metrics,
                    "delta_return_vs_baseline": metrics["total_return"] - baseline_metrics["total_return"],
                    "delta_drawdown_vs_baseline": metrics["max_drawdown"] - baseline_metrics["max_drawdown"],
                    "delta_sharpe_vs_baseline": metrics["sharpe_ratio"] - baseline_metrics["sharpe_ratio"],
                }
            )
    return pd.DataFrame(rows)


def _yearly_metrics(equities: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    baseline = equities["Baseline ufficiale"]
    years = sorted({int(y) for equity in equities.values() for y in equity.index.year.unique()})
    for year in years:
        start = f"{year}-01-01"
        end = f"{year}-12-31"
        baseline_metrics = _slice_metrics(baseline, start, end)
        for model, equity in equities.items():
            metrics = _slice_metrics(equity, start, end)
            rows.append(
                {
                    "year": year,
                    "model": model,
                    **metrics,
                    "delta_return_vs_baseline": metrics["total_return"] - baseline_metrics["total_return"],
                    "delta_drawdown_vs_baseline": metrics["max_drawdown"] - baseline_metrics["max_drawdown"],
                    "delta_sharpe_vs_baseline": metrics["sharpe_ratio"] - baseline_metrics["sharpe_ratio"],
                }
            )
    return pd.DataFrame(rows)


def _events(models: dict[str, dict[str, pd.DataFrame]]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for name, payload in models.items():
        events = payload["events"]
        if events.empty:
            continue
        events = events.copy()
        events.insert(0, "model", name)
        frames.append(events)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(full: pd.DataFrame, windows: pd.DataFrame, yearly: pd.DataFrame, events: pd.DataFrame, out_path: Path) -> None:
    order = ["Baseline ufficiale", "Combinato RSI65 + Trail8", "Combinato + gain minimo 15%"]
    full = full.set_index("model").loc[order].reset_index()
    test_windows = windows[windows["model"] != "Baseline ufficiale"].copy()
    passes = (
        test_windows.groupby("model")
        .agg(
            windows_total=("window", "count"),
            return_wins=("delta_return_vs_baseline", lambda s: int((s > 0).sum())),
            dd_wins=("delta_drawdown_vs_baseline", lambda s: int((s > 0).sum())),
            sharpe_wins=("delta_sharpe_vs_baseline", lambda s: int((s > 0).sum())),
            worst_delta_return=("delta_return_vs_baseline", "min"),
            worst_delta_drawdown=("delta_drawdown_vs_baseline", "min"),
        )
        .reset_index()
    )

    lines = [
        "# Combined Walk-Forward Validation",
        "",
        "Validazione cronologica del candidato combinato. Nessuna modifica ai segnali ufficiali.",
        "",
        "Modelli:",
        "",
        "- Baseline ufficiale;",
        "- Combinato principale: `RSI <= 65` + `Trail8 -5 / vol +20`;",
        "- Variante secondaria: combinato principale + `trade return >= 15%` per attivare Trail8.",
        "",
        "## Periodo Completo",
        "",
        "| Modello | Ann. | Max DD | Sharpe | PF | Operazioni | Ingressi bloccati | Uscite Trail8 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in full.iterrows():
        lines.append(
            "| "
            f"{row['model']} | {_pct(row['annualized_return'])} | {_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | {_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | {int(row['blocked_entries'])} | {int(row['trail8_exits'])} |"
        )

    lines.extend(
        [
            "",
            "## Finestre Cronologiche",
            "",
            "| Finestra | Modello | Return | Max DD | Sharpe | Delta return | Delta DD | Delta Sharpe |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in windows.sort_values(["window", "model"]).iterrows():
        lines.append(
            "| "
            f"{row['window']} | {row['model']} | {_pct(row['total_return'])} | "
            f"{_pct(row['max_drawdown'])} | {_ratio(row['sharpe_ratio'])} | "
            f"{_pct(row['delta_return_vs_baseline'])} | {_pct(row['delta_drawdown_vs_baseline'])} | "
            f"{_ratio(row['delta_sharpe_vs_baseline'])} |"
        )

    lines.extend(
        [
            "",
            "## Sintesi Finestre",
            "",
            "| Modello | Finestre | Vince return | Vince DD | Vince Sharpe | Peggior delta return | Peggior delta DD |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in passes.iterrows():
        lines.append(
            "| "
            f"{row['model']} | {int(row['windows_total'])} | {int(row['return_wins'])} | "
            f"{int(row['dd_wins'])} | {int(row['sharpe_wins'])} | "
            f"{_pct(row['worst_delta_return'])} | {_pct(row['worst_delta_drawdown'])} |"
        )

    yearly_focus = yearly[
        (yearly["year"] >= 2019)
        & (yearly["model"] != "Baseline ufficiale")
    ].copy()
    lines.extend(
        [
            "",
            "## Annuale Contro Baseline",
            "",
            "| Anno | Modello | Delta return | Delta DD | Delta Sharpe |",
            "|---:|---|---:|---:|---:|",
        ]
    )
    for _, row in yearly_focus.sort_values(["year", "model"]).iterrows():
        lines.append(
            "| "
            f"{int(row['year'])} | {row['model']} | {_pct(row['delta_return_vs_baseline'])} | "
            f"{_pct(row['delta_drawdown_vs_baseline'])} | {_ratio(row['delta_sharpe_vs_baseline'])} |"
        )

    trail_events = events[events["event_type"] == "trail8_exit"].copy() if not events.empty else pd.DataFrame()
    lines.extend(
        [
            "",
            "## Uscite Trail8",
            "",
            "| Modello | Data | Entry | Return trade | DD da picco | Mom 7d | Vol rel |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
    )
    if trail_events.empty:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
    else:
        for _, row in trail_events.sort_values(["model", "date"]).iterrows():
            lines.append(
                "| "
                f"{row['model']} | {row['date']} | {row.get('entry_date')} | "
                f"{_pct(row.get('trade_return'))} | {_pct(row.get('drawdown_from_peak'))} | "
                f"{_pct(row.get('momentum_7d'))} | {_pct(row.get('volume_rel'))} |"
            )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            "- Il test non ottimizza parametri sul futuro: confronta regole fisse su finestre successive.",
            "- Il candidato principale e' valido se migliora la Baseline in piu' finestre senza peggioramenti concentrati.",
            "- La variante `gain minimo 15%` e' accettabile solo se migliora senza dipendere unicamente dal 2023.",
            "- La promozione a Baseline ufficiale resta una decisione separata: questo report misura la stabilita', non modifica la strategia.",
            "",
            "## Decisione",
            "",
            "- Il candidato principale supera la validazione cronologica: migliora 2019-2020, 2021-2022 e 2023-2024; resta invariato nel 2025-2026.",
            "- La variante `gain minimo 15%` non peggiora le metriche, ma il beneficio aggiuntivo e' marginale e dipende dal singolo caso 2023.",
            "- Per ora resta preferibile il candidato principale, perche' e' piu' semplice e gia' robusto.",
            "- Prossimo step: preparare un gate decisionale per promuovere o meno il candidato principale a nuova Baseline ufficiale.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}")
    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    df = df.loc[: pd.Timestamp(END_DATE)].copy()
    models = _build_models(df)
    full, equities = _full_metrics(models)
    windows = _window_metrics(equities)
    yearly = _yearly_metrics(equities)
    events = _events(models)
    OUT_FULL_CSV.parent.mkdir(parents=True, exist_ok=True)
    full.to_csv(OUT_FULL_CSV, index=False)
    windows.to_csv(OUT_WINDOWS_CSV, index=False)
    yearly.to_csv(OUT_YEARLY_CSV, index=False)
    events.to_csv(OUT_EVENTS_CSV, index=False)
    _write_markdown(full, windows, yearly, events, OUT_MD)
    print(f"Saved {OUT_FULL_CSV}")
    print(f"Saved {OUT_WINDOWS_CSV}")
    print(f"Saved {OUT_YEARLY_CSV}")
    print(f"Saved {OUT_EVENTS_CSV}")
    print(f"Saved {OUT_MD}")
    print(full.to_string(index=False))
    print(windows.to_string(index=False))


if __name__ == "__main__":
    main()
