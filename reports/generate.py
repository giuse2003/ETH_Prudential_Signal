"""Generazione deterministica degli artefatti di ETH-USD Signal."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from config import CFG
from strategy.signals import HOLD_ACTION, live_condition_statuses


def write_utf8_text(out_path: str | Path, content: str) -> Path:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content.replace("\r\n", "\n").encode("utf-8"))
    return path


def save_dataframe_csv(
    frame: pd.DataFrame,
    out_path: str | Path,
    *,
    index: bool,
) -> Path:
    return write_utf8_text(out_path, frame.to_csv(index=index, lineterminator="\n"))


def _json_float(value) -> float | None:
    if value is None or pd.isna(value):
        return None
    return float(value)


def _condition_groups(
    buy_statuses: list[bool],
    breakout_statuses: list[bool],
    sell_statuses: list[bool],
    live: bool,
) -> dict:
    qualifier = " live" if live else ""
    buy_labels = [
        f"prezzo{qualifier} sopra SMA200",
        f"SMA50{qualifier} sopra SMA200",
        f"RSI{qualifier} tra 40 e 65 per i nuovi ingressi",
        f"prezzo{qualifier} sopra quello di 7 giorni prima",
        f"volume ETH-USD{qualifier} sopra media 20 giorni",
    ]
    breakout_labels = [
        f"SMA50{qualifier} sotto o uguale a SMA200",
        f"prezzo{qualifier} sopra SMA50 e almeno al 90% di SMA200",
        f"SMA50{qualifier} non in calo rispetto a 5 giorni prima",
        f"RSI{qualifier} tra 40 e 65",
        f"prezzo{qualifier} sopra quello di 7 giorni prima",
        f"volume ETH-USD{qualifier} almeno 20% sopra media 20 giorni",
        f"Close{qualifier} sopra i 5 Close precedenti",
        "guardrail superato: non insieme SMA200 slope20 > 0% e gap SMA50/SMA200 < -15%",
    ]
    sell_labels = [
        f"prezzo{qualifier} oltre il 2% sotto SMA50",
        "trailing stop 8% confermato da momentum 7g >= -15% e volume >= +20%",
    ]
    return {
        "buy": [
            {"label": label, "passed": bool(passed)}
            for label, passed in zip(buy_labels, buy_statuses)
        ],
        "buy_breakout": [
            {"label": label, "passed": bool(passed)}
            for label, passed in zip(breakout_labels, breakout_statuses)
        ],
        "sell": [
            {"label": label, "passed": bool(passed)}
            for label, passed in zip(sell_labels, sell_statuses)
        ],
    }


def save_historical_csv(df: pd.DataFrame, out_path: str | Path) -> Path:
    output = df.copy()
    output["Data"] = output.index.strftime("%Y-%m-%d")
    output["ETH-USD"] = output["Close"]
    output["Azione"] = output["Segnale"]
    columns = [
        "Data", "Open", "High", "Low", "Close", "ETH-USD", "SMA50", "SMA200",
        "RSI", "ATR", "Volume", "VolumeAvg20", "Azione", "Livello_Rischio",
        "Standard_Entry", "Breakout_Raw", "Breakout_Guard_Passed",
        "Breakout_Entry", "Entry_Path", "Position_Open", "Official_Sell",
        "Trail8_Stop_Hit", "Trail8_Confirmed",
    ]
    return save_dataframe_csv(output[columns], out_path, index=False)


def save_chart_data_json(
    df: pd.DataFrame,
    out_path: str | Path,
    metadata: dict,
) -> Path:
    rows = [
        {
            "date": pd.Timestamp(date).strftime("%Y-%m-%d"),
            "open": _json_float(row.get("Open")),
            "high": _json_float(row.get("High")),
            "low": _json_float(row.get("Low")),
            "close": _json_float(row.get("Close")),
            "sma50": _json_float(row.get("SMA50")),
            "sma200": _json_float(row.get("SMA200")),
            "rsi": _json_float(row.get("RSI")),
            "volume": _json_float(row.get("Volume")),
            "volume_avg20": _json_float(row.get("VolumeAvg20")),
            "action": str(row.get("Segnale", HOLD_ACTION)),
            "entry_path": str(row.get("Entry_Path", "")),
        }
        for date, row in df.sort_index().iterrows()
    ]
    return write_utf8_text(
        out_path,
        json.dumps({**metadata, "mode": "DAILY", "rows": rows}, separators=(",", ":")),
    )


def save_live_status_json(
    *,
    action: str,
    price_usd: float,
    price_eur: float | None,
    volume_24h_eth: float,
    buy_statuses: list[bool],
    breakout_statuses: list[bool],
    sell_statuses: list[bool],
    position_open: bool,
    rsi: float | None,
    sma50: float | None,
    sma200: float | None,
    atr: float | None,
    risk_level: str,
    metadata: dict,
    out_path: str | Path,
) -> Path:
    payload = {
        **metadata,
        "mode": "LIVE PREVIEW",
        "action": action,
        "price_usd": float(price_usd),
        "price_eur": _json_float(price_eur),
        "volume_24h_eth": float(volume_24h_eth),
        "status": "Attivo",
        "position_open": bool(position_open),
        "breakout_operational_start": "2026-08-28",
        "rsi": _json_float(rsi),
        "sma50": _json_float(sma50),
        "sma200": _json_float(sma200),
        "atr": _json_float(atr),
        "risk_level": risk_level,
        "condition_groups": _condition_groups(
            buy_statuses, breakout_statuses, sell_statuses, live=True
        ),
    }
    return write_utf8_text(out_path, json.dumps(payload, indent=2))


def save_status_json(
    df: pd.DataFrame,
    *,
    metadata: dict,
    out_path: str | Path,
) -> Path:
    latest = df.iloc[-1]
    previous = df.iloc[-2] if len(df) >= 2 else None
    buy_statuses, breakout_statuses, sell_statuses = live_condition_statuses(df)
    payload = {
        **metadata,
        "mode": "DAILY",
        "candle_date": df.index[-1].strftime("%Y-%m-%d"),
        "action": str(latest["Segnale"]),
        "price_usd": _json_float(latest["Close"]),
        "price_eur": None,
        "status": "Attivo",
        "position_open": bool(latest.get("Position_Open", False)),
        "breakout_operational_start": "2026-08-28",
        "risk_level": str(latest.get("Livello_Rischio", "MEDIO")),
        "rsi": _json_float(latest.get("RSI")),
        "sma50": _json_float(latest.get("SMA50")),
        "sma200": _json_float(latest.get("SMA200")),
        "atr": _json_float(latest.get("ATR")),
        "volume_eth": _json_float(latest.get("Volume")),
        "volume_avg20_eth": _json_float(latest.get("VolumeAvg20")),
        "previous_close": _json_float(previous.get("Close") if previous is not None else None),
        "previous_sma50": _json_float(previous.get("SMA50") if previous is not None else None),
        "condition_groups": _condition_groups(
            buy_statuses, breakout_statuses, sell_statuses, live=False
        ),
    }
    return write_utf8_text(out_path, json.dumps(payload, indent=2))


def save_text_report(
    df: pd.DataFrame,
    metrics_strategy,
    metrics_bh,
    out_path: str | Path,
    *,
    price_eur: float | None = None,
    price_usd: float | None = None,
) -> Path:
    latest = df.iloc[-1]

    def pct(value: float) -> str:
        return "n/a" if pd.isna(value) else f"{value * 100:.2f}%"

    lines = [
        CFG.model_name.upper(),
        f"Candela DAILY: {df.index[-1].strftime('%Y-%m-%d')} UTC",
        f"Fonte: {CFG.data_source} - {CFG.product_id}",
        "",
        f"Azione: {latest['Segnale']}",
        f"Posizione operativa: {'DENTRO' if bool(latest.get('Position_Open', False)) else 'FUORI'}",
        "Secondo ingresso breakout operativo dalle candele chiuse del 2026-08-28",
        f"Rischio informativo: {latest.get('Livello_Rischio', 'MEDIO')}",
        f"Close ETH-USD: {float(latest['Close']):.2f} USD",
        f"Spot ETH-USD: {price_usd:.2f} USD" if price_usd is not None else "Spot ETH-USD: non disponibile",
        f"Spot ETH-EUR: {price_eur:.2f} EUR" if price_eur is not None else "Spot ETH-EUR: non disponibile",
        f"SMA50: {float(latest['SMA50']):.2f}",
        f"SMA200: {float(latest['SMA200']):.2f}",
        f"RSI14: {float(latest['RSI']):.2f}",
        f"ATR14: {float(latest['ATR']):.2f}",
        "",
        f"BACKTEST {df.index[0].strftime('%Y-%m-%d')} - {df.index[-1].strftime('%Y-%m-%d')}",
        "Esecuzione: azione a chiusura t applicata al rendimento t+1",
        f"Commissione: {CFG.transaction_cost_rate * 100:.1f}% per lato inclusa",
        "Spread, slippage, imposte e rendimento della liquidita: non inclusi",
        "",
        CFG.model_name,
        f"- Rendimento totale: {pct(metrics_strategy.total_return)}",
        f"- Rendimento annualizzato: {pct(metrics_strategy.annualized_return)}",
        f"- Drawdown massimo: {pct(metrics_strategy.max_drawdown)}",
        f"- Operazioni completate: {metrics_strategy.num_operations}",
        f"- Operazioni vincenti: {metrics_strategy.win_rate * 100:.1f}%",
        f"- Sharpe Ratio: {metrics_strategy.sharpe_ratio:.3f}",
        f"- Profit factor: {metrics_strategy.profit_factor:.3f}",
        "",
        "Buy & Hold ETH-USD",
        f"- Rendimento totale: {pct(metrics_bh.total_return)}",
        f"- Rendimento annualizzato: {pct(metrics_bh.annualized_return)}",
        f"- Drawdown massimo: {pct(metrics_bh.max_drawdown)}",
        f"- Sharpe Ratio: {metrics_bh.sharpe_ratio:.3f}",
    ]
    return write_utf8_text(out_path, "\n".join(lines))


def plot_price_and_sma_with_signals(df: pd.DataFrame, out_path: str | Path) -> Path:
    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = df.sort_index()
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.plot(frame.index, frame["Close"], linewidth=1.2, label="ETH-USD")
    ax.plot(frame.index, frame["SMA50"], linewidth=1.0, label="SMA50")
    ax.plot(frame.index, frame["SMA200"], linewidth=1.0, label="SMA200")
    buys = frame[frame["Segnale"] == "ACQUISTA"]
    sells = frame[frame["Segnale"] == "VENDI"]
    ax.scatter(buys.index, buys["Close"], color="#15803d", s=18, label="ACQUISTA")
    ax.scatter(sells.index, sells["Close"], color="#dc2626", s=18, label="VENDI")
    ax.set_title("ETH-USD Signal - DAILY Coinbase")
    ax.set_xlabel("Data UTC")
    ax.set_ylabel("USD")
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, alpha=0.15)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
