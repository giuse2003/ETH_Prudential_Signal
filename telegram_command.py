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
    sell_statuses = [bool(item.get("passed")) for item in groups.get("sell", [])]
    if len(buy_statuses) != 5 or len(sell_statuses) != 2:
        raise ValueError("Il pacchetto LIVE non contiene le sette condizioni ETH ufficiali.")
    return format_condition_message(
        signal=str(payload["action"]),
        price_eur=payload.get("price_eur"),
        buy_statuses=buy_statuses,
        sell_statuses=sell_statuses,
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
        elif command in {"/start", "/help"}:
            message = "Comando disponibile:\n/segnale - mostra il segnale ETH corrente"
        else:
            message = "Comando non riconosciuto.\nUsa /segnale"
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
