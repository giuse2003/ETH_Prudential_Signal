from __future__ import annotations

import unittest

import pandas as pd

from scripts.run_january_2026_entry_guardrail_research import (
    aggregate_guards,
    primary_guardrail,
    secondary_guardrail,
)


class JanuaryEntryGuardrailTests(unittest.TestCase):
    @staticmethod
    def _regimes() -> pd.DataFrame:
        return pd.DataFrame(
            {
                "SMA200Slope20": [0.012392, 0.015686, -0.056314],
                "SMA50VsSMA200": [-0.164960, -0.161670, -0.082249],
                "Return90": [-0.272063, -0.166557, -0.093893],
            },
            index=pd.to_datetime(
                ["2026-01-06", "2026-01-13", "2026-08-17"]
            ),
        )

    def test_primary_blocks_both_january_regimes_and_allows_august(self) -> None:
        allowed = primary_guardrail().allowed(self._regimes())

        self.assertFalse(bool(allowed.loc["2026-01-06"]))
        self.assertFalse(bool(allowed.loc["2026-01-13"]))
        self.assertTrue(bool(allowed.loc["2026-08-17"]))

    def test_secondary_requires_at_least_two_risk_flags(self) -> None:
        regimes = self._regimes()
        regimes.loc[pd.Timestamp("2026-08-17"), "SMA200Slope20"] = 0.01
        allowed = secondary_guardrail().allowed(regimes)

        self.assertFalse(bool(allowed.loc["2026-01-06"]))
        self.assertFalse(bool(allowed.loc["2026-01-13"]))
        self.assertTrue(bool(allowed.loc["2026-08-17"]))

    def test_empty_missed_episode_from_csv_is_not_counted(self) -> None:
        rows = []
        for base_variant in ("current_rsi40_65_mom7_high5", "rsi40_mom7_high5"):
            for guardrail, january_entries in (("none", 1), ("candidate", 0)):
                rows.append(
                    {
                        "base_variant": base_variant,
                        "guardrail": guardrail,
                        "guardrail_label": guardrail,
                        "family": "none" if guardrail == "none" else "slope_gap",
                        "pre_jan_annualized_return": 1.0,
                        "pre_jan_sharpe_ratio": 1.0,
                        "january_entries": january_entries,
                        "captures_august": True,
                        "missed_profitable_episodes": float("nan"),
                        "full_annualized_return": 1.0,
                        "full_max_drawdown": -0.2,
                        "full_sharpe_ratio": 1.0,
                    }
                )

        aggregate = aggregate_guards(pd.DataFrame(rows)).set_index("guardrail")

        self.assertEqual(
            int(aggregate.loc["candidate", "max_missed_profitable_episodes"]), 0
        )
        self.assertTrue(bool(aggregate.loc["candidate", "eligible"]))


if __name__ == "__main__":
    unittest.main()
