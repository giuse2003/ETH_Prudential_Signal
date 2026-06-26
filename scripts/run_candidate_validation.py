"""
Validazione sperimentale dei migliori candidati modello.

Questo script non modifica i segnali ufficiali. Confronta alcuni candidati
emersi dai test precedenti su:
- periodo completo;
- sottoperiodi fissi;
- walk-forward semplice.
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
OUT_FULL_CSV = PROJECT_ROOT / "reports" / "candidate_validation_full.csv"
OUT_PERIOD_CSV = PROJECT_ROOT / "reports" / "candidate_validation_periods.csv"
OUT_WALK_FORWARD_CSV = PROJECT_ROOT / "reports" / "candidate_validation_walk_forward.csv"
OUT_MD = PROJECT_ROOT / "reports" / "candidate_validation_results.md"


PERIODS = {
    "2017-2020": ("2017-11-11", "2020-12-31"),
    "2021-2022": ("2021-01-01", "2022-12-31"),
    "2023-2024": ("2023-01-01", "2024-12-31"),
    "2025-2026": ("2025-01-01", "2026-06-25"),
}

WALK_FORWARD_SPLITS = [
    ("2017-2020", "2017-11-11", "2020-12-31", "2021-2022", "2021-01-01", "2022-12-31"),
    ("2017-2022", "2017-11-11", "2022-12-31", "2023-2024", "2023-01-01", "2024-12-31"),
    ("2017-2024", "2017-11-11", "2024-12-31", "2025-2026", "2025-01-01", "2026-06-25"),
]


def _confirmed_trailing_frame(df: pd.DataFrame, momentum_min: float, volume_rel_min: float) -> pd.DataFrame:
    out = df[["Close", "Segnale"]].copy()
    exposure = 0.0
    peak_close: float | None = None
    signals: list[str] = []

    for _, row in df.iterrows():
        signal = str(row["Segnale"])
        close = float(row["Close"])

        if signal == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            peak_close = close if peak_close is None else max(peak_close, close)
        elif signal == "ACQUISTA":
            exposure = 1.0
            peak_close = close if peak_close is None else max(peak_close, close)
        elif signal == "VENDI":
            exposure = 0.0
            peak_close = None
        elif exposure > 0.0 and peak_close is not None:
            peak_close = max(peak_close, close)
            if close <= peak_close * 0.92:
                momentum = close / row["Close_7d_ago"] - 1.0
                volume_rel = row["Volume"] / row["VolumeAvg20"] - 1.0
                if momentum >= momentum_min and volume_rel >= volume_rel_min:
                    signal = "VENDI"
                    exposure = 0.0
                    peak_close = None

        signals.append(signal)

    out["Segnale"] = signals
    return out


def _entry_stop_frame(df: pd.DataFrame, stop_pct: float) -> pd.DataFrame:
    out = df[["Close", "Segnale"]].copy()
    exposure = 0.0
    entry: float | None = None
    signals: list[str] = []

    for _, row in df.iterrows():
        signal = str(row["Segnale"])
        close = float(row["Close"])

        if signal == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            entry = close
        elif signal == "ACQUISTA":
            exposure = 1.0
        elif signal == "VENDI":
            exposure = 0.0
            entry = None
        elif exposure > 0.0 and entry is not None and close <= entry * (1.0 - stop_pct):
            signal = "VENDI"
            exposure = 0.0
            entry = None

        signals.append(signal)

    out["Segnale"] = signals
    return out


def _exit_sma50_1d_frame(df: pd.DataFrame) -> pd.DataFrame:
    out = df[["Close", "Segnale"]].copy()
    out.loc[df["Close"] < df["SMA50"], "Segnale"] = "VENDI"
    return out


def _candidate_frames(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "baseline": df[["Close", "Segnale"]].copy(),
        "entry_stop_9pct": _entry_stop_frame(df, 0.09),
        "confirmed_trail8_mom_-5_vol_10": _confirmed_trailing_frame(df, -0.05, 0.10),
        "confirmed_trail8_mom_-5_vol_20": _confirmed_trailing_frame(df, -0.05, 0.20),
        "confirmed_trail8_mom_-6_vol_20": _confirmed_trailing_frame(df, -0.06, 0.20),
        "exit_sma50_1d": _exit_sma50_1d_frame(df),
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


def _slice_metrics(equity_df: pd.DataFrame, start: str, end: str) -> dict[str, float]:
    subset = equity_df.loc[start:end].copy()
    if len(subset) < 2:
        return {
            "total_return": float("nan"),
            "annualized_return": float("nan"),
            "max_drawdown": float("nan"),
            "sharpe_ratio": float("nan"),
        }

    equity = subset["EquityStrategy"]
    returns = subset["DailyReturnStrategy"]
    n_days = max(len(subset) - 1, 1)
    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    annualized_return = float(
        (equity.iloc[-1] / equity.iloc[0]) ** (CFG.periods_per_year / n_days) - 1.0
    )
    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "max_drawdown": _max_drawdown(equity),
        "sharpe_ratio": _sharpe(returns),
    }


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(
    full: pd.DataFrame,
    periods: pd.DataFrame,
    walk_forward: pd.DataFrame,
    out_path: Path,
) -> None:
    full_sorted = full.sort_values(["sharpe_ratio", "annualized_return"], ascending=False)
    robustness = (
        periods.groupby("variant")
        .agg(
            median_period_sharpe=("sharpe_ratio", "median"),
            min_period_sharpe=("sharpe_ratio", "min"),
            median_period_ann=("annualized_return", "median"),
            worst_period_dd=("max_drawdown", "min"),
            positive_periods=("annualized_return", lambda s: int((s > 0).sum())),
            periods=("annualized_return", "count"),
        )
        .reset_index()
    )

    lines = [
        "# Candidate Validation Results",
        "",
        "Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.",
        "",
        "## Periodo Completo",
        "",
        "| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Net 0,25% Sharpe |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in full_sorted.iterrows():
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
            "## Robustezza Per Sottoperiodi",
            "",
            "| Variante | Mediana Sharpe | Min Sharpe | Mediana Ann. | Peggior DD | Periodi positivi |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    merged = robustness.merge(full[["variant", "sharpe_ratio"]], on="variant", how="left")
    for _, row in merged.sort_values("sharpe_ratio", ascending=False).iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_ratio(row['median_period_sharpe'])} | "
            f"{_ratio(row['min_period_sharpe'])} | "
            f"{_pct(row['median_period_ann'])} | "
            f"{_pct(row['worst_period_dd'])} | "
            f"{int(row['positive_periods'])}/{int(row['periods'])} |"
        )

    lines.extend(
        [
            "",
            "## Walk-Forward",
            "",
            "Per ogni split, seleziona il miglior candidato sul train per Sharpe e misura il test successivo.",
            "",
            "| Train | Test | Selezionato | Test Ann. | Test DD | Test Sharpe |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    selected = walk_forward[walk_forward["selected_by_train_sharpe"] == walk_forward["variant"]]
    for _, row in selected.iterrows():
        lines.append(
            "| "
            f"{row['train_period']} | "
            f"{row['test_period']} | "
            f"{row['variant']} | "
            f"{_pct(row['test_annualized_return'])} | "
            f"{_pct(row['test_max_drawdown'])} | "
            f"{_ratio(row['test_sharpe_ratio'])} |"
        )

    best_full = full_sorted.iloc[0]
    stable = robustness.sort_values(["min_period_sharpe", "median_period_sharpe"], ascending=False).iloc[0]
    lines.extend(
        [
            "",
            "## Sintesi",
            "",
            f"- Migliore sul periodo completo: `{best_full['variant']}` con Sharpe "
            f"{_ratio(best_full['sharpe_ratio'])}.",
            f"- Migliore per min Sharpe nei sottoperiodi: `{stable['variant']}` con "
            f"min Sharpe {_ratio(stable['min_period_sharpe'])}.",
            "- La validazione mostra rischio overfitting: il migliore sul periodo",
            "  completo non e' sempre il migliore nel periodo successivo.",
            "- Nessun candidato viene promosso a regola operativa in questa fase.",
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
    frames = _candidate_frames(source)
    equity_by_variant: dict[str, pd.DataFrame] = {}

    full_rows: list[dict] = []
    period_rows: list[dict] = []
    for variant, frame in frames.items():
        equity, gross, _ = run_backtest(frame)
        _, net_025, _ = run_backtest(frame, transaction_cost_rate=0.0025)
        equity_by_variant[variant] = equity
        full_rows.append(
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

        for period, (start, end) in PERIODS.items():
            period_rows.append(
                {
                    "variant": variant,
                    "period": period,
                    **_slice_metrics(equity, start, end),
                }
            )

    walk_rows: list[dict] = []
    for train_period, train_start, train_end, test_period, test_start, test_end in WALK_FORWARD_SPLITS:
        train_metrics = []
        for variant, equity in equity_by_variant.items():
            train_metrics.append(
                {
                    "variant": variant,
                    **_slice_metrics(equity, train_start, train_end),
                }
            )
        train_df = pd.DataFrame(train_metrics)
        selected = train_df.sort_values(["sharpe_ratio", "annualized_return"], ascending=False).iloc[0]["variant"]

        for variant, equity in equity_by_variant.items():
            train = _slice_metrics(equity, train_start, train_end)
            test = _slice_metrics(equity, test_start, test_end)
            walk_rows.append(
                {
                    "train_period": train_period,
                    "test_period": test_period,
                    "selected_by_train_sharpe": selected,
                    "variant": variant,
                    "train_annualized_return": train["annualized_return"],
                    "train_max_drawdown": train["max_drawdown"],
                    "train_sharpe_ratio": train["sharpe_ratio"],
                    "test_annualized_return": test["annualized_return"],
                    "test_max_drawdown": test["max_drawdown"],
                    "test_sharpe_ratio": test["sharpe_ratio"],
                }
            )

    full = pd.DataFrame(full_rows)
    periods = pd.DataFrame(period_rows)
    walk_forward = pd.DataFrame(walk_rows)

    OUT_FULL_CSV.parent.mkdir(parents=True, exist_ok=True)
    full.to_csv(OUT_FULL_CSV, index=False)
    periods.to_csv(OUT_PERIOD_CSV, index=False)
    walk_forward.to_csv(OUT_WALK_FORWARD_CSV, index=False)
    _write_markdown(full, periods, walk_forward, OUT_MD)

    display_cols = [
        "variant",
        "annualized_return",
        "max_drawdown",
        "sharpe_ratio",
        "profit_factor",
        "num_operations",
        "net_025_sharpe_ratio",
    ]
    print(full.sort_values(["sharpe_ratio", "annualized_return"], ascending=False)[display_cols].to_string(index=False))
    print("")
    print(f"Full CSV: {OUT_FULL_CSV}")
    print(f"Period CSV: {OUT_PERIOD_CSV}")
    print(f"Walk-forward CSV: {OUT_WALK_FORWARD_CSV}")
    print(f"Report: {OUT_MD}")


if __name__ == "__main__":
    main()
