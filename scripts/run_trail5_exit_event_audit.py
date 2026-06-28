"""
Audit evento-per-evento del candidato uscita Trail8 confermato -5 / vol +20.

Questo script non modifica i segnali ufficiali. Mantiene invariati gli ingressi
Baseline e analizza solo le uscite forzate dal candidato:
- trailing stop 8% sul massimo Close post-ingresso;
- conferma momentum 7g >= -5%;
- conferma volume relativo >= +20%.

Le performance sono misurate in EUR tramite Close_EUR.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


SOURCE_CSV = PROJECT_ROOT / "data" / "indicators_with_signals.csv"
OUT_CSV = PROJECT_ROOT / "reports" / "trail5_exit_event_audit.csv"
OUT_MD = PROJECT_ROOT / "reports" / "trail5_exit_event_audit.md"

END_DATE = "2026-06-27"
STOP_PCT = 0.08
MOMENTUM_MIN = -0.05
VOLUME_REL_MIN = 0.20


def _next_official_buy(df: pd.DataFrame, date: pd.Timestamp) -> pd.Timestamp | None:
    future = df.loc[df.index > date]
    buys = future[future["Segnale"] == "ACQUISTA"]
    return None if buys.empty else buys.index[0]


def _audit(df: pd.DataFrame) -> pd.DataFrame:
    exposure = 0.0
    peak_close: float | None = None
    entry_date: pd.Timestamp | None = None
    events: list[dict[str, float | int | str | bool]] = []

    for date, row in df.iterrows():
        official = str(row["Segnale"])
        close_usd = float(row["Close"])
        close_eur = float(row["Close_EUR"])

        if official == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            peak_close = close_usd
            entry_date = date
            continue

        if official == "ACQUISTA" and exposure > 0.0:
            peak_close = max(peak_close or close_usd, close_usd)
            continue

        if official == "VENDI":
            exposure = 0.0
            peak_close = None
            entry_date = None
            continue

        if exposure <= 0.0 or peak_close is None or entry_date is None:
            continue

        peak_close = max(peak_close, close_usd)
        stop_level = peak_close * (1.0 - STOP_PCT)
        if close_usd > stop_level:
            continue

        momentum_7d = close_usd / float(row["Close_7d_ago"]) - 1.0
        volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
        confirmed = momentum_7d >= MOMENTUM_MIN and volume_rel >= VOLUME_REL_MIN
        if not confirmed:
            continue

        next_buy_date = _next_official_buy(df, date)
        next_buy_price = float(df.loc[next_buy_date, "Close_EUR"]) if next_buy_date is not None else float("nan")

        entry_price = float(df.loc[entry_date, "Close_EUR"])
        trade_path = df.loc[entry_date:date, "Close_EUR"]
        trade_norm = trade_path / entry_price
        trade_dd = trade_norm / trade_norm.cummax() - 1.0
        trade_return = close_eur / entry_price - 1.0

        if next_buy_date is not None:
            post_path = df.loc[date:next_buy_date, "Close_EUR"]
        else:
            post_path = df.loc[date:, "Close_EUR"]

        post_return_from_exit = post_path / close_eur - 1.0
        post_min_return = float(post_return_from_exit.min())
        post_max_return = float(post_return_from_exit.max())
        drawdown_avoided = max(0.0, -post_min_return)
        missed_upside = max(0.0, post_max_return)
        reentry_vs_exit = next_buy_price / close_eur - 1.0 if next_buy_date is not None else float("nan")

        if drawdown_avoided >= 0.03 and drawdown_avoided > missed_upside:
            classification = "utile"
        elif reentry_vs_exit > 0.0 and missed_upside > drawdown_avoided:
            classification = "dannosa"
        else:
            classification = "neutra"

        events.append(
            {
                "exit_date": date.date().isoformat(),
                "exit_price_eur": close_eur,
                "entry_date": entry_date.date().isoformat(),
                "entry_price_eur": entry_price,
                "trade_return_to_exit": trade_return,
                "trade_result": "positivo" if trade_return > 0.0 else "negativo",
                "drawdown_suffered_to_exit": float(trade_dd.min()),
                "peak_gain_to_exit": float(trade_norm.max() - 1.0),
                "next_entry_date": next_buy_date.date().isoformat() if next_buy_date is not None else "",
                "next_entry_price_eur": next_buy_price,
                "next_entry_vs_exit": reentry_vs_exit,
                "post_exit_min_return_until_reentry": post_min_return,
                "post_exit_max_return_until_reentry": post_max_return,
                "drawdown_avoided_until_reentry": drawdown_avoided,
                "missed_upside_until_reentry": missed_upside,
                "momentum_7d": momentum_7d,
                "volume_rel": volume_rel,
                "classification": classification,
            }
        )

        exposure = 0.0
        peak_close = None
        entry_date = None

    return pd.DataFrame(events)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _price(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.2f}"


def _write_markdown(events: pd.DataFrame, out_path: Path, start_date: str, end_date: str) -> None:
    positives = int((events["trade_return_to_exit"] > 0.0).sum()) if not events.empty else 0
    negatives = int((events["trade_return_to_exit"] <= 0.0).sum()) if not events.empty else 0
    useful = int((events["classification"] == "utile").sum()) if not events.empty else 0
    neutral = int((events["classification"] == "neutra").sum()) if not events.empty else 0
    harmful = int((events["classification"] == "dannosa").sum()) if not events.empty else 0

    lines = [
        "# Trail8 -5 / Vol +20 Exit Event Audit",
        "",
        f"Periodo: `{start_date}` -> `{end_date}`.",
        "",
        "Audit del candidato uscita `Trail8 confermato -5 / vol +20`.",
        "Gli ingressi restano quelli Baseline ufficiali. Nessun segnale ufficiale viene modificato.",
        "",
        "Definizioni:",
        "",
        "- `Return trade`: rendimento dall'ingresso precedente alla data di uscita forzata.",
        "- `DD subito`: peggior drawdown interno dal giorno di ingresso alla data di uscita forzata.",
        "- `DD evitato`: peggior discesa dal prezzo di uscita fino al rientro successivo; se il prezzo non scende, vale 0.",
        "- `Upside perso`: massimo rialzo dal prezzo di uscita fino al rientro successivo.",
        "",
        "## Sintesi",
        "",
        f"- Uscite forzate: {len(events)}.",
        f"- Uscite con trade positivo: {positives}.",
        f"- Uscite con trade negativo: {negatives}.",
        f"- Classificate utili: {useful}.",
        f"- Classificate neutre: {neutral}.",
        f"- Classificate dannose: {harmful}.",
        "",
        "## Eventi",
        "",
        "| Uscita | Prezzo uscita | Ingresso precedente | Prezzo ingresso | Return trade | Esito | DD subito | Rientro successivo | Prezzo rientro | Rientro vs uscita | DD evitato | Upside perso | Lettura |",
        "|---|---:|---|---:|---:|---|---:|---|---:|---:|---:|---:|---|",
    ]
    for _, row in events.iterrows():
        lines.append(
            "| "
            f"{row['exit_date']} | "
            f"{_price(row['exit_price_eur'])} | "
            f"{row['entry_date']} | "
            f"{_price(row['entry_price_eur'])} | "
            f"{_pct(row['trade_return_to_exit'])} | "
            f"{row['trade_result']} | "
            f"{_pct(row['drawdown_suffered_to_exit'])} | "
            f"{row['next_entry_date'] or 'n/a'} | "
            f"{_price(row['next_entry_price_eur'])} | "
            f"{_pct(row['next_entry_vs_exit'])} | "
            f"{_pct(row['drawdown_avoided_until_reentry'])} | "
            f"{_pct(row['missed_upside_until_reentry'])} | "
            f"{row['classification']} |"
        )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            "- Il candidato va giudicato sugli eventi, non solo sulla metrica aggregata.",
            "- Una buona uscita deve proteggere capitale gia' acquisito senza generare troppi rientri piu' alti.",
            "- Le uscite con rientro successivo piu' alto vanno considerate con cautela: possono migliorare il drawdown ma perdere rendimento.",
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

    events = _audit(df)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    events.to_csv(OUT_CSV, index=False)
    _write_markdown(events, OUT_MD, df.index[0].date().isoformat(), df.index[-1].date().isoformat())
    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_MD}")
    print(
        events[
            [
                "exit_date",
                "exit_price_eur",
                "entry_date",
                "entry_price_eur",
                "trade_return_to_exit",
                "drawdown_suffered_to_exit",
                "next_entry_date",
                "next_entry_price_eur",
                "next_entry_vs_exit",
                "drawdown_avoided_until_reentry",
                "missed_upside_until_reentry",
                "classification",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
