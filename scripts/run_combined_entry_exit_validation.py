"""
Validazione combinata filtro ingresso RSI + uscita trailing confermata.

Questo script non modifica i segnali ufficiali. Applica solo in backtest:
- filtro ingresso RSI <= 65;
- trailing stop 8% su massimo Close post-ingresso;
- conferma uscita con momentum 7g e volume relativo.

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
OUT_SUMMARY_CSV = PROJECT_ROOT / "reports" / "combined_entry_exit_validation.csv"
OUT_PERIODS_CSV = PROJECT_ROOT / "reports" / "combined_entry_exit_periods.csv"
OUT_COSTS_CSV = PROJECT_ROOT / "reports" / "combined_entry_exit_costs.csv"
OUT_MD = PROJECT_ROOT / "reports" / "combined_entry_exit_validation.md"

RECENT_START = "2022-01-01"
STOP_PCT = 0.08
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


VARIANTS = {
    "baseline": {"rsi_max": None, "momentum_min": None, "volume_rel_min": None},
    "rsi_le_65": {"rsi_max": 65.0, "momentum_min": None, "volume_rel_min": None},
    "trail8_mom_-5_vol_10": {"rsi_max": None, "momentum_min": -0.05, "volume_rel_min": 0.10},
    "trail8_mom_-5_vol_20": {"rsi_max": None, "momentum_min": -0.05, "volume_rel_min": 0.20},
    "rsi65_trail8_mom_-5_vol_10": {"rsi_max": 65.0, "momentum_min": -0.05, "volume_rel_min": 0.10},
    "rsi65_trail8_mom_-5_vol_20": {"rsi_max": 65.0, "momentum_min": -0.05, "volume_rel_min": 0.20},
}


def _make_frame(
    df: pd.DataFrame,
    *,
    rsi_max: float | None,
    momentum_min: float | None,
    volume_rel_min: float | None,
) -> tuple[pd.DataFrame, int]:
    exposure = 0.0
    peak_close: float | None = None
    signals: list[str] = []
    confirmed_exits = 0

    for _, row in df.iterrows():
        signal = str(row["Segnale"])
        close = float(row["Close"])

        if signal == "ACQUISTA" and rsi_max is not None and float(row["RSI"]) > rsi_max:
            signal = "MANTIENI"

        if signal == "ACQUISTA":
            exposure = 1.0
            peak_close = close if peak_close is None else max(peak_close, close)
        elif signal == "VENDI":
            exposure = 0.0
            peak_close = None
        elif (
            exposure > 0.0
            and peak_close is not None
            and momentum_min is not None
            and volume_rel_min is not None
        ):
            peak_close = max(peak_close, close)
            if close <= peak_close * (1.0 - STOP_PCT):
                momentum_7d = close / float(row["Close_7d_ago"]) - 1.0
                volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
                if momentum_7d >= momentum_min and volume_rel >= volume_rel_min:
                    signal = "VENDI"
                    exposure = 0.0
                    peak_close = None
                    confirmed_exits += 1

        signals.append(signal)

    out = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    out["Segnale"] = signals
    return out, confirmed_exits


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
    daily_returns = normalized.pct_change()
    n_days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    annualized_return = float((1.0 + total_return) ** (CFG.periods_per_year / n_days) - 1.0)
    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "max_drawdown": _max_drawdown(normalized),
        "sharpe_ratio": _sharpe(daily_returns),
        "exposure_ratio": float(subset["EffectiveExposure"].gt(0.0).mean()),
        "turnover": float(subset["Turnover"].sum()),
    }


def _summary(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, pd.DataFrame]]:
    rows: list[dict[str, float | int | str]] = []
    equities: dict[str, pd.DataFrame] = {}
    frames: dict[str, pd.DataFrame] = {}

    for variant, spec in VARIANTS.items():
        frame, confirmed_exits = _make_frame(df, **spec)
        equity, metrics, _ = run_backtest(frame)
        recent = _slice_metrics(equity, RECENT_START)
        equities[variant] = equity
        frames[variant] = frame
        rows.append(
            {
                "variant": variant,
                "confirmed_exits": confirmed_exits,
                "full_total_return": metrics.total_return,
                "full_annualized_return": metrics.annualized_return,
                "full_max_drawdown": metrics.max_drawdown,
                "full_sharpe_ratio": metrics.sharpe_ratio,
                "full_profit_factor": metrics.profit_factor,
                "full_num_operations": metrics.num_operations,
                "full_win_rate": metrics.win_rate,
                "full_exposure_ratio": metrics.exposure_ratio,
                "full_turnover": metrics.turnover,
                "recent_total_return": recent["total_return"],
                "recent_annualized_return": recent["annualized_return"],
                "recent_max_drawdown": recent["max_drawdown"],
                "recent_sharpe_ratio": recent["sharpe_ratio"],
                "recent_exposure_ratio": recent["exposure_ratio"],
                "recent_turnover": recent["turnover"],
            }
        )

    return pd.DataFrame(rows), equities, frames


def _costs(frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for variant, frame in frames.items():
        for scenario, rate in COST_RATES.items():
            _, metrics, _ = run_backtest(frame, transaction_cost_rate=rate)
            rows.append(
                {
                    "variant": variant,
                    "scenario": scenario,
                    "cost_rate": rate,
                    "annualized_return": metrics.annualized_return,
                    "max_drawdown": metrics.max_drawdown,
                    "sharpe_ratio": metrics.sharpe_ratio,
                    "profit_factor": metrics.profit_factor,
                    "num_operations": metrics.num_operations,
                }
            )
    return pd.DataFrame(rows)


def _periods(equities: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for variant, equity in equities.items():
        for period, (start, end) in PERIODS.items():
            rows.append({"variant": variant, "period": period, **_slice_metrics(equity, start, end)})
    return pd.DataFrame(rows)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(summary: pd.DataFrame, periods: pd.DataFrame, costs: pd.DataFrame, out_path: Path) -> None:
    full_sorted = summary.sort_values(["full_sharpe_ratio", "full_annualized_return"], ascending=False)
    recent_sorted = summary.sort_values(["recent_sharpe_ratio", "recent_annualized_return"], ascending=False)
    best = full_sorted.iloc[0]
    cost_focus = costs[
        costs["variant"].isin(["baseline", "rsi_le_65", "trail8_mom_-5_vol_20", "rsi65_trail8_mom_-5_vol_20"])
    ]

    lines = [
        "# Combined Entry/Exit Validation",
        "",
        "Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.",
        "",
        "Test combinato:",
        "",
        "- filtro ingresso `RSI <= 65`;",
        "- trailing stop 8% sul massimo Close post-ingresso;",
        "- conferma uscita con momentum 7g >= -5% e volume relativo >= soglia.",
        "",
        "Performance misurata in EUR con `Close_EUR`; condizioni tecniche calcolate sulla serie ufficiale.",
        "",
        "## Periodo Completo",
        "",
        "| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Win rate | Uscite trail |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in full_sorted.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['full_annualized_return'])} | "
            f"{_pct(row['full_max_drawdown'])} | "
            f"{_ratio(row['full_sharpe_ratio'])} | "
            f"{_ratio(row['full_profit_factor'])} | "
            f"{int(row['full_num_operations'])} | "
            f"{_pct(row['full_win_rate'])} | "
            f"{int(row['confirmed_exits'])} |"
        )

    lines.extend(
        [
            "",
            "## Periodo 2022-Oggi",
            "",
            "| Variante | Ann. | Max DD | Sharpe | Esposizione | Turnover |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in recent_sorted.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['recent_annualized_return'])} | "
            f"{_pct(row['recent_max_drawdown'])} | "
            f"{_ratio(row['recent_sharpe_ratio'])} | "
            f"{_pct(row['recent_exposure_ratio'])} | "
            f"{int(row['recent_turnover'])} |"
        )

    lines.extend(
        [
            "",
            "## Costi Operativi - Periodo Completo",
            "",
            "| Variante | Scenario | Ann. | Max DD | Sharpe | PF |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in cost_focus.iterrows():
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
            "## Decisione",
            "",
            f"- Migliore variante del test: `{best['variant']}` con ann. "
            f"{_pct(best['full_annualized_return'])}, max DD "
            f"{_pct(best['full_max_drawdown'])}, Sharpe {_ratio(best['full_sharpe_ratio'])}.",
            "- Il miglioramento nasce dall'unione di due effetti diversi: meno ingressi in estensione e uscite protettive confermate.",
            "- Non e' una regola operativa: va validata con walk-forward piu' severo e controllo evento per evento.",
            "- Se supera quei controlli, diventa il primo vero candidato da confrontare contro la Baseline ufficiale.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`."
        )

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    summary, equities, frames = _summary(df)
    periods = _periods(equities)
    costs = _costs(frames)

    OUT_SUMMARY_CSV.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(OUT_SUMMARY_CSV, index=False)
    periods.to_csv(OUT_PERIODS_CSV, index=False)
    costs.to_csv(OUT_COSTS_CSV, index=False)
    _write_markdown(summary, periods, costs, OUT_MD)

    print(f"Saved {OUT_SUMMARY_CSV}")
    print(f"Saved {OUT_PERIODS_CSV}")
    print(f"Saved {OUT_COSTS_CSV}")
    print(f"Saved {OUT_MD}")
    print("")
    print(
        summary.sort_values(["full_sharpe_ratio", "full_annualized_return"], ascending=False)[
            [
                "variant",
                "full_annualized_return",
                "full_max_drawdown",
                "full_sharpe_ratio",
                "full_profit_factor",
                "recent_annualized_return",
                "recent_max_drawdown",
                "recent_sharpe_ratio",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
