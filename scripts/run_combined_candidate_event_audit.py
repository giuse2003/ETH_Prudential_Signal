"""
Audit evento-per-evento del candidato combinato.

Questo script non modifica i segnali ufficiali. Ricostruisce in backtest il
candidato:
- filtro ingresso RSI <= 65;
- trailing stop 8% su massimo Close post-ingresso;
- conferma momentum 7g >= -5%;
- conferma volume relativo >= +20%.

Output:
- ingressi ufficiali bloccati dal filtro RSI;
- uscite aggiuntive generate dal trailing confermato;
- confronto trade Baseline vs candidato.
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
OUT_BLOCKED_CSV = PROJECT_ROOT / "reports" / "combined_candidate_blocked_entries.csv"
OUT_EXITS_CSV = PROJECT_ROOT / "reports" / "combined_candidate_trailing_exits.csv"
OUT_TRADES_CSV = PROJECT_ROOT / "reports" / "combined_candidate_trade_comparison.csv"
OUT_MD = PROJECT_ROOT / "reports" / "combined_candidate_event_audit.md"

RSI_MAX = 65.0
STOP_PCT = 0.08
MOMENTUM_MIN = -0.05
VOLUME_REL_MIN = 0.20


def _make_candidate_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    exposure = 0.0
    peak_close: float | None = None
    signals: list[str] = []
    blocked_entries: list[dict[str, float | str]] = []
    trailing_exits: list[dict[str, float | str]] = []
    last_effective_entry_date: pd.Timestamp | None = None
    last_effective_entry_price_eur: float | None = None

    for date, row in df.iterrows():
        official = str(row["Segnale"])
        signal = official
        close_usd = float(row["Close"])
        close_eur = float(row["Close_EUR"])
        rsi = float(row["RSI"])
        was_exposed = exposure > 0.0

        if official == "ACQUISTA" and rsi > RSI_MAX:
            signal = "MANTIENI"
            blocked_entries.append(
                {
                    "date": date.date().isoformat(),
                    "close_eur": close_eur,
                    "close_usd": close_usd,
                    "rsi": rsi,
                    "distance_sma200_pct": close_usd / float(row["SMA200"]) - 1.0,
                    "momentum_7d_pct": close_usd / float(row["Close_7d_ago"]) - 1.0,
                    "volume_rel_pct": float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0,
                    "was_already_exposed": was_exposed,
                }
            )

        if signal == "ACQUISTA":
            if exposure <= 0.0:
                last_effective_entry_date = date
                last_effective_entry_price_eur = close_eur
            exposure = 1.0
            peak_close = close_usd if peak_close is None else max(peak_close, close_usd)
        elif signal == "VENDI":
            exposure = 0.0
            peak_close = None
            last_effective_entry_date = None
            last_effective_entry_price_eur = None
        elif exposure > 0.0 and peak_close is not None:
            peak_close = max(peak_close, close_usd)
            stop_level = peak_close * (1.0 - STOP_PCT)
            if close_usd <= stop_level:
                momentum_7d = close_usd / float(row["Close_7d_ago"]) - 1.0
                volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
                if momentum_7d >= MOMENTUM_MIN and volume_rel >= VOLUME_REL_MIN:
                    future = df.loc[df.index > date]
                    official_sell = future[future["Segnale"] == "VENDI"]
                    next_official_sell_date = official_sell.index[0] if not official_sell.empty else pd.NaT
                    next_official_sell_close_eur = (
                        float(official_sell.iloc[0]["Close_EUR"]) if not official_sell.empty else float("nan")
                    )
                    official_delta = (
                        next_official_sell_close_eur / close_eur - 1.0
                        if not pd.isna(next_official_sell_close_eur)
                        else float("nan")
                    )
                    trailing_exits.append(
                        {
                            "date": date.date().isoformat(),
                            "close_eur": close_eur,
                            "close_usd": close_usd,
                            "entry_date": (
                                last_effective_entry_date.date().isoformat()
                                if last_effective_entry_date is not None
                                else None
                            ),
                            "entry_price_eur": last_effective_entry_price_eur,
                            "return_from_entry_pct": (
                                close_eur / last_effective_entry_price_eur - 1.0
                                if last_effective_entry_price_eur is not None
                                else float("nan")
                            ),
                            "peak_close_usd": peak_close,
                            "stop_level_usd": stop_level,
                            "drawdown_from_peak_pct": close_usd / peak_close - 1.0,
                            "momentum_7d_pct": momentum_7d,
                            "volume_rel_pct": volume_rel,
                            "next_official_sell_date": (
                                next_official_sell_date.date().isoformat()
                                if not pd.isna(next_official_sell_date)
                                else None
                            ),
                            "next_official_sell_close_eur": next_official_sell_close_eur,
                            "next_official_sell_delta_pct": official_delta,
                        }
                    )
                    signal = "VENDI"
                    exposure = 0.0
                    peak_close = None
                    last_effective_entry_date = None
                    last_effective_entry_price_eur = None

        signals.append(signal)

    frame = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    frame["Segnale"] = signals
    return frame, pd.DataFrame(blocked_entries), pd.DataFrame(trailing_exits)


def _enrich_exits_with_reentry(
    df: pd.DataFrame,
    candidate_frame: pd.DataFrame,
    exits: pd.DataFrame,
) -> pd.DataFrame:
    if exits.empty:
        return exits

    enriched = exits.copy()
    next_buy_dates: list[str | None] = []
    next_buy_prices: list[float] = []
    next_buy_deltas: list[float] = []
    reentry_is_lower: list[bool | None] = []

    for _, row in enriched.iterrows():
        exit_date = pd.Timestamp(row["date"])
        future = candidate_frame.loc[candidate_frame.index > exit_date]
        buys = future[future["Segnale"] == "ACQUISTA"]
        if buys.empty:
            next_buy_dates.append(None)
            next_buy_prices.append(float("nan"))
            next_buy_deltas.append(float("nan"))
            reentry_is_lower.append(None)
            continue

        next_buy_date = buys.index[0]
        next_buy_price = float(df.loc[next_buy_date, "Close_EUR"])
        delta = next_buy_price / float(row["close_eur"]) - 1.0
        next_buy_dates.append(next_buy_date.date().isoformat())
        next_buy_prices.append(next_buy_price)
        next_buy_deltas.append(delta)
        reentry_is_lower.append(bool(delta < 0.0))

    enriched["next_candidate_buy_date"] = next_buy_dates
    enriched["next_candidate_buy_close_eur"] = next_buy_prices
    enriched["next_candidate_buy_delta_pct"] = next_buy_deltas
    enriched["reentry_lower_than_exit"] = reentry_is_lower
    return enriched


def _blocked_entry_episodes(blocked: pd.DataFrame) -> pd.DataFrame:
    if blocked.empty:
        return blocked

    new_entries = blocked[~blocked["was_already_exposed"]].copy()
    if new_entries.empty:
        return pd.DataFrame()

    dates = pd.to_datetime(new_entries["date"])
    groups = (dates.diff().dt.days.fillna(99) > 1).cumsum()
    rows: list[dict[str, float | int | str]] = []
    for _, group in new_entries.groupby(groups):
        rows.append(
            {
                "start_date": group.iloc[0]["date"],
                "end_date": group.iloc[-1]["date"],
                "days": int(len(group)),
                "min_price_eur": float(group["close_eur"].min()),
                "max_price_eur": float(group["close_eur"].max()),
                "avg_rsi": float(group["rsi"].mean()),
                "max_rsi": float(group["rsi"].max()),
                "avg_distance_sma200_pct": float(group["distance_sma200_pct"].mean()),
                "avg_momentum_7d_pct": float(group["momentum_7d_pct"].mean()),
                "avg_volume_rel_pct": float(group["volume_rel_pct"].mean()),
            }
        )
    return pd.DataFrame(rows)


def _enrich_exits_with_trade_delta(
    exits: pd.DataFrame,
    baseline_trades: pd.DataFrame,
    candidate_equity: pd.DataFrame,
) -> pd.DataFrame:
    if exits.empty:
        return exits

    enriched = exits.copy()
    baseline_entry_dates: list[str | None] = []
    baseline_exit_dates: list[str | None] = []
    baseline_returns: list[float] = []
    candidate_interval_returns: list[float] = []
    candidate_minus_baseline: list[float] = []

    for _, row in enriched.iterrows():
        exit_date = pd.Timestamp(row["date"])
        containing = baseline_trades[
            (pd.to_datetime(baseline_trades["entry_signal_date"]) <= exit_date)
            & (pd.to_datetime(baseline_trades["exit_signal_date"]) >= exit_date)
        ]
        if containing.empty:
            baseline_entry_dates.append(None)
            baseline_exit_dates.append(None)
            baseline_returns.append(float("nan"))
            candidate_interval_returns.append(float("nan"))
            candidate_minus_baseline.append(float("nan"))
            continue

        trade = containing.iloc[0]
        start = pd.Timestamp(trade["entry_signal_date"])
        end = pd.Timestamp(trade["exit_signal_date"])
        interval = candidate_equity.loc[start:end]
        if len(interval) < 2:
            candidate_return = float("nan")
        else:
            candidate_return = float(interval["EquityStrategy"].iloc[-1] / interval["EquityStrategy"].iloc[0] - 1.0)
        baseline_return = float(trade["trade_return"])

        baseline_entry_dates.append(str(trade["entry_signal_date"]))
        baseline_exit_dates.append(str(trade["exit_signal_date"]))
        baseline_returns.append(baseline_return)
        candidate_interval_returns.append(candidate_return)
        candidate_minus_baseline.append(candidate_return - baseline_return)

    enriched["baseline_trade_entry"] = baseline_entry_dates
    enriched["baseline_trade_exit"] = baseline_exit_dates
    enriched["baseline_trade_return"] = baseline_returns
    enriched["candidate_same_interval_return"] = candidate_interval_returns
    enriched["candidate_minus_baseline_return"] = candidate_minus_baseline
    return enriched


def _baseline_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()


def _completed_trades(df: pd.DataFrame, equity: pd.DataFrame, variant: str) -> pd.DataFrame:
    active = equity["EffectiveExposure"].gt(0.0).to_numpy()
    index = list(equity.index)
    trades: list[dict[str, float | int | str]] = []
    entry_pos: int | None = None

    for pos, is_active in enumerate(active):
        if is_active and entry_pos is None:
            entry_pos = pos
            continue

        if not is_active and entry_pos is not None:
            exit_pos = pos
            entry_signal_date = index[max(entry_pos - 1, 0)]
            exit_signal_date = index[max(exit_pos - 1, 0)]
            entry_price = float(df.loc[entry_signal_date, "Close_EUR"])
            exit_price = float(df.loc[exit_signal_date, "Close_EUR"])
            path = df.loc[entry_signal_date:exit_signal_date, "Close_EUR"]
            normalized = path / entry_price
            drawdown = normalized / normalized.cummax() - 1.0
            trades.append(
                {
                    "variant": variant,
                    "entry_signal_date": entry_signal_date.date().isoformat(),
                    "exit_signal_date": exit_signal_date.date().isoformat(),
                    "entry_price_eur": entry_price,
                    "exit_price_eur": exit_price,
                    "trade_return": exit_price / entry_price - 1.0,
                    "trade_max_drawdown": float(drawdown.min()),
                    "duration_calendar_days": int((exit_signal_date - entry_signal_date).days),
                    "entry_rsi": float(df.loc[entry_signal_date, "RSI"]),
                    "entry_distance_sma200_pct": (
                        float(df.loc[entry_signal_date, "Close"])
                        / float(df.loc[entry_signal_date, "SMA200"])
                        - 1.0
                    ),
                }
            )
            entry_pos = None

    return pd.DataFrame(trades)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _num(value: float | None, digits: int = 2) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.{digits}f}"


def _write_markdown(
    blocked: pd.DataFrame,
    exits: pd.DataFrame,
    blocked_episodes: pd.DataFrame,
    trades: pd.DataFrame,
    out_path: Path,
) -> None:
    baseline_trades = trades[trades["variant"] == "baseline"].copy()
    candidate_trades = trades[trades["variant"] == "candidate"].copy()
    blocked_new_entries = blocked[~blocked["was_already_exposed"]].copy()
    blocked_while_exposed = blocked[blocked["was_already_exposed"]].copy()

    baseline_after_2022 = baseline_trades[baseline_trades["entry_signal_date"] >= "2022-01-01"]
    candidate_after_2022 = candidate_trades[candidate_trades["entry_signal_date"] >= "2022-01-01"]

    lines = [
        "# Combined Candidate Event Audit",
        "",
        "Questa analisi e' solo ricerca. Non modifica i segnali ufficiali.",
        "",
        "Candidato auditato: `RSI <= 65` sugli ingressi + trailing stop 8% con",
        "momentum 7g >= -5% e volume relativo >= +20%.",
        "",
        "## Sintesi Eventi",
        "",
        f"- Segnali `ACQUISTA` bloccati da RSI > 65: {len(blocked)}.",
        f"- Di questi, nuovi ingressi effettivamente bloccati: {len(blocked_new_entries)}.",
        f"- Episodi distinti di nuovo ingresso bloccato: {len(blocked_episodes)}.",
        f"- `ACQUISTA` bloccati mentre la posizione era gia' aperta: {len(blocked_while_exposed)}.",
        f"- Uscite trailing confermate: {len(exits)}.",
        f"- Trade Baseline dal 2022: {len(baseline_after_2022)}.",
        f"- Trade candidato dal 2022: {len(candidate_after_2022)}.",
        "",
        "## Nuovi Ingressi Bloccati Da RSI",
        "",
        "| Data | Prezzo EUR | RSI | Dist SMA200 | Mom 7g | Volume rel |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in blocked_new_entries.iterrows():
        lines.append(
            "| "
            f"{row['date']} | "
            f"{_num(row['close_eur'], 2)} | "
            f"{_num(row['rsi'], 1)} | "
            f"{_pct(row['distance_sma200_pct'])} | "
            f"{_pct(row['momentum_7d_pct'])} | "
            f"{_pct(row['volume_rel_pct'])} |"
        )

    lines.extend(
        [
            "",
            "## Episodi Di Nuovo Ingresso Bloccato",
            "",
            "| Inizio | Fine | Giorni | Prezzo min/max EUR | RSI medio/max | Dist SMA200 media | Mom 7g medio | Volume rel medio |",
            "|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in blocked_episodes.iterrows():
        lines.append(
            "| "
            f"{row['start_date']} | "
            f"{row['end_date']} | "
            f"{int(row['days'])} | "
            f"{_num(row['min_price_eur'], 2)} / {_num(row['max_price_eur'], 2)} | "
            f"{_num(row['avg_rsi'], 1)} / {_num(row['max_rsi'], 1)} | "
            f"{_pct(row['avg_distance_sma200_pct'])} | "
            f"{_pct(row['avg_momentum_7d_pct'])} | "
            f"{_pct(row['avg_volume_rel_pct'])} |"
        )

    lines.extend(
        [
            "",
            "## Uscite Trailing Confermate",
            "",
            "| Data uscita | Entry | Return da entry | DD da picco | VENDI ufficiale successivo | Delta vs VENDI ufficiale | Rientro candidato | Delta rientro | Esito rientro |",
            "|---|---|---:|---:|---|---:|---|---:|---|",
        ]
    )
    for _, row in exits.iterrows():
        if pd.isna(row.get("next_candidate_buy_delta_pct")):
            reentry_text = "nessun rientro"
        elif bool(row.get("reentry_lower_than_exit")):
            reentry_text = "utile: rientro piu' basso"
        else:
            reentry_text = "costo: rientro piu' alto"
        lines.append(
            "| "
            f"{row['date']} | "
            f"{row['entry_date']} | "
            f"{_pct(row['return_from_entry_pct'])} | "
            f"{_pct(row['drawdown_from_peak_pct'])} | "
            f"{row['next_official_sell_date']} | "
            f"{_pct(row['next_official_sell_delta_pct'])} | "
            f"{row.get('next_candidate_buy_date')} | "
            f"{_pct(row.get('next_candidate_buy_delta_pct'))} | "
            f"{reentry_text} |"
        )

    lines.extend(
        [
            "",
            "## Saldo Per Segmento Baseline",
            "",
            "| Uscita trailing | Segmento Baseline | Return Baseline | Return candidato stesso intervallo | Delta candidato |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for _, row in exits.iterrows():
        lines.append(
            "| "
            f"{row['date']} | "
            f"{row.get('baseline_trade_entry')} -> {row.get('baseline_trade_exit')} | "
            f"{_pct(row.get('baseline_trade_return'))} | "
            f"{_pct(row.get('candidate_same_interval_return'))} | "
            f"{_pct(row.get('candidate_minus_baseline_return'))} |"
        )

    lines.extend(
        [
            "",
            "## Trade Dal 2022 - Baseline",
            "",
            "| Entry | Exit | Return | Max DD trade | RSI entry | Dist SMA200 |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in baseline_after_2022.iterrows():
        lines.append(
            "| "
            f"{row['entry_signal_date']} | {row['exit_signal_date']} | "
            f"{_pct(row['trade_return'])} | "
            f"{_pct(row['trade_max_drawdown'])} | "
            f"{_num(row['entry_rsi'], 1)} | "
            f"{_pct(row['entry_distance_sma200_pct'])} |"
        )

    lines.extend(
        [
            "",
            "## Trade Dal 2022 - Candidato",
            "",
            "| Entry | Exit | Return | Max DD trade | RSI entry | Dist SMA200 |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in candidate_after_2022.iterrows():
        lines.append(
            "| "
            f"{row['entry_signal_date']} | {row['exit_signal_date']} | "
            f"{_pct(row['trade_return'])} | "
            f"{_pct(row['trade_max_drawdown'])} | "
            f"{_num(row['entry_rsi'], 1)} | "
            f"{_pct(row['entry_distance_sma200_pct'])} |"
        )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            "- Il filtro RSI blocca pochi episodi di ingresso, ma sono quasi tutti ingressi in forte estensione.",
            "- Le uscite trailing confermate anticipano sempre un `VENDI` ufficiale successivo a prezzo piu' basso nel campione analizzato.",
            "- Il rientro successivo puo' avvenire anche piu' in alto, ma il saldo va letto sul segmento Baseline completo.",
            "- Il candidato resta sperimentale: il prossimo controllo e' quantificare il saldo netto di ogni uscita trailing fra protezione fino al `VENDI` ufficiale e costo/beneficio del rientro.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`."
        )

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    baseline_equity, _, _ = run_backtest(_baseline_frame(df))
    candidate_frame, blocked, exits = _make_candidate_frame(df)
    candidate_equity, _, _ = run_backtest(candidate_frame)

    baseline_trades = _completed_trades(df, baseline_equity, "baseline")
    candidate_trades = _completed_trades(df, candidate_equity, "candidate")
    exits = _enrich_exits_with_reentry(df, candidate_frame, exits)
    exits = _enrich_exits_with_trade_delta(exits, baseline_trades, candidate_equity)
    blocked_episodes = _blocked_entry_episodes(blocked)
    trades = pd.concat([baseline_trades, candidate_trades], ignore_index=True)

    OUT_BLOCKED_CSV.parent.mkdir(parents=True, exist_ok=True)
    blocked.to_csv(OUT_BLOCKED_CSV, index=False)
    exits.to_csv(OUT_EXITS_CSV, index=False)
    trades.to_csv(OUT_TRADES_CSV, index=False)
    _write_markdown(blocked, exits, blocked_episodes, trades, OUT_MD)

    print(f"Saved {OUT_BLOCKED_CSV}")
    print(f"Saved {OUT_EXITS_CSV}")
    print(f"Saved {OUT_TRADES_CSV}")
    print(f"Saved {OUT_MD}")
    print("")
    print("Blocked new entries:")
    if blocked.empty:
        print("none")
    else:
        print(blocked[~blocked["was_already_exposed"]].to_string(index=False))
    print("")
    print("Trailing exits:")
    if exits.empty:
        print("none")
    else:
        print(exits.to_string(index=False))


if __name__ == "__main__":
    main()
