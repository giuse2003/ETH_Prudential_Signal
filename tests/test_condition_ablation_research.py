from __future__ import annotations

import math
import unittest

import pandas as pd

from scripts.run_condition_ablation_research import (
    CONSERVATIVE_PARETO_VARIANT,
    FEE_SCENARIOS,
    FOCUS_COALITIONS,
    MAX_FEE_RATE,
    _completed_net_trade_returns,
    baseline_variant,
    build_event_audit,
    build_signal_frame,
    build_variants,
    load_frozen_indicators,
    shapley_attribution,
)


class ConditionAblationResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.indicators, _ = load_frozen_indicators(verify=False)

    def test_experimental_baseline_matches_frozen_legacy_signals(self) -> None:
        experimental = build_signal_frame(self.indicators, baseline_variant())
        self.assertTrue(experimental["Segnale"].equals(self.indicators["Segnale"]))

    def test_fee_scenarios_never_exceed_declared_maximum(self) -> None:
        self.assertEqual(MAX_FEE_RATE, 0.006)
        self.assertEqual(max(FEE_SCENARIOS.values()), MAX_FEE_RATE)

    def test_variant_names_are_unique(self) -> None:
        names = [variant.name for variant in build_variants()]
        self.assertEqual(len(names), len(set(names)))

    def test_local_grid_contains_all_focus_coalitions(self) -> None:
        names = {variant.name for variant in build_variants()}
        self.assertTrue(set(FOCUS_COALITIONS.values()).issubset(names))
        self.assertIn(CONSERVATIVE_PARETO_VARIANT, names)

    def test_early_momentum_plateau_has_identical_historical_signals(self) -> None:
        by_name = {variant.name: variant for variant in build_variants()}
        signals_8 = build_signal_frame(
            self.indicators, by_name["entry_early_momentum_max_8"]
        )["Segnale"]
        signals_10 = build_signal_frame(
            self.indicators, by_name["entry_early_momentum_max_10"]
        )["Segnale"]
        self.assertTrue(signals_8.equals(signals_10))

    def test_conservative_trail_plateau_extends_to_twenty_percent(self) -> None:
        by_name = {variant.name: variant for variant in build_variants()}
        signals_15 = build_signal_frame(
            self.indicators, by_name["combo_three_early_8_trail_15_sma_2_0"]
        )["Segnale"]
        signals_20 = build_signal_frame(
            self.indicators, by_name["combo_three_early_8_trail_20_sma_2_0"]
        )["Segnale"]
        self.assertTrue(signals_15.equals(signals_20))

    def test_net_trade_return_includes_entry_and_exit_costs(self) -> None:
        equity = pd.DataFrame(
            {
                "EffectiveExposure": [0.0, 1.0, 0.0],
                "DailyReturnStrategy": [0.0, -0.006, -0.006],
            }
        )
        returns = _completed_net_trade_returns(equity)
        self.assertEqual(len(returns), 1)
        self.assertAlmostEqual(returns[0], (1.0 - 0.006) ** 2 - 1.0)

    def test_shapley_contributions_reconcile_to_full_delta(self) -> None:
        rows = []
        for coalition, variant in FOCUS_COALITIONS.items():
            size = len(coalition)
            rows.append(
                {
                    "variant": variant,
                    "fee_0_60_annualized_return": 0.5 + size * 0.1,
                    "fee_0_60_max_drawdown": -0.5 + size * 0.02,
                    "fee_0_60_sharpe_ratio": 1.0 + size * 0.05,
                    "fee_0_60_total_return": math.exp(size * 0.2) - 1.0,
                }
            )
        attribution = shapley_attribution(pd.DataFrame(rows))
        self.assertAlmostEqual(attribution["annualized_return"].sum(), 0.3)
        self.assertAlmostEqual(attribution["max_drawdown"].sum(), 0.06)
        self.assertAlmostEqual(attribution["sharpe_ratio"].sum(), 0.15)
        self.assertAlmostEqual(attribution["log_terminal_wealth"].sum(), 0.6)

    def test_event_audit_isolates_both_focus_effects(self) -> None:
        events = build_event_audit(self.indicators, build_variants())
        self.assertEqual(
            set(events["event_type"]), {"extra_early_entry", "new_trail_exit"}
        )
        self.assertGreater((events["event_type"] == "extra_early_entry").sum(), 0)
        self.assertGreater((events["event_type"] == "new_trail_exit").sum(), 0)


if __name__ == "__main__":
    unittest.main()
