"""
Audit trade-by-trade della variante SMA50 a 1 giorno.

Confronta la Baseline ufficiale (SMA50 sotto per 2 giorni + Trail8) con la
variante che vende gia' al primo Close sotto SMA50, mantenendo invariati
ingressi e Trail8.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_sma50_exit_timing_test import _build_signals, _trades  # noqa: E402


DATA_PATH = ROOT / "data" / "indicators_with_signals.csv"
REPORT_MD = ROOT / "reports" / "sma50_exit_timing_audit.md"
AUDIT_CSV = ROOT / "reports" / "sma50_exit_timing_audit.csv"
DIFF_CSV = ROOT / "reports" / "sma50_exit_timing_changed_segments.csv"


def _pct(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _usd(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.2f}"


def _status(delta: float) -> str:
    if pd.isna(delta):
        return "n/a"
    if delta > 1e-12:
        return "migliora"
    if delta < -1e-12:
        return "peggiora"
    return "uguale"


def main() -> None:
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    baseline_signals = _build_signals(df, sell_after_days=2)
    one_day_signals = _build_signals(df, sell_after_days=1)

    baseline_trades = _trades(baseline_signals, "SMA50 2 giorni + Trail8")
    one_day_trades = _trades(one_day_signals, "SMA50 1 giorno + Trail8")

    rows: list[dict[str, object]] = []
    for _, base in baseline_trades.iterrows():
        seg = one_day_trades[
            (pd.to_datetime(one_day_trades["entry_date"]) >= pd.to_datetime(base["entry_date"]))
            & (pd.to_datetime(one_day_trades["exit_date"]) <= pd.to_datetime(base["exit_date"]))
        ].copy()
        if seg.empty:
            compound = 0.0
            sequence = "nessuna operazione"
        else:
            compound = 1.0
            for _, trade in seg.iterrows():
                compound *= 1.0 + float(trade["return"])
            compound -= 1.0
            sequence = "; ".join(
                f"{trade['entry_date']}->{trade['exit_date']} {trade['exit_reason']} {_pct(float(trade['return']))}"
                for _, trade in seg.iterrows()
            )

        delta = compound - float(base["return"])
        changed = (
            len(seg) != 1
            or (not seg.empty and str(seg.iloc[0]["entry_date"]) != str(base["entry_date"]))
            or (not seg.empty and str(seg.iloc[0]["exit_date"]) != str(base["exit_date"]))
            or abs(delta) > 1e-12
        )

        rows.append(
            {
                "baseline_entry": base["entry_date"],
                "baseline_entry_price": base["entry_price"],
                "baseline_exit": base["exit_date"],
                "baseline_exit_price": base["exit_price"],
                "baseline_reason": base["exit_reason"],
                "baseline_return": base["return"],
                "one_day_trades": len(seg),
                "one_day_compound_return": compound,
                "delta": delta,
                "status": _status(delta),
                "changed": changed,
                "one_day_sequence": sequence,
            }
        )

    audit = pd.DataFrame(rows)
    changed = audit[audit["changed"]].copy()

    AUDIT_CSV.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(AUDIT_CSV, index=False)
    changed.to_csv(DIFF_CSV, index=False)

    lines = [
        "# SMA50 Exit Timing Audit",
        "",
        "Audit trade-by-trade della variante `Close < SMA50` a 1 giorno rispetto alla Baseline a 2 giorni.",
        "",
        "## Sintesi",
        "",
        f"- Segmenti Baseline confrontati: {len(audit)}.",
        f"- Segmenti modificati dalla variante a 1 giorno: {len(changed)}.",
        f"- Segmenti migliorati: {int((changed['status'] == 'migliora').sum())}.",
        f"- Segmenti uguali: {int((changed['status'] == 'uguale').sum())}.",
        f"- Segmenti peggiorati: {int((changed['status'] == 'peggiora').sum())}.",
        "",
        "## Segmenti Modificati",
        "",
        "| Baseline entry | Baseline exit | Baseline return | Variante 1g return | Delta | Esito | Sequenza variante 1g |",
        "|---|---|---:|---:|---:|---|---|",
    ]

    for _, row in changed.iterrows():
        lines.append(
            f"| {row['baseline_entry']} | {row['baseline_exit']} | {_pct(row['baseline_return'])} | "
            f"{_pct(row['one_day_compound_return'])} | {_pct(row['delta'])} | "
            f"{row['status']} | {row['one_day_sequence']} |"
        )

    lines.extend(
        [
            "",
            "## File generati",
            "",
            f"- `{AUDIT_CSV.relative_to(ROOT)}`",
            f"- `{DIFF_CSV.relative_to(ROOT)}`",
        ]
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(audit.to_string(index=False))
    print(f"Changed segments: {len(changed)}")
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
