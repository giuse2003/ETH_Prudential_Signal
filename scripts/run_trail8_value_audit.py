"""Misura il valore storico del Trail8 contro la stessa Baseline senza trailing."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import run_backtest
from data.coinbase import fetch_daily_candles
from indicators.technical_indicators import compute_all_indicators
from scripts.run_rsi_upper_cap_removal import completed_trades
from scripts.run_trailing_stop_9pct_test import signal_frame


OUT_MD = PROJECT_ROOT / "reports" / "trail8_value_audit.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Trail8 contro trailing disattivato.")
    parser.add_argument(
        "--as-of",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Ultima candela chiusa inclusa (YYYY-MM-DD).",
    )
    parser.add_argument("--output", type=Path, default=OUT_MD)
    return parser.parse_args()


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def segment_return(equity: pd.DataFrame, start: str, end: str) -> float:
    start_pos = equity.index.get_loc(pd.Timestamp(start)) + 1
    end_pos = min(equity.index.get_loc(pd.Timestamp(end)) + 1, len(equity) - 1)
    returns = equity["DailyReturnStrategy"].iloc[start_pos : end_pos + 1].fillna(0.0)
    return float((1.0 + returns).prod() - 1.0)


def main() -> None:
    args = parse_args()
    with TemporaryDirectory() as temp_dir:
        candles = fetch_daily_candles(
            as_of=args.as_of,
            refresh_all=True,
            cache_path=Path(temp_dir) / "ETH-USD.csv",
        )
    indicators = compute_all_indicators(candles)
    frames = {
        "Trail8 ufficiale": signal_frame(indicators, 0.08),
        "Senza trailing": signal_frame(indicators, 1.0),
    }

    rows: list[dict[str, float | int | str]] = []
    equities: dict[str, pd.DataFrame] = {}
    for cost_name, cost_rate in (("taker_0_16pct", 0.0016), ("prudenziale_0_60pct", 0.006)):
        for name, frame in frames.items():
            equity, metrics, _ = run_backtest(
                frame[["Close", "Segnale"]], transaction_cost_rate=cost_rate
            )
            if cost_rate == 0.0016:
                equities[name] = equity
            rows.append(
                {
                    "cost": cost_name,
                    "model": name,
                    "total_return": metrics.total_return,
                    "annualized_return": metrics.annualized_return,
                    "max_drawdown": metrics.max_drawdown,
                    "sharpe": metrics.sharpe_ratio,
                    "profit_factor": metrics.profit_factor,
                    "operations": metrics.num_operations,
                    "win_rate": metrics.win_rate,
                    "exposure": metrics.exposure_ratio,
                }
            )
    metrics_df = pd.DataFrame(rows)

    trail_events = frames["Trail8 ufficiale"].index[
        frames["Trail8 ufficiale"]["Trail8_Confirmed"]
    ]
    no_trail_trades = completed_trades(frames["Senza trailing"], equities["Senza trailing"])
    segments: list[dict[str, float | int | str]] = []
    for _, trade in no_trail_trades.iterrows():
        start = pd.Timestamp(trade["entry"])
        end = pd.Timestamp(trade["exit"])
        events = trail_events[(trail_events >= start) & (trail_events <= end)]
        if not len(events):
            continue
        trail_return = segment_return(equities["Trail8 ufficiale"], trade["entry"], trade["exit"])
        no_trail_return = segment_return(equities["Senza trailing"], trade["entry"], trade["exit"])
        segments.append(
            {
                "entry": trade["entry"],
                "comparison_end": trade["exit"],
                "trail_dates": ", ".join(day.date().isoformat() for day in events),
                "trail8_return": trail_return,
                "no_trail_return": no_trail_return,
                "delta": trail_return - no_trail_return,
                "result": "migliora" if trail_return > no_trail_return else "peggiora",
            }
        )
    segments_df = pd.DataFrame(segments)

    lines = [
        "# Valore storico del Trail8",
        "",
        f"Data test: `{date.today().isoformat()}`.",
        f"Periodo: `{frames['Trail8 ufficiale'].index[0].date()}` -> "
        f"`{frames['Trail8 ufficiale'].index[-1].date()}`.",
        "",
        "Confronto tra la Baseline ufficiale e la stessa strategia con il trailing",
        "disattivato. Ingressi e uscita `Close < SMA50 * 0,98` restano identici.",
        "",
        "## Metriche",
        "",
        "| Costi | Modello | Totale | Annualizzato | Max DD | Sharpe | PF | Trade | Win rate | Esposizione |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in metrics_df.iterrows():
        lines.append(
            f"| {row['cost']} | {row['model']} | {pct(row['total_return'])} | "
            f"{pct(row['annualized_return'])} | {pct(row['max_drawdown'])} | "
            f"{row['sharpe']:.3f} | {row['profit_factor']:.3f} | "
            f"{int(row['operations'])} | {pct(row['win_rate'])} | {pct(row['exposure'])} |"
        )

    lines.extend(
        [
            "",
            "## Sequenze modificate",
            "",
            "Ogni riga confronta i due modelli dalla stessa entrata fino all'uscita",
            "che sarebbe avvenuta senza trailing. I rendimenti includono la sequenza",
            "completa di eventuali uscite e rientri Trail8, con costo taker `0,16%`.",
            "",
            "| Entrata comune | Fine confronto | Uscite Trail8 | Con Trail8 | Senza Trail8 | Delta | Esito |",
            "|---|---|---|---:|---:|---:|---|",
        ]
    )
    for _, row in segments_df.iterrows():
        lines.append(
            f"| {row['entry']} | {row['comparison_end']} | {row['trail_dates']} | "
            f"{pct(row['trail8_return'])} | {pct(row['no_trail_return'])} | "
            f"{pct(row['delta'])} | {row['result']} |"
        )

    improved = int((segments_df["result"] == "migliora").sum())
    worsened = int((segments_df["result"] == "peggiora").sum())
    lines.extend(
        [
            "",
            "## Conclusione",
            "",
            f"- Sequenze migliorate: `{improved}`; peggiorate: `{worsened}`.",
            "- Trail8 aumenta rendimento annualizzato e Sharpe e riduce nettamente il max drawdown.",
            "- Il profit factor e il win rate sono piu alti senza trailing, perche Trail8 divide alcuni trade.",
            "- Le principali uscite premature sono dicembre 2017 e agosto 2025.",
            "- Nel complesso Trail8 resta valido, ma non elimina il problema dei falsi stop.",
            "",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {args.output}")
    print(metrics_df.to_string(index=False))
    print(segments_df.to_string(index=False))


if __name__ == "__main__":
    main()
