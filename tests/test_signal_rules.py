from __future__ import annotations

import unittest

import pandas as pd

from strategy.signals import build_live_signal_frame, compute_signals, live_condition_statuses


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

        self.assertEqual(result.iloc[-1]["Segnale"], "MANTIENI")
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

    def test_price_below_sma50_triggers_sell_signal(self) -> None:
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

    def test_single_close_below_sma50_triggers_sell_signal(self) -> None:
        df = pd.DataFrame(
            {
                "Close": [132.0, 119.0],
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
        self.assertEqual(result.iloc[-1]["Segnale"], "MANTIENI")
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
        buy_statuses, sell_statuses = live_condition_statuses(result)

        self.assertEqual(result.index[-1], pd.Timestamp("2026-08-01"))
        self.assertEqual(result.iloc[-1]["Close"], 150.0)
        self.assertEqual(result.iloc[-1]["Volume"], 2500.0)
        self.assertEqual(result.iloc[-1]["VolumeAvg20"], 1000.0)
        self.assertTrue(buy_statuses[0])
        self.assertTrue(buy_statuses[2])
        self.assertTrue(buy_statuses[4])
        self.assertTrue(buy_statuses[5])
        self.assertFalse(sell_statuses[0])
        self.assertFalse(sell_statuses[1])


if __name__ == "__main__":
    unittest.main()
