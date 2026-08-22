"""Confronta la Baseline Trail8 con un Trail9 sperimentale."""

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
from pipeline import evaluation_frame
from scripts.run_rsi_upper_cap_removal import completed_trades
import strategy.signals as signals_module


OUT_MD = PROJECT_ROOT / "reports" / "trailing_stop_8_vs_9.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Backtest Trail8 contro Trail9.")
    parser.add_argument(
        "--as-of",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Ultima candela chiusa inclusa (YYYY-MM-DD).",
    )
    parser.add_argument("--output", type=Path, default=OUT_MD)
    return parser.parse_args()


def signal_frame(indicators: pd.DataFrame, trailing_pct: float) -> pd.DataFrame:
    original = signals_module.TRAILING_STOP_PCT
    try:
        signals_module.TRAILING_STOP_PCT = trailing_pct
        return evaluation_frame(signals_module.compute_signals(indicators))
    finally:
        signals_module.TRAILING_STOP_PCT = original


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


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
        "Trail9 test": signal_frame(indicators, 0.09),
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
                    "exposure": metrics.exposure_ratio,
                }
            )
    metrics_df = pd.DataFrame(rows)

    changed_dates = frames["Trail8 ufficiale"].index[
        frames["Trail8 ufficiale"]["Segnale"] != frames["Trail9 test"]["Segnale"]
    ]
    changed_trades: list[tuple[str, pd.DataFrame]] = []
    for name, frame in frames.items():
        trades = completed_trades(frame, equities[name])
        changed_trades.append(
            (name, trades[(trades["entry"] >= "2023-06-01") & (trades["entry"] <= "2023-08-31")])
        )

    entry_2025 = pd.Timestamp("2025-07-02")
    exit_2025 = pd.Timestamp("2025-08-19")
    path_2025 = indicators.loc[entry_2025:exit_2025, "Close"]
    peak_date = path_2025.idxmax()
    peak_close = float(path_2025.max())
    exit_close = float(path_2025.loc[exit_2025])
    exit_drawdown = exit_close / peak_close - 1.0
    row_exit = indicators.loc[exit_2025]
    momentum = exit_close / float(row_exit["Close_7d_ago"]) - 1.0
    volume_rel = float(row_exit["Volume"]) / float(row_exit["VolumeAvg20"]) - 1.0

    lines = [
        "# Trail8 contro Trail9 - Test sperimentale",
        "",
        f"Data test: `{date.today().isoformat()}`.",
        f"Periodo: `{frames['Trail8 ufficiale'].index[0].date()}` -> "
        f"`{frames['Trail8 ufficiale'].index[-1].date()}`.",
        "",
        "Il test cambia esclusivamente il trailing stop dall'8% al 9%. Tutte le",
        "condizioni di ingresso, le conferme momentum/volume e l'uscita SMA50 restano invariate.",
        "La Baseline ufficiale non viene modificata.",
        "",
        "## Metriche",
        "",
        "| Costi | Modello | Totale | Annualizzato | Max DD | Sharpe | PF | Trade | Esposizione |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in metrics_df.iterrows():
        lines.append(
            f"| {row['cost']} | {row['model']} | {pct(row['total_return'])} | "
            f"{pct(row['annualized_return'])} | {pct(row['max_drawdown'])} | "
            f"{row['sharpe']:.3f} | {row['profit_factor']:.3f} | "
            f"{int(row['operations'])} | {pct(row['exposure'])} |"
        )

    lines.extend(
        [
            "",
            "## Episodi modificati",
            "",
            f"Date con segnale diverso: `{len(changed_dates)}`.",
            "",
            "| Modello | Entrata | Uscita | Rendimento netto taker | DD trade |",
            "|---|---|---|---:|---:|",
        ]
    )
    for name, trades in changed_trades:
        for _, trade in trades.iterrows():
            lines.append(
                f"| {name} | {trade['entry']} | {trade['exit']} | "
                f"{pct(trade['return'])} | {pct(trade['drawdown'])} |"
            )

    lines.extend(
        [
            "",
            "## Uscita 19 agosto 2025",
            "",
            f"- massimo Close post-ingresso: `{peak_close:.2f} USD` il `{peak_date.date()}`;",
            f"- Close di uscita: `{exit_close:.2f} USD`;",
            f"- discesa dal massimo: `{pct(exit_drawdown)}`;",
            f"- momentum 7 giorni: `{pct(momentum)}`;",
            f"- volume relativo: `{pct(volume_rel)}`;",
            "- sia Trail8 sia Trail9 vendono il 19 agosto 2025;",
            "- il successivo ingresso della Baseline resta il 25 agosto 2025.",
            "",
            "## Conclusione",
            "",
            "- Trail9 non risolve l'uscita e il rientro di agosto 2025.",
            "- Sull'intera storia cambia soltanto l'uscita del 2 agosto 2023, ritardandola al 4 agosto.",
            "- Quel ritardo riduce leggermente rendimento, Sharpe e profit factor e aumenta il DD del trade.",
            "- Non ci sono elementi per sostituire Trail8 con Trail9.",
            "",
        ]
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {args.output}")
    print(metrics_df.to_string(index=False))


if __name__ == "__main__":
    main()
