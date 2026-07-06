from __future__ import annotations

import unittest

from hourly_monitor import should_notify
from state.state_store import MonitorState


class HourlyMonitorNotificationTests(unittest.TestCase):
    def test_first_run_saves_baseline_without_notification(self) -> None:
        must_notify, reason = should_notify(
            MonitorState(),
            signal="MANTIENI",
            conditions_key="BUY:00100|SELL:00",
        )

        self.assertFalse(must_notify)
        self.assertEqual(reason, "baseline iniziale salvata senza notifica")

    def test_unchanged_signal_and_conditions_do_not_notify(self) -> None:
        must_notify, reason = should_notify(
            MonitorState(
                last_signal="MANTIENI",
                last_conditions_key="BUY:00100|SELL:00",
            ),
            signal="MANTIENI",
            conditions_key="BUY:00100|SELL:00",
        )

        self.assertFalse(must_notify)
        self.assertEqual(reason, "condizioni operative invariate")

    def test_signal_change_without_condition_change_does_not_notify(self) -> None:
        must_notify, reason = should_notify(
            MonitorState(
                last_signal="ACQUISTA",
                last_conditions_key="BUY:11111|SELL:00",
            ),
            signal="MANTIENI",
            conditions_key="BUY:11111|SELL:00",
        )

        self.assertFalse(must_notify)
        self.assertEqual(reason, "segnale cambiato senza cambio condizioni: ACQUISTA -> MANTIENI")

    def test_condition_change_notifies_even_when_signal_is_unchanged(self) -> None:
        must_notify, reason = should_notify(
            MonitorState(
                last_signal="MANTIENI",
                last_conditions_key="BUY:00100|SELL:00",
            ),
            signal="MANTIENI",
            conditions_key="BUY:00110|SELL:00",
        )

        self.assertTrue(must_notify)
        self.assertEqual(reason, "condizioni operative cambiate")

    def test_signal_change_with_condition_change_notifies(self) -> None:
        must_notify, reason = should_notify(
            MonitorState(
                last_signal="MANTIENI",
                last_conditions_key="BUY:00100|SELL:00",
            ),
            signal="VENDI",
            conditions_key="BUY:00100|SELL:01",
        )

        self.assertTrue(must_notify)
        self.assertEqual(reason, "condizioni operative cambiate")

    def test_user_sequence_notifies_only_when_condition_key_changes(self) -> None:
        state = MonitorState(
            last_signal="MANTIENI",
            last_conditions_key="BUY:00000|SELL:00",
        )

        sequence = [
            ("giorno 1", "ACQUISTA", "BUY:11111|SELL:00", True),
            ("giorno 2", "MANTIENI", "BUY:11111|SELL:00", False),
            ("giorno 3", "MANTIENI", "BUY:11101|SELL:00", True),
            ("giorno 11", "MANTIENI", "BUY:11101|SELL:00", False),
            ("giorno 12", "VENDI", "BUY:00000|SELL:01", True),
            ("giorno 13", "MANTIENI", "BUY:00000|SELL:01", False),
        ]

        for day, signal, conditions_key, expected_notify in sequence:
            with self.subTest(day=day):
                must_notify, _ = should_notify(state, signal=signal, conditions_key=conditions_key)
                self.assertEqual(must_notify, expected_notify)
                if must_notify:
                    state.last_signal = signal
                    state.last_conditions_key = conditions_key


if __name__ == "__main__":
    unittest.main()
