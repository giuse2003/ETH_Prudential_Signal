"""
Test sperimentali su combinazioni di uscite protettive.

Questo script non modifica i segnali ufficiali. Costruisce frame temporanei
per confrontare:
- stop loss da ingresso;
- trailing stop 8% confermato da momentum/volume;
- combinazioni fra i due.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import run_backtest


SOURCE_CSV = PROJECT_ROOT / "data" / "indicators_with_signals.csv"
OUT_CSV = PROJECT_ROOT / "reports" / "combined_exit_experiment_results.csv"
OUT_MD = PROJECT_ROOT / "reports" / "combined_exit_experiment_results.md"


def _apply_combined_exit(
    df: pd.DataFrame,
    *,
    entry_stop_pct: float | None = None,
    trailing_stop_pct: float | None = None,
    momentum_min: float | None = None,
    volume_rel_min: float | None = None,
) -> pd.DataFrame:
    out = df[["Close", "Segnale"]].copy()
    exposure = 0.0
    entry_close: float | None = None
    peak_close: float | None = None
    signals: list[str] = []

    for _, row in df.iterrows():
        signal = str(row["Segnale"])
        close = float(row["Close"])

        if signal == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            entry_close = close
            peak_close = close
        elif signal == "ACQUISTA":
            exposure = 1.0
            if peak_close is None:
                peak_close = close
            else:
                peak_close = max(peak_close, close)
        elif signal == "VENDI":
            exposure = 0.0
            entry_close = None
            peak_close = None
        elif exposure > 0.0:
            if peak_close is None:
                peak_close = close
            peak_close = max(peak_close, close)

            exit_by_entry_stop = (
                entry_stop_pct is not None
                and entry_close is not None
                and close <= entry_close * (1.0 - entry_stop_pct)
            )

            exit_by_confirmed_trailing = False
            if (
                trailing_stop_pct is not None
                and momentum_min is not None
                and volume_rel_min is not None
                and close <= peak_close * (1.0 - trailing_stop_pct)
            ):
                momentum = close / row["Close_7d_ago"] - 1.0
                volume_rel = row["Volume"] / row["VolumeAvg20"] - 1.0
                exit_by_confirmed_trailing = (
                    momentum >= momentum_min and volume_rel >= volume_rel_min
                )

            if exit_by_entry_stop or exit_by_confirmed_trailing:
                signal = "VENDI"
                exposure = 0.0
                entry_close = None
                peak_close = None

        signals.append(signal)

    out["Segnale"] = signals
    return out


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(results: pd.DataFrame, out_path: Path) -> None:
    sorted_results = results.sort_values(
        ["sharpe_ratio", "annualized_return"], ascending=False
    )
    lines = [
        "# Combined Exit Experiment Results",
        "",
        "Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.",
        "",
        "## Periodo Completo",
        "",
        "| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Net 0,25% Sharpe |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in sorted_results.iterrows():
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

    best = sorted_results.iloc[0]
    lines.extend(
        [
            "",
            "## Sintesi",
            "",
            f"- Migliore combinazione per Sharpe: `{best['variant']}` con Sharpe "
            f"{_ratio(best['sharpe_ratio'])}.",
            "- Le combinazioni vanno confrontate con la validazione walk-forward "
            "prima di essere considerate operative.",
            "- Nessuna variante viene promossa a regola operativa in questa fase.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`."
        )

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).set_index("Date")
    variants = {
        "baseline": df[["Close", "Segnale"]].copy(),
        "entry_stop_9pct": _apply_combined_exit(df, entry_stop_pct=0.09),
        "trail8_mom_-5_vol_10": _apply_combined_exit(
            df, trailing_stop_pct=0.08, momentum_min=-0.05, volume_rel_min=0.10
        ),
        "trail8_mom_-5_vol_20": _apply_combined_exit(
            df, trailing_stop_pct=0.08, momentum_min=-0.05, volume_rel_min=0.20
        ),
        "trail8_mom_-6_vol_20": _apply_combined_exit(
            df, trailing_stop_pct=0.08, momentum_min=-0.06, volume_rel_min=0.20
        ),
        "entry9_plus_trail8_mom_-5_vol_10": _apply_combined_exit(
            df,
            entry_stop_pct=0.09,
            trailing_stop_pct=0.08,
            momentum_min=-0.05,
            volume_rel_min=0.10,
        ),
        "entry9_plus_trail8_mom_-5_vol_20": _apply_combined_exit(
            df,
            entry_stop_pct=0.09,
            trailing_stop_pct=0.08,
            momentum_min=-0.05,
            volume_rel_min=0.20,
        ),
        "entry9_plus_trail8_mom_-6_vol_20": _apply_combined_exit(
            df,
            entry_stop_pct=0.09,
            trailing_stop_pct=0.08,
            momentum_min=-0.06,
            volume_rel_min=0.20,
        ),
    }

    rows = []
    for variant, frame in variants.items():
        _, gross, _ = run_backtest(frame)
        _, net_025, _ = run_backtest(frame, transaction_cost_rate=0.0025)
        rows.append(
            {
                "variant": variant,
                "total_return": gross.total_return,
                "annualized_return": gross.annualized_return,
                "max_drawdown": gross.max_drawdown,
                "sharpe_ratio": gross.sharpe_ratio,
                "profit_factor": gross.profit_factor,
                "num_operations": gross.num_operations,
                "win_rate": gross.win_rate,
                "net_025_annualized_return": net_025.annualized_return,
                "net_025_max_drawdown": net_025.max_drawdown,
                "net_025_sharpe_ratio": net_025.sharpe_ratio,
            }
        )

    results = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_CSV, index=False)
    _write_markdown(results, OUT_MD)

    display_cols = [
        "variant",
        "annualized_return",
        "max_drawdown",
        "sharpe_ratio",
        "profit_factor",
        "num_operations",
        "net_025_sharpe_ratio",
    ]
    print(
        results.sort_values(["sharpe_ratio", "annualized_return"], ascending=False)[
            display_cols
        ].to_string(index=False)
    )
    print("")
    print(f"CSV: {OUT_CSV}")
    print(f"Report: {OUT_MD}")


if __name__ == "__main__":
    main()
