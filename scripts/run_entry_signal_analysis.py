"""
Analisi dedicata ai soli ingressi.

Questo script non modifica i segnali ufficiali. Valuta solo filtri sui nuovi
ACQUISTA, lasciando invariato il VENDI ufficiale:
- uscita sotto SMA50 per 2 giorni consecutivi.

Il benchmark decisionale e' la Baseline ufficiale.
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
OUT_CSV = PROJECT_ROOT / "reports" / "entry_signal_analysis.csv"
OUT_MD = PROJECT_ROOT / "reports" / "entry_signal_analysis.md"

RECENT_START = "2022-01-01"

ENTRY_MODELS = [
    {
        "variant": "Baseline ufficiale",
        "description": "Nessun filtro aggiuntivo sugli ingressi.",
        "rsi_max": None,
    },
    {
        "variant": "RSI <= 65",
        "description": "Blocca nuovi ACQUISTA quando RSI > 65.",
        "rsi_max": 65.0,
    },
    {
        "variant": "RSI <= 62",
        "description": "Blocca nuovi ACQUISTA quando RSI > 62.",
        "rsi_max": 62.0,
    },
    {
        "variant": "RSI <= 60",
        "description": "Blocca nuovi ACQUISTA quando RSI > 60.",
        "rsi_max": 60.0,
    },
]


def _entry_frame(df: pd.DataFrame, rsi_max: float | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    exposure = 0.0
    signals: list[str] = []
    blocked: list[dict[str, float | str | bool]] = []

    for date, row in df.iterrows():
        signal = str(row["Segnale"])
        if signal == "ACQUISTA" and rsi_max is not None and float(row["RSI"]) > rsi_max:
            blocked.append(
                {
                    "date": date.date().isoformat(),
                    "close_eur": float(row["Close_EUR"]),
                    "rsi": float(row["RSI"]),
                    "distance_sma200_pct": float(row["Close"]) / float(row["SMA200"]) - 1.0,
                    "momentum_7d_pct": float(row["Close"]) / float(row["Close_7d_ago"]) - 1.0,
                    "volume_rel_pct": float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0,
                    "was_already_exposed": exposure > 0.0,
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
    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    returns = normalized.pct_change()
    n_days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    return {
        "recent_annualized_return": float((1.0 + total_return) ** (CFG.periods_per_year / n_days) - 1.0),
        "recent_max_drawdown": _max_drawdown(normalized),
        "recent_sharpe_ratio": _sharpe(returns),
    }


def _blocked_episodes(blocked: pd.DataFrame) -> pd.DataFrame:
    if blocked.empty:
        return pd.DataFrame()
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
                "avg_rsi": float(group["rsi"].mean()),
                "max_rsi": float(group["rsi"].max()),
                "avg_distance_sma200_pct": float(group["distance_sma200_pct"].mean()),
                "avg_momentum_7d_pct": float(group["momentum_7d_pct"].mean()),
                "avg_volume_rel_pct": float(group["volume_rel_pct"].mean()),
            }
        )
    return pd.DataFrame(rows)


def _run(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, float | int | str]] = []
    episode_frames: list[pd.DataFrame] = []

    for model in ENTRY_MODELS:
        frame, blocked = _entry_frame(df, model["rsi_max"])
        equity, metrics, _ = run_backtest(frame)
        recent = _slice_metrics(equity, RECENT_START)
        new_blocked = blocked[~blocked["was_already_exposed"]] if not blocked.empty else pd.DataFrame()
        episodes = _blocked_episodes(blocked)
        if not episodes.empty:
            episodes.insert(0, "variant", model["variant"])
            episode_frames.append(episodes)

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
                "recent_annualized_return": recent["recent_annualized_return"],
                "recent_max_drawdown": recent["recent_max_drawdown"],
                "recent_sharpe_ratio": recent["recent_sharpe_ratio"],
                "blocked_new_entries": int(len(new_blocked)),
                "blocked_total_signals": int(len(blocked)),
                "blocked_episodes": int(len(episodes)),
            }
        )

    episodes_all = pd.concat(episode_frames, ignore_index=True) if episode_frames else pd.DataFrame()
    return pd.DataFrame(rows), episodes_all


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(results: pd.DataFrame, episodes: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# Entry Signal Analysis",
        "",
        "Questo report valuta solo i filtri di ingresso. Non modifica i segnali ufficiali.",
        "",
        "Regola fissa in questo test:",
        "",
        "- uscita ufficiale invariata: `VENDI` sotto SMA50 per 2 giorni consecutivi;",
        "- nessun trailing stop;",
        "- nessuna combinazione ingresso + uscita;",
        "- benchmark decisionale: `Baseline ufficiale`.",
        "",
        "## Metriche",
        "",
        "| Modello ingresso | Ann. | Max DD | Sharpe | PF | Ops | Win rate | Esp. | 2022+ Ann. | 2022+ DD | 2022+ Sharpe | Nuovi ingressi bloccati | Episodi |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in results.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{_pct(row['win_rate'])} | "
            f"{_pct(row['exposure_ratio'])} | "
            f"{_pct(row['recent_annualized_return'])} | "
            f"{_pct(row['recent_max_drawdown'])} | "
            f"{_ratio(row['recent_sharpe_ratio'])} | "
            f"{int(row['blocked_new_entries'])} | "
            f"{int(row['blocked_episodes'])} |"
        )

    lines.extend(
        [
            "",
            "## Episodi Di Nuovo Ingresso Bloccato",
            "",
            "| Variante | Inizio | Fine | Giorni | RSI medio/max | Dist SMA200 media | Mom 7g medio | Volume rel medio |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    if episodes.empty:
        lines.append("| n/a | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
    else:
        for _, row in episodes.iterrows():
            lines.append(
                "| "
                f"{row['variant']} | "
                f"{row['start_date']} | "
                f"{row['end_date']} | "
                f"{int(row['days'])} | "
                f"{row['avg_rsi']:.1f} / {row['max_rsi']:.1f} | "
                f"{_pct(row['avg_distance_sma200_pct'])} | "
                f"{_pct(row['avg_momentum_7d_pct'])} | "
                f"{_pct(row['avg_volume_rel_pct'])} |"
            )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            "- `RSI <= 65` e' il miglior candidato di ingresso pulito: migliora rendimento, drawdown, Sharpe e profit factor rispetto alla Baseline.",
            "- `RSI <= 62` produce metriche quasi identiche a `RSI <= 65`, ma blocca piu' ingressi: non aggiunge abbastanza valore per preferirlo ora.",
            "- `RSI <= 60` riduce un po' il drawdown, ma sacrifica rendimento e non migliora il 2022+ rispetto a RSI65/62.",
            "",
            "Decisione provvisoria sugli ingressi:",
            "",
            "- candidato ingresso principale: `RSI <= 65`;",
            "- `RSI <= 62` resta alternativa da tenere in osservazione;",
            "- nessuna modifica viene promossa nei segnali ufficiali.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    results, episodes = _run(df)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_CSV, index=False)
    _write_markdown(results, episodes, OUT_MD)
    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_MD}")
    print(results[["variant", "annualized_return", "max_drawdown", "sharpe_ratio", "blocked_new_entries"]].to_string(index=False))


if __name__ == "__main__":
    main()
