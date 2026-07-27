from __future__ import annotations

import json
import hashlib
import tempfile
import unittest
from pathlib import Path

from reports.publication import validate_bundle, write_manifest


class PublicationBundleTests(unittest.TestCase):
    def test_rejects_mixed_run_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            for name in ("status.json", "live-status.json"):
                (root / name).write_text(json.dumps({"run_id": "run-a"}), encoding="utf-8")
            (root / "chart-data.json").write_text(
                json.dumps({"run_id": "run-b", "rows": []}), encoding="utf-8"
            )
            (root / "raw_candles.csv").write_text("Date,Close\n", encoding="utf-8")
            raw_hash = hashlib.sha256((root / "raw_candles.csv").read_bytes()).hexdigest()
            write_manifest(
                root,
                {"run_id": "run-a"},
                period={},
                metrics={},
                provenance={"input_candles_sha256": raw_hash},
                artifact_names=["raw_candles.csv", "status.json", "live-status.json", "chart-data.json"],
            )
            with self.assertRaisesRegex(ValueError, "run_id incoerente"):
                validate_bundle(root)

    def test_accepts_complete_bundle_with_matching_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            for name in ("status.json", "live-status.json", "chart-data.json"):
                (root / name).write_text(json.dumps({"run_id": "run-a"}), encoding="utf-8")
            (root / "raw_candles.csv").write_text("Date,Close\n", encoding="utf-8")
            raw_hash = hashlib.sha256((root / "raw_candles.csv").read_bytes()).hexdigest()
            write_manifest(
                root,
                {"run_id": "run-a"},
                period={},
                metrics={},
                provenance={"input_candles_sha256": raw_hash},
                artifact_names=["raw_candles.csv", "status.json", "live-status.json", "chart-data.json"],
            )
            manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["rules"]["sell"][0], "Close < SMA50 * 0.98")
            self.assertIn("momentum 7d >= -15%", manifest["rules"]["sell"][1])
            self.assertIn("0.6% per lato", manifest["rules"]["transaction_costs"])
            validate_bundle(root)


if __name__ == "__main__":
    unittest.main()
