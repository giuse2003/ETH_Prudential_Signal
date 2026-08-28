from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from reports.generate import save_chart_data_json, save_live_status_json


class ChartDataJsonTests(unittest.TestCase):
    def test_saves_compact_chart_rows_with_run_metadata(self) -> None:
        frame = pd.DataFrame(
            {
                "Open": [95.0], "High": [105.0], "Low": [92.0], "Close": [100.0],
                "SMA50": [90.0], "SMA200": [80.0], "RSI": [45.0],
                "Volume": [1000.0], "VolumeAvg20": [900.0],
                "Segnale": ["MANTIENI STATO ATTUALE"],
            },
            index=pd.to_datetime(["2026-06-21"]),
        )
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "chart-data.json"
            save_chart_data_json(frame, path, {"run_id": "run-1"})
            payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["run_id"], "run-1")
        self.assertEqual(payload["mode"], "DAILY")
        self.assertEqual(payload["rows"][0]["action"], "MANTIENI STATO ATTUALE")

    def test_saves_live_status_with_both_buy_paths_and_sell_conditions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "live-status.json"
            save_live_status_json(
                action="VENDI",
                price_usd=3000.0,
                price_eur=2600.0,
                volume_24h_eth=10000.0,
                buy_statuses=[False, False, True, False, False],
                breakout_statuses=[False] * 8,
                sell_statuses=[True, False],
                position_open=False,
                rsi=45.0,
                sma50=2900.0,
                sma200=2500.0,
                atr=100.0,
                risk_level="MEDIO",
                metadata={"run_id": "run-1"},
                out_path=path,
            )
            payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["run_id"], "run-1")
        self.assertEqual(payload["action"], "VENDI")
        self.assertEqual(len(payload["condition_groups"]["buy"]), 5)
        self.assertEqual(len(payload["condition_groups"]["buy_breakout"]), 8)
        self.assertEqual(len(payload["condition_groups"]["sell"]), 2)
        self.assertFalse(payload["position_open"])


if __name__ == "__main__":
    unittest.main()
