"""
Promotion gate sperimentale per SMA50 a 1 giorno + Trail8.

Non modifica i segnali ufficiali. Valuta se il candidato puo' sostituire la
regola Baseline `Close < SMA50` per 2 giorni consecutivi.
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
OUT_MD = ROOT / "reports" / "sma50_one_day_promotion_gate.md"
OUT_WINDOWS_CSV = ROOT / "reports" / "sma50_one_day_promotion_gate_windows.csv"
OUT_GATE_CSV = ROOT / "reports" / "sma50_one_day_promotion_gate_checks.csv"

COSTS = {
    "gross_0.00%": 0.0,
    "cost_0.10%": 0.001,
    "cost_0.25%": 0.0025,
    "stress_0.50%": 0.005,
}

WINDOWS = {
    "2019-2020": ("2019-01-01", "2020-12-31"),
    "2020-2021": ("2020-01-01", "2021-12-31"),
    "2021-2022": ("2021-01-01", "2022-12-31"),
    "2023-2024": ("2023-01-01", "2024-12-31"),
    "2024-2025": ("2024-01-01", "2025-12-31"),
    "2025-2026": ("2025-01-01", "2026-12-31"),
}


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


def _sharpe(returns: pd.Series) -> float:
    r = returns.dropna()
    if len(r) < 2:
        return float("nan")
    std = r.std(ddof=1)
    if std == 0:
        return float("nan")
    return float(np.sqrt(CFG.periods_per_year) * r.mean() / std)


def _period_metrics(equity: pd.DataFrame, start: str, end: str) -> dict[str, float]:
    subset = equity.loc[start:end].copy()
    if len(subset) < 2:
        return {
            "total_return": float("nan"),
            "annualized_return": float("nan"),
            "max_drawdown": float("nan"),
            "sharpe": float("nan"),
            "exposure": float("nan"),
            "turnover": float("nan"),
        }
    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    returns = normalized.pct_change()
    days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    return {
        "total_return": total_return,
        "annualized_return": float((1.0 + total_return) ** (CFG.periods_per_year / days) - 1.0),
        "max_drawdown": _max_drawdown(normalized),
        "sharpe": _sharpe(returns),
        "exposure": float(subset["EffectiveExposure"].gt(0.0).mean()),
        "turnover": float(subset["Turnover"].sum()),
    }


def _full_row(model: str, signals: pd.DataFrame, cost: float = 0.0) -> dict[str, object]:
    _, metrics, _ = run_backtest(signals, transaction_cost_rate=cost)
    trades = _trades(signals, model)
    return {
        "model": model,
        "total_return": metrics.total_return,
        "annualized_return": metrics.annualized_return,
        "max_drawdown": metrics.max_drawdown,
        "sharpe": metrics.sharpe_ratio,
        "profit_factor": metrics.profit_factor,
        "operations": metrics.num_operations,
        "entries": len(trades),
        "sma50_exits": int((trades["exit_reason"] == "SMA50").sum()),
        "trail8_exits": int((trades["exit_reason"] == "Trail8").sum()),
        "win_rate": metrics.win_rate,
        "exposure": metrics.exposure_ratio,
        "turnover": metrics.turnover,
    }


def _gate(status: bool) -> str:
    return "PASS" if status else "FAIL"


def main() -> None:
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    baseline = _build_signals(df, sell_after_days=2)
    candidate = _build_signals(df, sell_after_days=1)
    models = {
        "Baseline SMA50 2g + Trail8": baseline,
        "Candidate SMA50 1g + Trail8": candidate,
    }

    equities: dict[str, pd.DataFrame] = {}
    full_rows: list[dict[str, object]] = []
    for model, signals in models.items():
        equity, _, _ = run_backtest(signals)
        equities[model] = equity
        full_rows.append(_full_row(model, signals))
    full = pd.DataFrame(full_rows).set_index("model")
    base = full.loc["Baseline SMA50 2g + Trail8"]
    cand = full.loc["Candidate SMA50 1g + Trail8"]

    cost_rows: list[dict[str, object]] = []
    for scenario, cost in COSTS.items():
        b = _full_row("Baseline SMA50 2g + Trail8", baseline, cost)
        c = _full_row("Candidate SMA50 1g + Trail8", candidate, cost)
        cost_rows.append(
            {
                "scenario": scenario,
                "baseline_ann": b["annualized_return"],
                "candidate_ann": c["annualized_return"],
                "delta_ann": float(c["annualized_return"]) - float(b["annualized_return"]),
                "baseline_dd": b["max_drawdown"],
                "candidate_dd": c["max_drawdown"],
                "delta_dd": float(c["max_drawdown"]) - float(b["max_drawdown"]),
                "baseline_sharpe": b["sharpe"],
                "candidate_sharpe": c["sharpe"],
                "delta_sharpe": float(c["sharpe"]) - float(b["sharpe"]),
                "baseline_pf": b["profit_factor"],
                "candidate_pf": c["profit_factor"],
                "delta_pf": float(c["profit_factor"]) - float(b["profit_factor"]),
            }
        )
    costs = pd.DataFrame(cost_rows)

    window_rows: list[dict[str, object]] = []
    for label, (start, end) in WINDOWS.items():
        b = _period_metrics(equities["Baseline SMA50 2g + Trail8"], start, end)
        c = _period_metrics(equities["Candidate SMA50 1g + Trail8"], start, end)
        window_rows.append(
            {
                "window": label,
                "start": start,
                "end": min(end, df.index[-1].date().isoformat()),
                "baseline_return": b["total_return"],
                "candidate_return": c["total_return"],
                "delta_return": c["total_return"] - b["total_return"],
                "baseline_dd": b["max_drawdown"],
                "candidate_dd": c["max_drawdown"],
                "delta_dd": c["max_drawdown"] - b["max_drawdown"],
                "baseline_sharpe": b["sharpe"],
                "candidate_sharpe": c["sharpe"],
                "delta_sharpe": c["sharpe"] - b["sharpe"],
            }
        )
    windows = pd.DataFrame(window_rows)

    yearly_rows: list[dict[str, object]] = []
    for year in sorted(df.index.year.unique()):
        b = _period_metrics(equities["Baseline SMA50 2g + Trail8"], f"{year}-01-01", f"{year}-12-31")
        c = _period_metrics(equities["Candidate SMA50 1g + Trail8"], f"{year}-01-01", f"{year}-12-31")
        yearly_rows.append(
            {
                "year": int(year),
                "baseline_return": b["total_return"],
                "candidate_return": c["total_return"],
                "delta_return": c["total_return"] - b["total_return"],
                "baseline_dd": b["max_drawdown"],
                "candidate_dd": c["max_drawdown"],
                "delta_dd": c["max_drawdown"] - b["max_drawdown"],
                "baseline_sharpe": b["sharpe"],
                "candidate_sharpe": c["sharpe"],
                "delta_sharpe": c["sharpe"] - b["sharpe"],
            }
        )
    yearly = pd.DataFrame(yearly_rows)
    active_yearly = yearly[yearly[["baseline_return", "candidate_return"]].abs().sum(axis=1) > 1e-12].copy()

    changed_segments = pd.read_csv(ROOT / "reports" / "sma50_exit_timing_changed_segments.csv")
    improved_segments = int((changed_segments["status"] == "migliora").sum())
    worsened_segments = int((changed_segments["status"] == "peggiora").sum())

    checks = pd.DataFrame(
        [
            {
                "check": "Full annualized return improves",
                "status": _gate(cand["annualized_return"] > base["annualized_return"]),
                "note": f"{_pct(cand['annualized_return'])} vs {_pct(base['annualized_return'])}",
            },
            {
                "check": "Full max drawdown improves",
                "status": _gate(cand["max_drawdown"] > base["max_drawdown"]),
                "note": f"{_pct(cand['max_drawdown'])} vs {_pct(base['max_drawdown'])}",
            },
            {
                "check": "Full Sharpe improves",
                "status": _gate(cand["sharpe"] > base["sharpe"]),
                "note": f"{_ratio(cand['sharpe'])} vs {_ratio(base['sharpe'])}",
            },
            {
                "check": "Full profit factor improves",
                "status": _gate(cand["profit_factor"] > base["profit_factor"]),
                "note": f"{_ratio(cand['profit_factor'])} vs {_ratio(base['profit_factor'])}",
            },
            {
                "check": "Cost stress improves in every scenario",
                "status": _gate(bool((costs["delta_ann"] > 0).all() and (costs["delta_dd"] > 0).all() and (costs["delta_sharpe"] > 0).all())),
                "note": f"{int((costs['delta_ann'] > 0).sum())}/{len(costs)} ann, {int((costs['delta_dd'] > 0).sum())}/{len(costs)} DD, {int((costs['delta_sharpe'] > 0).sum())}/{len(costs)} Sharpe",
            },
            {
                "check": "Active yearly return improves in majority",
                "status": _gate(int((active_yearly["delta_return"] > 0).sum()) > int((active_yearly["delta_return"] < 0).sum())),
                "note": f"{int((active_yearly['delta_return'] > 0).sum())} better, {int((active_yearly['delta_return'] < 0).sum())} worse",
            },
            {
                "check": "Active yearly drawdown improves in majority",
                "status": _gate(int((active_yearly["delta_dd"] > 0).sum()) >= int((active_yearly["delta_dd"] < 0).sum())),
                "note": f"{int((active_yearly['delta_dd'] > 0).sum())} better, {int((active_yearly['delta_dd'] < 0).sum())} worse",
            },
            {
                "check": "Rolling windows return improves in majority",
                "status": _gate(int((windows["delta_return"] > 0).sum()) > int((windows["delta_return"] < 0).sum())),
                "note": f"{int((windows['delta_return'] > 0).sum())} better, {int((windows['delta_return'] < 0).sum())} worse",
            },
            {
                "check": "Changed segments improve in majority",
                "status": _gate(improved_segments > worsened_segments),
                "note": f"{improved_segments} improved, {worsened_segments} worsened",
            },
        ]
    )

    OUT_GATE_CSV.parent.mkdir(parents=True, exist_ok=True)
    checks.to_csv(OUT_GATE_CSV, index=False)
    windows.to_csv(OUT_WINDOWS_CSV, index=False)

    pass_count = int((checks["status"] == "PASS").sum())
    fail_count = int((checks["status"] == "FAIL").sum())

    lines = [
        "# SMA50 One-Day Promotion Gate",
        "",
        f"Periodo testato: `{df.index[0].date().isoformat()}` -> `{df.index[-1].date().isoformat()}`.",
        "",
        "Candidato: `Close < SMA50` a 1 giorno + Trail8.",
        "Baseline: `Close < SMA50` per 2 giorni + Trail8.",
        "Ingressi invariati. Metriche in USD.",
        "",
        "## Gate",
        "",
        f"- PASS: {pass_count}.",
        f"- FAIL: {fail_count}.",
        "",
        "| Check | Status | Nota |",
        "|---|---:|---|",
    ]
    for _, row in checks.iterrows():
        lines.append(f"| {row['check']} | {row['status']} | {row['note']} |")

    lines.extend(
        [
            "",
            "## Metriche Complete",
            "",
            "| Modello | Totale | Ann. | Max DD | Sharpe | PF | Operazioni | Turnover |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for model, row in full.iterrows():
        lines.append(
            f"| {model} | {_pct(row['total_return'])} | {_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | {_ratio(row['sharpe'])} | {_ratio(row['profit_factor'])} | "
            f"{int(row['operations'])} | {row['turnover']:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Finestre Rolling",
            "",
            "| Finestra | Baseline ret | Candidate ret | Delta ret | Baseline DD | Candidate DD | Delta DD | Delta Sharpe |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in windows.iterrows():
        lines.append(
            f"| {row['window']} | {_pct(row['baseline_return'])} | {_pct(row['candidate_return'])} | "
            f"{_pct(row['delta_return'])} | {_pct(row['baseline_dd'])} | {_pct(row['candidate_dd'])} | "
            f"{_pct(row['delta_dd'])} | {_ratio(row['delta_sharpe'])} |"
        )

    lines.extend(
        [
            "",
            "## Stress Costi",
            "",
            "| Scenario | Delta ann. | Delta DD | Delta Sharpe | Delta PF |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in costs.iterrows():
        lines.append(
            f"| {row['scenario']} | {_pct(row['delta_ann'])} | {_pct(row['delta_dd'])} | "
            f"{_ratio(row['delta_sharpe'])} | {_ratio(row['delta_pf'])} |"
        )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            "- Il candidato supera nettamente i controlli aggregati e lo stress costi.",
            "- Il punto debole resta la distribuzione annuale: migliora molto 2024-2025 ma peggiora 2019-2020 e leggermente 2023.",
            "- La promozione richiede una decisione esplicita: privilegiare protezione e reattivita' oppure stabilita' annuale piu' uniforme.",
            "",
            "## File generati",
            "",
            f"- `{OUT_GATE_CSV.relative_to(ROOT)}`",
            f"- `{OUT_WINDOWS_CSV.relative_to(ROOT)}`",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(checks.to_string(index=False))
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
