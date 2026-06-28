"""
Analisi dedicata ai soli segnali di uscita.

Questo script non modifica i segnali ufficiali. Valuta solo regole di uscita
sperimentali mantenendo invariati gli ingressi Baseline.

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
OUT_CSV = PROJECT_ROOT / "reports" / "exit_signal_analysis.csv"
OUT_EVENTS_CSV = PROJECT_ROOT / "reports" / "exit_signal_events.csv"
OUT_MD = PROJECT_ROOT / "reports" / "exit_signal_analysis.md"

END_DATE = "2026-06-27"
RECENT_START = "2022-01-01"
STOP_PCT = 0.08

EXIT_MODELS = [
    {
        "variant": "Baseline ufficiale",
        "description": "Uscita ufficiale: Close sotto SMA50 per 2 giorni consecutivi.",
        "mode": "baseline",
        "momentum_min": None,
        "volume_rel_min": None,
    },
    {
        "variant": "SMA50 1 giorno",
        "description": "Uscita appena Close chiude sotto SMA50.",
        "mode": "sma50_1d",
        "momentum_min": None,
        "volume_rel_min": None,
    },
    {
        "variant": "Trailing 8% puro",
        "description": "Uscita se Close scende almeno 8% dal massimo Close post-ingresso.",
        "mode": "trailing_all",
        "momentum_min": None,
        "volume_rel_min": None,
    },
    {
        "variant": "Trail8 confermato -5 / vol +20",
        "description": "Trailing 8% eseguito solo con momentum 7g >= -5% e volume relativo >= +20%.",
        "mode": "trailing_confirmed",
        "momentum_min": -0.05,
        "volume_rel_min": 0.20,
    },
    {
        "variant": "Trail8 confermato -6 / vol +20",
        "description": "Trailing 8% eseguito solo con momentum 7g >= -6% e volume relativo >= +20%.",
        "mode": "trailing_confirmed",
        "momentum_min": -0.06,
        "volume_rel_min": 0.20,
    },
]


def _baseline_frame(df: pd.DataFrame) -> pd.DataFrame:
    return df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()


def _exit_frame(
    df: pd.DataFrame,
    *,
    variant: str,
    mode: str,
    momentum_min: float | None,
    volume_rel_min: float | None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    exposure = 0.0
    peak_close: float | None = None
    entry_date: pd.Timestamp | None = None
    signals: list[str] = []
    events: list[dict[str, float | int | str | bool]] = []

    for date, row in df.iterrows():
        official = str(row["Segnale"])
        signal = official
        close = float(row["Close"])

        if official == "ACQUISTA" and exposure <= 0.0:
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
        elif exposure > 0.0:
            peak_close = max(peak_close or close, close)
            forced = False
            reason = ""
            stop_level = float("nan")
            momentum_7d = float("nan")
            volume_rel = float("nan")

            if mode == "sma50_1d":
                forced = bool(close < float(row["SMA50"]))
                reason = "close_below_sma50_1d"
            elif mode in {"trailing_all", "trailing_confirmed"}:
                stop_level = peak_close * (1.0 - STOP_PCT)
                if close <= stop_level:
                    if mode == "trailing_all":
                        forced = True
                    else:
                        momentum_7d = close / float(row["Close_7d_ago"]) - 1.0
                        volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
                        forced = bool(momentum_7d >= momentum_min and volume_rel >= volume_rel_min)
                    reason = "trailing8"

            if forced:
                official_exit = _next_official_exit(df, date)
                next_buy = _next_official_buy(df, date)
                official_exit_price = (
                    float(df.loc[official_exit, "Close_EUR"]) if official_exit is not None else float("nan")
                )
                next_buy_price = float(df.loc[next_buy, "Close_EUR"]) if next_buy is not None else float("nan")
                exit_price = float(row["Close_EUR"])
                events.append(
                    {
                        "variant": variant,
                        "date": date.date().isoformat(),
                        "entry_date": entry_date.date().isoformat() if entry_date is not None else "",
                        "exit_price_eur": exit_price,
                        "reason": reason,
                        "official_exit_date": official_exit.date().isoformat() if official_exit is not None else "",
                        "official_exit_price_eur": official_exit_price,
                        "exit_vs_official_exit_pct": (
                            exit_price / official_exit_price - 1.0
                            if official_exit_price and not pd.isna(official_exit_price)
                            else float("nan")
                        ),
                        "next_buy_date": next_buy.date().isoformat() if next_buy is not None else "",
                        "next_buy_price_eur": next_buy_price,
                        "next_buy_vs_exit_pct": (
                            next_buy_price / exit_price - 1.0
                            if next_buy_price and not pd.isna(next_buy_price)
                            else float("nan")
                        ),
                        "peak_drawdown_pct": close / peak_close - 1.0,
                        "momentum_7d_pct": momentum_7d,
                        "volume_rel_pct": volume_rel,
                    }
                )
                signal = "VENDI"
                exposure = 0.0
                peak_close = None
                entry_date = None

        signals.append(signal)

    frame = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    frame["Segnale"] = signals
    return frame, pd.DataFrame(events)


def _next_official_exit(df: pd.DataFrame, date: pd.Timestamp) -> pd.Timestamp | None:
    future = df.loc[df.index > date]
    sells = future[future["Segnale"] == "VENDI"]
    return None if sells.empty else sells.index[0]


def _next_official_buy(df: pd.DataFrame, date: pd.Timestamp) -> pd.Timestamp | None:
    future = df.loc[df.index > date]
    buys = future[future["Segnale"] == "ACQUISTA"]
    return None if buys.empty else buys.index[0]


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


def _slice_metrics(equity: pd.DataFrame, start: str) -> dict[str, float]:
    subset = equity.loc[start:].copy()
    if len(subset) < 2:
        return {
            "recent_annualized_return": float("nan"),
            "recent_max_drawdown": float("nan"),
            "recent_sharpe_ratio": float("nan"),
        }
    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    returns = normalized.pct_change()
    n_days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    return {
        "recent_annualized_return": float((1.0 + total_return) ** (CFG.periods_per_year / n_days) - 1.0),
        "recent_max_drawdown": _max_drawdown(normalized),
        "recent_sharpe_ratio": _sharpe(returns),
    }


def _run(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, float | int | str]] = []
    event_frames: list[pd.DataFrame] = []
    baseline_frame = _baseline_frame(df)
    _, baseline_metrics, _ = run_backtest(baseline_frame)

    for model in EXIT_MODELS:
        if model["mode"] == "baseline":
            frame = baseline_frame
            events = pd.DataFrame()
        else:
            frame, events = _exit_frame(
                df,
                variant=model["variant"],
                mode=model["mode"],
                momentum_min=model["momentum_min"],
                volume_rel_min=model["volume_rel_min"],
            )
        equity, metrics, _ = run_backtest(frame)
        if not events.empty:
            event_frames.append(events)
        rows.append(
            {
                "variant": model["variant"],
                "description": model["description"],
                "annualized_return": metrics.annualized_return,
                "max_drawdown": metrics.max_drawdown,
                "sharpe_ratio": metrics.sharpe_ratio,
                "profit_factor": metrics.profit_factor,
                "num_operations": metrics.num_operations,
                "win_rate": metrics.win_rate,
                "exposure_ratio": metrics.exposure_ratio,
                **_slice_metrics(equity, RECENT_START),
                "forced_exits": int(len(events)),
                "delta_ann_vs_baseline": metrics.annualized_return - baseline_metrics.annualized_return,
                "delta_dd_vs_baseline": metrics.max_drawdown - baseline_metrics.max_drawdown,
                "delta_sharpe_vs_baseline": metrics.sharpe_ratio - baseline_metrics.sharpe_ratio,
            }
        )

    events_all = pd.concat(event_frames, ignore_index=True) if event_frames else pd.DataFrame()
    return pd.DataFrame(rows), events_all


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(results: pd.DataFrame, events: pd.DataFrame, out_path: Path, start_date: str, end_date: str) -> None:
    lines = [
        "# Exit Signal Analysis",
        "",
        f"Periodo: `{start_date}` -> `{end_date}`.",
        "",
        "Questo report valuta solo segnali di uscita. Gli ingressi restano quelli Baseline ufficiali.",
        "",
        "## Metriche",
        "",
        "| Modello uscita | Ann. | Delta Ann. | Max DD | Delta DD | Sharpe | Delta Sharpe | PF | Ops | Uscite forzate | 2022+ Ann. | 2022+ DD |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in results.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['delta_ann_vs_baseline'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_pct(row['delta_dd_vs_baseline'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['delta_sharpe_vs_baseline'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{int(row['forced_exits'])} | "
            f"{_pct(row['recent_annualized_return'])} | "
            f"{_pct(row['recent_max_drawdown'])} |"
        )

    lines.extend(
        [
            "",
            "## Eventi Di Uscita Forzata",
            "",
            "| Variante | Data | Entry | Prezzo uscita | Uscita ufficiale | Delta vs uscita ufficiale | Rientro ufficiale | Rientro vs uscita |",
            "|---|---|---|---:|---|---:|---|---:|",
        ]
    )
    if events.empty:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
    else:
        display = events.sort_values(["variant", "date"])
        for _, row in display.iterrows():
            lines.append(
                "| "
                f"{row['variant']} | "
                f"{row['date']} | "
                f"{row['entry_date']} | "
                f"{_pct(row['exit_price_eur'] / 100.0) if False else f'{row['exit_price_eur']:.2f}'} | "
                f"{row['official_exit_date'] or 'n/a'} | "
                f"{_pct(row['exit_vs_official_exit_pct'])} | "
                f"{row['next_buy_date'] or 'n/a'} | "
                f"{_pct(row['next_buy_vs_exit_pct'])} |"
            )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            "- `Trailing 8% puro` riduce il drawdown ma distrugge rendimento e Sharpe: resta scartato.",
            "- `SMA50 1 giorno` e' semplice ma non migliora abbastanza il drawdown rispetto al costo di rendimento.",
            "- `Trail8 confermato -5 / vol +20` e' il candidato uscita pulito da riprendere: migliora rendimento, drawdown e Sharpe senza essere aggressivo quanto il trailing puro.",
            "- `Trail8 confermato -6 / vol +20` va confrontato con attenzione per il precedente falso stop grave di gennaio 2021.",
            "",
            "Decisione provvisoria: proseguire l'analisi evento-per-evento su `Trail8 confermato -5 / vol +20` come candidato uscita principale.",
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
    results, events = _run(df)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_CSV, index=False)
    events.to_csv(OUT_EVENTS_CSV, index=False)
    _write_markdown(results, events, OUT_MD, df.index[0].date().isoformat(), df.index[-1].date().isoformat())
    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_EVENTS_CSV}")
    print(f"Saved {OUT_MD}")
    print(results[["variant", "annualized_return", "max_drawdown", "sharpe_ratio", "profit_factor", "forced_exits"]].to_string(index=False))


if __name__ == "__main__":
    main()
