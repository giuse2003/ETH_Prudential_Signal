from __future__ import annotations

import unittest

import pandas as pd

from strategy.signals import (
    BREAKOUT_OPERATIONAL_START,
    SMA50_BREAK_PCT,
    TRAILING_MOMENTUM_MIN,
    build_live_signal_frame,
    compute_signals,
    live_condition_statuses,
)


class SignalRulesTests(unittest.TestCase):
    def test_buy_requires_rsi_not_above_65(self) -> None:
        df = pd.DataFrame(
            {
                "Close": [120.0],
                "SMA50": [110.0],
                "SMA200": [100.0],
                "RSI": [72.0],
                "Volume": [2000.0],
                "VolumeAvg20": [1000.0],
                "Close_7d_ago": [115.0],
            }
        )

        result = compute_signals(df)

        self.assertEqual(result.iloc[-1]["Segnale"], "MANTIENI STATO ATTUALE")
        self.assertFalse(result.iloc[-1]["Entry_RSI_Filter_Passed"])

    def test_buy_allows_rsi_equal_to_65(self) -> None:
        df = pd.DataFrame(
            {
                "Close": [120.0],
                "SMA50": [110.0],
                "SMA200": [100.0],
                "RSI": [65.0],
                "Volume": [2000.0],
                "VolumeAvg20": [1000.0],
                "Close_7d_ago": [115.0],
            }
        )

        result = compute_signals(df)

        self.assertEqual(result.iloc[-1]["Segnale"], "ACQUISTA")
        self.assertTrue(result.iloc[-1]["Entry_RSI_Filter_Passed"])

    def test_price_more_than_two_percent_below_sma50_triggers_sell(self) -> None:
        df = pd.DataFrame(
            {
                "Close": [120.0, 119.0],
                "SMA50": [130.0, 128.0],
                "SMA200": [100.0, 100.0],
                "RSI": [55.0, 56.0],
                "Volume": [800.0, 850.0],
                "VolumeAvg20": [1000.0, 1000.0],
                "Close_7d_ago": [110.0, 111.0],
            }
        )

        result = compute_signals(df)

        self.assertEqual(result.iloc[-1]["Segnale"], "VENDI")

    def test_price_inside_two_percent_sma50_margin_does_not_sell(self) -> None:
        df = pd.DataFrame(
            {
                "Close": [99.0],
                "SMA50": [100.0],
                "SMA200": [80.0],
                "RSI": [35.0],
                "Volume": [800.0],
                "VolumeAvg20": [1000.0],
                "Close_7d_ago": [100.0],
            }
        )

        result = compute_signals(df)

        self.assertEqual(SMA50_BREAK_PCT, 0.02)
        self.assertEqual(result.iloc[-1]["Segnale"], "MANTIENI STATO ATTUALE")
        self.assertFalse(result.iloc[-1]["Official_Sell"])

    def test_trailing_stop_confirmed_triggers_sell_signal(self) -> None:
        df = pd.DataFrame(
            {
                "Close": [100.0, 110.0, 120.0, 109.0],
                "SMA50": [90.0, 95.0, 100.0, 105.0],
                "SMA200": [80.0, 80.0, 80.0, 80.0],
                "RSI": [55.0, 55.0, 55.0, 55.0],
                "Volume": [2000.0, 900.0, 900.0, 1500.0],
                "VolumeAvg20": [1000.0, 1000.0, 1000.0, 1000.0],
                "Close_7d_ago": [95.0, 100.0, 110.0, 110.0],
            },
            index=pd.date_range("2026-01-01", periods=4, freq="D"),
        )

        result = compute_signals(df)

        self.assertEqual(result.iloc[-1]["Segnale"], "VENDI")
        self.assertTrue(result.iloc[-1]["Trail8_Stop_Hit"])
        self.assertTrue(result.iloc[-1]["Trail8_Confirmed"])

    def test_trailing_accepts_ten_percent_negative_momentum(self) -> None:
        df = pd.DataFrame(
            {
                "Close": [100.0, 120.0, 108.0],
                "SMA50": [90.0, 95.0, 100.0],
                "SMA200": [80.0, 80.0, 80.0],
                "RSI": [55.0, 55.0, 55.0],
                "Volume": [2000.0, 900.0, 1500.0],
                "VolumeAvg20": [1000.0, 1000.0, 1000.0],
                "Close_7d_ago": [95.0, 110.0, 120.0],
            },
            index=pd.date_range("2026-01-01", periods=3, freq="D"),
        )

        result = compute_signals(df)

        self.assertEqual(TRAILING_MOMENTUM_MIN, -0.15)
        self.assertEqual(result.iloc[-1]["Segnale"], "VENDI")
        self.assertTrue(result.iloc[-1]["Trail8_Confirmed"])

    def test_trailing_rejects_momentum_below_minus_fifteen_percent(self) -> None:
        df = pd.DataFrame(
            {
                "Close": [100.0, 120.0, 100.8],
                "SMA50": [90.0, 95.0, 100.0],
                "SMA200": [80.0, 80.0, 80.0],
                "RSI": [55.0, 55.0, 55.0],
                "Volume": [2000.0, 900.0, 1500.0],
                "VolumeAvg20": [1000.0, 1000.0, 1000.0],
                "Close_7d_ago": [95.0, 110.0, 120.0],
            },
            index=pd.date_range("2026-01-01", periods=3, freq="D"),
        )

        result = compute_signals(df)

        self.assertTrue(result.iloc[-1]["Trail8_Stop_Hit"])
        self.assertFalse(result.iloc[-1]["Trail8_Confirmed"])
        self.assertEqual(result.iloc[-1]["Segnale"], "MANTIENI STATO ATTUALE")

    def test_rsi_filter_applies_only_to_new_entries_not_existing_position_holds(self) -> None:
        df = pd.DataFrame(
            {
                "Close": [100.0, 120.0, 109.0],
                "SMA50": [90.0, 95.0, 100.0],
                "SMA200": [80.0, 80.0, 80.0],
                "RSI": [55.0, 60.0, 67.0],
                "Volume": [2000.0, 900.0, 1500.0],
                "VolumeAvg20": [1000.0, 1000.0, 1000.0],
                "Close_7d_ago": [95.0, 110.0, 100.0],
            },
            index=pd.date_range("2026-01-01", periods=3, freq="D"),
        )

        result = compute_signals(df)

        self.assertEqual(result.iloc[0]["Segnale"], "ACQUISTA")
        self.assertEqual(result.iloc[-1]["Segnale"], "MANTIENI STATO ATTUALE")
        self.assertFalse(result.iloc[-1]["Entry_RSI_Filter_Passed"])
        self.assertFalse(result.iloc[-1]["Trail8_Confirmed"])

    def test_live_signal_recomputes_indicators_with_live_price_and_volume(self) -> None:
        dates = pd.date_range("2026-01-01", periods=210, freq="D")
        df = pd.DataFrame(
            {
                "Open": [100.0] * 210,
                "High": [101.0] * 210,
                "Low": [99.0] * 210,
                "Close": [100.0] * 210,
                "Volume": [1000.0] * 210,
            },
            index=dates,
        )

        result = build_live_signal_frame(
            df,
            live_price_usd=150.0,
            live_volume_24h=2500.0,
            live_time_utc=pd.Timestamp("2026-08-01 12:00:00", tz="UTC"),
        )
        buy_statuses, breakout_statuses, sell_statuses = live_condition_statuses(result)

        self.assertEqual(result.index[-1], pd.Timestamp("2026-08-01"))
        self.assertEqual(result.iloc[-1]["Close"], 150.0)
        self.assertEqual(result.iloc[-1]["Volume"], 2500.0)
        self.assertEqual(result.iloc[-1]["VolumeAvg20"], 1000.0)
        self.assertTrue(buy_statuses[0])
        self.assertFalse(buy_statuses[2])
        self.assertTrue(buy_statuses[3])
        self.assertTrue(buy_statuses[4])
        self.assertEqual(len(breakout_statuses), 8)
        self.assertFalse(sell_statuses[0])
        self.assertFalse(sell_statuses[1])

    def test_published_contract_has_two_buy_paths_and_two_sell_conditions(self) -> None:
        df = pd.DataFrame(
            {
                "Close": [120.0],
                "SMA50": [110.0],
                "SMA200": [100.0],
                "RSI": [55.0],
                "Volume": [2000.0],
                "VolumeAvg20": [1000.0],
                "Close_7d_ago": [115.0],
                "Trail8_Confirmed": [False],
            }
        )
        buy, breakout, sell = live_condition_statuses(df)
        self.assertEqual(len(buy), 5)
        self.assertEqual(len(breakout), 8)
        self.assertEqual(len(sell), 2)

    def test_protected_breakout_opens_before_sma50_cross(self) -> None:
        dates = pd.date_range("2026-07-19", periods=30, freq="D")
        frame = pd.DataFrame(
            {
                "Close": [90.0] * 29 + [99.0],
                "SMA50": [90.0 + index * 0.1 for index in range(30)],
                "SMA200": [100.0] * 30,
                "RSI": [55.0] * 30,
                "Volume": [1000.0] * 29 + [1300.0],
                "VolumeAvg20": [1000.0] * 30,
                "Close_7d_ago": [90.0] * 30,
            },
            index=dates,
        )

        result = compute_signals(frame)

        self.assertEqual(result.iloc[-1]["Segnale"], "ACQUISTA")
        self.assertEqual(result.iloc[-1]["Entry_Path"], "breakout_protected")
        self.assertTrue(result.iloc[-1]["Breakout_Entry"])
        self.assertTrue(result.iloc[-1]["Position_Open"])

    def test_breakout_guard_blocks_deep_gap_with_rising_sma200(self) -> None:
        dates = pd.date_range("2025-12-15", periods=30, freq="D")
        frame = pd.DataFrame(
            {
                "Close": [90.0] * 29 + [95.0],
                "SMA50": [80.0 + index * 0.1 for index in range(30)],
                "SMA200": [90.0 + index * (10.0 / 29.0) for index in range(30)],
                "RSI": [55.0] * 30,
                "Volume": [1000.0] * 29 + [1300.0],
                "VolumeAvg20": [1000.0] * 30,
                "Close_7d_ago": [90.0] * 30,
            },
            index=dates,
        )

        result = compute_signals(frame)

        self.assertTrue(result.iloc[-1]["Breakout_Raw"])
        self.assertFalse(result.iloc[-1]["Breakout_Guard_Passed"])
        self.assertFalse(result.iloc[-1]["Breakout_Entry"])
        self.assertEqual(result.iloc[-1]["Segnale"], "MANTIENI STATO ATTUALE")

    def test_operational_activation_does_not_backfill_a_previous_breakout(self) -> None:
        dates = pd.date_range("2026-07-30", periods=30, freq="D")
        frame = pd.DataFrame(
            {
                "Close": [90.0] * 18 + [99.0] + [99.0] * 11,
                "SMA50": [90.0 + index * 0.1 for index in range(30)],
                "SMA200": [100.0] * 30,
                "RSI": [55.0] * 30,
                "Volume": [1000.0] * 18 + [1300.0] + [1000.0] * 11,
                "VolumeAvg20": [1000.0] * 30,
                "Close_7d_ago": [90.0] * 30,
            },
            index=dates,
        )

        historical = compute_signals(frame)
        operational = compute_signals(
            frame,
            breakout_active_from=BREAKOUT_OPERATIONAL_START,
            state_reset_date=BREAKOUT_OPERATIONAL_START,
        )

        self.assertEqual(historical.loc["2026-08-17", "Segnale"], "ACQUISTA")
        self.assertFalse(operational.loc["2026-08-17", "Breakout_Enabled"])
        self.assertFalse(operational.iloc[-1]["Position_Open"])


if __name__ == "__main__":
    unittest.main()
