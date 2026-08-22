"""Ricerca sugli ingressi capaci di intercettare il breakout di agosto 2026.

La Baseline ufficiale non viene modificata. Le varianti mantengono identiche
le uscite ufficiali e aggiungono, in alternativa all'ingresso ordinario, un
percorso di breakout precoce o di impulso sopra SMA200.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from datetime import date, timedelta
import hashlib
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import BacktestMetrics, exposure_from_signal, run_backtest
from config import CFG
from data.coinbase import fetch_daily_candles
from indicators.technical_indicators import compute_all_indicators
from pipeline import evaluation_frame
from strategy.signals import (
    ENTRY_RSI_MAX,
    HOLD_ACTION,
    SMA50_BREAK_PCT,
    TRAILING_MOMENTUM_MIN,
    TRAILING_STOP_PCT,
    TRAILING_VOLUME_REL_MIN,
    compute_signals,
)
from scripts.run_trail8_guardrail_walkforward import circular_block_bootstrap
from scripts.run_walk_forward_research import (
    cscv_pbo,
    daily_sharpe_values,
    expected_max_sharpe,
    probabilistic_sharpe,
)


EVENT_START = pd.Timestamp("2026-08-17")
PRE_EVENT_END = pd.Timestamp("2026-08-16")
TARGET_CAPTURE_LATEST = pd.Timestamp("2026-08-18")
TAKER_FEE = 0.0016
FEE_SCENARIOS = {
    "maker_0_07pct": 0.0007,
    "taker_0_16pct": TAKER_FEE,
    "stress_0_60pct": 0.006,
}
OUT_MD = PROJECT_ROOT / "reports" / "august_2026_breakout_entry_research.md"
OUT_METRICS = PROJECT_ROOT / "reports" / "august_2026_breakout_entry_metrics.csv"
OUT_TRADES = PROJECT_ROOT / "reports" / "august_2026_breakout_entry_trades.csv"
OUT_REGIMES = PROJECT_ROOT / "reports" / "august_2026_breakout_entry_regimes.csv"
OUT_COSTS = PROJECT_ROOT / "reports" / "august_2026_breakout_entry_costs.csv"
OUT_STATS = PROJECT_ROOT / "reports" / "august_2026_breakout_entry_statistics.csv"
OUT_SEGMENTS = PROJECT_ROOT / "reports" / "august_2026_breakout_entry_segments.csv"
OUT_DELAYS = PROJECT_ROOT / "reports" / "august_2026_breakout_entry_delays.csv"
OUT_ANCHORED = PROJECT_ROOT / "reports" / "august_2026_breakout_entry_anchored.csv"


@dataclass(frozen=True)
class EntryVariant:
    name: str
    family: str
    description: str
    standard_require_sma50: bool = True
    standard_rsi_max: float | None = ENTRY_RSI_MAX
    early_lookback: int | None = None
    early_volume_rel_min: float = 0.20
    early_max_below_sma200: float = 0.05
    early_sma50_slope5_min: float = 0.0
    impulse_momentum_min: float | None = None
    impulse_volume_rel_min: float = 1.0
    impulse_require_cross: bool = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ricerca ingresso breakout agosto 2026.")
    parser.add_argument(
        "--as-of",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Ultima candela giornaliera chiusa inclusa (YYYY-MM-DD).",
    )
    parser.add_argument("--output", type=Path, default=OUT_MD)
    return parser.parse_args()


def baseline_variant() -> EntryVariant:
    return EntryVariant(
        name="baseline",
        family="baseline",
        description="Baseline ufficiale replicata senza modifiche.",
    )


def _early_name(lookback: int, volume: float, proximity: float, slope: float) -> str:
    return (
        f"early_lb{lookback}_vol{volume * 100:.0f}_near{proximity * 100:.1f}_"
        f"slope{slope * 100:.1f}"
    ).replace(".0", "")


def build_variants() -> list[EntryVariant]:
    base = baseline_variant()
    variants = [
        base,
        replace(
            base,
            name="control_rsi_gt40_only",
            family="control",
            description="Rimuove solo il limite RSI superiore.",
            standard_rsi_max=None,
        ),
        replace(
            base,
            name="control_no_sma50_gate",
            family="control",
            description="Rimuove solo SMA50>SMA200, conservando RSI 40-65.",
            standard_require_sma50=False,
        ),
        replace(
            base,
            name="control_no_sma50_no_rsi_cap",
            family="control",
            description="Rimuove SMA50>SMA200 e il limite RSI superiore.",
            standard_require_sma50=False,
            standard_rsi_max=None,
        ),
    ]

    for lookback in (5, 7, 10):
        for volume in (0.20, 0.50):
            for proximity in (0.05, 0.075, 0.10):
                for slope in (0.0, 0.01, 0.015):
                    variants.append(
                        replace(
                            base,
                            name=_early_name(lookback, volume, proximity, slope),
                            family="early_breakout",
                            description=(
                                f"Breakout {lookback}g, volume +{volume:.0%}, Close entro "
                                f"{proximity:.1%} sotto SMA200, slope SMA50 5g >= {slope:.1%}."
                            ),
                            early_lookback=lookback,
                            early_volume_rel_min=volume,
                            early_max_below_sma200=proximity,
                            early_sma50_slope5_min=slope,
                        )
                    )

    for momentum in (0.10, 0.15, 0.20):
        for volume in (1.0, 2.0):
            for require_cross in (True, False):
                variants.append(
                    replace(
                        base,
                        name=(
                            f"impulse_mom{momentum * 100:.0f}_vol{volume * 100:.0f}_"
                            f"{'cross' if require_cross else 'above'}"
                        ),
                        family="sma200_impulse",
                        description=(
                            f"Impulso sopra SMA200 con momentum >= {momentum:.0%}, "
                            f"volume +{volume:.0%} e "
                            f"{'incrocio giornaliero' if require_cross else 'prezzo gia sopra'}."
                        ),
                        impulse_momentum_min=momentum,
                        impulse_volume_rel_min=volume,
                        impulse_require_cross=require_cross,
                    )
                )

    balanced_name = _early_name(7, 0.20, 0.05, 0.0)
    balanced = next(variant for variant in variants if variant.name == balanced_name)
    variants.append(
        replace(
            balanced,
            name="combo_balanced_plus_impulse",
            family="combined",
            description="Breakout precoce bilanciato piu impulso SMA200 15%/+100%.",
            impulse_momentum_min=0.15,
            impulse_volume_rel_min=1.0,
            impulse_require_cross=True,
        )
    )
    return variants


def add_research_features(indicators: pd.DataFrame) -> pd.DataFrame:
    out = indicators.copy()
    out["Momentum7"] = out["Close"] / out[f"Close_{CFG.momentum_days}d_ago"] - 1.0
    out["VolumeRel20"] = out["Volume"] / out["VolumeAvg20"] - 1.0
    out["SMA50Slope5"] = out["SMA50"] / out["SMA50"].shift(5) - 1.0
    out["DistanceSMA50"] = out["Close"] / out["SMA50"] - 1.0
    out["DistanceSMA200"] = out["Close"] / out["SMA200"] - 1.0
    for lookback in (5, 7, 10):
        out[f"PriorHigh{lookback}"] = (
            out["Close"].shift(1).rolling(lookback, min_periods=lookback).max()
        )
    return out


def _entry_masks(
    df: pd.DataFrame, variant: EntryVariant
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
    close = df["Close"]
    sma50 = df["SMA50"]
    sma200 = df["SMA200"]
    rsi = df["RSI"]
    momentum = df["Momentum7"]
    volume_rel = df["VolumeRel20"]

    baseline_core = (
        (close > sma200)
        & (sma50 > sma200)
        & (rsi >= 40.0)
        & (momentum > 0.0)
        & (volume_rel > 0.0)
    )
    baseline_entry = baseline_core & (rsi <= ENTRY_RSI_MAX)

    standard_core = (
        (close > sma200)
        & (rsi >= 40.0)
        & (momentum > 0.0)
        & (volume_rel > 0.0)
    )
    if variant.standard_require_sma50:
        standard_core &= sma50 > sma200
    standard_entry = standard_core.copy()
    if variant.standard_rsi_max is not None:
        standard_entry &= rsi <= variant.standard_rsi_max

    early = pd.Series(False, index=df.index)
    if variant.early_lookback is not None:
        early = (
            (sma50 <= sma200)
            & (close > sma50)
            & (close >= sma200 * (1.0 - variant.early_max_below_sma200))
            & (df["SMA50Slope5"] >= variant.early_sma50_slope5_min)
            & rsi.between(40.0, ENTRY_RSI_MAX, inclusive="both")
            & (momentum > 0.0)
            & (volume_rel >= variant.early_volume_rel_min)
            & (close > df[f"PriorHigh{variant.early_lookback}"])
        )

    impulse = pd.Series(False, index=df.index)
    if variant.impulse_momentum_min is not None:
        impulse = (
            (sma50 <= sma200)
            & (close > sma200)
            & rsi.between(40.0, 90.0, inclusive="both")
            & (momentum >= variant.impulse_momentum_min)
            & (volume_rel >= variant.impulse_volume_rel_min)
            & (close > df["PriorHigh7"])
        )
        if variant.impulse_require_cross:
            impulse &= close.shift(1) <= sma200.shift(1)

    entry = standard_entry | early | impulse
    relaxed_standard = standard_entry & ~baseline_entry
    return entry, baseline_core, early, impulse, relaxed_standard


def build_signal_frame(df: pd.DataFrame, variant: EntryVariant) -> pd.DataFrame:
    entry, baseline_hold_core, early, impulse, relaxed = _entry_masks(df, variant)
    official_sell = df["Close"] < df["SMA50"] * (1.0 - SMA50_BREAK_PCT)
    signals = np.full(len(df), HOLD_ACTION, dtype=object)
    origins = np.full(len(df), "", dtype=object)
    exposed = False
    peak_close: float | None = None

    for pos, (day, row) in enumerate(df.iterrows()):
        close = float(row["Close"])
        if bool(official_sell.loc[day]):
            signals[pos] = "VENDI"
            origins[pos] = "sma50_exit"
            exposed = False
            peak_close = None
            continue

        if not exposed and bool(entry.loc[day]):
            signals[pos] = "ACQUISTA"
            if bool(early.loc[day]):
                origins[pos] = "early_breakout"
            elif bool(impulse.loc[day]):
                origins[pos] = "sma200_impulse"
            elif bool(relaxed.loc[day]):
                origins[pos] = "relaxed_standard"
            else:
                origins[pos] = "standard"
            exposed = True
            peak_close = close
            continue

        if exposed and bool(baseline_hold_core.loc[day]):
            peak_close = max(peak_close if peak_close is not None else close, close)
            continue

        if exposed:
            peak_close = max(peak_close if peak_close is not None else close, close)
            stop_hit = close <= peak_close * (1.0 - TRAILING_STOP_PCT)
            if stop_hit:
                confirmed = bool(
                    row["Momentum7"] >= TRAILING_MOMENTUM_MIN
                    and row["VolumeRel20"] >= TRAILING_VOLUME_REL_MIN
                )
                if confirmed:
                    signals[pos] = "VENDI"
                    origins[pos] = "trail8_exit"
                    exposed = False
                    peak_close = None

    return pd.DataFrame(
        {"Close": df["Close"], "Segnale": signals, "SignalOrigin": origins},
        index=df.index,
    )


def _fingerprint(signals: pd.Series) -> str:
    payload = "\x1f".join(signals.astype(str)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def extract_trades(
    frame: pd.DataFrame,
    *,
    variant: str,
    fee_rate: float,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    active: dict[str, object] | None = None
    for day, row in frame.iterrows():
        signal = str(row["Segnale"])
        if signal == "ACQUISTA" and active is None:
            active = {
                "entry_date": day,
                "entry_price": float(row["Close"]),
                "entry_origin": str(row["SignalOrigin"]),
            }
        elif signal == "VENDI" and active is not None:
            entry_date = pd.Timestamp(active["entry_date"])
            entry_price = float(active["entry_price"])
            prices = frame.loc[entry_date:day, "Close"]
            path_dd = float((prices / prices.cummax() - 1.0).min())
            rows.append(
                {
                    "variant": variant,
                    **active,
                    "exit_date": day,
                    "exit_price": float(row["Close"]),
                    "exit_origin": str(row["SignalOrigin"]),
                    "status": "closed",
                    "net_return": (
                        float(row["Close"]) / entry_price
                        * (1.0 - fee_rate) ** 2
                        - 1.0
                    ),
                    "max_drawdown": path_dd,
                    "days": int((day - entry_date).days),
                }
            )
            active = None
    if active is not None:
        entry_date = pd.Timestamp(active["entry_date"])
        entry_price = float(active["entry_price"])
        last_day = frame.index[-1]
        last_price = float(frame.iloc[-1]["Close"])
        prices = frame.loc[entry_date:last_day, "Close"]
        rows.append(
            {
                "variant": variant,
                **active,
                "exit_date": pd.NaT,
                "exit_price": np.nan,
                "exit_origin": "",
                "status": "open",
                "net_return": last_price / entry_price * (1.0 - fee_rate) - 1.0,
                "max_drawdown": float((prices / prices.cummax() - 1.0).min()),
                "days": int((last_day - entry_date).days),
            }
        )
    return pd.DataFrame(rows)


def _metrics_dict(metrics: BacktestMetrics, prefix: str) -> dict[str, object]:
    return {f"{prefix}_{key}": value for key, value in asdict(metrics).items()}


def _return_stats(returns: pd.Series) -> dict[str, float]:
    values = returns.fillna(0.0)
    equity = (1.0 + values).cumprod()
    days = max(len(values) - 1, 1)
    total = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    annualized = float((equity.iloc[-1] / equity.iloc[0]) ** (365.0 / days) - 1.0)
    drawdown = float((equity / equity.cummax() - 1.0).min())
    std = float(values.std(ddof=1))
    sharpe = float(np.sqrt(365.0) * values.mean() / std) if std > 0.0 else np.nan
    return {
        "total_return": total,
        "annualized_return": annualized,
        "max_drawdown": drawdown,
        "sharpe_ratio": sharpe,
    }


def evaluate_variants(
    indicators: pd.DataFrame,
    variants: list[EntryVariant],
) -> tuple[pd.DataFrame, dict[str, pd.DataFrame], dict[str, pd.DataFrame], pd.DataFrame]:
    metric_rows: list[dict[str, object]] = []
    frames: dict[str, pd.DataFrame] = {}
    equities: dict[str, pd.DataFrame] = {}
    all_trades: list[pd.DataFrame] = []

    for variant in variants:
        frame = build_signal_frame(indicators, variant)
        equity, full, _ = run_backtest(frame[["Close", "Segnale"]], transaction_cost_rate=TAKER_FEE)
        _, pre, _ = run_backtest(
            frame.loc[:PRE_EVENT_END, ["Close", "Segnale"]],
            transaction_cost_rate=TAKER_FEE,
        )
        trades = extract_trades(frame, variant=variant.name, fee_rate=TAKER_FEE)
        all_trades.append(trades)
        target_buys = frame.loc[EVENT_START:]
        target_buys = target_buys[target_buys["Segnale"] == "ACQUISTA"]
        signal_date = target_buys.index[0] if not target_buys.empty else pd.NaT
        signal_origin = (
            str(target_buys.iloc[0]["SignalOrigin"]) if not target_buys.empty else ""
        )
        if pd.notna(signal_date):
            event_returns = equity.loc[equity.index > signal_date, "DailyReturnStrategy"]
            event_return = float((1.0 + event_returns.fillna(0.0)).prod() - 1.0)
        else:
            event_return = 0.0
        alt_trades = trades[trades["entry_origin"] != "standard"] if not trades.empty else trades
        alt_closed = alt_trades[alt_trades["status"] == "closed"] if not trades.empty else trades
        metric_rows.append(
            {
                "variant": variant.name,
                "family": variant.family,
                "description": variant.description,
                "signal_fingerprint": _fingerprint(frame["Segnale"]),
                **_metrics_dict(full, "full"),
                **_metrics_dict(pre, "pre"),
                "target_signal_date": signal_date,
                "target_signal_origin": signal_origin,
                "captures_main_candle": bool(
                    pd.notna(signal_date) and pd.Timestamp(signal_date) <= TARGET_CAPTURE_LATEST
                ),
                "event_return_to_cutoff": event_return,
                "alternative_entries": len(alt_trades),
                "alternative_closed": len(alt_closed),
                "alternative_losses": int((alt_closed["net_return"] <= 0.0).sum())
                if not alt_closed.empty
                else 0,
                "alternative_win_rate": float((alt_closed["net_return"] > 0.0).mean())
                if not alt_closed.empty
                else np.nan,
                "alternative_avg_return": float(alt_closed["net_return"].mean())
                if not alt_closed.empty
                else np.nan,
            }
        )
        frames[variant.name] = frame
        equities[variant.name] = equity

    metrics = pd.DataFrame(metric_rows)
    trades_out = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    return metrics, frames, equities, trades_out


def select_candidate(metrics: pd.DataFrame) -> str:
    baseline = metrics[metrics["variant"] == "baseline"].iloc[0]
    early = metrics[
        (metrics["family"] == "early_breakout")
        & metrics["captures_main_candle"]
        & (metrics["pre_annualized_return"] >= baseline["pre_annualized_return"])
        & (metrics["pre_max_drawdown"] >= baseline["pre_max_drawdown"] - 0.02)
        & (metrics["pre_sharpe_ratio"] >= baseline["pre_sharpe_ratio"])
    ].copy()
    if early.empty:
        return _early_name(7, 0.20, 0.05, 0.0)
    return str(
        early.sort_values(
            ["pre_sharpe_ratio", "pre_annualized_return", "alternative_losses"],
            ascending=[False, False, True],
        ).iloc[0]["variant"]
    )


def regime_comparison(
    equities: dict[str, pd.DataFrame], candidate: str
) -> pd.DataFrame:
    regimes = {
        "2017-2019": ("2017-01-01", "2019-12-31"),
        "2020-2022": ("2020-01-01", "2022-12-31"),
        "2023-pre-event": ("2023-01-01", PRE_EVENT_END),
    }
    rows: list[dict[str, object]] = []
    for label, (start, end) in regimes.items():
        for model in ("baseline", candidate):
            returns = equities[model].loc[start:end, "DailyReturnStrategy"]
            rows.append({"regime": label, "model": model, **_return_stats(returns)})
    return pd.DataFrame(rows)


def cost_comparison(
    frames: dict[str, pd.DataFrame], candidate: str
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for scenario, fee in FEE_SCENARIOS.items():
        for model in ("baseline", candidate):
            frame = frames[model]
            _, full, _ = run_backtest(
                frame[["Close", "Segnale"]], transaction_cost_rate=fee
            )
            _, pre, _ = run_backtest(
                frame.loc[:PRE_EVENT_END, ["Close", "Segnale"]],
                transaction_cost_rate=fee,
            )
            rows.append(
                {
                    "scenario": scenario,
                    "fee_rate": fee,
                    "model": model,
                    "full_annualized_return": full.annualized_return,
                    "full_max_drawdown": full.max_drawdown,
                    "full_sharpe": full.sharpe_ratio,
                    "pre_annualized_return": pre.annualized_return,
                    "pre_max_drawdown": pre.max_drawdown,
                    "pre_sharpe": pre.sharpe_ratio,
                }
            )
    return pd.DataFrame(rows)


def execution_delay_comparison(
    frames: dict[str, pd.DataFrame], candidate: str
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for extra_delay in (0, 1, 2):
        for model in ("baseline", candidate):
            frame = frames[model]
            desired = exposure_from_signal(frame["Segnale"], CFG.exposure_map)
            desired = desired.ffill().fillna(0.0)
            effective = desired.shift(1 + extra_delay).fillna(0.0)
            turnover = effective.diff().abs().fillna(effective.abs())
            daily = effective * frame["Close"].pct_change() - turnover * TAKER_FEE
            full = _return_stats(daily)
            pre = _return_stats(daily.loc[:PRE_EVENT_END])
            event = _return_stats(daily.loc[EVENT_START:])
            rows.append(
                {
                    "extra_delay_days": extra_delay,
                    "model": model,
                    "pre_annualized_return": pre["annualized_return"],
                    "pre_max_drawdown": pre["max_drawdown"],
                    "pre_sharpe": pre["sharpe_ratio"],
                    "full_annualized_return": full["annualized_return"],
                    "full_max_drawdown": full["max_drawdown"],
                    "full_sharpe": full["sharpe_ratio"],
                    "event_return": event["total_return"],
                }
            )
    return pd.DataFrame(rows)


def anchored_pre2020_validation(
    metrics: pd.DataFrame,
    frames: dict[str, pd.DataFrame],
    equities: dict[str, pd.DataFrame],
) -> tuple[str, pd.DataFrame]:
    names = ["baseline"] + metrics.loc[
        metrics["family"] == "early_breakout", "variant"
    ].tolist()
    seen: set[str] = set()
    training_rows: list[dict[str, object]] = []
    for name in names:
        fingerprint = _fingerprint(frames[name].loc[:"2019-12-31", "Segnale"])
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        stats = _return_stats(
            equities[name].loc[:"2019-12-31", "DailyReturnStrategy"]
        )
        training_rows.append({"variant": name, **stats})
    training = pd.DataFrame(training_rows).set_index("variant")
    baseline_train = training.loc["baseline"]
    eligible = training.drop(index="baseline")
    eligible = eligible[
        (eligible["annualized_return"] > baseline_train["annualized_return"])
        & (eligible["max_drawdown"] >= baseline_train["max_drawdown"] - 0.02)
        & (eligible["sharpe_ratio"] > baseline_train["sharpe_ratio"])
    ]
    selected = (
        "baseline"
        if eligible.empty
        else str(
            eligible.sort_values(
                ["sharpe_ratio", "annualized_return"], ascending=False
            ).index[0]
        )
    )
    rows: list[dict[str, object]] = []
    for period, start, end in (
        ("train_to_2019", None, pd.Timestamp("2019-12-31")),
        ("test_2020_pre_event", pd.Timestamp("2020-01-01"), PRE_EVENT_END),
    ):
        for model in ("baseline", selected):
            returns = equities[model]["DailyReturnStrategy"]
            subset = returns.loc[:end] if start is None else returns.loc[start:end]
            rows.append(
                {
                    "period": period,
                    "model": model,
                    "selected_variant": selected,
                    **_return_stats(subset),
                }
            )
    return selected, pd.DataFrame(rows)


def divergence_segments(
    frames: dict[str, pd.DataFrame],
    equities: dict[str, pd.DataFrame],
    candidate: str,
) -> pd.DataFrame:
    baseline_equity = equities["baseline"]
    candidate_equity = equities[candidate]
    daily_diff = (
        candidate_equity["DailyReturnStrategy"]
        - baseline_equity["DailyReturnStrategy"]
    ).abs() > 1e-15
    group_id = daily_diff.ne(daily_diff.shift(fill_value=False)).cumsum()
    rows: list[dict[str, object]] = []
    for _, mask_group in daily_diff.groupby(group_id):
        if not bool(mask_group.iloc[0]):
            continue
        start = mask_group.index[0]
        end = mask_group.index[-1]
        candidate_returns = candidate_equity.loc[start:end, "DailyReturnStrategy"].fillna(0.0)
        baseline_returns = baseline_equity.loc[start:end, "DailyReturnStrategy"].fillna(0.0)
        candidate_wealth = float((1.0 + candidate_returns).prod())
        baseline_wealth = float((1.0 + baseline_returns).prod())
        prior_signals = frames[candidate].loc[:start]
        prior_signals = prior_signals[prior_signals["Segnale"] == "ACQUISTA"]
        trigger_date = prior_signals.index[-1] if not prior_signals.empty else pd.NaT
        trigger_origin = (
            str(prior_signals.iloc[-1]["SignalOrigin"]) if not prior_signals.empty else ""
        )
        future_baseline = frames["baseline"].loc[start:]
        future_baseline = future_baseline[future_baseline["Segnale"] == "ACQUISTA"]
        baseline_buy = future_baseline.index[0] if not future_baseline.empty else pd.NaT
        rows.append(
            {
                "start": start,
                "end": end,
                "trigger_signal_date": trigger_date,
                "trigger_origin": trigger_origin,
                "baseline_next_buy": baseline_buy,
                "candidate_return": candidate_wealth - 1.0,
                "baseline_return": baseline_wealth - 1.0,
                "wealth_advantage": candidate_wealth / baseline_wealth - 1.0,
                "candidate_exposed_days": int(
                    candidate_equity.loc[start:end, "EffectiveExposure"].gt(0.0).sum()
                ),
                "baseline_exposed_days": int(
                    baseline_equity.loc[start:end, "EffectiveExposure"].gt(0.0).sum()
                ),
                "status": "open" if end == candidate_equity.index[-1] else "closed",
            }
        )
    return pd.DataFrame(rows)


def statistical_validation(
    metrics: pd.DataFrame,
    frames: dict[str, pd.DataFrame],
    equities: dict[str, pd.DataFrame],
    candidate: str,
) -> pd.DataFrame:
    pre_returns: dict[str, pd.Series] = {}
    early_returns: dict[str, pd.Series] = {}
    seen_all: set[str] = set()
    seen_early: set[str] = set()
    family_by_name = metrics.set_index("variant")["family"]
    for name, frame in frames.items():
        fingerprint = _fingerprint(frame.loc[:PRE_EVENT_END, "Segnale"])
        returns = equities[name].loc[:PRE_EVENT_END, "DailyReturnStrategy"].fillna(0.0)
        if fingerprint not in seen_all:
            seen_all.add(fingerprint)
            pre_returns[name] = returns
        if family_by_name.loc[name] == "early_breakout" and fingerprint not in seen_early:
            seen_early.add(fingerprint)
            early_returns[name] = returns
    if "baseline" not in pre_returns:
        pre_returns = {"baseline": equities["baseline"].loc[:PRE_EVENT_END, "DailyReturnStrategy"].fillna(0.0), **pre_returns}
    early_matrix = pd.DataFrame(
        {
            "baseline": equities["baseline"].loc[:PRE_EVENT_END, "DailyReturnStrategy"].fillna(0.0),
            **early_returns,
        }
    )
    all_matrix = pd.DataFrame(pre_returns)
    pbo_all, _ = cscv_pbo(all_matrix, blocks=10, label="all_unique_pre_event")
    pbo_early, _ = cscv_pbo(early_matrix, blocks=10, label="early_unique_pre_event")

    trial_sharpes = daily_sharpe_values(all_matrix)
    benchmark = expected_max_sharpe(trial_sharpes, trials=len(metrics))
    candidate_returns = equities[candidate].loc[:PRE_EVENT_END, "DailyReturnStrategy"].fillna(0.0)
    baseline_returns = equities["baseline"].loc[:PRE_EVENT_END, "DailyReturnStrategy"].fillna(0.0)
    dsr = probabilistic_sharpe(candidate_returns, benchmark_daily_sharpe=benchmark)
    incremental = probabilistic_sharpe(
        candidate_returns - baseline_returns, benchmark_daily_sharpe=0.0
    )
    streams = {
        "baseline": pd.DataFrame({"DailyReturn": baseline_returns}),
        "candidate": pd.DataFrame({"DailyReturn": candidate_returns}),
    }
    bootstrap = pd.concat(
        [
            circular_block_bootstrap(streams, block_days=30),
            circular_block_bootstrap(streams, block_days=90),
        ],
        ignore_index=True,
    )
    rows = [
        {
            "test": "pbo_all_unique_pre_event",
            "value": float(pbo_all["pbo"]),
            "secondary": float(pbo_all["median_test_rank"]),
            "paths": int(pbo_all["paths"]),
        },
        {
            "test": "pbo_early_unique_pre_event",
            "value": float(pbo_early["pbo"]),
            "secondary": float(pbo_early["median_test_rank"]),
            "paths": int(pbo_early["paths"]),
        },
        {
            "test": "deflated_sharpe_71_trials",
            "value": float(dsr["probability"]),
            "secondary": float(benchmark * np.sqrt(365.0)),
            "paths": len(metrics),
        },
        {
            "test": "incremental_psr_candidate_vs_baseline",
            "value": float(incremental["probability"]),
            "secondary": float(incremental["annualized_sharpe"]),
            "paths": 2,
        },
    ]
    for _, row in bootstrap.iterrows():
        rows.append(
            {
                "test": f"bootstrap_{int(row['block_days'])}d",
                "value": float(row["probability_outperform"]),
                "secondary": float(row["p05_wealth_advantage"]),
                "paths": 2,
            }
        )
    return pd.DataFrame(rows)


def _pct(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value * 100:.2f}%"


def _ratio(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value:.3f}"


def write_report(
    path: Path,
    *,
    as_of: str,
    indicators: pd.DataFrame,
    metrics: pd.DataFrame,
    candidate: str,
    regimes: pd.DataFrame,
    costs: pd.DataFrame,
    trades: pd.DataFrame,
    statistics: pd.DataFrame,
    segments: pd.DataFrame,
    delays: pd.DataFrame,
    anchored_selected: str,
    anchored: pd.DataFrame,
) -> None:
    baseline = metrics.set_index("variant").loc["baseline"]
    chosen = metrics.set_index("variant").loc[candidate]
    balanced_name = _early_name(7, 0.20, 0.05, 0.0)
    focus_names = [
        "baseline",
        "control_rsi_gt40_only",
        "control_no_sma50_gate",
        "control_no_sma50_no_rsi_cap",
        balanced_name,
        candidate,
    ]
    impulse = metrics[metrics["family"] == "sma200_impulse"].sort_values(
        ["full_sharpe_ratio", "full_annualized_return"], ascending=False
    )
    if not impulse.empty:
        focus_names.append(str(impulse.iloc[0]["variant"]))
    focus_names = list(dict.fromkeys(focus_names))
    focus = metrics.set_index("variant").loc[focus_names].reset_index()

    early = metrics[metrics["family"] == "early_breakout"].copy()
    pre_all3 = (
        (early["pre_annualized_return"] > baseline["pre_annualized_return"])
        & (early["pre_max_drawdown"] >= baseline["pre_max_drawdown"] - 1e-12)
        & (early["pre_sharpe_ratio"] > baseline["pre_sharpe_ratio"])
    )
    capture = early["captures_main_candle"].astype(bool)
    unique_early = early.drop_duplicates("signal_fingerprint")
    chosen_trades = trades[trades["variant"] == candidate]
    chosen_alt = chosen_trades[chosen_trades["entry_origin"] != "standard"]
    stats = statistics.set_index("test")

    recent = indicators.loc["2026-08-16":as_of].copy()
    movement = float(recent.iloc[-1]["Close"] / recent.iloc[0]["Close"] - 1.0)
    lines = [
        "# Ricerca ingresso breakout agosto 2026",
        "",
        f"Data test: `{date.today().isoformat()}`. Cutoff: `{as_of}`.",
        "Mercato: `ETH-USD` Coinbase, candele daily UTC chiuse.",
        "La Baseline ufficiale non e' stata modificata.",
        "",
        "## Caso osservato",
        "",
        f"Dal Close del 16 agosto al cutoff ETH-USD e' salito di `{_pct(movement)}`.",
        "",
        "| Data | Close USD | SMA50 | SMA200 | RSI | Mom. 7g | Volume rel. | Slope SMA50 5g | Dist. SMA200 | Breakout 7g |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for day, row in recent.iterrows():
        breakout = row["Close"] / row["PriorHigh7"] - 1.0
        lines.append(
            f"| {day.date().isoformat()} | {row['Close']:.2f} | {row['SMA50']:.2f} | "
            f"{row['SMA200']:.2f} | {row['RSI']:.2f} | {_pct(row['Momentum7'])} | "
            f"{_pct(row['VolumeRel20'])} | {_pct(row['SMA50Slope5'])} | "
            f"{_pct(row['DistanceSMA200'])} | {_pct(breakout)} |"
        )

    lines.extend(
        [
            "",
            "Il 17 agosto erano verdi RSI, momentum, volume e struttura sopra SMA50.",
            "Erano rossi Close>SMA200 e SMA50>SMA200. Il 19 agosto il Close ha",
            "superato SMA200, ma RSI era gia' sopra 82: la Baseline e' quindi rimasta fuori.",
            "",
            "## Regole provate",
            "",
            "- controlli: rimozione isolata del limite RSI e/o del gate SMA50>SMA200;",
            "- breakout precoce: Close sopra SMA50 e massimo precedente, SMA50 crescente,",
            "  RSI 40-65, volume forte e prezzo non troppo lontano sotto SMA200;",
            "- impulso SMA200: rottura sopra SMA200 con momentum e volume eccezionali,",
            "  consentendo RSI alto;",
            "- uscite sempre identiche alla Baseline: Close 2% sotto SMA50 oppure Trail8",
            "  confermato da momentum >= -15% e volume relativo >= +20%;",
            "- la condizione di ingresso alternativa apre soltanto la posizione: non la",
            "  mantiene e non sospende il Trail8. Dopo l'ingresso vale esclusivamente la",
            "  gestione Baseline, inclusa la priorita' del suo BUY core originale.",
            "",
            "## Confronto principale",
            "",
            "`Pre-evento` termina il 16 agosto 2026 e impedisce al rialzo studiato",
            "di migliorare artificialmente la valutazione storica della variante.",
            "",
            "| Variante | Segnale target | Origine | Cattura candela 19/8 | Evento al cutoff | Ann. pre | DD pre | Sharpe pre | Ann. completo | DD completo | Sharpe completo | Ingressi alternativi | Loss alternativi |",
            "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in focus.iterrows():
        signal_date = (
            pd.Timestamp(row["target_signal_date"]).date().isoformat()
            if pd.notna(row["target_signal_date"])
            else "nessuno"
        )
        lines.append(
            f"| {row['variant']} | {signal_date} | {row['target_signal_origin'] or '-'} | "
            f"{'SI' if row['captures_main_candle'] else 'NO'} | "
            f"{_pct(row['event_return_to_cutoff'])} | {_pct(row['pre_annualized_return'])} | "
            f"{_pct(row['pre_max_drawdown'])} | {_ratio(row['pre_sharpe_ratio'])} | "
            f"{_pct(row['full_annualized_return'])} | {_pct(row['full_max_drawdown'])} | "
            f"{_ratio(row['full_sharpe_ratio'])} | {int(row['alternative_entries'])} | "
            f"{int(row['alternative_losses'])} |"
        )

    lines.extend(
        [
            "",
            "## Stabilita della famiglia precoce",
            "",
            f"- combinazioni testate: `{len(early)}`; percorsi distinti: "
            f"`{early['signal_fingerprint'].nunique()}`;",
            f"- combinazioni che catturano la candela principale: `{_pct(float(capture.mean()))}`;",
            f"- combinazioni che migliorano annualizzato, DD e Sharpe prima dell'evento: "
            f"`{_pct(float(pre_all3.mean()))}`;",
            f"- combinazioni che fanno entrambe le cose: "
            f"`{_pct(float((capture & pre_all3).mean()))}`;",
            f"- sui soli percorsi distinti, cattura target: "
            f"`{_pct(float(unique_early['captures_main_candle'].mean()))}`.",
            "",
            "## Candidato esplorativo selezionato",
            "",
            f"`{candidate}`: {chosen['description']}",
            "",
            f"- segnale sul caso corrente: `{pd.Timestamp(chosen['target_signal_date']).date().isoformat() if pd.notna(chosen['target_signal_date']) else 'nessuno'}`;",
            f"- rendimento simulato dal segnale al cutoff: `{_pct(chosen['event_return_to_cutoff'])}`;",
            f"- prima dell'evento: annualizzato `{_pct(chosen['pre_annualized_return'])}`, "
            f"DD `{_pct(chosen['pre_max_drawdown'])}`, Sharpe `{_ratio(chosen['pre_sharpe_ratio'])}`;",
            f"- Baseline prima dell'evento: annualizzato `{_pct(baseline['pre_annualized_return'])}`, "
            f"DD `{_pct(baseline['pre_max_drawdown'])}`, Sharpe `{_ratio(baseline['pre_sharpe_ratio'])}`;",
            f"- ingressi alternativi storici: `{len(chosen_alt)}`, di cui "
            f"`{int(((chosen_alt['status'] == 'closed') & (chosen_alt['net_return'] <= 0.0)).sum())}` chiusi in perdita.",
            "",
            "## Regimi precedenti",
            "",
            "| Periodo | Modello | Totale | Annualizzato | Max DD | Sharpe |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in regimes.iterrows():
        lines.append(
            f"| {row['regime']} | {row['model']} | {_pct(row['total_return'])} | "
            f"{_pct(row['annualized_return'])} | {_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Sensibilita ai costi",
            "",
            "| Scenario | Modello | Ann. pre | DD pre | Sharpe pre | Ann. completo | DD completo | Sharpe completo |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in costs.iterrows():
        lines.append(
            f"| {row['scenario']} | {row['model']} | {_pct(row['pre_annualized_return'])} | "
            f"{_pct(row['pre_max_drawdown'])} | {_ratio(row['pre_sharpe'])} | "
            f"{_pct(row['full_annualized_return'])} | {_pct(row['full_max_drawdown'])} | "
            f"{_ratio(row['full_sharpe'])} |"
        )

    lines.extend(
        [
            "",
            "## Stress ritardo di esecuzione",
            "",
            "Il ritardo indicato si aggiunge allo shift prudenziale gia presente nel",
            "backtest ufficiale.",
            "",
            "| Ritardo extra | Modello | Evento al cutoff | Ann. pre | DD pre | Sharpe pre | Ann. completo | DD completo | Sharpe completo |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in delays.iterrows():
        lines.append(
            f"| {int(row['extra_delay_days'])}g | {row['model']} | "
            f"{_pct(row['event_return'])} | {_pct(row['pre_annualized_return'])} | "
            f"{_pct(row['pre_max_drawdown'])} | {_ratio(row['pre_sharpe'])} | "
            f"{_pct(row['full_annualized_return'])} | {_pct(row['full_max_drawdown'])} | "
            f"{_ratio(row['full_sharpe'])} |"
        )

    lines.extend(
        [
            "",
            "## Segmenti divergenti dalla Baseline",
            "",
            "Ogni riga comprende un periodo continuo in cui i rendimenti giornalieri",
            "del candidato differiscono da quelli della Baseline, inclusi i costi.",
            "",
            "| Trigger | Origine | Fine segmento | Buy Baseline successivo | Return candidato | Return Baseline | Vantaggio ricchezza | Stato |",
            "|---|---|---|---|---:|---:|---:|---|",
        ]
    )
    for _, row in segments.iterrows():
        trigger = (
            pd.Timestamp(row["trigger_signal_date"]).date().isoformat()
            if pd.notna(row["trigger_signal_date"])
            else "-"
        )
        baseline_buy = (
            pd.Timestamp(row["baseline_next_buy"]).date().isoformat()
            if pd.notna(row["baseline_next_buy"])
            else "nessuno"
        )
        lines.append(
            f"| {trigger} | {row['trigger_origin']} | "
            f"{pd.Timestamp(row['end']).date().isoformat()} | {baseline_buy} | "
            f"{_pct(row['candidate_return'])} | {_pct(row['baseline_return'])} | "
            f"{_pct(row['wealth_advantage'])} | {row['status']} |"
        )

    lines.extend(
        [
            "",
            "## Controlli statistici pre-evento",
            "",
            "| Controllo | Risultato | Lettura secondaria | Percorsi/prove |",
            "|---|---:|---:|---:|",
            f"| PBO tutti i percorsi distinti | {_pct(stats.loc['pbo_all_unique_pre_event', 'value'])} | rank test mediano {_pct(stats.loc['pbo_all_unique_pre_event', 'secondary'])} | {int(stats.loc['pbo_all_unique_pre_event', 'paths'])} |",
            f"| PBO famiglia breakout precoce | {_pct(stats.loc['pbo_early_unique_pre_event', 'value'])} | rank test mediano {_pct(stats.loc['pbo_early_unique_pre_event', 'secondary'])} | {int(stats.loc['pbo_early_unique_pre_event', 'paths'])} |",
            f"| Deflated Sharpe corretto per 71 prove | {_pct(stats.loc['deflated_sharpe_71_trials', 'value'])} | benchmark Sharpe {_ratio(stats.loc['deflated_sharpe_71_trials', 'secondary'])} | 71 |",
            f"| Probabilita vantaggio incrementale | {_pct(stats.loc['incremental_psr_candidate_vs_baseline', 'value'])} | Sharpe differenziale {_ratio(stats.loc['incremental_psr_candidate_vs_baseline', 'secondary'])} | 2 |",
            f"| Bootstrap blocchi 30g | {_pct(stats.loc['bootstrap_30d', 'value'])} | percentile 5% {_pct(stats.loc['bootstrap_30d', 'secondary'])} | 2 |",
            f"| Bootstrap blocchi 90g | {_pct(stats.loc['bootstrap_90d', 'value'])} | percentile 5% {_pct(stats.loc['bootstrap_90d', 'secondary'])} | 2 |",
            "",
            "## Selezione cronologica ancorata",
            "",
            "La scelta usa soltanto i rendimenti fino al 31 dicembre 2019; il periodo",
            "2020-16 agosto 2026 viene valutato senza cambiare i parametri.",
            f"Variante selezionata dal solo training: `{anchored_selected}`.",
            "",
            "| Periodo | Modello | Totale | Annualizzato | Max DD | Sharpe |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in anchored.iterrows():
        lines.append(
            f"| {row['period']} | {row['model']} | {_pct(row['total_return'])} | "
            f"{_pct(row['annualized_return'])} | {_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Interpretazione",
            "",
            "- il caso corrente e' conosciuto e ha generato la domanda: non e' un test",
            "  fuori campione e non puo' autorizzare da solo una nuova regola;",
            "- il controllo pre-evento e i regimi precedenti servono a verificare se il",
            "  percorso alternativo aveva gia' comportamento ragionevole prima del caso;",
            "- la selezione resta esplorativa. Nessun segnale ufficiale, dashboard o bot",
            "  viene modificato da questo report.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> None:
    args = parse_args()
    with TemporaryDirectory() as temp_dir:
        candles = fetch_daily_candles(
            as_of=args.as_of,
            refresh_all=True,
            cache_path=Path(temp_dir) / "ETH-USD.csv",
        )
    indicators_all = compute_all_indicators(candles)
    official = evaluation_frame(compute_signals(indicators_all))
    indicators = add_research_features(evaluation_frame(indicators_all))
    variants = build_variants()
    metrics, frames, equities, trades = evaluate_variants(indicators, variants)

    if not frames["baseline"]["Segnale"].equals(official.loc[indicators.index, "Segnale"]):
        mismatch = int(
            (frames["baseline"]["Segnale"] != official.loc[indicators.index, "Segnale"]).sum()
        )
        raise AssertionError(f"Replica Baseline non esatta: {mismatch} segnali diversi.")

    candidate = select_candidate(metrics)
    regimes = regime_comparison(equities, candidate)
    costs = cost_comparison(frames, candidate)
    segments = divergence_segments(frames, equities, candidate)
    statistics = statistical_validation(metrics, frames, equities, candidate)
    delays = execution_delay_comparison(frames, candidate)
    anchored_selected, anchored = anchored_pre2020_validation(
        metrics, frames, equities
    )

    OUT_METRICS.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUT_METRICS, index=False)
    trades.to_csv(OUT_TRADES, index=False)
    regimes.to_csv(OUT_REGIMES, index=False)
    costs.to_csv(OUT_COSTS, index=False)
    statistics.to_csv(OUT_STATS, index=False)
    segments.to_csv(OUT_SEGMENTS, index=False)
    delays.to_csv(OUT_DELAYS, index=False)
    anchored.to_csv(OUT_ANCHORED, index=False)
    write_report(
        args.output,
        as_of=args.as_of,
        indicators=indicators,
        metrics=metrics,
        candidate=candidate,
        regimes=regimes,
        costs=costs,
        trades=trades,
        statistics=statistics,
        segments=segments,
        delays=delays,
        anchored_selected=anchored_selected,
        anchored=anchored,
    )

    baseline = metrics.set_index("variant").loc["baseline"]
    chosen = metrics.set_index("variant").loc[candidate]
    print(f"Saved {args.output}")
    print(f"Variants: {len(metrics)}; unique paths: {metrics['signal_fingerprint'].nunique()}")
    print(f"Candidate: {candidate}")
    print(
        "PRE baseline/candidate: "
        f"ann {baseline['pre_annualized_return']:.2%}/{chosen['pre_annualized_return']:.2%}, "
        f"DD {baseline['pre_max_drawdown']:.2%}/{chosen['pre_max_drawdown']:.2%}, "
        f"Sharpe {baseline['pre_sharpe_ratio']:.3f}/{chosen['pre_sharpe_ratio']:.3f}"
    )
    print(
        f"Target signal: {chosen['target_signal_date']} "
        f"({chosen['target_signal_origin']}), event return {chosen['event_return_to_cutoff']:.2%}"
    )
    print(statistics.to_string(index=False))
    print(f"Anchored pre-2020 selection: {anchored_selected}")
    print(anchored.to_string(index=False))


if __name__ == "__main__":
    main()
