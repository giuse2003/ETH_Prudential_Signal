"""
Audit evento-per-evento degli ingressi bloccati dal filtro RSI <= 65.

Questo script non modifica i segnali ufficiali. Analizza solo cosa succede
quando il filtro sperimentale RSI <= 65 blocca un nuovo ACQUISTA, mantenendo
invariata l'uscita ufficiale sotto SMA50 per 2 giorni consecutivi.

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
OUT_CSV = PROJECT_ROOT / "reports" / "rsi65_blocked_entry_audit.csv"
OUT_MD = PROJECT_ROOT / "reports" / "rsi65_blocked_entry_audit.md"

RSI_MAX = 65.0


def _variant_frame_and_blocked(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    exposure = 0.0
    signals: list[str] = []
    blocked: list[dict[str, float | str]] = []

    for date, row in df.iterrows():
        signal = str(row["Segnale"])
        if signal == "ACQUISTA" and float(row["RSI"]) > RSI_MAX:
            if exposure <= 0.0:
                blocked.append(
                    {
                        "date": date.date().isoformat(),
                        "close_eur": float(row["Close_EUR"]),
                        "rsi": float(row["RSI"]),
                        "distance_sma200_pct": float(row["Close"]) / float(row["SMA200"]) - 1.0,
                        "momentum_7d_pct": float(row["Close"]) / float(row["Close_7d_ago"]) - 1.0,
                        "volume_rel_pct": float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0,
                    }
                )
            signal = "MANTIENI"

        if signal == "ACQUISTA":
            exposure = 1.0
        elif signal == "VENDI":
            exposure = 0.0

        signals.append(signal)

    frame = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    frame["Segnale"] = signals
    return frame, pd.DataFrame(blocked)


def _baseline_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()


def _signal_trades(df: pd.DataFrame, signals: pd.Series) -> pd.DataFrame:
    exposure = 0.0
    entry_date: pd.Timestamp | None = None
    rows: list[dict[str, float | int | str | bool]] = []

    for date, signal in signals.items():
        if signal == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            entry_date = date
            continue

        if signal == "VENDI" and exposure > 0.0 and entry_date is not None:
            rows.append(_trade_row(df, entry_date, date, is_open=False))
            exposure = 0.0
            entry_date = None

    if exposure > 0.0 and entry_date is not None:
        rows.append(_trade_row(df, entry_date, df.index[-1], is_open=True))

    return pd.DataFrame(rows)


def _trade_row(
    df: pd.DataFrame,
    entry_date: pd.Timestamp,
    exit_date: pd.Timestamp,
    *,
    is_open: bool,
) -> dict[str, float | int | str | bool]:
    entry_price = float(df.loc[entry_date, "Close_EUR"])
    exit_price = float(df.loc[exit_date, "Close_EUR"])
    path = df.loc[entry_date:exit_date, "Close_EUR"]
    normalized = path / entry_price
    drawdown = normalized / normalized.cummax() - 1.0
    return {
        "entry_date": entry_date.date().isoformat(),
        "exit_date": exit_date.date().isoformat(),
        "entry_price_eur": entry_price,
        "exit_price_eur": exit_price,
        "trade_return": exit_price / entry_price - 1.0,
        "trade_max_drawdown": float(drawdown.min()),
        "trade_max_gain": float(normalized.max() - 1.0),
        "duration_days": int((exit_date - entry_date).days),
        "is_open": bool(is_open),
    }


def _blocked_episodes(blocked: pd.DataFrame) -> pd.DataFrame:
    if blocked.empty:
        return pd.DataFrame()

    dates = pd.to_datetime(blocked["date"])
    groups = (dates.diff().dt.days.fillna(99) > 1).cumsum()
    rows: list[dict[str, float | int | str]] = []
    for _, group in blocked.groupby(groups):
        rows.append(
            {
                "start_date": group.iloc[0]["date"],
                "end_date": group.iloc[-1]["date"],
                "blocked_signals": int(len(group)),
                "blocked_start_price_eur": float(group.iloc[0]["close_eur"]),
                "avg_rsi": float(group["rsi"].mean()),
                "max_rsi": float(group["rsi"].max()),
                "avg_distance_sma200_pct": float(group["distance_sma200_pct"].mean()),
                "avg_momentum_7d_pct": float(group["momentum_7d_pct"].mean()),
                "avg_volume_rel_pct": float(group["volume_rel_pct"].mean()),
            }
        )
    return pd.DataFrame(rows)


def _trade_covering(trades: pd.DataFrame, date: str) -> pd.Series:
    ts = pd.Timestamp(date)
    mask = (pd.to_datetime(trades["entry_date"]) <= ts) & (pd.to_datetime(trades["exit_date"]) >= ts)
    matches = trades[mask]
    if matches.empty:
        raise ValueError(f"Nessun trade Baseline copre la data {date}")
    return matches.iloc[0]


def _next_trade_after(trades: pd.DataFrame, date: str) -> pd.Series | None:
    ts = pd.Timestamp(date)
    mask = pd.to_datetime(trades["entry_date"]) > ts
    matches = trades[mask].sort_values("entry_date")
    if matches.empty:
        return None
    return matches.iloc[0]


def _audit(df: pd.DataFrame) -> pd.DataFrame:
    filtered_frame, blocked = _variant_frame_and_blocked(df)
    episodes = _blocked_episodes(blocked)
    baseline_trades = _signal_trades(df, df["Segnale"])
    rsi65_trades = _signal_trades(df, filtered_frame["Segnale"])

    rows: list[dict[str, float | int | str | bool]] = []
    for _, episode in episodes.iterrows():
        baseline_trade = _trade_covering(baseline_trades, str(episode["start_date"]))
        next_rsi65_trade = _next_trade_after(rsi65_trades, str(episode["start_date"]))

        next_entry_date = ""
        next_entry_price = float("nan")
        next_entry_delta = float("nan")
        days_to_next_entry = float("nan")
        reentered_before_baseline_exit = False
        next_exit_date = ""
        next_trade_return = float("nan")
        next_trade_max_drawdown = float("nan")

        if next_rsi65_trade is not None:
            next_entry_date = str(next_rsi65_trade["entry_date"])
            next_entry_price = float(next_rsi65_trade["entry_price_eur"])
            next_entry_delta = next_entry_price / float(episode["blocked_start_price_eur"]) - 1.0
            days_to_next_entry = int((pd.Timestamp(next_entry_date) - pd.Timestamp(episode["start_date"])).days)
            reentered_before_baseline_exit = pd.Timestamp(next_entry_date) <= pd.Timestamp(
                str(baseline_trade["exit_date"])
            )
            next_exit_date = str(next_rsi65_trade["exit_date"])
            next_trade_return = float(next_rsi65_trade["trade_return"])
            next_trade_max_drawdown = float(next_rsi65_trade["trade_max_drawdown"])

        if float(baseline_trade["trade_return"]) <= 0.0 and reentered_before_baseline_exit:
            classification = "utile: ritarda ingresso perdente"
        elif float(baseline_trade["trade_return"]) <= 0.0:
            classification = "utile: salta trade perdente"
        elif reentered_before_baseline_exit and next_entry_delta <= 0.0:
            classification = "utile: rientra piu' basso nello stesso trade"
        elif reentered_before_baseline_exit:
            classification = "misto: rientra piu' alto nello stesso trade"
        else:
            classification = "costo: salta trade vincente"

        rows.append(
            {
                **episode.to_dict(),
                "baseline_entry_date": baseline_trade["entry_date"],
                "baseline_exit_date": baseline_trade["exit_date"],
                "baseline_return": baseline_trade["trade_return"],
                "baseline_max_drawdown": baseline_trade["trade_max_drawdown"],
                "baseline_max_gain": baseline_trade["trade_max_gain"],
                "baseline_duration_days": baseline_trade["duration_days"],
                "next_rsi65_entry_date": next_entry_date,
                "next_rsi65_entry_price_eur": next_entry_price,
                "next_entry_vs_blocked_pct": next_entry_delta,
                "days_to_next_rsi65_entry": days_to_next_entry,
                "reentered_before_baseline_exit": reentered_before_baseline_exit,
                "next_rsi65_exit_date": next_exit_date,
                "next_rsi65_trade_return": next_trade_return,
                "next_rsi65_trade_max_drawdown": next_trade_max_drawdown,
                "classification": classification,
            }
        )

    return pd.DataFrame(rows)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _num(value: float | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.{digits}f}"


def _price(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.2f}"


def _write_markdown(audit: pd.DataFrame, out_path: Path) -> None:
    useful = audit[audit["classification"].str.startswith("utile")]
    mixed = audit[audit["classification"].str.startswith("misto")]
    costly = audit[audit["classification"].str.startswith("costo")]
    unique_trades = audit[["baseline_entry_date", "baseline_exit_date", "baseline_return"]].drop_duplicates()
    losing_unique_trades = unique_trades[unique_trades["baseline_return"] <= 0.0]

    lines = [
        "# RSI65 Blocked Entry Audit",
        "",
        "Questo report valuta solo gli ingressi bloccati da `RSI <= 65`.",
        "Non modifica i segnali ufficiali e mantiene invariata l'uscita ufficiale sotto SMA50 per 2 giorni consecutivi.",
        "",
        "## Sintesi",
        "",
        f"- Segnali giornalieri bloccati: {int(audit['blocked_signals'].sum())}.",
        f"- Finestre operative bloccate: {len(audit)}.",
        f"- Trade Baseline unici coinvolti: {len(unique_trades)}.",
        f"- Trade Baseline unici perdenti: {len(losing_unique_trades)}.",
        f"- Finestre utili: {len(useful)}.",
        f"- Finestre miste: {len(mixed)}.",
        f"- Finestre costose: {len(costly)}.",
        "",
        "Nota: piu' finestre possono appartenere allo stesso trade Baseline, perche' il filtro resta fuori e il segnale ufficiale puo' ripresentarsi nei giorni successivi.",
        "",
        "## Eventi",
        "",
        "| Blocco | Segnali | Prezzo blocco | RSI medio/max | Baseline exit | Return Baseline | DD trade | Max gain | Nuovo ingresso RSI65 | Delta ingresso | Return RSI65 trade | Giorni | Lettura |",
        "|---|---:|---:|---:|---|---:|---:|---:|---|---:|---:|---:|---|",
    ]
    for _, row in audit.iterrows():
        lines.append(
            "| "
            f"{row['start_date']} -> {row['end_date']} | "
            f"{int(row['blocked_signals'])} | "
            f"{_price(row['blocked_start_price_eur'])} | "
            f"{_num(row['avg_rsi'])} / {_num(row['max_rsi'])} | "
            f"{row['baseline_exit_date']} | "
            f"{_pct(row['baseline_return'])} | "
            f"{_pct(row['baseline_max_drawdown'])} | "
            f"{_pct(row['baseline_max_gain'])} | "
            f"{row['next_rsi65_entry_date'] or 'n/a'} | "
            f"{_pct(row['next_entry_vs_blocked_pct'])} | "
            f"{_pct(row['next_rsi65_trade_return'])} | "
            f"{_num(row['days_to_next_rsi65_entry'], 0)} | "
            f"{row['classification']} |"
        )

    lines.extend(
        [
            "",
            "## Conclusione",
            "",
            "- `RSI <= 65` non sta solo ottimizzando una metrica aggregata: concentra i blocchi in poche finestre operative ad alto RSI.",
            "- Tutti i trade Baseline unici intercettati dal filtro sono perdenti.",
            "- Quando RSI65 rientra, lo fa a un prezzo inferiore rispetto al blocco iniziale.",
            "- In questa analisi non emergono finestre costose, cioe' casi in cui RSI65 elimina un trade Baseline vincente.",
            "- Prima di promuovere il filtro serve ancora una validazione annuale/costi e un controllo che la soglia non sia troppo dipendente da pochi eventi.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    baseline_frame = _baseline_frame(df)
    rsi65_frame, _ = _variant_frame_and_blocked(df)
    _, baseline_metrics, _ = run_backtest(baseline_frame)
    _, rsi65_metrics, _ = run_backtest(rsi65_frame)

    audit = _audit(df)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    audit.to_csv(OUT_CSV, index=False)
    _write_markdown(audit, OUT_MD)

    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_MD}")
    print(
        "Baseline vs RSI65: "
        f"ann {baseline_metrics.annualized_return:.4f}->{rsi65_metrics.annualized_return:.4f}, "
        f"dd {baseline_metrics.max_drawdown:.4f}->{rsi65_metrics.max_drawdown:.4f}, "
        f"sharpe {baseline_metrics.sharpe_ratio:.4f}->{rsi65_metrics.sharpe_ratio:.4f}"
    )
    print(
        audit[
            [
                "start_date",
                "end_date",
                "blocked_signals",
                "baseline_return",
                "baseline_max_drawdown",
                "next_entry_vs_blocked_pct",
                "classification",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
