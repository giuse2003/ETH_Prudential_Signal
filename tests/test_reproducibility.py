from __future__ import annotations

import unittest
from pathlib import Path

from reproducibility import verify_frozen_run


class ReproducibilityTests(unittest.TestCase):
    def test_frozen_baseline_is_reproduced_exactly(self) -> None:
        root = Path(__file__).resolve().parents[1]
        manifest = root / "docs" / "runs" / "baseline-v1-2026-07-26" / "manifest.json"
        result = verify_frozen_run(manifest, strict_environment=True)
        self.assertEqual(result["run_id"], "baseline-v1-2026-07-26")
        self.assertEqual(result["period"]["coinbase_history_start"], "2016-05-23")
        self.assertEqual(result["period"]["evaluation_end"], "2026-07-26")
        self.assertEqual(result["period"]["observations"], 3518)


if __name__ == "__main__":
    unittest.main()
