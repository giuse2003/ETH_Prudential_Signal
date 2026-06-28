"""
Comparazione finale Baseline vs candidato combinato.

Candidato combinato:
- ingressi Baseline + filtro RSI <= 65;
- uscita ufficiale invariata;
- uscita aggiuntiva Trail8 confermato -5 / vol +20.

Questo script non modifica i segnali ufficiali.
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
OUT_COSTS_CSV = PROJECT_ROOT / "reports" / "final_combined_cost_stress.csv"
OUT_YEARS_CSV = PROJECT_ROOT / "reports" / "final_combined_yearly_validation.csv"
OUT_TRADES_CSV = PROJECT_ROOT / "reports" / "final_combined_trades.csv"
OUT_MD = PROJECT_ROOT / "reports" / "final_combined_candidate_validation.md"

END_DATE = "2026-06-27"
RSI_MAX = 65.0
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


def _combined_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, set[str], int]:
    exposure = 0.0
    peak_close: float | None = None
    signals: list[str] = []
    forced_exit_dates: set[str] = set()
    blocked_new_entries = 0

    for date, row in df.iterrows():
        official = str(row["Segnale"])
        signal = official
        close = float(row["Close"])

        if official == "ACQUISTA" and exposure <= 0.0 and float(row["RSI"]) > RSI_MAX:
            signal = "MANTIENI"
            blocked_new_entries += 1
        elif official == "ACQUISTA" and exposure <= 0.0:
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
                    forced_exit_dates.add(date.date().isoformat())
                    exposure = 0.0
                    peak_close = None

        signals.append(signal)

    out = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    out["Segnale"] = signals
    return out, forced_exit_dates, blocked_new_entries


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
            "max_drawdown": float("nan"),
            "sharpe_ratio": float("nan"),
            "exposure_ratio": float("nan"),
        }
    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    returns = normalized.pct_change()
    return {
        "total_return": float(normalized.iloc[-1] - 1.0),
        "max_drawdown": _max_drawdown(normalized),
        "sharpe_ratio": _sharpe(returns),
        "exposure_ratio": float(subset["EffectiveExposure"].gt(0.0).mean()),
    }


def _cost_stress(base: pd.DataFrame, combined: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for scenario, cost in COST_SCENARIOS:
        _, bm, _ = run_backtest(base, transaction_cost_rate=cost)
        _, cm, _ = run_backtest(combined, transaction_cost_rate=cost)
        for model, m in [("Baseline ufficiale", bm), ("Combinato RSI65 + Trail8 -5/vol20", cm)]:
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
                    "win_rate": m.win_rate,
                    "turnover": m.turnover,
                }
            )
        rows.append(
            {
                "scenario": scenario,
                "cost_rate": cost,
                "model": "Delta combinato - Baseline",
                "annualized_return": cm.annualized_return - bm.annualized_return,
                "max_drawdown": cm.max_drawdown - bm.max_drawdown,
                "sharpe_ratio": cm.sharpe_ratio - bm.sharpe_ratio,
                "profit_factor": cm.profit_factor - bm.profit_factor,
                "num_operations": cm.num_operations - bm.num_operations,
                "win_rate": cm.win_rate - bm.win_rate,
                "turnover": cm.turnover - bm.turnover,
            }
        )
    return pd.DataFrame(rows)


def _yearly(base: pd.DataFrame, combined: pd.DataFrame) -> pd.DataFrame:
    base_eq, _, _ = run_backtest(base)
    combined_eq, _, _ = run_backtest(combined)
    rows: list[dict[str, float | int]] = []
    for year in sorted(base.index.year.unique()):
        bm = _year_metrics(base_eq, int(year))
        cm = _year_metrics(combined_eq, int(year))
        rows.append(
            {
                "year": int(year),
                "baseline_return": bm["total_return"],
                "combined_return": cm["total_return"],
                "delta_return": cm["total_return"] - bm["total_return"],
                "baseline_max_drawdown": bm["max_drawdown"],
                "combined_max_drawdown": cm["max_drawdown"],
                "delta_max_drawdown": cm["max_drawdown"] - bm["max_drawdown"],
                "baseline_sharpe": bm["sharpe_ratio"],
                "combined_sharpe": cm["sharpe_ratio"],
                "delta_sharpe": cm["sharpe_ratio"] - bm["sharpe_ratio"],
            }
        )
    return pd.DataFrame(rows)


def _trades(df: pd.DataFrame, signals: pd.Series, forced_exit_dates: set[str] | None = None) -> pd.DataFrame:
    forced_exit_dates = forced_exit_dates or set()
    exposure = 0.0
    entry_date: pd.Timestamp | None = None
    rows: list[dict[str, float | int | str]] = []
    for date, signal in signals.items():
        if signal == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            entry_date = date
        elif signal == "VENDI" and exposure > 0.0 and entry_date is not None:
            rows.append(_trade_row(df, len(rows) + 1, entry_date, date, "trail8" if date.date().isoformat() in forced_exit_dates else "official"))
            exposure = 0.0
            entry_date = None
    return pd.DataFrame(rows)


def _trade_row(df: pd.DataFrame, trade_id: int, entry_date: pd.Timestamp, exit_date: pd.Timestamp, exit_type: str) -> dict[str, float | int | str]:
    entry = float(df.loc[entry_date, "Close_EUR"])
    exit_ = float(df.loc[exit_date, "Close_EUR"])
    path = df.loc[entry_date:exit_date, "Close_EUR"] / entry
    dd = path / path.cummax() - 1.0
    return {
        "trade_id": trade_id,
        "entry_date": entry_date.date().isoformat(),
        "exit_date": exit_date.date().isoformat(),
        "entry_price_eur": entry,
        "exit_price_eur": exit_,
        "exit_type": exit_type,
        "trade_return": exit_ / entry - 1.0,
        "drawdown_suffered_pct": float(dd.min()),
    }


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(costs: pd.DataFrame, years: pd.DataFrame, trades: pd.DataFrame, out_path: Path, start: str, end: str, blocked_entries: int, forced_exits: int) -> None:
    model_rows = costs[costs["model"] != "Delta combinato - Baseline"]
    deltas = costs[costs["model"] == "Delta combinato - Baseline"]
    better_years = years[years["delta_return"] > 1e-8]
    worse_years = years[years["delta_return"] < -1e-8]
    gross_delta = deltas[deltas["scenario"] == "lordo_0_00pct"].iloc[0]

    lines = [
        "# Final Combined Candidate Validation",
        "",
        f"Periodo: `{start}` -> `{end}`.",
        "",
        "Confronto finale tra Baseline ufficiale e candidato combinato:",
        "",
        "- ingresso: Baseline + `RSI <= 65` sui nuovi `ACQUISTA`;",
        "- uscita: ufficiale + `Trail8 confermato -5 / vol +20`.",
        "",
        f"Ingressi bloccati dal filtro RSI65: {blocked_entries}.",
        f"Uscite forzate Trail8 confermate: {forced_exits}.",
        "",
        "## Stress Costi",
        "",
        "| Scenario | Modello | Ann. | Max DD | Sharpe | PF | Ops | Win rate |",
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
            f"{_pct(row['win_rate'])} |"
        )

    lines.extend(["", "## Delta Combinato Meno Baseline", "", "| Scenario | Delta Ann. | Delta DD | Delta Sharpe | Delta PF | Delta Ops |", "|---|---:|---:|---:|---:|---:|"])
    for _, row in deltas.iterrows():
        lines.append(
            "| "
            f"{row['scenario']} | {_pct(row['annualized_return'])} | {_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | {_ratio(row['profit_factor'])} | {int(row['num_operations'])} |"
        )

    lines.extend(["", "## Validazione Annuale", "", "| Anno | Baseline Ret | Combinato Ret | Delta Ret | Baseline DD | Combinato DD | Delta DD | Baseline Sharpe | Combinato Sharpe |", "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"])
    for _, row in years.iterrows():
        lines.append(
            "| "
            f"{int(row['year'])} | {_pct(row['baseline_return'])} | {_pct(row['combined_return'])} | {_pct(row['delta_return'])} | "
            f"{_pct(row['baseline_max_drawdown'])} | {_pct(row['combined_max_drawdown'])} | {_pct(row['delta_max_drawdown'])} | "
            f"{_ratio(row['baseline_sharpe'])} | {_ratio(row['combined_sharpe'])} |"
        )

    combined_trades = trades[trades["model"] == "Combinato RSI65 + Trail8 -5/vol20"]
    lines.extend(["", "## Operazioni Combinato", "", "| # | Ingresso | Prezzo in | Uscita | Prezzo out | Tipo uscita | Return | DD trade |", "|---:|---|---:|---|---:|---|---:|---:|"])
    for _, row in combined_trades.iterrows():
        lines.append(
            "| "
            f"{int(row['trade_id'])} | {row['entry_date']} | {row['entry_price_eur']:.2f} | "
            f"{row['exit_date']} | {row['exit_price_eur']:.2f} | {row['exit_type']} | "
            f"{_pct(row['trade_return'])} | {_pct(row['drawdown_suffered_pct'])} |"
        )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Delta lordo annualizzato: {_pct(gross_delta['annualized_return'])}.",
            f"- Delta lordo max DD: {_pct(gross_delta['max_drawdown'])}.",
            f"- Anni migliorati: {len(better_years)}.",
            f"- Anni peggiorati: {len(worse_years)}.",
            "- Il combinato va promosso solo se il peggioramento annuale residuo e i segmenti critici sono accettabili.",
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
    combined, forced_dates, blocked_entries = _combined_frame(df)
    costs = _cost_stress(base, combined)
    years = _yearly(base, combined)
    baseline_trades = _trades(df, base["Segnale"])
    baseline_trades.insert(0, "model", "Baseline ufficiale")
    combined_trades = _trades(df, combined["Segnale"], forced_dates)
    combined_trades.insert(0, "model", "Combinato RSI65 + Trail8 -5/vol20")
    trades = pd.concat([baseline_trades, combined_trades], ignore_index=True)
    OUT_COSTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    costs.to_csv(OUT_COSTS_CSV, index=False)
    years.to_csv(OUT_YEARS_CSV, index=False)
    trades.to_csv(OUT_TRADES_CSV, index=False)
    _write_markdown(costs, years, trades, OUT_MD, df.index[0].date().isoformat(), df.index[-1].date().isoformat(), blocked_entries, len(forced_dates))
    print(f"Saved {OUT_COSTS_CSV}")
    print(f"Saved {OUT_YEARS_CSV}")
    print(f"Saved {OUT_TRADES_CSV}")
    print(f"Saved {OUT_MD}")
    print(costs[costs["model"] == "Delta combinato - Baseline"].to_string(index=False))
    print(years[["year", "baseline_return", "combined_return", "delta_return", "baseline_max_drawdown", "combined_max_drawdown", "delta_max_drawdown"]].to_string(index=False))


if __name__ == "__main__":
    main()
