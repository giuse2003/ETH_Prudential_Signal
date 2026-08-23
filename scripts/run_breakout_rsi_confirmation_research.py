"""Confronto mirato delle condizioni RSI e conferma prezzo del breakout.

La Baseline ufficiale resta invariata. Ogni variante aggiunge soltanto un
percorso di ingresso alternativo; dopo l'acquisto usa le uscite Baseline.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from datetime import date, timedelta
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import exposure_from_signal, run_backtest
from config import CFG
from data.coinbase import fetch_daily_candles
from indicators.technical_indicators import compute_all_indicators
from pipeline import evaluation_frame
from scripts.run_august_2026_breakout_entry_research import (
    EVENT_START,
    FEE_SCENARIOS,
    PRE_EVENT_END,
    TAKER_FEE,
    _entry_masks,
    _fingerprint,
    _return_stats,
    add_research_features,
    baseline_variant,
    build_signal_frame,
    extract_trades,
)
from scripts.run_trail8_guardrail_walkforward import circular_block_bootstrap
from scripts.run_walk_forward_research import (
    cscv_pbo,
    daily_sharpe_values,
    expected_max_sharpe,
    probabilistic_sharpe,
)
from strategy.signals import (
    HOLD_ACTION,
    SMA50_BREAK_PCT,
    TRAILING_MOMENTUM_MIN,
    TRAILING_STOP_PCT,
    TRAILING_VOLUME_REL_MIN,
    compute_signals,
)


OUT_MD = PROJECT_ROOT / "reports" / "breakout_rsi_confirmation_research.md"
OUT_METRICS = PROJECT_ROOT / "reports" / "breakout_rsi_confirmation_metrics.csv"
OUT_ENTRIES = PROJECT_ROOT / "reports" / "breakout_rsi_confirmation_entries.csv"
OUT_TRIGGERS = PROJECT_ROOT / "reports" / "breakout_rsi_confirmation_triggers.csv"
OUT_YEARLY = PROJECT_ROOT / "reports" / "breakout_rsi_confirmation_yearly.csv"
OUT_COSTS = PROJECT_ROOT / "reports" / "breakout_rsi_confirmation_costs.csv"
OUT_DELAYS = PROJECT_ROOT / "reports" / "breakout_rsi_confirmation_delays.csv"
OUT_STATS = PROJECT_ROOT / "reports" / "breakout_rsi_confirmation_statistics.csv"

CURRENT = "current_rsi40_65_mom7_high5"
RSI40_LEGACY = "rsi40_mom7_high5"
MEAN7_CAPPED = "rsi40_65_mean7"
MEAN7 = "rsi40_mean7"
HIGH7_CAPPED = "rsi40_65_high7"
HIGH7 = "rsi40_high7"

FOCUS_NAMES = [
    "baseline",
    CURRENT,
    RSI40_LEGACY,
    MEAN7_CAPPED,
    MEAN7,
    HIGH7_CAPPED,
    HIGH7,
]


@dataclass(frozen=True)
class BreakoutRule:
    name: str
    label: str
    rsi_max: float | None
    confirmation: str
    lookback: int = 7
    diagnostic: bool = False


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ricerca RSI e conferma prezzo del breakout precoce."
    )
    parser.add_argument(
        "--as-of",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Ultima candela daily chiusa inclusa (YYYY-MM-DD).",
    )
    parser.add_argument("--output", type=Path, default=OUT_MD)
    return parser.parse_args()


def build_rules() -> list[BreakoutRule]:
    return [
        BreakoutRule(
            CURRENT,
            "Attuale: RSI 40-65, momentum7 e massimo5",
            65.0,
            "legacy",
            5,
        ),
        BreakoutRule(
            RSI40_LEGACY,
            "RSI >=40, momentum7 e massimo5",
            None,
            "legacy",
            5,
        ),
        BreakoutRule(
            MEAN7_CAPPED,
            "RSI 40-65, Close sopra media7 precedente",
            65.0,
            "mean",
            7,
        ),
        BreakoutRule(
            MEAN7,
            "Proposta: RSI >=40 e Close sopra media7 precedente",
            None,
            "mean",
            7,
        ),
        BreakoutRule(
            HIGH7_CAPPED,
            "RSI 40-65, Close sopra massimo7 precedente",
            65.0,
            "high",
            7,
        ),
        BreakoutRule(
            HIGH7,
            "RSI >=40 e Close sopra massimo7 precedente",
            None,
            "high",
            7,
        ),
        BreakoutRule(
            "rsi40_65_mean7_mom7",
            "Diagnostica: RSI 40-65, media7 e momentum7",
            65.0,
            "mean_momentum",
            7,
            True,
        ),
        BreakoutRule(
            "rsi40_mean7_mom7",
            "Diagnostica: RSI >=40, media7 e momentum7",
            None,
            "mean_momentum",
            7,
            True,
        ),
        BreakoutRule(
            "rsi40_mean5",
            "Sensibilita': RSI >=40 e media5",
            None,
            "mean",
            5,
            True,
        ),
        BreakoutRule(
            "rsi40_mean10",
            "Sensibilita': RSI >=40 e media10",
            None,
            "mean",
            10,
            True,
        ),
        BreakoutRule(
            "rsi40_high5",
            "Diagnostica: RSI >=40 e massimo5 senza momentum7",
            None,
            "high",
            5,
            True,
        ),
        BreakoutRule(
            "rsi40_high10",
            "Sensibilita': RSI >=40 e massimo10",
            None,
            "high",
            10,
            True,
        ),
        BreakoutRule(
            "rsi40_momentum7_only",
            "Diagnostica: RSI >=40 e solo momentum7",
            None,
            "momentum",
            7,
            True,
        ),
    ]


def add_confirmation_features(indicators: pd.DataFrame) -> pd.DataFrame:
    out = add_research_features(indicators)
    for lookback in (5, 7, 10):
        out[f"PriorMean{lookback}"] = (
            out["Close"].shift(1).rolling(lookback, min_periods=lookback).mean()
        )
    return out


def breakout_mask(df: pd.DataFrame, rule: BreakoutRule) -> pd.Series:
    close = df["Close"]
    common = (
        (df["SMA50"] <= df["SMA200"])
        & (close > df["SMA50"])
        & (close >= df["SMA200"] * 0.90)
        & (df["SMA50Slope5"] >= 0.0)
        & (df["RSI"] >= 40.0)
        & (df["VolumeRel20"] >= 0.20)
    )
    if rule.rsi_max is not None:
        common &= df["RSI"] <= rule.rsi_max

    if rule.confirmation == "legacy":
        confirmation = (
            (df["Momentum7"] > 0.0)
            & (close > df[f"PriorHigh{rule.lookback}"])
        )
    elif rule.confirmation == "mean":
        confirmation = close > df[f"PriorMean{rule.lookback}"]
    elif rule.confirmation == "mean_momentum":
        confirmation = (
            (close > df[f"PriorMean{rule.lookback}"])
            & (df["Momentum7"] > 0.0)
        )
    elif rule.confirmation == "high":
        confirmation = close > df[f"PriorHigh{rule.lookback}"]
    elif rule.confirmation == "momentum":
        confirmation = df["Momentum7"] > 0.0
    else:
        raise ValueError(f"Conferma sconosciuta: {rule.confirmation}")
    return (common & confirmation).fillna(False)


def build_breakout_frame(
    df: pd.DataFrame,
    rule: BreakoutRule | None,
) -> tuple[pd.DataFrame, pd.Series]:
    baseline_entry, baseline_hold_core, _, _, _ = _entry_masks(
        df, baseline_variant()
    )
    breakout = (
        pd.Series(False, index=df.index)
        if rule is None
        else breakout_mask(df, rule)
    )
    entry = baseline_entry | breakout
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
            origins[pos] = "breakout_entry" if bool(breakout.loc[day]) else "standard"
            exposed = True
            peak_close = close
            continue

        if exposed and bool(baseline_hold_core.loc[day]):
            peak_close = max(peak_close if peak_close is not None else close, close)
            continue

        if exposed:
            peak_close = max(peak_close if peak_close is not None else close, close)
            trail_hit = close <= peak_close * (1.0 - TRAILING_STOP_PCT)
            trail_confirmed = bool(
                trail_hit
                and row["Momentum7"] >= TRAILING_MOMENTUM_MIN
                and row["VolumeRel20"] >= TRAILING_VOLUME_REL_MIN
            )
            if trail_confirmed:
                signals[pos] = "VENDI"
                origins[pos] = "trail8_exit"
                exposed = False
                peak_close = None

    frame = pd.DataFrame(
        {"Close": df["Close"], "Segnale": signals, "SignalOrigin": origins},
        index=df.index,
    )
    return frame, breakout


def confirmation_reference(
    row: pd.Series,
    rule: BreakoutRule,
) -> float:
    if rule.confirmation in {"legacy", "high"}:
        return float(row[f"PriorHigh{rule.lookback}"])
    if rule.confirmation in {"mean", "mean_momentum"}:
        return float(row[f"PriorMean{rule.lookback}"])
    return float(row["Close"] / (1.0 + row["Momentum7"]))


def entry_audit(
    indicators: pd.DataFrame,
    frames: dict[str, pd.DataFrame],
    rules: list[BreakoutRule],
) -> pd.DataFrame:
    baseline_buys = frames["baseline"].index[
        frames["baseline"]["Segnale"] == "ACQUISTA"
    ]
    rows: list[dict[str, object]] = []
    for rule in rules:
        frame = frames[rule.name]
        trades = extract_trades(frame, variant=rule.name, fee_rate=TAKER_FEE)
        for _, trade in trades[trades["entry_origin"] == "breakout_entry"].iterrows():
            signal_date = pd.Timestamp(trade["entry_date"])
            pos = frame.index.get_loc(signal_date)
            effective_date = frame.index[pos + 1] if pos + 1 < len(frame) else pd.NaT
            future_buys = baseline_buys[baseline_buys >= signal_date]
            baseline_next_buy = future_buys[0] if len(future_buys) else pd.NaT
            row = indicators.loc[signal_date]
            reference = confirmation_reference(row, rule)
            rows.append(
                {
                    "variant": rule.name,
                    "label": rule.label,
                    "signal_date": signal_date,
                    "signal_close": float(row["Close"]),
                    "effective_from": effective_date,
                    "exit_date": trade["exit_date"],
                    "exit_price": trade["exit_price"],
                    "exit_origin": trade["exit_origin"],
                    "status": trade["status"],
                    "net_return": float(trade["net_return"]),
                    "trade_drawdown": float(trade["max_drawdown"]),
                    "trade_days": int(trade["days"]),
                    "baseline_next_buy": baseline_next_buy,
                    "days_to_baseline_buy": (
                        int((baseline_next_buy - signal_date).days)
                        if pd.notna(baseline_next_buy)
                        else np.nan
                    ),
                    "rsi": float(row["RSI"]),
                    "momentum_7d": float(row["Momentum7"]),
                    "volume_rel_20": float(row["VolumeRel20"]),
                    "distance_sma200": float(row["DistanceSMA200"]),
                    "sma50_slope_5d": float(row["SMA50Slope5"]),
                    "confirmation_reference": reference,
                    "confirmation_margin": float(row["Close"] / reference - 1.0),
                }
            )
    return pd.DataFrame(rows)


def trigger_audit(
    indicators: pd.DataFrame,
    frames: dict[str, pd.DataFrame],
    masks: dict[str, pd.Series],
    rules: list[BreakoutRule],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for rule in rules:
        frame = frames[rule.name]
        for day in masks[rule.name].index[masks[rule.name]]:
            row = indicators.loc[day]
            rows.append(
                {
                    "variant": rule.name,
                    "date": day,
                    "actual_breakout_entry": bool(
                        frame.loc[day, "Segnale"] == "ACQUISTA"
                        and frame.loc[day, "SignalOrigin"] == "breakout_entry"
                    ),
                    "close": float(row["Close"]),
                    "rsi": float(row["RSI"]),
                    "momentum_7d": float(row["Momentum7"]),
                    "volume_rel_20": float(row["VolumeRel20"]),
                    "distance_sma200": float(row["DistanceSMA200"]),
                    "sma50_slope_5d": float(row["SMA50Slope5"]),
                }
            )
    return pd.DataFrame(rows)


def evaluate(
    indicators: pd.DataFrame,
    rules: list[BreakoutRule],
) -> tuple[
    pd.DataFrame,
    dict[str, pd.DataFrame],
    dict[str, pd.DataFrame],
    dict[str, pd.Series],
]:
    frames: dict[str, pd.DataFrame] = {}
    equities: dict[str, pd.DataFrame] = {}
    masks: dict[str, pd.Series] = {}
    rows: list[dict[str, object]] = []

    baseline_frame, baseline_mask = build_breakout_frame(indicators, None)
    official = evaluation_frame(compute_signals(indicators))
    if not baseline_frame["Segnale"].equals(official.loc[indicators.index, "Segnale"]):
        raise AssertionError("La replica della Baseline non coincide con il modello ufficiale.")
    frames["baseline"] = baseline_frame
    masks["baseline"] = baseline_mask

    frozen = replace(
        baseline_variant(),
        name="frozen_current",
        family="early_breakout",
        early_lookback=5,
        early_volume_rel_min=0.20,
        early_max_below_sma200=0.10,
        early_sma50_slope5_min=0.0,
    )
    frozen_frame = build_signal_frame(indicators, frozen)

    rule_by_name = {rule.name: rule for rule in rules}
    for name in ["baseline", *rule_by_name]:
        if name == "baseline":
            frame = baseline_frame
            rule = None
        else:
            rule = rule_by_name[name]
            frame, masks[name] = build_breakout_frame(indicators, rule)
            frames[name] = frame
        if name == CURRENT and not frame["Segnale"].equals(frozen_frame["Segnale"]):
            raise AssertionError("Il candidato attuale non replica il percorso congelato.")

        equity, full, _ = run_backtest(
            frame[["Close", "Segnale"]], transaction_cost_rate=TAKER_FEE
        )
        _, pre, _ = run_backtest(
            frame.loc[:PRE_EVENT_END, ["Close", "Segnale"]],
            transaction_cost_rate=TAKER_FEE,
        )
        equities[name] = equity
        train_stats = _return_stats(
            equity.loc[:"2019-12-31", "DailyReturnStrategy"]
        )
        test_stats = _return_stats(
            equity.loc["2020-01-01":PRE_EVENT_END, "DailyReturnStrategy"]
        )
        trades = extract_trades(frame, variant=name, fee_rate=TAKER_FEE)
        alternative = trades[trades["entry_origin"] == "breakout_entry"]
        closed = alternative[alternative["status"] == "closed"]
        target = alternative[pd.to_datetime(alternative["entry_date"]) >= EVENT_START]
        target_date = pd.Timestamp(target.iloc[0]["entry_date"]) if not target.empty else pd.NaT
        event_returns = equity.loc[EVENT_START:, "DailyReturnStrategy"].fillna(0.0)
        event_return = float((1.0 + event_returns).prod() - 1.0)
        event_source_date = pd.NaT
        covering = alternative[
            (pd.to_datetime(alternative["entry_date"]) <= EVENT_START)
            & (
                pd.to_datetime(alternative["exit_date"]).isna()
                | (pd.to_datetime(alternative["exit_date"]) >= EVENT_START)
            )
        ]
        if not covering.empty:
            event_source_date = pd.Timestamp(covering.iloc[-1]["entry_date"])
        elif not target.empty:
            event_source_date = target_date
        main_candle = pd.Timestamp("2026-08-19")
        captures_main_candle = bool(
            main_candle in equity.index
            and float(equity.loc[main_candle, "EffectiveExposure"]) > 0.0
        )
        rows.append(
            {
                "variant": name,
                "label": "Baseline ufficiale" if rule is None else rule.label,
                "rsi_max": np.nan if rule is None or rule.rsi_max is None else rule.rsi_max,
                "confirmation": "baseline" if rule is None else rule.confirmation,
                "lookback": np.nan if rule is None else rule.lookback,
                "diagnostic": False if rule is None else rule.diagnostic,
                "fingerprint_pre": _fingerprint(frame.loc[:PRE_EVENT_END, "Segnale"]),
                **{f"full_{key}": value for key, value in asdict(full).items()},
                **{f"pre_{key}": value for key, value in asdict(pre).items()},
                **{f"train_{key}": value for key, value in train_stats.items()},
                **{f"test_{key}": value for key, value in test_stats.items()},
                "raw_breakout_days": int(masks[name].sum()),
                "breakout_entries": len(alternative),
                "breakout_closed": len(closed),
                "breakout_losses": int((closed["net_return"] <= 0.0).sum()) if len(closed) else 0,
                "breakout_win_rate": float((closed["net_return"] > 0.0).mean()) if len(closed) else np.nan,
                "breakout_average_return": float(closed["net_return"].mean()) if len(closed) else np.nan,
                "breakout_worst_return": float(closed["net_return"].min()) if len(closed) else np.nan,
                "target_signal_date": target_date,
                "event_source_entry_date": event_source_date,
                "exposed_at_event_start": bool(
                    EVENT_START in equity.index
                    and float(equity.loc[EVENT_START, "EffectiveExposure"]) > 0.0
                ),
                "captures_main_candle": captures_main_candle,
                "event_return_to_cutoff": event_return,
            }
        )

    metrics = pd.DataFrame(rows)
    equivalent_pairs = (
        (CURRENT, HIGH7_CAPPED),
        (RSI40_LEGACY, HIGH7),
    )
    for left, right in equivalent_pairs:
        if not frames[left]["Segnale"].equals(frames[right]["Segnale"]):
            raise AssertionError(
                f"La semplificazione massimo7 non replica {left}: {right}."
            )
    baseline = metrics.set_index("variant").loc["baseline"]
    current = metrics.set_index("variant").loc[CURRENT]
    for prefix, reference in (("baseline", baseline), ("current", current)):
        metrics[f"delta_ann_vs_{prefix}"] = (
            metrics["pre_annualized_return"] - reference["pre_annualized_return"]
        )
        metrics[f"delta_dd_vs_{prefix}"] = (
            metrics["pre_max_drawdown"] - reference["pre_max_drawdown"]
        )
        metrics[f"delta_sharpe_vs_{prefix}"] = (
            metrics["pre_sharpe_ratio"] - reference["pre_sharpe_ratio"]
        )
    return metrics, frames, equities, masks


def yearly_comparison(
    equities: dict[str, pd.DataFrame],
    entries: pd.DataFrame,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for name, equity in equities.items():
        for year, returns in equity["DailyReturnStrategy"].groupby(equity.index.year):
            stats = _return_stats(returns)
            count = 0
            if not entries.empty:
                selected = entries[entries["variant"] == name]
                count = int((pd.to_datetime(selected["signal_date"]).dt.year == year).sum())
            rows.append(
                {
                    "year": int(year),
                    "variant": name,
                    "breakout_entries": count,
                    **stats,
                }
            )
    return pd.DataFrame(rows)


def cost_comparison(
    frames: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for scenario, fee in FEE_SCENARIOS.items():
        for name in FOCUS_NAMES:
            frame = frames[name]
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
                    "variant": name,
                    "full_annualized_return": full.annualized_return,
                    "full_max_drawdown": full.max_drawdown,
                    "full_sharpe": full.sharpe_ratio,
                    "pre_annualized_return": pre.annualized_return,
                    "pre_max_drawdown": pre.max_drawdown,
                    "pre_sharpe": pre.sharpe_ratio,
                }
            )
    return pd.DataFrame(rows)


def delay_comparison(
    frames: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for delay in (0, 1, 2):
        for name in FOCUS_NAMES:
            frame = frames[name]
            desired = exposure_from_signal(frame["Segnale"], CFG.exposure_map).ffill().fillna(0.0)
            effective = desired.shift(1 + delay).fillna(0.0)
            turnover = effective.diff().abs().fillna(effective.abs())
            daily = effective * frame["Close"].pct_change() - turnover * TAKER_FEE
            rows.append(
                {
                    "extra_delay_days": delay,
                    "variant": name,
                    **{f"pre_{key}": value for key, value in _return_stats(daily.loc[:PRE_EVENT_END]).items()},
                    **{f"full_{key}": value for key, value in _return_stats(daily).items()},
                    "event_return": float(
                        (1.0 + daily.loc[EVENT_START:].fillna(0.0)).prod() - 1.0
                    ),
                }
            )
    return pd.DataFrame(rows)


def statistical_validation(
    metrics: pd.DataFrame,
    frames: dict[str, pd.DataFrame],
    equities: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    unique_returns: dict[str, pd.Series] = {}
    seen: set[str] = set()
    for name, frame in frames.items():
        fingerprint = _fingerprint(frame.loc[:PRE_EVENT_END, "Segnale"])
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        unique_returns[name] = equities[name].loc[
            :PRE_EVENT_END, "DailyReturnStrategy"
        ].fillna(0.0)
    matrix = pd.DataFrame(unique_returns)
    pbo, _ = cscv_pbo(matrix, blocks=10, label="rsi_confirmation_unique_pre_event")
    benchmark = expected_max_sharpe(
        daily_sharpe_values(matrix), trials=len(metrics)
    )
    baseline_returns = equities["baseline"].loc[
        :PRE_EVENT_END, "DailyReturnStrategy"
    ].fillna(0.0)
    rows = [
        {
            "test": "pbo_unique_pre_event",
            "variant": "all",
            "value": float(pbo["pbo"]),
            "secondary": float(pbo["median_test_rank"]),
            "paths": int(pbo["paths"]),
        }
    ]
    for name in FOCUS_NAMES[1:]:
        returns = equities[name].loc[:PRE_EVENT_END, "DailyReturnStrategy"].fillna(0.0)
        dsr = probabilistic_sharpe(returns, benchmark_daily_sharpe=benchmark)
        incremental = probabilistic_sharpe(
            returns - baseline_returns, benchmark_daily_sharpe=0.0
        )
        rows.extend(
            [
                {
                    "test": "deflated_sharpe",
                    "variant": name,
                    "value": float(dsr["probability"]),
                    "secondary": float(dsr["annualized_sharpe"]),
                    "paths": len(metrics),
                },
                {
                    "test": "incremental_psr_vs_baseline",
                    "variant": name,
                    "value": float(incremental["probability"]),
                    "secondary": float(incremental["annualized_sharpe"]),
                    "paths": 2,
                },
            ]
        )
    for block in (30, 90):
        for name in FOCUS_NAMES[1:]:
            returns = equities[name].loc[
                :PRE_EVENT_END, "DailyReturnStrategy"
            ].fillna(0.0)
            bootstrap = circular_block_bootstrap(
                {
                    "baseline": pd.DataFrame({"DailyReturn": baseline_returns}),
                    name: pd.DataFrame({"DailyReturn": returns}),
                },
                block_days=block,
            ).iloc[0]
            rows.append(
                {
                    "test": f"bootstrap_{block}d_vs_baseline",
                    "variant": name,
                    "value": float(bootstrap["probability_outperform"]),
                    "secondary": float(bootstrap["p05_wealth_advantage"]),
                    "paths": 2,
                }
            )
    current_returns = equities[CURRENT].loc[
        :PRE_EVENT_END, "DailyReturnStrategy"
    ].fillna(0.0)
    for name in FOCUS_NAMES[2:]:
        returns = equities[name].loc[:PRE_EVENT_END, "DailyReturnStrategy"].fillna(0.0)
        incremental = probabilistic_sharpe(
            returns - current_returns, benchmark_daily_sharpe=0.0
        )
        rows.append(
            {
                "test": "incremental_psr_vs_current",
                "variant": name,
                "value": float(incremental["probability"]),
                "secondary": float(incremental["annualized_sharpe"]),
                "paths": 2,
            }
        )
    for block in (30, 90):
        for name in FOCUS_NAMES[2:]:
            returns = equities[name].loc[
                :PRE_EVENT_END, "DailyReturnStrategy"
            ].fillna(0.0)
            if returns.equals(current_returns):
                continue
            bootstrap = circular_block_bootstrap(
                {
                    "baseline": pd.DataFrame({"DailyReturn": current_returns}),
                    name: pd.DataFrame({"DailyReturn": returns}),
                },
                block_days=block,
            ).iloc[0]
            rows.append(
                {
                    "test": f"bootstrap_{block}d_vs_current",
                    "variant": name,
                    "value": float(bootstrap["probability_outperform"]),
                    "secondary": float(bootstrap["p05_wealth_advantage"]),
                    "paths": 2,
                }
            )
    return pd.DataFrame(rows)


def _pct(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value * 100:.2f}%"


def _num(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value:.3f}"


def _date(value: object) -> str:
    return "-" if pd.isna(value) else pd.Timestamp(value).date().isoformat()


def write_report(
    path: Path,
    *,
    as_of: str,
    metrics: pd.DataFrame,
    entries: pd.DataFrame,
    costs: pd.DataFrame,
    delays: pd.DataFrame,
    statistics: pd.DataFrame,
) -> None:
    indexed = metrics.set_index("variant")
    lines = [
        "# Breakout precoce - RSI e conferma del prezzo",
        "",
        f"Data test: `{date.today().isoformat()}`. Cutoff: `{as_of}`.",
        "Mercato: `ETH-USD` Coinbase, candele daily UTC chiuse.",
        "Commissione principale: taker `0,16%` per lato.",
        "La Baseline ufficiale, il bot e la dashboard non sono stati modificati.",
        "",
        "## Domande verificate",
        "",
        "1. Togliere il limite RSI 65 e conservare soltanto RSI >= 40.",
        "2. Sostituire momentum7 + massimo5 con Close sopra la media dei sette",
        "   Close precedenti.",
        "3. Unire le due conferme con Close sopra il massimo dei sette Close",
        "   precedenti.",
        "",
        "Tutte le altre condizioni del breakout restano congelate: SMA50<=SMA200,",
        "Close>SMA50, Close non oltre 10% sotto SMA200, SMA50 non in calo in 5g",
        "e volume almeno 20% sopra la media20. Dopo l'ingresso valgono soltanto",
        "le uscite ufficiali della Baseline.",
        "",
        "## Metriche principali",
        "",
        "Il periodo `pre-evento` termina il 16 agosto 2026 e non beneficia del",
        "movimento che ha generato questa ricerca.",
        "",
        "| Variante | Ann. pre | DD pre | Sharpe pre | Ann. completo | DD completo | Sharpe completo | Trade completati | PF | Ingressi breakout | Perdite breakout | Entry che copre evento | Cattura 19/8 | Rendimento evento |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---:|",
    ]
    for name in FOCUS_NAMES:
        row = indexed.loc[name]
        lines.append(
            f"| {row['label']} | {_pct(row['pre_annualized_return'])} | "
            f"{_pct(row['pre_max_drawdown'])} | {_num(row['pre_sharpe_ratio'])} | "
            f"{_pct(row['full_annualized_return'])} | {_pct(row['full_max_drawdown'])} | "
            f"{_num(row['full_sharpe_ratio'])} | {int(row['full_num_operations'])} | "
            f"{_num(row['full_profit_factor'])} | {int(row['breakout_entries'])} | "
            f"{int(row['breakout_losses'])} | {_date(row['event_source_entry_date'])} | "
            f"{'SI' if row['captures_main_candle'] else 'NO'} | "
            f"{_pct(row['event_return_to_cutoff'])} |"
        )

    lines.extend(["", "## Date degli ingressi breakout", ""])
    for name in FOCUS_NAMES[1:]:
        selected = entries[entries["variant"] == name]
        dates = ", ".join(_date(value) for value in selected["signal_date"])
        lines.append(f"- **{indexed.loc[name, 'label']}**: {dates or 'nessun ingresso'}.")

    lines.extend(
        [
            "",
            "Il segnale e' calcolato sul Close della data indicata; l'esposizione",
            "prudenziale viene applicata al rendimento della candela successiva.",
            "",
            "## Operazioni breakout delle varianti principali",
            "",
            "| Variante | Segnale | Close | Uscita | Prezzo uscita | Motivo | Netto | DD trade | Baseline compra dopo |",
            "|---|---|---:|---|---:|---|---:|---:|---|",
        ]
    )
    focus_entries = entries[entries["variant"].isin(FOCUS_NAMES[1:])]
    for _, row in focus_entries.iterrows():
        exit_price = "-" if pd.isna(row["exit_price"]) else f"{row['exit_price']:.2f}"
        lines.append(
            f"| {row['variant']} | {_date(row['signal_date'])} | {row['signal_close']:.2f} | "
            f"{_date(row['exit_date'])} | {exit_price} | {row['exit_origin'] or 'aperto'} | "
            f"{_pct(row['net_return'])} | {_pct(row['trade_drawdown'])} | "
            f"{_date(row['baseline_next_buy'])} |"
        )

    lines.extend(
        [
            "",
            "## Stabilita temporale pre-evento",
            "",
            "| Variante | Ann. fino 2019 | DD fino 2019 | Sharpe fino 2019 | Ann. 2020-16/8/2026 | DD 2020-16/8/2026 | Sharpe 2020-16/8/2026 |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for name in FOCUS_NAMES:
        row = indexed.loc[name]
        lines.append(
            f"| {row['label']} | {_pct(row['train_annualized_return'])} | "
            f"{_pct(row['train_max_drawdown'])} | {_num(row['train_sharpe_ratio'])} | "
            f"{_pct(row['test_annualized_return'])} | {_pct(row['test_max_drawdown'])} | "
            f"{_num(row['test_sharpe_ratio'])} |"
        )

    taker = costs[costs["scenario"] == "taker_0_16pct"].set_index("variant")
    stress = costs[costs["scenario"] == "stress_0_60pct"].set_index("variant")
    delay2 = delays[delays["extra_delay_days"] == 2].set_index("variant")
    lines.extend(
        [
            "",
            "## Costi e ritardo",
            "",
            "| Variante | Ann. taker pre | Ann. stress pre | Evento senza ritardo extra | Evento con 2 giorni extra |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for name in FOCUS_NAMES:
        event0 = delays[
            (delays["variant"] == name) & (delays["extra_delay_days"] == 0)
        ].iloc[0]["event_return"]
        lines.append(
            f"| {indexed.loc[name, 'label']} | {_pct(taker.loc[name, 'pre_annualized_return'])} | "
            f"{_pct(stress.loc[name, 'pre_annualized_return'])} | {_pct(event0)} | "
            f"{_pct(delay2.loc[name, 'event_return'])} |"
        )

    pbo = statistics[statistics["test"] == "pbo_unique_pre_event"].iloc[0]
    psr_current = statistics[
        statistics["test"] == "incremental_psr_vs_current"
    ].set_index("variant")
    boot30_current = statistics[
        statistics["test"] == "bootstrap_30d_vs_current"
    ].set_index("variant")
    boot90_current = statistics[
        statistics["test"] == "bootstrap_90d_vs_current"
    ].set_index("variant")
    lines.extend(
        [
            "",
            "## Controlli statistici",
            "",
            f"- configurazioni testate: `{len(metrics) - 1}`; percorsi pre-evento "
            f"distinti: `{int(pbo['paths'])}`;",
            f"- PBO/CSCV: `{_pct(pbo['value'])}`; rango mediano fuori campione "
            f"`{_pct(pbo['secondary'])}`;",
            "- DSR, probabilita' incrementale e bootstrap per ciascuna variante",
            "  principale sono disponibili nel CSV statistico;",
            "- le configurazioni diagnostiche e le sensibilita' 5/10 giorni sono",
            "  riportate integralmente nei CSV metriche, ingressi e trigger.",
            "",
            "Confronto diretto contro il candidato attuale, sempre fino al 16 agosto:",
            "",
            "| Variante | PSR vantaggio | Bootstrap 30g: prob. migliore | P05 30g | Bootstrap 90g: prob. migliore | P05 90g |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for name in FOCUS_NAMES[2:]:
        if indexed.loc[name, "fingerprint_pre"] == indexed.loc[CURRENT, "fingerprint_pre"]:
            lines.append(
                f"| {indexed.loc[name, 'label']} | IDENTICO | IDENTICO | 0.00% | "
                "IDENTICO | 0.00% |"
            )
        else:
            lines.append(
                f"| {indexed.loc[name, 'label']} | {_pct(psr_current.loc[name, 'value'])} | "
                f"{_pct(boot30_current.loc[name, 'value'])} | "
                f"{_pct(boot30_current.loc[name, 'secondary'])} | "
                f"{_pct(boot90_current.loc[name, 'value'])} | "
                f"{_pct(boot90_current.loc[name, 'secondary'])} |"
            )
    lines.extend(
        [
            "",
            "## Lettura prudenziale",
            "",
            "- un numero maggiore di ingressi non costituisce automaticamente un",
            "  miglioramento: va letto insieme a drawdown, Sharpe e nuove perdite;",
            "- la media7 misura recupero sopra la tendenza breve, non un vero breakout;",
            "- il massimo7 conserva la natura di breakout e fonde le vecchie condizioni",
            "  in una formula unica, ma puo' essere piu' selettivo;",
            "- nessuna variante viene promossa automaticamente da questo test.",
            "",
            "## Conclusioni del test",
            "",
            "- `Close > massimo dei 7 Close precedenti`, mantenendo RSI 40-65,",
            "  produce esattamente gli stessi segnali e le stesse metriche del",
            "  candidato attuale: nello storico disponibile e' una semplificazione",
            "  equivalente di momentum7 + massimo5;",
            "- eliminare il tetto RSI porta l'annualizzato pre-evento da 120,64% a",
            "  125,29%, ma lo Sharpe resta praticamente fermo (1,833 -> 1,835),",
            "  gli ingressi breakout raddoppiano da 6 a 12 e le perdite passano da",
            "  1 a 5; il profit factor complessivo scende da 16,830 a 13,005;",
            "  il bootstrap diretto gli assegna soltanto circa 63% di probabilita'",
            "  di battere il candidato attuale, con percentile 5% fortemente negativo;",
            "- la proposta `RSI >=40 + Close sopra media7` cattura il movimento",
            "  corrente da una posizione aperta il 28 luglio, ma prima dell'evento",
            "  riduce annualizzato, drawdown e Sharpe rispetto al candidato attuale",
            "  e porta le perdite breakout da 1 a 7;",
            "  anche PSR e bootstrap diretti non mostrano un vantaggio sul candidato;",
            "- il PBO elevato segnala che scegliere ora la variante col rendimento",
            "  piu' alto sarebbe fragile. Il massimo7 puo' restare come formulazione",
            "  equivalente da monitorare; RSI senza tetto resta una variante shadow;",
            "  la media7 non e' candidata alla sostituzione.",
            "",
            "## File completi",
            "",
            "- `reports/breakout_rsi_confirmation_metrics.csv`;",
            "- `reports/breakout_rsi_confirmation_entries.csv`;",
            "- `reports/breakout_rsi_confirmation_triggers.csv`;",
            "- `reports/breakout_rsi_confirmation_yearly.csv`;",
            "- `reports/breakout_rsi_confirmation_costs.csv`;",
            "- `reports/breakout_rsi_confirmation_delays.csv`;",
            "- `reports/breakout_rsi_confirmation_statistics.csv`.",
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
    indicators = evaluation_frame(
        add_confirmation_features(compute_all_indicators(candles))
    )
    rules = build_rules()
    metrics, frames, equities, masks = evaluate(indicators, rules)
    entries = entry_audit(indicators, frames, rules)
    triggers = trigger_audit(indicators, frames, masks, rules)
    yearly = yearly_comparison(equities, entries)
    costs = cost_comparison(frames)
    delays = delay_comparison(frames)
    statistics = statistical_validation(metrics, frames, equities)

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUT_METRICS, index=False)
    entries.to_csv(OUT_ENTRIES, index=False)
    triggers.to_csv(OUT_TRIGGERS, index=False)
    yearly.to_csv(OUT_YEARLY, index=False)
    costs.to_csv(OUT_COSTS, index=False)
    delays.to_csv(OUT_DELAYS, index=False)
    statistics.to_csv(OUT_STATS, index=False)
    write_report(
        args.output,
        as_of=args.as_of,
        metrics=metrics,
        entries=entries,
        costs=costs,
        delays=delays,
        statistics=statistics,
    )

    focus = metrics[metrics["variant"].isin(FOCUS_NAMES)][
        [
            "variant",
            "pre_annualized_return",
            "pre_max_drawdown",
            "pre_sharpe_ratio",
            "breakout_entries",
            "breakout_losses",
            "target_signal_date",
            "event_source_entry_date",
            "captures_main_candle",
            "event_return_to_cutoff",
        ]
    ]
    print(f"Saved {args.output}")
    print(focus.to_string(index=False))
    print("\nBREAKOUT ENTRY DATES")
    for name in FOCUS_NAMES[1:]:
        selected = entries[entries["variant"] == name]
        dates = ", ".join(_date(value) for value in selected["signal_date"])
        print(f"{name}: {dates or '-'}")


if __name__ == "__main__":
    main()
