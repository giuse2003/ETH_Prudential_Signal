from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from data.fetch_yahoo import fetch_eth_daily_csv, join_usd_with_eur_from_first_common_date


class FetchYahooTests(unittest.TestCase):
    def test_required_symbol_uses_existing_csv_when_download_returns_no_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "ETH-USD_daily.csv"
            csv_path.write_text("Date,Close\n2026-06-21,100\n", encoding="utf-8")

            with (
                patch("data.fetch_yahoo._default_output_path", return_value=csv_path),
                patch("data.fetch_yahoo.yf.download", return_value=pd.DataFrame()),
            ):
                result = fetch_eth_daily_csv(
                    symbol="ETH-USD",
                    force_download=True,
                    is_optional=False,
                )

        self.assertEqual(result, csv_path)

    def test_required_symbol_raises_when_download_fails_without_existing_csv(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "ETH-USD_daily.csv"

            with (
                patch("data.fetch_yahoo._default_output_path", return_value=csv_path),
                patch("data.fetch_yahoo.yf.download", return_value=pd.DataFrame()),
            ):
                with self.assertRaises(RuntimeError):
                    fetch_eth_daily_csv(
                        symbol="ETH-USD",
                        force_download=True,
                        is_optional=False,
                    )

    def test_join_usd_with_eur_starts_from_first_common_eur_quote(self) -> None:
        index_usd = pd.to_datetime(["2015-07-30", "2017-11-09", "2017-11-10"])
        index_eur = pd.to_datetime(["2017-11-09", "2017-11-10"])
        df_usd = pd.DataFrame(
            {
                "Open": [1.0, 2.0, 3.0],
                "High": [1.0, 2.0, 3.0],
                "Low": [1.0, 2.0, 3.0],
                "Close": [1.0, 2.0, 3.0],
                "Volume": [10.0, 20.0, 30.0],
            },
            index=index_usd,
        )
        df_eur = pd.DataFrame({"Close": [1.8, 2.7]}, index=index_eur)

        result = join_usd_with_eur_from_first_common_date(df_usd, df_eur)

        self.assertEqual(result.index[0], pd.Timestamp("2017-11-09"))
        self.assertEqual(result["Close"].tolist(), [2.0, 3.0])
        self.assertEqual(result["Close_EUR"].tolist(), [1.8, 2.7])


if __name__ == "__main__":
    unittest.main()
