"""
Test sperimentale: Trail8 valutato prima delle condizioni BUY.

Non modifica la Baseline ufficiale. Serve a capire se conviene uscire con
trailing stop confermato anche quando le condizioni di acquisto sono ancora
vere.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backtest.backtest import run_backtest
from config import CFG
from strategy.signals import (
    ENTRY_RSI_MAX,
    TRAILING_MOMENTUM_MIN,
    TRAILING_STOP_PCT,
    TRAILING_VOLUME_REL_MIN,
)


DATA_PATH = ROOT / "data" / "indicators_with_signals.csv"
REPORT_MD = ROOT / "reports" / "trail_priority_validation.md"
EVENTS_CSV = ROOT / "reports" / "trail_priority_events.csv"
TRADES_CSV = ROOT / "reports" / "trail_priority_trades.csv"


def _pct(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date")
    return df.set_index("Date")


def _trail_confirmed(row: pd.Series, close_value: float) -> tuple[bool, float, float]:
    close_ago = row.get(f"Close_{CFG.momentum_days}d_ago", np.nan)
    volume_avg = row.get("VolumeAvg20", np.nan)
    momentum_7d = (
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
        pd.notna(momentum_7d)
        and pd.notna(volume_rel)
        and momentum_7d >= TRAILING_MOMENTUM_MIN
        and volume_rel >= TRAILING_VOLUME_REL_MIN
    )
    return confirmed, float(momentum_7d), float(volume_rel)


def apply_trail_priority(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df.copy()

    close = out["Close"]
    sma50 = out["SMA50"]
    sma200 = out["SMA200"]
    rsi = out["RSI"]
    volume = out["Volume"]
    volume_avg20 = out["VolumeAvg20"]
    close_momentum = out[f"Close_{CFG.momentum_days}d_ago"]

    official_buy_cond = (
        (close > sma200)
        & (sma50 > sma200)
        & (rsi >= 40)
        & (close > close_momentum)
        & (volume > volume_avg20)
    )
    filtered_new_entry_cond = official_buy_cond & (rsi <= ENTRY_RSI_MAX)
    below_sma50 = close < sma50
    official_sell_cond = below_sma50 & below_sma50.shift(1).fillna(False)

    signals = np.full(len(out), "MANTIENI", dtype=object)
    trail_hit = pd.Series(False, index=out.index)
    trail_confirmed = pd.Series(False, index=out.index)
    events: list[dict[str, object]] = []

    exposure = False
    peak_close: float | None = None
    entry_date: pd.Timestamp | None = None
    entry_close: float | None = None

    for pos, (date, row) in enumerate(out.iterrows()):
        close_value = float(row["Close"])
        should_official_sell = bool(official_sell_cond.loc[date])
        should_trail_sell = False
        stop_level = np.nan
        momentum_7d = np.nan
        volume_rel = np.nan

        if should_official_sell:
            signals[pos] = "VENDI"
            if exposure:
                events.append(
                    {
                        "date": date.date(),
                        "event": "EXIT",
                        "reason": "Official_Sell",
                        "entry_date": entry_date.date() if entry_date is not None else None,
                        "entry_close": entry_close,
                        "exit_close": close_value,
                        "trade_return": close_value / entry_close - 1.0 if entry_close else np.nan,
                        "peak_close": peak_close,
                        "stop_level": stop_level,
                        "momentum_7d": momentum_7d,
                        "volume_rel": volume_rel,
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
                        "reason": "Trail8_Priority",
                        "entry_date": entry_date.date() if entry_date is not None else None,
                        "entry_close": entry_close,
                        "exit_close": close_value,
                        "trade_return": close_value / entry_close - 1.0 if entry_close else np.nan,
                        "peak_close": peak_close,
                        "stop_level": stop_level,
                        "momentum_7d": momentum_7d,
                        "volume_rel": volume_rel,
                        "official_buy_still_true": bool(official_buy_cond.loc[date]),
                    }
                )
                exposure = False
                peak_close = None
                entry_date = None
                entry_close = None
                continue

        if bool(filtered_new_entry_cond.loc[date]) and not exposure:
            signals[pos] = "ACQUISTA"
            exposure = True
            peak_close = close_value
            entry_date = date
            entry_close = close_value
            events.append(
                {
                    "date": date.date(),
                    "event": "ENTRY",
                    "reason": "Buy",
                    "entry_date": date.date(),
                    "entry_close": close_value,
                    "exit_close": np.nan,
                    "trade_return": np.nan,
                    "peak_close": peak_close,
                    "stop_level": np.nan,
                    "momentum_7d": np.nan,
                    "volume_rel": np.nan,
                    "official_buy_still_true": bool(official_buy_cond.loc[date]),
                }
            )

    out["Segnale"] = signals
    out["Trail8_Stop_Hit_Priority"] = trail_hit
    out["Trail8_Confirmed_Priority"] = trail_confirmed
    return out, pd.DataFrame(events)


def _metrics_row(name: str, metrics) -> dict[str, object]:
    return {
        "model": name,
        "total_return": metrics.total_return,
        "annualized_return": metrics.annualized_return,
        "max_drawdown": metrics.max_drawdown,
        "sharpe": metrics.sharpe_ratio,
        "profit_factor": metrics.profit_factor,
        "operations": metrics.num_operations,
        "win_rate": metrics.win_rate,
        "exposure": metrics.exposure_ratio,
        "turnover": metrics.turnover,
    }


def _completed_trades_from_events(events: pd.DataFrame) -> pd.DataFrame:
    exits = events[events["event"] == "EXIT"].copy()
    if exits.empty:
        return exits
    exits["trade_return_pct"] = exits["trade_return"] * 100.0
    return exits


def main() -> None:
    df = _load_data()

    baseline = df.copy()
    variant, events = apply_trail_priority(df)

    _, baseline_metrics, _ = run_backtest(baseline)
    _, variant_metrics, _ = run_backtest(variant)

    rows = [
        _metrics_row("Baseline ufficiale", baseline_metrics),
        _metrics_row("Trail8 priority", variant_metrics),
    ]
    metrics_df = pd.DataFrame(rows)

    cost_rows: list[dict[str, object]] = []
    for cost in [0.0, 0.001, 0.0025, 0.005, 0.01]:
        _, base_cost_metrics, _ = run_backtest(baseline, transaction_cost_rate=cost)
        _, variant_cost_metrics, _ = run_backtest(variant, transaction_cost_rate=cost)
        cost_rows.extend(
            [
                {"cost": cost, **_metrics_row("Baseline ufficiale", base_cost_metrics)},
                {"cost": cost, **_metrics_row("Trail8 priority", variant_cost_metrics)},
            ]
        )
    cost_df = pd.DataFrame(cost_rows)

    trades = _completed_trades_from_events(events)
    EVENTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    events.to_csv(EVENTS_CSV, index=False)
    trades.to_csv(TRADES_CSV, index=False)

    priority_exits = events[(events["event"] == "EXIT") & (events["reason"] == "Trail8_Priority")]
    priority_while_buy = priority_exits[priority_exits.get("official_buy_still_true", False) == True]

    lines = [
        "# Trail8 Priority Validation",
        "",
        "Test sperimentale: valutare il trailing stop 8% confermato prima delle condizioni BUY quando la posizione e' gia' aperta.",
        "",
        "La Baseline ufficiale non viene modificata.",
        "",
        "## Metriche USD",
        "",
        "| Modello | Totale | Ann. | Max DD | Sharpe | PF | Operazioni | Win rate | Esposizione | Turnover |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['model']} | {_pct(row['total_return'])} | {_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | {row['sharpe']:.3f} | {row['profit_factor']:.3f} | "
            f"{row['operations']} | {_pct(row['win_rate'])} | {_pct(row['exposure'])} | {row['turnover']:.0f} |"
        )

    lines.extend(
        [
            "",
            "## Stress Costi",
            "",
            "| Costo cambio esposizione | Modello | Ann. | Max DD | Sharpe | PF | Operazioni |",
            "|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in cost_df.iterrows():
        lines.append(
            f"| {_pct(row['cost'])} | {row['model']} | {_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | {row['sharpe']:.3f} | {row['profit_factor']:.3f} | "
            f"{int(row['operations'])} |"
        )

    lines.extend(
        [
            "",
            "## Uscite Trail8 Priority",
            "",
            f"- Uscite Trail8 nella variante: {len(priority_exits)}.",
            f"- Uscite Trail8 avvenute mentre le condizioni BUY erano ancora vere: {len(priority_while_buy)}.",
            "",
        ]
    )

    if not priority_exits.empty:
        lines.extend(
            [
                "| Data | Entry | Exit USD | Return trade | Peak | Stop | Mom 7g | Volume rel | BUY ancora vero |",
                "|---|---|---:|---:|---:|---:|---:|---:|---|",
            ]
        )
        for _, row in priority_exits.iterrows():
            lines.append(
                f"| {row['date']} | {row['entry_date']} | {row['exit_close']:.2f} | "
                f"{_pct(row['trade_return'])} | {row['peak_close']:.2f} | {row['stop_level']:.2f} | "
                f"{_pct(row['momentum_7d'])} | {_pct(row['volume_rel'])} | "
                f"{bool(row.get('official_buy_still_true', False))} |"
            )

    lines.extend(
        [
            "",
            "## File generati",
            "",
            f"- `{EVENTS_CSV.relative_to(ROOT)}`",
            f"- `{TRADES_CSV.relative_to(ROOT)}`",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(metrics_df.to_string(index=False))
    print(f"Priority exits: {len(priority_exits)}")
    print(f"Priority exits while BUY still true: {len(priority_while_buy)}")
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
