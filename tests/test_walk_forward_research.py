from __future__ import annotations

import math
import unittest

import numpy as np
import pandas as pd

from scripts.run_walk_forward_research import (
    _comparison_status,
    _sharpe_from_moments,
    build_stitched_stream,
    cscv_pbo,
    expected_max_sharpe,
    probabilistic_sharpe,
    select_training_candidate,
)


class WalkForwardResearchTests(unittest.TestCase):
    def test_comparison_status_distinguishes_neutral_and_mixed(self) -> None:
        neutral = pd.Series(
            {
                "model": "candidate",
                "delta_total_return_vs_baseline": 0.0,
                "delta_max_drawdown_vs_baseline": 0.0,
                "delta_sharpe_vs_baseline": float("nan"),
                "all3_vs_baseline": False,
            }
        )
        mixed = neutral.copy()
        mixed["delta_total_return_vs_baseline"] = 0.1
        mixed["delta_max_drawdown_vs_baseline"] = -0.05
        self.assertEqual(_comparison_status(neutral), "INVARIATO")
        self.assertEqual(_comparison_status(mixed), "MISTO")

    def test_moment_sharpe_matches_direct_calculation(self) -> None:
        values = np.asarray(
            [
                [0.01, 0.02],
                [-0.02, 0.01],
                [0.03, -0.01],
                [0.00, 0.02],
            ]
        )
        actual = _sharpe_from_moments(
            values.sum(axis=0),
            np.square(values).sum(axis=0),
            len(values),
        )
        expected = math.sqrt(365.0) * values.mean(axis=0) / values.std(
            axis=0, ddof=1
        )
        np.testing.assert_allclose(actual, expected)

    def test_selector_rejects_candidate_with_worse_drawdown(self) -> None:
        metrics = pd.DataFrame(
            {
                "annualized_return": [0.50, 0.90, 0.70],
                "max_drawdown": [-0.40, -0.60, -0.30],
                "sharpe_ratio": [1.0, 1.8, 1.4],
                "completed_trades": [10, 10, 8],
                "turnover": [20.0, 22.0, 18.0],
                "family": ["baseline", "test", "test"],
                "complexity": [0, 1, 1],
                "exit_only": [True, True, True],
            },
            index=["baseline", "bad_dd", "balanced"],
        )
        selected, eligible = select_training_candidate(
            metrics,
            ["baseline", "bad_dd", "balanced"],
        )
        self.assertEqual(selected, "balanced")
        self.assertNotIn("bad_dd", eligible.index)

    def test_selector_falls_back_to_baseline(self) -> None:
        metrics = pd.DataFrame(
            {
                "annualized_return": [0.50, 0.40],
                "max_drawdown": [-0.40, -0.45],
                "sharpe_ratio": [1.0, 0.8],
                "completed_trades": [10, 10],
                "turnover": [20.0, 20.0],
                "family": ["baseline", "test"],
                "complexity": [0, 1],
                "exit_only": [True, True],
            },
            index=["baseline", "worse"],
        )
        selected, _ = select_training_candidate(metrics, ["baseline", "worse"])
        self.assertEqual(selected, "baseline")

    def test_stitched_stream_charges_model_transition(self) -> None:
        index = pd.to_datetime(
            ["2021-01-01", "2021-12-31", "2022-01-01", "2022-01-02"]
        )
        eth_returns = pd.Series(0.0, index=index)
        exposures = pd.DataFrame(
            {
                "model_a": [1.0, 1.0, 1.0, 1.0],
                "model_b": [0.0, 0.0, 0.0, 0.0],
            },
            index=index,
        )
        stream = build_stitched_stream(
            eth_returns,
            exposures,
            {2021: "model_a", 2022: "model_b"},
            start=index[0],
            end=index[-1],
        )
        self.assertAlmostEqual(float(stream["Turnover"].sum()), 2.0)
        self.assertAlmostEqual(float(stream["DailyReturn"].sum()), -0.012)
        self.assertEqual(stream.loc[pd.Timestamp("2021-12-31"), "SelectedVariant"], "model_a")
        self.assertEqual(stream.loc[pd.Timestamp("2022-01-01"), "SelectedVariant"], "model_b")

    def test_extra_delay_uses_previous_exposure(self) -> None:
        full_index = pd.to_datetime(["2020-12-31", "2021-01-01", "2021-01-02"])
        eth_returns = pd.Series(0.0, index=full_index)
        exposures = pd.DataFrame({"model": [1.0, 0.0, 0.0]}, index=full_index)
        delayed = build_stitched_stream(
            eth_returns,
            exposures,
            {2021: "model"},
            start=pd.Timestamp("2021-01-01"),
            end=pd.Timestamp("2021-01-02"),
            extra_delay_days=1,
        )
        self.assertEqual(float(delayed.iloc[0]["Exposure"]), 1.0)
        self.assertEqual(float(delayed.iloc[1]["Exposure"]), 0.0)
        self.assertAlmostEqual(float(delayed["Turnover"].sum()), 2.0)

    def test_cscv_returns_all_symmetric_splits(self) -> None:
        rng = np.random.default_rng(42)
        returns = pd.DataFrame(
            rng.normal(0.0005, 0.02, size=(80, 4)),
            columns=["a", "b", "c", "d"],
        )
        summary, details = cscv_pbo(returns, blocks=4, label="test")
        self.assertEqual(summary["splits"], math.comb(4, 2))
        self.assertEqual(len(details), math.comb(4, 2))
        self.assertGreaterEqual(summary["pbo"], 0.0)
        self.assertLessEqual(summary["pbo"], 1.0)

    def test_cscv_handles_tied_test_sharpes(self) -> None:
        base = np.asarray([0.01, -0.005, 0.004, 0.002] * 20)
        returns = pd.DataFrame({"a": base, "b": base, "c": base + 1e-15})
        summary, details = cscv_pbo(returns, blocks=4, label="ties")
        self.assertEqual(len(details), math.comb(4, 2))
        self.assertTrue(np.isfinite(details["logit"]).all())
        self.assertGreaterEqual(summary["pbo"], 0.0)
        self.assertLessEqual(summary["pbo"], 1.0)

    def test_expected_max_sharpe_increases_with_trials(self) -> None:
        sharpes = pd.Series([-0.02, -0.01, 0.0, 0.01, 0.02])
        two_trials = expected_max_sharpe(sharpes, trials=2)
        hundred_trials = expected_max_sharpe(sharpes, trials=100)
        self.assertGreater(hundred_trials, two_trials)

    def test_higher_dsr_benchmark_reduces_probability(self) -> None:
        returns = pd.Series([0.01, -0.004, 0.008, 0.002, -0.003] * 60)
        psr = probabilistic_sharpe(returns, benchmark_daily_sharpe=0.0)
        dsr = probabilistic_sharpe(returns, benchmark_daily_sharpe=0.05)
        self.assertGreater(psr["probability"], dsr["probability"])


if __name__ == "__main__":
    unittest.main()
