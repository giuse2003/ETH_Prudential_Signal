"""
Audit trade-by-trade della variante Trail8 priority.

Confronta la cronologia acquisti/vendite della variante con la Baseline
ufficiale e analizza i rientri successivi alle uscite Trail8.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.run_trail_priority_validation import apply_trail_priority  # noqa: E402


DATA_PATH = ROOT / "data" / "indicators_with_signals.csv"
REPORT_MD = ROOT / "reports" / "trail_priority_trade_audit.md"
TRADE_CSV = ROOT / "reports" / "trail_priority_trade_audit.csv"
REENTRY_CSV = ROOT / "reports" / "trail_priority_reentry_audit.csv"


def _fmt_pct(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _fmt_usd(value: float) -> str:
    if pd.isna(value):
        return "n/a"
    return f"{value:.2f}"


def _load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"]).sort_values("Date")
    return df.set_index("Date")


def trades_from_signals(df: pd.DataFrame, reason_col: str | None = None) -> pd.DataFrame:
    trades: list[dict[str, object]] = []
    exposure = False
    entry_date: pd.Timestamp | None = None
    entry_price: float | None = None

    for date, row in df.iterrows():
        signal = row["Segnale"]
        close = float(row["Close"])
        if signal == "ACQUISTA" and not exposure:
            exposure = True
            entry_date = date
            entry_price = close
        elif signal == "VENDI" and exposure:
            trade_slice = df.loc[entry_date:date]
            peak = float(trade_slice["Close"].max())
            trough = float(trade_slice["Close"].min())
            reason = row.get(reason_col, "") if reason_col else ""
            trades.append(
                {
                    "entry_date": entry_date,
                    "entry_price": entry_price,
                    "exit_date": date,
                    "exit_price": close,
                    "exit_reason": reason,
                    "return": close / entry_price - 1.0,
                    "days": int((date - entry_date).days),
                    "peak_price": peak,
                    "max_gain": peak / entry_price - 1.0,
                    "trough_price": trough,
                    "max_drawdown_from_entry": trough / entry_price - 1.0,
                }
            )
            exposure = False
            entry_date = None
            entry_price = None

    return pd.DataFrame(trades)


def add_priority_exit_reason(priority: pd.DataFrame) -> pd.DataFrame:
    out = priority.copy()
    reason = pd.Series("", index=out.index, dtype=object)
    reason[(out["Segnale"] == "VENDI") & (out["Trail8_Confirmed_Priority"])] = "Trail8 priority"
    reason[(out["Segnale"] == "VENDI") & (reason == "")] = "Official sell"
    out["ExitReason"] = reason
    return out


def find_baseline_context(row: pd.Series, baseline_trades: pd.DataFrame) -> pd.Series | None:
    entry = row["entry_date"]
    matches = baseline_trades[
        (baseline_trades["entry_date"] <= entry)
        & (baseline_trades["exit_date"] >= entry)
    ]
    if not matches.empty:
        return matches.iloc[0]

    next_matches = baseline_trades[baseline_trades["entry_date"] >= entry]
    if not next_matches.empty:
        return next_matches.iloc[0]
    return None


def build_trade_audit(priority_trades: pd.DataFrame, baseline_trades: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for idx, trade in priority_trades.iterrows():
        context = find_baseline_context(trade, baseline_trades)
        baseline_return = np.nan
        baseline_exit_date = pd.NaT
        baseline_exit_price = np.nan
        baseline_entry_date = pd.NaT
        relation = "no baseline context"

        if context is not None:
            baseline_entry_date = context["entry_date"]
            baseline_exit_date = context["exit_date"]
            baseline_exit_price = float(context["exit_price"])
            baseline_return = baseline_exit_price / float(trade["entry_price"]) - 1.0
            if trade["exit_date"] < context["exit_date"]:
                relation = "exits before baseline"
            elif trade["exit_date"] == context["exit_date"]:
                relation = "same exit as baseline"
            else:
                relation = "exits after baseline context"

        delta_vs_baseline_hold = float(trade["return"]) - baseline_return if pd.notna(baseline_return) else np.nan
        if pd.isna(delta_vs_baseline_hold):
            comparison_status = "n/a"
        elif delta_vs_baseline_hold > 1e-12:
            comparison_status = "migliora"
        elif delta_vs_baseline_hold < -1e-12:
            comparison_status = "peggiora"
        else:
            comparison_status = "uguale"

        rows.append(
            {
                "operation": idx + 1,
                "entry_date": trade["entry_date"].date(),
                "entry_price": trade["entry_price"],
                "exit_date": trade["exit_date"].date(),
                "exit_price": trade["exit_price"],
                "exit_reason": trade["exit_reason"],
                "return": trade["return"],
                "days": trade["days"],
                "max_gain": trade["max_gain"],
                "max_drawdown_from_entry": trade["max_drawdown_from_entry"],
                "baseline_entry_date": baseline_entry_date.date() if pd.notna(baseline_entry_date) else None,
                "baseline_exit_date": baseline_exit_date.date() if pd.notna(baseline_exit_date) else None,
                "baseline_exit_price": baseline_exit_price,
                "baseline_hold_return_from_same_entry": baseline_return,
                "delta_vs_baseline_hold": delta_vs_baseline_hold,
                "relation": relation,
                "improves_vs_baseline_hold": bool(delta_vs_baseline_hold > 0) if pd.notna(delta_vs_baseline_hold) else None,
                "comparison_status": comparison_status,
            }
        )

    return pd.DataFrame(rows)


def build_reentry_audit(priority_trades: pd.DataFrame, baseline_trades: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for idx, trade in priority_trades.iterrows():
        if trade["exit_reason"] != "Trail8 priority":
            continue

        next_trade = priority_trades.iloc[idx + 1] if idx + 1 < len(priority_trades) else None
        context = find_baseline_context(trade, baseline_trades)

        next_entry_date = pd.NaT
        next_entry_price = np.nan
        days_to_reentry = np.nan
        reentry_delta = np.nan
        reentry_advantage = "no reentry"

        if next_trade is not None:
            next_entry_date = next_trade["entry_date"]
            next_entry_price = float(next_trade["entry_price"])
            days_to_reentry = int((next_entry_date - trade["exit_date"]).days)
            reentry_delta = next_entry_price / float(trade["exit_price"]) - 1.0
            if reentry_delta < 0:
                reentry_advantage = "vantaggioso: rientro piu' basso"
            elif reentry_delta > 0:
                reentry_advantage = "svantaggioso: rientro piu' alto"
            else:
                reentry_advantage = "neutro"

        baseline_exit_date = pd.NaT
        baseline_exit_price = np.nan
        baseline_move_to_exit = np.nan
        if context is not None:
            baseline_exit_date = context["exit_date"]
            baseline_exit_price = float(context["exit_price"])
            baseline_move_to_exit = baseline_exit_price / float(trade["exit_price"]) - 1.0

        rows.append(
            {
                "trail_exit_date": trade["exit_date"].date(),
                "trail_exit_price": trade["exit_price"],
                "trade_entry_date": trade["entry_date"].date(),
                "trade_return_at_exit": trade["return"],
                "next_entry_date": next_entry_date.date() if pd.notna(next_entry_date) else None,
                "next_entry_price": next_entry_price,
                "days_to_reentry": days_to_reentry,
                "reentry_delta": reentry_delta,
                "reentry_advantage": reentry_advantage,
                "baseline_exit_date": baseline_exit_date.date() if pd.notna(baseline_exit_date) else None,
                "baseline_exit_price": baseline_exit_price,
                "baseline_move_after_trail_exit": baseline_move_to_exit,
            }
        )

    return pd.DataFrame(rows)


def main() -> None:
    df = _load_data()
    priority, _events = apply_trail_priority(df)
    priority = add_priority_exit_reason(priority)

    baseline_trades = trades_from_signals(df)
    priority_trades = trades_from_signals(priority, reason_col="ExitReason")
    trade_audit = build_trade_audit(priority_trades, baseline_trades)
    reentry_audit = build_reentry_audit(priority_trades, baseline_trades)

    TRADE_CSV.parent.mkdir(parents=True, exist_ok=True)
    trade_audit.to_csv(TRADE_CSV, index=False)
    reentry_audit.to_csv(REENTRY_CSV, index=False)

    improved = int((trade_audit["comparison_status"] == "migliora").sum())
    equal = int((trade_audit["comparison_status"] == "uguale").sum())
    worsened = int((trade_audit["comparison_status"] == "peggiora").sum())
    trail_exits = trade_audit[trade_audit["exit_reason"] == "Trail8 priority"]
    lower_reentries = int((reentry_audit["reentry_delta"] < 0).sum())
    higher_reentries = int((reentry_audit["reentry_delta"] > 0).sum())

    lines = [
        "# Trail8 Priority Trade Audit",
        "",
        "Audit cronologico della variante Trail8 priority rispetto alla Baseline ufficiale.",
        "",
        "La Baseline ufficiale non viene modificata.",
        "",
        "## Sintesi",
        "",
        f"- Operazioni Trail8 priority chiuse: {len(priority_trades)}.",
        f"- Operazioni Baseline chiuse: {len(baseline_trades)}.",
        f"- Operazioni Trail8 priority migliori del mantenimento Baseline sullo stesso segmento: {improved}.",
        f"- Operazioni Trail8 priority uguali al mantenimento Baseline sullo stesso segmento: {equal}.",
        f"- Operazioni Trail8 priority peggiori del mantenimento Baseline sullo stesso segmento: {worsened}.",
        f"- Uscite Trail8 priority: {len(trail_exits)}.",
        f"- Rientri successivi piu' bassi dell'uscita Trail8: {lower_reentries}.",
        f"- Rientri successivi piu' alti dell'uscita Trail8: {higher_reentries}.",
        "",
        "## Cronologia Operazioni Trail8 Priority",
        "",
        "| # | Entry | Buy USD | Exit | Sell USD | Motivo | Return | Baseline exit | Baseline hold | Delta | Esito |",
        "|---:|---|---:|---|---:|---|---:|---|---:|---:|---|",
    ]

    for _, row in trade_audit.iterrows():
        esito = row["comparison_status"]
        lines.append(
            f"| {int(row['operation'])} | {row['entry_date']} | {_fmt_usd(row['entry_price'])} | "
            f"{row['exit_date']} | {_fmt_usd(row['exit_price'])} | {row['exit_reason']} | "
            f"{_fmt_pct(row['return'])} | {row['baseline_exit_date']} | "
            f"{_fmt_pct(row['baseline_hold_return_from_same_entry'])} | "
            f"{_fmt_pct(row['delta_vs_baseline_hold'])} | {esito} |"
        )

    lines.extend(
        [
            "",
            "## Rientri Dopo Uscita Trail8 Priority",
            "",
            "| Uscita Trail8 | Sell USD | Rientro | Buy USD | Giorni | Delta rientro | Lettura | Baseline exit | Movimento fino a exit Baseline |",
            "|---|---:|---|---:|---:|---:|---|---|---:|",
        ]
    )

    for _, row in reentry_audit.iterrows():
        lines.append(
            f"| {row['trail_exit_date']} | {_fmt_usd(row['trail_exit_price'])} | "
            f"{row['next_entry_date']} | {_fmt_usd(row['next_entry_price'])} | "
            f"{int(row['days_to_reentry']) if pd.notna(row['days_to_reentry']) else 'n/a'} | "
            f"{_fmt_pct(row['reentry_delta'])} | {row['reentry_advantage']} | "
            f"{row['baseline_exit_date']} | {_fmt_pct(row['baseline_move_after_trail_exit'])} |"
        )

    lines.extend(
        [
            "",
            "## File generati",
            "",
            f"- `{TRADE_CSV.relative_to(ROOT)}`",
            f"- `{REENTRY_CSV.relative_to(ROOT)}`",
        ]
    )

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Priority trades: {len(priority_trades)}")
    print(f"Baseline trades: {len(baseline_trades)}")
    print(f"Improved vs baseline hold: {improved}")
    print(f"Equal vs baseline hold: {equal}")
    print(f"Worse vs baseline hold: {worsened}")
    print(f"Trail exits: {len(trail_exits)}")
    print(f"Lower reentries: {lower_reentries}")
    print(f"Higher reentries: {higher_reentries}")
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
