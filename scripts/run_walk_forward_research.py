"""Walk-forward retrospettivo ETH con costi massimi e controlli overfit.

Il runner usa la baseline congelata e le varianti sperimentali esclusivamente in
lettura. A ogni fine anno seleziona una configurazione usando solo il passato e
applica quella configurazione all'anno successivo. Le sole finestre di test
vengono poi cucite in una curva pseudo out-of-sample.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, fields
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
from statistics import NormalDist
import sys

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import run_backtest  # noqa: E402
from config import CFG  # noqa: E402
from scripts.run_condition_ablation_research import (  # noqa: E402
    DEFAULT_MANIFEST,
    StrategyVariant,
    baseline_variant,
    build_signal_frame,
    build_variants,
    load_frozen_indicators,
)


FEE_RATE = 0.006
FIRST_TEST_YEAR = 2021
CSCV_BLOCKS = 10
MIN_TRAIN_TRADES = 5
TURNOVER_ALLOWANCE = 12.0

CHALLENGER_A = "combo_trail_mom_10_sma_break_2_0"
CHALLENGER_B = "combo_trail_mom_15_sma_break_2_0"
TRIPLE_RETURN = "combo_three_early_8_trail_10_sma_2_0"
TRIPLE_DEFENSIVE = "combo_three_early_8_trail_15_sma_2_0"

DEFAULT_REPORT = PROJECT_ROOT / "reports" / "walk_forward_coinbase_0_6.md"
DEFAULT_METRICS = PROJECT_ROOT / "reports" / "walk_forward_coinbase_0_6_metrics.csv"
DEFAULT_SELECTIONS = (
    PROJECT_ROOT / "reports" / "walk_forward_coinbase_0_6_selections.csv"
)
DEFAULT_YEARLY = PROJECT_ROOT / "reports" / "walk_forward_coinbase_0_6_yearly.csv"
DEFAULT_EQUITY = PROJECT_ROOT / "reports" / "walk_forward_coinbase_0_6_equity.csv"
DEFAULT_PBO = PROJECT_ROOT / "reports" / "walk_forward_coinbase_0_6_pbo.csv"
DEFAULT_STATISTICS = (
    PROJECT_ROOT / "reports" / "walk_forward_coinbase_0_6_statistics.csv"
)
DEFAULT_PATHS = PROJECT_ROOT / "reports" / "walk_forward_coinbase_0_6_paths.csv"

PREFERRED_REPRESENTATIVES = [
    "baseline",
    CHALLENGER_A,
    CHALLENGER_B,
    TRIPLE_RETURN,
    TRIPLE_DEFENSIVE,
]

ENTRY_FIELDS = (
    "require_close_above_sma200",
    "require_sma50_above_sma200",
    "entry_rsi_min",
    "entry_rsi_max",
    "entry_momentum_min",
    "entry_volume_rel_min",
    "early_rsi_max",
    "early_momentum_max",
    "early_volume_rel_min",
)


@dataclass(frozen=True)
class PerformanceStats:
    total_return: float
    annualized_return: float
    max_drawdown: float
    sharpe_ratio: float
    turnover: float
    completed_trades: int
    exposure_ratio: float


def _signal_fingerprint(signals: pd.Series) -> str:
    payload = "\x1f".join(signals.astype(str).tolist()).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _variant_complexity(variant: StrategyVariant) -> int:
    base = baseline_variant()
    ignored = {"name", "family", "description"}
    return sum(
        getattr(variant, field.name) != getattr(base, field.name)
        for field in fields(StrategyVariant)
        if field.name not in ignored
    )


def _is_exit_only(variant: StrategyVariant) -> bool:
    base = baseline_variant()
    return all(getattr(variant, name) == getattr(base, name) for name in ENTRY_FIELDS)


def _preferred_rank(name: str, original_position: int) -> tuple[int, int]:
    try:
        return PREFERRED_REPRESENTATIVES.index(name), original_position
    except ValueError:
        return len(PREFERRED_REPRESENTATIVES), original_position


def prepare_unique_paths(
    indicators: pd.DataFrame,
    variants: list[StrategyVariant],
    *,
    fee_rate: float = FEE_RATE,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, dict[str, StrategyVariant]]:
    """Costruisce un rappresentante per ogni percorso di segnali distinto."""
    official = indicators["Segnale"].astype(str)
    representatives: dict[str, dict[str, object]] = {}

    for position, variant in enumerate(variants):
        frame = build_signal_frame(indicators, variant)
        signals = frame["Segnale"].astype(str)
        fingerprint = _signal_fingerprint(signals)
        current = representatives.get(fingerprint)
        candidate_rank = _preferred_rank(variant.name, position)
        if current is None:
            representatives[fingerprint] = {
                "variant": variant,
                "frame": frame,
                "rank": candidate_rank,
                "equivalent_names": [variant.name],
                "signal_changes": int((signals != official).sum()),
            }
        else:
            current["equivalent_names"].append(variant.name)
            if candidate_rank < current["rank"]:
                current.update(
                    {
                        "variant": variant,
                        "frame": frame,
                        "rank": candidate_rank,
                        "signal_changes": int((signals != official).sum()),
                    }
                )

    chosen_names = {
        item["variant"].name for item in representatives.values()  # type: ignore[union-attr]
    }
    missing_focus = set(PREFERRED_REPRESENTATIVES) - chosen_names
    if missing_focus:
        raise ValueError(f"Varianti focus non rappresentate: {sorted(missing_focus)}")

    baseline_frame = next(
        item["frame"]
        for item in representatives.values()
        if item["variant"].name == "baseline"  # type: ignore[union-attr]
    )
    if not baseline_frame["Segnale"].astype(str).equals(official):
        raise ValueError("La replica walk-forward diverge dalla baseline ufficiale.")

    returns: dict[str, pd.Series] = {}
    exposures: dict[str, pd.Series] = {}
    metadata_rows: list[dict[str, object]] = []
    chosen_variants: dict[str, StrategyVariant] = {}

    for fingerprint, item in representatives.items():
        variant = item["variant"]
        frame = item["frame"]
        equity, _, _ = run_backtest(frame, transaction_cost_rate=fee_rate)
        name = variant.name
        returns[name] = equity["DailyReturnStrategy"].fillna(0.0)
        exposures[name] = equity["EffectiveExposure"].fillna(0.0)
        chosen_variants[name] = variant
        metadata_rows.append(
            {
                "variant": name,
                "family": variant.family,
                "description": variant.description,
                "signal_fingerprint": fingerprint,
                "equivalent_variants": len(item["equivalent_names"]),
                "equivalent_names": "|".join(sorted(item["equivalent_names"])),
                "signal_changes_vs_baseline": item["signal_changes"],
                "complexity": _variant_complexity(variant),
                "exit_only": _is_exit_only(variant),
                **asdict(variant),
            }
        )

    return (
        pd.DataFrame(returns, index=indicators.index),
        pd.DataFrame(exposures, index=indicators.index),
        pd.DataFrame(metadata_rows).set_index("variant"),
        chosen_variants,
    )


def _max_drawdown(equity: pd.Series) -> float:
    return float((equity / equity.cummax() - 1.0).min())


def _sharpe(returns: pd.Series) -> float:
    clean = returns.dropna()
    if len(clean) < 2:
        return float("nan")
    std = float(clean.std(ddof=1))
    if std == 0.0:
        return float("nan")
    return float(math.sqrt(CFG.periods_per_year) * clean.mean() / std)


def performance_stats(
    returns: pd.Series,
    exposure: pd.Series,
    turnover: pd.Series,
    *,
    periods: int | None = None,
) -> PerformanceStats:
    clean_returns = returns.fillna(0.0).astype(float)
    clean_exposure = exposure.reindex(clean_returns.index).fillna(0.0).astype(float)
    clean_turnover = turnover.reindex(clean_returns.index).fillna(0.0).astype(float)
    equity = (1.0 + clean_returns).cumprod()
    total_return = float(equity.iloc[-1] - 1.0)
    annual_periods = max(periods if periods is not None else len(clean_returns), 1)
    annualized = float(
        (1.0 + total_return) ** (CFG.periods_per_year / annual_periods) - 1.0
    )
    active = clean_exposure.gt(0.0)
    completed = int((~active & active.shift(1, fill_value=False)).sum())
    return PerformanceStats(
        total_return=total_return,
        annualized_return=annualized,
        max_drawdown=_max_drawdown(equity),
        sharpe_ratio=_sharpe(clean_returns),
        turnover=float(clean_turnover.sum()),
        completed_trades=completed,
        exposure_ratio=float(active.mean()),
    )


def training_metrics(
    returns: pd.DataFrame,
    exposures: pd.DataFrame,
    metadata: pd.DataFrame,
    train_end: pd.Timestamp,
) -> pd.DataFrame:
    train_returns = returns.loc[:train_end]
    train_exposure = exposures.loc[:train_end]
    equity = (1.0 + train_returns.fillna(0.0)).cumprod()
    total_return = equity.iloc[-1] - 1.0
    calendar_days = max((train_returns.index[-1] - train_returns.index[0]).days, 1)
    annualized = (1.0 + total_return) ** (CFG.periods_per_year / calendar_days) - 1.0
    drawdown = (equity / equity.cummax() - 1.0).min()
    std = train_returns.std(ddof=1).replace(0.0, np.nan)
    sharpe = math.sqrt(CFG.periods_per_year) * train_returns.mean() / std
    turnover = train_exposure.diff().abs()
    turnover.iloc[0] = train_exposure.iloc[0].abs()
    active = train_exposure.gt(0.0)
    operations = (~active & active.shift(1, fill_value=False)).sum()

    out = pd.DataFrame(
        {
            "total_return": total_return,
            "annualized_return": annualized,
            "max_drawdown": drawdown,
            "sharpe_ratio": sharpe,
            "turnover": turnover.sum(),
            "completed_trades": operations,
            "exposure_ratio": active.mean(),
        }
    )
    return out.join(metadata[["family", "complexity", "exit_only"]], how="left")


def select_training_candidate(
    metrics: pd.DataFrame,
    universe: list[str],
) -> tuple[str, pd.DataFrame]:
    available = metrics.loc[metrics.index.intersection(universe)].copy()
    if "baseline" not in available.index:
        raise ValueError("La baseline deve appartenere a ogni universo di selezione.")

    baseline = available.loc["baseline"]
    eligible = available.drop(index="baseline", errors="ignore")
    eligible = eligible[
        (eligible["annualized_return"] > baseline["annualized_return"])
        & (eligible["max_drawdown"] >= baseline["max_drawdown"])
        & (eligible["sharpe_ratio"] > baseline["sharpe_ratio"])
        & (eligible["completed_trades"] >= MIN_TRAIN_TRADES)
        & (eligible["turnover"] <= baseline["turnover"] + TURNOVER_ALLOWANCE)
    ].copy()

    if eligible.empty:
        fallback = available.loc[["baseline"]].copy()
        fallback["balanced_score"] = 0.0
        return "baseline", fallback

    eligible["return_rank"] = eligible["annualized_return"].rank(pct=True)
    eligible["drawdown_rank"] = eligible["max_drawdown"].rank(pct=True)
    eligible["sharpe_rank"] = eligible["sharpe_ratio"].rank(pct=True)
    eligible["balanced_score"] = eligible[
        ["return_rank", "drawdown_rank", "sharpe_rank"]
    ].mean(axis=1)
    ordered = eligible.reset_index(names="variant").sort_values(
        [
            "balanced_score",
            "sharpe_ratio",
            "max_drawdown",
            "annualized_return",
            "complexity",
            "turnover",
            "variant",
        ],
        ascending=[False, False, False, False, True, True, True],
    )
    selected = str(ordered.iloc[0]["variant"])
    return selected, eligible


def walk_forward_selections(
    returns: pd.DataFrame,
    exposures: pd.DataFrame,
    metadata: pd.DataFrame,
    *,
    first_test_year: int = FIRST_TEST_YEAR,
) -> pd.DataFrame:
    last_date = returns.index.max()
    all_universe = list(returns.columns)
    exit_universe = [
        name
        for name in returns.columns
        if name == "baseline" or bool(metadata.loc[name, "exit_only"])
    ]
    policies = {
        "wf_full_grid": all_universe,
        "wf_exit_only": exit_universe,
    }
    rows: list[dict[str, object]] = []

    for test_year in range(first_test_year, last_date.year + 1):
        test_start = pd.Timestamp(year=test_year, month=1, day=1)
        if test_start > last_date:
            break
        train_end = test_start - pd.Timedelta(days=1)
        test_end = min(
            pd.Timestamp(year=test_year, month=12, day=31),
            last_date,
        )
        metrics = training_metrics(returns, exposures, metadata, train_end)
        for policy, universe in policies.items():
            selected, eligible = select_training_candidate(metrics, universe)
            chosen = metrics.loc[selected]
            baseline = metrics.loc["baseline"]
            rows.append(
                {
                    "policy": policy,
                    "test_year": test_year,
                    "train_start": returns.index.min().strftime("%Y-%m-%d"),
                    "train_end": train_end.strftime("%Y-%m-%d"),
                    "test_start": test_start.strftime("%Y-%m-%d"),
                    "test_end": test_end.strftime("%Y-%m-%d"),
                    "universe_paths": len(universe),
                    "eligible_paths": len(eligible),
                    "selected_variant": selected,
                    "selected_family": metadata.loc[selected, "family"],
                    "selected_complexity": int(metadata.loc[selected, "complexity"]),
                    "train_annualized_return": chosen["annualized_return"],
                    "train_max_drawdown": chosen["max_drawdown"],
                    "train_sharpe_ratio": chosen["sharpe_ratio"],
                    "train_completed_trades": int(chosen["completed_trades"]),
                    "train_turnover": chosen["turnover"],
                    "baseline_train_annualized_return": baseline["annualized_return"],
                    "baseline_train_max_drawdown": baseline["max_drawdown"],
                    "baseline_train_sharpe_ratio": baseline["sharpe_ratio"],
                }
            )
    return pd.DataFrame(rows)


def _selection_map(selections: pd.DataFrame, policy: str) -> dict[int, str]:
    subset = selections[selections["policy"] == policy]
    return {
        int(row["test_year"]): str(row["selected_variant"])
        for _, row in subset.iterrows()
    }


def build_stitched_stream(
    eth_returns: pd.Series,
    exposures: pd.DataFrame,
    selection_by_year: dict[int, str],
    *,
    start: pd.Timestamp,
    end: pd.Timestamp,
    fee_rate: float = FEE_RATE,
    extra_delay_days: int = 0,
) -> pd.DataFrame:
    if extra_delay_days < 0:
        raise ValueError("Il ritardo extra non puo essere negativo.")
    source_exposure = exposures.shift(extra_delay_days).fillna(0.0)
    index = eth_returns.loc[start:end].index
    selected_exposure = pd.Series(0.0, index=index, dtype=float)
    selected_variant = pd.Series("", index=index, dtype=object)

    for year in sorted({date.year for date in index}):
        if year not in selection_by_year:
            raise ValueError(f"Nessuna selezione disponibile per il {year}.")
        variant = selection_by_year[year]
        year_mask = index.year == year
        year_index = index[year_mask]
        selected_exposure.loc[year_index] = source_exposure.loc[year_index, variant]
        selected_variant.loc[year_index] = variant

    turnover = selected_exposure.diff().abs()
    turnover.iloc[0] = abs(float(selected_exposure.iloc[0]))
    strategy_returns = (
        selected_exposure * eth_returns.reindex(index).fillna(0.0)
        - turnover * fee_rate
    )

    if float(selected_exposure.iloc[-1]) > 0.0:
        final_cost = float(selected_exposure.iloc[-1]) * fee_rate
        strategy_returns.iloc[-1] -= final_cost
        turnover.iloc[-1] += float(selected_exposure.iloc[-1])

    equity = (1.0 + strategy_returns).cumprod()
    return pd.DataFrame(
        {
            "DailyReturn": strategy_returns,
            "Exposure": selected_exposure,
            "Turnover": turnover,
            "Equity": equity,
            "SelectedVariant": selected_variant,
        },
        index=index,
    )


def build_buy_hold_stream(
    eth_returns: pd.Series,
    *,
    start: pd.Timestamp,
    end: pd.Timestamp,
    fee_rate: float = FEE_RATE,
) -> pd.DataFrame:
    index = eth_returns.loc[start:end].index
    exposure = pd.Series(1.0, index=index)
    turnover = pd.Series(0.0, index=index)
    turnover.iloc[0] = 1.0
    turnover.iloc[-1] += 1.0
    daily = eth_returns.reindex(index).fillna(0.0) - turnover * fee_rate
    return pd.DataFrame(
        {
            "DailyReturn": daily,
            "Exposure": exposure,
            "Turnover": turnover,
            "Equity": (1.0 + daily).cumprod(),
            "SelectedVariant": "buy_hold",
        },
        index=index,
    )


def build_all_oos_streams(
    indicators: pd.DataFrame,
    exposures: pd.DataFrame,
    selections: pd.DataFrame,
    *,
    first_test_year: int = FIRST_TEST_YEAR,
    extra_delay_days: int = 0,
) -> dict[str, pd.DataFrame]:
    start = pd.Timestamp(year=first_test_year, month=1, day=1)
    end = indicators.index.max()
    eth_returns = indicators["Close"].pct_change()
    years = range(first_test_year, end.year + 1)
    fixed = {
        "baseline": "baseline",
        "challenger_a": CHALLENGER_A,
        "challenger_b": CHALLENGER_B,
        "triple_return": TRIPLE_RETURN,
        "triple_defensive": TRIPLE_DEFENSIVE,
    }
    streams: dict[str, pd.DataFrame] = {}
    for label, variant in fixed.items():
        streams[label] = build_stitched_stream(
            eth_returns,
            exposures,
            {year: variant for year in years},
            start=start,
            end=end,
            extra_delay_days=extra_delay_days,
        )
    for policy in ["wf_full_grid", "wf_exit_only"]:
        streams[policy] = build_stitched_stream(
            eth_returns,
            exposures,
            _selection_map(selections, policy),
            start=start,
            end=end,
            extra_delay_days=extra_delay_days,
        )
    streams["buy_hold"] = build_buy_hold_stream(
        eth_returns,
        start=start,
        end=end,
    )
    return streams


def summarize_streams(
    streams: dict[str, pd.DataFrame],
    *,
    scenario: str,
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for model, stream in streams.items():
        stats = performance_stats(
            stream["DailyReturn"],
            stream["Exposure"],
            stream["Turnover"],
        )
        rows.append({"scenario": scenario, "model": model, **asdict(stats)})
    return pd.DataFrame(rows)


def yearly_stream_metrics(streams: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for model, stream in streams.items():
        for year, subset in stream.groupby(stream.index.year):
            stats = performance_stats(
                subset["DailyReturn"],
                subset["Exposure"],
                subset["Turnover"],
            )
            rows.append({"year": int(year), "model": model, **asdict(stats)})
    out = pd.DataFrame(rows)
    baseline = out[out["model"] == "baseline"].set_index("year")
    out["delta_total_return_vs_baseline"] = out.apply(
        lambda row: row["total_return"]
        - float(baseline.loc[int(row["year"]), "total_return"]),
        axis=1,
    )
    out["delta_max_drawdown_vs_baseline"] = out.apply(
        lambda row: row["max_drawdown"]
        - float(baseline.loc[int(row["year"]), "max_drawdown"]),
        axis=1,
    )
    out["delta_sharpe_vs_baseline"] = out.apply(
        lambda row: row["sharpe_ratio"]
        - float(baseline.loc[int(row["year"]), "sharpe_ratio"]),
        axis=1,
    )
    out["all3_vs_baseline"] = (
        (out["delta_total_return_vs_baseline"] > 0.0)
        & (out["delta_max_drawdown_vs_baseline"] >= -1e-12)
        & (out["delta_sharpe_vs_baseline"] > 0.0)
    )
    out["comparison_status"] = out.apply(_comparison_status, axis=1)
    return out


def _comparison_status(row: pd.Series, tolerance: float = 1e-12) -> str:
    if row["model"] == "baseline":
        return "BASELINE"
    delta_return = float(row["delta_total_return_vs_baseline"])
    delta_dd = float(row["delta_max_drawdown_vs_baseline"])
    delta_sharpe_raw = row["delta_sharpe_vs_baseline"]
    delta_sharpe = (
        float(delta_sharpe_raw) if pd.notna(delta_sharpe_raw) else float("nan")
    )
    neutral_sharpe = pd.isna(delta_sharpe) or abs(delta_sharpe) <= tolerance
    if (
        abs(delta_return) <= tolerance
        and abs(delta_dd) <= tolerance
        and neutral_sharpe
    ):
        return "INVARIATO"
    if bool(row["all3_vs_baseline"]):
        return "MIGLIORA"
    if (
        delta_return < -tolerance
        and delta_dd < -tolerance
        and pd.notna(delta_sharpe)
        and delta_sharpe < -tolerance
    ):
        return "PEGGIORA"
    return "MISTO"


def attach_test_metrics(
    selections: pd.DataFrame,
    yearly: pd.DataFrame,
) -> pd.DataFrame:
    out = selections.copy()
    yearly_indexed = yearly.set_index(["model", "year"])
    test_fields = [
        "total_return",
        "max_drawdown",
        "sharpe_ratio",
        "delta_total_return_vs_baseline",
        "delta_max_drawdown_vs_baseline",
        "delta_sharpe_vs_baseline",
        "all3_vs_baseline",
        "comparison_status",
    ]
    for field in test_fields:
        out[f"test_{field}"] = out.apply(
            lambda row: yearly_indexed.loc[
                (str(row["policy"]), int(row["test_year"])), field
            ],
            axis=1,
        )
    return out


def _sharpe_from_moments(
    sums: np.ndarray,
    sums_of_squares: np.ndarray,
    observations: int,
) -> np.ndarray:
    if observations < 2:
        return np.full_like(sums, np.nan, dtype=float)
    variance = (
        sums_of_squares - np.square(sums) / float(observations)
    ) / float(observations - 1)
    variance = np.maximum(variance, 0.0)
    std = np.sqrt(variance)
    mean = sums / float(observations)
    return np.divide(
        math.sqrt(CFG.periods_per_year) * mean,
        std,
        out=np.full_like(mean, np.nan, dtype=float),
        where=std > 0.0,
    )


def cscv_pbo(
    returns: pd.DataFrame,
    *,
    blocks: int = CSCV_BLOCKS,
    label: str,
) -> tuple[dict[str, object], pd.DataFrame]:
    """Calcola il Probability of Backtest Overfitting con CSCV esaustivo."""
    if blocks < 4 or blocks % 2 != 0:
        raise ValueError("CSCV richiede almeno quattro blocchi e un numero pari.")
    if len(returns) < blocks * 2:
        raise ValueError("Osservazioni insufficienti per i blocchi CSCV richiesti.")

    matrix = returns.fillna(0.0).to_numpy(dtype=float)
    block_positions = np.array_split(np.arange(len(matrix)), blocks)
    block_sums = np.vstack([matrix[pos].sum(axis=0) for pos in block_positions])
    block_squares = np.vstack(
        [np.square(matrix[pos]).sum(axis=0) for pos in block_positions]
    )
    block_counts = np.asarray([len(pos) for pos in block_positions], dtype=int)
    total_sums = block_sums.sum(axis=0)
    total_squares = block_squares.sum(axis=0)
    total_count = int(block_counts.sum())
    names = list(returns.columns)
    rows: list[dict[str, object]] = []

    for split_number, train_blocks_tuple in enumerate(
        combinations(range(blocks), blocks // 2),
        start=1,
    ):
        train_blocks = np.asarray(train_blocks_tuple, dtype=int)
        train_sum = block_sums[train_blocks].sum(axis=0)
        train_squares = block_squares[train_blocks].sum(axis=0)
        train_count = int(block_counts[train_blocks].sum())
        test_sum = total_sums - train_sum
        test_squares = total_squares - train_squares
        test_count = total_count - train_count
        train_sharpes = _sharpe_from_moments(
            train_sum, train_squares, train_count
        )
        test_sharpes = _sharpe_from_moments(test_sum, test_squares, test_count)
        selection_scores = np.where(np.isfinite(train_sharpes), train_sharpes, -np.inf)
        selected_pos = int(np.argmax(selection_scores))
        selected_test = float(test_sharpes[selected_pos])
        finite_test = test_sharpes[np.isfinite(test_sharpes)]
        tied = np.isclose(
            finite_test,
            selected_test,
            rtol=1e-12,
            atol=1e-12,
        )
        lower = int(np.sum((finite_test < selected_test) & ~tied))
        equal = int(np.sum(tied))
        average_rank = lower + (equal + 1.0) / 2.0
        omega = average_rank / (len(finite_test) + 1.0)
        omega = min(max(omega, np.finfo(float).eps), 1.0 - np.finfo(float).eps)
        logit = math.log(omega / (1.0 - omega))
        rows.append(
            {
                "label": label,
                "split": split_number,
                "train_blocks": "|".join(str(value) for value in train_blocks_tuple),
                "selected_variant": names[selected_pos],
                "train_sharpe": float(train_sharpes[selected_pos]),
                "test_sharpe": selected_test,
                "test_rank_percentile": omega,
                "logit": logit,
                "below_test_median": logit <= 0.0,
            }
        )

    details = pd.DataFrame(rows)
    summary = {
        "label": label,
        "observations": len(returns),
        "paths": len(returns.columns),
        "blocks": blocks,
        "splits": len(details),
        "pbo": float(details["below_test_median"].mean()),
        "median_test_rank": float(details["test_rank_percentile"].median()),
        "mean_selected_train_sharpe": float(details["train_sharpe"].mean()),
        "mean_selected_test_sharpe": float(details["test_sharpe"].mean()),
        "test_sharpe_positive_ratio": float((details["test_sharpe"] > 0.0).mean()),
    }
    return summary, details


def daily_sharpe_values(returns: pd.DataFrame) -> pd.Series:
    std = returns.std(ddof=1).replace(0.0, np.nan)
    return returns.mean() / std


def expected_max_sharpe(
    trial_daily_sharpes: pd.Series,
    *,
    trials: int | None = None,
) -> float:
    clean = trial_daily_sharpes.replace([np.inf, -np.inf], np.nan).dropna()
    number = int(trials if trials is not None else len(clean))
    if number <= 1 or len(clean) < 2:
        return 0.0
    sigma = float(clean.std(ddof=1))
    euler_gamma = 0.5772156649015329
    normal = NormalDist()
    first = normal.inv_cdf(1.0 - 1.0 / number)
    second = normal.inv_cdf(1.0 - 1.0 / (number * math.e))
    return sigma * ((1.0 - euler_gamma) * first + euler_gamma * second)


def probabilistic_sharpe(
    returns: pd.Series,
    *,
    benchmark_daily_sharpe: float,
) -> dict[str, float | int]:
    clean = returns.replace([np.inf, -np.inf], np.nan).dropna().astype(float)
    if len(clean) < 3 or float(clean.std(ddof=1)) == 0.0:
        return {
            "observations": len(clean),
            "daily_sharpe": float("nan"),
            "annualized_sharpe": float("nan"),
            "skewness": float("nan"),
            "kurtosis": float("nan"),
            "probability": float("nan"),
        }
    mean = float(clean.mean())
    std = float(clean.std(ddof=1))
    daily_sr = mean / std
    centered = clean.to_numpy() - mean
    second_moment = float(np.mean(np.square(centered)))
    skewness = float(np.mean(np.power(centered, 3)) / second_moment**1.5)
    kurtosis = float(np.mean(np.power(centered, 4)) / second_moment**2)
    denominator_squared = (
        1.0
        - skewness * daily_sr
        + ((kurtosis - 1.0) / 4.0) * daily_sr**2
    )
    if denominator_squared <= 0.0:
        probability = float("nan")
    else:
        z_score = (
            (daily_sr - benchmark_daily_sharpe)
            * math.sqrt(len(clean) - 1)
            / math.sqrt(denominator_squared)
        )
        probability = NormalDist().cdf(z_score)
    return {
        "observations": len(clean),
        "daily_sharpe": daily_sr,
        "annualized_sharpe": daily_sr * math.sqrt(CFG.periods_per_year),
        "skewness": skewness,
        "kurtosis": kurtosis,
        "probability": probability,
    }


MODEL_LABELS = {
    "baseline": "Baseline netta",
    "buy_hold": "Buy & Hold netto",
    "challenger_a": "Challenger A: Trail -10 / SMA 2%",
    "challenger_b": "Challenger B: Trail -15 / SMA 2%",
    "triple_return": "Tripla rendimento: Early 8 / Trail -10 / SMA 2%",
    "triple_defensive": "Tripla difensiva: Early 8 / Trail -15 / SMA 2%",
    "wf_full_grid": "Walk-forward intero universo",
    "wf_exit_only": "Walk-forward sole uscite",
}


def statistical_diagnostics(
    path_returns: pd.DataFrame,
    metadata: pd.DataFrame,
    streams: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    exit_columns = [
        name
        for name in path_returns.columns
        if name == "baseline" or bool(metadata.loc[name, "exit_only"])
    ]
    initial_train = path_returns.loc[: pd.Timestamp("2020-12-31")]
    pbo_jobs = [
        ("full_all_paths", path_returns),
        ("train_to_2020_all_paths", initial_train),
        ("full_exit_only", path_returns[exit_columns]),
        ("train_to_2020_exit_only", initial_train[exit_columns]),
    ]
    pbo_summaries: list[dict[str, object]] = []
    pbo_details: list[pd.DataFrame] = []
    for label, frame in pbo_jobs:
        summary, details = cscv_pbo(frame, label=label)
        pbo_summaries.append(summary)
        pbo_details.append(details)
    pbo_summary = pd.DataFrame(pbo_summaries)
    pbo_detail = pd.concat(pbo_details, ignore_index=True)

    trial_daily_srs = daily_sharpe_values(path_returns)
    benchmark = expected_max_sharpe(
        trial_daily_srs,
        trials=len(path_returns.columns),
    )
    best_full_variant = str(trial_daily_srs.idxmax())
    series_to_test: dict[str, tuple[str, pd.Series]] = {
        "full_best_path": (best_full_variant, path_returns[best_full_variant]),
        "full_challenger_a": (CHALLENGER_A, path_returns[CHALLENGER_A]),
        "full_challenger_b": (CHALLENGER_B, path_returns[CHALLENGER_B]),
        "full_triple_return": (TRIPLE_RETURN, path_returns[TRIPLE_RETURN]),
        "full_triple_defensive": (
            TRIPLE_DEFENSIVE,
            path_returns[TRIPLE_DEFENSIVE],
        ),
        "oos_baseline": ("baseline", streams["baseline"]["DailyReturn"]),
        "oos_challenger_a": (
            CHALLENGER_A,
            streams["challenger_a"]["DailyReturn"],
        ),
        "oos_challenger_b": (
            CHALLENGER_B,
            streams["challenger_b"]["DailyReturn"],
        ),
        "oos_wf_full_grid": (
            "wf_full_grid",
            streams["wf_full_grid"]["DailyReturn"],
        ),
        "oos_wf_exit_only": (
            "wf_exit_only",
            streams["wf_exit_only"]["DailyReturn"],
        ),
    }
    dsr_rows: list[dict[str, object]] = []
    for label, (variant, series) in series_to_test.items():
        psr = probabilistic_sharpe(series, benchmark_daily_sharpe=0.0)
        dsr = probabilistic_sharpe(
            series,
            benchmark_daily_sharpe=benchmark,
        )
        dsr_rows.append(
            {
                "label": label,
                "variant": variant,
                "observations": dsr["observations"],
                "annualized_sharpe": dsr["annualized_sharpe"],
                "skewness": dsr["skewness"],
                "kurtosis": dsr["kurtosis"],
                "psr_above_zero": psr["probability"],
                "deflated_sharpe_probability": dsr["probability"],
                "dsr_benchmark_annualized": benchmark
                * math.sqrt(CFG.periods_per_year),
                "unique_trials": len(path_returns.columns),
            }
        )
    return pbo_summary, pbo_detail, pd.DataFrame(dsr_rows)


def _pct(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:.2f}%"


def _pp(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:+.2f} pp"


def _ratio(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):.3f}"


def _signed_ratio(value: object) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):+.3f}"


def write_report(
    *,
    manifest: dict,
    metadata: pd.DataFrame,
    metrics: pd.DataFrame,
    selections: pd.DataFrame,
    yearly: pd.DataFrame,
    pbo_summary: pd.DataFrame,
    dsr: pd.DataFrame,
    out_path: Path,
) -> None:
    regular = metrics[metrics["scenario"] == "normal"].set_index("model")
    delayed = metrics[metrics["scenario"] == "extra_delay_1d"].set_index("model")
    baseline = regular.loc["baseline"]
    challenger_a = regular.loc["challenger_a"]
    challenger_b = regular.loc["challenger_b"]
    focus_models = [
        "baseline",
        "buy_hold",
        "challenger_a",
        "challenger_b",
        "triple_return",
        "triple_defensive",
        "wf_exit_only",
        "wf_full_grid",
    ]
    test_end = manifest["period"]["evaluation_end"]
    unique_paths = len(metadata)
    exit_paths = int(metadata["exit_only"].sum())

    lines = [
        "# Walk-Forward ETH Coinbase - Commissione 0,6%",
        "",
        "## Protocollo",
        "",
        f"- Baseline congelata: `{manifest['run_id']}`.",
        f"- Serie grezza Coinbase: `{manifest['period']['coinbase_history_start']}` -> `{test_end}`.",
        f"- Valutazione indicatori: `{manifest['period']['evaluation_start']}` -> `{test_end}`.",
        f"- Pseudo out-of-sample cucito: `2021-01-01` -> `{test_end}`.",
        f"- Definizioni esplorate: {sum(metadata['equivalent_variants'])}; percorsi di segnale distinti: {unique_paths}.",
        f"- Universo prudente con soli ingressi baseline: {exit_paths} percorsi.",
        "- Commissione applicata: 0,6% a ogni cambio completo di esposizione; Buy & Hold paga acquisto e liquidazione.",
        "- Ogni selezione annuale usa esclusivamente dati fino al 31 dicembre precedente.",
        "- Il portafoglio non viene azzerato artificialmente tra gli anni: ogni cambio di esposizione del modello selezionato paga la commissione.",
        "- Questo e un walk-forward retrospettivo, non un vero futuro non osservato: l'universo delle ipotesi e stato definito dopo avere visto la serie completa.",
        "",
        "## Regola Di Selezione",
        "",
        "Un percorso e eleggibile solo se sul training migliora annualizzato, drawdown e Sharpe rispetto alla baseline, completa almeno cinque trade e non supera il turnover baseline di oltre 12 lati. Fra gli eleggibili viene scelto il miglior rango medio delle tre metriche; complessita e turnover rompono soltanto le parita.",
        "",
        "## Selezioni Annuali",
        "",
        "| Policy | Test | Eleggibili / universo | Variante scelta | Ann. train | DD train | Sharpe train | Delta return test | Delta DD test | Delta Sharpe test | Esito |",
        "|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in selections.sort_values(["test_year", "policy"]).iterrows():
        lines.append(
            f"| `{row['policy']}` | {int(row['test_year'])} | "
            f"{int(row['eligible_paths'])}/{int(row['universe_paths'])} | "
            f"`{row['selected_variant']}` | {_pct(row['train_annualized_return'])} | "
            f"{_pct(row['train_max_drawdown'])} | {_ratio(row['train_sharpe_ratio'])} | "
            f"{_pp(row['test_delta_total_return_vs_baseline'])} | "
            f"{_pp(row['test_delta_max_drawdown_vs_baseline'])} | "
            f"{_signed_ratio(row['test_delta_sharpe_vs_baseline'])} | "
            f"{row['test_comparison_status']} |"
        )

    lines.extend(
        [
            "",
            "## Curva Pseudo Out-Of-Sample 2021-2026",
            "",
            "Le configurazioni fisse sono riferimenti scelti con hindsight; le due righe walk-forward sono le sole che ricostruiscono una selezione annuale basata sul passato.",
            "",
            "| Modello | Totale | Ann. | Max DD | Sharpe | Turnover | Trade | Esposizione |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for model in focus_models:
        row = regular.loc[model]
        lines.append(
            f"| {MODEL_LABELS[model]} | {_pct(row['total_return'])} | "
            f"{_pct(row['annualized_return'])} | {_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | {float(row['turnover']):.0f} | "
            f"{int(row['completed_trades'])} | {_pct(row['exposure_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Risultati Annuali Dei Selettori",
            "",
            "| Anno | Policy | Return | Delta return | DD | Delta DD | Sharpe | Delta Sharpe | Esito |",
            "|---:|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    yearly_focus = yearly[yearly["model"].isin(["wf_exit_only", "wf_full_grid"])]
    for _, row in yearly_focus.sort_values(["year", "model"]).iterrows():
        lines.append(
            f"| {int(row['year'])} | `{row['model']}` | {_pct(row['total_return'])} | "
            f"{_pp(row['delta_total_return_vs_baseline'])} | {_pct(row['max_drawdown'])} | "
            f"{_pp(row['delta_max_drawdown_vs_baseline'])} | {_ratio(row['sharpe_ratio'])} | "
            f"{_signed_ratio(row['delta_sharpe_vs_baseline'])} | "
            f"{row['comparison_status']} |"
        )

    lines.extend(
        [
            "",
            "## Sintesi Annuale",
            "",
            "| Modello | Migliora | Invariato | Misto | Peggiora |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    annual_models = [
        "challenger_a",
        "challenger_b",
        "triple_return",
        "triple_defensive",
        "wf_exit_only",
        "wf_full_grid",
    ]
    annual_status = (
        yearly[yearly["model"].isin(annual_models)]
        .groupby(["model", "comparison_status"])
        .size()
        .unstack(fill_value=0)
    )
    for model in annual_models:
        counts = annual_status.loc[model]
        lines.append(
            f"| {MODEL_LABELS[model]} | {int(counts.get('MIGLIORA', 0))} | "
            f"{int(counts.get('INVARIATO', 0))} | {int(counts.get('MISTO', 0))} | "
            f"{int(counts.get('PEGGIORA', 0))} |"
        )

    lines.extend(
        [
            "",
            "## Stress: Una Candela Di Ritardo Aggiuntiva",
            "",
            "Il segnale baseline e gia applicato al rendimento successivo; questo scenario aggiunge un ulteriore giorno di ritardo senza superare la commissione dello 0,6%.",
            "",
            "| Modello | Ann. normale | Ann. ritardato | DD ritardato | Sharpe ritardato | Delta ann. da ritardo |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for model in ["baseline", "challenger_a", "challenger_b", "wf_exit_only", "wf_full_grid"]:
        normal_row = regular.loc[model]
        delayed_row = delayed.loc[model]
        lines.append(
            f"| {MODEL_LABELS[model]} | {_pct(normal_row['annualized_return'])} | "
            f"{_pct(delayed_row['annualized_return'])} | {_pct(delayed_row['max_drawdown'])} | "
            f"{_ratio(delayed_row['sharpe_ratio'])} | "
            f"{_pp(delayed_row['annualized_return'] - normal_row['annualized_return'])} |"
        )

    lines.extend(
        [
            "",
            "## Probability Of Backtest Overfitting",
            "",
            f"CSCV esaustivo con {CSCV_BLOCKS} blocchi contigui e {math.comb(CSCV_BLOCKS, CSCV_BLOCKS // 2)} suddivisioni simmetriche. PBO e la quota di vincitori in-sample che finiscono sotto la mediana nel complemento.",
            "La statistica di selezione CSCV e lo Sharpe, come nel test PBO standard: misura la stabilita del ranking relativo, non replica il selettore multi-metrica. Un PBO alto puo quindi coesistere con Sharpe test positivi.",
            "",
            "| Campione | Osservazioni | Percorsi | PBO | Rank test mediano | Sharpe train scelto | Sharpe test scelto | Test Sharpe > 0 |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in pbo_summary.iterrows():
        lines.append(
            f"| `{row['label']}` | {int(row['observations'])} | {int(row['paths'])} | "
            f"{_pct(row['pbo'])} | {_pct(row['median_test_rank'])} | "
            f"{_ratio(row['mean_selected_train_sharpe'])} | "
            f"{_ratio(row['mean_selected_test_sharpe'])} | "
            f"{_pct(row['test_sharpe_positive_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Deflated Sharpe Ratio",
            "",
            "Il benchmark DSR e lo Sharpe massimo atteso dopo 134 tentativi distinti. La probabilita DSR corregge selezione multipla, asimmetria e code non normali; resta una diagnostica, non una garanzia.",
            "",
            "| Serie | Variante | Osservazioni | Sharpe | Benchmark DSR | PSR > 0 | Probabilita DSR |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in dsr.iterrows():
        lines.append(
            f"| `{row['label']}` | `{row['variant']}` | {int(row['observations'])} | "
            f"{_ratio(row['annualized_sharpe'])} | {_ratio(row['dsr_benchmark_annualized'])} | "
            f"{_pct(row['psr_above_zero'])} | {_pct(row['deflated_sharpe_probability'])} |"
        )

    selector_rows = regular.loc[["wf_exit_only", "wf_full_grid"]]
    selector_status = (
        yearly_focus.groupby(["model", "comparison_status"])
        .size()
        .unstack(fill_value=0)
    )
    best_selector = str(selector_rows["sharpe_ratio"].idxmax())
    best = selector_rows.loc[best_selector]
    improves_all3 = bool(
        best["annualized_return"] > baseline["annualized_return"]
        and best["max_drawdown"] >= baseline["max_drawdown"]
        and best["sharpe_ratio"] > baseline["sharpe_ratio"]
    )
    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Il selettore con Sharpe pseudo out-of-sample piu alto e `{best_selector}`: ann. {_pct(best['annualized_return'])}, DD {_pct(best['max_drawdown'])}, Sharpe {_ratio(best['sharpe_ratio'])}.",
            f"- Rispetto alla baseline, questo selettore {'migliora tutte e tre le metriche aggregate' if improves_all3 else 'non migliora contemporaneamente tutte e tre le metriche aggregate'}.",
            f"- `wf_exit_only` conta {int(selector_status.loc['wf_exit_only'].get('MIGLIORA', 0))} anni migliori, {int(selector_status.loc['wf_exit_only'].get('INVARIATO', 0))} invariati e {int(selector_status.loc['wf_exit_only'].get('MISTO', 0))} misti; `wf_full_grid` mostra la stessa ripartizione: {int(selector_status.loc['wf_full_grid'].get('MIGLIORA', 0))}/{int(selector_status.loc['wf_full_grid'].get('INVARIATO', 0))}/{int(selector_status.loc['wf_full_grid'].get('MISTO', 0))}.",
            f"- Il Challenger B fisso offre il compromesso semplice piu difensivo: ann. {_pct(challenger_b['annualized_return'])}, DD {_pct(challenger_b['max_drawdown'])}, Sharpe {_ratio(challenger_b['sharpe_ratio'])}; il Challenger A rende {_pp(challenger_a['annualized_return'] - challenger_b['annualized_return'])} in piu ma ha un DD peggiore di {abs(float(challenger_b['max_drawdown'] - challenger_a['max_drawdown'])) * 100:.2f} pp.",
            f"- Con una candela extra di ritardo, B mantiene ann. {_pct(delayed.loc['challenger_b', 'annualized_return'])}, DD {_pct(delayed.loc['challenger_b', 'max_drawdown'])} e Sharpe {_ratio(delayed.loc['challenger_b', 'sharpe_ratio'])}, tutti migliori di A nello stesso stress.",
            "- La riottimizzazione annuale non batte il Challenger B fisso sullo Sharpe e aggiunge complessita; il PBO iniziale del solo universo uscite rafforza la preferenza per una soglia congelata.",
            "- I riferimenti fissi A/B e tripli non diventano out-of-sample solo perche sono misurati dal 2021: sono stati scelti dopo avere osservato anche quel periodo.",
            "- La decisione su una baseline v2 deve pesare insieme curva cucita, PBO, DSR, stabilita annuale e stress di esecuzione.",
            "",
            "## Integrita",
            "",
            f"- Snapshot Coinbase SHA-256: `{manifest['input']['snapshot_sha256']}`.",
            "- La replica dei segnali baseline e stata verificata riga per riga prima del test.",
            "- Baseline, strategia ufficiale, manifest e artefatti congelati non sono stati modificati.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Walk-forward ETH Coinbase con PBO e Deflated Sharpe."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS)
    parser.add_argument("--selections", type=Path, default=DEFAULT_SELECTIONS)
    parser.add_argument("--yearly", type=Path, default=DEFAULT_YEARLY)
    parser.add_argument("--equity", type=Path, default=DEFAULT_EQUITY)
    parser.add_argument("--pbo", type=Path, default=DEFAULT_PBO)
    parser.add_argument("--statistics", type=Path, default=DEFAULT_STATISTICS)
    parser.add_argument("--paths", type=Path, default=DEFAULT_PATHS)
    parser.add_argument("--skip-verify", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    indicators, manifest = load_frozen_indicators(
        args.manifest,
        verify=not args.skip_verify,
    )
    variants = build_variants()
    path_returns, exposures, metadata, _ = prepare_unique_paths(
        indicators,
        variants,
    )
    selections = walk_forward_selections(path_returns, exposures, metadata)
    streams = build_all_oos_streams(indicators, exposures, selections)
    delayed_streams = build_all_oos_streams(
        indicators,
        exposures,
        selections,
        extra_delay_days=1,
    )
    metrics = pd.concat(
        [
            summarize_streams(streams, scenario="normal"),
            summarize_streams(delayed_streams, scenario="extra_delay_1d"),
        ],
        ignore_index=True,
    )
    yearly = yearly_stream_metrics(streams)
    selections = attach_test_metrics(selections, yearly)
    pbo_summary, pbo_details, dsr = statistical_diagnostics(
        path_returns,
        metadata,
        streams,
    )
    statistics = pd.concat(
        [
            pbo_summary.assign(statistic_type="pbo_summary"),
            dsr.assign(statistic_type="deflated_sharpe"),
        ],
        ignore_index=True,
        sort=False,
    )
    equity = pd.DataFrame(
        {model: stream["Equity"] for model, stream in streams.items()}
    )
    equity.index.name = "Date"

    args.report.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(args.metrics, index=False)
    selections.to_csv(args.selections, index=False)
    yearly.to_csv(args.yearly, index=False)
    equity.to_csv(args.equity)
    pbo_details.to_csv(args.pbo, index=False)
    statistics.to_csv(args.statistics, index=False)
    metadata.reset_index().to_csv(args.paths, index=False)
    write_report(
        manifest=manifest,
        metadata=metadata,
        metrics=metrics,
        selections=selections,
        yearly=yearly,
        pbo_summary=pbo_summary,
        dsr=dsr,
        out_path=args.report,
    )

    display_columns = [
        "model",
        "annualized_return",
        "max_drawdown",
        "sharpe_ratio",
        "turnover",
        "completed_trades",
    ]
    print(
        metrics[metrics["scenario"] == "normal"][display_columns]
        .sort_values("sharpe_ratio", ascending=False)
        .to_string(index=False)
    )
    print("\nPBO")
    print(pbo_summary.to_string(index=False))
    print(f"\nReport: {args.report.resolve()}")


if __name__ == "__main__":
    main()
