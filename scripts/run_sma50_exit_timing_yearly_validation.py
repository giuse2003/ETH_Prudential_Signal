"""
Validazione annuale della variante uscita SMA50 a 1 giorno.

Confronta:
- Baseline ufficiale: Close sotto SMA50 per 2 giorni + Trail8;
- variante: Close sotto SMA50 per 1 giorno + Trail8.

Ingressi e Trail8 restano invariati. Metriche in USD.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backtest.backtest import run_backtest  # noqa: E402
from config import CFG  # noqa: E402
from scripts.run_sma50_exit_timing_test import _build_signals, _trades  # noqa: E402


DATA_PATH = ROOT / "data" / "indicators_with_signals.csv"
REPORT_MD = ROOT / "reports" / "sma50_exit_timing_yearly_validation.md"
YEARLY_CSV = ROOT / "reports" / "sma50_exit_timing_yearly_validation.csv"


def _pct(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


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


def _period_metrics(equity: pd.DataFrame, trades: pd.DataFrame, year: int) -> dict[str, float | int]:
    subset = equity.loc[f"{year}-01-01":f"{year}-12-31"].copy()
    if len(subset) < 2:
        return {
            "total_return": float("nan"),
            "annualized_return": float("nan"),
            "max_drawdown": float("nan"),
            "sharpe": float("nan"),
            "exposure": float("nan"),
            "entries": 0,
            "exits": 0,
            "sma50_exits": 0,
            "trail8_exits": 0,
        }

    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    returns = normalized.pct_change()
    days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    entries = trades[pd.to_datetime(trades["entry_date"]).dt.year == year]
    exits = trades[pd.to_datetime(trades["exit_date"]).dt.year == year]

    return {
        "total_return": total_return,
        "annualized_return": float((1.0 + total_return) ** (CFG.periods_per_year / days) - 1.0),
        "max_drawdown": _max_drawdown(normalized),
        "sharpe": _sharpe(returns),
        "exposure": float(subset["EffectiveExposure"].gt(0.0).mean()),
        "entries": int(len(entries)),
        "exits": int(len(exits)),
        "sma50_exits": int((exits["exit_reason"] == "SMA50").sum()),
        "trail8_exits": int((exits["exit_reason"] == "Trail8").sum()),
    }


def main() -> None:
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    models = {
        "SMA50 2 giorni + Trail8": _build_signals(df, sell_after_days=2),
        "SMA50 1 giorno + Trail8": _build_signals(df, sell_after_days=1),
    }

    equities: dict[str, pd.DataFrame] = {}
    trades_by_model: dict[str, pd.DataFrame] = {}
    for name, signals in models.items():
        equities[name], _, _ = run_backtest(signals)
        trades_by_model[name] = _trades(signals, name)

    rows: list[dict[str, float | int | str]] = []
    for year in sorted(df.index.year.unique()):
        base = _period_metrics(equities["SMA50 2 giorni + Trail8"], trades_by_model["SMA50 2 giorni + Trail8"], int(year))
        one = _period_metrics(equities["SMA50 1 giorno + Trail8"], trades_by_model["SMA50 1 giorno + Trail8"], int(year))
        rows.append(
            {
                "year": int(year),
                "baseline_return": base["total_return"],
                "one_day_return": one["total_return"],
                "delta_return": float(one["total_return"]) - float(base["total_return"]),
                "baseline_max_drawdown": base["max_drawdown"],
                "one_day_max_drawdown": one["max_drawdown"],
                "delta_max_drawdown": float(one["max_drawdown"]) - float(base["max_drawdown"]),
                "baseline_sharpe": base["sharpe"],
                "one_day_sharpe": one["sharpe"],
                "delta_sharpe": float(one["sharpe"]) - float(base["sharpe"]),
                "baseline_entries": base["entries"],
                "one_day_entries": one["entries"],
                "delta_entries": int(one["entries"]) - int(base["entries"]),
                "baseline_exits": base["exits"],
                "one_day_exits": one["exits"],
                "delta_exits": int(one["exits"]) - int(base["exits"]),
                "baseline_sma50_exits": base["sma50_exits"],
                "one_day_sma50_exits": one["sma50_exits"],
                "baseline_trail8_exits": base["trail8_exits"],
                "one_day_trail8_exits": one["trail8_exits"],
                "baseline_exposure": base["exposure"],
                "one_day_exposure": one["exposure"],
            }
        )

    yearly = pd.DataFrame(rows)
    YEARLY_CSV.parent.mkdir(parents=True, exist_ok=True)
    yearly.to_csv(YEARLY_CSV, index=False)

    better_return = int((yearly["delta_return"] > 1e-12).sum())
    worse_return = int((yearly["delta_return"] < -1e-12).sum())
    better_dd = int((yearly["delta_max_drawdown"] > 1e-12).sum())
    worse_dd = int((yearly["delta_max_drawdown"] < -1e-12).sum())

    lines = [
        "# SMA50 Exit Timing Yearly Validation",
        "",
        "Validazione annuale della variante `Close < SMA50` a 1 giorno contro Baseline a 2 giorni.",
        "Ingressi e Trail8 restano invariati. Metriche in USD.",
        "",
        "## Sintesi",
        "",
        f"- Anni con rendimento migliore usando SMA50 a 1 giorno: {better_return}.",
        f"- Anni con rendimento peggiore usando SMA50 a 1 giorno: {worse_return}.",
        f"- Anni con drawdown annuale meno profondo: {better_dd}.",
        f"- Anni con drawdown annuale piu' profondo: {worse_dd}.",
        "",
        "## Tabella Annuale",
        "",
        "| Anno | Ret 2g | Ret 1g | Delta ret | DD 2g | DD 1g | Delta DD | Sharpe 2g | Sharpe 1g | Entry 2g/1g | Exit 2g/1g | SMA50 exit 2g/1g | Trail8 exit 2g/1g |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in yearly.iterrows():
        lines.append(
            f"| {int(row['year'])} | "
            f"{_pct(row['baseline_return'])} | {_pct(row['one_day_return'])} | {_pct(row['delta_return'])} | "
            f"{_pct(row['baseline_max_drawdown'])} | {_pct(row['one_day_max_drawdown'])} | {_pct(row['delta_max_drawdown'])} | "
            f"{_ratio(row['baseline_sharpe'])} | {_ratio(row['one_day_sharpe'])} | "
            f"{int(row['baseline_entries'])}/{int(row['one_day_entries'])} | "
            f"{int(row['baseline_exits'])}/{int(row['one_day_exits'])} | "
            f"{int(row['baseline_sma50_exits'])}/{int(row['one_day_sma50_exits'])} | "
            f"{int(row['baseline_trail8_exits'])}/{int(row['one_day_trail8_exits'])} |"
        )

    lines.extend(
        [
            "",
            "## File generato",
            "",
            f"- `{YEARLY_CSV.relative_to(ROOT)}`",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(yearly.to_string(index=False))
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
