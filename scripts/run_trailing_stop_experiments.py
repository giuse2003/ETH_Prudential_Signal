"""
Analisi sperimentale del trailing stop su Close giornaliero.

Questo script non modifica i segnali ufficiali. Forza VENDI solo nel frame di
backtest quando il Close scende sotto una percentuale dal massimo Close
raggiunto dopo l'ingresso sperimentale.
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
OUT_GRID_CSV = PROJECT_ROOT / "reports" / "trailing_stop_experiment_grid.csv"
OUT_PERIOD_CSV = PROJECT_ROOT / "reports" / "trailing_stop_experiment_periods.csv"
OUT_MD = PROJECT_ROOT / "reports" / "trailing_stop_experiment_results.md"


PERIODS = {
    "2017-2020": ("2017-11-11", "2020-12-31"),
    "2021-2022": ("2021-01-01", "2022-12-31"),
    "2023-2026": ("2023-01-01", "2026-06-25"),
    "2025-2026": ("2025-01-01", "2026-06-25"),
}


def _trailing_stop_frame(df: pd.DataFrame, stop_pct: float) -> pd.DataFrame:
    out = df[["Close", "Segnale"]].copy()
    exposure = 0.0
    peak_close: float | None = None
    signals: list[str] = []

    for _, row in df.iterrows():
        signal = str(row["Segnale"])
        close = float(row["Close"])

        if signal == "ACQUISTA":
            exposure = 1.0
            peak_close = close if peak_close is None else max(peak_close, close)
        elif signal == "VENDI":
            exposure = 0.0
            peak_close = None
        elif exposure > 0.0 and peak_close is not None:
            peak_close = max(peak_close, close)
            if close <= peak_close * (1.0 - stop_pct):
                signal = "VENDI"
                exposure = 0.0
                peak_close = None

        signals.append(signal)

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


def _period_metrics(equity_df: pd.DataFrame, start: str, end: str) -> dict[str, float]:
    subset = equity_df.loc[start:end].copy()
    if len(subset) < 2:
        return {
            "period_total_return": float("nan"),
            "period_annualized_return": float("nan"),
            "period_max_drawdown": float("nan"),
            "period_sharpe_ratio": float("nan"),
        }

    equity = subset["EquityStrategy"]
    daily_returns = subset["DailyReturnStrategy"]
    n_days = max(len(subset) - 1, 1)
    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    annualized_return = float(
        (equity.iloc[-1] / equity.iloc[0]) ** (CFG.periods_per_year / n_days) - 1.0
    )
    return {
        "period_total_return": total_return,
        "period_annualized_return": annualized_return,
        "period_max_drawdown": _max_drawdown(equity),
        "period_sharpe_ratio": _sharpe(daily_returns),
    }


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(grid: pd.DataFrame, periods: pd.DataFrame, out_path: Path) -> None:
    by_sharpe = grid.sort_values(["sharpe_ratio", "annualized_return"], ascending=False).head(8)
    by_drawdown = grid.sort_values(["max_drawdown", "annualized_return"], ascending=[False, False]).head(8)
    focus = grid[grid["variant"].isin(["baseline", "trailing_8pct", "trailing_10pct", "trailing_12pct", "trailing_15pct", "trailing_20pct"])]

    lines = [
        "# Trailing Stop Experiment Results",
        "",
        "Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.",
        "",
        "La regola sperimentale aggiorna lo stop sul massimo Close raggiunto dopo",
        "l'ingresso. Se il Close scende sotto `massimo_close * (1 - stop)`, forza",
        "`VENDI` nel frame di backtest.",
        "",
        "Esempio: ingresso a 2.000, Close sale a 2.100, trailing stop 8% = 1.932.",
        "",
        "## Griglia Principale",
        "",
        "| Variante | Ann. | Max DD | Sharpe | Profit factor | Operazioni | Net 0,25% Sharpe |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in by_sharpe.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{_ratio(row['net_025_sharpe_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Migliori Per Drawdown",
            "",
            "| Variante | Ann. | Max DD | Sharpe | Operazioni | Net 0,25% DD |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in by_drawdown.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{int(row['num_operations'])} | "
            f"{_pct(row['net_025_max_drawdown'])} |"
        )

    lines.extend(
        [
            "",
            "## Focus",
            "",
            "| Variante | Ann. | Max DD | Sharpe | Net 0,25% Sharpe | Stress 0,50% Sharpe |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in focus.sort_values("variant").iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['net_025_sharpe_ratio'])} | "
            f"{_ratio(row['net_050_sharpe_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Sottoperiodi: Max Drawdown",
            "",
            "| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    dd_table = periods.pivot(index="variant", columns="period", values="period_max_drawdown")
    for variant in ["baseline", "trailing_8pct", "trailing_10pct", "trailing_12pct", "trailing_15pct", "trailing_20pct"]:
        row = dd_table.loc[variant]
        lines.append(
            "| "
            f"{variant} | "
            f"{_pct(row['2017-2020'])} | "
            f"{_pct(row['2021-2022'])} | "
            f"{_pct(row['2023-2026'])} | "
            f"{_pct(row['2025-2026'])} |"
        )

    best_sharpe = by_sharpe.iloc[0]
    best_dd = by_drawdown.iloc[0]
    lines.extend(
        [
            "",
            "## Sintesi",
            "",
            f"- Migliore Sharpe: `{best_sharpe['variant']}` con Sharpe "
            f"{_ratio(best_sharpe['sharpe_ratio'])}, ann. "
            f"{_pct(best_sharpe['annualized_return'])}, max DD "
            f"{_pct(best_sharpe['max_drawdown'])}.",
            f"- Migliore drawdown: `{best_dd['variant']}` con max DD "
            f"{_pct(best_dd['max_drawdown'])}, ann. "
            f"{_pct(best_dd['annualized_return'])}.",
            "- Il trailing stop 8% riduce il drawdown ma sacrifica troppo rendimento",
            "  e Sharpe rispetto alla baseline.",
            "- Nessuna regola viene promossa a operativa senza ulteriori controlli.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`."
        )

    source = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).set_index("Date")
    variants = {"baseline": source[["Close", "Segnale"]].copy()}
    for pct in range(4, 26):
        variants[f"trailing_{pct}pct"] = _trailing_stop_frame(source, pct / 100.0)

    grid_rows: list[dict] = []
    period_rows: list[dict] = []
    for name, frame in variants.items():
        equity, gross, _ = run_backtest(frame)
        _, net_010, _ = run_backtest(frame, transaction_cost_rate=0.001)
        _, net_025, _ = run_backtest(frame, transaction_cost_rate=0.0025)
        _, net_050, _ = run_backtest(frame, transaction_cost_rate=0.005)

        grid_rows.append(
            {
                "variant": name,
                "total_return": gross.total_return,
                "annualized_return": gross.annualized_return,
                "max_drawdown": gross.max_drawdown,
                "sharpe_ratio": gross.sharpe_ratio,
                "profit_factor": gross.profit_factor,
                "num_operations": gross.num_operations,
                "win_rate": gross.win_rate,
                "exposure_ratio": gross.exposure_ratio,
                "net_010_annualized_return": net_010.annualized_return,
                "net_010_max_drawdown": net_010.max_drawdown,
                "net_010_sharpe_ratio": net_010.sharpe_ratio,
                "net_025_annualized_return": net_025.annualized_return,
                "net_025_max_drawdown": net_025.max_drawdown,
                "net_025_sharpe_ratio": net_025.sharpe_ratio,
                "net_050_annualized_return": net_050.annualized_return,
                "net_050_max_drawdown": net_050.max_drawdown,
                "net_050_sharpe_ratio": net_050.sharpe_ratio,
            }
        )

        for period, (start, end) in PERIODS.items():
            period_rows.append(
                {
                    "variant": name,
                    "period": period,
                    **_period_metrics(equity, start, end),
                }
            )

    grid = pd.DataFrame(grid_rows).sort_values(
        ["sharpe_ratio", "annualized_return"],
        ascending=False,
    )
    periods = pd.DataFrame(period_rows)
    OUT_GRID_CSV.parent.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUT_GRID_CSV, index=False)
    periods.to_csv(OUT_PERIOD_CSV, index=False)
    _write_markdown(grid, periods, OUT_MD)

    display_cols = [
        "variant",
        "annualized_return",
        "max_drawdown",
        "sharpe_ratio",
        "profit_factor",
        "num_operations",
        "net_025_sharpe_ratio",
    ]
    print(grid[display_cols].head(12).to_string(index=False))
    print("")
    print(f"Grid CSV: {OUT_GRID_CSV}")
    print(f"Period CSV: {OUT_PERIOD_CSV}")
    print(f"Report: {OUT_MD}")


if __name__ == "__main__":
    main()
