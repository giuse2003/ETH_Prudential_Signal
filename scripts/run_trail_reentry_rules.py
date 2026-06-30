"""
Test regole di rientro dopo uscita Trail8 priority.

Varianti testate:
- cooldown fisso: dopo Trail8 ignora ACQUISTA per X giorni;
- reset + conferma verde: dopo Trail8 richiede almeno una condizione BUY rossa,
  poi X giorni consecutivi con tutte le condizioni BUY vere.
- wait_official_sell: dopo Trail8 ignora nuovi ACQUISTA finche' non arriva il
  VENDI ufficiale sotto SMA50 per 2 giorni.

La Baseline ufficiale non viene modificata.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backtest.backtest import run_backtest  # noqa: E402
from config import CFG  # noqa: E402
from scripts.run_trail_priority_validation import _trail_confirmed  # noqa: E402
from strategy.signals import ENTRY_RSI_MAX, TRAILING_STOP_PCT  # noqa: E402


DATA_PATH = ROOT / "data" / "indicators_with_signals.csv"
REPORT_MD = ROOT / "reports" / "trail_reentry_rules.md"
METRICS_CSV = ROOT / "reports" / "trail_reentry_rules_metrics.csv"
EVENTS_CSV = ROOT / "reports" / "trail_reentry_rules_events.csv"

COOLDOWNS = [0, 3, 7, 10, 14, 21, 30]


def _pct(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _load_data() -> pd.DataFrame:
    return pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date").set_index("Date")


def _conditions(df: pd.DataFrame) -> tuple[pd.Series, pd.Series, pd.Series]:
    close = df["Close"]
    sma50 = df["SMA50"]
    sma200 = df["SMA200"]
    rsi = df["RSI"]
    volume = df["Volume"]
    volume_avg20 = df["VolumeAvg20"]
    close_momentum = df[f"Close_{CFG.momentum_days}d_ago"]

    official_buy = (
        (close > sma200)
        & (sma50 > sma200)
        & (rsi >= 40)
        & (close > close_momentum)
        & (volume > volume_avg20)
    )
    filtered_buy = official_buy & (rsi <= ENTRY_RSI_MAX)
    below_sma50 = close < sma50
    official_sell = below_sma50 & below_sma50.shift(1).fillna(False)
    return official_buy, filtered_buy, official_sell


def apply_variant(df: pd.DataFrame, *, mode: str, cooldown_days: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df.copy()
    official_buy, filtered_buy, official_sell = _conditions(out)

    signals = np.full(len(out), "MANTIENI", dtype=object)
    trail_hit = pd.Series(False, index=out.index)
    trail_confirmed = pd.Series(False, index=out.index)
    entry_blocked = pd.Series(False, index=out.index)
    events: list[dict[str, object]] = []

    exposure = False
    peak_close: float | None = None
    entry_date: pd.Timestamp | None = None
    entry_close: float | None = None
    last_trail_exit_date: pd.Timestamp | None = None
    reset_seen_red = False
    green_streak = 0
    wait_official_sell_reset = False

    for pos, (date, row) in enumerate(out.iterrows()):
        close_value = float(row["Close"])
        buy_ok = bool(filtered_buy.loc[date])
        official_buy_ok = bool(official_buy.loc[date])
        official_sell_ok = bool(official_sell.loc[date])
        should_trail_sell = False
        block_reason = ""

        if official_sell_ok:
            if wait_official_sell_reset:
                wait_official_sell_reset = False
                last_trail_exit_date = None
            signals[pos] = "VENDI"
            if exposure:
                events.append(
                    {
                        "date": date.date(),
                        "event": "EXIT",
                        "reason": "Official_Sell",
                        "mode": mode,
                        "cooldown_days": cooldown_days,
                        "entry_date": entry_date.date() if entry_date is not None else None,
                        "entry_close": entry_close,
                        "exit_close": close_value,
                        "trade_return": close_value / entry_close - 1.0 if entry_close else np.nan,
                    }
                )
            exposure = False
            peak_close = None
            entry_date = None
            entry_close = None
            continue

        if exposure:
            peak_close = max(peak_close if peak_close is not None else close_value, close_value)
            stop_level = peak_close * (1.0 - TRAILING_STOP_PCT)
            stop_hit = close_value <= stop_level
            trail_hit.loc[date] = bool(stop_hit)
            if stop_hit:
                confirmed, momentum_7d, volume_rel = _trail_confirmed(row, close_value)
                should_trail_sell = confirmed
                trail_confirmed.loc[date] = confirmed

            if should_trail_sell:
                signals[pos] = "VENDI"
                events.append(
                    {
                        "date": date.date(),
                        "event": "EXIT",
                        "reason": "Trail8",
                        "mode": mode,
                        "cooldown_days": cooldown_days,
                        "entry_date": entry_date.date() if entry_date is not None else None,
                        "entry_close": entry_close,
                        "exit_close": close_value,
                        "trade_return": close_value / entry_close - 1.0 if entry_close else np.nan,
                        "peak_close": peak_close,
                        "stop_level": stop_level,
                        "momentum_7d": momentum_7d,
                        "volume_rel": volume_rel,
                        "official_buy_still_true": official_buy_ok,
                    }
                )
                exposure = False
                peak_close = None
                entry_date = None
                entry_close = None
                last_trail_exit_date = date
                reset_seen_red = False
                green_streak = 0
                wait_official_sell_reset = mode == "wait_official_sell"
                continue

        if last_trail_exit_date is not None and not exposure:
            days_since_trail = int((date - last_trail_exit_date).days)
            if mode == "cooldown":
                if days_since_trail < cooldown_days:
                    block_reason = f"cooldown_{cooldown_days}"
            elif mode == "reset_green":
                if not buy_ok:
                    reset_seen_red = True
                    green_streak = 0
                else:
                    green_streak = green_streak + 1 if reset_seen_red else 0
                if not reset_seen_red:
                    block_reason = "wait_red_condition"
                elif green_streak < cooldown_days:
                    block_reason = f"wait_{cooldown_days}_green_days"
            elif mode == "wait_official_sell":
                if wait_official_sell_reset:
                    block_reason = "wait_official_sell"

        if buy_ok and not exposure:
            if block_reason:
                entry_blocked.loc[date] = True
                events.append(
                    {
                        "date": date.date(),
                        "event": "BLOCKED_ENTRY",
                        "reason": block_reason,
                        "mode": mode,
                        "cooldown_days": cooldown_days,
                        "entry_close": close_value,
                        "days_since_trail": int((date - last_trail_exit_date).days)
                        if last_trail_exit_date is not None
                        else np.nan,
                        "reset_seen_red": reset_seen_red,
                        "green_streak": green_streak,
                    }
                )
            else:
                signals[pos] = "ACQUISTA"
                exposure = True
                peak_close = close_value
                entry_date = date
                entry_close = close_value
                last_trail_exit_date = None
                reset_seen_red = False
                green_streak = 0
                wait_official_sell_reset = False
                events.append(
                    {
                        "date": date.date(),
                        "event": "ENTRY",
                        "reason": "Buy",
                        "mode": mode,
                        "cooldown_days": cooldown_days,
                        "entry_date": date.date(),
                        "entry_close": close_value,
                    }
                )

    out["Segnale"] = signals
    out["Trail8_Stop_Hit_ReentryTest"] = trail_hit
    out["Trail8_Confirmed_ReentryTest"] = trail_confirmed
    out["Entry_Blocked_ReentryTest"] = entry_blocked
    return out, pd.DataFrame(events)


def _metrics_row(label: str, mode: str, cooldown: int, metrics, events: pd.DataFrame) -> dict[str, object]:
    trail_exits = events[(events["event"] == "EXIT") & (events["reason"] == "Trail8")]
    blocked = events[events["event"] == "BLOCKED_ENTRY"]
    return {
        "label": label,
        "mode": mode,
        "cooldown_days": cooldown,
        "total_return": metrics.total_return,
        "annualized_return": metrics.annualized_return,
        "max_drawdown": metrics.max_drawdown,
        "sharpe": metrics.sharpe_ratio,
        "profit_factor": metrics.profit_factor,
        "operations": metrics.num_operations,
        "win_rate": metrics.win_rate,
        "exposure": metrics.exposure_ratio,
        "turnover": metrics.turnover,
        "trail_exits": len(trail_exits),
        "blocked_entries": len(blocked),
    }


def main() -> None:
    df = _load_data()

    rows: list[dict[str, object]] = []
    all_events: list[pd.DataFrame] = []

    _, base_metrics, _ = run_backtest(df)
    rows.append(
        {
            "label": "Baseline ufficiale",
            "mode": "baseline",
            "cooldown_days": 0,
            "total_return": base_metrics.total_return,
            "annualized_return": base_metrics.annualized_return,
            "max_drawdown": base_metrics.max_drawdown,
            "sharpe": base_metrics.sharpe_ratio,
            "profit_factor": base_metrics.profit_factor,
            "operations": base_metrics.num_operations,
            "win_rate": base_metrics.win_rate,
            "exposure": base_metrics.exposure_ratio,
            "turnover": base_metrics.turnover,
            "trail_exits": int(df.get("Trail8_Confirmed", pd.Series(False, index=df.index)).sum()),
            "blocked_entries": 0,
        }
    )

    test_grid = [(mode, cooldown) for mode in ["cooldown", "reset_green"] for cooldown in COOLDOWNS]
    test_grid.append(("wait_official_sell", 0))

    for mode, cooldown in test_grid:
            variant, events = apply_variant(df, mode=mode, cooldown_days=cooldown)
            _, metrics, _ = run_backtest(variant)
            if cooldown == 0 and mode == "cooldown":
                label = "Trail8 priority"
            elif mode == "wait_official_sell":
                label = "wait official sell"
            else:
                label = f"{mode} {cooldown}d"
            rows.append(_metrics_row(label, mode, cooldown, metrics, events))
            if not events.empty:
                all_events.append(events)

    metrics_df = pd.DataFrame(rows)
    events_df = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()

    METRICS_CSV.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(METRICS_CSV, index=False)
    events_df.to_csv(EVENTS_CSV, index=False)

    ranked = metrics_df[metrics_df["mode"] != "baseline"].sort_values(
        ["sharpe", "annualized_return"], ascending=[False, False]
    )

    lines = [
        "# Trail8 Reentry Rules",
        "",
        "Test sperimentale su regole di rientro dopo uscita Trail8 priority.",
        "",
        "La Baseline ufficiale non viene modificata.",
        "",
        "## Regole Testate",
        "",
        "- `cooldown Xd`: dopo una uscita Trail8 ignora nuovi ACQUISTA per X giorni.",
        "- `reset_green Xd`: dopo una uscita Trail8 richiede almeno una condizione BUY rossa, poi X giorni consecutivi con BUY tutte verdi.",
        "- `wait_official_sell`: dopo una uscita Trail8 ignora nuovi ACQUISTA finche' non arriva il VENDI ufficiale sotto SMA50 per 2 giorni.",
        "",
        "## Metriche",
        "",
        "| Modello | Ann. | Max DD | Sharpe | PF | Operazioni | Trail8 exits | Entry bloccati |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for _, row in metrics_df.iterrows():
        lines.append(
            f"| {row['label']} | {_pct(row['annualized_return'])} | {_pct(row['max_drawdown'])} | "
            f"{row['sharpe']:.3f} | {row['profit_factor']:.3f} | {int(row['operations'])} | "
            f"{int(row['trail_exits'])} | {int(row['blocked_entries'])} |"
        )

    lines.extend(
        [
            "",
            "## Migliori Varianti Per Sharpe",
            "",
            "| Rank | Modello | Ann. | Max DD | Sharpe | PF | Operazioni |",
            "|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for rank, (_, row) in enumerate(ranked.head(8).iterrows(), start=1):
        lines.append(
            f"| {rank} | {row['label']} | {_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | {row['sharpe']:.3f} | "
            f"{row['profit_factor']:.3f} | {int(row['operations'])} |"
        )

    lines.extend(
        [
            "",
            "## File generati",
            "",
            f"- `{METRICS_CSV.relative_to(ROOT)}`",
            f"- `{EVENTS_CSV.relative_to(ROOT)}`",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(metrics_df.to_string(index=False))
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
