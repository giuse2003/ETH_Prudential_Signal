"""
Griglia test per uscita SMA50 a 1 giorno con conferme aggiuntive.

Obiettivo:
- non testare solo `Close < SMA50` a 1 giorno;
- aggiungere conferme di profondita', momentum, volume, RSI e combinazioni;
- confrontare tutto lo storico disponibile con Baseline e SMA50 1 giorno pura.

Ingressi e Trail8 restano invariati. Metriche in USD.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backtest.backtest import run_backtest  # noqa: E402
from config import CFG  # noqa: E402
from scripts.run_sma50_exit_timing_test import _build_signals, _trades  # noqa: E402
from strategy.signals import ENTRY_RSI_MAX, _stateful_signals  # noqa: E402


DATA_PATH = ROOT / "data" / "indicators_with_signals.csv"
OUT_MD = ROOT / "reports" / "sma50_exit_confirmation_grid.md"
OUT_CSV = ROOT / "reports" / "sma50_exit_confirmation_grid.csv"
OUT_YEARLY_CSV = ROOT / "reports" / "sma50_exit_confirmation_grid_yearly_top.csv"


@dataclass(frozen=True)
class Variant:
    label: str
    description: str
    kind: str
    extra_condition: pd.Series


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


def _build_conditional_signals(df: pd.DataFrame, extra_condition: pd.Series) -> pd.DataFrame:
    out = df.copy()
    close = out["Close"]
    sma50 = out["SMA50"]
    sma200 = out["SMA200"]
    rsi = out["RSI"]
    volume = out["Volume"]
    volume_avg20 = out["VolumeAvg20"]
    close_momentum = out[f"Close_{CFG.momentum_days}d_ago"]

    official_buy = (
        (close > sma200)
        & (sma50 > sma200)
        & (rsi >= 40)
        & (close > close_momentum)
        & (volume > volume_avg20)
    )
    filtered_buy = official_buy & (rsi <= ENTRY_RSI_MAX)

    below_sma50 = close < sma50
    below_sma50_two_days = below_sma50 & below_sma50.shift(1).fillna(False)
    official_sell = below_sma50_two_days | (below_sma50 & extra_condition.fillna(False))

    signal, trail_hit, trail_confirmed = _stateful_signals(
        df=out,
        official_buy_cond=official_buy,
        filtered_new_entry_cond=filtered_buy,
        official_sell_cond=official_sell,
    )
    out["Segnale"] = signal
    out["Official_Sell_Test"] = official_sell
    out["Trail8_Stop_Hit_Test"] = trail_hit
    out["Trail8_Confirmed_Test"] = trail_confirmed
    return out


def _variants(df: pd.DataFrame) -> list[Variant]:
    close = df["Close"]
    sma50 = df["SMA50"]
    rsi = df["RSI"]
    dist = close / sma50 - 1.0
    momentum7 = close / df["Close_7d_ago"] - 1.0
    volume_rel = df["Volume"] / df["VolumeAvg20"] - 1.0
    day_return = close.pct_change()
    bearish_candle = close < df["Open"]
    sma50_slope_5d = sma50 / sma50.shift(5) - 1.0

    variants: list[Variant] = [
        Variant("SMA50 1 giorno pura", "Close sotto SMA50 gia' al primo giorno.", "plain", pd.Series(True, index=df.index)),
        Variant("1g + candela rossa", "Close sotto SMA50 e candela giornaliera rossa.", "candle", bearish_candle),
        Variant("1g + close < ieri", "Close sotto SMA50 e rendimento giornaliero negativo.", "daily_return", day_return < 0.0),
        Variant("1g + slope SMA50 < 0", "Close sotto SMA50 e SMA50 inclinata negativamente su 5 giorni.", "slope", sma50_slope_5d < 0.0),
    ]

    for threshold in [0.0025, 0.005, 0.0075, 0.01, 0.0125, 0.015, 0.02, 0.03, 0.04, 0.05]:
        variants.append(
            Variant(
                f"1g + distanza <= -{threshold:.2%}",
                f"Close sotto SMA50 di almeno {threshold:.2%}.",
                "distance",
                dist <= -threshold,
            )
        )

    for threshold in [-0.01, -0.02, -0.03, -0.04, -0.05, -0.075, -0.10]:
        variants.append(
            Variant(
                f"1g + momentum7 <= {threshold:.1%}",
                f"Close sotto SMA50 e momentum 7 giorni <= {threshold:.1%}.",
                "momentum",
                momentum7 <= threshold,
            )
        )

    for threshold in [-0.10, 0.0, 0.10, 0.20, 0.50]:
        variants.append(
            Variant(
                f"1g + volume rel >= {threshold:.0%}",
                f"Close sotto SMA50 e volume relativo >= {threshold:.0%}.",
                "volume",
                volume_rel >= threshold,
            )
        )

    for threshold in [40, 42, 45, 48, 50, 52]:
        variants.append(
            Variant(
                f"1g + RSI <= {threshold}",
                f"Close sotto SMA50 e RSI <= {threshold}.",
                "rsi",
                rsi <= threshold,
            )
        )

    for distance in [0.005, 0.01, 0.015, 0.02]:
        for momentum in [-0.02, -0.03, -0.05]:
            variants.append(
                Variant(
                    f"1g + dist -{distance:.1%} OR mom {momentum:.0%}",
                    "Close sotto SMA50 e almeno una conferma fra distanza e momentum.",
                    "distance_or_momentum",
                    (dist <= -distance) | (momentum7 <= momentum),
                )
            )
            variants.append(
                Variant(
                    f"1g + dist -{distance:.1%} AND mom {momentum:.0%}",
                    "Close sotto SMA50 e conferma simultanea di distanza e momentum.",
                    "distance_and_momentum",
                    (dist <= -distance) & (momentum7 <= momentum),
                )
            )

    for distance in [0.005, 0.01, 0.015, 0.02]:
        for volume_threshold in [0.0, 0.10, 0.20]:
            variants.append(
                Variant(
                    f"1g + dist -{distance:.1%} AND vol {volume_threshold:.0%}",
                    "Close sotto SMA50 con rottura minima e volume relativo.",
                    "distance_and_volume",
                    (dist <= -distance) & (volume_rel >= volume_threshold),
                )
            )

    for rsi_threshold in [42, 45, 48, 50]:
        for momentum in [-0.02, -0.03, -0.05]:
            variants.append(
                Variant(
                    f"1g + RSI {rsi_threshold} OR mom {momentum:.0%}",
                    "Close sotto SMA50 e almeno una conferma fra RSI debole e momentum.",
                    "rsi_or_momentum",
                    (rsi <= rsi_threshold) | (momentum7 <= momentum),
                )
            )
            variants.append(
                Variant(
                    f"1g + RSI {rsi_threshold} AND mom {momentum:.0%}",
                    "Close sotto SMA50 con RSI debole e momentum debole insieme.",
                    "rsi_and_momentum",
                    (rsi <= rsi_threshold) & (momentum7 <= momentum),
                )
            )

    return variants


def _summary(model: str, description: str, kind: str, signals: pd.DataFrame) -> dict[str, object]:
    equity, metrics, _ = run_backtest(signals)
    trades = _trades(signals, model)
    return {
        "model": model,
        "description": description,
        "kind": kind,
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
        "equity": equity,
    }


def _period_metrics(equity: pd.DataFrame, year: int) -> dict[str, float]:
    subset = equity.loc[f"{year}-01-01":f"{year}-12-31"]
    if len(subset) < 2:
        return {
            "total_return": float("nan"),
            "max_drawdown": float("nan"),
            "sharpe": float("nan"),
        }
    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    returns = normalized.pct_change()
    return {
        "total_return": float(normalized.iloc[-1] - 1.0),
        "max_drawdown": _max_drawdown(normalized),
        "sharpe": _sharpe(returns),
    }


def _write_report(results: pd.DataFrame, yearly: pd.DataFrame, start: str, end: str) -> None:
    baseline = results[results["model"] == "SMA50 2 giorni + Trail8"].iloc[0]
    pure = results[results["model"] == "SMA50 1 giorno pura"].iloc[0]
    reference_models = ["SMA50 2 giorni + Trail8", "SMA50 1 giorno pura"]
    variants = results[~results["model"].isin(reference_models)].copy()
    top_ann = variants.sort_values(["annualized_return", "sharpe"], ascending=False).head(12)
    top_sharpe = variants.sort_values(["sharpe", "annualized_return"], ascending=False).head(12)
    top_dd = variants.sort_values(["max_drawdown", "annualized_return"], ascending=False).head(12)

    better_than_baseline = variants[
        (variants["annualized_return"] > baseline["annualized_return"])
        & (variants["max_drawdown"] > baseline["max_drawdown"])
        & (variants["sharpe"] > baseline["sharpe"])
    ]
    better_than_pure = variants[
        (variants["annualized_return"] > pure["annualized_return"])
        & (variants["max_drawdown"] >= pure["max_drawdown"])
        & (variants["sharpe"] >= pure["sharpe"])
    ]

    def table(rows: pd.DataFrame) -> list[str]:
        out = [
            "| Modello | Ann. | Totale | Max DD | Sharpe | PF | Operazioni | Turnover |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
        for _, row in rows.iterrows():
            out.append(
                f"| {row['model']} | {_pct(row['annualized_return'])} | {_pct(row['total_return'])} | "
                f"{_pct(row['max_drawdown'])} | {_ratio(row['sharpe'])} | {_ratio(row['profit_factor'])} | "
                f"{int(row['operations'])} | {row['turnover']:.1f} |"
            )
        return out

    lines = [
        "# SMA50 Exit Confirmation Grid",
        "",
        f"Periodo testato: `{start}` -> `{end}`.",
        "",
        "Test sperimentale su tutto lo storico disponibile. Ingressi e Trail8 restano invariati.",
        "La Baseline resta `Close < SMA50` per 2 giorni; le varianti anticipano a 1 giorno solo con una conferma aggiuntiva.",
        "Metriche in USD.",
        "",
        "## Modelli Di Riferimento",
        "",
        *table(results.set_index("model").loc[reference_models].reset_index()),
        "",
        "## Sintesi",
        "",
        f"- Varianti testate oltre ai riferimenti: {len(variants)}.",
        f"- Varianti che battono la Baseline su ann., drawdown e Sharpe: {len(better_than_baseline)}.",
        f"- Varianti che battono o pareggiano la SMA50 1 giorno pura su ann., drawdown e Sharpe: {len(better_than_pure)}.",
        "",
        "## Top Per Rendimento Annualizzato",
        "",
        *table(top_ann),
        "",
        "## Top Per Sharpe",
        "",
        *table(top_sharpe),
        "",
        "## Top Per Drawdown",
        "",
        *table(top_dd),
        "",
        "## Lettura",
        "",
        "- La SMA50 1 giorno pura resta il riferimento piu' forte tra le regole semplici testate.",
        "- Alcune conferme migliorano leggermente il rendimento annualizzato ma non migliorano simultaneamente anche Sharpe e drawdown rispetto alla variante pura.",
        "- I filtri piu' severi riducono operazioni e turnover, ma tendono a perdere uscite utili.",
        "- Le conferme migliori rispetto alla Baseline sono utili come candidati secondari, non come promozione automatica.",
        "",
        "## Annuale Dei Migliori Candidati",
        "",
        "| Anno | Modello | Ret | Max DD | Sharpe | Delta ret vs Baseline | Delta DD vs Baseline |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in yearly.iterrows():
        lines.append(
            f"| {int(row['year'])} | {row['model']} | {_pct(row['total_return'])} | "
            f"{_pct(row['max_drawdown'])} | {_ratio(row['sharpe'])} | "
            f"{_pct(row['delta_return_vs_baseline'])} | {_pct(row['delta_dd_vs_baseline'])} |"
        )

    lines.extend(["", "## File generati", "", f"- `{OUT_CSV.relative_to(ROOT)}`", f"- `{OUT_YEARLY_CSV.relative_to(ROOT)}`"])
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    base_signals = _build_signals(df, sell_after_days=2)
    pure_signals = _build_signals(df, sell_after_days=1)

    rows: list[dict[str, object]] = []
    equities: dict[str, pd.DataFrame] = {}

    for model, description, kind, signals in [
        ("SMA50 2 giorni + Trail8", "Baseline ufficiale uscita SMA50 a 2 giorni.", "baseline", base_signals),
        ("SMA50 1 giorno pura", "Close sotto SMA50 gia' al primo giorno.", "plain", pure_signals),
    ]:
        row = _summary(model, description, kind, signals)
        equities[model] = row.pop("equity")
        rows.append(row)

    for variant in _variants(df):
        signals = _build_conditional_signals(df, variant.extra_condition)
        row = _summary(variant.label, variant.description, variant.kind, signals)
        equities[variant.label] = row.pop("equity")
        rows.append(row)

    results = pd.DataFrame(rows).drop_duplicates(subset=["model"], keep="first")
    baseline = results[results["model"] == "SMA50 2 giorni + Trail8"].iloc[0]
    results["delta_ann_vs_baseline"] = results["annualized_return"] - baseline["annualized_return"]
    results["delta_dd_vs_baseline"] = results["max_drawdown"] - baseline["max_drawdown"]
    results["delta_sharpe_vs_baseline"] = results["sharpe"] - baseline["sharpe"]
    results = results.sort_values(["annualized_return", "sharpe"], ascending=False)

    focus_models = (
        ["SMA50 2 giorni + Trail8", "SMA50 1 giorno pura"]
        + results[~results["model"].isin(["SMA50 2 giorni + Trail8", "SMA50 1 giorno pura"])]
        .head(5)["model"]
        .tolist()
    )
    yearly_rows: list[dict[str, object]] = []
    years = sorted(int(year) for year in df.index.year.unique())
    for year in years:
        base_year = _period_metrics(equities["SMA50 2 giorni + Trail8"], year)
        for model in focus_models:
            metrics = _period_metrics(equities[model], year)
            yearly_rows.append(
                {
                    "year": year,
                    "model": model,
                    **metrics,
                    "delta_return_vs_baseline": metrics["total_return"] - base_year["total_return"],
                    "delta_dd_vs_baseline": metrics["max_drawdown"] - base_year["max_drawdown"],
                    "delta_sharpe_vs_baseline": metrics["sharpe"] - base_year["sharpe"],
                }
            )
    yearly = pd.DataFrame(yearly_rows)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_CSV, index=False)
    yearly.to_csv(OUT_YEARLY_CSV, index=False)
    _write_report(results, yearly, df.index[0].date().isoformat(), df.index[-1].date().isoformat())

    print(results.head(20).to_string(index=False))
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
