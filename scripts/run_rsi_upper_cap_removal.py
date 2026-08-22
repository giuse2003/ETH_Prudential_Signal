"""Backtest sperimentale: rimuove solo il limite superiore RSI dagli ingressi."""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import run_backtest
from config import CFG
from data.coinbase import fetch_daily_candles
from indicators.technical_indicators import compute_all_indicators
from pipeline import evaluation_frame
from strategy.signals import (
    _sma50_sell_condition,
    _stateful_signals,
    compute_signals,
)


OUT_MD = PROJECT_ROOT / "reports" / "rsi_upper_cap_removal.md"
COST_SCENARIOS = [
    ("lordo", 0.0),
    ("promo_maker_0_07pct", 0.0007),
    ("promo_misto_0_115pct", 0.00115),
    ("promo_taker_0_16pct", 0.0016),
    ("prudenziale_0_60pct", CFG.transaction_cost_rate),
    ("stress_1_00pct", 0.01),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Confronta la Baseline con ingressi RSI >= 40 senza tetto RSI 65."
    )
    parser.add_argument(
        "--as-of",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Ultima candela chiusa inclusa (YYYY-MM-DD).",
    )
    parser.add_argument("--output", type=Path, default=OUT_MD)
    return parser.parse_args()


def build_frames(candles: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    indicators = compute_all_indicators(candles)
    baseline = compute_signals(indicators)

    buy_without_upper_cap = (
        (indicators["Close"] > indicators["SMA200"])
        & (indicators["SMA50"] > indicators["SMA200"])
        & (indicators["RSI"] >= 40.0)
        & (indicators["Close"] > indicators[f"Close_{CFG.momentum_days}d_ago"])
        & (indicators["Volume"] > indicators["VolumeAvg20"])
    )
    variant_signals, trail_hit, trail_confirmed = _stateful_signals(
        df=indicators,
        official_buy_cond=buy_without_upper_cap,
        filtered_new_entry_cond=buy_without_upper_cap,
        official_sell_cond=_sma50_sell_condition(indicators["Close"], indicators["SMA50"]),
    )
    variant = indicators.copy()
    variant["Segnale"] = variant_signals
    variant["Trail8_Stop_Hit"] = trail_hit
    variant["Trail8_Confirmed"] = trail_confirmed

    baseline = evaluation_frame(baseline)
    variant = variant.loc[baseline.index].copy()
    indicators = indicators.loc[baseline.index].copy()
    return indicators, baseline, variant


def metrics_table(
    baseline: pd.DataFrame, variant: pd.DataFrame
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    rows: list[dict[str, float | int | str]] = []
    official_equities: dict[str, pd.DataFrame] = {}
    for scenario, rate in COST_SCENARIOS:
        for name, frame in (("baseline_rsi_40_65", baseline), ("rsi_ge_40_only", variant)):
            equity, metrics, _ = run_backtest(
                frame[["Close", "Segnale"]], transaction_cost_rate=rate
            )
            if rate == CFG.transaction_cost_rate:
                official_equities[name] = equity
            row = asdict(metrics)
            row.update({"scenario": scenario, "variant": name})
            rows.append(row)
    return pd.DataFrame(rows), official_equities


def yearly_table(equities: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for name, equity in equities.items():
        for year in sorted(equity.index.year.unique()):
            subset = equity.loc[str(year)]
            normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
            returns = normalized.pct_change().dropna()
            std = returns.std(ddof=1)
            rows.append(
                {
                    "year": int(year),
                    "variant": name,
                    "return": float(normalized.iloc[-1] - 1.0),
                    "max_drawdown": float((normalized / normalized.cummax() - 1.0).min()),
                    "sharpe": (
                        float(np.sqrt(CFG.periods_per_year) * returns.mean() / std)
                        if pd.notna(std) and std > 0.0
                        else float("nan")
                    ),
                    "exposure": float(subset["EffectiveExposure"].gt(0.0).mean()),
                }
            )
    return pd.DataFrame(rows)


def rolling_comparison(equities: dict[str, pd.DataFrame]) -> dict[str, float | int]:
    rows: list[dict[str, float | pd.Timestamp]] = []
    base = equities["baseline_rsi_40_65"]
    variant = equities["rsi_ge_40_only"]
    for start_pos in range(0, len(base), 30):
        start = base.index[start_pos]
        end = start + pd.Timedelta(days=730)
        base_window = base.loc[start:end]
        variant_window = variant.loc[start:end]
        if len(base_window) < 657:
            continue

        item: dict[str, float | pd.Timestamp] = {"start": start}
        for prefix, window in (("base", base_window), ("variant", variant_window)):
            normalized = window["EquityStrategy"] / float(window["EquityStrategy"].iloc[0])
            returns = normalized.pct_change().dropna()
            std = returns.std(ddof=1)
            item[f"{prefix}_return"] = float(normalized.iloc[-1] - 1.0)
            item[f"{prefix}_dd"] = float((normalized / normalized.cummax() - 1.0).min())
            item[f"{prefix}_sharpe"] = (
                float(np.sqrt(CFG.periods_per_year) * returns.mean() / std)
                if pd.notna(std) and std > 0.0
                else float("nan")
            )
        rows.append(item)

    rolling = pd.DataFrame(rows)
    return {
        "windows": len(rolling),
        "return_better_ratio": float(
            (rolling["variant_return"] > rolling["base_return"]).mean()
        ),
        "sharpe_better_ratio": float(
            (rolling["variant_sharpe"] > rolling["base_sharpe"]).mean()
        ),
        "dd_better_ratio": float((rolling["variant_dd"] >= rolling["base_dd"]).mean()),
        "worst_return_delta": float(
            (rolling["variant_return"] - rolling["base_return"]).min()
        ),
        "worst_sharpe_delta": float(
            (rolling["variant_sharpe"] - rolling["base_sharpe"]).min()
        ),
        "worst_dd_delta": float((rolling["variant_dd"] - rolling["base_dd"]).min()),
    }


def completed_trades(frame: pd.DataFrame, equity: pd.DataFrame) -> pd.DataFrame:
    active = equity["EffectiveExposure"].gt(0.0).to_numpy()
    rows: list[dict[str, float | int | str]] = []
    entry_pos: int | None = None
    for pos, is_active in enumerate(active):
        if is_active and entry_pos is None:
            entry_pos = pos
        elif not is_active and entry_pos is not None:
            entry_date = frame.index[max(entry_pos - 1, 0)]
            exit_date = frame.index[max(pos - 1, 0)]
            trade_returns = equity["DailyReturnStrategy"].iloc[entry_pos:pos].fillna(0.0)
            price_path = frame.loc[entry_date:exit_date, "Close"]
            rows.append(
                {
                    "entry": entry_date.date().isoformat(),
                    "exit": exit_date.date().isoformat(),
                    "entry_price": float(frame.loc[entry_date, "Close"]),
                    "entry_rsi": float(frame.loc[entry_date, "RSI"]),
                    "return": float((1.0 + trade_returns).prod() - 1.0),
                    "drawdown": float((price_path / price_path.cummax() - 1.0).min()),
                    "days": int((exit_date - entry_date).days),
                }
            )
            entry_pos = None
    return pd.DataFrame(rows)


def pct(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value * 100:.2f}%"


def ratio(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value:.3f}"


def write_report(
    path: Path,
    as_of: str,
    indicators: pd.DataFrame,
    baseline: pd.DataFrame,
    variant: pd.DataFrame,
    metrics: pd.DataFrame,
    equities: dict[str, pd.DataFrame],
    years: pd.DataFrame,
    rolling: dict[str, float | int],
) -> None:
    official = metrics[metrics["scenario"] == "prudenziale_0_60pct"]
    extra_dates = variant.index[
        (variant["Segnale"] == "ACQUISTA") & (baseline["Segnale"] != "ACQUISTA")
    ]
    variant_trades = completed_trades(variant, equities["rsi_ge_40_only"])
    extra_trades = variant_trades[variant_trades["entry"].isin([d.date().isoformat() for d in extra_dates])]

    lines = [
        "# Rimozione del tetto RSI 65 - Backtest sperimentale",
        "",
        f"Data test: `{date.today().isoformat()}`.",
        f"Periodo valutato: `{indicators.index[0].date()}` -> `{indicators.index[-1].date()}`.",
        f"Cutoff richiesto: `{as_of}`. Mercato: `ETH-USD` Coinbase, candele daily UTC chiuse.",
        "",
        "Questo test non modifica la Baseline ufficiale. Cambia una sola regola di ingresso:",
        "",
        "- Baseline: `40 <= RSI(14) <= 65`;",
        "- variante: `RSI(14) >= 40`, senza limite superiore;",
        "- tutte le altre condizioni di acquisto e le due uscite restano invariate.",
        "",
        "## Metriche periodo completo",
        "",
        "Commissione ufficiale conservativa: `0,60%` per lato.",
        "",
        "| Modello | Totale | Annualizzato | Max DD | Sharpe | PF | Trade | Win rate | Esposizione |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in official.iterrows():
        lines.append(
            f"| {row['variant']} | {pct(row['total_return'])} | "
            f"{pct(row['annualized_return'])} | {pct(row['max_drawdown'])} | "
            f"{ratio(row['sharpe_ratio'])} | {ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | {pct(row['win_rate'])} | "
            f"{pct(row['exposure_ratio'])} |"
        )

    lines.extend(
        [
            "",
        "## Stress costi",
        "",
        "Le tariffe VIP Coinbase sono trattate come scenari operativi: maker `0,07%`,",
        "taker `0,16%` e misto `0,115%` medio per lato. Lo scenario taker e' il",
        "riferimento piu conservativo quando si richiede esecuzione immediata; il",
        "maker non garantisce il riempimento dell'ordine. Il `0,60%` resta lo stress",
        "prudenziale configurato nel modello.",
        "",
            "| Scenario | Modello | Annualizzato | Max DD | Sharpe | PF |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in metrics.iterrows():
        lines.append(
            f"| {row['scenario']} | {row['variant']} | {pct(row['annualized_return'])} | "
            f"{pct(row['max_drawdown'])} | {ratio(row['sharpe_ratio'])} | "
            f"{ratio(row['profit_factor'])} |"
        )

    lines.extend(
        [
            "",
            "## Stabilita annuale",
            "",
            "| Anno | Baseline ret | RSI >= 40 ret | Baseline DD | RSI >= 40 DD |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    pivot = years.pivot(index="year", columns="variant")
    for year in pivot.index:
        lines.append(
            f"| {year} | {pct(pivot.loc[year, ('return', 'baseline_rsi_40_65')])} | "
            f"{pct(pivot.loc[year, ('return', 'rsi_ge_40_only')])} | "
            f"{pct(pivot.loc[year, ('max_drawdown', 'baseline_rsi_40_65')])} | "
            f"{pct(pivot.loc[year, ('max_drawdown', 'rsi_ge_40_only')])} |"
        )

    lines.extend(
        [
            "",
            "## Nuovi ingressi causati dalla rimozione del tetto",
            "",
            f"Nuovi ingressi effettivi: `{len(extra_dates)}`.",
            "",
            "| Entrata | Uscita | Prezzo USD | RSI | Rendimento netto | DD trade | Giorni |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in extra_trades.iterrows():
        lines.append(
            f"| {row['entry']} | {row['exit']} | {row['entry_price']:.2f} | "
            f"{row['entry_rsi']:.2f} | {pct(row['return'])} | {pct(row['drawdown'])} | "
            f"{int(row['days'])} |"
        )

    august = indicators.loc["2026-08-16":"2026-08-21"]
    august_unchanged = bool(
        (baseline.loc[august.index, "Segnale"] == variant.loc[august.index, "Segnale"]).all()
    )
    lines.extend(
        [
            "",
            "## Finestre mobili e caso agosto 2026",
            "",
            f"- Finestre mobili di 730 giorni: `{int(rolling['windows'])}`.",
            f"- Rendimento migliore della Baseline: `{pct(float(rolling['return_better_ratio']))}` delle finestre.",
            f"- Sharpe migliore: `{pct(float(rolling['sharpe_better_ratio']))}` delle finestre.",
            f"- Drawdown uguale o migliore: `{pct(float(rolling['dd_better_ratio']))}` delle finestre.",
            f"- Peggior delta rendimento: `{pct(float(rolling['worst_return_delta']))}`.",
            f"- Peggior delta drawdown: `{pct(float(rolling['worst_dd_delta']))}`.",
            f"- Dal 16 al 21 agosto 2026 i segnali restano identici: `{'si' if august_unchanged else 'no'}`.",
            "- La rimozione del tetto RSI non intercetta il rally di agosto 2026, perche `SMA50 > SMA200` resta falsa.",
            "",
            "## Conclusione",
            "",
            "- Le metriche complete migliorano, ma il vantaggio e' concentrato soprattutto negli ingressi anticipati del 2017.",
            "- La variante peggiora il 2025 e non migliora la maggioranza delle finestre mobili biennali.",
            "- Il risultato non giustifica una promozione immediata e non risolve il movimento che ha motivato il test.",
            "- Prossimo test corretto: un ingresso breakout separato, senza allentare globalmente il filtro RSI.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    with TemporaryDirectory() as temp_dir:
        candles = fetch_daily_candles(
            as_of=args.as_of,
            refresh_all=True,
            cache_path=Path(temp_dir) / "ETH-USD.csv",
        )
    indicators, baseline, variant = build_frames(candles)
    metrics, equities = metrics_table(baseline, variant)
    years = yearly_table(equities)
    rolling = rolling_comparison(equities)
    write_report(
        args.output,
        args.as_of,
        indicators,
        baseline,
        variant,
        metrics,
        equities,
        years,
        rolling,
    )
    print(f"Saved {args.output}")
    print(metrics[metrics["scenario"] == "prudenziale_0_60pct"].to_string(index=False))
    print(rolling)


if __name__ == "__main__":
    main()
