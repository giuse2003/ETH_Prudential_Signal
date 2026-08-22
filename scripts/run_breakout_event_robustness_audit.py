"""Audit dei singoli eventi del candidato breakout precoce.

Confronta il falso ingresso del 13 gennaio 2026 con gli episodi favorevoli,
senza cercare o applicare nuove soglie alla strategia ufficiale.
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta
import math
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import run_backtest
from data.coinbase import fetch_daily_candles
from indicators.technical_indicators import compute_all_indicators
from pipeline import evaluation_frame
from scripts.run_august_2026_breakout_entry_research import (
    PRE_EVENT_END,
    TAKER_FEE,
    _return_stats,
    add_research_features,
    build_signal_frame,
    build_variants,
    divergence_segments,
    extract_trades,
)
from strategy.signals import (
    SMA50_BREAK_PCT,
    TRAILING_MOMENTUM_MIN,
    TRAILING_STOP_PCT,
    TRAILING_VOLUME_REL_MIN,
    compute_signals,
)


CANDIDATE_NAME = "early_lb5_vol20_near10_slope0"
OUT_MD = PROJECT_ROOT / "reports" / "august_2026_breakout_event_audit.md"
OUT_EVENTS = PROJECT_ROOT / "reports" / "august_2026_breakout_event_features.csv"
OUT_FEATURES = PROJECT_ROOT / "reports" / "august_2026_breakout_bad_event_features.csv"
OUT_LOEO = PROJECT_ROOT / "reports" / "august_2026_breakout_leave_one_out.csv"
OUT_STATS = PROJECT_ROOT / "reports" / "august_2026_breakout_event_statistics.csv"
OUT_EXIT_STATE = PROJECT_ROOT / "reports" / "august_2026_breakout_exit_state.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit robustezza eventi breakout.")
    parser.add_argument(
        "--as-of",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Ultima candela daily chiusa inclusa (YYYY-MM-DD).",
    )
    parser.add_argument("--output", type=Path, default=OUT_MD)
    return parser.parse_args()


def add_context_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["SMA50VsSMA200"] = out["SMA50"] / out["SMA200"] - 1.0
    out["SMA50Slope20"] = out["SMA50"] / out["SMA50"].shift(20) - 1.0
    out["SMA200Slope20"] = out["SMA200"] / out["SMA200"].shift(20) - 1.0
    out["Return1"] = out["Close"].pct_change()
    out["Return30"] = out["Close"] / out["Close"].shift(30) - 1.0
    out["Return90"] = out["Close"] / out["Close"].shift(90) - 1.0
    out["Drawdown90"] = out["Close"] / out["Close"].rolling(90).max() - 1.0
    out["ATRRel"] = out["ATR"] / out["Close"]
    out["RSIChange3"] = out["RSI"] - out["RSI"].shift(3)
    out["CandleRange"] = (out["High"] - out["Low"]) / out["Close"]
    candle_span = (out["High"] - out["Low"]).replace(0.0, np.nan)
    out["CloseLocation"] = (out["Close"] - out["Low"]) / candle_span
    out["Breakout5"] = out["Close"] / out["PriorHigh5"] - 1.0
    return out


def _forward_return(close: pd.Series, day: pd.Timestamp, horizon: int) -> float:
    pos = close.index.get_loc(day)
    if not isinstance(pos, (int, np.integer)) or pos + horizon >= len(close):
        return np.nan
    return float(close.iloc[pos + horizon] / close.iloc[pos] - 1.0)


def event_table(
    indicators: pd.DataFrame,
    candidate_frame: pd.DataFrame,
    trades: pd.DataFrame,
    segments: pd.DataFrame,
) -> pd.DataFrame:
    alternative = trades[trades["entry_origin"] == "early_breakout"].copy()
    segment_index = segments.set_index("trigger_signal_date")
    rows: list[dict[str, object]] = []
    for _, trade in alternative.iterrows():
        day = pd.Timestamp(trade["entry_date"])
        row = indicators.loc[day]
        segment = segment_index.loc[day]
        if isinstance(segment, pd.DataFrame):
            segment = segment.iloc[0]
        end = (
            pd.Timestamp(trade["exit_date"])
            if pd.notna(trade["exit_date"])
            else candidate_frame.index[-1]
        )
        prices = indicators.loc[day:end, "Close"]
        wealth_advantage = float(segment["wealth_advantage"])
        status = str(trade["status"])
        outcome = (
            "open"
            if status == "open"
            else ("favorable" if wealth_advantage > 0.0 else "negative")
        )
        rows.append(
            {
                "entry_date": day,
                "entry_price": float(trade["entry_price"]),
                "outcome": outcome,
                "exit_date": trade["exit_date"],
                "exit_price": trade["exit_price"],
                "exit_origin": trade["exit_origin"],
                "trade_net_return": float(trade["net_return"]),
                "wealth_advantage_vs_baseline": wealth_advantage,
                "baseline_next_buy": segment["baseline_next_buy"],
                "mfe_to_exit": float(prices.max() / prices.iloc[0] - 1.0),
                "mae_to_exit": float(prices.min() / prices.iloc[0] - 1.0),
                "forward_1d": _forward_return(indicators["Close"], day, 1),
                "forward_3d": _forward_return(indicators["Close"], day, 3),
                "forward_7d": _forward_return(indicators["Close"], day, 7),
                "forward_14d": _forward_return(indicators["Close"], day, 14),
                "forward_30d": _forward_return(indicators["Close"], day, 30),
                "rsi": float(row["RSI"]),
                "momentum_7d": float(row["Momentum7"]),
                "volume_rel_20": float(row["VolumeRel20"]),
                "sma50_slope_5d": float(row["SMA50Slope5"]),
                "sma50_slope_20d": float(row["SMA50Slope20"]),
                "sma200_slope_20d": float(row["SMA200Slope20"]),
                "distance_sma50": float(row["DistanceSMA50"]),
                "distance_sma200": float(row["DistanceSMA200"]),
                "sma50_vs_sma200": float(row["SMA50VsSMA200"]),
                "return_1d": float(row["Return1"]),
                "return_30d": float(row["Return30"]),
                "return_90d": float(row["Return90"]),
                "drawdown_90d": float(row["Drawdown90"]),
                "atr_relative": float(row["ATRRel"]),
                "rsi_change_3d": float(row["RSIChange3"]),
                "candle_range": float(row["CandleRange"]),
                "close_location": float(row["CloseLocation"]),
                "breakout_5d": float(row["Breakout5"]),
            }
        )
    return pd.DataFrame(rows)


def compare_bad_event_features(events: pd.DataFrame) -> pd.DataFrame:
    favorable = events[events["outcome"] == "favorable"]
    negative = events[events["outcome"] == "negative"].iloc[0]
    current = events[events["outcome"] == "open"].iloc[0]
    features = [
        "rsi",
        "momentum_7d",
        "volume_rel_20",
        "sma50_slope_5d",
        "sma50_slope_20d",
        "sma200_slope_20d",
        "distance_sma50",
        "distance_sma200",
        "sma50_vs_sma200",
        "return_1d",
        "return_30d",
        "return_90d",
        "drawdown_90d",
        "atr_relative",
        "rsi_change_3d",
        "candle_range",
        "close_location",
        "breakout_5d",
    ]
    rows: list[dict[str, object]] = []
    for feature in features:
        low = float(favorable[feature].min())
        high = float(favorable[feature].max())
        bad = float(negative[feature])
        rows.append(
            {
                "feature": feature,
                "favorable_min": low,
                "favorable_median": float(favorable[feature].median()),
                "favorable_max": high,
                "negative_2026_01_13": bad,
                "current_2026_08_17": float(current[feature]),
                "negative_outside_favorable_range": bool(bad < low or bad > high),
            }
        )
    return pd.DataFrame(rows)


def leave_one_event_out(
    baseline_equity: pd.DataFrame,
    candidate_equity: pd.DataFrame,
    segments: pd.DataFrame,
) -> pd.DataFrame:
    baseline_returns = baseline_equity.loc[:PRE_EVENT_END, "DailyReturnStrategy"].fillna(0.0)
    candidate_returns = candidate_equity.loc[:PRE_EVENT_END, "DailyReturnStrategy"].fillna(0.0)
    baseline_stats = _return_stats(baseline_returns)
    rows: list[dict[str, object]] = []

    def append_result(label: str, returns: pd.Series) -> None:
        stats = _return_stats(returns)
        rows.append(
            {
                "removed_event": label,
                **stats,
                "delta_annualized": stats["annualized_return"]
                - baseline_stats["annualized_return"],
                "delta_drawdown": stats["max_drawdown"]
                - baseline_stats["max_drawdown"],
                "delta_sharpe": stats["sharpe_ratio"] - baseline_stats["sharpe_ratio"],
                "improves_all3": bool(
                    stats["annualized_return"] > baseline_stats["annualized_return"]
                    and stats["max_drawdown"] >= baseline_stats["max_drawdown"] - 1e-12
                    and stats["sharpe_ratio"] > baseline_stats["sharpe_ratio"]
                ),
            }
        )

    append_result("none", candidate_returns)
    completed = segments[
        (pd.to_datetime(segments["trigger_signal_date"]) <= PRE_EVENT_END)
        & (segments["status"] == "closed")
    ]
    for _, segment in completed.iterrows():
        modified = candidate_returns.copy()
        start = pd.Timestamp(segment["start"])
        end = min(pd.Timestamp(segment["end"]), PRE_EVENT_END)
        modified.loc[start:end] = baseline_returns.loc[start:end]
        append_result(pd.Timestamp(segment["trigger_signal_date"]).date().isoformat(), modified)
    return pd.DataFrame(rows)


def event_level_statistics(events: pd.DataFrame) -> pd.DataFrame:
    completed = events[events["outcome"].isin(["favorable", "negative"])]
    advantages = completed["wealth_advantage_vs_baseline"].to_numpy(dtype=float)
    wins = int((advantages > 0.0).sum())
    n = len(advantages)
    sign_test_p = float(
        sum(math.comb(n, value) for value in range(wins, n + 1)) / (2**n)
    )

    z = 1.959963984540054
    p_hat = wins / n
    denominator = 1.0 + z**2 / n
    center = (p_hat + z**2 / (2.0 * n)) / denominator
    half_width = (
        z
        * math.sqrt(p_hat * (1.0 - p_hat) / n + z**2 / (4.0 * n**2))
        / denominator
    )

    rng = np.random.default_rng(20260822)
    samples = 20000
    positions = rng.integers(0, n, size=(samples, n))
    boot = np.prod(1.0 + advantages[positions], axis=1) - 1.0
    observed = float(np.prod(1.0 + advantages) - 1.0)
    negative = advantages[advantages < 0.0]
    repeat_loss = float(negative[0]) if len(negative) == 1 else np.nan
    losses_to_erase = np.nan
    if observed > 0.0 and pd.notna(repeat_loss) and -1.0 < repeat_loss < 0.0:
        losses_to_erase = math.ceil(
            math.log(1.0 / (1.0 + observed)) / math.log(1.0 + repeat_loss)
        )
    return pd.DataFrame(
        [
            {"metric": "completed_events", "value": n},
            {"metric": "favorable_events", "value": wins},
            {"metric": "event_win_rate", "value": p_hat},
            {"metric": "wilson_95_low", "value": max(0.0, center - half_width)},
            {"metric": "wilson_95_high", "value": min(1.0, center + half_width)},
            {"metric": "one_sided_sign_test_p", "value": sign_test_p},
            {"metric": "observed_compound_advantage", "value": observed},
            {"metric": "event_bootstrap_probability_positive", "value": float((boot > 0.0).mean())},
            {"metric": "event_bootstrap_p05", "value": float(np.quantile(boot, 0.05))},
            {"metric": "event_bootstrap_median", "value": float(np.median(boot))},
            {"metric": "event_bootstrap_p95", "value": float(np.quantile(boot, 0.95))},
            {"metric": "repeat_bad_losses_to_erase", "value": losses_to_erase},
        ]
    )


def current_exit_state(
    indicators: pd.DataFrame,
    candidate_frame: pd.DataFrame,
    events: pd.DataFrame,
) -> pd.DataFrame:
    open_events = events[events["outcome"] == "open"]
    if open_events.empty:
        return pd.DataFrame()
    event = open_events.iloc[-1]
    entry_date = pd.Timestamp(event["entry_date"])
    path = indicators.loc[entry_date:]
    peak_date = path["Close"].idxmax()
    peak_close = float(path.loc[peak_date, "Close"])
    latest_date = path.index[-1]
    latest = path.iloc[-1]
    close = float(latest["Close"])
    trail_level = peak_close * (1.0 - TRAILING_STOP_PCT)
    sma50_exit_level = float(latest["SMA50"]) * (1.0 - SMA50_BREAK_PCT)
    official_buy_core = bool(
        close > float(latest["SMA200"])
        and float(latest["SMA50"]) > float(latest["SMA200"])
        and float(latest["RSI"]) >= 40.0
        and float(latest["Momentum7"]) > 0.0
        and float(latest["VolumeRel20"]) > 0.0
    )
    trail_hit = bool(close <= trail_level)
    momentum_confirmed = bool(float(latest["Momentum7"]) >= TRAILING_MOMENTUM_MIN)
    volume_confirmed = bool(float(latest["VolumeRel20"]) >= TRAILING_VOLUME_REL_MIN)
    trail_exit = bool(
        not official_buy_core and trail_hit and momentum_confirmed and volume_confirmed
    )
    official_sma50_exit = bool(close < sma50_exit_level)
    return pd.DataFrame(
        [
            {
                "entry_date": entry_date,
                "entry_price": float(event["entry_price"]),
                "latest_date": latest_date,
                "latest_close": close,
                "peak_date": peak_date,
                "peak_close": peak_close,
                "trail8_level": trail_level,
                "distance_above_trail8": close / trail_level - 1.0,
                "trail8_hit": trail_hit,
                "momentum_7d": float(latest["Momentum7"]),
                "momentum_confirmed": momentum_confirmed,
                "volume_rel_20": float(latest["VolumeRel20"]),
                "volume_confirmed": volume_confirmed,
                "official_buy_core": official_buy_core,
                "sma50": float(latest["SMA50"]),
                "sma50_exit_level": sma50_exit_level,
                "official_sma50_exit": official_sma50_exit,
                "trail8_exit": trail_exit,
                "candidate_action": str(candidate_frame.loc[latest_date, "Segnale"]),
            }
        ]
    )


def _pct(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value * 100:.2f}%"


def _num(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value:.3f}"


def write_report(
    path: Path,
    *,
    as_of: str,
    events: pd.DataFrame,
    features: pd.DataFrame,
    loeo: pd.DataFrame,
    statistics: pd.DataFrame,
    exit_state: pd.DataFrame,
) -> None:
    stats = statistics.set_index("metric")["value"]
    outside = features[features["negative_outside_favorable_range"]]
    lines = [
        "# Audit robustezza degli ingressi breakout",
        "",
        f"Data test: `{date.today().isoformat()}`. Cutoff: `{as_of}`.",
        f"Candidato congelato: `{CANDIDATE_NAME}`. Commissione taker `0,16%`.",
        "La Baseline ufficiale non e' stata modificata.",
        "",
        "## Eventi",
        "",
        "| Entry | Esito | RSI | Mom. 7g | Volume rel. | Dist. SMA200 | SMA50/SMA200 | Return 90g | Breakout 5g | MFE | MAE | Vantaggio vs Baseline |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in events.iterrows():
        lines.append(
            f"| {pd.Timestamp(row['entry_date']).date().isoformat()} | {row['outcome']} | "
            f"{row['rsi']:.2f} | {_pct(row['momentum_7d'])} | "
            f"{_pct(row['volume_rel_20'])} | {_pct(row['distance_sma200'])} | "
            f"{_pct(row['sma50_vs_sma200'])} | {_pct(row['return_90d'])} | "
            f"{_pct(row['breakout_5d'])} | {_pct(row['mfe_to_exit'])} | "
            f"{_pct(row['mae_to_exit'])} | "
            f"{_pct(row['wealth_advantage_vs_baseline'])} |"
        )

    lines.extend(
        [
            "",
            "## Caso negativo del 13 gennaio 2026",
            "",
            "Valori che risultano fuori dall'intervallo osservato nei quattro eventi",
            "favorevoli. Sono descrittivi: con un solo caso negativo non costituiscono",
            "una soglia validata.",
            "",
            "| Caratteristica | Min favorevoli | Mediana favorevoli | Max favorevoli | 13/01/2026 | 17/08/2026 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in outside.iterrows():
        lines.append(
            f"| {row['feature']} | {_num(row['favorable_min'])} | "
            f"{_num(row['favorable_median'])} | {_num(row['favorable_max'])} | "
            f"{_num(row['negative_2026_01_13'])} | "
            f"{_num(row['current_2026_08_17'])} |"
        )

    lines.extend(
        [
            "",
            "## Leave-one-event-out",
            "",
            "Per ogni riga il rendimento del candidato nel segmento rimosso viene",
            "sostituito con quello della Baseline. Il test termina il 16 agosto 2026.",
            "",
            "| Evento rimosso | Annualizzato | Max DD | Sharpe | Delta ann. | Delta DD | Delta Sharpe | Migliora tutte e 3 |",
            "|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for _, row in loeo.iterrows():
        lines.append(
            f"| {row['removed_event']} | {_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | {_num(row['sharpe_ratio'])} | "
            f"{_pct(row['delta_annualized'])} | {_pct(row['delta_drawdown'])} | "
            f"{_num(row['delta_sharpe'])} | {'SI' if row['improves_all3'] else 'NO'} |"
        )

    lines.extend(
        [
            "",
            "## Statistica a livello di eventi",
            "",
            f"- eventi completati: `{int(stats['completed_events'])}`; favorevoli: "
            f"`{int(stats['favorable_events'])}`; win rate `{_pct(stats['event_win_rate'])}`;",
            f"- intervallo Wilson 95% del win rate: `{_pct(stats['wilson_95_low'])}` -> "
            f"`{_pct(stats['wilson_95_high'])}`;",
            f"- sign test unilaterale contro 50%: p-value `{_pct(stats['one_sided_sign_test_p'])}`;",
            f"- vantaggio composto osservato sui cinque segmenti: "
            f"`{_pct(stats['observed_compound_advantage'])}`;",
            f"- bootstrap per evento: probabilita' positiva "
            f"`{_pct(stats['event_bootstrap_probability_positive'])}`, intervallo 5%-95% "
            f"`{_pct(stats['event_bootstrap_p05'])}` -> `{_pct(stats['event_bootstrap_p95'])}`;",
            f"- servirebbero circa `{int(stats['repeat_bad_losses_to_erase'])}` perdite consecutive "
            "uguali al caso del 13 gennaio per annullare il vantaggio composto storico.",
        ]
    )
    if not exit_state.empty:
        state = exit_state.iloc[0]
        lines.extend(
            [
                "",
                "## Stato uscita del trade aperto",
                "",
                f"Aggiornamento alla candela `{pd.Timestamp(state['latest_date']).date().isoformat()}`:",
                "",
                f"- entry candidata `{pd.Timestamp(state['entry_date']).date().isoformat()}` a "
                f"`{state['entry_price']:.2f} USD`;",
                f"- massimo Close `{state['peak_close']:.2f} USD` il "
                f"`{pd.Timestamp(state['peak_date']).date().isoformat()}`;",
                f"- Trail8 dinamico `{state['trail8_level']:.2f} USD`; Close attuale "
                f"`{state['latest_close']:.2f} USD`, distanza `{_pct(state['distance_above_trail8'])}`;",
                f"- momentum 7g `{_pct(state['momentum_7d'])}` "
                f"({'confermato' if state['momentum_confirmed'] else 'non confermato'});",
                f"- volume relativo `{_pct(state['volume_rel_20'])}` "
                f"({'confermato' if state['volume_confirmed'] else 'non confermato'});",
                f"- livello uscita SMA50 `{state['sma50_exit_level']:.2f} USD`;",
                f"- azione candidata corrente: `{state['candidate_action']}`;",
                "- il livello Trail8 verra' ricalcolato su ogni nuovo massimo Close;",
                "  un suo superamento al ribasso produce VENDI soltanto con le conferme",
                "  momentum/volume e con la priorita' BUY originale della Baseline.",
            ]
        )

    lines.extend(
        [
            "",
            "## Decisione",
            "",
            "- il candidato non dipende da un solo episodio favorevole se il leave-one-out",
            "  continua a migliorare tutte le metriche;",
            "- il campione di cinque eventi completati resta troppo piccolo: il sign test",
            "  non raggiunge significativita' statistica al 5%;",
            "- le differenze del 13 gennaio sono indizi utili, ma trasformarle ora in",
            "  filtri significherebbe ottimizzare una regola su un solo errore;",
            "- ingresso alternativo e uscita sono ora separati nel runner: dopo ACQUISTA",
            "  la gestione e' esclusivamente quella ufficiale della Baseline;",
            "- mantenere congelato il candidato senza modificare la Baseline.",
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
    indicators = evaluation_frame(
        add_context_features(add_research_features(indicators_all))
    )
    variants = {variant.name: variant for variant in build_variants()}
    baseline_frame = build_signal_frame(indicators, variants["baseline"])
    candidate_frame = build_signal_frame(indicators, variants[CANDIDATE_NAME])
    if not baseline_frame["Segnale"].equals(official.loc[indicators.index, "Segnale"]):
        raise AssertionError("La replica della Baseline non coincide con i segnali ufficiali.")

    baseline_equity, _, _ = run_backtest(
        baseline_frame[["Close", "Segnale"]], transaction_cost_rate=TAKER_FEE
    )
    candidate_equity, _, _ = run_backtest(
        candidate_frame[["Close", "Segnale"]], transaction_cost_rate=TAKER_FEE
    )
    frames = {"baseline": baseline_frame, CANDIDATE_NAME: candidate_frame}
    equities = {"baseline": baseline_equity, CANDIDATE_NAME: candidate_equity}
    trades = extract_trades(
        candidate_frame, variant=CANDIDATE_NAME, fee_rate=TAKER_FEE
    )
    segments = divergence_segments(frames, equities, CANDIDATE_NAME)
    events = event_table(indicators, candidate_frame, trades, segments)
    features = compare_bad_event_features(events)
    loeo = leave_one_event_out(baseline_equity, candidate_equity, segments)
    statistics = event_level_statistics(events)
    exit_state = current_exit_state(indicators, candidate_frame, events)

    OUT_EVENTS.parent.mkdir(parents=True, exist_ok=True)
    events.to_csv(OUT_EVENTS, index=False)
    features.to_csv(OUT_FEATURES, index=False)
    loeo.to_csv(OUT_LOEO, index=False)
    statistics.to_csv(OUT_STATS, index=False)
    exit_state.to_csv(OUT_EXIT_STATE, index=False)
    write_report(
        args.output,
        as_of=args.as_of,
        events=events,
        features=features,
        loeo=loeo,
        statistics=statistics,
        exit_state=exit_state,
    )
    print(f"Saved {args.output}")
    print(events.to_string(index=False))
    print("\nLEAVE ONE OUT")
    print(loeo.to_string(index=False))
    print("\nEVENT STATISTICS")
    print(statistics.to_string(index=False))
    if not exit_state.empty:
        print("\nCURRENT EXIT STATE")
        print(exit_state.to_string(index=False))


if __name__ == "__main__":
    main()
