"""
Analisi separata delle componenti del modello.

Questo script non modifica i segnali ufficiali. Produce un report che separa:
- modelli di uscita, lasciando invariati gli ingressi Baseline;
- filtri di ingresso, lasciando invariata l'uscita ufficiale;
- combinazioni ingresso + uscita, solo come blocco finale.

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
OUT_CSV = PROJECT_ROOT / "reports" / "signal_component_analysis.csv"
OUT_MD = PROJECT_ROOT / "reports" / "signal_component_analysis.md"

RECENT_START = "2022-01-01"
STOP_PCT = 0.08


COMPONENTS = [
    {
        "section": "benchmark",
        "variant": "Baseline ufficiale",
        "description": "Ingressi e uscite ufficiali: ACQUISTA Baseline, VENDI sotto SMA50 per 2 giorni.",
        "rsi_max": None,
        "trail_mode": None,
        "momentum_min": None,
        "volume_rel_min": None,
    },
    {
        "section": "uscita",
        "variant": "Trailing 8% puro",
        "description": "Uscita se Close <= 92% del massimo Close post-ingresso. Nessuna conferma.",
        "rsi_max": None,
        "trail_mode": "all",
        "momentum_min": None,
        "volume_rel_min": None,
    },
    {
        "section": "uscita",
        "variant": "Trail8 confermato -5 / vol +20",
        "description": "Uscita trailing 8% solo con momentum 7g >= -5% e volume relativo >= +20%.",
        "rsi_max": None,
        "trail_mode": "confirmed",
        "momentum_min": -0.05,
        "volume_rel_min": 0.20,
    },
    {
        "section": "uscita",
        "variant": "Trail8 confermato -6 / vol +20",
        "description": "Come sopra, ma momentum 7g >= -6%. Piu' sensibile, piu' rischio falso stop.",
        "rsi_max": None,
        "trail_mode": "confirmed",
        "momentum_min": -0.06,
        "volume_rel_min": 0.20,
    },
    {
        "section": "ingresso",
        "variant": "RSI <= 65 solo ingresso",
        "description": "Blocca nuovi ACQUISTA se RSI > 65. Uscita ufficiale invariata.",
        "rsi_max": 65.0,
        "trail_mode": None,
        "momentum_min": None,
        "volume_rel_min": None,
    },
    {
        "section": "ingresso",
        "variant": "RSI <= 62 solo ingresso",
        "description": "Blocca nuovi ACQUISTA se RSI > 62. Uscita ufficiale invariata.",
        "rsi_max": 62.0,
        "trail_mode": None,
        "momentum_min": None,
        "volume_rel_min": None,
    },
    {
        "section": "ingresso",
        "variant": "RSI <= 60 solo ingresso",
        "description": "Blocca nuovi ACQUISTA se RSI > 60. Variante piu' restrittiva.",
        "rsi_max": 60.0,
        "trail_mode": None,
        "momentum_min": None,
        "volume_rel_min": None,
    },
    {
        "section": "combinato",
        "variant": "RSI65 + Trail8 -5 / vol +20",
        "description": "Candidato pulito: filtro ingresso RSI65 + uscita confermata -5/+20.",
        "rsi_max": 65.0,
        "trail_mode": "confirmed",
        "momentum_min": -0.05,
        "volume_rel_min": 0.20,
    },
    {
        "section": "combinato",
        "variant": "RSI65 + Trail8 -6 / vol +20",
        "description": "Candidato aggressivo intermedio: RSI65 + uscita confermata -6/+20.",
        "rsi_max": 65.0,
        "trail_mode": "confirmed",
        "momentum_min": -0.06,
        "volume_rel_min": 0.20,
    },
    {
        "section": "combinato",
        "variant": "RSI62 + Trail8 -6 / vol +20",
        "description": "Migliore per metriche: RSI62 + uscita confermata -6/+20.",
        "rsi_max": 62.0,
        "trail_mode": "confirmed",
        "momentum_min": -0.06,
        "volume_rel_min": 0.20,
    },
]


def _make_frame(
    df: pd.DataFrame,
    *,
    rsi_max: float | None,
    trail_mode: str | None,
    momentum_min: float | None,
    volume_rel_min: float | None,
) -> tuple[pd.DataFrame, int, int, int]:
    exposure = 0.0
    peak_close: float | None = None
    signals: list[str] = []
    blocked_new_entries = 0
    blocked_total = 0
    trailing_exits = 0

    for _, row in df.iterrows():
        signal = str(row["Segnale"])
        close = float(row["Close"])

        if signal == "ACQUISTA" and rsi_max is not None and float(row["RSI"]) > rsi_max:
            blocked_total += 1
            if exposure <= 0.0:
                blocked_new_entries += 1
            signal = "MANTIENI"

        if signal == "ACQUISTA":
            exposure = 1.0
            peak_close = close if peak_close is None else max(peak_close, close)
        elif signal == "VENDI":
            exposure = 0.0
            peak_close = None
        elif exposure > 0.0 and peak_close is not None and trail_mode is not None:
            peak_close = max(peak_close, close)
            if close <= peak_close * (1.0 - STOP_PCT):
                confirmed = trail_mode == "all"
                if trail_mode == "confirmed":
                    momentum_7d = close / float(row["Close_7d_ago"]) - 1.0
                    volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
                    confirmed = bool(momentum_7d >= momentum_min and volume_rel >= volume_rel_min)

                if confirmed:
                    signal = "VENDI"
                    exposure = 0.0
                    peak_close = None
                    trailing_exits += 1

        signals.append(signal)

    frame = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    frame["Segnale"] = signals
    return frame, blocked_new_entries, blocked_total, trailing_exits


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


def _buy_hold_metrics(df: pd.DataFrame) -> dict[str, float | int | str]:
    frame = df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()
    equity, _, bh = run_backtest(frame)
    recent = equity.loc[RECENT_START:].copy()
    normalized = recent["EquityBuyHold"] / float(recent["EquityBuyHold"].iloc[0])
    returns = normalized.pct_change()
    n_days = max((recent.index[-1] - recent.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    return {
        "section": "benchmark",
        "variant": "Buy & Hold ETH/EUR",
        "description": "Acquisto e mantenimento di ETH/EUR.",
        "annualized_return": bh.annualized_return,
        "max_drawdown": bh.max_drawdown,
        "sharpe_ratio": bh.sharpe_ratio,
        "profit_factor": float("nan"),
        "num_operations": 0,
        "win_rate": float("nan"),
        "exposure_ratio": 1.0,
        "recent_annualized_return": float((1.0 + total_return) ** (CFG.periods_per_year / n_days) - 1.0),
        "recent_max_drawdown": _max_drawdown(normalized),
        "recent_sharpe_ratio": _sharpe(returns),
        "blocked_new_entries": 0,
        "blocked_total": 0,
        "trailing_exits": 0,
    }


def _run(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = [_buy_hold_metrics(df)]
    for component in COMPONENTS:
        frame, blocked_new, blocked_total, trailing_exits = _make_frame(
            df,
            rsi_max=component["rsi_max"],
            trail_mode=component["trail_mode"],
            momentum_min=component["momentum_min"],
            volume_rel_min=component["volume_rel_min"],
        )
        equity, metrics, _ = run_backtest(frame)
        rows.append(
            {
                "section": component["section"],
                "variant": component["variant"],
                "description": component["description"],
                "annualized_return": metrics.annualized_return,
                "max_drawdown": metrics.max_drawdown,
                "sharpe_ratio": metrics.sharpe_ratio,
                "profit_factor": metrics.profit_factor,
                "num_operations": metrics.num_operations,
                "win_rate": metrics.win_rate,
                "exposure_ratio": metrics.exposure_ratio,
                **_slice_metrics(equity, RECENT_START),
                "blocked_new_entries": blocked_new,
                "blocked_total": blocked_total,
                "trailing_exits": trailing_exits,
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


def _table(lines: list[str], rows: pd.DataFrame, include_events: bool = True) -> None:
    columns = [
        "Modello",
        "Ann.",
        "Max DD",
        "Sharpe",
        "PF",
        "Ops",
        "Esp.",
        "2022+ Ann.",
        "2022+ DD",
        "2022+ Sharpe",
    ]
    if include_events:
        columns.extend(["Ingressi bloccati", "Uscite trail"])

    aligns = ["---"] + ["---:"] * (len(columns) - 1)
    lines.append("| " + " | ".join(columns) + " |")
    lines.append("|" + "|".join(aligns) + "|")

    for _, row in rows.iterrows():
        values = [
            row["variant"],
            _pct(row["annualized_return"]),
            _pct(row["max_drawdown"]),
            _ratio(row["sharpe_ratio"]),
            _ratio(row["profit_factor"]),
            str(int(row["num_operations"])),
            _pct(row["exposure_ratio"]),
            _pct(row["recent_annualized_return"]),
            _pct(row["recent_max_drawdown"]),
            _ratio(row["recent_sharpe_ratio"]),
        ]
        if include_events:
            values.extend([str(int(row["blocked_new_entries"])), str(int(row["trailing_exits"]))])
        lines.append("| " + " | ".join(values) + " |")


def _write_markdown(results: pd.DataFrame, out_path: Path) -> None:
    benchmark = results[results["section"] == "benchmark"].copy()
    baseline = results[results["variant"] == "Baseline ufficiale"].copy()
    exits = pd.concat([baseline, results[results["section"] == "uscita"]], ignore_index=True)
    entries = pd.concat([baseline, results[results["section"] == "ingresso"]], ignore_index=True)
    combined = pd.concat([baseline, results[results["section"] == "combinato"]], ignore_index=True)

    lines = [
        "# Signal Component Analysis",
        "",
        "Questo report separa entrate, uscite e combinazioni. Non modifica i segnali ufficiali.",
        "",
        "Performance misurata in EUR con `Close_EUR`, usando gli indicatori ufficiali.",
        "",
        "## 1. Benchmark",
        "",
    ]
    _table(lines, benchmark, include_events=False)

    lines.extend(
        [
            "",
            "## 2. Modelli Di Uscita",
            "",
            "Qui gli ingressi restano quelli Baseline. Cambia solo il modo di uscire.",
            "",
        ]
    )
    _table(lines, exits, include_events=True)

    lines.extend(
        [
            "",
            "Lettura uscite:",
            "",
            "- `Trailing 8% puro` riduce il drawdown ma peggiora rendimento e Sharpe: resta scartato.",
            "- `Trail8 confermato -5 / vol +20` e' l'uscita piu' pulita: migliora Sharpe senza il falso stop grave di gennaio 2021.",
            "- `Trail8 confermato -6 / vol +20` migliora il drawdown, ma introduce la falsa uscita grave di gennaio 2021.",
            "",
            "## 3. Modelli Di Ingresso",
            "",
            "Qui l'uscita resta quella ufficiale sotto SMA50 per 2 giorni. Cambia solo il filtro sui nuovi ACQUISTA.",
            "",
        ]
    )
    _table(lines, entries, include_events=True)

    lines.extend(
        [
            "",
            "Lettura ingressi:",
            "",
            "- `RSI <= 65` migliora Baseline in modo pulito e resta semplice da spiegare.",
            "- `RSI <= 62` e' molto vicino a `RSI <= 65`; non cambia il 2022-oggi in modo rilevante.",
            "- `RSI <= 60` riduce ancora alcuni rischi ma diventa piu' restrittivo.",
            "",
            "## 4. Combinazioni Ingresso + Uscita",
            "",
            "Questa sezione serve solo dopo aver capito separatamente entrata e uscita.",
            "",
        ]
    )
    _table(lines, combined, include_events=True)

    lines.extend(
        [
            "",
            "Lettura combinazioni:",
            "",
            "- `RSI65 + Trail8 -5 / vol +20` e' il candidato prudente principale: meno performante del -6, ma piu' pulito sugli eventi.",
            "- `RSI62/65 + Trail8 -6 / vol +20` sono piu' forti numericamente, ma hanno la falsa uscita grave di gennaio 2021.",
            "- Per decidere il modello operativo non bisogna promuovere la combinazione migliore per numero assoluto; serve prima decidere se accettare o correggere il problema gennaio 2021.",
            "",
            "## Decisione Operativa Provvisoria",
            "",
            "- Uscita candidata pulita: `Trail8 confermato -5 / vol +20`.",
            "- Ingresso candidato pulito: `RSI <= 65`.",
            "- Combinazione candidata prudente: `RSI65 + Trail8 -5 / vol +20`.",
            "- Combinazione candidata aggressiva: `RSI62/65 + Trail8 -6 / vol +20`, da correggere per il caso gennaio 2021.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")
    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    results = _run(df)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_CSV, index=False)
    _write_markdown(results, OUT_MD)
    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_MD}")
    print(results[["section", "variant", "annualized_return", "max_drawdown", "sharpe_ratio"]].to_string(index=False))


if __name__ == "__main__":
    main()
