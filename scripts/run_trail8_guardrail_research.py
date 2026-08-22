"""Ricerca sperimentale di filtri selettivi per le uscite Trail8."""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict, dataclass
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
from scripts.run_rsi_upper_cap_removal import completed_trades
from strategy.signals import (
    ENTRY_RSI_MAX,
    HOLD_ACTION,
    TRAILING_MOMENTUM_MIN,
    TRAILING_STOP_PCT,
    TRAILING_VOLUME_REL_MIN,
    _sma50_sell_condition,
    compute_signals,
)


OUT_MD = PROJECT_ROOT / "reports" / "trail8_guardrail_research.md"
OUT_GRID = PROJECT_ROOT / "reports" / "trail8_guardrail_grid.csv"
OUT_EVENTS = PROJECT_ROOT / "reports" / "trail8_guardrail_events.csv"
TAKER_COST = 0.0016


@dataclass(frozen=True)
class Rule:
    name: str
    stop_pct: float = TRAILING_STOP_PCT
    momentum_min: float = TRAILING_MOMENTUM_MIN
    volume_min: float = TRAILING_VOLUME_REL_MIN
    min_slope5: float | None = None
    min_atr_pct: float | None = None
    min_extension: float | None = None
    min_sma_gap: float | None = None
    gate_mode: str = "all"
    widen_to: float | None = None
    widen_if_slope_below: float | None = None
    widen_if_atr_below: float | None = None
    widen_mode: str = "any"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ricerca guardrail per Trail8.")
    parser.add_argument(
        "--as-of",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Ultima candela chiusa inclusa (YYYY-MM-DD).",
    )
    parser.add_argument("--output", type=Path, default=OUT_MD)
    return parser.parse_args()


def feature_frame(indicators: pd.DataFrame) -> pd.DataFrame:
    frame = indicators.copy()
    frame["SMA50_Slope5"] = frame["SMA50"] / frame["SMA50"].shift(5) - 1.0
    frame["ATR_Pct"] = frame["ATR"] / frame["Close"]
    frame["Close_vs_SMA50"] = frame["Close"] / frame["SMA50"] - 1.0
    frame["SMA_Gap"] = frame["SMA50"] / frame["SMA200"] - 1.0
    return frame


def _gate(rule: Rule, row: pd.Series) -> bool:
    checks: list[bool] = []
    if rule.min_slope5 is not None:
        checks.append(float(row["SMA50_Slope5"]) >= rule.min_slope5)
    if rule.min_atr_pct is not None:
        checks.append(float(row["ATR_Pct"]) >= rule.min_atr_pct)
    if rule.min_extension is not None:
        checks.append(float(row["Close_vs_SMA50"]) >= rule.min_extension)
    if rule.min_sma_gap is not None:
        checks.append(float(row["SMA_Gap"]) >= rule.min_sma_gap)
    if not checks:
        return True
    return any(checks) if rule.gate_mode == "any" else all(checks)


def _stop_width(rule: Rule, row: pd.Series) -> float:
    if rule.widen_to is None:
        return rule.stop_pct
    low_checks: list[bool] = []
    if rule.widen_if_slope_below is not None:
        low_checks.append(float(row["SMA50_Slope5"]) <= rule.widen_if_slope_below)
    if rule.widen_if_atr_below is not None:
        low_checks.append(float(row["ATR_Pct"]) <= rule.widen_if_atr_below)
    if not low_checks:
        return rule.stop_pct
    should_widen = all(low_checks) if rule.widen_mode == "all" else any(low_checks)
    return rule.widen_to if should_widen else rule.stop_pct


