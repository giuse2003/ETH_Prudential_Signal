"""
Validazione annuale degli ingressi Baseline vs RSI <= 65.

Questo script non modifica i segnali ufficiali. Tiene ferma l'uscita ufficiale
e confronta anno per anno:
- Baseline ufficiale;
- Baseline + filtro ingresso RSI <= 65.

Le performance sono misurate in EUR tramite Close_EUR.
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
from config import CFG


SOURCE_CSV = PROJECT_ROOT / "data" / "indicators_with_signals.csv"
OUT_CSV = PROJECT_ROOT / "reports" / "entry_yearly_validation.csv"
OUT_MD = PROJECT_ROOT / "reports" / "entry_yearly_validation.md"

RSI_MAX = 65.0
END_DATE = "2026-06-27"
EPSILON = 1e-8


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
            signal = "MANTIENI"

        if signal == "ACQUISTA":
            exposure = 1.0
        elif signal == "VENDI":
            exposure = 0.0
        signals.append(signal)

    out = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    out["Segnale"] = signals
    return out


def _trades_from_signals(df: pd.DataFrame, signals: pd.Series) -> pd.DataFrame:
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
        "entry_year": int(entry_date.year),
        "exit_year": int(exit_date.year),
        "entry_price_eur": entry_price,
        "exit_price_eur": exit_price,
        "trade_return": exit_price / entry_price - 1.0,
        "trade_max_drawdown": float(drawdown.min()),
        "duration_days": int((exit_date - entry_date).days),
        "is_open": bool(is_open),
    }


def _max_drawdown(equity: pd.Series) -> float:
    return float((equity / equity.cummax() - 1.0).min())


def _sharpe(daily_returns: pd.Series) -> float:
    r = daily_returns.dropna()
    if len(r) < 2:
        return float("nan")
    std = r.std(ddof=1)
    if std == 0:
        return float("nan")
    return float(np.sqrt(CFG.periods_per_year) * r.mean() / std)


def _year_metrics(equity: pd.DataFrame, trades: pd.DataFrame, year: int) -> dict[str, float | int]:
    subset = equity.loc[f"{year}-01-01":f"{year}-12-31"].copy()
    if len(subset) < 2:
        return {
            "total_return": float("nan"),
            "annualized_return": float("nan"),
            "max_drawdown": float("nan"),
            "sharpe_ratio": float("nan"),
            "exposure_ratio": float("nan"),
            "entries": 0,
            "closed_trades": 0,
            "wins_closed": 0,
            "losses_closed": 0,
            "win_rate_closed": float("nan"),
        }

    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    returns = normalized.pct_change()
    n_days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)

    entries = trades[trades["entry_year"] == year]
    closed = trades[(trades["exit_year"] == year) & (~trades["is_open"])]
    wins = closed[closed["trade_return"] > 0.0]
    losses = closed[closed["trade_return"] <= 0.0]

    return {
        "total_return": total_return,
        "annualized_return": float((1.0 + total_return) ** (CFG.periods_per_year / n_days) - 1.0),
        "max_drawdown": _max_drawdown(normalized),
        "sharpe_ratio": _sharpe(returns),
        "exposure_ratio": float(subset["EffectiveExposure"].gt(0.0).mean()),
        "entries": int(len(entries)),
        "closed_trades": int(len(closed)),
        "wins_closed": int(len(wins)),
        "losses_closed": int(len(losses)),
        "win_rate_closed": float(len(wins) / len(closed)) if len(closed) else float("nan"),
    }


def _run(df: pd.DataFrame) -> pd.DataFrame:
    variants = {
        "Baseline ufficiale": _baseline_frame(df),
        "RSI <= 65 ingresso": _rsi65_frame(df),
    }
    equities: dict[str, pd.DataFrame] = {}
    trades_by_model: dict[str, pd.DataFrame] = {}
    for model, frame in variants.items():
        equity, _, _ = run_backtest(frame)
        equities[model] = equity
        trades_by_model[model] = _trades_from_signals(df, frame["Segnale"])

    rows: list[dict[str, float | int | str]] = []
    for year in sorted(df.index.year.unique()):
        base = _year_metrics(equities["Baseline ufficiale"], trades_by_model["Baseline ufficiale"], int(year))
        rsi = _year_metrics(equities["RSI <= 65 ingresso"], trades_by_model["RSI <= 65 ingresso"], int(year))
        rows.append(
            {
                "year": int(year),
                "baseline_total_return": base["total_return"],
                "rsi65_total_return": rsi["total_return"],
                "delta_total_return": float(rsi["total_return"]) - float(base["total_return"]),
                "baseline_max_drawdown": base["max_drawdown"],
                "rsi65_max_drawdown": rsi["max_drawdown"],
                "delta_max_drawdown": float(rsi["max_drawdown"]) - float(base["max_drawdown"]),
                "baseline_sharpe": base["sharpe_ratio"],
                "rsi65_sharpe": rsi["sharpe_ratio"],
                "delta_sharpe": float(rsi["sharpe_ratio"]) - float(base["sharpe_ratio"]),
                "baseline_entries": base["entries"],
                "rsi65_entries": rsi["entries"],
                "delta_entries": int(rsi["entries"]) - int(base["entries"]),
                "baseline_closed_trades": base["closed_trades"],
                "rsi65_closed_trades": rsi["closed_trades"],
                "delta_closed_trades": int(rsi["closed_trades"]) - int(base["closed_trades"]),
                "baseline_win_rate_closed": base["win_rate_closed"],
                "rsi65_win_rate_closed": rsi["win_rate_closed"],
                "baseline_exposure": base["exposure_ratio"],
                "rsi65_exposure": rsi["exposure_ratio"],
            }
        )
    return pd.DataFrame(rows)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _signed_int(value: int) -> str:
    return f"{value:+d}" if value else "0"


def _write_markdown(results: pd.DataFrame, out_path: Path, start_date: str, end_date: str) -> None:
    changed_years = results[(results["delta_entries"] != 0) | (results["delta_closed_trades"] != 0)]
    different_return = results[results["delta_total_return"].abs() > EPSILON]
    better_return = results[results["delta_total_return"] > EPSILON]
    worse_return = results[results["delta_total_return"] < -EPSILON]
    better_dd = results[results["delta_max_drawdown"] > EPSILON]

    lines = [
        "# Entry Yearly Validation",
        "",
        f"Periodo: `{start_date}` -> `{end_date}`.",
        "",
        "Confronto solo sugli ingressi: Baseline ufficiale vs Baseline + filtro `RSI <= 65`.",
        "L'uscita resta invariata: `VENDI` sotto SMA50 per 2 giorni consecutivi.",
        "",
        "## Tabella Annuale",
        "",
        "| Anno | Baseline Ret | RSI65 Ret | Delta Ret | Baseline DD | RSI65 DD | Delta DD | Baseline Sharpe | RSI65 Sharpe | Entry B/R | Chiusi B/R | Delta chiusi |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in results.iterrows():
        lines.append(
            "| "
            f"{int(row['year'])} | "
            f"{_pct(row['baseline_total_return'])} | "
            f"{_pct(row['rsi65_total_return'])} | "
            f"{_pct(row['delta_total_return'])} | "
            f"{_pct(row['baseline_max_drawdown'])} | "
            f"{_pct(row['rsi65_max_drawdown'])} | "
            f"{_pct(row['delta_max_drawdown'])} | "
            f"{_ratio(row['baseline_sharpe'])} | "
            f"{_ratio(row['rsi65_sharpe'])} | "
            f"{int(row['baseline_entries'])}/{int(row['rsi65_entries'])} | "
            f"{int(row['baseline_closed_trades'])}/{int(row['rsi65_closed_trades'])} | "
            f"{_signed_int(int(row['delta_closed_trades']))} |"
        )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Anni in cui cambia il numero di operazioni: {', '.join(str(int(y)) for y in changed_years['year']) if not changed_years.empty else 'nessuno'}.",
            f"- Anni in cui cambia il rendimento in modo reale: {', '.join(str(int(y)) for y in different_return['year']) if not different_return.empty else 'nessuno'}.",
            f"- Anni con rendimento RSI65 migliore della Baseline: {len(better_return)}.",
            f"- Anni con rendimento RSI65 peggiore della Baseline: {len(worse_return)}.",
            f"- Anni con drawdown annuale meno profondo usando RSI65: {len(better_dd)}.",
            "- `Entry B/R` significa ingressi Baseline / ingressi RSI65 nello stesso anno.",
            "- `Chiusi B/R` significa trade chiusi Baseline / trade chiusi RSI65 nello stesso anno.",
            "- Delta DD positivo significa drawdown meno negativo, quindi miglioramento.",
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

    results = _run(df)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_CSV, index=False)
    _write_markdown(results, OUT_MD, df.index[0].date().isoformat(), df.index[-1].date().isoformat())

    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_MD}")
    print(
        results[
            [
                "year",
                "baseline_total_return",
                "rsi65_total_return",
                "delta_total_return",
                "baseline_entries",
                "rsi65_entries",
                "baseline_closed_trades",
                "rsi65_closed_trades",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
