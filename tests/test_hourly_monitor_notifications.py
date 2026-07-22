from __future__ import annotations

import unittest
from pathlib import Path

from hourly_monitor import should_force_daily_download
from state.state_store import MonitorState


class HourlyMonitorNotificationTests(unittest.TestCase):
    def test_forces_daily_download_until_expected_candle_is_processed(self) -> None:
        self.assertTrue(
            should_force_daily_download(
                MonitorState(last_processed_candle_date="2026-07-03"),
                expected_closed_candle_date="2026-07-04",
            )
        )

    def test_uses_cache_after_expected_candle_is_processed(self) -> None:
        self.assertFalse(
            should_force_daily_download(
                MonitorState(last_processed_candle_date="2026-07-04"),
                expected_closed_candle_date="2026-07-04",
            )
        )

    def test_manual_run_forces_download_even_after_processing(self) -> None:
        self.assertTrue(
            should_force_daily_download(
                MonitorState(last_processed_candle_date="2026-07-04"),
                expected_closed_candle_date="2026-07-04",
                is_manual_run=True,
            )
        )

    def test_monitor_has_no_daily_telegram_send_path(self) -> None:
        source = (
            Path(__file__)
            .resolve()
            .parents[1]
            .joinpath("hourly_monitor.py")
            .read_text(encoding="utf-8")
        )

        self.assertNotIn("should_notify", source)
        self.assertNotIn("ETH MONITOR DAILY!", source)
        self.assertEqual(source.count("send_telegram_message(cfg, live_msg)"), 1)

    def test_local_analysis_does_not_send_telegram_messages(self) -> None:
        source = (
            Path(__file__)
            .resolve()
            .parents[1]
            .joinpath("main.py")
            .read_text(encoding="utf-8")
        )

        self.assertNotIn("send_telegram_message", source)
        self.assertNotIn("TELEGRAM_BOT_TOKEN", source)


if __name__ == "__main__":
    unittest.main()
