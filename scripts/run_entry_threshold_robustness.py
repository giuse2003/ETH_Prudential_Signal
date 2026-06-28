"""
Robustezza soglia RSI per i soli ingressi.

Questo script non modifica i segnali ufficiali. Tiene ferma l'uscita ufficiale
e confronta filtri di ingresso RSI <= 63 fino a RSI <= 70.

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
OUT_CSV = PROJECT_ROOT / "reports" / "entry_threshold_robustness.csv"
OUT_MD = PROJECT_ROOT / "reports" / "entry_threshold_robustness.md"

END_DATE = "2026-06-27"
RECENT_START = "2022-01-01"
THRESHOLDS = [63, 64, 65, 66, 67, 68, 69, 70]


def _entry_frame(df: pd.DataFrame, threshold: int | None) -> tuple[pd.DataFrame, int, int]:
    exposure = 0.0
    signals: list[str] = []
    blocked_new_entries = 0
    blocked_total = 0

    for _, row in df.iterrows():
        signal = str(row["Segnale"])
        if threshold is not None and signal == "ACQUISTA" and float(row["RSI"]) > threshold:
            blocked_total += 1
            if exposure <= 0.0:
                blocked_new_entries += 1
            signal = "MANTIENI"
        elif signal == "ACQUISTA" and exposure > 0.0:
            signal = "MANTIENI"

        if signal == "ACQUISTA":
            exposure = 1.0
        elif signal == "VENDI":
            exposure = 0.0
        signals.append(signal)

    frame = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    frame["Segnale"] = signals
    return frame, blocked_new_entries, blocked_total


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


def _slice_metrics(equity: pd.DataFrame, start: str) -> dict[str, float]:
    subset = equity.loc[start:].copy()
    if len(subset) < 2:
        return {
            "recent_annualized_return": float("nan"),
            "recent_max_drawdown": float("nan"),
            "recent_sharpe_ratio": float("nan"),
        }
    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    returns = normalized.pct_change()
    n_days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    return {
        "recent_annualized_return": float((1.0 + total_return) ** (CFG.periods_per_year / n_days) - 1.0),
        "recent_max_drawdown": _max_drawdown(normalized),
        "recent_sharpe_ratio": _sharpe(returns),
    }


def _run(df: pd.DataFrame) -> pd.DataFrame:
    baseline_frame, _, _ = _entry_frame(df, None)
    _, baseline_metrics, _ = run_backtest(baseline_frame)
    rows: list[dict[str, float | int | str]] = [
        {
            "variant": "Baseline ufficiale",
            "threshold": float("nan"),
            "annualized_return": baseline_metrics.annualized_return,
            "max_drawdown": baseline_metrics.max_drawdown,
            "sharpe_ratio": baseline_metrics.sharpe_ratio,
            "profit_factor": baseline_metrics.profit_factor,
            "num_operations": baseline_metrics.num_operations,
            "win_rate": baseline_metrics.win_rate,
            "exposure_ratio": baseline_metrics.exposure_ratio,
            **_slice_metrics(run_backtest(baseline_frame)[0], RECENT_START),
            "blocked_new_entries": 0,
            "blocked_total_signals": 0,
            "delta_ann_vs_baseline": 0.0,
            "delta_dd_vs_baseline": 0.0,
            "delta_sharpe_vs_baseline": 0.0,
            "delta_pf_vs_baseline": 0.0,
        }
    ]

    for threshold in THRESHOLDS:
        frame, blocked_new, blocked_total = _entry_frame(df, threshold)
        equity, metrics, _ = run_backtest(frame)
        rows.append(
            {
                "variant": f"RSI <= {threshold}",
                "threshold": threshold,
                "annualized_return": metrics.annualized_return,
                "max_drawdown": metrics.max_drawdown,
                "sharpe_ratio": metrics.sharpe_ratio,
                "profit_factor": metrics.profit_factor,
                "num_operations": metrics.num_operations,
                "win_rate": metrics.win_rate,
                "exposure_ratio": metrics.exposure_ratio,
                **_slice_metrics(equity, RECENT_START),
                "blocked_new_entries": blocked_new,
                "blocked_total_signals": blocked_total,
                "delta_ann_vs_baseline": metrics.annualized_return - baseline_metrics.annualized_return,
                "delta_dd_vs_baseline": metrics.max_drawdown - baseline_metrics.max_drawdown,
                "delta_sharpe_vs_baseline": metrics.sharpe_ratio - baseline_metrics.sharpe_ratio,
                "delta_pf_vs_baseline": metrics.profit_factor - baseline_metrics.profit_factor,
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


def _write_markdown(results: pd.DataFrame, out_path: Path, start_date: str, end_date: str) -> None:
    candidates = results[results["variant"] != "Baseline ufficiale"].copy()
    best_sharpe = candidates.sort_values(["sharpe_ratio", "annualized_return"], ascending=False).iloc[0]
    best_dd = candidates.sort_values(["max_drawdown", "annualized_return"], ascending=False).iloc[0]
    best_ann = candidates.sort_values(["annualized_return", "sharpe_ratio"], ascending=False).iloc[0]

    lines = [
        "# Entry Threshold Robustness",
        "",
        f"Periodo: `{start_date}` -> `{end_date}`.",
        "",
        "Confronto solo sugli ingressi. L'uscita resta invariata: `VENDI` sotto SMA50 per 2 giorni consecutivi.",
        "",
        "Soglie testate: `RSI <= 63` fino a `RSI <= 70`.",
        "",
        "## Risultati",
        "",
        "| Variante | Ann. | Delta Ann. | Max DD | Delta DD | Sharpe | Delta Sharpe | PF | Ops | Nuovi ingressi bloccati | 2022+ Ann. | 2022+ DD |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in results.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['delta_ann_vs_baseline'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_pct(row['delta_dd_vs_baseline'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['delta_sharpe_vs_baseline'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{int(row['blocked_new_entries'])} | "
            f"{_pct(row['recent_annualized_return'])} | "
            f"{_pct(row['recent_max_drawdown'])} |"
        )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Migliore Sharpe: `{best_sharpe['variant']}` con Sharpe {_ratio(best_sharpe['sharpe_ratio'])}.",
            f"- Miglior rendimento annualizzato: `{best_ann['variant']}` con ann. {_pct(best_ann['annualized_return'])}.",
            f"- Miglior max drawdown: `{best_dd['variant']}` con DD {_pct(best_dd['max_drawdown'])}.",
            "- Se soglie vicine producono risultati simili, la zona e' robusta; se cambia tutto per un punto RSI, la regola e' fragile.",
            "- Questa analisi resta un test sugli ingressi: nessun segnale ufficiale viene modificato.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    df = df.loc[: pd.Timestamp(END_DATE)].copy()
    if df.empty:
        raise ValueError(f"Nessuna candela disponibile fino a {END_DATE}.")

    results = _run(df)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_CSV, index=False)
    _write_markdown(results, OUT_MD, df.index[0].date().isoformat(), df.index[-1].date().isoformat())

    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_MD}")
    print(
        results[
            [
                "variant",
                "annualized_return",
                "max_drawdown",
                "sharpe_ratio",
                "profit_factor",
                "num_operations",
                "blocked_new_entries",
                "recent_annualized_return",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
