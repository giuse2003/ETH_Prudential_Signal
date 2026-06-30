"""
Test uscita SMA50 a 1 giorno filtrata da rottura almeno 1% sotto SMA50.

Confronta:
- Baseline: Close sotto SMA50 per 2 giorni + Trail8;
- SMA50 1 giorno pura: Close sotto SMA50 per 1 giorno + Trail8;
- SMA50 1 giorno -1%: Close almeno 1% sotto SMA50 oppure 2 giorni sotto SMA50.

Ingressi e Trail8 restano invariati. Metriche in USD.
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
from scripts.run_sma50_exit_timing_test import _build_signals, _trades  # noqa: E402


DATA_PATH = ROOT / "data" / "indicators_with_signals.csv"
REPORT_MD = ROOT / "reports" / "sma50_exit_1pct_filter_test.md"
TRADES_CSV = ROOT / "reports" / "sma50_exit_1pct_filter_trades.csv"


def _pct(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _build_1pct_filter(df: pd.DataFrame) -> pd.DataFrame:
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
    below_sma50_deep_1pct = close <= sma50 * 0.99
    official_sell = below_sma50_two_days | below_sma50_deep_1pct

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


def _summary(model: str, signals: pd.DataFrame) -> dict[str, object]:
    _, metrics, _ = run_backtest(signals)
    trades = _trades(signals, model)
    return {
        "model": model,
        "total_return": metrics.total_return,
        "annualized_return": metrics.annualized_return,
        "max_drawdown": metrics.max_drawdown,
        "sharpe": metrics.sharpe_ratio,
        "profit_factor": metrics.profit_factor,
        "operations": metrics.num_operations,
        "entries": len(trades),
        "sma50_exits": int((trades["exit_reason"] == "SMA50").sum()),
        "trail8_exits": int((trades["exit_reason"] == "Trail8").sum()),
        "exposure": metrics.exposure_ratio,
        "turnover": metrics.turnover,
    }


def main() -> None:
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    models = {
        "SMA50 2 giorni + Trail8": _build_signals(df, sell_after_days=2),
        "SMA50 1 giorno pura + Trail8": _build_signals(df, sell_after_days=1),
        "SMA50 1 giorno solo se -1% + Trail8": _build_1pct_filter(df),
    }

    summaries = pd.DataFrame([_summary(name, signals) for name, signals in models.items()])
    trades = pd.concat([_trades(signals, name) for name, signals in models.items()], ignore_index=True)
    TRADES_CSV.parent.mkdir(parents=True, exist_ok=True)
    trades.to_csv(TRADES_CSV, index=False)

    base = summaries.iloc[0]
    plain = summaries.iloc[1]
    filtered = summaries.iloc[2]

    lines = [
        "# SMA50 Exit 1pct Filter Test",
        "",
        "Test sperimentale: uscita a 1 giorno solo se `Close <= SMA50 * 0.99`.",
        "Se la rottura non arriva ad almeno -1%, resta valida la Baseline a 2 giorni.",
        "Ingressi e Trail8 restano invariati. Metriche in USD.",
        "",
        "## Metriche",
        "",
        "| Modello | Totale | Ann. | Max DD | Sharpe | PF | Operazioni | Entry | SMA50 exit | Trail8 exit | Esposizione | Turnover |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in summaries.iterrows():
        lines.append(
            f"| {row['model']} | {_pct(row['total_return'])} | {_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | {row['sharpe']:.3f} | {row['profit_factor']:.3f} | "
            f"{int(row['operations'])} | {int(row['entries'])} | {int(row['sma50_exits'])} | "
            f"{int(row['trail8_exits'])} | {_pct(row['exposure'])} | {row['turnover']:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Delta filtro -1%",
            "",
            "| Confronto | Delta ann. | Delta DD | Delta Sharpe | Delta PF | Delta operazioni |",
            "|---|---:|---:|---:|---:|---:|",
            (
                f"| vs Baseline 2 giorni | "
                f"{_pct(float(filtered['annualized_return']) - float(base['annualized_return']))} | "
                f"{_pct(float(filtered['max_drawdown']) - float(base['max_drawdown']))} | "
                f"{float(filtered['sharpe']) - float(base['sharpe']):+.3f} | "
                f"{float(filtered['profit_factor']) - float(base['profit_factor']):+.3f} | "
                f"{int(filtered['operations']) - int(base['operations']):+d} |"
            ),
            (
                f"| vs SMA50 1 giorno pura | "
                f"{_pct(float(filtered['annualized_return']) - float(plain['annualized_return']))} | "
                f"{_pct(float(filtered['max_drawdown']) - float(plain['max_drawdown']))} | "
                f"{float(filtered['sharpe']) - float(plain['sharpe']):+.3f} | "
                f"{float(filtered['profit_factor']) - float(plain['profit_factor']):+.3f} | "
                f"{int(filtered['operations']) - int(plain['operations']):+d} |"
            ),
            "",
            "## File generato",
            "",
            f"- `{TRADES_CSV.relative_to(ROOT)}`",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(summaries.to_string(index=False))
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
