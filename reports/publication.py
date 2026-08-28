"""Pubblicazione validata e transazionale degli artefatti di un'esecuzione."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import shutil
import subprocess
import tempfile
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from config import CFG
from reports.generate import write_utf8_text

PUBLIC_JSON_FILES = ("status.json", "live-status.json", "chart-data.json")
BASELINE_MANIFEST = "runs/baseline-v3-2026-08-27/manifest.json"


def new_run_metadata() -> dict[str, str]:
    now = datetime.now(timezone.utc)
    return {
        "run_id": f"{now.strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}",
        "generated_at_utc": now.isoformat(),
        "run_type": "operational-latest",
        "project": CFG.model_name,
        "model_version": CFG.model_version,
        "data_source": CFG.data_source,
        "market": CFG.product_id,
        "timezone": "UTC",
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def operational_provenance(candles, project_root: str | Path) -> dict:
    root = Path(project_root)
    normalized = candles.copy().sort_index()
    normalized.index.name = "Date"
    raw_bytes = normalized.to_csv(index=True, lineterminator="\n").encode("utf-8")
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    lock_path = root / "requirements.lock"
    dependencies = {
        name: importlib.metadata.version(name)
        for name in ("numpy", "pandas", "matplotlib", "requests")
    }
    return {
        "source_commit": commit,
        "python": platform.python_version(),
        "dependencies": dependencies,
        "requirements_lock_sha256": _sha256(lock_path) if lock_path.exists() else None,
        "input_candles_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "input_observations": int(len(normalized)),
        "input_first_candle": normalized.index[0].strftime("%Y-%m-%d"),
        "input_last_candle": normalized.index[-1].strftime("%Y-%m-%d"),
        "historical_cache_allowed": True,
        "frozen_baseline_manifest": BASELINE_MANIFEST,
    }


@contextmanager
def staged_run(target_dir: str | Path) -> Iterator[Path]:
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="eth-usd-signal-") as temp_dir:
        yield Path(temp_dir)


def write_manifest(
    staging_dir: str | Path,
    metadata: dict,
    *,
    period: dict,
    metrics: dict,
    provenance: dict,
    artifact_names: list[str],
) -> Path:
    staging = Path(staging_dir)
    artifacts = {
        name: {
            "path": name,
            "sha256": _sha256(staging / name),
            "bytes": (staging / name).stat().st_size,
        }
        for name in artifact_names
    }
    payload = {
        **metadata,
        "period": period,
        "rules": {
            "buy_logic": "tutte le condizioni del percorso standard OR tutte le condizioni del breakout protetto",
            "buy_standard": [
                "Close > SMA200",
                "SMA50 > SMA200",
                "40 <= RSI14 <= 65 per nuovi ingressi",
                "Close > Close 7 giorni prima",
                "Volume ETH-USD > media 20 giorni",
            ],
            "buy_breakout": [
                "SMA50 <= SMA200",
                "Close > SMA50 e Close >= SMA200 * 0.90",
                "SMA50 >= SMA50 di 5 giorni prima",
                "40 <= RSI14 <= 65",
                "Close > Close 7 giorni prima",
                "Volume ETH-USD >= media 20 giorni * 1.20",
                "Close > massimo dei 5 Close precedenti",
                "guardrail: non insieme SMA200 slope20 > 0% e SMA50/SMA200 < -15%",
            ],
            "sell": [
                "Close < SMA50 * 0.98",
                "Trailing stop 8% dal massimo post-ingresso, confermato da momentum 7d >= -15% e volume relativo >= 20%",
            ],
            "sell_precedence": True,
            "breakout_operational_start": "2026-08-28",
            "operational_state_at_promotion": "FUORI; nessun ingresso retroattivo il 2026-08-17",
            "execution_delay_days": 1,
            "exposure": "0% o 100%; MANTIENI STATO ATTUALE conserva l'esposizione",
            "transaction_costs": "0.6% per lato inclusi per strategia e Buy & Hold",
            "slippage_spread_taxes_cash_yield": "non inclusi",
        },
        "metrics": metrics,
        "provenance": provenance,
        "artifacts": artifacts,
    }
    return write_utf8_text(staging / "manifest.json", json.dumps(payload, indent=2))


def validate_bundle(staging_dir: str | Path) -> None:
    staging = Path(staging_dir)
    manifest = json.loads((staging / "manifest.json").read_text(encoding="utf-8"))
    run_id = manifest.get("run_id")
    if not run_id:
        raise ValueError("Manifest senza run_id.")
    for name in PUBLIC_JSON_FILES:
        payload = json.loads((staging / name).read_text(encoding="utf-8"))
        if payload.get("run_id") != run_id:
            raise ValueError(f"run_id incoerente in {name}.")
    for name, info in manifest.get("artifacts", {}).items():
        path = staging / name
        if not path.exists() or _sha256(path) != info.get("sha256"):
            raise ValueError(f"Artefatto non valido: {name}")
    raw_hash = manifest["artifacts"]["raw_candles.csv"]["sha256"]
    if raw_hash != manifest["provenance"]["input_candles_sha256"]:
        raise ValueError("Hash dello snapshot grezzo incoerente con la provenienza.")


def publish_bundle(
    staging_dir: str | Path,
    target_dir: str | Path,
    artifact_names: list[str],
) -> None:
    staging = Path(staging_dir)
    target = Path(target_dir)
    target.mkdir(parents=True, exist_ok=True)
    names = [*artifact_names, "manifest.json"]
    backup_dir = Path(tempfile.mkdtemp(prefix="eth-usd-signal-backup-"))
    replaced: list[str] = []
    try:
        for name in names:
            destination = target / name
            if destination.exists():
                shutil.copy2(destination, backup_dir / name)
        for name in names:
            source = staging / name
            if not source.exists():
                raise FileNotFoundError(source)
            temporary = target / f".{name}.new"
            shutil.copy2(source, temporary)
            os.replace(temporary, target / name)
            replaced.append(name)
    except Exception:
        for name in replaced:
            backup = backup_dir / name
            destination = target / name
            if backup.exists():
                os.replace(backup, destination)
            elif destination.exists():
                destination.unlink()
        raise
    finally:
        shutil.rmtree(backup_dir, ignore_errors=True)
