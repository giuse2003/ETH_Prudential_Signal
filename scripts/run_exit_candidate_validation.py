"""
Validazione del candidato uscita Trail8 confermato -5 / vol +20.

Questo script non modifica i segnali ufficiali. Mantiene invariati gli ingressi
Baseline e valida il candidato uscita con:
- stress costi/slippage;
- confronto anno per anno.

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
OUT_COSTS_CSV = PROJECT_ROOT / "reports" / "exit_candidate_cost_stress.csv"
OUT_YEARS_CSV = PROJECT_ROOT / "reports" / "exit_candidate_yearly_validation.csv"
OUT_MD = PROJECT_ROOT / "reports" / "exit_candidate_validation.md"

END_DATE = "2026-06-27"
STOP_PCT = 0.08
MOMENTUM_MIN = -0.05
VOLUME_REL_MIN = 0.20
COST_SCENARIOS = [
    ("lordo_0_00pct", 0.0),
    ("costo_0_10pct", 0.001),
    ("costo_0_25pct", 0.0025),
    ("stress_0_50pct", 0.005),
    ("stress_1_00pct", 0.01),
]


def _baseline_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()


def _candidate_frame(df: pd.DataFrame) -> pd.DataFrame:
    exposure = 0.0
    peak_close: float | None = None
    signals: list[str] = []

    for _, row in df.iterrows():
        official = str(row["Segnale"])
        signal = official
        close = float(row["Close"])

        if official == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            peak_close = close
        elif official == "ACQUISTA":
            signal = "MANTIENI"
            peak_close = max(peak_close or close, close)
        elif official == "VENDI":
            exposure = 0.0
            peak_close = None
        elif exposure > 0.0 and peak_close is not None:
            peak_close = max(peak_close, close)
            if close <= peak_close * (1.0 - STOP_PCT):
                momentum_7d = close / float(row["Close_7d_ago"]) - 1.0
                volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
                if momentum_7d >= MOMENTUM_MIN and volume_rel >= VOLUME_REL_MIN:
                    signal = "VENDI"
                    exposure = 0.0
                    peak_close = None

        signals.append(signal)

    out = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    out["Segnale"] = signals
    return out


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


def _year_metrics(equity: pd.DataFrame, year: int) -> dict[str, float]:
    subset = equity.loc[f"{year}-01-01":f"{year}-12-31"].copy()
    if len(subset) < 2:
        return {
            "total_return": float("nan"),
            "annualized_return": float("nan"),
            "max_drawdown": float("nan"),
            "sharpe_ratio": float("nan"),
            "exposure_ratio": float("nan"),
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
    }


def _cost_stress(base: pd.DataFrame, cand: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for scenario, cost in COST_SCENARIOS:
        _, bm, _ = run_backtest(base, transaction_cost_rate=cost)
        _, cm, _ = run_backtest(cand, transaction_cost_rate=cost)
        for model, m in [("Baseline ufficiale", bm), ("Trail8 -5 / vol +20", cm)]:
            rows.append(
                {
                    "scenario": scenario,
                    "cost_rate": cost,
                    "model": model,
                    "annualized_return": m.annualized_return,
                    "max_drawdown": m.max_drawdown,
                    "sharpe_ratio": m.sharpe_ratio,
                    "profit_factor": m.profit_factor,
                    "num_operations": m.num_operations,
                    "turnover": m.turnover,
                }
            )
        rows.append(
            {
                "scenario": scenario,
                "cost_rate": cost,
                "model": "Delta candidato - Baseline",
                "annualized_return": cm.annualized_return - bm.annualized_return,
                "max_drawdown": cm.max_drawdown - bm.max_drawdown,
                "sharpe_ratio": cm.sharpe_ratio - bm.sharpe_ratio,
                "profit_factor": cm.profit_factor - bm.profit_factor,
                "num_operations": cm.num_operations - bm.num_operations,
                "turnover": cm.turnover - bm.turnover,
            }
        )
    return pd.DataFrame(rows)


def _yearly(base: pd.DataFrame, cand: pd.DataFrame) -> pd.DataFrame:
    base_eq, _, _ = run_backtest(base)
    cand_eq, _, _ = run_backtest(cand)
    rows: list[dict[str, float | int]] = []
    for year in sorted(base.index.year.unique()):
        bm = _year_metrics(base_eq, int(year))
        cm = _year_metrics(cand_eq, int(year))
        rows.append(
            {
                "year": int(year),
                "baseline_return": bm["total_return"],
                "candidate_return": cm["total_return"],
                "delta_return": cm["total_return"] - bm["total_return"],
                "baseline_max_drawdown": bm["max_drawdown"],
                "candidate_max_drawdown": cm["max_drawdown"],
                "delta_max_drawdown": cm["max_drawdown"] - bm["max_drawdown"],
                "baseline_sharpe": bm["sharpe_ratio"],
                "candidate_sharpe": cm["sharpe_ratio"],
                "delta_sharpe": cm["sharpe_ratio"] - bm["sharpe_ratio"],
                "baseline_exposure": bm["exposure_ratio"],
                "candidate_exposure": cm["exposure_ratio"],
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


def _write_markdown(costs: pd.DataFrame, years: pd.DataFrame, out_path: Path, start: str, end: str) -> None:
    deltas = costs[costs["model"] == "Delta candidato - Baseline"]
    model_rows = costs[costs["model"] != "Delta candidato - Baseline"]
    real_years = years[years["delta_return"].abs() > 1e-8]
    better_years = years[years["delta_return"] > 1e-8]
    worse_years = years[years["delta_return"] < -1e-8]

    lines = [
        "# Exit Candidate Validation",
        "",
        f"Periodo: `{start}` -> `{end}`.",
        "",
        "Candidato uscita: `Trail8 confermato -5 / vol +20`.",
        "Ingressi Baseline invariati. Nessun segnale ufficiale viene modificato.",
        "",
        "## Stress Costi",
        "",
        "| Scenario | Modello | Ann. | Max DD | Sharpe | PF | Ops | Turnover |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in model_rows.iterrows():
        lines.append(
            "| "
            f"{row['scenario']} | {row['model']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{int(row['turnover'])} |"
        )

    lines.extend(
        [
            "",
            "## Delta Candidato Meno Baseline",
            "",
            "| Scenario | Delta Ann. | Delta DD | Delta Sharpe | Delta PF | Delta Ops |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in deltas.iterrows():
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
            "| Anno | Baseline Ret | Candidato Ret | Delta Ret | Baseline DD | Candidato DD | Delta DD | Baseline Sharpe | Candidato Sharpe |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in years.iterrows():
        lines.append(
            "| "
            f"{int(row['year'])} | "
            f"{_pct(row['baseline_return'])} | "
            f"{_pct(row['candidate_return'])} | "
            f"{_pct(row['delta_return'])} | "
            f"{_pct(row['baseline_max_drawdown'])} | "
            f"{_pct(row['candidate_max_drawdown'])} | "
            f"{_pct(row['delta_max_drawdown'])} | "
            f"{_ratio(row['baseline_sharpe'])} | "
            f"{_ratio(row['candidate_sharpe'])} |"
        )

    worst_cost = deltas.sort_values("annualized_return").iloc[0]
    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Anche nello scenario costi piu' severo, il delta annuo resta {_pct(worst_cost['annualized_return'])}.",
            f"- Anni in cui cambia il rendimento in modo reale: {', '.join(str(int(y)) for y in real_years['year']) if not real_years.empty else 'nessuno'}.",
            f"- Anni migliorati: {len(better_years)}.",
            f"- Anni peggiorati: {len(worse_years)}.",
            "- Se il candidato supera costi e anni, il passo successivo e' il test combinato con RSI <= 65.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")
    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    df = df.loc[: pd.Timestamp(END_DATE)].copy()
    base = _baseline_frame(df)
    cand = _candidate_frame(df)
    costs = _cost_stress(base, cand)
    years = _yearly(base, cand)
    OUT_COSTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    costs.to_csv(OUT_COSTS_CSV, index=False)
    years.to_csv(OUT_YEARS_CSV, index=False)
    _write_markdown(costs, years, OUT_MD, df.index[0].date().isoformat(), df.index[-1].date().isoformat())
    print(f"Saved {OUT_COSTS_CSV}")
    print(f"Saved {OUT_YEARS_CSV}")
    print(f"Saved {OUT_MD}")
    print(costs[costs["model"] == "Delta candidato - Baseline"].to_string(index=False))
    print(years[["year", "baseline_return", "candidate_return", "delta_return", "baseline_max_drawdown", "candidate_max_drawdown", "delta_max_drawdown"]].to_string(index=False))


if __name__ == "__main__":
    main()
