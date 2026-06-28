"""
Impatto netto dei segmenti modificati dal candidato uscita Trail8 -5 / vol +20.

Un segmento e' un trade Baseline originale che viene modificato dal candidato.
Il confronto avviene tra:
- trade Baseline completo;
- sequenza completa di trade candidato sovrapposti allo stesso segmento.

Questo script non modifica i segnali ufficiali.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


SOURCE_CSV = PROJECT_ROOT / "data" / "indicators_with_signals.csv"
OUT_CSV = PROJECT_ROOT / "reports" / "exit_segment_impact.csv"
OUT_MD = PROJECT_ROOT / "reports" / "exit_segment_impact.md"

END_DATE = "2026-06-27"
STOP_PCT = 0.08
MOMENTUM_MIN = -0.05
VOLUME_REL_MIN = 0.20


def _candidate_signals(df: pd.DataFrame) -> tuple[pd.Series, set[str]]:
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
            if close <= peak_close * (1.0 - STOP_PCT):
                momentum_7d = close / float(row["Close_7d_ago"]) - 1.0
                volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
                if momentum_7d >= MOMENTUM_MIN and volume_rel >= VOLUME_REL_MIN:
                    signal = "VENDI"
                    forced_exit_dates.add(date.date().isoformat())
                    exposure = 0.0
                    peak_close = None

        signals.append(signal)

    return pd.Series(signals, index=df.index), forced_exit_dates


def _trades(df: pd.DataFrame, signals: pd.Series, forced_exit_dates: set[str] | None = None) -> pd.DataFrame:
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
            exit_type = "trail8_confirmed" if date.date().isoformat() in forced_exit_dates else "official"
            rows.append(_trade_row(df, len(rows) + 1, entry_date, date, exit_type))
            exposure = 0.0
            entry_date = None

    return pd.DataFrame(rows)


def _trade_row(
    df: pd.DataFrame,
    trade_id: int,
    entry_date: pd.Timestamp,
    exit_date: pd.Timestamp,
    exit_type: str,
) -> dict[str, float | int | str]:
    entry_price = float(df.loc[entry_date, "Close_EUR"])
    exit_price = float(df.loc[exit_date, "Close_EUR"])
    path = df.loc[entry_date:exit_date, "Close_EUR"]
    normalized = path / entry_price
    drawdown = normalized / normalized.cummax() - 1.0
    return {
        "trade_id": trade_id,
        "entry_date": entry_date.date().isoformat(),
        "exit_date": exit_date.date().isoformat(),
        "entry_price_eur": entry_price,
        "exit_price_eur": exit_price,
        "exit_type": exit_type,
        "trade_return": exit_price / entry_price - 1.0,
        "drawdown_suffered_pct": float(drawdown.min()),
        "max_gain_pct": float(normalized.max() - 1.0),
    }


def _baseline_segments_modified(baseline: pd.DataFrame, candidate: pd.DataFrame) -> pd.DataFrame:
    base_pairs = set(zip(baseline["entry_date"], baseline["exit_date"]))
    candidate_pairs = set(zip(candidate["entry_date"], candidate["exit_date"]))
    changed_pairs = base_pairs - candidate_pairs
    return baseline[
        baseline.apply(lambda r: (r["entry_date"], r["exit_date"]) in changed_pairs, axis=1)
    ].copy()


def _candidate_trades_for_segment(candidate: pd.DataFrame, segment: pd.Series) -> pd.DataFrame:
    start = pd.Timestamp(segment["entry_date"])
    end = pd.Timestamp(segment["exit_date"])
    trades = candidate.copy()
    trades["entry_ts"] = pd.to_datetime(trades["entry_date"])
    trades["exit_ts"] = pd.to_datetime(trades["exit_date"])
    return trades[(trades["entry_ts"] >= start) & (trades["exit_ts"] <= end)].copy()


def _compound_return(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    return float((1.0 + returns).prod() - 1.0)


def _segment_rows(baseline: pd.DataFrame, candidate: pd.DataFrame) -> pd.DataFrame:
    segments = _baseline_segments_modified(baseline, candidate)
    rows: list[dict[str, float | int | str]] = []

    for idx, segment in segments.reset_index(drop=True).iterrows():
        candidate_segment = _candidate_trades_for_segment(candidate, segment)
        candidate_return = _compound_return(candidate_segment["trade_return"])
        candidate_min_dd = float(candidate_segment["drawdown_suffered_pct"].min()) if not candidate_segment.empty else 0.0
        candidate_trades = "; ".join(
            f"{r.entry_date}->{r.exit_date} ({r.exit_type}, {r.trade_return * 100:.2f}%)"
            for r in candidate_segment.itertuples()
        )
        forced_count = int((candidate_segment["exit_type"] == "trail8_confirmed").sum())
        official_count = int((candidate_segment["exit_type"] == "official").sum())

        rows.append(
            {
                "segment_id": int(idx + 1),
                "baseline_entry": segment["entry_date"],
                "baseline_exit": segment["exit_date"],
                "baseline_entry_price_eur": segment["entry_price_eur"],
                "baseline_exit_price_eur": segment["exit_price_eur"],
                "baseline_return": segment["trade_return"],
                "baseline_drawdown": segment["drawdown_suffered_pct"],
                "baseline_max_gain": segment["max_gain_pct"],
                "candidate_trades_count": int(len(candidate_segment)),
                "candidate_forced_exits": forced_count,
                "candidate_official_exits": official_count,
                "candidate_return": candidate_return,
                "candidate_worst_trade_drawdown": candidate_min_dd,
                "drawdown_avoided": candidate_min_dd - float(segment["drawdown_suffered_pct"]),
                "return_delta": candidate_return - float(segment["trade_return"]),
                "candidate_trades": candidate_trades,
            }
        )
    return pd.DataFrame(rows)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _price(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.2f}"


def _write_markdown(segments: pd.DataFrame, out_path: Path, start_date: str, end_date: str) -> None:
    total_baseline = _compound_return(segments["baseline_return"])
    total_candidate = _compound_return(segments["candidate_return"])
    useful = segments[segments["return_delta"] > 0.0]
    harmful = segments[segments["return_delta"] < 0.0]

    lines = [
        "# Exit Segment Impact",
        "",
        f"Periodo: `{start_date}` -> `{end_date}`.",
        "",
        "Confronto dei soli segmenti Baseline modificati dal candidato uscita `Trail8 confermato -5 / vol +20`.",
        "Un segmento e' un trade Baseline originale; il candidato puo' spezzarlo in uno o piu' trade.",
        "",
        "## Sintesi",
        "",
        f"- Segmenti modificati: {len(segments)}.",
        f"- Segmenti con delta rendimento positivo: {len(useful)}.",
        f"- Segmenti con delta rendimento negativo: {len(harmful)}.",
        f"- Rendimento composto Baseline sui segmenti: {_pct(total_baseline)}.",
        f"- Rendimento composto candidato sui segmenti: {_pct(total_candidate)}.",
        f"- Delta composto candidato - Baseline: {_pct(total_candidate - total_baseline)}.",
        "",
        "## Segmenti",
        "",
        "| # | Segmento Baseline | Return Baseline | DD Baseline | Trade candidato | Return candidato | DD candidato | DD evitato | Delta return | Lettura |",
        "|---:|---|---:|---:|---|---:|---:|---:|---:|---|",
    ]
    for _, row in segments.iterrows():
        if row["return_delta"] > 0.0 and row["drawdown_avoided"] > 0.0:
            reading = "migliora rendimento e DD"
        elif row["return_delta"] > 0.0:
            reading = "migliora rendimento"
        elif row["drawdown_avoided"] > 0.0:
            reading = "riduce DD ma peggiora rendimento"
        else:
            reading = "peggiora"
        lines.append(
            "| "
            f"{int(row['segment_id'])} | "
            f"{row['baseline_entry']} -> {row['baseline_exit']} "
            f"({_price(row['baseline_entry_price_eur'])} -> {_price(row['baseline_exit_price_eur'])}) | "
            f"{_pct(row['baseline_return'])} | "
            f"{_pct(row['baseline_drawdown'])} | "
            f"{row['candidate_trades']} | "
            f"{_pct(row['candidate_return'])} | "
            f"{_pct(row['candidate_worst_trade_drawdown'])} | "
            f"{_pct(row['drawdown_avoided'])} | "
            f"{_pct(row['return_delta'])} | "
            f"{reading} |"
        )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            "- Questo e' il livello corretto per valutare le modifiche prodotte dall'uscita candidata.",
            "- Se un'uscita anticipata genera un rientro, il segmento valuta la sequenza completa.",
            "- Il candidato e' interessante solo se il saldo di segmento migliora rendimento e/o drawdown senza introdurre danni ricorrenti.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    df = df.loc[: pd.Timestamp(END_DATE)].copy()
    baseline = _trades(df, df["Segnale"])
    candidate_signals, forced = _candidate_signals(df)
    candidate = _trades(df, candidate_signals, forced)
    segments = _segment_rows(baseline, candidate)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    segments.to_csv(OUT_CSV, index=False)
    _write_markdown(segments, OUT_MD, df.index[0].date().isoformat(), df.index[-1].date().isoformat())
    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_MD}")
    print(segments[["segment_id", "baseline_entry", "baseline_exit", "baseline_return", "candidate_return", "drawdown_avoided", "return_delta", "candidate_trades_count"]].to_string(index=False))


if __name__ == "__main__":
    main()
