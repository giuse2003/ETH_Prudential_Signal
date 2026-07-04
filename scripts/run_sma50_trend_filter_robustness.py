"""
Robustezza del candidato: rimuovere `SMA50 > SMA200` dagli ingressi.

Questo script non modifica i segnali ufficiali. Usa il runner base
`run_sma50_trend_filter_removal.py` e aggiunge:
- confronto EUR/USD;
- finestre storiche e rolling windows;
- stress costi sintetico;
- audit dei soli trade aperti quando `SMA50 <= SMA200`.
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
from scripts.run_sma50_trend_filter_removal import (
    _baseline_frame,
    _slice_metrics,
    _without_sma50_filter_frame,
)


SOURCE_CSV = PROJECT_ROOT / "data" / "indicators_with_signals.csv"
OUT_WINDOWS_CSV = PROJECT_ROOT / "reports" / "sma50_trend_filter_robustness_windows.csv"
OUT_ROLLING_CSV = PROJECT_ROOT / "reports" / "sma50_trend_filter_robustness_rolling.csv"
OUT_CURRENCY_CSV = PROJECT_ROOT / "reports" / "sma50_trend_filter_robustness_currency.csv"
OUT_EXTRA_TRADES_CSV = PROJECT_ROOT / "reports" / "sma50_trend_filter_robustness_extra_trades.csv"
OUT_MD = PROJECT_ROOT / "reports" / "sma50_trend_filter_robustness.md"

COST_FOR_GATE = 0.0025
ROLLING_DAYS = 730
ROLLING_STEP_DAYS = 90

WINDOWS = {
    "2018-2019": ("2018-05-29", "2019-12-31"),
    "2020-2021": ("2020-01-01", "2021-12-31"),
    "2022-2023": ("2022-01-01", "2023-12-31"),
    "2024-2026": ("2024-01-01", "2026-07-03"),
    "recent_2022_today": ("2022-01-01", "2026-07-03"),
}


def _load_data() -> pd.DataFrame:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`.")
    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    return df.dropna(
        subset=[
            "Close",
            "Close_EUR",
            "SMA50",
            "SMA200",
            "RSI",
            "VolumeAvg20",
            f"Close_{CFG.momentum_days}d_ago",
        ]
    ).copy()


def _frames(df: pd.DataFrame, currency: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if currency == "EUR":
        base = _baseline_frame(df)
        variant, events = _without_sma50_filter_frame(df)
        return base, variant, events

    variant_eur, events = _without_sma50_filter_frame(df)
    base = df[["Close", "Segnale"]].copy()
    variant = df[["Close"]].copy()
    variant["Segnale"] = variant_eur["Segnale"]
    return base, variant, events


def _currency_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, float | int | str]] = []
    for currency in ["EUR", "USD"]:
        base, variant, _ = _frames(df, currency)
        for name, frame in [("baseline", base), ("no_sma50_gt_sma200_entry", variant)]:
            _, gross, _ = run_backtest(frame)
            _, cost, _ = run_backtest(frame, transaction_cost_rate=COST_FOR_GATE)
            rows.append(
                {
                    "currency": currency,
                    "variant": name,
                    "gross_annualized_return": gross.annualized_return,
                    "gross_max_drawdown": gross.max_drawdown,
                    "gross_sharpe_ratio": gross.sharpe_ratio,
                    "gross_profit_factor": gross.profit_factor,
                    "cost_025_annualized_return": cost.annualized_return,
                    "cost_025_max_drawdown": cost.max_drawdown,
                    "cost_025_sharpe_ratio": cost.sharpe_ratio,
                    "cost_025_profit_factor": cost.profit_factor,
                    "num_operations": gross.num_operations,
                    "win_rate": gross.win_rate,
                }
            )
    return pd.DataFrame(rows)


def _window_summary(base: pd.DataFrame, variant: pd.DataFrame) -> pd.DataFrame:
    base_eq, _, _ = run_backtest(base)
    variant_eq, _, _ = run_backtest(variant)
    rows: list[dict[str, float | str]] = []
    for name, (start, end) in WINDOWS.items():
        bm = _slice_metrics(base_eq, start, end)
        vm = _slice_metrics(variant_eq, start, end)
        rows.append(
            {
                "window": name,
                "start": start,
                "end": end,
                "baseline_total_return": bm["total_return"],
                "variant_total_return": vm["total_return"],
                "delta_total_return": vm["total_return"] - bm["total_return"],
                "baseline_annualized_return": bm["annualized_return"],
                "variant_annualized_return": vm["annualized_return"],
                "delta_annualized_return": vm["annualized_return"] - bm["annualized_return"],
                "baseline_max_drawdown": bm["max_drawdown"],
                "variant_max_drawdown": vm["max_drawdown"],
                "delta_max_drawdown": vm["max_drawdown"] - bm["max_drawdown"],
                "baseline_sharpe": bm["sharpe_ratio"],
                "variant_sharpe": vm["sharpe_ratio"],
                "delta_sharpe": vm["sharpe_ratio"] - bm["sharpe_ratio"],
            }
        )
    return pd.DataFrame(rows)


def _rolling_windows(base: pd.DataFrame, variant: pd.DataFrame) -> pd.DataFrame:
    base_eq, _, _ = run_backtest(base)
    variant_eq, _, _ = run_backtest(variant)
    start = max(base.index.min(), variant.index.min())
    end = min(base.index.max(), variant.index.max())
    rows: list[dict[str, float | str]] = []
    cursor = start
    while cursor + pd.Timedelta(days=ROLLING_DAYS) <= end:
        window_end = cursor + pd.Timedelta(days=ROLLING_DAYS)
        bm = _slice_metrics(base_eq, cursor.strftime("%Y-%m-%d"), window_end.strftime("%Y-%m-%d"))
        vm = _slice_metrics(variant_eq, cursor.strftime("%Y-%m-%d"), window_end.strftime("%Y-%m-%d"))
        rows.append(
            {
                "start": cursor.date().isoformat(),
                "end": window_end.date().isoformat(),
                "delta_total_return": vm["total_return"] - bm["total_return"],
                "delta_annualized_return": vm["annualized_return"] - bm["annualized_return"],
                "delta_max_drawdown": vm["max_drawdown"] - bm["max_drawdown"],
                "delta_sharpe": vm["sharpe_ratio"] - bm["sharpe_ratio"],
                "baseline_total_return": bm["total_return"],
                "variant_total_return": vm["total_return"],
            }
        )
        cursor += pd.Timedelta(days=ROLLING_STEP_DAYS)
    return pd.DataFrame(rows)


def _completed_trades(frame: pd.DataFrame, source_df: pd.DataFrame, extra_entry_dates: set[str]) -> pd.DataFrame:
    rows: list[dict[str, float | int | str | bool]] = []
    exposed = False
    entry: pd.Timestamp | None = None
    for date, row in frame.iterrows():
        signal = str(row["Segnale"])
        if signal == "ACQUISTA" and not exposed:
            exposed = True
            entry = date
        elif signal == "VENDI" and exposed and entry is not None:
            entry_price = float(frame.loc[entry, "Close"])
            exit_price = float(row["Close"])
            path = frame.loc[entry:date, "Close"] / entry_price
            dd = path / path.cummax() - 1.0
            rows.append(
                {
                    "entry_date": entry.date().isoformat(),
                    "exit_date": date.date().isoformat(),
                    "days": int((date - entry).days),
                    "trade_return": exit_price / entry_price - 1.0,
                    "trade_drawdown": float(dd.min()),
                    "entry_sma50_gt_sma200": bool(source_df.loc[entry, "SMA50"] > source_df.loc[entry, "SMA200"]),
                    "entry_was_unlocked_by_removal": entry.date().isoformat() in extra_entry_dates,
                    "entry_rsi": float(source_df.loc[entry, "RSI"]),
                    "entry_momentum_7d": float(source_df.loc[entry, "Close"] / source_df.loc[entry, f"Close_{CFG.momentum_days}d_ago"] - 1.0),
                    "entry_volume_rel": float(source_df.loc[entry, "Volume"] / source_df.loc[entry, "VolumeAvg20"] - 1.0),
                }
            )
            exposed = False
            entry = None
    return pd.DataFrame(rows)


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _promotion_gate(currency: pd.DataFrame, windows: pd.DataFrame, rolling: pd.DataFrame) -> list[tuple[str, bool, str]]:
    eur = currency[currency["currency"] == "EUR"].set_index("variant")
    base = eur.loc["baseline"]
    variant = eur.loc["no_sma50_gt_sma200_entry"]
    rolling_positive = float((rolling["delta_total_return"] > 0.0).mean()) if not rolling.empty else 0.0
    worst_window_dd_delta = float(windows["delta_max_drawdown"].min())
    worst_window_return_delta = float(windows["delta_total_return"].min())

    return [
        (
            "Rendimento annuo completo migliora",
            bool(variant["gross_annualized_return"] > base["gross_annualized_return"]),
            f"{_pct(variant['gross_annualized_return'] - base['gross_annualized_return'])}",
        ),
        (
            "Sharpe completo migliora",
            bool(variant["gross_sharpe_ratio"] > base["gross_sharpe_ratio"]),
            f"{_ratio(variant['gross_sharpe_ratio'] - base['gross_sharpe_ratio'])}",
        ),
        (
            "Stress costi 0,25% resta positivo",
            bool(variant["cost_025_annualized_return"] > base["cost_025_annualized_return"]),
            f"{_pct(variant['cost_025_annualized_return'] - base['cost_025_annualized_return'])}",
        ),
        (
            "Finestre rolling positive almeno 60%",
            bool(rolling_positive >= 0.60),
            f"{rolling_positive * 100:.1f}%",
        ),
        (
            "Nessuna finestra peggiora DD oltre 10 punti",
            bool(worst_window_dd_delta >= -0.10),
            f"peggiore {_pct(worst_window_dd_delta)}",
        ),
        (
            "Nessuna finestra perde oltre 20 punti di rendimento",
            bool(worst_window_return_delta >= -0.20),
            f"peggiore {_pct(worst_window_return_delta)}",
        ),
    ]


def _write_markdown(
    currency: pd.DataFrame,
    windows: pd.DataFrame,
    rolling: pd.DataFrame,
    extra_trades: pd.DataFrame,
    gate: list[tuple[str, bool, str]],
    out_path: Path,
) -> None:
    eur = currency[currency["currency"] == "EUR"].set_index("variant")
    base = eur.loc["baseline"]
    variant = eur.loc["no_sma50_gt_sma200_entry"]
    rolling_positive = float((rolling["delta_total_return"] > 0.0).mean()) if not rolling.empty else float("nan")
    rolling_sharpe_positive = float((rolling["delta_sharpe"] > 0.0).mean()) if not rolling.empty else float("nan")
    unlocked = extra_trades[extra_trades["entry_was_unlocked_by_removal"]] if not extra_trades.empty else pd.DataFrame()

    lines = [
        "# SMA50 Trend Filter Robustness",
        "",
        "Verifica aggiuntiva del candidato: rimuovere `SMA50 > SMA200` dagli ingressi.",
        "",
        "## Currency Check",
        "",
        "| Valuta | Variante | Ann. | Max DD | Sharpe | PF | Ann. con costi 0,25% |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in currency.iterrows():
        lines.append(
            "| "
            f"{row['currency']} | {row['variant']} | "
            f"{_pct(row['gross_annualized_return'])} | "
            f"{_pct(row['gross_max_drawdown'])} | "
            f"{_ratio(row['gross_sharpe_ratio'])} | "
            f"{_ratio(row['gross_profit_factor'])} | "
            f"{_pct(row['cost_025_annualized_return'])} |"
        )

    lines.extend(
        [
            "",
            "## Finestre Storiche",
            "",
            "| Finestra | Delta Total | Delta Ann. | Delta DD | Delta Sharpe |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in windows.iterrows():
        lines.append(
            "| "
            f"{row['window']} | "
            f"{_pct(row['delta_total_return'])} | "
            f"{_pct(row['delta_annualized_return'])} | "
            f"{_pct(row['delta_max_drawdown'])} | "
            f"{_ratio(row['delta_sharpe'])} |"
        )

    lines.extend(
        [
            "",
            "## Rolling Windows",
            "",
            f"- Finestre rolling 730 giorni: {len(rolling)}.",
            f"- Delta rendimento positivo: {rolling_positive * 100:.1f}%.",
            f"- Delta Sharpe positivo: {rolling_sharpe_positive * 100:.1f}%.",
            f"- Peggior delta rendimento rolling: {_pct(rolling['delta_total_return'].min())}.",
            f"- Miglior delta rendimento rolling: {_pct(rolling['delta_total_return'].max())}.",
            "",
            "## Trade Sbloccati",
            "",
            f"- Trade aperti quando la Baseline avrebbe bloccato `SMA50 <= SMA200`: {len(unlocked)}.",
            f"- Rendimento medio di questi trade: {_pct(unlocked['trade_return'].mean() if not unlocked.empty else float('nan'))}.",
            f"- Win rate di questi trade: {_pct((unlocked['trade_return'] > 0.0).mean() if not unlocked.empty else float('nan'))}.",
            "",
            "| Entry | Exit | Return | DD trade | RSI | Mom 7g | Volume rel |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in unlocked.iterrows():
        lines.append(
            "| "
            f"{row['entry_date']} | {row['exit_date']} | "
            f"{_pct(row['trade_return'])} | "
            f"{_pct(row['trade_drawdown'])} | "
            f"{float(row['entry_rsi']):.2f} | "
            f"{_pct(row['entry_momentum_7d'])} | "
            f"{_pct(row['entry_volume_rel'])} |"
        )

    lines.extend(
        [
            "",
            "## Promotion Gate",
            "",
            "| Criterio | Esito | Valore |",
            "|---|---:|---:|",
        ]
    )
    for label, passed, value in gate:
        lines.append(f"| {label} | {'PASS' if passed else 'FAIL'} | {value} |")

    passed_count = sum(1 for _, passed, _ in gate if passed)
    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Delta annualizzato EUR completo: {_pct(variant['gross_annualized_return'] - base['gross_annualized_return'])}.",
            f"- Gate superati: {passed_count}/{len(gate)}.",
            "- Il candidato resta interessante se vince sui costi e su abbastanza finestre rolling.",
            "- Non va promosso se il miglioramento dipende da pochi ingressi e peggiora troppo una finestra storica.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    df = _load_data()
    base_eur, variant_eur, events = _frames(df, "EUR")
    extra_entry_dates = set(
        events[
            (events["event_type"] == "new_entry_without_sma50_filter")
            & (~events["sma50_gt_sma200"])
        ]["date"]
    )

    currency = _currency_summary(df)
    windows = _window_summary(base_eur, variant_eur)
    rolling = _rolling_windows(base_eur, variant_eur)
    extra_trades = _completed_trades(variant_eur, df, extra_entry_dates)
    gate = _promotion_gate(currency, windows, rolling)

    OUT_WINDOWS_CSV.parent.mkdir(parents=True, exist_ok=True)
    windows.to_csv(OUT_WINDOWS_CSV, index=False)
    rolling.to_csv(OUT_ROLLING_CSV, index=False)
    currency.to_csv(OUT_CURRENCY_CSV, index=False)
    extra_trades.to_csv(OUT_EXTRA_TRADES_CSV, index=False)
    _write_markdown(currency, windows, rolling, extra_trades, gate, OUT_MD)

    print(f"Saved {OUT_WINDOWS_CSV}")
    print(f"Saved {OUT_ROLLING_CSV}")
    print(f"Saved {OUT_CURRENCY_CSV}")
    print(f"Saved {OUT_EXTRA_TRADES_CSV}")
    print(f"Saved {OUT_MD}")
    print("")
    print("Promotion gate")
    for label, passed, value in gate:
        print(f"- {'PASS' if passed else 'FAIL'}: {label} ({value})")


if __name__ == "__main__":
    main()
