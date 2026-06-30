"""
Stress costi/slippage per la variante uscita SMA50 a 1 giorno.

Confronta Baseline SMA50 2 giorni + Trail8 contro SMA50 1 giorno + Trail8
con costi applicati a ogni cambio di esposizione.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backtest.backtest import run_backtest  # noqa: E402
from scripts.run_sma50_exit_timing_test import _build_signals, _trades  # noqa: E402


DATA_PATH = ROOT / "data" / "indicators_with_signals.csv"
REPORT_MD = ROOT / "reports" / "sma50_exit_timing_cost_stress.md"
COST_CSV = ROOT / "reports" / "sma50_exit_timing_cost_stress.csv"

COSTS = {
    "0.00%": 0.0,
    "0.10%": 0.001,
    "0.25%": 0.0025,
    "0.50%": 0.005,
}


def _pct(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def main() -> None:
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    models = {
        "SMA50 2 giorni + Trail8": _build_signals(df, sell_after_days=2),
        "SMA50 1 giorno + Trail8": _build_signals(df, sell_after_days=1),
    }

    rows: list[dict[str, float | int | str]] = []
    for scenario, cost in COSTS.items():
        for model, signals in models.items():
            _, metrics, _ = run_backtest(signals, transaction_cost_rate=cost)
            trades = _trades(signals, model)
            rows.append(
                {
                    "scenario": scenario,
                    "cost_rate": cost,
                    "model": model,
                    "total_return": metrics.total_return,
                    "annualized_return": metrics.annualized_return,
                    "max_drawdown": metrics.max_drawdown,
                    "sharpe": metrics.sharpe_ratio,
                    "profit_factor": metrics.profit_factor,
                    "operations": metrics.num_operations,
                    "turnover": metrics.turnover,
                    "entries": len(trades),
                    "sma50_exits": int((trades["exit_reason"] == "SMA50").sum()),
                    "trail8_exits": int((trades["exit_reason"] == "Trail8").sum()),
                }
            )

    results = pd.DataFrame(rows)
    COST_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(COST_CSV, index=False)

    lines = [
        "# SMA50 Exit Timing Cost Stress",
        "",
        "Stress costi/slippage per `Close < SMA50` a 1 giorno contro Baseline a 2 giorni.",
        "Ingressi e Trail8 restano invariati. Metriche in USD.",
        "",
        "## Metriche",
        "",
        "| Costo | Modello | Totale | Ann. | Max DD | Sharpe | PF | Operazioni | Turnover |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in results.iterrows():
        lines.append(
            f"| {row['scenario']} | {row['model']} | {_pct(row['total_return'])} | "
            f"{_pct(row['annualized_return'])} | {_pct(row['max_drawdown'])} | "
            f"{row['sharpe']:.3f} | {row['profit_factor']:.3f} | "
            f"{int(row['operations'])} | {row['turnover']:.1f} |"
        )

    lines.extend(["", "## Delta 1 giorno vs 2 giorni", ""])
    lines.append("| Costo | Delta ann. | Delta DD | Delta Sharpe | Delta PF |")
    lines.append("|---:|---:|---:|---:|---:|")
    for scenario in COSTS:
        subset = results[results["scenario"] == scenario].set_index("model")
        base = subset.loc["SMA50 2 giorni + Trail8"]
        one = subset.loc["SMA50 1 giorno + Trail8"]
        lines.append(
            f"| {scenario} | "
            f"{_pct(float(one['annualized_return']) - float(base['annualized_return']))} | "
            f"{_pct(float(one['max_drawdown']) - float(base['max_drawdown']))} | "
            f"{float(one['sharpe']) - float(base['sharpe']):+.3f} | "
            f"{float(one['profit_factor']) - float(base['profit_factor']):+.3f} |"
        )

    lines.extend(["", "## File generato", "", f"- `{COST_CSV.relative_to(ROOT)}`"])
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(results.to_string(index=False))
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
