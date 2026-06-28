"""
Stress test parametrico del candidato combinato.

Questo script non modifica i segnali ufficiali. Valida se il candidato:
- RSI massimo sugli ingressi;
- trailing stop 8%;
- conferma momentum 7g;
- conferma volume relativo;

funziona in una zona robusta di parametri oppure solo in un punto specifico.

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
OUT_GRID_CSV = PROJECT_ROOT / "reports" / "combined_parameter_stress_grid.csv"
OUT_PERIODS_CSV = PROJECT_ROOT / "reports" / "combined_parameter_stress_periods.csv"
OUT_WALK_CSV = PROJECT_ROOT / "reports" / "combined_parameter_stress_walkforward.csv"
OUT_MD = PROJECT_ROOT / "reports" / "combined_parameter_stress.md"

STOP_PCT = 0.08
RECENT_START = "2022-01-01"
RSI_VALUES = [60, 62, 65, 68, 70]
MOMENTUM_VALUES = [-0.06, -0.05, -0.04]
VOLUME_VALUES = [0.10, 0.20, 0.30, 0.40]

PERIODS = {
    "2017-2020": ("2017-11-11", "2020-12-31"),
    "2021-2022": ("2021-01-01", "2022-12-31"),
    "2023-2026": ("2023-01-01", "2026-06-27"),
    "2025-2026": ("2025-01-01", "2026-06-27"),
}

WALK_FORWARD_SPLITS = [
    ("train_2017_2020", "2017-11-11", "2020-12-31", "test_2021_2022", "2021-01-01", "2022-12-31"),
    ("train_2017_2022", "2017-11-11", "2022-12-31", "test_2023_2026", "2023-01-01", "2026-06-27"),
    ("train_2017_2024", "2017-11-11", "2024-12-31", "test_2025_2026", "2025-01-01", "2026-06-27"),
]


def _variant_name(rsi_max: int | None, momentum_min: float | None, volume_rel_min: float | None) -> str:
    if rsi_max is None and momentum_min is None and volume_rel_min is None:
        return "baseline"
    if momentum_min is None or volume_rel_min is None:
        return f"rsi_le_{rsi_max}"
    rsi_part = "no_rsi" if rsi_max is None else f"rsi{rsi_max}"
    momentum_part = f"mom{int(momentum_min * 100)}"
    volume_part = f"vol{int(volume_rel_min * 100)}"
    return f"{rsi_part}_trail8_{momentum_part}_{volume_part}"


def _make_frame(
    df: pd.DataFrame,
    *,
    rsi_max: int | None,
    momentum_min: float | None,
    volume_rel_min: float | None,
) -> tuple[pd.DataFrame, int]:
    exposure = 0.0
    peak_close: float | None = None
    signals: list[str] = []
    confirmed_exits = 0

    for _, row in df.iterrows():
        signal = str(row["Segnale"])
        close = float(row["Close"])

        if signal == "ACQUISTA" and rsi_max is not None and float(row["RSI"]) > rsi_max:
            signal = "MANTIENI"

        if signal == "ACQUISTA":
            exposure = 1.0
            peak_close = close if peak_close is None else max(peak_close, close)
        elif signal == "VENDI":
            exposure = 0.0
            peak_close = None
        elif exposure > 0.0 and peak_close is not None and momentum_min is not None and volume_rel_min is not None:
            peak_close = max(peak_close, close)
            if close <= peak_close * (1.0 - STOP_PCT):
                momentum_7d = close / float(row["Close_7d_ago"]) - 1.0
                volume_rel = float(row["Volume"]) / float(row["VolumeAvg20"]) - 1.0
                if momentum_7d >= momentum_min and volume_rel >= volume_rel_min:
                    signal = "VENDI"
                    exposure = 0.0
                    peak_close = None
                    confirmed_exits += 1

        signals.append(signal)

    out = df[["Close_EUR"]].rename(columns={"Close_EUR": "Close"}).copy()
    out["Segnale"] = signals
    return out, confirmed_exits


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


def _slice_metrics(equity: pd.DataFrame, start: str, end: str | None = None) -> dict[str, float]:
    subset = equity.loc[start:end].copy()
    if len(subset) < 2:
        return {
            "total_return": float("nan"),
            "annualized_return": float("nan"),
            "max_drawdown": float("nan"),
            "sharpe_ratio": float("nan"),
            "exposure_ratio": float("nan"),
            "turnover": float("nan"),
        }

    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    daily_returns = normalized.pct_change()
    n_days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    annualized_return = float((1.0 + total_return) ** (CFG.periods_per_year / n_days) - 1.0)
    return {
        "total_return": total_return,
        "annualized_return": annualized_return,
        "max_drawdown": _max_drawdown(normalized),
        "sharpe_ratio": _sharpe(daily_returns),
        "exposure_ratio": float(subset["EffectiveExposure"].gt(0.0).mean()),
        "turnover": float(subset["Turnover"].sum()),
    }


def _candidate_specs() -> list[dict[str, int | float | None | str]]:
    specs: list[dict[str, int | float | None | str]] = [
        {
            "variant": "baseline",
            "rsi_max": None,
            "momentum_min": None,
            "volume_rel_min": None,
            "kind": "baseline",
        }
    ]

    for rsi in RSI_VALUES:
        specs.append(
            {
                "variant": _variant_name(rsi, None, None),
                "rsi_max": rsi,
                "momentum_min": None,
                "volume_rel_min": None,
                "kind": "rsi_only",
            }
        )

    for momentum in MOMENTUM_VALUES:
        for volume in VOLUME_VALUES:
            specs.append(
                {
                    "variant": _variant_name(None, momentum, volume),
                    "rsi_max": None,
                    "momentum_min": momentum,
                    "volume_rel_min": volume,
                    "kind": "trail_only",
                }
            )

    for rsi in RSI_VALUES:
        for momentum in MOMENTUM_VALUES:
            for volume in VOLUME_VALUES:
                specs.append(
                    {
                        "variant": _variant_name(rsi, momentum, volume),
                        "rsi_max": rsi,
                        "momentum_min": momentum,
                        "volume_rel_min": volume,
                        "kind": "combined",
                    }
                )
    return specs


def _run_grid(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, pd.DataFrame]]:
    rows: list[dict[str, float | int | str | None]] = []
    period_rows: list[dict[str, float | int | str | None]] = []
    equities: dict[str, pd.DataFrame] = {}

    for spec in _candidate_specs():
        frame, confirmed_exits = _make_frame(
            df,
            rsi_max=spec["rsi_max"],
            momentum_min=spec["momentum_min"],
            volume_rel_min=spec["volume_rel_min"],
        )
        equity, metrics, _ = run_backtest(frame)
        equities[str(spec["variant"])] = equity
        recent = _slice_metrics(equity, RECENT_START)
        rows.append(
            {
                **spec,
                "confirmed_exits": confirmed_exits,
                "full_total_return": metrics.total_return,
                "full_annualized_return": metrics.annualized_return,
                "full_max_drawdown": metrics.max_drawdown,
                "full_sharpe_ratio": metrics.sharpe_ratio,
                "full_profit_factor": metrics.profit_factor,
                "full_num_operations": metrics.num_operations,
                "full_win_rate": metrics.win_rate,
                "full_exposure_ratio": metrics.exposure_ratio,
                "full_turnover": metrics.turnover,
                "recent_total_return": recent["total_return"],
                "recent_annualized_return": recent["annualized_return"],
                "recent_max_drawdown": recent["max_drawdown"],
                "recent_sharpe_ratio": recent["sharpe_ratio"],
                "recent_exposure_ratio": recent["exposure_ratio"],
                "recent_turnover": recent["turnover"],
            }
        )
        for period, (start, end) in PERIODS.items():
            period_rows.append(
                {
                    "variant": spec["variant"],
                    "kind": spec["kind"],
                    "rsi_max": spec["rsi_max"],
                    "momentum_min": spec["momentum_min"],
                    "volume_rel_min": spec["volume_rel_min"],
                    "period": period,
                    **_slice_metrics(equity, start, end),
                }
            )

    grid = pd.DataFrame(rows)
    periods = pd.DataFrame(period_rows)

    robustness = (
        periods.groupby("variant")
        .agg(
            median_period_sharpe=("sharpe_ratio", "median"),
            min_period_sharpe=("sharpe_ratio", "min"),
            median_period_ann=("annualized_return", "median"),
            worst_period_drawdown=("max_drawdown", "min"),
            positive_periods=("annualized_return", lambda s: int((s > 0).sum())),
            measured_periods=("annualized_return", "count"),
        )
        .reset_index()
    )
    grid = grid.merge(robustness, on="variant", how="left")
    grid["robustness_score"] = (
        grid["full_sharpe_ratio"].fillna(0.0)
        + grid["median_period_sharpe"].fillna(0.0)
        + grid["recent_sharpe_ratio"].fillna(0.0)
        + grid["full_annualized_return"].fillna(0.0)
        + grid["full_max_drawdown"].fillna(-1.0)
    )
    return grid, periods, equities


def _walk_forward(grid: pd.DataFrame, equities: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, float | str]] = []
    candidates = grid[grid["kind"] == "combined"].copy()
    baseline_equity = equities["baseline"]

    for train_label, train_start, train_end, test_label, test_start, test_end in WALK_FORWARD_SPLITS:
        train_rows: list[dict[str, float | str]] = []
        for _, row in candidates.iterrows():
            variant = str(row["variant"])
            equity = equities[variant]
            train_metrics = _slice_metrics(equity, train_start, train_end)
            train_rows.append(
                {
                    "variant": variant,
                    "train_sharpe": train_metrics["sharpe_ratio"],
                    "train_annualized_return": train_metrics["annualized_return"],
                    "train_max_drawdown": train_metrics["max_drawdown"],
                }
            )

        train_table = pd.DataFrame(train_rows).sort_values(
            ["train_sharpe", "train_annualized_return", "train_max_drawdown"],
            ascending=[False, False, False],
        )
        selected = str(train_table.iloc[0]["variant"])
        selected_equity = equities[selected]
        test_metrics = _slice_metrics(selected_equity, test_start, test_end)
        baseline_test = _slice_metrics(baseline_equity, test_start, test_end)
        selected_spec = grid.loc[grid["variant"] == selected].iloc[0]

        rows.append(
            {
                "train_period": train_label,
                "test_period": test_label,
                "selected_variant": selected,
                "selected_rsi_max": selected_spec["rsi_max"],
                "selected_momentum_min": selected_spec["momentum_min"],
                "selected_volume_rel_min": selected_spec["volume_rel_min"],
                "train_sharpe": float(train_table.iloc[0]["train_sharpe"]),
                "train_annualized_return": float(train_table.iloc[0]["train_annualized_return"]),
                "train_max_drawdown": float(train_table.iloc[0]["train_max_drawdown"]),
                "test_annualized_return": test_metrics["annualized_return"],
                "test_max_drawdown": test_metrics["max_drawdown"],
                "test_sharpe_ratio": test_metrics["sharpe_ratio"],
                "baseline_test_annualized_return": baseline_test["annualized_return"],
                "baseline_test_max_drawdown": baseline_test["max_drawdown"],
                "baseline_test_sharpe_ratio": baseline_test["sharpe_ratio"],
                "delta_test_sharpe": test_metrics["sharpe_ratio"] - baseline_test["sharpe_ratio"],
                "delta_test_drawdown": test_metrics["max_drawdown"] - baseline_test["max_drawdown"],
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


def _write_markdown(grid: pd.DataFrame, periods: pd.DataFrame, walk: pd.DataFrame, out_path: Path) -> None:
    baseline = grid.loc[grid["variant"] == "baseline"].iloc[0]
    combined = grid[grid["kind"] == "combined"].copy()
    top_full = combined.sort_values(["full_sharpe_ratio", "full_annualized_return"], ascending=False).head(12)
    top_robust = combined.sort_values(
        ["robustness_score", "full_sharpe_ratio", "recent_sharpe_ratio"],
        ascending=False,
    ).head(12)
    neighborhood = combined[
        combined["rsi_max"].isin([62, 65, 68])
        & combined["momentum_min"].isin([-0.06, -0.05, -0.04])
        & combined["volume_rel_min"].isin([0.10, 0.20, 0.30])
    ].sort_values(["rsi_max", "momentum_min", "volume_rel_min"])
    focus = combined[
        (combined["rsi_max"] == 65)
        & (combined["momentum_min"] == -0.05)
        & (combined["volume_rel_min"] == 0.20)
    ].iloc[0]
    strong_zone = combined[
        (combined["full_sharpe_ratio"] >= 1.15)
        & (combined["full_max_drawdown"] >= -0.45)
        & (combined["recent_sharpe_ratio"] > baseline["recent_sharpe_ratio"])
    ]

    lines = [
        "# Combined Parameter Stress Test",
        "",
        "Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.",
        "",
        "Griglia testata:",
        "",
        "- RSI massimo: 60, 62, 65, 68, 70;",
        "- momentum 7g minimo: -6%, -5%, -4%;",
        "- volume relativo minimo: +10%, +20%, +30%, +40%;",
        "- trailing stop: 8% fisso su massimo Close post-ingresso.",
        "",
        "Performance misurata in EUR con `Close_EUR`.",
        "",
        "## Focus Candidato",
        "",
        "| Variante | Ann. | Max DD | Sharpe | Recent Sharpe | PF | Operazioni |",
        "|---|---:|---:|---:|---:|---:|---:|",
        "| "
        f"{focus['variant']} | "
        f"{_pct(focus['full_annualized_return'])} | "
        f"{_pct(focus['full_max_drawdown'])} | "
        f"{_ratio(focus['full_sharpe_ratio'])} | "
        f"{_ratio(focus['recent_sharpe_ratio'])} | "
        f"{_ratio(focus['full_profit_factor'])} | "
        f"{int(focus['full_num_operations'])} |",
        "",
        "## Top Per Sharpe Completo",
        "",
        "| Variante | Ann. | Max DD | Sharpe | Recent Sharpe | PF | Uscite |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in top_full.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['full_annualized_return'])} | "
            f"{_pct(row['full_max_drawdown'])} | "
            f"{_ratio(row['full_sharpe_ratio'])} | "
            f"{_ratio(row['recent_sharpe_ratio'])} | "
            f"{_ratio(row['full_profit_factor'])} | "
            f"{int(row['confirmed_exits'])} |"
        )

    lines.extend(
        [
            "",
            "## Top Per Robustezza",
            "",
            "| Variante | Ann. | Max DD | Sharpe | Median Period Sharpe | Min Period Sharpe | Recent Sharpe |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in top_robust.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['full_annualized_return'])} | "
            f"{_pct(row['full_max_drawdown'])} | "
            f"{_ratio(row['full_sharpe_ratio'])} | "
            f"{_ratio(row['median_period_sharpe'])} | "
            f"{_ratio(row['min_period_sharpe'])} | "
            f"{_ratio(row['recent_sharpe_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Zona Intorno Al Candidato",
            "",
            "| RSI | Mom | Vol | Ann. | Max DD | Sharpe | Recent Sharpe |",
            "|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in neighborhood.iterrows():
        lines.append(
            "| "
            f"{int(row['rsi_max'])} | "
            f"{_pct(row['momentum_min'])} | "
            f"{_pct(row['volume_rel_min'])} | "
            f"{_pct(row['full_annualized_return'])} | "
            f"{_pct(row['full_max_drawdown'])} | "
            f"{_ratio(row['full_sharpe_ratio'])} | "
            f"{_ratio(row['recent_sharpe_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Walk-Forward",
            "",
            "Per ogni split viene scelto il miglior parametro sul solo periodo train e",
            "poi valutato sul periodo test successivo.",
            "",
            "| Train | Test | Selezionato | Test Ann. | Test DD | Test Sharpe | Baseline Sharpe | Delta Sharpe |",
            "|---|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in walk.iterrows():
        lines.append(
            "| "
            f"{row['train_period']} | {row['test_period']} | {row['selected_variant']} | "
            f"{_pct(row['test_annualized_return'])} | "
            f"{_pct(row['test_max_drawdown'])} | "
            f"{_ratio(row['test_sharpe_ratio'])} | "
            f"{_ratio(row['baseline_test_sharpe_ratio'])} | "
            f"{_ratio(row['delta_test_sharpe'])} |"
        )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Baseline: ann. {_pct(baseline['full_annualized_return'])}, max DD "
            f"{_pct(baseline['full_max_drawdown'])}, Sharpe {_ratio(baseline['full_sharpe_ratio'])}.",
            f"- Numero combinazioni nella zona forte: {len(strong_zone)}.",
            "- Una zona forte richiede Sharpe completo >= 1,15, max DD non peggiore di -45%, e recent Sharpe sopra Baseline.",
            "- Se molte combinazioni vicine superano questi criteri, il candidato e' meno dipendente da un singolo set di parametri.",
            "- Il candidato resta sperimentale finche' non superiamo anche l'audit sul caso inefficiente 2023-04-20.",
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
    grid, periods, equities = _run_grid(df)
    walk = _walk_forward(grid, equities)

    OUT_GRID_CSV.parent.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUT_GRID_CSV, index=False)
    periods.to_csv(OUT_PERIODS_CSV, index=False)
    walk.to_csv(OUT_WALK_CSV, index=False)
    _write_markdown(grid, periods, walk, OUT_MD)

    print(f"Saved {OUT_GRID_CSV}")
    print(f"Saved {OUT_PERIODS_CSV}")
    print(f"Saved {OUT_WALK_CSV}")
    print(f"Saved {OUT_MD}")
    print("")
    print(
        grid[grid["kind"] == "combined"]
        .sort_values(["full_sharpe_ratio", "full_annualized_return"], ascending=False)
        .head(12)[
            [
                "variant",
                "full_annualized_return",
                "full_max_drawdown",
                "full_sharpe_ratio",
                "recent_sharpe_ratio",
                "median_period_sharpe",
                "confirmed_exits",
            ]
        ]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
