"""
Confronto trade-by-trade tra Baseline e filtro ingresso RSI <= 65.

Questo script non modifica i segnali ufficiali. Tiene ferma l'uscita ufficiale
e confronta:
- Baseline ufficiale;
- Baseline + filtro ingresso RSI <= 65.

Le date/prezzi sono quelli della candela che genera il segnale, misurati su
Close_EUR. Il backtest resta conservativo: l'esposizione economica viene
applicata dal giorno successivo.
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
OUT_CSV = PROJECT_ROOT / "reports" / "entry_trade_comparison.csv"
OUT_MD = PROJECT_ROOT / "reports" / "entry_trade_comparison.md"

RSI_MAX = 65.0
END_DATE = "2026-06-27"


def _baseline_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()


def _rsi65_frame(df: pd.DataFrame) -> pd.DataFrame:
    exposure = 0.0
    signals: list[str] = []
    for _, row in df.iterrows():
        signal = str(row["Segnale"])
        if signal == "ACQUISTA" and exposure <= 0.0 and float(row["RSI"]) > RSI_MAX:
            signal = "MANTIENI"
        elif signal == "ACQUISTA" and exposure > 0.0:
            # Un ACQUISTA gia' in posizione non cambia il trade aperto.
            signal = "MANTIENI"

        if signal == "ACQUISTA":
            exposure = 1.0
        elif signal == "VENDI":
            exposure = 0.0
        signals.append(signal)

    out = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    out["Segnale"] = signals
    return out


def _trade_row(
    df: pd.DataFrame,
    model: str,
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
    min_return = normalized.min() - 1.0
    max_gain = normalized.max() - 1.0
    total_return = exit_price / entry_price - 1.0
    return {
        "model": model,
        "entry_date": entry_date.date().isoformat(),
        "entry_price_eur": entry_price,
        "exit_date": exit_date.date().isoformat(),
        "exit_price_eur": exit_price,
        "gain_pct": max(total_return, 0.0),
        "loss_pct": min(total_return, 0.0),
        "trade_return": total_return,
        "drawdown_suffered_pct": float(drawdown.min()),
        "min_return_from_entry_pct": float(min_return),
        "max_gain_pct": float(max_gain),
        "duration_days": int((exit_date - entry_date).days),
        "is_open": bool(is_open),
        "entry_rsi": float(df.loc[entry_date, "RSI"]),
    }


def _trades_from_signals(df: pd.DataFrame, signals: pd.Series, model: str) -> pd.DataFrame:
    exposure = 0.0
    entry_date: pd.Timestamp | None = None
    rows: list[dict[str, float | int | str | bool]] = []

    for date, signal in signals.items():
        if signal == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            entry_date = date
            continue

        if signal == "VENDI" and exposure > 0.0 and entry_date is not None:
            rows.append(_trade_row(df, model, entry_date, date, is_open=False))
            exposure = 0.0
            entry_date = None

    if exposure > 0.0 and entry_date is not None:
        rows.append(_trade_row(df, model, entry_date, df.index[-1], is_open=True))

    out = pd.DataFrame(rows)
    if not out.empty:
        out.insert(1, "trade_id", range(1, len(out) + 1))
    return out


def _matching_baseline_trade(baseline: pd.DataFrame, entry_date: str) -> pd.Series | None:
    ts = pd.Timestamp(entry_date)
    covering = baseline[
        (pd.to_datetime(baseline["entry_date"]) <= ts)
        & (pd.to_datetime(baseline["exit_date"]) >= ts)
    ]
    if not covering.empty:
        return covering.iloc[0]

    previous = baseline[pd.to_datetime(baseline["exit_date"]) < ts].sort_values("exit_date")
    if previous.empty:
        return None
    return previous.iloc[-1]


def _add_comparison_fields(trades: pd.DataFrame, baseline: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str | bool]] = []
    for _, row in trades.iterrows():
        out = row.to_dict()
        if row["model"] == "Baseline ufficiale":
            out["baseline_reference_entry_date"] = row["entry_date"]
            out["baseline_reference_exit_date"] = row["exit_date"]
            out["drawdown_avoided_vs_baseline_pct"] = 0.0
            out["entry_price_delta_vs_baseline_pct"] = 0.0
            out["return_delta_vs_baseline_pct"] = 0.0
        else:
            ref = _matching_baseline_trade(baseline, str(row["entry_date"]))
            if ref is None:
                out["baseline_reference_entry_date"] = ""
                out["baseline_reference_exit_date"] = ""
                out["drawdown_avoided_vs_baseline_pct"] = float("nan")
                out["entry_price_delta_vs_baseline_pct"] = float("nan")
                out["return_delta_vs_baseline_pct"] = float("nan")
            else:
                out["baseline_reference_entry_date"] = ref["entry_date"]
                out["baseline_reference_exit_date"] = ref["exit_date"]
                out["drawdown_avoided_vs_baseline_pct"] = float(row["drawdown_suffered_pct"]) - float(
                    ref["drawdown_suffered_pct"]
                )
                out["entry_price_delta_vs_baseline_pct"] = float(row["entry_price_eur"]) / float(
                    ref["entry_price_eur"]
                ) - 1.0
                out["return_delta_vs_baseline_pct"] = float(row["trade_return"]) - float(ref["trade_return"])
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


def _summary_rows(frames: dict[str, pd.DataFrame], all_trades: pd.DataFrame) -> list[str]:
    lines = [
        "| Modello | Trade | Ann. | Max DD sistema | Sharpe | PF | Win rate | Gain medio | Loss medio | DD medio trade |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for model, frame in frames.items():
        _, metrics, _ = run_backtest(frame)
        trades = all_trades[all_trades["model"] == model]
        gains = trades.loc[trades["trade_return"] > 0.0, "trade_return"]
        losses = trades.loc[trades["trade_return"] <= 0.0, "trade_return"]
        lines.append(
            "| "
            f"{model} | "
            f"{len(trades)} | "
            f"{_pct(metrics.annualized_return)} | "
            f"{_pct(metrics.max_drawdown)} | "
            f"{metrics.sharpe_ratio:.3f} | "
            f"{metrics.profit_factor:.3f} | "
            f"{_pct(metrics.win_rate)} | "
            f"{_pct(float(gains.mean()) if not gains.empty else float('nan'))} | "
            f"{_pct(float(losses.mean()) if not losses.empty else float('nan'))} | "
            f"{_pct(float(trades['drawdown_suffered_pct'].mean()) if not trades.empty else float('nan'))} |"
        )
    return lines


def _table_for_model(lines: list[str], trades: pd.DataFrame, model: str) -> None:
    subset = trades[trades["model"] == model].copy()
    lines.extend(
        [
            f"## {model}",
            "",
            "| # | Ingresso | Prezzo in | Uscita | Prezzo out | Gain | Loss | DD subito | DD evitato vs Baseline | RSI in | Stato |",
            "|---:|---|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for _, row in subset.iterrows():
        status = "aperto" if bool(row["is_open"]) else "chiuso"
        lines.append(
            "| "
            f"{int(row['trade_id'])} | "
            f"{row['entry_date']} | "
            f"{_price(row['entry_price_eur'])} | "
            f"{row['exit_date']} | "
            f"{_price(row['exit_price_eur'])} | "
            f"{_pct(row['gain_pct'])} | "
            f"{_pct(row['loss_pct'])} | "
            f"{_pct(row['drawdown_suffered_pct'])} | "
            f"{_pct(row['drawdown_avoided_vs_baseline_pct'])} | "
            f"{row['entry_rsi']:.1f} | "
            f"{status} |"
        )
    lines.append("")


def _write_markdown(trades: pd.DataFrame, frames: dict[str, pd.DataFrame], out_path: Path, end_date: str) -> None:
    baseline = trades[trades["model"] == "Baseline ufficiale"]
    rsi65 = trades[trades["model"] == "RSI <= 65 ingresso"]
    changed = rsi65[
        (rsi65["entry_price_delta_vs_baseline_pct"].abs() > 0.000001)
        | (rsi65["return_delta_vs_baseline_pct"].abs() > 0.000001)
    ]

    lines = [
        "# Entry Trade Comparison",
        "",
        f"Periodo: inizio serie -> `{end_date}`.",
        "",
        "Confronto solo sugli ingressi. L'uscita resta quella ufficiale: `VENDI` sotto SMA50 per 2 giorni consecutivi.",
        "",
        "Modelli:",
        "",
        "- `Baseline ufficiale`: segnali attuali invariati;",
        "- `RSI <= 65 ingresso`: aggiunge il vincolo `RSI <= 65` ai soli nuovi `ACQUISTA`.",
        "",
        "Prezzi e rendimenti sono calcolati su `Close_EUR` della candela del segnale.",
        "",
        "## Sintesi",
        "",
        *_summary_rows(frames, trades),
        "",
        "## Trade Modificati Dal Filtro RSI65",
        "",
        "| Ingresso RSI65 | Prezzo RSI65 | Rif. Baseline | Delta prezzo ingresso | Return RSI65 | Delta return | DD subito RSI65 | DD evitato vs Baseline |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in changed.iterrows():
        lines.append(
            "| "
            f"{row['entry_date']} | "
            f"{_price(row['entry_price_eur'])} | "
            f"{row['baseline_reference_entry_date']} -> {row['baseline_reference_exit_date']} | "
            f"{_pct(row['entry_price_delta_vs_baseline_pct'])} | "
            f"{_pct(row['trade_return'])} | "
            f"{_pct(row['return_delta_vs_baseline_pct'])} | "
            f"{_pct(row['drawdown_suffered_pct'])} | "
            f"{_pct(row['drawdown_avoided_vs_baseline_pct'])} |"
        )

    lines.extend(
        [
            "",
            "Nota sul `DD evitato vs Baseline`: valore positivo significa che il trade RSI65 ha subito meno drawdown del trade Baseline di riferimento.",
            "",
        ]
    )
    _table_for_model(lines, trades, "Baseline ufficiale")
    _table_for_model(lines, trades, "RSI <= 65 ingresso")

    lines.extend(
        [
            "## Lettura",
            "",
            f"- Baseline genera {len(baseline)} trade; RSI65 genera {len(rsi65)} trade.",
            f"- I trade cambiati dal filtro sono {len(changed)}.",
            "- Il filtro RSI65 non sostituisce la Baseline: aggiunge solo un limite superiore all'RSI per evitare ingressi su mercato gia' tirato.",
            "- La decisione operativa resta sospesa fino al controllo annuale e ai test con costi/slippage.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    end_ts = pd.Timestamp(END_DATE)
    df = df.loc[:end_ts].copy()
    if df.empty:
        raise ValueError(f"Nessuna candela disponibile fino a {END_DATE}.")
    actual_end = df.index[-1].date().isoformat()

    baseline_frame = _baseline_frame(df)
    rsi65_frame = _rsi65_frame(df)
    baseline_trades = _trades_from_signals(df, baseline_frame["Segnale"], "Baseline ufficiale")
    rsi65_trades = _trades_from_signals(df, rsi65_frame["Segnale"], "RSI <= 65 ingresso")

    all_trades = pd.concat([baseline_trades, rsi65_trades], ignore_index=True)
    all_trades = _add_comparison_fields(all_trades, baseline_trades)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    all_trades.to_csv(OUT_CSV, index=False)
    _write_markdown(
        all_trades,
        {
            "Baseline ufficiale": baseline_frame,
            "RSI <= 65 ingresso": rsi65_frame,
        },
        OUT_MD,
        actual_end,
    )

    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_MD}")
    print(f"Periodo: {df.index[0].date().isoformat()} -> {actual_end}")
    print(all_trades[["model", "trade_id", "entry_date", "entry_price_eur", "exit_date", "exit_price_eur", "trade_return", "drawdown_suffered_pct", "drawdown_avoided_vs_baseline_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()
