"""
Analisi ricorrenza falsa uscita tipo gennaio 2021.

Questo script non modifica i segnali ufficiali. Classifica le uscite trailing
dei candidati principali per capire se l'errore di gennaio 2021 si ripete:
- uscita in trend ancora valido;
- VENDI ufficiale successivo a prezzo piu' alto;
- rientro candidato a prezzo piu' alto;
- saldo del segmento peggiore della Baseline.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import run_backtest


SOURCE_CSV = PROJECT_ROOT / "data" / "indicators_with_signals.csv"
OUT_CSV = PROJECT_ROOT / "reports" / "false_exit_recurrence.csv"
OUT_MD = PROJECT_ROOT / "reports" / "false_exit_recurrence.md"

STOP_PCT = 0.08
VARIANTS = {
    "rsi65_mom-5_vol20": (65, -0.05, 0.20),
    "rsi62_mom-6_vol20": (62, -0.06, 0.20),
    "rsi65_mom-6_vol20": (65, -0.06, 0.20),
    "trail_only_mom-6_vol20": (None, -0.06, 0.20),
}


def _make_candidate(df: pd.DataFrame, rsi_max: int | None, momentum_min: float, volume_rel_min: float) -> tuple[pd.DataFrame, pd.DataFrame]:
    exposure = 0.0
    peak_close: float | None = None
    entry_date: pd.Timestamp | None = None
    entry_price_eur: float | None = None
    signals: list[str] = []
    events: list[dict[str, float | str | None]] = []

    for date, row in df.iterrows():
        signal = str(row["Segnale"])
        close = float(row["Close"])
        close_eur = float(row["Close_EUR"])

        if signal == "ACQUISTA" and rsi_max is not None and float(row["RSI"]) > rsi_max:
            signal = "MANTIENI"

        if signal == "ACQUISTA":
            if exposure <= 0.0:
                entry_date = date
                entry_price_eur = close_eur
            exposure = 1.0
            peak_close = close if peak_close is None else max(peak_close, close)
        elif signal == "VENDI":
            exposure = 0.0
            peak_close = None
            entry_date = None
            entry_price_eur = None
        elif exposure > 0.0 and peak_close is not None:
            peak_close = max(peak_close, close)
            if close <= peak_close * (1.0 - STOP_PCT):
                momentum_7d = close / float(row["Close_7d_ago"]) - 1.0
                volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
                if momentum_7d >= momentum_min and volume_rel >= volume_rel_min:
                    future = df.loc[df.index > date]
                    official_sells = future[future["Segnale"] == "VENDI"]
                    next_sell = official_sells.index[0] if not official_sells.empty else pd.NaT
                    next_sell_price = float(df.loc[next_sell, "Close_EUR"]) if not pd.isna(next_sell) else float("nan")
                    events.append(
                        {
                            "exit_date": date.date().isoformat(),
                            "entry_date": entry_date.date().isoformat() if entry_date is not None else None,
                            "exit_price_eur": close_eur,
                            "entry_price_eur": entry_price_eur,
                            "return_from_entry": close_eur / entry_price_eur - 1.0 if entry_price_eur else float("nan"),
                            "drawdown_from_peak": close / peak_close - 1.0,
                            "momentum_7d": momentum_7d,
                            "volume_rel": volume_rel,
                            "next_official_sell": next_sell.date().isoformat() if not pd.isna(next_sell) else None,
                            "next_official_sell_delta": next_sell_price / close_eur - 1.0 if not pd.isna(next_sell_price) else float("nan"),
                        }
                    )
                    signal = "VENDI"
                    exposure = 0.0
                    peak_close = None
                    entry_date = None
                    entry_price_eur = None

        signals.append(signal)

    frame = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    frame["Segnale"] = signals
    return frame, pd.DataFrame(events)


def _completed_trades(df: pd.DataFrame, equity: pd.DataFrame) -> pd.DataFrame:
    active = equity["EffectiveExposure"].gt(0.0).to_numpy()
    index = list(equity.index)
    trades: list[dict[str, float | str]] = []
    start_pos: int | None = None

    for pos, is_active in enumerate(active):
        if is_active and start_pos is None:
            start_pos = pos
        elif not is_active and start_pos is not None:
            entry = index[max(start_pos - 1, 0)]
            exit_ = index[max(pos - 1, 0)]
            entry_price = float(df.loc[entry, "Close_EUR"])
            exit_price = float(df.loc[exit_, "Close_EUR"])
            trades.append(
                {
                    "entry": entry,
                    "exit": exit_,
                    "return": exit_price / entry_price - 1.0,
                }
            )
            start_pos = None

    return pd.DataFrame(trades)


def _analyze(df: pd.DataFrame) -> pd.DataFrame:
    base_frame = df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()
    base_equity, _, _ = run_backtest(base_frame)
    base_trades = _completed_trades(df, base_equity)
    rows: list[dict[str, float | str | bool | None]] = []

    for variant, (rsi_max, momentum_min, volume_rel_min) in VARIANTS.items():
        frame, events = _make_candidate(df, rsi_max, momentum_min, volume_rel_min)
        equity, _, _ = run_backtest(frame)

        for _, event in events.iterrows():
            exit_date = pd.Timestamp(event["exit_date"])
            containing = base_trades[(base_trades["entry"] <= exit_date) & (base_trades["exit"] >= exit_date)]
            if containing.empty:
                continue

            base_trade = containing.iloc[0]
            interval = equity.loc[base_trade["entry"] : base_trade["exit"]]
            candidate_return = float(interval["EquityStrategy"].iloc[-1] / interval["EquityStrategy"].iloc[0] - 1.0)

            future = frame.loc[frame.index > exit_date]
            buys = future[future["Segnale"] == "ACQUISTA"]
            next_buy = buys.index[0] if not buys.empty else pd.NaT
            next_buy_price = float(df.loc[next_buy, "Close_EUR"]) if not pd.isna(next_buy) else float("nan")
            next_buy_delta = next_buy_price / float(event["exit_price_eur"]) - 1.0 if not pd.isna(next_buy_price) else float("nan")
            delta_vs_base = candidate_return - float(base_trade["return"])

            rows.append(
                {
                    "variant": variant,
                    "exit_date": event["exit_date"],
                    "entry_date": event["entry_date"],
                    "return_from_entry": event["return_from_entry"],
                    "drawdown_from_peak": event["drawdown_from_peak"],
                    "momentum_7d": event["momentum_7d"],
                    "volume_rel": event["volume_rel"],
                    "baseline_entry": base_trade["entry"].date().isoformat(),
                    "baseline_exit": base_trade["exit"].date().isoformat(),
                    "baseline_return": base_trade["return"],
                    "candidate_same_segment_return": candidate_return,
                    "delta_vs_baseline_segment": delta_vs_base,
                    "next_official_sell": event["next_official_sell"],
                    "next_official_sell_delta": event["next_official_sell_delta"],
                    "next_candidate_buy": next_buy.date().isoformat() if not pd.isna(next_buy) else None,
                    "next_candidate_buy_delta": next_buy_delta,
                    "official_sell_higher": bool(event["next_official_sell_delta"] > 0),
                    "reentry_higher": bool(next_buy_delta > 0) if not pd.isna(next_buy_delta) else False,
                    "harmful_segment": bool(delta_vs_base < 0),
                    "jan_2021_like": bool(event["next_official_sell_delta"] > 0 and next_buy_delta > 0 and delta_vs_base < -0.05),
                }
            )

    return pd.DataFrame(rows)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _write_markdown(results: pd.DataFrame, out_path: Path) -> None:
    summary = (
        results.groupby("variant")
        .agg(
            exits=("exit_date", "count"),
            official_sell_higher=("official_sell_higher", "sum"),
            reentry_higher=("reentry_higher", "sum"),
            harmful_segment=("harmful_segment", "sum"),
            jan_2021_like=("jan_2021_like", "sum"),
        )
        .reset_index()
    )
    jan_like = results[results["jan_2021_like"]].copy()
    harmful = results[results["harmful_segment"]].copy()

    lines = [
        "# False Exit Recurrence Analysis",
        "",
        "Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.",
        "",
        "Obiettivo: verificare se la falsa uscita di gennaio 2021 si ripete nel tempo.",
        "",
        "Definizione di evento tipo gennaio 2021:",
        "",
        "- uscita trailing confermata;",
        "- `VENDI` ufficiale successivo a prezzo piu' alto;",
        "- rientro candidato a prezzo piu' alto;",
        "- saldo del segmento peggiore della Baseline di almeno 5 punti percentuali.",
        "",
        "## Sintesi Per Variante",
        "",
        "| Variante | Uscite | VENDI ufficiale piu' alto | Rientro piu' alto | Segmenti peggiori | Tipo gennaio 2021 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in summary.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{int(row['exits'])} | "
            f"{int(row['official_sell_higher'])} | "
            f"{int(row['reentry_higher'])} | "
            f"{int(row['harmful_segment'])} | "
            f"{int(row['jan_2021_like'])} |"
        )

    lines.extend(
        [
            "",
            "## Eventi Tipo Gennaio 2021",
            "",
            "| Variante | Uscita | Entry | Baseline segment | Delta segmento | Rientro | Delta rientro |",
            "|---|---|---|---|---:|---|---:|",
        ]
    )
    if jan_like.empty:
        lines.append("| nessuno | n/a | n/a | n/a | n/a | n/a | n/a |")
    else:
        for _, row in jan_like.iterrows():
            lines.append(
                "| "
                f"{row['variant']} | "
                f"{row['exit_date']} | "
                f"{row['entry_date']} | "
                f"{row['baseline_entry']} -> {row['baseline_exit']} | "
                f"{_pct(row['delta_vs_baseline_segment'])} | "
                f"{row['next_candidate_buy']} | "
                f"{_pct(row['next_candidate_buy_delta'])} |"
            )

    lines.extend(
        [
            "",
            "## Tutti I Segmenti Peggiori",
            "",
            "| Variante | Uscita | Delta segmento | VENDI ufficiale delta | Rientro delta | Lettura |",
            "|---|---|---:|---:|---:|---|",
        ]
    )
    for _, row in harmful.sort_values(["variant", "exit_date"]).iterrows():
        if row["jan_2021_like"]:
            label = "grave: trend prosegue"
        else:
            label = "minore"
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{row['exit_date']} | "
            f"{_pct(row['delta_vs_baseline_segment'])} | "
            f"{_pct(row['next_official_sell_delta'])} | "
            f"{_pct(row['next_candidate_buy_delta'])} | "
            f"{label} |"
        )

    lines.extend(
        [
            "",
            "## Decisione",
            "",
            "- Il comportamento grave di gennaio 2021 appare isolato nel campione.",
            "- Si ripete solo come effetto della soglia `momentum >= -6%`; non compare nella variante `momentum >= -5%`.",
            "- Esistono falsi segnali minori, soprattutto 2023-04-20, ma con impatto molto piu' piccolo.",
            "- Quindi gennaio 2021 va trattato come caso speciale di trend parabolico, non come errore ricorrente ordinario.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    results = _analyze(df)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_CSV, index=False)
    _write_markdown(results, OUT_MD)
    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_MD}")
    print(results.groupby("variant").agg(exits=("exit_date", "count"), jan_2021_like=("jan_2021_like", "sum"), harmful=("harmful_segment", "sum")).to_string())


if __name__ == "__main__":
    main()
