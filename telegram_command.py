"""Risponde ai comandi Telegram usando il pacchetto LIVE pubblicato."""

from __future__ import annotations

import json
import os
from pathlib import Path

from notifications.telegram import (
    TelegramConfig,
    extract_authorized_commands,
    format_condition_message,
    get_telegram_updates,
    send_telegram_message,
)

CONDITIONS_HELP_MESSAGE = "\n".join(
    [
        "CONDIZIONI ETH MONITOR",
        "",
        "ACQUISTA si attiva quando e' completo almeno uno dei due percorsi.",
        "",
        "PERCORSO 1 - TREND CONFERMATO:",
        "1. prezzo sopra SMA200;",
        "2. SMA50 sopra SMA200;",
        "3. valore RSI compreso tra 40 e 65;",
        "4. prezzo sopra quello di 7 giorni prima;",
        "5. volume sopra media 20 giorni.",
        "",
        "PERCORSO 2 - BREAKOUT PROTETTO:",
        "1. SMA50 sotto o uguale a SMA200;",
        "2. prezzo sopra SMA50 e almeno al 90% di SMA200;",
        "3. SMA50 non in calo rispetto a 5 giorni prima;",
        "4. valore RSI compreso tra 40 e 65;",
        "5. prezzo sopra quello di 7 giorni prima;",
        "6. volume almeno 20% sopra la media 20 giorni;",
        "7. Close sopra tutti i 5 Close precedenti;",
        "8. guardrail superato: il breakout viene bloccato solo se SMA200 sale da 20 giorni e SMA50 e' oltre il 15% sotto SMA200.",
        "",
        "Per VENDI deve essere vera almeno una di queste condizioni:",
        "1. prezzo oltre il 2% sotto SMA50 (Close &lt; SMA50 x 0,98);",
        "2. trailing stop 8% dal massimo post-ingresso, confermato da:",
        "   - momentum 7 giorni uguale o maggiore di -15%;",
        "   - volume almeno 20% sopra la media 20 giorni.",
    ]
)


def load_published_live_status(project_root: Path) -> dict:
    for path in (
        project_root / "docs" / "live-status.json",
        project_root / "reports" / "live-status.json",
    ):
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict) and payload.get("mode") == "LIVE PREVIEW":
                return payload
    raise FileNotFoundError("Nessun live-status.json pubblicato disponibile.")


def build_live_signal_message(payload: dict) -> str:
    groups = payload.get("condition_groups", {})
    buy_statuses = [bool(item.get("passed")) for item in groups.get("buy", [])]
    breakout_statuses = [
        bool(item.get("passed")) for item in groups.get("buy_breakout", [])
    ]
    sell_statuses = [bool(item.get("passed")) for item in groups.get("sell", [])]
    if len(buy_statuses) != 5 or len(breakout_statuses) != 8 or len(sell_statuses) != 2:
        raise ValueError("Il pacchetto LIVE non contiene le condizioni ETH ufficiali.")
    return format_condition_message(
        signal=str(payload["action"]),
        price_eur=payload.get("price_eur"),
        buy_statuses=buy_statuses,
        breakout_statuses=breakout_statuses,
        sell_statuses=sell_statuses,
        position_open=bool(payload.get("position_open", False)),
        title="ETH-USD Signal - LIVE PREVIEW",
    )


def main() -> None:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not bot_token or not chat_id:
        raise RuntimeError("Mancano TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID.")
    cfg = TelegramConfig(bot_token=bot_token, chat_id=chat_id)
    updates = get_telegram_updates(cfg)
    commands, next_offset = extract_authorized_commands(updates, chat_id)
    if not updates:
        print("Nessun aggiornamento Telegram in attesa.")
        return
    response_sent = False
    project_root = Path(__file__).resolve().parent
    for command in commands:
        if command == "/segnale":
            try:
                message = build_live_signal_message(load_published_live_status(project_root))
            except Exception:
                message = "Segnale ETH LIVE temporaneamente non disponibile. Riprova tra poco."
        elif command == "/conditions":
            message = CONDITIONS_HELP_MESSAGE
        elif command in {"/start", "/help"}:
            message = (
                "Comandi disponibili:\n"
                "/segnale - mostra il segnale ETH corrente\n"
                "/conditions - mostra le condizioni di acquisto e vendita"
            )
        else:
            message = "Comando non riconosciuto.\nUsa /segnale o /conditions"
        send_telegram_message(cfg, message)
        response_sent = True
    if next_offset is not None:
        get_telegram_updates(cfg, offset=next_offset)
    print(
        "Risposta al comando Telegram inviata con successo."
        if response_sent
        else "Nessun comando proveniente dalla chat autorizzata."
    )


if __name__ == "__main__":
    main()
