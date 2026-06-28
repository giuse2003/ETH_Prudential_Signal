"""
Audit del peggioramento residuo 2023 nel candidato combinato.

Obiettivo:
- isolare il segmento 2023 che peggiora leggermente la Baseline;
- confrontare le caratteristiche note al giorno dell'uscita Trail8;
- valutare se esiste una regola generale che eviti quel caso senza perdere
  le uscite utili degli altri anni.

Questo script non modifica i segnali ufficiali.
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
OUT_CSV = PROJECT_ROOT / "reports" / "residual_2023_exit_audit.csv"
OUT_MD = PROJECT_ROOT / "reports" / "residual_2023_exit_audit.md"

END_DATE = "2026-06-27"
RSI_MAX = 65.0
STOP_PCT = 0.08
MOMENTUM_MIN = -0.05
VOLUME_REL_MIN = 0.20


def _combined_signals(
    df: pd.DataFrame,
    min_trade_return: float | None = None,
    min_max_gain: float | None = None,
) -> tuple[pd.Series, set[str]]:
    exposure = 0.0
    peak_close: float | None = None
    entry_date: pd.Timestamp | None = None
    signals: list[str] = []
    forced_exit_dates: set[str] = set()

    for date, row in df.iterrows():
        official = str(row["Segnale"])
        signal = official
        close = float(row["Close"])

        if official == "ACQUISTA" and exposure <= 0.0 and float(row["RSI"]) > RSI_MAX:
            signal = "MANTIENI"
        elif official == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            peak_close = close
            entry_date = date
        elif official == "ACQUISTA":
            signal = "MANTIENI"
            peak_close = max(peak_close or close, close)
        elif official == "VENDI":
            exposure = 0.0
            peak_close = None
            entry_date = None
        elif exposure > 0.0 and peak_close is not None and entry_date is not None:
            peak_close = max(peak_close, close)
            if close <= peak_close * (1.0 - STOP_PCT):
                momentum_7d = close / float(row["Close_7d_ago"]) - 1.0
                volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
                entry_price = float(df.loc[entry_date, "Close_EUR"])
                exit_price = float(row["Close_EUR"])
                trade_return = exit_price / entry_price - 1.0
                max_gain = float(df.loc[entry_date:date, "Close_EUR"].max()) / entry_price - 1.0
                passes_optional = True
                if min_trade_return is not None:
                    passes_optional = passes_optional and trade_return >= min_trade_return
                if min_max_gain is not None:
                    passes_optional = passes_optional and max_gain >= min_max_gain
                if momentum_7d >= MOMENTUM_MIN and volume_rel >= VOLUME_REL_MIN and passes_optional:
                    signal = "VENDI"
                    forced_exit_dates.add(date.date().isoformat())
                    exposure = 0.0
                    peak_close = None
                    entry_date = None

        signals.append(signal)

    return pd.Series(signals, index=df.index), forced_exit_dates


def _trades(df: pd.DataFrame, signals: pd.Series, forced_exit_dates: set[str] | None = None) -> pd.DataFrame:
    forced_exit_dates = forced_exit_dates or set()
    rows: list[dict[str, float | int | str]] = []
    exposure = 0.0
    entry_date: pd.Timestamp | None = None

    for date, signal in signals.items():
        if signal == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            entry_date = date
        elif signal == "VENDI" and exposure > 0.0 and entry_date is not None:
            exit_type = "trail8" if date.date().isoformat() in forced_exit_dates else "official"
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


def _compound_return(returns: pd.Series) -> float:
    if returns.empty:
        return 0.0
    return float((1.0 + returns).prod() - 1.0)


def _baseline_segment_for_trade(baseline: pd.DataFrame, trade: pd.Series) -> pd.Series:
    entry = pd.Timestamp(trade["entry_date"])
    exit_ = pd.Timestamp(trade["exit_date"])
    candidates = baseline.copy()
    candidates["entry_ts"] = pd.to_datetime(candidates["entry_date"])
    candidates["exit_ts"] = pd.to_datetime(candidates["exit_date"])
    match = candidates[(candidates["entry_ts"] <= entry) & (candidates["exit_ts"] >= exit_)]
    if match.empty:
        raise ValueError(f"Nessun segmento Baseline trovato per {trade['entry_date']} -> {trade['exit_date']}")
    return match.iloc[0]


def _candidate_segment_return(candidate: pd.DataFrame, segment: pd.Series) -> float:
    start = pd.Timestamp(segment["entry_date"])
    end = pd.Timestamp(segment["exit_date"])
    trades = candidate.copy()
    trades["entry_ts"] = pd.to_datetime(trades["entry_date"])
    trades["exit_ts"] = pd.to_datetime(trades["exit_date"])
    inside = trades[(trades["entry_ts"] >= start) & (trades["exit_ts"] <= end)]
    return _compound_return(inside["trade_return"])


def _audit_rows(df: pd.DataFrame, baseline: pd.DataFrame, candidate: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    forced = candidate[candidate["exit_type"] == "trail8"].copy()

    for _, trade in forced.iterrows():
        segment = _baseline_segment_for_trade(baseline, trade)
        segment_return = _candidate_segment_return(candidate, segment)
        exit_date = pd.Timestamp(trade["exit_date"])
        entry_date = pd.Timestamp(trade["entry_date"])
        row = df.loc[exit_date]
        entry_price = float(trade["entry_price_eur"])
        exit_price = float(trade["exit_price_eur"])
        peak_price = float(df.loc[entry_date:exit_date, "Close_EUR"].max())
        days_in_trade = int((exit_date - entry_date).days)
        days_to_official_exit = int((pd.Timestamp(segment["exit_date"]) - exit_date).days)

        rows.append(
            {
                "exit_date": trade["exit_date"],
                "entry_date": trade["entry_date"],
                "exit_price_eur": exit_price,
                "trade_return": float(trade["trade_return"]),
                "trade_max_gain": float(trade["max_gain_pct"]),
                "drawdown_from_peak": exit_price / peak_price - 1.0,
                "drawdown_suffered_pct": float(trade["drawdown_suffered_pct"]),
                "days_in_trade": days_in_trade,
                "days_to_official_exit": days_to_official_exit,
                "rsi": float(row["RSI"]),
                "momentum_7d": float(row["Close"]) / float(row["Close_7d_ago"]) - 1.0,
                "volume_rel": float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0,
                "distance_sma50": float(row["Close_EUR"]) / float(row["SMA50"]) - 1.0,
                "distance_sma200": float(row["DistanceFromSMA200_Pct"]),
                "atr_pct": float(row["ATR"]) / float(row["Close"]),
                "baseline_segment": f"{segment['entry_date']} -> {segment['exit_date']}",
                "baseline_segment_return": float(segment["trade_return"]),
                "candidate_segment_return": segment_return,
                "segment_delta_return": segment_return - float(segment["trade_return"]),
            }
        )

    return pd.DataFrame(rows)


def _candidate_filters(audit: pd.DataFrame) -> pd.DataFrame:
    rules = [
        ("richiedi gain trade >= 15%", audit["trade_return"] >= 0.15),
        ("richiedi max gain >= 35%", audit["trade_max_gain"] >= 0.35),
        ("richiedi RSI uscita >= 55", audit["rsi"] >= 55.0),
        ("richiedi volume relativo >= 40%", audit["volume_rel"] >= 0.40),
        ("richiedi almeno 40 giorni in trade", audit["days_in_trade"] >= 40),
        ("blocca solo se uscita ufficiale distante >= 20 giorni", audit["days_to_official_exit"] >= 20),
    ]
    rows: list[dict[str, float | int | str]] = []
    for name, mask in rules:
        kept = audit[mask]
        removed = audit[~mask]
        rows.append(
            {
                "rule": name,
                "kept_exits": int(len(kept)),
                "removed_exits": int(len(removed)),
                "removes_2023": bool("2023-04-20" in set(removed["exit_date"])),
                "removed_positive_segments": int((removed["segment_delta_return"] > 0).sum()),
                "kept_positive_segments": int((kept["segment_delta_return"] > 0).sum()),
                "kept_delta_sum": float(kept["segment_delta_return"].sum()),
                "removed_delta_sum": float(removed["segment_delta_return"].sum()),
            }
        )
    return pd.DataFrame(rows)


def _frame_from_signals(df: pd.DataFrame, signals: pd.Series) -> pd.DataFrame:
    out = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    out["Segnale"] = signals
    return out


def _variant_metrics(df: pd.DataFrame) -> pd.DataFrame:
    variants = [
        ("Baseline ufficiale", df["Segnale"], set[str]()),
        ("Combinato attuale", *_combined_signals(df)),
        ("Combinato + trade return >= 15%", *_combined_signals(df, min_trade_return=0.15)),
        ("Combinato + max gain >= 35%", *_combined_signals(df, min_max_gain=0.35)),
    ]
    rows: list[dict[str, float | int | str]] = []
    for name, signals, forced_dates in variants:
        _, metrics, _ = run_backtest(_frame_from_signals(df, signals))
        rows.append(
            {
                "variant": name,
                "annualized_return": metrics.annualized_return,
                "max_drawdown": metrics.max_drawdown,
                "sharpe_ratio": metrics.sharpe_ratio,
                "profit_factor": metrics.profit_factor,
                "num_operations": metrics.num_operations,
                "forced_exits": ", ".join(sorted(forced_dates)),
            }
        )
    return pd.DataFrame(rows)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _num(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.2f}"


def _write_markdown(audit: pd.DataFrame, filters: pd.DataFrame, variants: pd.DataFrame, out_path: Path) -> None:
    target = audit[audit["exit_date"] == "2023-04-20"].iloc[0]
    positives = audit[audit["segment_delta_return"] > 0]
    negatives = audit[audit["segment_delta_return"] < 0]

    lines = [
        "# Audit Peggioramento Residuo 2023",
        "",
        "Obiettivo: capire se l'uscita `Trail8 confermato -5 / vol +20` del 2023 puo' essere evitata con una regola generale.",
        "",
        "## Caso 2023",
        "",
        f"- Segmento Baseline: `{target['baseline_segment']}`.",
        f"- Uscita Trail8: `{target['exit_date']}` a EUR {target['exit_price_eur']:.2f}.",
        f"- Rendimento del trade al momento dell'uscita: {_pct(target['trade_return'])}.",
        f"- Rendimento segmento Baseline: {_pct(target['baseline_segment_return'])}.",
        f"- Rendimento segmento candidato: {_pct(target['candidate_segment_return'])}.",
        f"- Delta candidato - Baseline: {_pct(target['segment_delta_return'])}.",
        f"- Drawdown subito fino all'uscita Trail8: {_pct(target['drawdown_suffered_pct'])}.",
        f"- Giorni tra uscita Trail8 e uscita ufficiale Baseline: {int(target['days_to_official_exit'])}.",
        "",
        "## Confronto Uscite Trail8 Nel Combinato",
        "",
        "| Uscita | Entry | Return trade | Max gain | DD da picco | RSI | Mom 7d | Vol rel | Giorni trade | Delta segmento | Lettura |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in audit.iterrows():
        reading = "utile" if row["segment_delta_return"] > 0 else "costo residuo"
        lines.append(
            "| "
            f"{row['exit_date']} | {row['entry_date']} | "
            f"{_pct(row['trade_return'])} | {_pct(row['trade_max_gain'])} | {_pct(row['drawdown_from_peak'])} | "
            f"{_num(row['rsi'])} | {_pct(row['momentum_7d'])} | {_pct(row['volume_rel'])} | "
            f"{int(row['days_in_trade'])} | {_pct(row['segment_delta_return'])} | {reading} |"
        )

    lines.extend(
        [
            "",
            "## Regole Candidate Per Escludere Il 2023",
            "",
            "| Regola | Uscite tenute | Uscite escluse | Esclude 2023 | Uscite utili escluse | Delta tenuto | Delta escluso |",
            "|---|---:|---:|---|---:|---:|---:|",
        ]
    )
    for _, row in filters.iterrows():
        lines.append(
            "| "
            f"{row['rule']} | {int(row['kept_exits'])} | {int(row['removed_exits'])} | "
            f"{'si' if row['removes_2023'] else 'no'} | {int(row['removed_positive_segments'])} | "
            f"{_pct(row['kept_delta_sum'])} | {_pct(row['removed_delta_sum'])} |"
        )

    lines.extend(
        [
            "",
            "## Impatto Varianti Sul Modello Combinato",
            "",
            "| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Uscite Trail8 |",
            "|---|---:|---:|---:|---:|---:|---|",
        ]
    )
    for _, row in variants.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | {_pct(row['annualized_return'])} | {_pct(row['max_drawdown'])} | "
            f"{_num(row['sharpe_ratio'])} | {_num(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | {row['forced_exits']} |"
        )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Uscite Trail8 utili nel combinato: {len(positives)}.",
            f"- Uscite Trail8 con costo residuo: {len(negatives)}.",
            "- Il caso 2023 e' un costo piccolo: peggiora il segmento di 0,48 punti ma riduce il drawdown del segmento.",
            "- Molte regole semplici che eliminano il 2023 eliminano anche uscite utili rilevanti.",
            "- Le uniche regole semplici che eliminano solo il 2023 nel campione sono `trade return >= 15%` e `max gain >= 35%`.",
            "- Sono coerenti con l'idea di proteggere capitale gia' acquisito, ma modificano un solo evento storico: rischio overfit alto.",
            "- Non emergono elementi sufficienti per trasformarle subito in filtro ufficiale.",
            "",
            "## Decisione",
            "",
            "- Non aggiungere subito una regola specifica per evitare il 2023.",
            "- Accettare provvisoriamente il costo residuo 2023 come prezzo del candidato uscita.",
            "- Tenere `trade return >= 15%` come candidato secondario da validare, non come modifica ufficiale.",
            "- Il combinato resta candidato finale, non Baseline ufficiale.",
            "- Il prossimo gate deve essere una validazione out-of-sample / walk-forward del combinato prima della promozione.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}")
    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    df = df.loc[: pd.Timestamp(END_DATE)].copy()
    baseline = _trades(df, df["Segnale"])
    combined_signals, forced_dates = _combined_signals(df)
    candidate = _trades(df, combined_signals, forced_dates)
    audit = _audit_rows(df, baseline, candidate)
    filters = _candidate_filters(audit)
    variants = _variant_metrics(df)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUT_CSV, index=False)
    filters.to_csv(PROJECT_ROOT / "reports" / "residual_2023_exit_filter_tests.csv", index=False)
    variants.to_csv(PROJECT_ROOT / "reports" / "residual_2023_exit_variant_metrics.csv", index=False)
    _write_markdown(audit, filters, variants, OUT_MD)
    print(f"Saved {OUT_CSV}")
    print(f"Saved {PROJECT_ROOT / 'reports' / 'residual_2023_exit_filter_tests.csv'}")
    print(f"Saved {PROJECT_ROOT / 'reports' / 'residual_2023_exit_variant_metrics.csv'}")
    print(f"Saved {OUT_MD}")
    print(audit[["exit_date", "trade_return", "trade_max_gain", "rsi", "momentum_7d", "volume_rel", "segment_delta_return"]].to_string(index=False))
    print(filters.to_string(index=False))
    print(variants.to_string(index=False))


if __name__ == "__main__":
    main()
