"""Confronta la strategia ETH con Buy & Hold includendo le commissioni.

Lo script usa in sola lettura i segnali e il manifest di una baseline congelata.
Non modifica regole, dati o artefatti della baseline ufficiale.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import BacktestMetrics, run_backtest  # noqa: E402
from config import CFG  # noqa: E402
from reproducibility import verify_frozen_artifacts  # noqa: E402


DEFAULT_MANIFEST = (
    PROJECT_ROOT / "docs" / "runs" / "baseline-v1-2026-07-26" / "manifest.json"
)
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "coinbase_fee_0_6_comparison.md"


def buy_hold_net_return(gross_return: float, fee_rate: float) -> float:
    """Applica una commissione all'acquisto iniziale e alla vendita finale."""
    return (1.0 + gross_return) * (1.0 - fee_rate) ** 2 - 1.0


def annualized_return(total_return: float, observations: int) -> float:
    periods = max(observations - 1, 1)
    return (1.0 + total_return) ** (CFG.periods_per_year / periods) - 1.0


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _ratio(value: float) -> str:
    return f"{value:.3f}"


def _pp(value: float) -> str:
    return f"{value * 100:.2f} p.p."


def _money(value: float) -> str:
    sign = "-" if value < 0.0 else ""
    return f"{sign}USD {abs(value):,.2f}"


