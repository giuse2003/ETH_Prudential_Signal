"""
Audit per segmento Baseline della variante Trail8 priority.

Un segmento Baseline e' una singola operazione della Baseline ufficiale. Dentro
quel segmento la variante Trail8 priority puo' spezzare l'operazione in piu'
trade. Questo script confronta il risultato composto della variante con il
risultato dell'operazione Baseline unica.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_trail_priority_trade_audit import (  # noqa: E402
    add_priority_exit_reason,
    trades_from_signals,
)
from scripts.run_trail_priority_validation import apply_trail_priority  # noqa: E402


DATA_PATH = ROOT / "data" / "indicators_with_signals.csv"
REPORT_MD = ROOT / "reports" / "trail_priority_segment_audit.md"
SEGMENT_CSV = ROOT / "reports" / "trail_priority_segment_audit.csv"


def _pct(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _usd(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.2f}"


def main() -> None:
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    priority, _events = apply_trail_priority(df)
    priority = add_priority_exit_reason(priority)

    baseline_trades = trades_from_signals(df)
    priority_trades = trades_from_signals(priority, reason_col="ExitReason")

    rows: list[dict[str, object]] = []
    for _, base in baseline_trades.iterrows():
        seg = priority_trades[
            (priority_trades["entry_date"] >= base["entry_date"])
            & (priority_trades["exit_date"] <= base["exit_date"])
        ].copy()
        if seg.empty or not (seg["exit_reason"] == "Trail8 priority").any():
            continue

        compound = 1.0
        for _, trade in seg.iterrows():
            compound *= 1.0 + float(trade["return"])
        compound -= 1.0

        baseline_return = float(base["return"])
        delta = compound - baseline_return
        if delta > 1e-12:
            status = "migliora"
        elif delta < -1e-12:
            status = "peggiora"
        else:
            status = "uguale"

        sequence = "; ".join(
            f"{trade['entry_date'].date()}->{trade['exit_date'].date()} "
            f"{trade['exit_reason']} {_pct(float(trade['return']))}"
            for _, trade in seg.iterrows()
        )

        rows.append(
            {
                "baseline_entry": base["entry_date"].date(),
                "baseline_entry_price": base["entry_price"],
                "baseline_exit": base["exit_date"].date(),
                "baseline_exit_price": base["exit_price"],
                "baseline_return": baseline_return,
                "priority_trades": len(seg),
                "trail_exits": int((seg["exit_reason"] == "Trail8 priority").sum()),
                "priority_compound_return": compound,
                "delta_vs_baseline": delta,
                "status": status,
                "sequence": sequence,
            }
        )

    audit = pd.DataFrame(rows)
    SEGMENT_CSV.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(SEGMENT_CSV, index=False)

    without_2025 = audit[audit["baseline_entry"].astype(str) != "2025-07-07"]
    lines = [
        "# Trail8 Priority Segment Audit",
        "",
        "Confronto per segmento Baseline: una singola operazione Baseline contro la sequenza composta dei trade Trail8 priority nello stesso intervallo.",
        "",
        "## Sintesi",
        "",
        f"- Segmenti Baseline con almeno una uscita Trail8 priority: {len(audit)}.",
        f"- Segmenti che migliorano: {int((audit['status'] == 'migliora').sum())}.",
        f"- Segmenti uguali: {int((audit['status'] == 'uguale').sum())}.",
        f"- Segmenti che peggiorano: {int((audit['status'] == 'peggiora').sum())}.",
        "",
        "Escludendo il caso 2025 gia' classificato come sfavorevole:",
        "",
        f"- segmenti rimanenti: {len(without_2025)};",
        f"- migliorano: {int((without_2025['status'] == 'migliora').sum())};",
        f"- uguali: {int((without_2025['status'] == 'uguale').sum())};",
        f"- peggiorano: {int((without_2025['status'] == 'peggiora').sum())}.",
        "",
        "## Segmenti",
        "",
        "| Baseline entry | Baseline exit | Baseline return | Trail8 sequence return | Delta | Esito | Sequenza Trail8 priority |",
        "|---|---|---:|---:|---:|---|---|",
    ]

    for _, row in audit.iterrows():
        lines.append(
            f"| {row['baseline_entry']} | {row['baseline_exit']} | "
            f"{_pct(row['baseline_return'])} | {_pct(row['priority_compound_return'])} | "
            f"{_pct(row['delta_vs_baseline'])} | {row['status']} | {row['sequence']} |"
        )

    lines.extend(["", "## File generato", "", f"- `{SEGMENT_CSV.relative_to(ROOT)}`"])
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(audit.to_string(index=False))
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
