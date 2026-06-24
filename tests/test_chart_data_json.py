from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from backtest.backtest import BacktestMetrics
from reports.generate import save_backtest_json, save_chart_data_json, save_live_status_json


class ChartDataJsonTests(unittest.TestCase):
    def test_saves_compact_chart_rows(self) -> None:
        df = pd.DataFrame(
            {
                "Close": [100.0],
                "SMA50": [90.0],
                "SMA200": [80.0],
                "RSI": [45.0],
                "Volume": [1000.0],
                "VolumeAvg20": [900.0],
                "Segnale": ["MANTIENI"],
            },
            index=pd.to_datetime(["2026-06-21"]),
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "chart-data.json"
            save_chart_data_json(df, path)
            payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(
            payload,
            [
                {
                    "date": "2026-06-21",
                    "close": 100.0,
                    "sma50": 90.0,
                    "sma200": 80.0,
                    "rsi": 45.0,
                    "volume": 1000.0,
                    "volume_avg20": 900.0,
                    "signal": "MANTIENI",
                }
            ],
        )

    def test_saves_live_status_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "live-status.json"
            save_live_status_json(
                signal="VENDI",
                price_usd=64000.0,
                price_eur=56000.0,
                volume_24h_usd=27000000000.0,
                buy_statuses=[False, False, True, False, False],
                sell_statuses=[True],
                out_path=path,
            )
            payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(payload["signal"], "VENDI")
        self.assertEqual(payload["price_eur"], 56000.0)
        self.assertTrue(payload["condition_groups"]["buy"][2]["passed"])
        self.assertTrue(payload["condition_groups"]["sell"][0]["passed"])

    def test_saves_backtest_json(self) -> None:
        metrics_strategy = BacktestMetrics(
            total_return=9.8086,
            annualized_return=0.318,
            max_drawdown=-0.5257,
            num_operations=28,
            win_rate=0.393,
            sharpe_ratio=0.849,
        )
        metrics_bh = BacktestMetrics(
            total_return=4.3805,
            annualized_return=0.2155,
            max_drawdown=-0.9396,
            num_operations=0,
            win_rate=0.0,
            sharpe_ratio=0.659,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "backtest.json"
            save_backtest_json(
                metrics_strategy=metrics_strategy,
                metrics_bh=metrics_bh,
                out_path=path,
                start_date=pd.Timestamp("2017-11-09"),
                end_date=pd.Timestamp("2026-06-23"),
            )
            payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(payload["period"]["start_date"], "2017-11-09")
        self.assertEqual(payload["period"]["end_date"], "2026-06-23")
        self.assertEqual(payload["strategy"]["total_return"], 9.8086)
        self.assertEqual(payload["strategy"]["num_operations"], 28)
        self.assertEqual(payload["buy_hold"]["max_drawdown"], -0.9396)


if __name__ == "__main__":
    unittest.main()