def load_frozen_signals(manifest_path: Path) -> tuple[pd.DataFrame, dict]:
    verification = verify_frozen_artifacts(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    signals_path = manifest_path.parent / "historical_signals.csv"
    frame = (
        pd.read_csv(signals_path, parse_dates=["Data"])
        .sort_values("Data")
        .set_index("Data")
        .rename(columns={"Azione": "Segnale"})
    )
    required = {"Close", "Segnale"}
    if not required.issubset(frame.columns):
        missing = ", ".join(sorted(required - set(frame.columns)))
        raise ValueError(f"Segnali congelati incompleti: mancano {missing}.")
    if len(frame) != int(verification["period"]["observations"]):
        raise ValueError("Il numero di osservazioni non coincide con il manifest verificato.")
    return frame[["Close", "Segnale"]], manifest


def build_report(
    frame: pd.DataFrame,
    manifest: dict,
    fee_rate: float,
    initial_capital: float,
) -> str:
    gross_equity, gross_strategy, gross_buy_hold = run_backtest(
        frame,
        initial_capital=initial_capital,
    )
    net_equity, net_strategy, _ = run_backtest(
        frame,
        initial_capital=initial_capital,
        transaction_cost_rate=fee_rate,
    )

    buy_hold_total_net = buy_hold_net_return(gross_buy_hold.total_return, fee_rate)
    buy_hold_annualized_net = annualized_return(buy_hold_total_net, len(frame))
    strategy_final_gross = float(gross_equity["EquityStrategy"].iloc[-1])
    strategy_final_net = float(net_equity["EquityStrategy"].iloc[-1])
    buy_hold_final_gross = initial_capital * (1.0 + gross_buy_hold.total_return)
    buy_hold_final_net = initial_capital * (1.0 + buy_hold_total_net)

    final_exposure = float(net_equity["EffectiveExposure"].iloc[-1])
    if final_exposure != 0.0:
        raise ValueError(
            "La strategia termina con una posizione aperta: serve esplicitare la liquidazione finale."
        )

    period = manifest["period"]
    snapshot_hash = manifest["input"]["snapshot_sha256"]
    round_trip_cost = 1.0 - (1.0 - fee_rate) ** 2
    drawdown_advantage = net_strategy.max_drawdown - gross_buy_hold.max_drawdown

    lines = [
        f"# Coinbase ETH Backtest - Commissione {_pct(fee_rate)}",
        "",
        "## Perimetro",
        "",
        f"- Mercato: `{manifest['market']}` da `{manifest['data_source']}`.",
        f"- Periodo comune: `{period['evaluation_start']}` -> `{period['evaluation_end']}`.",
        f"- Osservazioni giornaliere: {period['observations']}.",
        f"- Capitale iniziale ipotetico: {_money(initial_capital)}.",
        f"- Commissione per lato: {_pct(fee_rate)}.",
        f"- Costo composto acquisto + vendita: {_pct(round_trip_cost)}.",
        "- Strategia: costo applicato dal motore a ogni cambio completo di esposizione.",
        "- Buy & Hold: un acquisto alla data iniziale e una vendita alla data finale.",
        "- Per Buy & Hold i costi iniziale e finale incidono su rendimento e capitale; max drawdown e Sharpe descrivono la serie del prezzo detenuto.",
        "- Slippage, spread e imposte: esclusi.",
        "",
        "## Confronto Netto",
        "",
        "| Metrica | Strategia prudenziale | Buy & Hold | Delta strategia - B&H |",
        "|---|---:|---:|---:|",
        f"| Rendimento totale | {_pct(net_strategy.total_return)} | {_pct(buy_hold_total_net)} | {_pp(net_strategy.total_return - buy_hold_total_net)} |",
        f"| Rendimento annualizzato | {_pct(net_strategy.annualized_return)} | {_pct(buy_hold_annualized_net)} | {_pp(net_strategy.annualized_return - buy_hold_annualized_net)} |",
        f"| Max drawdown | {_pct(net_strategy.max_drawdown)} | {_pct(gross_buy_hold.max_drawdown)} | {_pp(drawdown_advantage)} |",
        f"| Sharpe | {_ratio(net_strategy.sharpe_ratio)} | {_ratio(gross_buy_hold.sharpe_ratio)} | {_ratio(net_strategy.sharpe_ratio - gross_buy_hold.sharpe_ratio)} |",
        f"| Capitale finale | {_money(strategy_final_net)} | {_money(buy_hold_final_net)} | {_money(strategy_final_net - buy_hold_final_net)} |",
        "",
        "## Operativita Strategia",
        "",
        f"- Operazioni complete: {net_strategy.num_operations}.",
        f"- Lati soggetti a commissione: {int(net_strategy.turnover)}.",
        f"- Win rate netto: {_pct(net_strategy.win_rate)}.",
        f"- Profit factor netto: {_ratio(net_strategy.profit_factor)}.",
        f"- Esposizione media: {_pct(net_strategy.exposure_ratio)}.",
        "- Posizione finale: chiusa; la commissione dell'ultima vendita e inclusa.",
        "",
        "## Impatto Commissioni",
        "",
        "| Modello | Capitale finale lordo | Capitale finale netto | Riduzione finale |",
        "|---|---:|---:|---:|",
        f"| Strategia prudenziale | {_money(strategy_final_gross)} | {_money(strategy_final_net)} | {_money(strategy_final_gross - strategy_final_net)} |",
        f"| Buy & Hold | {_money(buy_hold_final_gross)} | {_money(buy_hold_final_net)} | {_money(buy_hold_final_gross - buy_hold_final_net)} |",
        "",
        "La riduzione finale include anche il rendimento composto non maturato sul capitale assorbito dalle commissioni; non rappresenta soltanto la somma nominale degli addebiti.",
        "",
        "## Lettura",
        "",
        f"- Buy & Hold prevale sul rendimento netto totale di {_pp(buy_hold_total_net - net_strategy.total_return)} e sul rendimento annualizzato di {_pp(buy_hold_annualized_net - net_strategy.annualized_return)}.",
        f"- La strategia riduce il max drawdown di {_pp(drawdown_advantage)} rispetto al Buy & Hold.",
        f"- La strategia mantiene uno Sharpe superiore di {_ratio(net_strategy.sharpe_ratio - gross_buy_hold.sharpe_ratio)}.",
        "- Il costo dello 0,6% per lato penalizza sensibilmente la strategia perche viene applicato su 72 cambi di esposizione, contro i due soli lati del Buy & Hold.",
        "",
        "## Integrita Baseline",
        "",
        f"- Baseline letta in sola lettura: `{manifest['run_id']}`.",
        f"- Snapshot Coinbase SHA-256: `{snapshot_hash}`.",
        "- Regole, sorgenti, manifest e artefatti congelati non sono stati modificati.",
    ]
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Confronta strategia ETH e Buy & Hold con commissioni simmetriche."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--fee-rate", type=float, default=0.006)
    parser.add_argument("--initial-capital", type=float, default=10_000.0)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not 0.0 <= args.fee_rate < 1.0:
        raise ValueError("--fee-rate deve essere compreso tra 0 e 1 escluso.")
    if args.initial_capital <= 0.0:
        raise ValueError("--initial-capital deve essere positivo.")

    manifest_path = args.manifest.resolve()
    frame, manifest = load_frozen_signals(manifest_path)
    report = build_report(frame, manifest, args.fee_rate, args.initial_capital)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8", newline="\n")
    print(report)
    print(f"Report scritto in: {args.output.resolve()}")


if __name__ == "__main__":
    main()
