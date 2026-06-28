"""
Confronto completo operazione-per-operazione tra Baseline e candidato uscita.

Modello candidato:
- ingressi Baseline invariati;
- uscita ufficiale invariata;
- uscita aggiuntiva Trail8 confermato -5 / vol +20.

Questo script non modifica i segnali ufficiali.
Le performance sono misurate in EUR tramite Close_EUR.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import run_backtest


SOURCE_CSV = PROJECT_ROOT / "data" / "indicators_with_signals.csv"
OUT_CSV = PROJECT_ROOT / "reports" / "exit_trade_comparison.csv"
OUT_MD = PROJECT_ROOT / "reports" / "exit_trade_comparison.md"

END_DATE = "2026-06-27"
STOP_PCT = 0.08
MOMENTUM_MIN = -0.05
VOLUME_REL_MIN = 0.20


def _baseline_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()


def _candidate_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, set[str]]:
    exposure = 0.0
    peak_close: float | None = None
    signals: list[str] = []
    forced_exit_dates: set[str] = set()

    for date, row in df.iterrows():
        official = str(row["Segnale"])
        signal = official
        close = float(row["Close"])

        if official == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            peak_close = close
        elif official == "ACQUISTA":
            signal = "MANTIENI"
            peak_close = max(peak_close or close, close)
        elif official == "VENDI":
            exposure = 0.0
            peak_close = None
        elif exposure > 0.0 and peak_close is not None:
            peak_close = max(peak_close, close)
            stop_level = peak_close * (1.0 - STOP_PCT)
            if close <= stop_level:
                momentum_7d = close / float(row["Close_7d_ago"]) - 1.0
                volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
                if momentum_7d >= MOMENTUM_MIN and volume_rel >= VOLUME_REL_MIN:
                    signal = "VENDI"
                    forced_exit_dates.add(date.date().isoformat())
                    exposure = 0.0
                    peak_close = None

        signals.append(signal)

    frame = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    frame["Segnale"] = signals
    return frame, forced_exit_dates


def _trade_row(
    df: pd.DataFrame,
    model: str,
    trade_id: int,
    entry_date: pd.Timestamp,
    exit_date: pd.Timestamp,
    *,
    exit_type: str,
) -> dict[str, float | int | str]:
    entry_price = float(df.loc[entry_date, "Close_EUR"])
    exit_price = float(df.loc[exit_date, "Close_EUR"])
    path = df.loc[entry_date:exit_date, "Close_EUR"]
    normalized = path / entry_price
    dd = normalized / normalized.cummax() - 1.0
    trade_return = exit_price / entry_price - 1.0
    return {
        "model": model,
        "trade_id": trade_id,
        "entry_date": entry_date.date().isoformat(),
        "entry_price_eur": entry_price,
        "exit_date": exit_date.date().isoformat(),
        "exit_price_eur": exit_price,
        "exit_type": exit_type,
        "trade_return": trade_return,
        "gain_pct": max(trade_return, 0.0),
        "loss_pct": min(trade_return, 0.0),
        "drawdown_suffered_pct": float(dd.min()),
        "max_gain_pct": float(normalized.max() - 1.0),
        "duration_days": int((exit_date - entry_date).days),
    }


def _trades_from_signals(
    df: pd.DataFrame,
    signals: pd.Series,
    model: str,
    forced_exit_dates: set[str] | None = None,
) -> pd.DataFrame:
    forced_exit_dates = forced_exit_dates or set()
    exposure = 0.0
    entry_date: pd.Timestamp | None = None
    rows: list[dict[str, float | int | str]] = []

    for date, signal in signals.items():
        if signal == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            entry_date = date
            continue

        if signal == "VENDI" and exposure > 0.0 and entry_date is not None:
            exit_iso = date.date().isoformat()
            exit_type = "trail8_confirmed" if exit_iso in forced_exit_dates else "official"
            rows.append(_trade_row(df, model, len(rows) + 1, entry_date, date, exit_type=exit_type))
            exposure = 0.0
            entry_date = None

    return pd.DataFrame(rows)


def _overlapping_baseline_trade(baseline: pd.DataFrame, entry_date: str, exit_date: str) -> pd.Series | None:
    start = pd.Timestamp(entry_date)
    end = pd.Timestamp(exit_date)
    base = baseline.copy()
    base["entry_ts"] = pd.to_datetime(base["entry_date"])
    base["exit_ts"] = pd.to_datetime(base["exit_date"])
    overlaps = base[(base["entry_ts"] <= end) & (base["exit_ts"] >= start)].copy()
    if overlaps.empty:
        return None
    overlaps["overlap_days"] = overlaps.apply(
        lambda r: (min(end, r["exit_ts"]) - max(start, r["entry_ts"])).days,
        axis=1,
    )
    return overlaps.sort_values("overlap_days", ascending=False).iloc[0]


def _add_comparison(candidate: pd.DataFrame, baseline: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for _, row in candidate.iterrows():
        out = row.to_dict()
        ref = _overlapping_baseline_trade(baseline, str(row["entry_date"]), str(row["exit_date"]))
        if ref is None:
            out.update(
                {
                    "baseline_ref_trade_id": "",
                    "baseline_ref_entry_date": "",
                    "baseline_ref_exit_date": "",
                    "baseline_ref_return": float("nan"),
                    "baseline_ref_drawdown": float("nan"),
                    "return_delta_vs_baseline": float("nan"),
                    "drawdown_avoided_vs_baseline": float("nan"),
                }
            )
        else:
            out.update(
                {
                    "baseline_ref_trade_id": int(ref["trade_id"]),
                    "baseline_ref_entry_date": ref["entry_date"],
                    "baseline_ref_exit_date": ref["exit_date"],
                    "baseline_ref_return": float(ref["trade_return"]),
                    "baseline_ref_drawdown": float(ref["drawdown_suffered_pct"]),
                    "return_delta_vs_baseline": float(row["trade_return"]) - float(ref["trade_return"]),
                    "drawdown_avoided_vs_baseline": float(row["drawdown_suffered_pct"])
                    - float(ref["drawdown_suffered_pct"]),
                }
            )
        rows.append(out)
    return pd.DataFrame(rows)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _price(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.2f}"


def _summary_lines(frames: dict[str, pd.DataFrame]) -> list[str]:
    lines = [
        "| Modello | Ann. | Max DD sistema | Sharpe | PF | Operazioni | Win rate |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for model, frame in frames.items():
        _, metrics, _ = run_backtest(frame)
        lines.append(
            "| "
            f"{model} | "
            f"{_pct(metrics.annualized_return)} | "
            f"{_pct(metrics.max_drawdown)} | "
            f"{metrics.sharpe_ratio:.3f} | "
            f"{metrics.profit_factor:.3f} | "
            f"{metrics.num_operations} | "
            f"{_pct(metrics.win_rate)} |"
        )
    return lines


def _trade_table(lines: list[str], title: str, trades: pd.DataFrame, include_comparison: bool) -> None:
    lines.extend(
        [
            f"## {title}",
            "",
            "| # | Ingresso | Prezzo in | Uscita | Prezzo out | Tipo uscita | Gain | Loss | DD subito | Max gain | DD evitato vs Baseline | Delta return vs Baseline | Rif. Baseline |",
            "|---:|---|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for _, row in trades.iterrows():
        ref = ""
        dd_avoided = 0.0
        return_delta = 0.0
        if include_comparison:
            ref = f"{row['baseline_ref_entry_date']} -> {row['baseline_ref_exit_date']}"
            dd_avoided = row["drawdown_avoided_vs_baseline"]
            return_delta = row["return_delta_vs_baseline"]
        lines.append(
            "| "
            f"{int(row['trade_id'])} | "
            f"{row['entry_date']} | "
            f"{_price(row['entry_price_eur'])} | "
            f"{row['exit_date']} | "
            f"{_price(row['exit_price_eur'])} | "
            f"{row['exit_type']} | "
            f"{_pct(row['gain_pct'])} | "
            f"{_pct(row['loss_pct'])} | "
            f"{_pct(row['drawdown_suffered_pct'])} | "
            f"{_pct(row['max_gain_pct'])} | "
            f"{_pct(dd_avoided)} | "
            f"{_pct(return_delta)} | "
            f"{ref} |"
        )
    lines.append("")


def _write_markdown(
    baseline: pd.DataFrame,
    candidate: pd.DataFrame,
    frames: dict[str, pd.DataFrame],
    out_path: Path,
    start_date: str,
    end_date: str,
) -> None:
    identical_pairs = set(zip(baseline["entry_date"], baseline["exit_date"])) & set(
        zip(candidate["entry_date"], candidate["exit_date"])
    )
    forced = candidate[candidate["exit_type"] == "trail8_confirmed"]
    improved = candidate[candidate["drawdown_avoided_vs_baseline"] > 0.0]

    lines = [
        "# Exit Trade Comparison",
        "",
        f"Periodo: `{start_date}` -> `{end_date}`.",
        "",
        "Confronto completo tra operazioni Baseline e operazioni del candidato uscita `Trail8 confermato -5 / vol +20`.",
        "Gli ingressi restano quelli Baseline ufficiali. Nessun segnale ufficiale viene modificato.",
        "",
        "## Sintesi Sistema",
        "",
        *_summary_lines(frames),
        "",
        "## Sintesi Operazioni",
        "",
        f"- Operazioni Baseline: {len(baseline)}.",
        f"- Operazioni candidato: {len(candidate)}.",
        f"- Operazioni identiche per ingresso e uscita: {len(identical_pairs)}.",
        f"- Uscite anticipate Trail8 confermate: {len(forced)}.",
        f"- Operazioni candidato con drawdown minore del riferimento Baseline: {len(improved)}.",
        "",
        "Nota: `DD evitato vs Baseline` positivo significa che il trade candidato ha subito meno drawdown del trade Baseline sovrapposto.",
        "",
    ]

    _trade_table(lines, "Operazioni Baseline", baseline, include_comparison=False)
    _trade_table(lines, "Operazioni Candidato Trail8 -5 / Vol +20", candidate, include_comparison=True)

    lines.extend(
        [
            "## Lettura",
            "",
            "- Questo report e' il confronto corretto operazione-per-operazione.",
            "- Le 6 uscite anticipate non sono tutte le operazioni: modificano 6 trade Baseline e generano 8 trade diversi nel candidato.",
            "- Le valutazioni sul candidato uscita vanno fatte da questa tabella, non solo dall'audit delle sole uscite anticipate.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    df = df.loc[: pd.Timestamp(END_DATE)].copy()
    if df.empty:
        raise ValueError(f"Nessuna candela disponibile fino a {END_DATE}.")

    baseline_frame = _baseline_frame(df)
    candidate_frame, forced_exit_dates = _candidate_frame(df)
    baseline = _trades_from_signals(df, baseline_frame["Segnale"], "Baseline ufficiale")
    candidate_raw = _trades_from_signals(
        df,
        candidate_frame["Segnale"],
        "Trail8 -5 / vol +20",
        forced_exit_dates,
    )
    candidate = _add_comparison(candidate_raw, baseline)
    all_trades = pd.concat([baseline, candidate], ignore_index=True)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    all_trades.to_csv(OUT_CSV, index=False)
    _write_markdown(
        baseline,
        candidate,
        {
            "Baseline ufficiale": baseline_frame,
            "Trail8 -5 / vol +20": candidate_frame,
        },
        OUT_MD,
        df.index[0].date().isoformat(),
        df.index[-1].date().isoformat(),
    )
    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_MD}")
    print("Baseline trades:", len(baseline))
    print("Candidate trades:", len(candidate))
    print(candidate[["trade_id", "entry_date", "entry_price_eur", "exit_date", "exit_price_eur", "exit_type", "trade_return", "drawdown_suffered_pct", "drawdown_avoided_vs_baseline", "return_delta_vs_baseline", "baseline_ref_trade_id"]].to_string(index=False))


if __name__ == "__main__":
    main()
