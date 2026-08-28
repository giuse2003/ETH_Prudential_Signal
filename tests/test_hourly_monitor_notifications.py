from __future__ import annotations

import unittest
from datetime import datetime, timezone
from pathlib import Path

from hourly_monitor import should_force_daily_download, should_send_live_alert
from state.state_store import MonitorState


class HourlyMonitorNotificationTests(unittest.TestCase):
    def test_incremental_run_uses_coinbase_cache(self) -> None:
        self.assertFalse(
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
        self.assertIn("title=\"ETH-USD Signal - LIVE PREVIEW\"", source)
        self.assertIn("include_dashboard_link=True", source)
        self.assertNotIn("DAILY!", source)

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

    def test_condition_schema_migration_saves_baseline_without_notification(self) -> None:
        state = MonitorState(
            last_live_conditions_key="BUY:10001|SELL:00",
            live_pending_conditions_key="BUY:10001|SELL:00",
            live_pending_since_utc="2026-08-28T09:00:00+00:00",
        )
        current_key = "BUY_STANDARD:10001|BUY_BREAKOUT:11100001|SELL:00"

        must_notify, reason = should_send_live_alert(
            state,
            current_key,
            datetime(2026, 8, 28, 10, 0, tzinfo=timezone.utc),
        )

        self.assertFalse(must_notify)
        self.assertIn("schema condizioni LIVE aggiornato", reason)
        self.assertEqual(state.last_live_conditions_key, current_key)
        self.assertIsNone(state.live_pending_conditions_key)
        self.assertIsNone(state.live_pending_since_utc)


if __name__ == "__main__":
    unittest.main()
