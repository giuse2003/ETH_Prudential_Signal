"""
Guardrail sperimentali per rimuovere `SMA50 > SMA200` dagli ingressi.

Questo script non modifica la Baseline. Testa varianti in cui la condizione
SMA50>SMA200 viene rimossa, ma solo gli ingressi anticipati con SMA50<=SMA200
possono ricevere un filtro aggiuntivo anti-falso-rimbalzo.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import run_backtest
from config import CFG
from scripts.run_sma50_trend_filter_removal import _baseline_frame, _slice_metrics
from scripts.run_sma50_trend_filter_robustness import _rolling_windows
from strategy.signals import (
    ENTRY_RSI_MAX,
    TRAILING_MOMENTUM_MIN,
    TRAILING_STOP_PCT,
    TRAILING_VOLUME_REL_MIN,
)


SOURCE_CSV = PROJECT_ROOT / "data" / "indicators_with_signals.csv"
OUT_CSV = PROJECT_ROOT / "reports" / "sma50_trend_filter_guardrails.csv"
OUT_MD = PROJECT_ROOT / "reports" / "sma50_trend_filter_guardrails.md"

Guard = Callable[[pd.Series, float, float], bool]

GUARDS: dict[str, tuple[str, Guard]] = {
    "remove_pure": (
        "Rimuove SMA50>SMA200 senza guardrail.",
        lambda row, momentum_7d, volume_rel: True,
    ),
    "guard_volrel_ge_15": (
        "Sugli ingressi con SMA50<=SMA200 richiede volume relativo >= +15%.",
        lambda row, momentum_7d, volume_rel: volume_rel >= 0.15,
    ),
    "guard_volrel_ge_20": (
        "Sugli ingressi con SMA50<=SMA200 richiede volume relativo >= +20%.",
        lambda row, momentum_7d, volume_rel: volume_rel >= 0.20,
    ),
    "guard_rsi_le_62": (
        "Sugli ingressi con SMA50<=SMA200 richiede RSI <= 62.",
        lambda row, momentum_7d, volume_rel: float(row["RSI"]) <= 62.0,
    ),
    "guard_mom_le_10": (
        "Sugli ingressi con SMA50<=SMA200 richiede momentum 7g <= +10%.",
        lambda row, momentum_7d, volume_rel: momentum_7d <= 0.10,
    ),
    "guard_rsi_le_62_or_vol15": (
        "Sugli ingressi con SMA50<=SMA200 richiede RSI <= 62 oppure volume relativo >= +15%.",
        lambda row, momentum_7d, volume_rel: float(row["RSI"]) <= 62.0 or volume_rel >= 0.15,
    ),
}


def _load_data() -> pd.DataFrame:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")
    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    return df.dropna(
        subset=[
            "Close_EUR",
            "SMA50",
            "SMA200",
            "RSI",
            "VolumeAvg20",
            f"Close_{CFG.momentum_days}d_ago",
        ]
    ).copy()


def _candidate_frame(df: pd.DataFrame, guard: Guard) -> tuple[pd.DataFrame, int, int]:
    exposure = False
    peak_close: float | None = None
    signals: list[str] = []
    unlocked_entries = 0
    blocked_entries = 0

    for _, row in df.iterrows():
        close = float(row["Close"])
        sma50 = float(row["SMA50"])
        sma200 = float(row["SMA200"])
        rsi = float(row["RSI"])
        volume = float(row["Volume"])
        volume_avg20 = float(row["VolumeAvg20"])
        close_ago = float(row[f"Close_{CFG.momentum_days}d_ago"])
        momentum_7d = close / close_ago - 1.0
        volume_rel = volume / volume_avg20 - 1.0

        buy_without_sma50_gate = (
            close > sma200
            and rsi >= 40.0
            and close > close_ago
            and volume > volume_avg20
        )
        filtered_new_entry = buy_without_sma50_gate and rsi <= ENTRY_RSI_MAX
        unlocked_by_removal = sma50 <= sma200

        if buy_without_sma50_gate and not exposure and filtered_new_entry and unlocked_by_removal:
            if not guard(row, momentum_7d, volume_rel):
                signals.append("MANTIENI")
                blocked_entries += 1
                continue

        if close < sma50:
            signals.append("VENDI")
            exposure = False
            peak_close = None
            continue

        if buy_without_sma50_gate:
            if not exposure and filtered_new_entry:
                signals.append("ACQUISTA")
                exposure = True
                peak_close = close
                if unlocked_by_removal:
                    unlocked_entries += 1
            elif exposure:
                peak_close = max(peak_close if peak_close is not None else close, close)
                signals.append("MANTIENI")
            else:
                signals.append("MANTIENI")
            continue

        signal = "MANTIENI"
        if exposure:
            peak_close = max(peak_close if peak_close is not None else close, close)
            stop_hit = close <= peak_close * (1.0 - TRAILING_STOP_PCT)
            if stop_hit:
                trail_confirmed = (
                    momentum_7d >= TRAILING_MOMENTUM_MIN
                    and volume_rel >= TRAILING_VOLUME_REL_MIN
                )
                if trail_confirmed:
                    signal = "VENDI"
                    exposure = False
                    peak_close = None
        signals.append(signal)

    out = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    out["Segnale"] = signals
    return out, unlocked_entries, blocked_entries


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(results: pd.DataFrame, out_path: Path) -> None:
    ordered = results.sort_values(["passes_gate", "sharpe_ratio", "annualized_return"], ascending=False)
    lines = [
        "# SMA50 Trend Filter Guardrails",
        "",
        "Test esplorativo: rimuovere `SMA50 > SMA200` ma filtrare solo gli ingressi anticipati",
        "in cui `SMA50 <= SMA200`.",
        "",
        "## Risultati",
        "",
        "| Variante | Ann. | Max DD | Sharpe | PF | Ops | Delta 2018-2019 | Delta recente | Rolling + | Gate |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in ordered.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{_pct(row['delta_2018_2019_total_return'])} | "
            f"{_pct(row['delta_recent_total_return'])} | "
            f"{_pct(row['rolling_positive_ratio'])} | "
            f"{'PASS' if row['passes_gate'] else 'FAIL'} |"
        )

    best = ordered.iloc[0]
    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Migliore candidato per gate e Sharpe: `{best['variant']}`.",
            f"- Annualizzato: {_pct(best['annualized_return'])}; Sharpe: {_ratio(best['sharpe_ratio'])}; PF: {_ratio(best['profit_factor'])}.",
            "- Il guardrail serve soprattutto a evitare il falso rimbalzo del 2019 che rende fragile la rimozione pura.",
            "- Questi candidati non sono ancora Baseline: vanno confrontati con il principio di semplicita' e con un audit evento-per-evento.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df = _load_data()
    base = _baseline_frame(df)
    base_eq, base_metrics, _ = run_backtest(base)
    base_2019 = _slice_metrics(base_eq, "2018-05-29", "2019-12-31")
    base_recent = _slice_metrics(base_eq, "2022-01-01", df.index[-1].strftime("%Y-%m-%d"))

    rows: list[dict[str, float | int | str | bool]] = []
    for name, (description, guard) in GUARDS.items():
        frame, unlocked_entries, blocked_entries = _candidate_frame(df, guard)
        equity, metrics, _ = run_backtest(frame)
        m2019 = _slice_metrics(equity, "2018-05-29", "2019-12-31")
        recent = _slice_metrics(equity, "2022-01-01", df.index[-1].strftime("%Y-%m-%d"))
        rolling = _rolling_windows(base, frame)
        rolling_positive_ratio = float((rolling["delta_total_return"] > 0.0).mean())
        delta_2019 = m2019["total_return"] - base_2019["total_return"]
        delta_recent = recent["total_return"] - base_recent["total_return"]
        passes_gate = (
            metrics.annualized_return > base_metrics.annualized_return
            and metrics.sharpe_ratio > base_metrics.sharpe_ratio
            and metrics.max_drawdown >= base_metrics.max_drawdown - 0.01
            and rolling_positive_ratio >= 0.60
            and delta_2019 >= 0.0
            and delta_recent >= 0.0
        )
        rows.append(
            {
                "variant": name,
                "description": description,
                "annualized_return": metrics.annualized_return,
                "max_drawdown": metrics.max_drawdown,
                "sharpe_ratio": metrics.sharpe_ratio,
                "profit_factor": metrics.profit_factor,
                "num_operations": metrics.num_operations,
                "win_rate": metrics.win_rate,
                "unlocked_entries": unlocked_entries,
                "blocked_entries": blocked_entries,
                "delta_2018_2019_total_return": delta_2019,
                "delta_recent_total_return": delta_recent,
                "rolling_positive_ratio": rolling_positive_ratio,
                "passes_gate": passes_gate,
            }
        )

    results = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_CSV, index=False)
    _write_markdown(results, OUT_MD)

    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_MD}")
    print("")
    print(results.sort_values(["passes_gate", "sharpe_ratio"], ascending=False).to_string(index=False))


if __name__ == "__main__":
    main()