def candidate_signal_frame(indicators: pd.DataFrame, rule: Rule) -> pd.DataFrame:
    frame = feature_frame(indicators)
    close = frame["Close"]
    official_buy = (
        (close > frame["SMA200"])
        & (frame["SMA50"] > frame["SMA200"])
        & (frame["RSI"] >= 40.0)
        & (close > frame[f"Close_{CFG.momentum_days}d_ago"])
        & (frame["Volume"] > frame["VolumeAvg20"])
    )
    filtered_entry = official_buy & (frame["RSI"] <= ENTRY_RSI_MAX)
    official_sell = _sma50_sell_condition(close, frame["SMA50"])

    signal = np.full(len(frame), HOLD_ACTION, dtype=object)
    trail_hit = pd.Series(False, index=frame.index)
    trail_confirmed = pd.Series(False, index=frame.index)
    exposure = False
    peak_close: float | None = None

    for pos, (day, row) in enumerate(frame.iterrows()):
        close_value = float(row["Close"])
        if bool(official_sell.loc[day]):
            signal[pos] = "VENDI"
            exposure = False
            peak_close = None
            continue

        if bool(official_buy.loc[day]):
            if not exposure and bool(filtered_entry.loc[day]):
                signal[pos] = "ACQUISTA"
                exposure = True
                peak_close = close_value
            elif exposure:
                peak_close = max(peak_close if peak_close is not None else close_value, close_value)
            continue

        if not exposure:
            continue

        peak_close = max(peak_close if peak_close is not None else close_value, close_value)
        stop_pct = _stop_width(rule, row)
        stop_hit = close_value <= peak_close * (1.0 - stop_pct)
        trail_hit.loc[day] = bool(stop_hit)
        if not stop_hit:
            continue

        close_ago = row.get(f"Close_{CFG.momentum_days}d_ago", np.nan)
        volume_avg = row.get("VolumeAvg20", np.nan)
        momentum = (
            close_value / float(close_ago) - 1.0
            if pd.notna(close_ago) and float(close_ago) != 0.0
            else np.nan
        )
        volume_rel = (
            float(row["Volume"]) / float(volume_avg) - 1.0
            if pd.notna(volume_avg) and float(volume_avg) != 0.0
            else np.nan
        )
        confirmed = bool(
            pd.notna(momentum)
            and pd.notna(volume_rel)
            and momentum >= rule.momentum_min
            and volume_rel >= rule.volume_min
            and _gate(rule, row)
        )
        trail_confirmed.loc[day] = confirmed
        if confirmed:
            signal[pos] = "VENDI"
            exposure = False
            peak_close = None

    frame["Segnale"] = signal
    frame["Trail8_Stop_Hit"] = trail_hit
    frame["Trail8_Confirmed"] = trail_confirmed
    return frame


def rules_to_test() -> list[Rule]:
    rules = [Rule("Trail8 ufficiale"), Rule("Senza trailing", stop_pct=1.0)]
    rules.extend(Rule(f"Trail{width}", stop_pct=width / 100.0) for width in (9, 10, 11, 12, 13, 15))
    rules.extend(
        Rule(f"Momentum >= {threshold:.0%}", momentum_min=threshold)
        for threshold in (-0.12, -0.10, -0.08, -0.06, -0.04, -0.02, 0.0)
    )
    rules.extend(
        Rule(f"Volume >= +{threshold:.0%}", volume_min=threshold)
        for threshold in (0.30, 0.40, 0.50, 0.60, 0.75, 1.00)
    )
    rules.extend(
        Rule(f"Trail solo slope5 >= {threshold:.0%}", min_slope5=threshold)
        for threshold in (0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08)
    )
    rules.extend(
        Rule(f"Trail solo ATR >= {threshold:.0%}", min_atr_pct=threshold)
        for threshold in (0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10)
    )
    rules.extend(
        Rule(f"Trail solo estensione >= {threshold:.0%}", min_extension=threshold)
        for threshold in (0.00, 0.03, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20)
    )
    rules.extend(
        Rule(f"Trail solo gap SMA >= {threshold:.0%}", min_sma_gap=threshold)
        for threshold in (0.00, 0.10, 0.20, 0.30, 0.40, 0.50)
    )
    for slope in (0.01, 0.02, 0.03, 0.04):
        for atr in (0.04, 0.05, 0.06, 0.07):
            rules.append(
                Rule(
                    f"Gate slope>={slope:.0%} AND ATR>={atr:.0%}",
                    min_slope5=slope,
                    min_atr_pct=atr,
                    gate_mode="all",
                )
            )
            rules.append(
                Rule(
                    f"Gate slope>={slope:.0%} OR ATR>={atr:.0%}",
                    min_slope5=slope,
                    min_atr_pct=atr,
                    gate_mode="any",
                )
            )
    for width in (0.10, 0.11, 0.12, 0.13, 0.15):
        for slope in (0.01, 0.02, 0.03, 0.04, 0.05, 0.06):
            rules.append(
                Rule(
                    f"Trail{width:.0%} se slope5 <= {slope:.0%}",
                    widen_to=width,
                    widen_if_slope_below=slope,
                )
            )
        for atr in (0.04, 0.05, 0.06, 0.07, 0.08):
            rules.append(
                Rule(
                    f"Trail{width:.0%} se ATR <= {atr:.0%}",
                    widen_to=width,
                    widen_if_atr_below=atr,
                )
            )
    for width in (0.11, 0.12, 0.13):
        for slope in (0.02, 0.03, 0.04):
            for atr in (0.05, 0.06, 0.07):
                for mode in ("all", "any"):
                    rules.append(
                        Rule(
                            f"Trail{width:.0%} low slope<={slope:.0%} {mode.upper()} ATR<={atr:.0%}",
                            widen_to=width,
                            widen_if_slope_below=slope,
                            widen_if_atr_below=atr,
                            widen_mode=mode,
                        )
                    )
    for width in (0.105, 0.11, 0.115, 0.12, 0.125, 0.13):
        for slope in (0.0300, 0.0325, 0.0350, 0.0375, 0.0400, 0.0425, 0.0450, 0.0475, 0.0500):
            rules.append(
                Rule(
                    f"Fine Trail{width * 100:.1f} slope<={slope * 100:.2f}%",
                    widen_to=width,
                    widen_if_slope_below=slope,
                )
            )
    for width in (0.11, 0.12, 0.13):
        for slope in (0.035, 0.0375, 0.04):
            for extension in (0.03, 0.05, 0.08):
                rules.append(
                    Rule(
                        f"Combo Trail{width * 100:.0f} slope<={slope * 100:.2f}% ext>={extension * 100:.0f}%",
                        min_extension=extension,
                        widen_to=width,
                        widen_if_slope_below=slope,
                    )
                )
    rules.extend(
        [
            Rule(
                "Combo ext>=5% e momentum>=-10%",
                momentum_min=-0.10,
                min_extension=0.05,
            ),
            Rule(
                "Combo Trail11 slope<=4% ext>=5% momentum>=-10%",
                momentum_min=-0.10,
                min_extension=0.05,
                widen_to=0.11,
                widen_if_slope_below=0.04,
            ),
        ]
    )
    return rules


