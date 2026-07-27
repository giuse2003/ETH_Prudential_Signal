from __future__ import annotations

import unittest
from pathlib import Path

from notifications.telegram import extract_authorized_commands, format_monitor_message
from telegram_command import build_live_signal_message


class TelegramCommandTests(unittest.TestCase):
    def test_extracts_only_commands_from_authorized_chat(self) -> None:
        updates = [
            {"update_id": 10, "message": {"chat": {"id": 123}, "text": "/segnale"}},
            {"update_id": 11, "message": {"chat": {"id": 999}, "text": "/segnale"}},
            {"update_id": 12, "message": {"chat": {"id": 123}, "text": "/HELP altro"}},
        ]
        commands, next_offset = extract_authorized_commands(updates, "123")
        self.assertEqual(commands, ["/segnale", "/help"])
        self.assertEqual(next_offset, 13)

    def test_shared_formatter_preserves_requested_layout(self) -> None:
        message = format_monitor_message("MANTIENI STATO ATTUALE", "ALTO", 54169.0)
        self.assertIn("54.169 EUR", message)
        self.assertNotIn("USD\nEUR", message)

    def test_command_uses_published_live_bundle(self) -> None:
        payload = {
            "mode": "LIVE PREVIEW",
            "action": "MANTIENI STATO ATTUALE",
            "price_eur": 2630.0,
            "condition_groups": {
                "buy": [{"passed": False}] * 5,
                "sell": [{"passed": True}, {"passed": False}],
            },
        }
        message = build_live_signal_message(payload)
        self.assertTrue(message.startswith("ETH-USD Signal - LIVE PREVIEW"))
        self.assertIn("Azione: MANTIENI STATO ATTUALE", message)
        self.assertIn("ACQUISTA:\n🟥 1.", message)
        self.assertIn("VENDI:\n🟩 1.", message)

    def test_worker_has_no_daily_fallback_for_signal_command(self) -> None:
        source = (Path(__file__).resolve().parents[1] / "cloudflare-worker" / "src" / "worker.js").read_text(encoding="utf-8")
        self.assertNotIn("buildDailySignalMessage", source)
        self.assertNotIn("ETH MONITOR DAILY!", source)
        self.assertNotIn("computeRsi14", source)
        self.assertNotIn("buildLiveSnapshot", source)


if __name__ == "__main__":
    unittest.main()
