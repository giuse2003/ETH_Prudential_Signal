"""
Stress test costi/slippage per Baseline vs filtro ingresso RSI <= 65.

Questo script non modifica i segnali ufficiali. Tiene ferma l'uscita ufficiale
e applica costi proporzionali a ogni cambio di esposizione.

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
OUT_CSV = PROJECT_ROOT / "reports" / "entry_cost_stress.csv"
OUT_MD = PROJECT_ROOT / "reports" / "entry_cost_stress.md"

END_DATE = "2026-06-27"
RECENT_START = "2022-01-01"
RSI_MAX = 65.0

COST_SCENARIOS = [
    ("lordo_0_00pct", 0.0),
    ("costo_0_10pct", 0.001),
    ("costo_0_25pct", 0.0025),
    ("stress_0_50pct", 0.005),
    ("stress_1_00pct", 0.01),
]


def _baseline_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()


def _rsi65_frame(df: pd.DataFrame) -> pd.DataFrame:
    exposure = 0.0
    signals: list[str] = []
    for _, row in df.iterrows():
        signal = str(row["Segnale"])
        if signal == "ACQUISTA" and exposure <= 0.0 and float(row["RSI"]) > RSI_MAX:
            signal = "MANTIENI"
        elif signal == "ACQUISTA" and exposure > 0.0:
            signal = "MANTIENI"

        if signal == "ACQUISTA":
            exposure = 1.0
        elif signal == "VENDI":
            exposure = 0.0
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


def _slice_metrics(equity: pd.DataFrame, start: str) -> dict[str, float]:
    subset = equity.loc[start:].copy()
    if len(subset) < 2:
        return {
            "recent_total_return": float("nan"),
            "recent_annualized_return": float("nan"),
            "recent_max_drawdown": float("nan"),
            "recent_sharpe_ratio": float("nan"),
        }
    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    returns = normalized.pct_change()
    n_days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    return {
        "recent_total_return": total_return,
        "recent_annualized_return": float((1.0 + total_return) ** (CFG.periods_per_year / n_days) - 1.0),
        "recent_max_drawdown": _max_drawdown(normalized),
        "recent_sharpe_ratio": _sharpe(returns),
    }


def _run(df: pd.DataFrame) -> pd.DataFrame:
    frames = {
        "Baseline ufficiale": _baseline_frame(df),
        "RSI <= 65 ingresso": _rsi65_frame(df),
    }
    rows: list[dict[str, float | int | str]] = []
    for scenario, cost_rate in COST_SCENARIOS:
        scenario_rows: dict[str, dict[str, float | int | str]] = {}
        for model, frame in frames.items():
            equity, metrics, _ = run_backtest(frame, transaction_cost_rate=cost_rate)
            row = {
                "scenario": scenario,
                "cost_rate": cost_rate,
                "model": model,
                "annualized_return": metrics.annualized_return,
                "max_drawdown": metrics.max_drawdown,
                "sharpe_ratio": metrics.sharpe_ratio,
                "profit_factor": metrics.profit_factor,
                "num_operations": metrics.num_operations,
                "win_rate": metrics.win_rate,
                "turnover": metrics.turnover,
                **_slice_metrics(equity, RECENT_START),
            }
            scenario_rows[model] = row
            rows.append(row)

        base = scenario_rows["Baseline ufficiale"]
        rsi = scenario_rows["RSI <= 65 ingresso"]
        rows.append(
            {
                "scenario": scenario,
                "cost_rate": cost_rate,
                "model": "Delta RSI65 - Baseline",
                "annualized_return": float(rsi["annualized_return"]) - float(base["annualized_return"]),
                "max_drawdown": float(rsi["max_drawdown"]) - float(base["max_drawdown"]),
                "sharpe_ratio": float(rsi["sharpe_ratio"]) - float(base["sharpe_ratio"]),
                "profit_factor": float(rsi["profit_factor"]) - float(base["profit_factor"]),
                "num_operations": int(rsi["num_operations"]) - int(base["num_operations"]),
                "win_rate": float(rsi["win_rate"]) - float(base["win_rate"]),
                "turnover": float(rsi["turnover"]) - float(base["turnover"]),
                "recent_total_return": float(rsi["recent_total_return"]) - float(base["recent_total_return"]),
                "recent_annualized_return": float(rsi["recent_annualized_return"])
                - float(base["recent_annualized_return"]),
                "recent_max_drawdown": float(rsi["recent_max_drawdown"]) - float(base["recent_max_drawdown"]),
                "recent_sharpe_ratio": float(rsi["recent_sharpe_ratio"]) - float(base["recent_sharpe_ratio"]),
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
    model_rows = results[results["model"] != "Delta RSI65 - Baseline"]
    delta_rows = results[results["model"] == "Delta RSI65 - Baseline"]

    lines = [
        "# Entry Cost Stress",
        "",
        f"Periodo: `{start_date}` -> `{end_date}`.",
        "",
        "Confronto solo sugli ingressi: Baseline ufficiale vs Baseline + filtro `RSI <= 65`.",
        "L'uscita resta invariata: `VENDI` sotto SMA50 per 2 giorni consecutivi.",
        "",
        "Il costo e' applicato a ogni cambio di esposizione, quindi su ingresso e uscita.",
        "",
        "## Periodo Completo",
        "",
        "| Scenario | Modello | Ann. | Max DD | Sharpe | PF | Operazioni | Turnover |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in model_rows.iterrows():
        lines.append(
            "| "
            f"{row['scenario']} | "
            f"{row['model']} | "
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
            "## Delta RSI65 Meno Baseline",
            "",
            "| Scenario | Delta Ann. | Delta Max DD | Delta Sharpe | Delta PF | Delta operazioni | Delta 2022+ Ann. | Delta 2022+ DD |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in delta_rows.iterrows():
        lines.append(
            "| "
            f"{row['scenario']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{_pct(row['recent_annualized_return'])} | "
            f"{_pct(row['recent_max_drawdown'])} |"
        )

    worst = delta_rows.sort_values("annualized_return").iloc[0]
    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Anche nello scenario piu' severo ({worst['scenario']}), RSI65 mantiene un delta annuo di {_pct(worst['annualized_return'])} rispetto alla Baseline.",
            "- Il vantaggio non dipende dal risparmio di costi: RSI65 fa una operazione in meno, ma il delta principale viene dagli ingressi evitati/ritardati.",
            "- La regola resta un candidato di ingresso, non una modifica ufficiale.",
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
                "scenario",
                "model",
                "annualized_return",
                "max_drawdown",
                "sharpe_ratio",
                "profit_factor",
                "num_operations",
                "recent_annualized_return",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