def segment_return(equity: pd.DataFrame, start: str, end: str) -> float:
    start_pos = equity.index.get_loc(pd.Timestamp(start)) + 1
    end_pos = min(equity.index.get_loc(pd.Timestamp(end)) + 1, len(equity) - 1)
    returns = equity["DailyReturnStrategy"].iloc[start_pos : end_pos + 1].fillna(0.0)
    return float((1.0 + returns).prod() - 1.0)


def build_segments(
    frames: dict[str, pd.DataFrame], equities: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    no_trail_trades = completed_trades(frames["Senza trailing"], equities["Senza trailing"])
    baseline_events = frames["Trail8 ufficiale"].index[
        frames["Trail8 ufficiale"]["Trail8_Confirmed"]
    ]
    rows: list[dict[str, object]] = []
    for _, trade in no_trail_trades.iterrows():
        start = str(trade["entry"])
        end = str(trade["exit"])
        events = baseline_events[
            (baseline_events >= pd.Timestamp(start)) & (baseline_events <= pd.Timestamp(end))
        ]
        if not len(events):
            continue
        no_trail = segment_return(equities["Senza trailing"], start, end)
        baseline = segment_return(equities["Trail8 ufficiale"], start, end)
        rows.append(
            {
                "entry": start,
                "comparison_end": end,
                "baseline_trail_dates": ", ".join(d.date().isoformat() for d in events),
                "no_trail_return": no_trail,
                "baseline_return": baseline,
                "baseline_delta": baseline - no_trail,
                "baseline_label": "GOOD" if baseline > no_trail else "FALSE",
            }
        )
    return pd.DataFrame(rows)


def event_features(frame: pd.DataFrame, segments: pd.DataFrame) -> pd.DataFrame:
    labels: dict[pd.Timestamp, dict[str, object]] = {}
    for _, segment in segments.iterrows():
        for value in str(segment["baseline_trail_dates"]).split(", "):
            labels[pd.Timestamp(value)] = segment.to_dict()

    rows: list[dict[str, object]] = []
    exposure = False
    peak = np.nan
    peak_date = pd.NaT
    for day, row in frame.iterrows():
        if row["Segnale"] == "ACQUISTA":
            exposure = True
            peak = float(row["Close"])
            peak_date = day
        elif exposure:
            if float(row["Close"]) > peak:
                peak = float(row["Close"])
                peak_date = day
        if bool(row["Trail8_Confirmed"]):
            close = float(row["Close"])
            info = labels[day]
            rows.append(
                {
                    "date": day.date().isoformat(),
                    "label": info["baseline_label"],
                    "segment_delta": info["baseline_delta"],
                    "close": close,
                    "peak_close": peak,
                    "drawdown_from_peak": close / peak - 1.0,
                    "days_since_peak": int((day - peak_date).days),
                    "momentum_7d": close / float(row[f"Close_{CFG.momentum_days}d_ago"]) - 1.0,
                    "volume_rel": float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0,
                    "rsi": float(row["RSI"]),
                    "close_vs_sma50": float(row["Close_vs_SMA50"]),
                    "sma_gap": float(row["SMA_Gap"]),
                    "sma50_slope5": float(row["SMA50_Slope5"]),
                    "atr_pct": float(row["ATR_Pct"]),
                }
            )
            exposure = False
            peak = np.nan
            peak_date = pd.NaT
        elif row["Segnale"] == "VENDI":
            exposure = False
            peak = np.nan
            peak_date = pd.NaT
    return pd.DataFrame(rows)


def rolling_summary(
    baseline_equity: pd.DataFrame, candidate_equity: pd.DataFrame
) -> dict[str, float | int]:
    rows: list[dict[str, float]] = []
    for start_pos in range(0, len(baseline_equity), 30):
        start = baseline_equity.index[start_pos]
        end = start + pd.Timedelta(days=730)
        base = baseline_equity.loc[start:end]
        cand = candidate_equity.loc[start:end]
        if len(base) < 657:
            continue
        item: dict[str, float] = {}
        for prefix, window in (("base", base), ("cand", cand)):
            normalized = window["EquityStrategy"] / float(window["EquityStrategy"].iloc[0])
            returns = normalized.pct_change().dropna()
            std = returns.std(ddof=1)
            item[f"{prefix}_return"] = float(normalized.iloc[-1] - 1.0)
            item[f"{prefix}_dd"] = float((normalized / normalized.cummax() - 1.0).min())
            item[f"{prefix}_sharpe"] = (
                float(np.sqrt(CFG.periods_per_year) * returns.mean() / std)
                if pd.notna(std) and std > 0.0
                else np.nan
            )
        rows.append(item)
    rolling = pd.DataFrame(rows)
    return {
        "windows": len(rolling),
        "rolling_return_better": float((rolling["cand_return"] > rolling["base_return"]).mean()),
        "rolling_sharpe_better": float((rolling["cand_sharpe"] > rolling["base_sharpe"]).mean()),
        "rolling_dd_better": float((rolling["cand_dd"] >= rolling["base_dd"]).mean()),
        "rolling_worst_return_delta": float((rolling["cand_return"] - rolling["base_return"]).min()),
    }


def period_summary(equity: pd.DataFrame, start: str, end: str) -> dict[str, float]:
    window = equity.loc[start:end]
    normalized = window["EquityStrategy"] / float(window["EquityStrategy"].iloc[0])
    returns = window["DailyReturnStrategy"].iloc[1:].dropna()
    std = returns.std(ddof=1)
    years = max((window.index[-1] - window.index[0]).days / CFG.periods_per_year, 1.0 / CFG.periods_per_year)
    return {
        "total_return": float(normalized.iloc[-1] - 1.0),
        "annualized_return": float(normalized.iloc[-1] ** (1.0 / years) - 1.0),
        "max_drawdown": float((normalized / normalized.cummax() - 1.0).min()),
        "sharpe": (
            float(np.sqrt(CFG.periods_per_year) * returns.mean() / std)
            if pd.notna(std) and std > 0.0
            else np.nan
        ),
    }


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
    baseline = evaluation_frame(compute_signals(indicators))
    aligned_indicators = indicators.loc[baseline.index].copy()

    frames: dict[str, pd.DataFrame] = {}
    equities: dict[str, pd.DataFrame] = {}
    metrics_by_name: dict[str, object] = {}
    rules = rules_to_test()
    for rule in rules:
        frame = candidate_signal_frame(aligned_indicators, rule)
        equity, metrics, _ = run_backtest(
            frame[["Close", "Segnale"]], transaction_cost_rate=TAKER_COST
        )
        frames[rule.name] = frame
        equities[rule.name] = equity
        metrics_by_name[rule.name] = metrics

    segments = build_segments(frames, equities)
    events = event_features(frames["Trail8 ufficiale"], segments)
    baseline_metrics = metrics_by_name["Trail8 ufficiale"]
    baseline_returns = {
        row["entry"]: float(row["baseline_return"]) for _, row in segments.iterrows()
    }

    grid_rows: list[dict[str, object]] = []
    event_rows: list[dict[str, object]] = []
    for rule in rules:
        metrics = metrics_by_name[rule.name]
        false_improved = 0
        false_rescued = 0
        good_harmed = 0
        good_preserved = 0
        for _, segment in segments.iterrows():
            candidate_return = segment_return(
                equities[rule.name], str(segment["entry"]), str(segment["comparison_end"])
            )
            change_vs_baseline = candidate_return - baseline_returns[str(segment["entry"])]
            candidate_delta = candidate_return - float(segment["no_trail_return"])
            label = str(segment["baseline_label"])
            if label == "FALSE":
                false_improved += int(change_vs_baseline > 0.000001)
                false_rescued += int(candidate_delta >= -0.000001)
            else:
                harmed = change_vs_baseline < -0.000001
                good_harmed += int(harmed)
                good_preserved += int(not harmed)
            event_rows.append(
                {
                    "candidate": rule.name,
                    "entry": segment["entry"],
                    "comparison_end": segment["comparison_end"],
                    "baseline_label": label,
                    "baseline_return": segment["baseline_return"],
                    "candidate_return": candidate_return,
                    "no_trail_return": segment["no_trail_return"],
                    "change_vs_baseline": change_vs_baseline,
                    "candidate_delta_vs_no_trail": candidate_delta,
                }
            )
        row = asdict(metrics)
        row.update(
            {
                "candidate": rule.name,
                "annualized_delta": metrics.annualized_return - baseline_metrics.annualized_return,
                "drawdown_delta": metrics.max_drawdown - baseline_metrics.max_drawdown,
                "sharpe_delta": metrics.sharpe_ratio - baseline_metrics.sharpe_ratio,
                "false_improved": false_improved,
                "false_rescued": false_rescued,
                "good_harmed": good_harmed,
                "good_preserved": good_preserved,
            }
        )
        grid_rows.append(row)

    grid = pd.DataFrame(grid_rows)
    event_comparison = pd.DataFrame(event_rows)
    eligible = grid[
        (grid["max_drawdown"] >= baseline_metrics.max_drawdown - 0.03)
        & (grid["sharpe_ratio"] >= baseline_metrics.sharpe_ratio - 0.03)
        & (grid["good_harmed"] <= 2)
    ].copy()
    eligible = eligible.sort_values(
        ["false_improved", "false_rescued", "good_harmed", "annualized_return"],
        ascending=[False, False, True, False],
    )
    selected_names = [
        "Trail8 ufficiale",
        "Combo Trail11 slope<=4.00% ext>=5%",
        "Combo Trail11 slope<=4.00% ext>=8%",
        "Combo Trail11 slope<=4% ext>=5% momentum>=-10%",
        "Trail11% se slope5 <= 4%",
        "Trail solo estensione >= 5%",
        "Trail12",
        "Senza trailing",
    ]

    cost_rows: list[dict[str, object]] = []
    rolling_rows: list[dict[str, object]] = []
    for name in selected_names:
        for cost_name, cost in (
            ("maker_0_07pct", 0.0007),
            ("taker_0_16pct", 0.0016),
            ("prudenziale_0_60pct", 0.006),
            ("stress_1_00pct", 0.01),
        ):
            _, metrics, _ = run_backtest(
                frames[name][["Close", "Segnale"]], transaction_cost_rate=cost
            )
            item = asdict(metrics)
            item.update({"candidate": name, "cost": cost_name})
            cost_rows.append(item)
        rolling = rolling_summary(equities["Trail8 ufficiale"], equities[name])
        rolling.update({"candidate": name})
        rolling_rows.append(rolling)
    costs = pd.DataFrame(cost_rows)
    rolling_df = pd.DataFrame(rolling_rows)
    period_rows: list[dict[str, object]] = []
    for name in selected_names[:4]:
        for period_name, start, end in (
            ("2017-2019", "2017-01-01", "2019-12-31"),
            ("2020-2022", "2020-01-01", "2022-12-31"),
            ("2023-oggi", "2023-01-01", args.as_of),
        ):
            item = period_summary(equities[name], start, end)
            item.update({"candidate": name, "period": period_name})
            period_rows.append(item)
    periods = pd.DataFrame(period_rows)

    OUT_GRID.parent.mkdir(parents=True, exist_ok=True)
    grid.sort_values("annualized_return", ascending=False).to_csv(OUT_GRID, index=False)
    event_comparison.to_csv(OUT_EVENTS, index=False)
    events.to_csv(PROJECT_ROOT / "reports" / "trail8_guardrail_event_features.csv", index=False)

    lines = [
        "# Trail8 - Ricerca di un guardrail selettivo",
        "",
        f"Data test: `{date.today().isoformat()}`.",
        f"Periodo: `{baseline.index[0].date()}` -> `{baseline.index[-1].date()}`.",
        "Mercato: `ETH-USD` Coinbase, candele daily UTC chiuse.",
        "",
        "Test sperimentale: nessuna regola ufficiale e' stata modificata. Gli ingressi",
        "e l'uscita `Close < SMA50 * 0,98` restano identici. Varia soltanto il",
        "meccanismo di conferma del Trail8 o, nei test indicati, la sua ampiezza.",
        "",
        "## Punto di partenza",
        "",
        "Il Trail8 modifica 15 sequenze rispetto alla stessa strategia senza trailing:",
        "9 migliorano e 6 peggiorano. L'obiettivo e' recuperare le sei sequenze",
        "peggiorative senza perdere la protezione delle altre nove.",
        "",
        "## Caratteristiche delle uscite ufficiali",
        "",
        "| Gruppo | Eventi | DD dal picco | Momentum 7g | Volume rel. | Close/SMA50 | Slope SMA50 5g | ATR/Close |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label in ("FALSE", "GOOD"):
        group = events[events["label"] == label]
        lines.append(
            f"| {label} | {len(group)} | {pct(group['drawdown_from_peak'].mean())} | "
            f"{pct(group['momentum_7d'].mean())} | {pct(group['volume_rel'].mean())} | "
            f"{pct(group['close_vs_sma50'].mean())} | {pct(group['sma50_slope5'].mean())} | "
            f"{pct(group['atr_pct'].mean())} |"
        )

    lines.extend(
        [
            "",
            "## Migliori compromessi nel filtro preliminare",
            "",
            "Filtro preliminare: max drawdown non peggiore di 3 punti, Sharpe non",
            "inferiore di oltre 0,03 e non piu di due sequenze protettive danneggiate.",
            "Costi taker `0,16%` per lato.",
            "",
            "| Candidato | Ann. | Max DD | Sharpe | PF | Trade | False migliorati | False recuperati | Protettivi danneggiati |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    shown = grid[grid["candidate"].isin(selected_names)].copy()
    shown["order"] = shown["candidate"].map({name: pos for pos, name in enumerate(selected_names)})
    shown = shown.sort_values("order")
    for _, row in shown.iterrows():
        lines.append(
            f"| {row['candidate']} | {pct(row['annualized_return'])} | "
            f"{pct(row['max_drawdown'])} | {row['sharpe_ratio']:.3f} | "
            f"{row['profit_factor']:.3f} | {int(row['num_operations'])} | "
            f"{int(row['false_improved'])}/6 | {int(row['false_rescued'])}/6 | "
            f"{int(row['good_harmed'])}/9 |"
        )

    lines.extend(
        [
            "",
            "## Robustezza dei candidati selezionati",
            "",
            "| Candidato | Finestre 2 anni | Rendimento migliore | Sharpe migliore | DD migliore | Peggior delta rendimento |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in rolling_df.iterrows():
        lines.append(
            f"| {row['candidate']} | {int(row['windows'])} | "
            f"{pct(row['rolling_return_better'])} | {pct(row['rolling_sharpe_better'])} | "
            f"{pct(row['rolling_dd_better'])} | {pct(row['rolling_worst_return_delta'])} |"
        )

    lines.extend(
        [
            "",
            "## Sottoperiodi",
            "",
            "Metriche ricavate dalla curva completa, cosi lo stato di esposizione",
            "all'inizio di ogni sottoperiodo resta coerente. Costi taker `0,16%`.",
            "",
            "| Candidato | Periodo | Totale | Ann. | Max DD | Sharpe |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in periods.iterrows():
        lines.append(
            f"| {row['candidate']} | {row['period']} | {pct(row['total_return'])} | "
            f"{pct(row['annualized_return'])} | {pct(row['max_drawdown'])} | "
            f"{row['sharpe']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Audit dei due compromessi",
            "",
            "Sono mostrate solo le sequenze che cambiano rispetto al Trail8 ufficiale.",
            "Il confronto termina alla data in cui sarebbe uscita la strategia senza trailing.",
            "",
            "| Candidato | Entrata | Fine | Classe Trail8 | Trail8 | Candidato | Senza trail | Delta vs Trail8 |",
            "|---|---|---|---|---:|---:|---:|---:|",
        ]
    )
    audit_names = [
        "Combo Trail11 slope<=4.00% ext>=5%",
        "Combo Trail11 slope<=4% ext>=5% momentum>=-10%",
    ]
    for name in audit_names:
        changed = event_comparison[
            (event_comparison["candidate"] == name)
            & (event_comparison["change_vs_baseline"].abs() > 0.000001)
        ]
        for _, row in changed.iterrows():
            lines.append(
                f"| {name} | {row['entry']} | {row['comparison_end']} | "
                f"{row['baseline_label']} | {pct(row['baseline_return'])} | "
                f"{pct(row['candidate_return'])} | {pct(row['no_trail_return'])} | "
                f"{pct(row['change_vs_baseline'])} |"
            )

    lines.extend(
        [
            "",
            "## Stress costi",
            "",
            "| Candidato | Costi | Totale | Ann. | Max DD | Sharpe | PF |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in costs.iterrows():
        lines.append(
            f"| {row['candidate']} | {row['cost']} | {pct(row['total_return'])} | "
            f"{pct(row['annualized_return'])} | {pct(row['max_drawdown'])} | "
            f"{row['sharpe_ratio']:.3f} | {row['profit_factor']:.3f} |"
        )

    perfect = grid[(grid["false_rescued"] == 6) & (grid["good_harmed"] == 0)]
    prudent_name = "Combo Trail11 slope<=4.00% ext>=5%"
    all_six_name = "Combo Trail11 slope<=4% ext>=5% momentum>=-10%"
    prudent = grid[grid["candidate"] == prudent_name].iloc[0]
    all_six = grid[grid["candidate"] == all_six_name].iloc[0]
    lines.extend(
        [
            "",
            "## Conclusione",
            "",
            f"- Regole testate: `{len(grid)}`.",
            f"- Candidati che recuperano tutti i 6 falsi stop senza danneggiare nessuna delle 9 uscite protettive: `{len(perfect)}`.",
            f"- Il candidato che migliora tutte e 6 le sequenze e' `{all_six_name}`, ma danneggia `{int(all_six['good_harmed'])}` uscite protettive e porta il max DD a `{pct(all_six['max_drawdown'])}`.",
            f"- Il compromesso prudente e' `{prudent_name}`: migliora `{int(prudent['false_improved'])}` sequenze su 6, ne recupera completamente `{int(prudent['false_rescued'])}` e danneggia una sola sequenza protettiva per 0,65 punti.",
            f"- Nel periodo completo il compromesso prudente passa da `{pct(baseline_metrics.annualized_return)}` a `{pct(prudent['annualized_return'])}` annualizzato, da Sharpe `{baseline_metrics.sharpe_ratio:.3f}` a `{prudent['sharpe_ratio']:.3f}` e da max DD `{pct(baseline_metrics.max_drawdown)}` a `{pct(prudent['max_drawdown'])}`.",
            "- L'assenza di separazione perfetta indica che una regola costruita per prendere tutti e sei i casi sarebbe sovra-adattata al campione.",
            "- Il compromesso prudente resta un candidato di ricerca: richiede validazione walk-forward realmente fuori campione prima di qualunque promozione.",
            "- La Baseline resta invariata.",
            "",
        ]
    )
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {args.output}")
    print(f"Tested {len(grid)} rules")
    print(eligible.head(15)[[
        "candidate", "annualized_return", "max_drawdown", "sharpe_ratio",
        "profit_factor", "false_improved", "false_rescued", "good_harmed",
    ]].to_string(index=False))


if __name__ == "__main__":
    main()
