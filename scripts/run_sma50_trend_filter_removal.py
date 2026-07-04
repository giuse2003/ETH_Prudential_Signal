"""
Valida se rimuovere dalla Baseline la condizione di ingresso SMA50 > SMA200.

Questo script e' solo di ricerca: non modifica i segnali ufficiali.
Confronta:
- Baseline ufficiale corrente;
- variante senza condizione `SMA50 > SMA200` in ingresso.

Le performance principali sono misurate in EUR tramite Close_EUR, come negli
altri report di validazione del progetto.
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
from strategy.signals import (
    ENTRY_RSI_MAX,
    TRAILING_MOMENTUM_MIN,
    TRAILING_STOP_PCT,
    TRAILING_VOLUME_REL_MIN,
)


SOURCE_CSV = PROJECT_ROOT / "data" / "indicators_with_signals.csv"
OUT_SUMMARY_CSV = PROJECT_ROOT / "reports" / "sma50_trend_filter_removal_summary.csv"
OUT_YEARS_CSV = PROJECT_ROOT / "reports" / "sma50_trend_filter_removal_years.csv"
OUT_COSTS_CSV = PROJECT_ROOT / "reports" / "sma50_trend_filter_removal_costs.csv"
OUT_EVENTS_CSV = PROJECT_ROOT / "reports" / "sma50_trend_filter_removal_events.csv"
OUT_MD = PROJECT_ROOT / "reports" / "sma50_trend_filter_removal.md"

RECENT_START = "2022-01-01"
COST_SCENARIOS = [
    ("lordo_0_00pct", 0.0),
    ("costo_0_10pct", 0.001),
    ("costo_0_25pct", 0.0025),
    ("stress_0_50pct", 0.005),
    ("stress_1_00pct", 0.01),
]


def _baseline_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()


def _without_sma50_filter_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    exposure = False
    peak_close: float | None = None
    signals: list[str] = []
    events: list[dict[str, float | str | bool | None]] = []

    for date, row in df.iterrows():
        close = float(row["Close"])
        close_eur = float(row["Close_EUR"])
        sma50 = float(row["SMA50"])
        sma200 = float(row["SMA200"])
        rsi = float(row["RSI"])
        volume = float(row["Volume"])
        volume_avg20 = float(row["VolumeAvg20"])
        close_7d_ago = float(row[f"Close_{CFG.momentum_days}d_ago"])

        official_buy_without_sma50 = (
            close > sma200
            and rsi >= 40.0
            and close > close_7d_ago
            and volume > volume_avg20
        )
        filtered_new_entry_without_sma50 = official_buy_without_sma50 and rsi <= ENTRY_RSI_MAX
        official_sell = close < sma50

        signal = "MANTIENI"
        trail_stop_hit = False
        trail_confirmed = False

        if official_sell:
            signal = "VENDI"
            if exposure:
                events.append(
                    _event_row(
                        date=date,
                        row=row,
                        event_type="sell_below_sma50",
                        was_exposed=True,
                    )
                )
            exposure = False
            peak_close = None
            signals.append(signal)
            continue

        if official_buy_without_sma50:
            if not exposure and filtered_new_entry_without_sma50:
                signal = "ACQUISTA"
                exposure = True
                peak_close = close
                events.append(
                    _event_row(
                        date=date,
                        row=row,
                        event_type="new_entry_without_sma50_filter",
                        was_exposed=False,
                    )
                )
            elif exposure:
                peak_close = max(peak_close if peak_close is not None else close, close)
            signals.append(signal)
            continue

        if exposure:
            peak_close = max(peak_close if peak_close is not None else close, close)
            trail_stop_hit = close <= peak_close * (1.0 - TRAILING_STOP_PCT)
            if trail_stop_hit:
                momentum_7d = close / close_7d_ago - 1.0 if close_7d_ago else float("nan")
                volume_rel = volume / volume_avg20 - 1.0 if volume_avg20 else float("nan")
                trail_confirmed = (
                    pd.notna(momentum_7d)
                    and pd.notna(volume_rel)
                    and momentum_7d >= TRAILING_MOMENTUM_MIN
                    and volume_rel >= TRAILING_VOLUME_REL_MIN
                )

        if trail_confirmed:
            signal = "VENDI"
            events.append(
                _event_row(
                    date=date,
                    row=row,
                    event_type="trail8_confirmed",
                    was_exposed=True,
                    trail_peak_close=peak_close,
                )
            )
            exposure = False
            peak_close = None

        signals.append(signal)

    out = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    out["Segnale"] = signals
    return out, pd.DataFrame(events)


def _event_row(
    *,
    date: pd.Timestamp,
    row: pd.Series,
    event_type: str,
    was_exposed: bool,
    trail_peak_close: float | None = None,
) -> dict[str, float | str | bool | None]:
    close = float(row["Close"])
    return {
        "date": date.date().isoformat(),
        "event_type": event_type,
        "was_exposed": was_exposed,
        "close_usd": close,
        "close_eur": float(row["Close_EUR"]),
        "sma50": float(row["SMA50"]),
        "sma200": float(row["SMA200"]),
        "sma50_gt_sma200": bool(float(row["SMA50"]) > float(row["SMA200"])),
        "rsi": float(row["RSI"]),
        "momentum_7d_pct": close / float(row[f"Close_{CFG.momentum_days}d_ago"]) - 1.0,
        "volume_rel_pct": float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0,
        "trail_peak_close": trail_peak_close,
        "drawdown_from_peak_pct": close / trail_peak_close - 1.0 if trail_peak_close else None,
    }


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


def _yearly(base: pd.DataFrame, variant: pd.DataFrame) -> pd.DataFrame:
    base_eq, _, _ = run_backtest(base)
    variant_eq, _, _ = run_backtest(variant)
    rows: list[dict[str, float | int]] = []
    for year in sorted(base.index.year.unique()):
        bm = _slice_metrics(base_eq, f"{year}-01-01", f"{year}-12-31")
        vm = _slice_metrics(variant_eq, f"{year}-01-01", f"{year}-12-31")
        rows.append(
            {
                "year": int(year),
                "baseline_return": bm["total_return"],
                "no_sma50_filter_return": vm["total_return"],
                "delta_return": vm["total_return"] - bm["total_return"],
                "baseline_max_drawdown": bm["max_drawdown"],
                "no_sma50_filter_max_drawdown": vm["max_drawdown"],
                "delta_max_drawdown": vm["max_drawdown"] - bm["max_drawdown"],
                "baseline_sharpe": bm["sharpe_ratio"],
                "no_sma50_filter_sharpe": vm["sharpe_ratio"],
                "delta_sharpe": vm["sharpe_ratio"] - bm["sharpe_ratio"],
                "baseline_exposure_ratio": bm["exposure_ratio"],
                "no_sma50_filter_exposure_ratio": vm["exposure_ratio"],
            }
        )
    return pd.DataFrame(rows)


def _summary(base: pd.DataFrame, variant: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for name, frame in [
        ("baseline", base),
        ("no_sma50_gt_sma200_entry", variant),
    ]:
        equity, metrics, _ = run_backtest(frame)
        recent = _slice_metrics(equity, RECENT_START)
        rows.append(
            {
                "variant": name,
                "annualized_return": metrics.annualized_return,
                "max_drawdown": metrics.max_drawdown,
                "sharpe_ratio": metrics.sharpe_ratio,
                "profit_factor": metrics.profit_factor,
                "num_operations": metrics.num_operations,
                "win_rate": metrics.win_rate,
                "exposure_ratio": metrics.exposure_ratio,
                "turnover": metrics.turnover,
                "recent_annualized_return": recent["annualized_return"],
                "recent_max_drawdown": recent["max_drawdown"],
                "recent_sharpe_ratio": recent["sharpe_ratio"],
                "recent_exposure_ratio": recent["exposure_ratio"],
                "new_entries_without_sma50_gate": int(
                    (events["event_type"] == "new_entry_without_sma50_filter").sum()
                )
                if not events.empty
                else 0,
            }
        )
    return pd.DataFrame(rows)


def _costs(base: pd.DataFrame, variant: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for scenario, cost in COST_SCENARIOS:
        _, bm, _ = run_backtest(base, transaction_cost_rate=cost)
        _, vm, _ = run_backtest(variant, transaction_cost_rate=cost)
        for model, metrics in [
            ("baseline", bm),
            ("no_sma50_gt_sma200_entry", vm),
        ]:
            rows.append(
                {
                    "scenario": scenario,
                    "cost_rate": cost,
                    "variant": model,
                    "annualized_return": metrics.annualized_return,
                    "max_drawdown": metrics.max_drawdown,
                    "sharpe_ratio": metrics.sharpe_ratio,
                    "profit_factor": metrics.profit_factor,
                    "num_operations": metrics.num_operations,
                    "win_rate": metrics.win_rate,
                    "turnover": metrics.turnover,
                }
            )
        rows.append(
            {
                "scenario": scenario,
                "cost_rate": cost,
                "variant": "delta_no_sma50_minus_baseline",
                "annualized_return": vm.annualized_return - bm.annualized_return,
                "max_drawdown": vm.max_drawdown - bm.max_drawdown,
                "sharpe_ratio": vm.sharpe_ratio - bm.sharpe_ratio,
                "profit_factor": vm.profit_factor - bm.profit_factor,
                "num_operations": vm.num_operations - bm.num_operations,
                "win_rate": vm.win_rate - bm.win_rate,
                "turnover": vm.turnover - bm.turnover,
            }
        )
    return pd.DataFrame(rows)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(
    summary: pd.DataFrame,
    years: pd.DataFrame,
    costs: pd.DataFrame,
    events: pd.DataFrame,
    out_path: Path,
    start: str,
    end: str,
) -> None:
    base = summary[summary["variant"] == "baseline"].iloc[0]
    variant = summary[summary["variant"] == "no_sma50_gt_sma200_entry"].iloc[0]
    delta_costs = costs[costs["variant"] == "delta_no_sma50_minus_baseline"]
    better_years = years[years["delta_return"] > 1e-8]
    worse_years = years[years["delta_return"] < -1e-8]
    extra_entries = events[events["event_type"] == "new_entry_without_sma50_filter"] if not events.empty else pd.DataFrame()
    extra_entries_with_gate_false = (
        extra_entries[~extra_entries["sma50_gt_sma200"]]
        if not extra_entries.empty
        else pd.DataFrame()
    )

    lines = [
        "# SMA50 Trend Filter Removal",
        "",
        "Test di ricerca: rimozione della condizione `SMA50 > SMA200` dalla Baseline.",
        "",
        f"Periodo: `{start}` -> `{end}`.",
        "",
        "Variante testata:",
        "",
        "- ingresso senza `SMA50 > SMA200`;",
        "- invariati `Close > SMA200`, `RSI >= 40`, `RSI <= 65` sui nuovi ingressi,",
        "  momentum 7 giorni positivo e volume sopra media 20 giorni;",
        "- uscite invariate: `Close < SMA50` e Trail8 confermato.",
        "",
        "## Periodo Completo",
        "",
        "| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Win rate | Esposizione |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{_pct(row['win_rate'])} | "
            f"{_pct(row['exposure_ratio'])} |"
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
    for _, row in summary.iterrows():
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
            "## Stress Costi",
            "",
            "| Scenario | Delta Ann. | Delta DD | Delta Sharpe | Delta PF | Delta Ops |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in delta_costs.iterrows():
        lines.append(
            "| "
            f"{row['scenario']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} |"
        )

    lines.extend(
        [
            "",
            "## Validazione Annuale",
            "",
            "| Anno | Baseline Ret | Senza SMA50 Ret | Delta Ret | Baseline DD | Senza SMA50 DD | Delta Sharpe |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in years.iterrows():
        lines.append(
            "| "
            f"{int(row['year'])} | "
            f"{_pct(row['baseline_return'])} | "
            f"{_pct(row['no_sma50_filter_return'])} | "
            f"{_pct(row['delta_return'])} | "
            f"{_pct(row['baseline_max_drawdown'])} | "
            f"{_pct(row['no_sma50_filter_max_drawdown'])} | "
            f"{_ratio(row['delta_sharpe'])} |"
        )

    lines.extend(
        [
            "",
            "## Eventi",
            "",
            f"- Nuovi ingressi della variante: {len(extra_entries)}.",
            f"- Nuovi ingressi che la Baseline bloccava per `SMA50 <= SMA200`: {len(extra_entries_with_gate_false)}.",
            "",
            "| Data | Close EUR | SMA50>SMA200 | RSI | Mom 7g | Volume rel |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    if extra_entries.empty:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a |")
    else:
        for _, row in extra_entries.head(30).iterrows():
            lines.append(
                "| "
                f"{row['date']} | "
                f"{float(row['close_eur']):.2f} | "
                f"{row['sma50_gt_sma200']} | "
                f"{float(row['rsi']):.2f} | "
                f"{_pct(row['momentum_7d_pct'])} | "
                f"{_pct(row['volume_rel_pct'])} |"
            )
        if len(extra_entries) > 30:
            lines.append(f"| ... | altri {len(extra_entries) - 30} eventi |  |  |  |  |")

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Delta annualizzato lordo: {_pct(variant['annualized_return'] - base['annualized_return'])}.",
            f"- Delta max drawdown lordo: {_pct(variant['max_drawdown'] - base['max_drawdown'])}.",
            f"- Delta Sharpe lordo: {_ratio(variant['sharpe_ratio'] - base['sharpe_ratio'])}.",
            f"- Anni migliorati per rendimento: {len(better_years)}.",
            f"- Anni peggiorati per rendimento: {len(worse_years)}.",
            "- La condizione va rimossa solo se migliora rendimento/rischio senza peggiorare la stabilita' annuale.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    df = df.dropna(subset=["Close_EUR", "SMA50", "SMA200", "RSI", "VolumeAvg20", f"Close_{CFG.momentum_days}d_ago"]).copy()

    base = _baseline_frame(df)
    variant, events = _without_sma50_filter_frame(df)
    summary = _summary(base, variant, events)
    years = _yearly(base, variant)
    costs = _costs(base, variant)

    OUT_SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY_CSV, index=False)
    years.to_csv(OUT_YEARS_CSV, index=False)
    costs.to_csv(OUT_COSTS_CSV, index=False)
    events.to_csv(OUT_EVENTS_CSV, index=False)
    _write_markdown(
        summary,
        years,
        costs,
        events,
        OUT_MD,
        df.index[0].date().isoformat(),
        df.index[-1].date().isoformat(),
    )

    print(f"Saved {OUT_SUMMARY_CSV}")
    print(f"Saved {OUT_YEARS_CSV}")
    print(f"Saved {OUT_COSTS_CSV}")
    print(f"Saved {OUT_EVENTS_CSV}")
    print(f"Saved {OUT_MD}")
    print("")
    print(summary.to_string(index=False))
    print("")
    print(costs[costs["variant"] == "delta_no_sma50_minus_baseline"].to_string(index=False))
    print("")
    print(years[["year", "delta_return", "delta_max_drawdown", "delta_sharpe"]].to_string(index=False))


if __name__ == "__main__":
    main()
