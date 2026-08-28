from __future__ import annotations

import unittest
from pathlib import Path

from reproducibility import sha256_file, verify_frozen_artifacts, verify_frozen_run


class ReproducibilityTests(unittest.TestCase):
    def test_official_frozen_baseline_is_reproduced_exactly(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = root / "docs" / "runs" / "baseline-v3-2026-08-27" / "manifest.json"
        result = verify_frozen_run(manifest, strict_environment=True)
        self.assertEqual(result["run_id"], "baseline-v3-2026-08-27")
        self.assertEqual(result["period"]["coinbase_history_start"], "2016-05-23")
        self.assertEqual(result["period"]["evaluation_end"], "2026-08-27")
        self.assertEqual(result["period"]["observations"], 3550)
        self.assertEqual(result["metrics"]["strategy"]["transaction_cost_rate"], 0.006)

    def test_previous_baseline_archive_is_unchanged(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = root / "docs" / "runs" / "baseline-v2-2026-07-26" / "manifest.json"
        result = verify_frozen_artifacts(manifest)

        self.assertEqual(result["run_id"], "baseline-v2-2026-07-26")
        self.assertEqual(
            sha256_file(manifest),
            "2df53ef75e6294940927e5a9dc63ce46ac5f8b2b60a3c0f7c3998c2d84283cb2",
        )

    def test_legacy_baseline_archive_is_unchanged(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = root / "docs" / "runs" / "baseline-v1-2026-07-26" / "manifest.json"
        result = verify_frozen_artifacts(manifest)

        self.assertEqual(result["run_id"], "baseline-v1-2026-07-26")
        self.assertEqual(
            sha256_file(manifest),
            "dd7cfbbbd93b535e069125ce348c5250b0545e1ed0c04608a80a9bccbc7509ce",
        )


if __name__ == "__main__":
    unittest.main()
