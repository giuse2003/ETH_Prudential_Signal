"""
Confronto diretto tra i migliori candidati sperimentali.

Questo script non modifica i segnali ufficiali. Confronta:
- Baseline ufficiale;
- RSI65 + trailing 8% confermato mom -5 / vol +20;
- RSI62 + trailing 8% confermato mom -6 / vol +20;
- RSI65 + trailing 8% confermato mom -6 / vol +20.

Le performance sono misurate in EUR tramite Close_EUR.
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
OUT_SUMMARY_CSV = PROJECT_ROOT / "reports" / "top_candidate_comparison.csv"
OUT_EVENTS_CSV = PROJECT_ROOT / "reports" / "top_candidate_events.csv"
OUT_PERIODS_CSV = PROJECT_ROOT / "reports" / "top_candidate_periods.csv"
OUT_COSTS_CSV = PROJECT_ROOT / "reports" / "top_candidate_costs.csv"
OUT_MD = PROJECT_ROOT / "reports" / "top_candidate_comparison.md"

STOP_PCT = 0.08
RECENT_START = "2022-01-01"

COST_RATES = {
    "gross_0_00pct": 0.0,
    "cost_0_10pct": 0.001,
    "cost_0_25pct": 0.0025,
    "stress_0_50pct": 0.005,
}

PERIODS = {
    "2017-2020": ("2017-11-11", "2020-12-31"),
    "2021-2022": ("2021-01-01", "2022-12-31"),
    "2023-2026": ("2023-01-01", "2026-06-27"),
    "2025-2026": ("2025-01-01", "2026-06-27"),
}

CANDIDATES = {
    "baseline": {"rsi_max": None, "momentum_min": None, "volume_rel_min": None},
    "rsi65_mom-5_vol20": {"rsi_max": 65.0, "momentum_min": -0.05, "volume_rel_min": 0.20},
    "rsi62_mom-6_vol20": {"rsi_max": 62.0, "momentum_min": -0.06, "volume_rel_min": 0.20},
    "rsi65_mom-6_vol20": {"rsi_max": 65.0, "momentum_min": -0.06, "volume_rel_min": 0.20},
}


def _make_frame(df: pd.DataFrame, *, rsi_max: float | None, momentum_min: float | None, volume_rel_min: float | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    exposure = 0.0
    peak_close: float | None = None
    signals: list[str] = []
    events: list[dict[str, float | str | bool | None]] = []
    entry_date: pd.Timestamp | None = None
    entry_price_eur: float | None = None

    for date, row in df.iterrows():
        official = str(row["Segnale"])
        signal = official
        close = float(row["Close"])
        close_eur = float(row["Close_EUR"])

        if signal == "ACQUISTA" and rsi_max is not None and float(row["RSI"]) > rsi_max:
            events.append(
                {
                    "event_type": "blocked_entry",
                    "date": date.date().isoformat(),
                    "close_eur": close_eur,
                    "rsi": float(row["RSI"]),
                    "distance_sma200_pct": close / float(row["SMA200"]) - 1.0,
                    "momentum_7d_pct": close / float(row["Close_7d_ago"]) - 1.0,
                    "volume_rel_pct": float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0,
                    "was_already_exposed": exposure > 0.0,
                }
            )
            signal = "MANTIENI"

        if signal == "ACQUISTA":
            if exposure <= 0.0:
                entry_date = date
                entry_price_eur = close_eur
            exposure = 1.0
            peak_close = close if peak_close is None else max(peak_close, close)
        elif signal == "VENDI":
            exposure = 0.0
            peak_close = None
            entry_date = None
            entry_price_eur = None
        elif exposure > 0.0 and peak_close is not None and momentum_min is not None and volume_rel_min is not None:
            peak_close = max(peak_close, close)
            stop_level = peak_close * (1.0 - STOP_PCT)
            if close <= stop_level:
                momentum_7d = close / float(row["Close_7d_ago"]) - 1.0
                volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
                if momentum_7d >= momentum_min and volume_rel >= volume_rel_min:
                    future = df.loc[df.index > date]
                    official_sells = future[future["Segnale"] == "VENDI"]
                    next_sell_date = official_sells.index[0] if not official_sells.empty else pd.NaT
                    next_sell_close_eur = float(official_sells.iloc[0]["Close_EUR"]) if not official_sells.empty else float("nan")
                    events.append(
                        {
                            "event_type": "trailing_exit",
                            "date": date.date().isoformat(),
                            "close_eur": close_eur,
                            "rsi": float(row["RSI"]),
                            "distance_sma200_pct": close / float(row["SMA200"]) - 1.0,
                            "momentum_7d_pct": momentum_7d,
                            "volume_rel_pct": volume_rel,
                            "was_already_exposed": True,
                            "entry_date": entry_date.date().isoformat() if entry_date is not None else None,
                            "entry_price_eur": entry_price_eur,
                            "return_from_entry_pct": close_eur / entry_price_eur - 1.0 if entry_price_eur else float("nan"),
                            "drawdown_from_peak_pct": close / peak_close - 1.0,
                            "next_official_sell_date": next_sell_date.date().isoformat() if not pd.isna(next_sell_date) else None,
                            "next_official_sell_close_eur": next_sell_close_eur,
                            "next_official_sell_delta_pct": next_sell_close_eur / close_eur - 1.0 if not pd.isna(next_sell_close_eur) else float("nan"),
                        }
                    )
                    signal = "VENDI"
                    exposure = 0.0
                    peak_close = None
                    entry_date = None
                    entry_price_eur = None

        signals.append(signal)

    frame = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    frame["Segnale"] = signals
    return frame, pd.DataFrame(events)


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


def _slice_metrics(equity: pd.DataFrame, start: str, end: str | None = None) -> dict[str, float]:
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
    n_days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    return {
        "total_return": total_return,
        "annualized_return": float((1.0 + total_return) ** (CFG.periods_per_year / n_days) - 1.0),
        "max_drawdown": _max_drawdown(normalized),
        "sharpe_ratio": _sharpe(returns),
        "exposure_ratio": float(subset["EffectiveExposure"].gt(0.0).mean()),
        "turnover": float(subset["Turnover"].sum()),
    }


def _run(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_rows: list[dict[str, float | int | str]] = []
    event_frames: list[pd.DataFrame] = []
    period_rows: list[dict[str, float | str]] = []
    cost_rows: list[dict[str, float | str]] = []

    for name, spec in CANDIDATES.items():
        frame, events = _make_frame(df, **spec)
        if not events.empty:
            events.insert(0, "variant", name)
            event_frames.append(events)

        equity, metrics, _ = run_backtest(frame)
        recent = _slice_metrics(equity, RECENT_START)
        blocked = events[(events["event_type"] == "blocked_entry") & (~events["was_already_exposed"])] if not events.empty else pd.DataFrame()
        trailing = events[events["event_type"] == "trailing_exit"] if not events.empty else pd.DataFrame()

        summary_rows.append(
            {
                "variant": name,
                "annualized_return": metrics.annualized_return,
                "max_drawdown": metrics.max_drawdown,
                "sharpe_ratio": metrics.sharpe_ratio,
                "profit_factor": metrics.profit_factor,
                "num_operations": metrics.num_operations,
                "win_rate": metrics.win_rate,
                "exposure_ratio": metrics.exposure_ratio,
                "recent_annualized_return": recent["annualized_return"],
                "recent_max_drawdown": recent["max_drawdown"],
                "recent_sharpe_ratio": recent["sharpe_ratio"],
                "recent_exposure_ratio": recent["exposure_ratio"],
                "blocked_new_entries": len(blocked),
                "trailing_exits": len(trailing),
            }
        )

        for period, (start, end) in PERIODS.items():
            period_rows.append({"variant": name, "period": period, **_slice_metrics(equity, start, end)})

        for scenario, cost in COST_RATES.items():
            _, cost_metrics, _ = run_backtest(frame, transaction_cost_rate=cost)
            cost_rows.append(
                {
                    "variant": name,
                    "scenario": scenario,
                    "cost_rate": cost,
                    "annualized_return": cost_metrics.annualized_return,
                    "max_drawdown": cost_metrics.max_drawdown,
                    "sharpe_ratio": cost_metrics.sharpe_ratio,
                    "profit_factor": cost_metrics.profit_factor,
                }
            )

    events_all = pd.concat(event_frames, ignore_index=True) if event_frames else pd.DataFrame()
    return pd.DataFrame(summary_rows), events_all, pd.DataFrame(period_rows), pd.DataFrame(cost_rows)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(summary: pd.DataFrame, events: pd.DataFrame, periods: pd.DataFrame, costs: pd.DataFrame, out_path: Path) -> None:
    ordered = summary.sort_values(["sharpe_ratio", "annualized_return"], ascending=False)
    trailing = events[events["event_type"] == "trailing_exit"].copy() if not events.empty else pd.DataFrame()
    blocked = events[(events["event_type"] == "blocked_entry") & (~events["was_already_exposed"])].copy() if not events.empty else pd.DataFrame()

    lines = [
        "# Top Candidate Comparison",
        "",
        "Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.",
        "",
        "Varianti confrontate:",
        "",
        "- Baseline ufficiale;",
        "- `RSI65 + mom -5 + vol +20`;",
        "- `RSI62 + mom -6 + vol +20`;",
        "- `RSI65 + mom -6 + vol +20`.",
        "",
        "## Periodo Completo",
        "",
        "| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Win rate | Ingressi bloccati | Uscite trail |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in ordered.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{_pct(row['win_rate'])} | "
            f"{int(row['blocked_new_entries'])} | "
            f"{int(row['trailing_exits'])} |"
        )

    lines.extend(
        [
            "",
            "## Periodo 2022-Oggi",
            "",
            "| Variante | Ann. | Max DD | Sharpe | Esposizione |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in ordered.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['recent_annualized_return'])} | "
            f"{_pct(row['recent_max_drawdown'])} | "
            f"{_ratio(row['recent_sharpe_ratio'])} | "
            f"{_pct(row['recent_exposure_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Costi 0,25% E Stress 0,50%",
            "",
            "| Variante | Scenario | Ann. | Max DD | Sharpe | PF |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    cost_focus = costs[costs["scenario"].isin(["cost_0_25pct", "stress_0_50pct"])]
    for _, row in cost_focus.sort_values(["variant", "scenario"]).iterrows():
        lines.append(
            "| "
            f"{row['variant']} | {row['scenario']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} |"
        )

    lines.extend(
        [
            "",
            "## Sottoperiodi",
            "",
            "| Variante | Periodo | Ann. | Max DD | Sharpe |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for _, row in periods.sort_values(["period", "variant"]).iterrows():
        lines.append(
            "| "
            f"{row['variant']} | {row['period']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Uscite Trailing",
            "",
            "| Variante | Data | Entry | Return da entry | DD da picco | VENDI ufficiale successivo | Delta vs VENDI ufficiale |",
            "|---|---|---|---:|---:|---|---:|",
        ]
    )
    if trailing.empty:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
    else:
        for _, row in trailing.sort_values(["variant", "date"]).iterrows():
            lines.append(
                "| "
                f"{row['variant']} | "
                f"{row['date']} | "
                f"{row.get('entry_date')} | "
                f"{_pct(row.get('return_from_entry_pct'))} | "
                f"{_pct(row.get('drawdown_from_peak_pct'))} | "
                f"{row.get('next_official_sell_date')} | "
                f"{_pct(row.get('next_official_sell_delta_pct'))} |"
            )

    lines.extend(
        [
            "",
            "## Nuovi Ingressi Bloccati",
            "",
            "| Variante | Conteggio | Periodi principali |",
            "|---|---:|---|",
        ]
    )
    for variant in [v for v in CANDIDATES if v != "baseline"]:
        rows = blocked[blocked["variant"] == variant]
        dates = rows["date"].to_list()
        if not dates:
            periods_text = "nessuno"
        else:
            periods_text = ", ".join(_compact_date_episodes(dates))
        lines.append(f"| {variant} | {len(rows)} | {periods_text} |")

    best = ordered.iloc[0]
    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Migliore variante per Sharpe: `{best['variant']}` con Sharpe {_ratio(best['sharpe_ratio'])} e max DD {_pct(best['max_drawdown'])}.",
            "- `RSI62 + mom -6 + vol +20` riduce il drawdown piu' del candidato precedente.",
            "- `RSI65 + mom -6 + vol +20` ha metriche quasi identiche al top, ma blocca meno ingressi.",
            "- La scelta finale non va fatta solo sul valore massimo: va preferita la regola piu' stabile e piu' spiegabile sugli eventi.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def _compact_date_episodes(dates: list[str]) -> list[str]:
    parsed = pd.Series(pd.to_datetime(dates)).sort_values().reset_index(drop=True)
    if parsed.empty:
        return []
    groups = (parsed.diff().dt.days.fillna(99) > 1).cumsum()
    episodes: list[str] = []
    for _, group in parsed.groupby(groups):
        start = group.iloc[0].date().isoformat()
        end = group.iloc[-1].date().isoformat()
        episodes.append(start if start == end else f"{start}->{end}")
    return episodes


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    summary, events, periods, costs = _run(df)

    OUT_SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY_CSV, index=False)
    events.to_csv(OUT_EVENTS_CSV, index=False)
    periods.to_csv(OUT_PERIODS_CSV, index=False)
    costs.to_csv(OUT_COSTS_CSV, index=False)
    _write_markdown(summary, events, periods, costs, OUT_MD)

    print(f"Saved {OUT_SUMMARY_CSV}")
    print(f"Saved {OUT_EVENTS_CSV}")
    print(f"Saved {OUT_PERIODS_CSV}")
    print(f"Saved {OUT_COSTS_CSV}")
    print(f"Saved {OUT_MD}")
    print("")
    print(summary.sort_values(["sharpe_ratio", "annualized_return"], ascending=False).to_string(index=False))


if __name__ == "__main__":
    main()
