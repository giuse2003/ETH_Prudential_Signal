"""
Test uscita SMA50 a 1 giorno contro Baseline SMA50 a 2 giorni.

Gli ingressi e il Trail8 restano invariati. Il conteggio di entrate/uscite
considera solo operazioni effettive, non i segnali VENDI ripetuti quando il
sistema e' gia' fuori mercato.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backtest.backtest import run_backtest  # noqa: E402
from config import CFG  # noqa: E402
from strategy.signals import ENTRY_RSI_MAX, _stateful_signals  # noqa: E402


DATA_PATH = ROOT / "data" / "indicators_with_signals.csv"
REPORT_MD = ROOT / "reports" / "sma50_exit_timing_test.md"
TRADES_CSV = ROOT / "reports" / "sma50_exit_timing_trades.csv"


def _pct(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _build_signals(df: pd.DataFrame, *, sell_after_days: int) -> pd.DataFrame:
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
    if sell_after_days == 1:
        official_sell = below_sma50
    elif sell_after_days == 2:
        official_sell = below_sma50 & below_sma50.shift(1).fillna(False)
    else:
        raise ValueError("sell_after_days deve essere 1 o 2.")

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


def _trades(df: pd.DataFrame, model: str) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    exposure = False
    entry_date = None
    entry_price = None

    for date, row in df.iterrows():
        signal = row["Segnale"]
        close = float(row["Close"])
        if signal == "ACQUISTA" and not exposure:
            exposure = True
            entry_date = date
            entry_price = close
        elif signal == "VENDI" and exposure:
            if bool(row["Trail8_Confirmed_Test"]):
                reason = "Trail8"
            elif bool(row["Official_Sell_Test"]):
                reason = "SMA50"
            else:
                reason = "VENDI"
            rows.append(
                {
                    "model": model,
                    "entry_date": entry_date.date(),
                    "entry_price": entry_price,
                    "exit_date": date.date(),
                    "exit_price": close,
                    "exit_reason": reason,
                    "return": close / entry_price - 1.0,
                    "days": int((date - entry_date).days),
                }
            )
            exposure = False
            entry_date = None
            entry_price = None

    return pd.DataFrame(rows)


def _summary(model: str, signals: pd.DataFrame, trades: pd.DataFrame) -> dict[str, object]:
    _, metrics, _ = run_backtest(signals)
    return {
        "model": model,
        "entries": len(trades),
        "exits": len(trades),
        "sma50_exits": int((trades["exit_reason"] == "SMA50").sum()),
        "trail8_exits": int((trades["exit_reason"] == "Trail8").sum()),
        "total_return": metrics.total_return,
        "annualized_return": metrics.annualized_return,
        "max_drawdown": metrics.max_drawdown,
        "sharpe": metrics.sharpe_ratio,
        "profit_factor": metrics.profit_factor,
        "win_rate": metrics.win_rate,
        "exposure": metrics.exposure_ratio,
    }


def main() -> None:
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    baseline = _build_signals(df, sell_after_days=2)
    one_day = _build_signals(df, sell_after_days=1)

    base_trades = _trades(baseline, "SMA50 2 giorni + Trail8")
    one_trades = _trades(one_day, "SMA50 1 giorno + Trail8")
    trades = pd.concat([base_trades, one_trades], ignore_index=True)

    rows = [
        _summary("SMA50 2 giorni + Trail8", baseline, base_trades),
        _summary("SMA50 1 giorno + Trail8", one_day, one_trades),
    ]
    summary = pd.DataFrame(rows)
    delta = summary.iloc[1].copy()
    for key in [
        "entries",
        "exits",
        "sma50_exits",
        "trail8_exits",
        "total_return",
        "annualized_return",
        "max_drawdown",
        "sharpe",
        "profit_factor",
        "win_rate",
        "exposure",
    ]:
        delta[key] = summary.iloc[1][key] - summary.iloc[0][key]

    TRADES_CSV.parent.mkdir(parents=True, exist_ok=True)
    trades.to_csv(TRADES_CSV, index=False)

    lines = [
        "# SMA50 Exit Timing Test",
        "",
        "Test sperimentale: uscita se `Close < SMA50` per 1 giorno contro Baseline `Close < SMA50` per 2 giorni.",
        "",
        "Ingressi e Trail8 restano invariati. Le metriche sono in USD.",
        "",
        "## Metriche",
        "",
        "| Modello | Entrate | Uscite | Uscite SMA50 | Uscite Trail8 | Totale | Ann. | Max DD | Sharpe | PF | Win rate | Esposizione |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            f"| {row['model']} | {int(row['entries'])} | {int(row['exits'])} | "
            f"{int(row['sma50_exits'])} | {int(row['trail8_exits'])} | "
            f"{_pct(row['total_return'])} | {_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | {row['sharpe']:.3f} | {row['profit_factor']:.3f} | "
            f"{_pct(row['win_rate'])} | {_pct(row['exposure'])} |"
        )

    lines.extend(
        [
            "",
            "## Differenza 1 giorno vs 2 giorni",
            "",
            f"- Entrate: {int(delta['entries']):+d}.",
            f"- Uscite: {int(delta['exits']):+d}.",
            f"- Uscite SMA50 effettive: {int(delta['sma50_exits']):+d}.",
            f"- Uscite Trail8 effettive: {int(delta['trail8_exits']):+d}.",
            f"- Rendimento totale: {_pct(delta['total_return'])}.",
            f"- Rendimento annualizzato: {_pct(delta['annualized_return'])}.",
            f"- Max drawdown: {_pct(delta['max_drawdown'])}.",
            f"- Sharpe: {delta['sharpe']:+.3f}.",
            f"- Profit factor: {delta['profit_factor']:+.3f}.",
            "",
            "## File generato",
            "",
            f"- `{TRADES_CSV.relative_to(ROOT)}`",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(summary.to_string(index=False))
    print("Delta 1g - 2g")
    print(delta.to_string())
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
