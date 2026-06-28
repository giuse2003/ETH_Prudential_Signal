"""
Validazione del filtro sperimentale RSI sugli ingressi.

Questo script non modifica i segnali ufficiali. Blocca solo in backtest i nuovi
ACQUISTA quando RSI supera una soglia, mantenendo invariati i VENDI ufficiali.

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
OUT_SWEEP_CSV = PROJECT_ROOT / "reports" / "rsi_entry_filter_sweep.csv"
OUT_COSTS_CSV = PROJECT_ROOT / "reports" / "rsi_entry_filter_costs.csv"
OUT_PERIODS_CSV = PROJECT_ROOT / "reports" / "rsi_entry_filter_periods.csv"
OUT_TRADES_CSV = PROJECT_ROOT / "reports" / "rsi_entry_filter_trades.csv"
OUT_MD = PROJECT_ROOT / "reports" / "rsi_entry_filter_validation.md"

RECENT_START = "2022-01-01"
THRESHOLDS = [58, 60, 62, 65, 68, 70, 72, 75]
COST_RATES = {
    "gross_0_00pct": 0.0,
    "cost_0_10pct": 0.001,
    "cost_0_25pct": 0.0025,
    "stress_0_50pct": 0.005,
}


def _variant_name(threshold: int | None) -> str:
    return "baseline" if threshold is None else f"rsi_le_{threshold}"


def _entry_filter_frame(df: pd.DataFrame, threshold: int | None) -> pd.DataFrame:
    out = df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()
    if threshold is None:
        return out

    blocked_buy = (out["Segnale"] == "ACQUISTA") & (df["RSI"] > threshold)
    out.loc[blocked_buy, "Segnale"] = "MANTIENI"
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


def _slice_metrics(equity: pd.DataFrame, start: str, end: str | None = None) -> dict[str, float]:
    subset = equity.loc[start:end].copy()
    if len(subset) < 2:
        return {
            "total_return": float("nan"),
            "annualized_return": float("nan"),
            "max_drawdown": float("nan"),
            "sharpe_ratio": float("nan"),
            "exposure_ratio": float("nan"),
            "turnover": float("nan"),
        }

    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    daily_returns = normalized.pct_change()
    n_days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    annualized_return = float((1.0 + total_return) ** (CFG.periods_per_year / n_days) - 1.0)
    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "max_drawdown": _max_drawdown(normalized),
        "sharpe_ratio": _sharpe(daily_returns),
        "exposure_ratio": float(subset["EffectiveExposure"].gt(0.0).mean()),
        "turnover": float(subset["Turnover"].sum()),
    }


def _completed_trades(df: pd.DataFrame, equity: pd.DataFrame, start: str) -> pd.DataFrame:
    active = equity["EffectiveExposure"].gt(0.0).to_numpy()
    index = list(equity.index)
    start_ts = pd.Timestamp(start)
    trades: list[dict[str, float | int | str | bool]] = []
    entry_pos: int | None = None

    for pos, is_active in enumerate(active):
        if is_active and entry_pos is None:
            entry_pos = pos
            continue

        if not is_active and entry_pos is not None:
            exit_pos = pos
            entry_signal_date = index[max(entry_pos - 1, 0)]
            exit_signal_date = index[max(exit_pos - 1, 0)]
            if entry_signal_date >= start_ts:
                entry_price = float(df.loc[entry_signal_date, "Close_EUR"])
                exit_price = float(df.loc[exit_signal_date, "Close_EUR"])
                path = df.loc[entry_signal_date:exit_signal_date, "Close_EUR"]
                normalized = path / entry_price
                drawdown = normalized / normalized.cummax() - 1.0
                trades.append(
                    {
                        "entry_signal_date": entry_signal_date.date().isoformat(),
                        "exit_signal_date": exit_signal_date.date().isoformat(),
                        "entry_price_eur": entry_price,
                        "exit_price_eur": exit_price,
                        "trade_return": exit_price / entry_price - 1.0,
                        "trade_max_drawdown": float(drawdown.min()),
                        "entry_rsi": float(df.loc[entry_signal_date, "RSI"]),
                        "duration_calendar_days": int((exit_signal_date - entry_signal_date).days),
                    }
                )
            entry_pos = None

    return pd.DataFrame(trades)


def _sweep(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    rows: list[dict[str, float | int | str]] = []
    equities: dict[str, pd.DataFrame] = {}

    for threshold in [None, *THRESHOLDS]:
        variant = _variant_name(threshold)
        frame = _entry_filter_frame(df, threshold)
        equity, metrics, _ = run_backtest(frame)
        equities[variant] = equity
        recent = _slice_metrics(equity, RECENT_START)
        rows.append(
            {
                "variant": variant,
                "threshold": threshold if threshold is not None else float("nan"),
                "full_total_return": metrics.total_return,
                "full_annualized_return": metrics.annualized_return,
                "full_max_drawdown": metrics.max_drawdown,
                "full_sharpe_ratio": metrics.sharpe_ratio,
                "full_profit_factor": metrics.profit_factor,
                "full_num_operations": metrics.num_operations,
                "full_win_rate": metrics.win_rate,
                "full_exposure_ratio": metrics.exposure_ratio,
                "full_turnover": metrics.turnover,
                "recent_total_return": recent["total_return"],
                "recent_annualized_return": recent["annualized_return"],
                "recent_max_drawdown": recent["max_drawdown"],
                "recent_sharpe_ratio": recent["sharpe_ratio"],
                "recent_exposure_ratio": recent["exposure_ratio"],
                "recent_turnover": recent["turnover"],
            }
        )

    return pd.DataFrame(rows), equities


def _costs(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for threshold in [None, 62, 65, 68]:
        variant = _variant_name(threshold)
        frame = _entry_filter_frame(df, threshold)
        for scenario, rate in COST_RATES.items():
            _, metrics, _ = run_backtest(frame, transaction_cost_rate=rate)
            rows.append(
                {
                    "variant": variant,
                    "scenario": scenario,
                    "cost_rate": rate,
                    "annualized_return": metrics.annualized_return,
                    "max_drawdown": metrics.max_drawdown,
                    "sharpe_ratio": metrics.sharpe_ratio,
                    "profit_factor": metrics.profit_factor,
                    "num_operations": metrics.num_operations,
                }
            )
    return pd.DataFrame(rows)


def _periods(equities: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for variant in ["baseline", "rsi_le_65"]:
        equity = equities[variant]
        for year in sorted(equity.index.year.unique()):
            start = f"{year}-01-01"
            end = f"{year}-12-31"
            metrics = _slice_metrics(equity, start, end)
            rows.append(
                {
                    "variant": variant,
                    "year": int(year),
                    **metrics,
                }
            )
    return pd.DataFrame(rows)


def _trade_impact(df: pd.DataFrame, equities: dict[str, pd.DataFrame]) -> pd.DataFrame:
    baseline = _completed_trades(df, equities["baseline"], RECENT_START)
    rsi65 = _completed_trades(df, equities["rsi_le_65"], RECENT_START)
    baseline["variant"] = "baseline"
    rsi65["variant"] = "rsi_le_65"
    return pd.concat([baseline, rsi65], ignore_index=True)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(
    sweep: pd.DataFrame,
    costs: pd.DataFrame,
    periods: pd.DataFrame,
    trades: pd.DataFrame,
    out_path: Path,
) -> None:
    baseline = sweep.loc[sweep["variant"] == "baseline"].iloc[0]
    rsi65 = sweep.loc[sweep["variant"] == "rsi_le_65"].iloc[0]
    sweep_full = sweep.sort_values(["full_sharpe_ratio", "full_annualized_return"], ascending=False)
    sweep_recent = sweep.sort_values(["recent_sharpe_ratio", "recent_annualized_return"], ascending=False)
    cost_focus = costs[costs["variant"].isin(["baseline", "rsi_le_65"])]
    period_pivot = periods[periods["variant"].isin(["baseline", "rsi_le_65"])]
    best_baseline_trades = (
        trades[trades["variant"] == "baseline"]
        .sort_values("trade_return", ascending=False)
        .head(8)
    )
    rsi65_trades = trades[trades["variant"] == "rsi_le_65"]

    lines = [
        "# RSI Entry Filter Validation",
        "",
        "Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.",
        "",
        "Performance misurata in EUR con `Close_EUR`; segnali e indicatori restano quelli ufficiali.",
        "",
        "## Risultato Chiave",
        "",
        f"- Baseline periodo completo: ann. {_pct(baseline['full_annualized_return'])}, "
        f"max DD {_pct(baseline['full_max_drawdown'])}, Sharpe {_ratio(baseline['full_sharpe_ratio'])}.",
        f"- `RSI <= 65` periodo completo: ann. {_pct(rsi65['full_annualized_return'])}, "
        f"max DD {_pct(rsi65['full_max_drawdown'])}, Sharpe {_ratio(rsi65['full_sharpe_ratio'])}.",
        f"- Baseline 2022-oggi: ann. {_pct(baseline['recent_annualized_return'])}, "
        f"max DD {_pct(baseline['recent_max_drawdown'])}, Sharpe {_ratio(baseline['recent_sharpe_ratio'])}.",
        f"- `RSI <= 65` 2022-oggi: ann. {_pct(rsi65['recent_annualized_return'])}, "
        f"max DD {_pct(rsi65['recent_max_drawdown'])}, Sharpe {_ratio(rsi65['recent_sharpe_ratio'])}.",
        "",
        "## Threshold Sweep - Periodo Completo",
        "",
        "| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Win rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in sweep_full.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['full_annualized_return'])} | "
            f"{_pct(row['full_max_drawdown'])} | "
            f"{_ratio(row['full_sharpe_ratio'])} | "
            f"{_ratio(row['full_profit_factor'])} | "
            f"{int(row['full_num_operations'])} | "
            f"{_pct(row['full_win_rate'])} |"
        )

    lines.extend(
        [
            "",
            "## Threshold Sweep - 2022-Oggi",
            "",
            "| Variante | Ann. | Max DD | Sharpe | Esposizione | Turnover |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in sweep_recent.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['recent_annualized_return'])} | "
            f"{_pct(row['recent_max_drawdown'])} | "
            f"{_ratio(row['recent_sharpe_ratio'])} | "
            f"{_pct(row['recent_exposure_ratio'])} | "
            f"{int(row['recent_turnover'])} |"
        )

    lines.extend(
        [
            "",
            "## Costi Operativi - Periodo Completo",
            "",
            "| Variante | Scenario | Ann. | Max DD | Sharpe | PF |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in cost_focus.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | {row['scenario']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} |"
        )

    lines.extend(
        [
            "",
            "## Anni - Baseline vs RSI <= 65",
            "",
            "| Anno | Variante | Return | Max DD | Sharpe | Esposizione |",
            "|---:|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in period_pivot.iterrows():
        lines.append(
            "| "
            f"{int(row['year'])} | {row['variant']} | "
            f"{_pct(row['total_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_pct(row['exposure_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Impatto Sui Migliori Trade Baseline Dal 2022",
            "",
            "| Entry Baseline | Return Baseline | RSI ingresso | Presente in RSI <= 65? |",
            "|---|---:|---:|---|",
        ]
    )
    rsi65_entries = set(rsi65_trades["entry_signal_date"].to_list())
    for _, row in best_baseline_trades.iterrows():
        retained = "si" if row["entry_signal_date"] in rsi65_entries else "no"
        lines.append(
            "| "
            f"{row['entry_signal_date']} | "
            f"{_pct(row['trade_return'])} | "
            f"{row['entry_rsi']:.1f} | "
            f"{retained} |"
        )

    lines.extend(
        [
            "",
            "## Decisione",
            "",
            "- `RSI <= 65` e' una soglia interessante ma non ancora promossa.",
            "- La zona 62-68 produce risultati simili sul periodo completo: questo riduce il rischio che 65 sia un numero puramente casuale.",
            "- Il filtro migliora Sharpe e drawdown sul periodo completo e sul 2022-oggi, ma va ancora validato con walk-forward e congiunto alle uscite protettive.",
            "- Prossimo controllo: confrontare `RSI <= 65` con il candidato trailing 8% momentum/volume, e poi testare la combinazione solo in ambiente sperimentale.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`."
        )

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    sweep, equities = _sweep(df)
    costs = _costs(df)
    periods = _periods(equities)
    trades = _trade_impact(df, equities)

    OUT_SWEEP_CSV.parent.mkdir(parents=True, exist_ok=True)
    sweep.to_csv(OUT_SWEEP_CSV, index=False)
    costs.to_csv(OUT_COSTS_CSV, index=False)
    periods.to_csv(OUT_PERIODS_CSV, index=False)
    trades.to_csv(OUT_TRADES_CSV, index=False)
    _write_markdown(sweep, costs, periods, trades, OUT_MD)

    print(f"Saved {OUT_SWEEP_CSV}")
    print(f"Saved {OUT_COSTS_CSV}")
    print(f"Saved {OUT_PERIODS_CSV}")
    print(f"Saved {OUT_TRADES_CSV}")
    print(f"Saved {OUT_MD}")
    print("")
    print(
        sweep.sort_values(["full_sharpe_ratio", "full_annualized_return"], ascending=False)[
            [
                "variant",
                "full_annualized_return",
                "full_max_drawdown",
                "full_sharpe_ratio",
                "recent_annualized_return",
                "recent_max_drawdown",
                "recent_sharpe_ratio",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
