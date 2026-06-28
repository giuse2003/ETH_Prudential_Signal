"""
Analisi qualita' ingressi Baseline.

Questo script non modifica i segnali ufficiali. Usa i segnali gia' generati
in data/indicators_with_signals.csv e misura i trade in EUR tramite Close_EUR.

Obiettivo:
- separare ingressi vincenti e perdenti;
- registrare gli indicatori presenti alla data del segnale;
- creare una base dati per testare filtri di ingresso senza overfitting.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import run_backtest


SOURCE_CSV = PROJECT_ROOT / "data" / "indicators_with_signals.csv"
OUT_TRADES_CSV = PROJECT_ROOT / "reports" / "entry_quality_trades.csv"
OUT_SUMMARY_CSV = PROJECT_ROOT / "reports" / "entry_quality_summary.csv"
OUT_MD = PROJECT_ROOT / "reports" / "entry_quality_analysis.md"

DEFAULT_START = "2022-01-01"


FEATURE_COLUMNS = [
    "rsi",
    "distance_sma50_pct",
    "distance_sma200_pct",
    "sma50_slope_10d_pct",
    "sma200_slope_20d_pct",
    "momentum_7d_pct",
    "momentum_14d_pct",
    "momentum_30d_pct",
    "volume_rel_pct",
    "atr_close_pct",
    "position_52w_pct",
    "days_since_previous_exit",
    "entry_vs_previous_exit_pct",
]


def _safe_pct(numerator: float, denominator: float) -> float:
    if denominator == 0 or pd.isna(denominator):
        return float("nan")
    return float(numerator / denominator - 1.0)


def _feature_snapshot(df: pd.DataFrame, signal_date: pd.Timestamp) -> dict[str, float]:
    row = df.loc[signal_date]
    close = float(row["Close"])
    high52 = float(row["High52w"])
    low52 = float(row["Low52w"])
    range52 = high52 - low52

    return {
        "rsi": float(row["RSI"]),
        "distance_sma50_pct": _safe_pct(close, float(row["SMA50"])),
        "distance_sma200_pct": _safe_pct(close, float(row["SMA200"])),
        "sma50_slope_10d_pct": _safe_pct(float(row["SMA50"]), float(df["SMA50"].shift(10).loc[signal_date])),
        "sma200_slope_20d_pct": _safe_pct(float(row["SMA200"]), float(df["SMA200"].shift(20).loc[signal_date])),
        "momentum_7d_pct": _safe_pct(close, float(row["Close_7d_ago"])),
        "momentum_14d_pct": _safe_pct(close, float(df["Close"].shift(14).loc[signal_date])),
        "momentum_30d_pct": _safe_pct(close, float(df["Close"].shift(30).loc[signal_date])),
        "volume_rel_pct": _safe_pct(float(row["Volume"]), float(row["VolumeAvg20"])),
        "atr_close_pct": _safe_pct(float(row["ATR"]) + close, close),
        "position_52w_pct": float((close - low52) / range52) if range52 > 0 else float("nan"),
    }


def _price_path_stats(prices: pd.Series) -> dict[str, float]:
    normalized = prices / float(prices.iloc[0])
    drawdown = normalized / normalized.cummax() - 1.0
    return {
        "trade_max_drawdown": float(drawdown.min()),
        "trade_max_gain": float(normalized.max() - 1.0),
        "trade_min_return_from_entry": float(normalized.min() - 1.0),
    }


def _completed_trades(df: pd.DataFrame, equity: pd.DataFrame, start: str) -> pd.DataFrame:
    index = list(equity.index)
    active = equity["EffectiveExposure"].gt(0.0).to_numpy()
    start_ts = pd.Timestamp(start)

    trades: list[dict[str, float | int | str]] = []
    entry_pos: int | None = None
    previous_exit_signal_date: pd.Timestamp | None = None
    previous_exit_price_eur: float | None = None

    for pos, is_active in enumerate(active):
        if is_active and entry_pos is None:
            entry_pos = pos
            continue

        if not is_active and entry_pos is not None:
            exit_pos = pos
            entry_effective_date = index[entry_pos]
            exit_effective_date = index[exit_pos]
            entry_signal_pos = max(entry_pos - 1, 0)
            exit_signal_pos = max(exit_pos - 1, 0)
            entry_signal_date = index[entry_signal_pos]
            exit_signal_date = index[exit_signal_pos]

            if entry_signal_date >= start_ts:
                entry_price_eur = float(df.loc[entry_signal_date, "Close_EUR"])
                exit_price_eur = float(df.loc[exit_signal_date, "Close_EUR"])
                trade_return = exit_price_eur / entry_price_eur - 1.0
                path = df.loc[entry_signal_date:exit_signal_date, "Close_EUR"]
                stats = _price_path_stats(path)
                snapshot = _feature_snapshot(df, entry_signal_date)

                days_since_exit = (
                    (entry_signal_date - previous_exit_signal_date).days
                    if previous_exit_signal_date is not None
                    else float("nan")
                )
                entry_vs_previous_exit = (
                    entry_price_eur / previous_exit_price_eur - 1.0
                    if previous_exit_price_eur is not None and previous_exit_price_eur > 0
                    else float("nan")
                )

                trades.append(
                    {
                        "entry_signal_date": entry_signal_date.date().isoformat(),
                        "entry_effective_date": entry_effective_date.date().isoformat(),
                        "exit_signal_date": exit_signal_date.date().isoformat(),
                        "exit_effective_date": exit_effective_date.date().isoformat(),
                        "entry_price_eur": entry_price_eur,
                        "exit_price_eur": exit_price_eur,
                        "trade_return": trade_return,
                        "is_winner": bool(trade_return > 0.0),
                        "duration_calendar_days": int((exit_signal_date - entry_signal_date).days),
                        "active_return_days": int(exit_pos - entry_pos),
                        "days_since_previous_exit": days_since_exit,
                        "previous_exit_price_eur": previous_exit_price_eur,
                        "entry_vs_previous_exit_pct": entry_vs_previous_exit,
                        **stats,
                        **snapshot,
                    }
                )

            previous_exit_signal_date = exit_signal_date
            previous_exit_price_eur = float(df.loc[exit_signal_date, "Close_EUR"])
            entry_pos = None

    return pd.DataFrame(trades)


def _summary(trades: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    for feature in FEATURE_COLUMNS:
        winners = trades.loc[trades["is_winner"], feature].dropna()
        losers = trades.loc[~trades["is_winner"], feature].dropna()
        rows.append(
            {
                "feature": feature,
                "winner_mean": float(winners.mean()) if not winners.empty else float("nan"),
                "loser_mean": float(losers.mean()) if not losers.empty else float("nan"),
                "winner_median": float(winners.median()) if not winners.empty else float("nan"),
                "loser_median": float(losers.median()) if not losers.empty else float("nan"),
                "delta_mean_winner_minus_loser": (
                    float(winners.mean() - losers.mean())
                    if not winners.empty and not losers.empty
                    else float("nan")
                ),
                "winner_count": int(winners.count()),
                "loser_count": int(losers.count()),
            }
        )
    return pd.DataFrame(rows)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _num(value: float | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.{digits}f}"


def _write_markdown(trades: pd.DataFrame, summary: pd.DataFrame, out_path: Path, start: str, end: str) -> None:
    winners = trades[trades["is_winner"]]
    losers = trades[~trades["is_winner"]]
    best = trades.sort_values("trade_return", ascending=False).head(5)
    worst = trades.sort_values("trade_return", ascending=True).head(5)
    ranked_features = summary.copy()
    ranked_features["abs_delta"] = ranked_features["delta_mean_winner_minus_loser"].abs()
    ranked_features = ranked_features.sort_values("abs_delta", ascending=False).head(8)

    lines = [
        "# Entry Quality Analysis",
        "",
        "Questa analisi e' solo ricerca. Non modifica i segnali ufficiali.",
        "",
        f"Periodo analizzato: `{start}` -> `{end}`.",
        "Performance misurata in EUR con `Close_EUR`; segnali e indicatori restano quelli ufficiali della Baseline.",
        "",
        "## Sintesi",
        "",
        f"- Trade chiusi analizzati: {len(trades)}.",
        f"- Trade vincenti: {len(winners)}.",
        f"- Trade perdenti: {len(losers)}.",
        f"- Win rate: {_pct(len(winners) / len(trades) if len(trades) else float('nan'))}.",
        f"- Rendimento medio trade: {_pct(float(trades['trade_return'].mean()) if len(trades) else float('nan'))}.",
        f"- Rendimento mediano trade: {_pct(float(trades['trade_return'].median()) if len(trades) else float('nan'))}.",
        f"- Drawdown medio interno trade: {_pct(float(trades['trade_max_drawdown'].mean()) if len(trades) else float('nan'))}.",
        "",
        "## Migliori Trade",
        "",
        "| Entry signal | Exit signal | Return | Max DD trade | RSI | Vol rel | Mom 30g | Dist SMA200 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in best.iterrows():
        lines.append(
            "| "
            f"{row['entry_signal_date']} | {row['exit_signal_date']} | "
            f"{_pct(row['trade_return'])} | {_pct(row['trade_max_drawdown'])} | "
            f"{_num(row['rsi'], 1)} | {_pct(row['volume_rel_pct'])} | "
            f"{_pct(row['momentum_30d_pct'])} | {_pct(row['distance_sma200_pct'])} |"
        )

    lines.extend(
        [
            "",
            "## Peggiori Trade",
            "",
            "| Entry signal | Exit signal | Return | Max DD trade | RSI | Vol rel | Mom 30g | Dist SMA200 |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in worst.iterrows():
        lines.append(
            "| "
            f"{row['entry_signal_date']} | {row['exit_signal_date']} | "
            f"{_pct(row['trade_return'])} | {_pct(row['trade_max_drawdown'])} | "
            f"{_num(row['rsi'], 1)} | {_pct(row['volume_rel_pct'])} | "
            f"{_pct(row['momentum_30d_pct'])} | {_pct(row['distance_sma200_pct'])} |"
        )

    lines.extend(
        [
            "",
            "## Differenze Medie Vincitori vs Perdenti",
            "",
            "| Feature | Media vincenti | Media perdenti | Delta |",
            "|---|---:|---:|---:|",
        ]
    )
    for _, row in ranked_features.iterrows():
        feature = row["feature"]
        as_pct = feature != "rsi" and feature != "days_since_previous_exit"
        if as_pct:
            winner = _pct(row["winner_mean"])
            loser = _pct(row["loser_mean"])
            delta = _pct(row["delta_mean_winner_minus_loser"])
        else:
            winner = _num(row["winner_mean"], 2)
            loser = _num(row["loser_mean"], 2)
            delta = _num(row["delta_mean_winner_minus_loser"], 2)
        lines.append(f"| {feature} | {winner} | {loser} | {delta} |")

    lines.extend(
        [
            "",
            "## Prima Lettura",
            "",
            "- Il campione dal 2022 e' piccolo: 17 trade chiusi. Le differenze sono utili per generare ipotesi, non per promuovere subito regole.",
            "- Il filtro di ingresso va testato solo dopo aver verificato che non elimini i migliori trade.",
            "- Il prossimo passo e' trasformare le feature piu' promettenti in filtri sperimentali e confrontarle contro Baseline, costi e sottoperiodi.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main(start: str = DEFAULT_START) -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`."
        )

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    frame_eur = df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"})
    equity, _, _ = run_backtest(frame_eur)

    trades = _completed_trades(df, equity, start)
    if trades.empty:
        raise RuntimeError(f"Nessun trade completato trovato da {start}.")

    summary = _summary(trades)

    OUT_TRADES_CSV.parent.mkdir(parents=True, exist_ok=True)
    trades.to_csv(OUT_TRADES_CSV, index=False)
    summary.to_csv(OUT_SUMMARY_CSV, index=False)
    _write_markdown(trades, summary, OUT_MD, start, df.index.max().date().isoformat())

    print(f"Saved {OUT_TRADES_CSV}")
    print(f"Saved {OUT_SUMMARY_CSV}")
    print(f"Saved {OUT_MD}")
    print("")
    print(
        trades[
            [
                "entry_signal_date",
                "exit_signal_date",
                "trade_return",
                "trade_max_drawdown",
                "rsi",
                "volume_rel_pct",
                "momentum_30d_pct",
                "distance_sma200_pct",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    arg_start = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_START
    main(arg_start)
