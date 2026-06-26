"""
Analisi sperimentale del trailing stop 8% con conferma momentum/volume.

Questo script non modifica i segnali ufficiali. Forza VENDI solo nel frame di
backtest quando:
- il Close scende sotto trailing stop 8% calcolato sul massimo Close post-entry;
- una conferma sperimentale momentum/volume e' soddisfatta.
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
OUT_GRID_CSV = PROJECT_ROOT / "reports" / "confirmed_trailing_experiment_grid.csv"
OUT_PERIOD_CSV = PROJECT_ROOT / "reports" / "confirmed_trailing_experiment_periods.csv"
OUT_EVENTS_CSV = PROJECT_ROOT / "reports" / "confirmed_trailing_event_analysis.csv"
OUT_MD = PROJECT_ROOT / "reports" / "confirmed_trailing_experiment_results.md"

STOP_PCT = 0.08
PERIODS = {
    "2017-2020": ("2017-11-11", "2020-12-31"),
    "2021-2022": ("2021-01-01", "2022-12-31"),
    "2023-2026": ("2023-01-01", "2026-06-25"),
    "2025-2026": ("2025-01-01", "2026-06-25"),
}


def _momentum_7d(row: pd.Series) -> float:
    return float(row["Close"] / row["Close_7d_ago"] - 1.0)


def _volume_rel(row: pd.Series) -> float:
    return float(row["Volume"] / row["VolumeAvg20"] - 1.0)


def _confirmed_trailing_frame(
    df: pd.DataFrame,
    *,
    momentum_min: float | None,
    volume_rel_min: float | None,
    label: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df[["Close", "Segnale"]].copy()
    exposure = 0.0
    peak_close: float | None = None
    signals: list[str] = []
    events: list[dict] = []

    for date, row in df.iterrows():
        official = str(row["Segnale"])
        signal = official
        close = float(row["Close"])

        if official == "ACQUISTA":
            exposure = 1.0
            peak_close = close if peak_close is None else max(peak_close, close)
        elif official == "VENDI":
            exposure = 0.0
            peak_close = None
        elif exposure > 0.0 and peak_close is not None:
            peak_close = max(peak_close, close)
            stop_level = peak_close * (1.0 - STOP_PCT)
            if close <= stop_level:
                momentum_7d = _momentum_7d(row)
                volume_rel = _volume_rel(row)
                momentum_ok = momentum_min is None or momentum_7d >= momentum_min
                volume_ok = volume_rel_min is None or volume_rel >= volume_rel_min
                confirmed = momentum_ok and volume_ok

                future = df.loc[df.index > date]
                buys = future[future["Segnale"] == "ACQUISTA"]
                next_buy_date = buys.index[0] if not buys.empty else pd.NaT
                next_buy_close = float(buys.iloc[0]["Close"]) if not buys.empty else float("nan")
                next_buy_pct = next_buy_close / close - 1.0 if not pd.isna(next_buy_close) else float("nan")
                useful = bool(next_buy_close < close) if not pd.isna(next_buy_close) else False

                events.append(
                    {
                        "variant": label,
                        "date": date.strftime("%Y-%m-%d"),
                        "close": close,
                        "peak_close": peak_close,
                        "stop_level": stop_level,
                        "drawdown_from_peak": close / peak_close - 1.0,
                        "momentum_7d": momentum_7d,
                        "volume_rel": volume_rel,
                        "confirmed": confirmed,
                        "useful": useful,
                        "next_buy_date": (
                            next_buy_date.strftime("%Y-%m-%d")
                            if not pd.isna(next_buy_date)
                            else None
                        ),
                        "next_buy_close": next_buy_close,
                        "next_buy_pct": next_buy_pct,
                    }
                )

                if confirmed:
                    signal = "VENDI"
                    exposure = 0.0
                    peak_close = None

        signals.append(signal)

    out["Segnale"] = signals
    return out, pd.DataFrame(events)


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


def _period_metrics(equity_df: pd.DataFrame, start: str, end: str) -> dict[str, float]:
    subset = equity_df.loc[start:end].copy()
    if len(subset) < 2:
        return {
            "period_total_return": float("nan"),
            "period_annualized_return": float("nan"),
            "period_max_drawdown": float("nan"),
            "period_sharpe_ratio": float("nan"),
        }

    equity = subset["EquityStrategy"]
    daily_returns = subset["DailyReturnStrategy"]
    n_days = max(len(subset) - 1, 1)
    total_return = float(equity.iloc[-1] / equity.iloc[0] - 1.0)
    annualized_return = float(
        (equity.iloc[-1] / equity.iloc[0]) ** (CFG.periods_per_year / n_days) - 1.0
    )
    return {
        "period_total_return": total_return,
        "period_annualized_return": annualized_return,
        "period_max_drawdown": _max_drawdown(equity),
        "period_sharpe_ratio": _sharpe(daily_returns),
    }


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _variant_specs() -> list[tuple[str, float | None, float | None]]:
    specs: list[tuple[str, float | None, float | None]] = [
        ("baseline", None, None),
        ("trailing8_all", None, None),
    ]
    for momentum in [-0.08, -0.07, -0.06, -0.05, -0.04, -0.03]:
        for volume in [0.0, 0.10, 0.20, 0.22, 0.30, 0.40]:
            specs.append(
                (
                    f"trail8_mom_ge_{int(momentum * 100)}_vol_ge_{int(volume * 100)}",
                    momentum,
                    volume,
                )
            )
    return specs


def _write_markdown(grid: pd.DataFrame, periods: pd.DataFrame, events: pd.DataFrame, out_path: Path) -> None:
    focus_names = [
        "baseline",
        "trailing8_all",
        "trail8_mom_ge_-5_vol_ge_20",
        "trail8_mom_ge_-7_vol_ge_22",
        "trail8_mom_ge_-5_vol_ge_22",
        "trail8_mom_ge_-4_vol_ge_20",
    ]
    focus = grid[grid["variant"].isin(focus_names)]
    top_sharpe = grid.sort_values(["sharpe_ratio", "annualized_return"], ascending=False).head(10)
    top_dd = grid.sort_values(["max_drawdown", "annualized_return"], ascending=[False, False]).head(10)

    lines = [
        "# Confirmed Trailing Stop Experiment Results",
        "",
        "Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.",
        "",
        "Modello testato: trailing stop 8% su massimo Close post-ingresso, eseguito",
        "solo se la conferma momentum/volume e' vera.",
        "",
        "## Focus Variants",
        "",
        "| Variante | Ann. | Max DD | Sharpe | PF | Operazioni | Net 0,25% Sharpe | Uscite confermate | Utili prese | Inutili prese |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in focus.sort_values(["sharpe_ratio", "annualized_return"], ascending=False).iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{_ratio(row['net_025_sharpe_ratio'])} | "
            f"{int(row['confirmed_events'])} | "
            f"{int(row['useful_confirmed'])} | "
            f"{int(row['useless_confirmed'])} |"
        )

    lines.extend(
        [
            "",
            "## Top By Sharpe",
            "",
            "| Variante | Ann. | Max DD | Sharpe | PF | Operazioni |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in top_sharpe.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} |"
        )

    lines.extend(
        [
            "",
            "## Top By Drawdown",
            "",
            "| Variante | Ann. | Max DD | Sharpe | Uscite confermate |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in top_dd.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{int(row['confirmed_events'])} |"
        )

    lines.extend(
        [
            "",
            "## Sottoperiodi: Max Drawdown",
            "",
            "| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    dd_table = periods.pivot(index="variant", columns="period", values="period_max_drawdown")
    for variant in [name for name in focus_names if name in dd_table.index]:
        row = dd_table.loc[variant]
        lines.append(
            "| "
            f"{variant} | "
            f"{_pct(row['2017-2020'])} | "
            f"{_pct(row['2021-2022'])} | "
            f"{_pct(row['2023-2026'])} | "
            f"{_pct(row['2025-2026'])} |"
        )

    original = events[events["variant"] == "trailing8_all"]
    best = top_sharpe.iloc[0]
    lines.extend(
        [
            "",
            "## Eventi Originali Trailing 8%",
            "",
            f"- Eventi totali: {len(original)}.",
            f"- Utili: {int(original['useful'].sum())}.",
            f"- Inutili: {int((~original['useful']).sum())}.",
            "",
            "## Sintesi",
            "",
            f"- Migliore Sharpe in griglia: `{best['variant']}` con Sharpe "
            f"{_ratio(best['sharpe_ratio'])}, ann. {_pct(best['annualized_return'])}, "
            f"max DD {_pct(best['max_drawdown'])}.",
            "- La conferma momentum/volume evita molte uscite inutili del trailing 8%",
            "  ma cattura solo una parte delle uscite utili.",
            "- Il candidato pratico resta da validare fuori campione; la dimensione",
            "  eventi e' piccola e il rischio overfitting e' alto.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`."
        )

    source = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).set_index("Date")
    grid_rows: list[dict] = []
    period_rows: list[dict] = []
    event_frames: list[pd.DataFrame] = []

    for label, momentum_min, volume_rel_min in _variant_specs():
        if label == "baseline":
            frame = source[["Close", "Segnale"]].copy()
            events = pd.DataFrame()
        else:
            frame, events = _confirmed_trailing_frame(
                source,
                momentum_min=momentum_min,
                volume_rel_min=volume_rel_min,
                label=label,
            )

        equity, gross, _ = run_backtest(frame)
        _, net_010, _ = run_backtest(frame, transaction_cost_rate=0.001)
        _, net_025, _ = run_backtest(frame, transaction_cost_rate=0.0025)
        _, net_050, _ = run_backtest(frame, transaction_cost_rate=0.005)

        confirmed_events = int(events["confirmed"].sum()) if not events.empty else 0
        useful_confirmed = int((events["confirmed"] & events["useful"]).sum()) if not events.empty else 0
        useless_confirmed = int((events["confirmed"] & ~events["useful"]).sum()) if not events.empty else 0
        useful_total = int(events["useful"].sum()) if not events.empty else 0
        useless_total = int((~events["useful"]).sum()) if not events.empty else 0

        grid_rows.append(
            {
                "variant": label,
                "momentum_min": momentum_min,
                "volume_rel_min": volume_rel_min,
                "total_return": gross.total_return,
                "annualized_return": gross.annualized_return,
                "max_drawdown": gross.max_drawdown,
                "sharpe_ratio": gross.sharpe_ratio,
                "profit_factor": gross.profit_factor,
                "num_operations": gross.num_operations,
                "win_rate": gross.win_rate,
                "exposure_ratio": gross.exposure_ratio,
                "net_010_annualized_return": net_010.annualized_return,
                "net_010_max_drawdown": net_010.max_drawdown,
                "net_010_sharpe_ratio": net_010.sharpe_ratio,
                "net_025_annualized_return": net_025.annualized_return,
                "net_025_max_drawdown": net_025.max_drawdown,
                "net_025_sharpe_ratio": net_025.sharpe_ratio,
                "net_050_annualized_return": net_050.annualized_return,
                "net_050_max_drawdown": net_050.max_drawdown,
                "net_050_sharpe_ratio": net_050.sharpe_ratio,
                "confirmed_events": confirmed_events,
                "useful_confirmed": useful_confirmed,
                "useless_confirmed": useless_confirmed,
                "useful_total": useful_total,
                "useless_total": useless_total,
                "useless_avoided": useless_total - useless_confirmed,
            }
        )

        for period, (start, end) in PERIODS.items():
            period_rows.append(
                {
                    "variant": label,
                    "period": period,
                    **_period_metrics(equity, start, end),
                }
            )

        if not events.empty:
            event_frames.append(events)

    grid = pd.DataFrame(grid_rows).sort_values(
        ["sharpe_ratio", "annualized_return"],
        ascending=False,
    )
    periods = pd.DataFrame(period_rows)
    events = pd.concat(event_frames, ignore_index=True) if event_frames else pd.DataFrame()

    OUT_GRID_CSV.parent.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUT_GRID_CSV, index=False)
    periods.to_csv(OUT_PERIOD_CSV, index=False)
    events.to_csv(OUT_EVENTS_CSV, index=False)
    _write_markdown(grid, periods, events, OUT_MD)

    display_cols = [
        "variant",
        "annualized_return",
        "max_drawdown",
        "sharpe_ratio",
        "profit_factor",
        "num_operations",
        "net_025_sharpe_ratio",
        "confirmed_events",
        "useful_confirmed",
        "useless_confirmed",
    ]
    print(grid[display_cols].head(15).to_string(index=False))
    print("")
    print(f"Grid CSV: {OUT_GRID_CSV}")
    print(f"Period CSV: {OUT_PERIOD_CSV}")
    print(f"Event CSV: {OUT_EVENTS_CSV}")
    print(f"Report: {OUT_MD}")


if __name__ == "__main__":
    main()
