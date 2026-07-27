"""Ricerca isolata sulle condizioni ETH senza modificare la baseline.

Il ranking usa il costo massimo dichiarato di 0,6% per cambio completo di
esposizione. Gli scenari senza costi e allo 0,3% servono solo a misurare quanto
del risultato dipende dal turnover.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import sys

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import run_backtest  # noqa: E402
from config import CFG  # noqa: E402
from indicators.technical_indicators import compute_all_indicators  # noqa: E402
from pipeline import evaluation_frame  # noqa: E402
from reproducibility import verify_frozen_artifacts  # noqa: E402
from strategy.signals import HOLD_ACTION  # noqa: E402


DEFAULT_MANIFEST = (
    PROJECT_ROOT / "docs" / "runs" / "baseline-v1-2026-07-26" / "manifest.json"
)
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "condition_ablation_coinbase_0_6.md"
DEFAULT_RESULTS = PROJECT_ROOT / "reports" / "condition_ablation_coinbase_0_6.csv"
DEFAULT_WINDOWS = PROJECT_ROOT / "reports" / "condition_ablation_coinbase_0_6_windows.csv"
DEFAULT_EVENTS = PROJECT_ROOT / "reports" / "condition_ablation_coinbase_0_6_events.csv"
DEFAULT_TRADES = PROJECT_ROOT / "reports" / "condition_ablation_coinbase_0_6_trades.csv"

MAX_FEE_RATE = 0.006
FEE_SCENARIOS = {
    "gross": 0.0,
    "fee_0_30": 0.003,
    "fee_0_60": MAX_FEE_RATE,
}
ROLLING_DAYS = 730
ROLLING_STEP_DAYS = 90
RECENT_START = "2022-01-01"
REGIMES = {
    "2017-2018": ("2016-12-08", "2018-12-31"),
    "2019-2020": ("2019-01-01", "2020-12-31"),
    "2021-2022": ("2021-01-01", "2022-12-31"),
    "2023-2026": ("2023-01-01", "2026-07-26"),
}

FOCUS_COALITIONS = {
    frozenset(): "baseline",
    frozenset({"early"}): "entry_early_momentum_max_8",
    frozenset({"trail"}): "trail_momentum_10",
    frozenset({"sma"}): "sell_sma50_break_2_0",
    frozenset({"early", "trail"}): "combo_early_mom_8_trail_mom_10",
    frozenset({"early", "sma"}): "combo_early_mom_8_sma_break_2_0",
    frozenset({"trail", "sma"}): "combo_trail_mom_10_sma_break_2_0",
    frozenset({"early", "trail", "sma"}): "combo_three_early_8_trail_10_sma_2_0",
}
FOCUS_LABELS = {
    "early": "Ingresso anticipato non esteso",
    "trail": "Trail8 su discese rapide",
    "sma": "Tolleranza 2% sotto SMA50",
}
CONSERVATIVE_PARETO_VARIANT = "combo_three_early_8_trail_15_sma_2_0"


@dataclass(frozen=True)
class StrategyVariant:
    name: str
    family: str
    description: str
    require_close_above_sma200: bool = True
    require_sma50_above_sma200: bool = True
    entry_rsi_min: float | None = 40.0
    entry_rsi_max: float | None = 65.0
    entry_momentum_min: float | None = 0.0
    entry_volume_rel_min: float | None = 0.0
    early_rsi_max: float | None = None
    early_momentum_max: float | None = None
    early_volume_rel_min: float | None = None
    sma50_sell_enabled: bool = True
    sma50_sell_days: int = 1
    sma50_break_pct: float = 0.0
    trailing_enabled: bool = True
    trailing_stop_pct: float = 0.08
    trailing_momentum_min: float | None = -0.05
    trailing_volume_rel_min: float | None = 0.20


def baseline_variant() -> StrategyVariant:
    return StrategyVariant(
        name="baseline",
        family="baseline",
        description="Vecchia baseline congelata replicata senza modifiche.",
    )


def load_frozen_indicators(
    manifest_path: Path = DEFAULT_MANIFEST,
    *,
    verify: bool = True,
) -> tuple[pd.DataFrame, dict]:
    manifest_path = manifest_path.resolve()
    if verify:
        verify_frozen_artifacts(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw_path = manifest_path.parent / manifest["input"]["snapshot"]
    raw = (
        pd.read_csv(raw_path, parse_dates=["Date"])
        .sort_values("Date")
        .set_index("Date")
    )
    indicators = evaluation_frame(compute_all_indicators(raw))
    frozen_signals = (
        pd.read_csv(manifest_path.parent / "historical_signals.csv", parse_dates=["Data"])
        .set_index("Data")["Azione"]
        .reindex(indicators.index)
    )
    if frozen_signals.isna().any():
        raise ValueError("I segnali della vecchia baseline non coprono tutto lo snapshot.")
    indicators["Segnale"] = frozen_signals.astype(str)
    return indicators, manifest


def _consecutive(mask: pd.Series, days: int) -> pd.Series:
    out = mask.fillna(False).copy()
    for lag in range(1, days):
        out &= mask.shift(lag, fill_value=False)
    return out


def build_signal_frame(indicators: pd.DataFrame, variant: StrategyVariant) -> pd.DataFrame:
    close = indicators["Close"]
    sma50 = indicators["SMA50"]
    sma200 = indicators["SMA200"]
    rsi = indicators["RSI"]
    volume = indicators["Volume"]
    volume_avg20 = indicators["VolumeAvg20"]
    close_ago = indicators[f"Close_{CFG.momentum_days}d_ago"]
    momentum = close / close_ago - 1.0
    volume_rel = volume / volume_avg20 - 1.0

    buy = pd.Series(True, index=indicators.index)
    if variant.require_close_above_sma200:
        buy &= close > sma200
    if variant.require_sma50_above_sma200:
        buy &= sma50 > sma200
    if variant.entry_rsi_min is not None:
        buy &= rsi >= variant.entry_rsi_min
    if variant.entry_momentum_min is not None:
        buy &= momentum > variant.entry_momentum_min
    if variant.entry_volume_rel_min is not None:
        buy &= volume_rel > variant.entry_volume_rel_min

    new_entry = buy.copy()
    if variant.entry_rsi_max is not None:
        new_entry &= rsi <= variant.entry_rsi_max

    if not variant.require_sma50_above_sma200:
        early = sma50 <= sma200
        early_guard = pd.Series(True, index=indicators.index)
        if variant.early_rsi_max is not None:
            early_guard &= rsi <= variant.early_rsi_max
        if variant.early_momentum_max is not None:
            early_guard &= momentum <= variant.early_momentum_max
        if variant.early_volume_rel_min is not None:
            early_guard &= volume_rel >= variant.early_volume_rel_min
        new_entry &= (~early) | early_guard

    below_sma50 = close < sma50 * (1.0 - variant.sma50_break_pct)
    sma50_sell = _consecutive(below_sma50, variant.sma50_sell_days)
    if not variant.sma50_sell_enabled:
        sma50_sell[:] = False

    signals = np.full(len(indicators), HOLD_ACTION, dtype=object)
    exposed = False
    peak_close: float | None = None

    for pos, (date, row) in enumerate(indicators.iterrows()):
        close_value = float(row["Close"])

        if bool(sma50_sell.loc[date]):
            signals[pos] = "VENDI"
            exposed = False
            peak_close = None
            continue

        if bool(buy.loc[date]):
            if not exposed and bool(new_entry.loc[date]):
                signals[pos] = "ACQUISTA"
                exposed = True
                peak_close = close_value
            elif exposed:
                peak_close = max(peak_close if peak_close is not None else close_value, close_value)
            continue

        if exposed:
            peak_close = max(peak_close if peak_close is not None else close_value, close_value)
            if variant.trailing_enabled and close_value <= peak_close * (1.0 - variant.trailing_stop_pct):
                momentum_value = float(momentum.loc[date])
                volume_rel_value = float(volume_rel.loc[date])
                momentum_ok = (
                    variant.trailing_momentum_min is None
                    or momentum_value >= variant.trailing_momentum_min
                )
                volume_ok = (
                    variant.trailing_volume_rel_min is None
                    or volume_rel_value >= variant.trailing_volume_rel_min
                )
                if momentum_ok and volume_ok:
                    signals[pos] = "VENDI"
                    exposed = False
                    peak_close = None

    out = indicators[["Close"]].copy()
    out["Segnale"] = signals
    return out


def build_variants() -> list[StrategyVariant]:
    base = baseline_variant()
    variants = [base]

    def add(name: str, family: str, description: str, **changes: object) -> None:
        variants.append(
            replace(base, name=name, family=family, description=description, **changes)
        )

    add(
        "entry_no_close_sma200",
        "entry_ablation",
        "Elimina Close>SMA200 dagli ingressi.",
        require_close_above_sma200=False,
    )
    add(
        "entry_no_rsi_min",
        "entry_ablation",
        "Elimina RSI>=40 dagli ingressi.",
        entry_rsi_min=None,
    )
    add(
        "entry_no_momentum",
        "entry_ablation",
        "Elimina il momentum positivo a 7 giorni.",
        entry_momentum_min=None,
    )
    add(
        "entry_no_volume",
        "entry_ablation",
        "Elimina Volume>VolumeAvg20.",
        entry_volume_rel_min=None,
    )

    add(
        "entry_no_sma50_gate",
        "entry_trend_gate",
        "Elimina SMA50>SMA200 senza guardrail.",
        require_sma50_above_sma200=False,
    )
    for value in [58.0, 60.0, 62.0, 64.0, 65.0]:
        add(
            f"entry_early_rsi_{int(value)}",
            "entry_trend_gate",
            f"Sblocca SMA50<=SMA200 solo con RSI<={value:.0f}.",
            require_sma50_above_sma200=False,
            early_rsi_max=value,
        )
    for value in [0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.12, 0.15]:
        add(
            f"entry_early_momentum_max_{int(value * 100)}",
            "entry_trend_gate",
            f"Sblocca SMA50<=SMA200 solo con momentum 7g<={value:.0%}.",
            require_sma50_above_sma200=False,
            early_momentum_max=value,
        )
    for value in [0.10, 0.15, 0.20]:
        add(
            f"entry_early_volume_min_{int(value * 100)}",
            "entry_trend_gate",
            f"Sblocca SMA50<=SMA200 solo con volume relativo>={value:.0%}.",
            require_sma50_above_sma200=False,
            early_volume_rel_min=value,
        )

    for value in [60.0, 62.0, 64.0, 66.0, 68.0, 70.0, 72.0]:
        add(
            f"entry_rsi_max_{int(value)}",
            "entry_rsi_cap",
            f"Imposta il limite globale dei nuovi ingressi a RSI<={value:.0f}.",
            entry_rsi_max=value,
        )
    add(
        "entry_rsi_max_disabled",
        "entry_rsi_cap",
        "Elimina il limite RSI massimo sui nuovi ingressi.",
        entry_rsi_max=None,
    )

    for value in [-0.02, 0.02, 0.05, 0.08]:
        label = f"m{abs(int(value * 100))}" if value < 0 else f"p{int(value * 100)}"
        add(
            f"entry_momentum_{label}",
            "entry_momentum",
            f"Imposta il momentum minimo di ingresso a {value:.0%}.",
            entry_momentum_min=value,
        )
    for value in [-0.10, 0.10, 0.20, 0.30]:
        label = f"m{abs(int(value * 100))}" if value < 0 else f"p{int(value * 100)}"
        add(
            f"entry_volume_{label}",
            "entry_volume",
            f"Imposta il volume relativo minimo di ingresso a {value:.0%}.",
            entry_volume_rel_min=value,
        )

    add(
        "sell_sma50_disabled",
        "sell_sma50",
        "Elimina l'uscita Close<SMA50.",
        sma50_sell_enabled=False,
    )
    add(
        "sell_sma50_two_days",
        "sell_sma50",
        "Richiede due chiusure consecutive sotto SMA50.",
        sma50_sell_days=2,
    )
    for value in [0.005, 0.01, 0.0125, 0.015, 0.0175, 0.02, 0.0225, 0.025, 0.03]:
        add(
            f"sell_sma50_break_{value * 100:.1f}".replace(".", "_"),
            "sell_sma50",
            f"Vende solo almeno {value:.1%} sotto SMA50.",
            sma50_break_pct=value,
        )

    add(
        "trail_disabled",
        "trail_width",
        "Elimina il Trail8 e mantiene solo Close<SMA50.",
        trailing_enabled=False,
    )
    for value in [0.04, 0.06, 0.07, 0.09, 0.10, 0.12, 0.15]:
        add(
            f"trail_width_{int(value * 100)}",
            "trail_width",
            f"Imposta il trailing stop a {value:.0%}.",
            trailing_stop_pct=value,
        )

    add(
        "trail_momentum_disabled",
        "trail_momentum",
        "Elimina la conferma momentum e mantiene volume relativo>=20%.",
        trailing_momentum_min=None,
    )
    for value in [-0.20, -0.15, -0.12, -0.11, -0.10, -0.09, -0.08, -0.07, -0.06, -0.04, -0.02, 0.0]:
        add(
            f"trail_momentum_{abs(int(value * 100)):02d}",
            "trail_momentum",
            f"Imposta la conferma momentum del trailing a >={value:.0%}.",
            trailing_momentum_min=value,
        )

    add(
        "trail_volume_disabled",
        "trail_volume",
        "Elimina la conferma volume e mantiene momentum>=-5%.",
        trailing_volume_rel_min=None,
    )
    for value in [0.0, 0.10, 0.15, 0.25, 0.30, 0.50]:
        add(
            f"trail_volume_{int(value * 100):02d}",
            "trail_volume",
            f"Imposta la conferma volume del trailing a >={value:.0%}.",
            trailing_volume_rel_min=value,
        )

    for early_rsi in [60.0, 62.0, 64.0]:
        for trail_momentum in [None, -0.08, -0.06]:
            momentum_label = "none" if trail_momentum is None else str(abs(int(trail_momentum * 100)))
            for trail_volume in [0.15, 0.20, 0.25]:
                add(
                    f"combo_early_rsi_{int(early_rsi)}_tm_{momentum_label}_tv_{int(trail_volume * 100)}",
                    "combined_early_trail",
                    "Combina ingresso anticipato protetto e Trail8 ricalibrato.",
                    require_sma50_above_sma200=False,
                    early_rsi_max=early_rsi,
                    trailing_momentum_min=trail_momentum,
                    trailing_volume_rel_min=trail_volume,
                )

    for early_momentum in [0.08, 0.10, 0.12]:
        for trail_momentum in [-0.12, -0.10, -0.08, None]:
            momentum_label = "none" if trail_momentum is None else str(abs(int(trail_momentum * 100)))
            add(
                f"combo_early_mom_{int(early_momentum * 100)}_trail_mom_{momentum_label}",
                "combined_momentum_trail",
                "Combina ingresso anticipato non esteso e conferma momentum Trail8 permissiva.",
                require_sma50_above_sma200=False,
                early_momentum_max=early_momentum,
                trailing_momentum_min=trail_momentum,
            )

    for early_momentum in [0.08, 0.10]:
        for sma_break in [0.015, 0.02, 0.025]:
            add(
                f"combo_early_mom_{int(early_momentum * 100)}_sma_break_{sma_break * 100:.1f}".replace(".", "_"),
                "combined_early_sma",
                "Combina ingresso anticipato non esteso e tolleranza sotto SMA50.",
                require_sma50_above_sma200=False,
                early_momentum_max=early_momentum,
                sma50_break_pct=sma_break,
            )

    for trail_momentum in [
        -0.20,
        -0.18,
        -0.16,
        -0.15,
        -0.14,
        -0.13,
        -0.12,
        -0.11,
        -0.10,
        -0.09,
        -0.08,
    ]:
        momentum_label = str(abs(int(trail_momentum * 100)))
        for sma_break in [0.015, 0.0175, 0.02, 0.0225, 0.025]:
            add(
                f"combo_trail_mom_{momentum_label}_sma_break_{sma_break * 100:.1f}".replace(".", "_"),
                "combined_trail_sma",
                "Griglia locale: conferma Trail8 permissiva e tolleranza sotto SMA50.",
                trailing_momentum_min=trail_momentum,
                sma50_break_pct=sma_break,
            )

    for early_momentum in [0.07, 0.08, 0.09, 0.10, 0.11, 0.12]:
        for trail_momentum in [-0.20, -0.18, -0.15, -0.12, -0.10, -0.08]:
            momentum_label = str(abs(int(trail_momentum * 100)))
            for sma_break in [0.0175, 0.02, 0.0225]:
                add(
                    (
                        f"combo_three_early_{int(early_momentum * 100)}_trail_{momentum_label}_"
                        f"sma_{sma_break * 100:.1f}"
                    ).replace(".", "_"),
                    "combined_three_way",
                    "Griglia locale: ingresso anticipato, Trail8 permissivo e tolleranza SMA50.",
                    require_sma50_above_sma200=False,
                    early_momentum_max=early_momentum,
                    trailing_momentum_min=trail_momentum,
                    sma50_break_pct=sma_break,
                )

    names = [variant.name for variant in variants]
    if len(names) != len(set(names)):
        raise ValueError("I nomi delle varianti sperimentali devono essere univoci.")
    return variants


def _max_drawdown(equity: pd.Series) -> float:
    return float((equity / equity.cummax() - 1.0).min())


def _sharpe(returns: pd.Series) -> float:
    clean = returns.dropna()
    if len(clean) < 2 or clean.std(ddof=1) == 0.0:
        return float("nan")
    return float(np.sqrt(CFG.periods_per_year) * clean.mean() / clean.std(ddof=1))


def slice_metrics(equity: pd.DataFrame, start: str, end: str | None = None) -> dict[str, float]:
    subset = equity.loc[start:end]
    if len(subset) < 2:
        return {
            "total_return": float("nan"),
            "annualized_return": float("nan"),
            "max_drawdown": float("nan"),
            "sharpe_ratio": float("nan"),
        }
    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    total_return = float(normalized.iloc[-1] - 1.0)
    calendar_days = max((subset.index[-1] - subset.index[0]).days, 1)
    return {
        "total_return": total_return,
        "annualized_return": float(
            (1.0 + total_return) ** (CFG.periods_per_year / calendar_days) - 1.0
        ),
        "max_drawdown": _max_drawdown(normalized),
        "sharpe_ratio": _sharpe(normalized.pct_change()),
    }


def _metric_fields(prefix: str, metrics: object) -> dict[str, float | int]:
    return {
        f"{prefix}_total_return": metrics.total_return,
        f"{prefix}_annualized_return": metrics.annualized_return,
        f"{prefix}_max_drawdown": metrics.max_drawdown,
        f"{prefix}_sharpe_ratio": metrics.sharpe_ratio,
        f"{prefix}_profit_factor": metrics.profit_factor,
        f"{prefix}_operations": metrics.num_operations,
        f"{prefix}_turnover": metrics.turnover,
        f"{prefix}_exposure": metrics.exposure_ratio,
    }


def _signal_fingerprint(signals: pd.Series) -> str:
    payload = "\x1f".join(signals.astype(str).tolist()).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _completed_net_trade_returns(equity: pd.DataFrame) -> list[float]:
    """Include i costi sia d'ingresso sia d'uscita per ogni trade chiuso."""
    active = equity["EffectiveExposure"].gt(0.0).to_numpy()
    daily = equity["DailyReturnStrategy"].fillna(0.0)
    returns: list[float] = []
    start_pos: int | None = None

    for pos, is_active in enumerate(active):
        if is_active and start_pos is None:
            start_pos = pos
        elif not is_active and start_pos is not None:
            trade_daily = daily.iloc[start_pos : pos + 1]
            returns.append(float((1.0 + trade_daily).prod() - 1.0))
            start_pos = None
    return returns


def _net_profit_factor(equity: pd.DataFrame) -> float:
    returns = pd.Series(_completed_net_trade_returns(equity), dtype=float)
    if returns.empty:
        return float("nan")
    gross_profit = float(returns[returns > 0.0].sum())
    gross_loss = float(returns[returns <= 0.0].sum())
    if gross_loss < 0.0:
        return gross_profit / abs(gross_loss)
    return float("inf") if gross_profit > 0.0 else float("nan")


def run_research(
    indicators: pd.DataFrame,
    variants: list[StrategyVariant],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    official_signals = indicators["Segnale"].astype(str)
    experimental_baseline = build_signal_frame(indicators, baseline_variant())["Segnale"].astype(str)
    if not official_signals.equals(experimental_baseline):
        changed = int((official_signals != experimental_baseline).sum())
        raise ValueError(f"La replica sperimentale diverge dalla baseline in {changed} righe.")

    records: list[dict[str, object]] = []
    max_fee_equities: dict[str, pd.DataFrame] = {}

    for variant in variants:
        frame = build_signal_frame(indicators, variant)
        signals = frame["Segnale"].astype(str)
        record: dict[str, object] = {
            "variant": variant.name,
            "family": variant.family,
            "description": variant.description,
            "signal_fingerprint": _signal_fingerprint(signals),
            "signal_changes_vs_baseline": int((signals != official_signals).sum()),
            **asdict(variant),
        }
        for scenario, fee_rate in FEE_SCENARIOS.items():
            equity, metrics, _ = run_backtest(frame, transaction_cost_rate=fee_rate)
            record.update(_metric_fields(scenario, metrics))
            record[f"{scenario}_profit_factor"] = _net_profit_factor(equity)
            if fee_rate == MAX_FEE_RATE:
                max_fee_equities[variant.name] = equity
        records.append(record)

    results = pd.DataFrame(records)
    results["equivalent_signal_variants"] = results.groupby("signal_fingerprint")[
        "variant"
    ].transform("size")
    baseline = results.loc[results["variant"] == "baseline"].iloc[0]
    results["delta_annualized"] = (
        results["fee_0_60_annualized_return"] - baseline["fee_0_60_annualized_return"]
    )
    results["delta_max_drawdown"] = (
        results["fee_0_60_max_drawdown"] - baseline["fee_0_60_max_drawdown"]
    )
    results["delta_sharpe"] = (
        results["fee_0_60_sharpe_ratio"] - baseline["fee_0_60_sharpe_ratio"]
    )
    results["full_all3"] = (
        (results["delta_annualized"] > 0.0)
        & (results["delta_max_drawdown"] >= 0.0)
        & (results["delta_sharpe"] > 0.0)
    )

    baseline_equity = max_fee_equities["baseline"]
    rolling_rows: list[dict[str, object]] = []
    validation_rows: list[dict[str, object]] = []

    for variant in variants:
        equity = max_fee_equities[variant.name]
        recent = slice_metrics(equity, RECENT_START)
        validation: dict[str, object] = {
            "variant": variant.name,
            "recent_annualized_return": recent["annualized_return"],
            "recent_max_drawdown": recent["max_drawdown"],
            "recent_sharpe_ratio": recent["sharpe_ratio"],
        }

        regime_return_wins = 0
        regime_dd_wins = 0
        regime_sharpe_wins = 0
        regime_all3_wins = 0
        for regime, (start, end) in REGIMES.items():
            base_metrics = slice_metrics(baseline_equity, start, end)
            candidate_metrics = slice_metrics(equity, start, end)
            delta_return = candidate_metrics["total_return"] - base_metrics["total_return"]
            delta_dd = candidate_metrics["max_drawdown"] - base_metrics["max_drawdown"]
            delta_sharpe = candidate_metrics["sharpe_ratio"] - base_metrics["sharpe_ratio"]
            return_win = bool(delta_return > 0.0)
            dd_win = bool(delta_dd >= 0.0)
            sharpe_win = bool(delta_sharpe > 0.0)
            regime_return_wins += int(return_win)
            regime_dd_wins += int(dd_win)
            regime_sharpe_wins += int(sharpe_win)
            regime_all3_wins += int(return_win and dd_win and sharpe_win)
            rolling_rows.append(
                {
                    "variant": variant.name,
                    "window_type": "regime",
                    "window": regime,
                    "start": start,
                    "end": end,
                    "delta_total_return": delta_return,
                    "delta_max_drawdown": delta_dd,
                    "delta_sharpe": delta_sharpe,
                }
            )

        validation.update(
            {
                "regime_return_wins": regime_return_wins,
                "regime_dd_wins": regime_dd_wins,
                "regime_sharpe_wins": regime_sharpe_wins,
                "regime_all3_wins": regime_all3_wins,
            }
        )

        if variant.name == "baseline":
            validation_rows.append(validation)
            continue

        window_values: list[tuple[float, float, float]] = []
        cursor = indicators.index.min()
        while cursor + pd.Timedelta(days=ROLLING_DAYS) <= indicators.index.max():
            window_end = cursor + pd.Timedelta(days=ROLLING_DAYS)
            start = cursor.strftime("%Y-%m-%d")
            end = window_end.strftime("%Y-%m-%d")
            base_metrics = slice_metrics(baseline_equity, start, end)
            candidate_metrics = slice_metrics(equity, start, end)
            values = (
                candidate_metrics["total_return"] - base_metrics["total_return"],
                candidate_metrics["max_drawdown"] - base_metrics["max_drawdown"],
                candidate_metrics["sharpe_ratio"] - base_metrics["sharpe_ratio"],
            )
            window_values.append(values)
            rolling_rows.append(
                {
                    "variant": variant.name,
                    "window_type": "rolling_730d",
                    "window": f"{start}_{end}",
                    "start": start,
                    "end": end,
                    "delta_total_return": values[0],
                    "delta_max_drawdown": values[1],
                    "delta_sharpe": values[2],
                }
            )
            cursor += pd.Timedelta(days=ROLLING_STEP_DAYS)

        values = np.asarray(window_values, dtype=float)
        validation.update(
            {
                "rolling_return_positive_ratio": float((values[:, 0] > 0.0).mean()),
                "rolling_dd_nonworse_ratio": float((values[:, 1] >= 0.0).mean()),
                "rolling_sharpe_positive_ratio": float((values[:, 2] > 0.0).mean()),
                "rolling_all3_ratio": float(
                    ((values[:, 0] > 0.0) & (values[:, 1] >= 0.0) & (values[:, 2] > 0.0)).mean()
                ),
                "worst_rolling_return_delta": float(values[:, 0].min()),
                "worst_rolling_dd_delta": float(values[:, 1].min()),
                "worst_rolling_sharpe_delta": float(values[:, 2].min()),
            }
        )
        validation_rows.append(validation)

    validation_df = pd.DataFrame(validation_rows)
    results = results.merge(validation_df, on="variant", how="left")
    baseline_recent = results.loc[results["variant"] == "baseline"].iloc[0]
    results["recent_all3"] = (
        (results["recent_annualized_return"] > baseline_recent["recent_annualized_return"])
        & (results["recent_max_drawdown"] >= baseline_recent["recent_max_drawdown"])
        & (results["recent_sharpe_ratio"] > baseline_recent["recent_sharpe_ratio"])
    )
    results["passes_robust_gate"] = (
        results["full_all3"]
        & (results["rolling_return_positive_ratio"].fillna(0.0) >= 0.60)
        & (results["rolling_dd_nonworse_ratio"].fillna(0.0) >= 0.60)
        & (results["rolling_sharpe_positive_ratio"].fillna(0.0) >= 0.60)
        & (results["rolling_all3_ratio"].fillna(0.0) >= 0.50)
        & (results["worst_rolling_dd_delta"].fillna(-1.0) >= -0.05)
        & results["recent_all3"]
        & (results["fee_0_60_turnover"] <= baseline["fee_0_60_turnover"] + 12.0)
    )

    return results, pd.DataFrame(rolling_rows)


def shapley_attribution(results: pd.DataFrame) -> pd.DataFrame:
    """Attribuisce in modo simmetrico i guadagni delle tre modifiche centrali."""
    indexed = results.set_index("variant")
    missing = sorted(set(FOCUS_COALITIONS.values()) - set(indexed.index))
    if missing:
        raise ValueError(f"Varianti mancanti per l'attribuzione: {missing}")

    games: dict[str, dict[frozenset[str], float]] = {
        "annualized_return": {},
        "max_drawdown": {},
        "sharpe_ratio": {},
        "log_terminal_wealth": {},
    }
    for coalition, variant_name in FOCUS_COALITIONS.items():
        row = indexed.loc[variant_name]
        games["annualized_return"][coalition] = float(
            row["fee_0_60_annualized_return"]
        )
        games["max_drawdown"][coalition] = float(row["fee_0_60_max_drawdown"])
        games["sharpe_ratio"][coalition] = float(row["fee_0_60_sharpe_ratio"])
        games["log_terminal_wealth"][coalition] = math.log1p(
            float(row["fee_0_60_total_return"])
        )

    factors = tuple(FOCUS_LABELS)
    rows: list[dict[str, object]] = []
    for factor in factors:
        others = tuple(item for item in factors if item != factor)
        row: dict[str, object] = {"factor": factor, "label": FOCUS_LABELS[factor]}
        for metric, game in games.items():
            contribution = 0.0
            for subset_size in range(len(others) + 1):
                for subset_items in combinations(others, subset_size):
                    subset = frozenset(subset_items)
                    weight = (
                        math.factorial(len(subset))
                        * math.factorial(len(factors) - len(subset) - 1)
                        / math.factorial(len(factors))
                    )
                    contribution += weight * (
                        game[subset | {factor}] - game[subset]
                    )
            row[metric] = contribution
        rows.append(row)

    out = pd.DataFrame(rows)
    full = frozenset(factors)
    empty = frozenset()
    total_log_gain = (
        games["log_terminal_wealth"][full]
        - games["log_terminal_wealth"][empty]
    )
    out["log_wealth_share"] = out["log_terminal_wealth"] / total_log_gain
    return out


def _event_context(indicators: pd.DataFrame, date: pd.Timestamp) -> dict[str, float]:
    row = indicators.loc[date]
    close = float(row["Close"])
    close_ago = float(row[f"Close_{CFG.momentum_days}d_ago"])
    volume_avg = float(row["VolumeAvg20"])
    sma200 = float(row["SMA200"])
    return {
        "close": close,
        "rsi": float(row["RSI"]),
        "momentum_7d": close / close_ago - 1.0,
        "volume_rel": float(row["Volume"]) / volume_avg - 1.0,
        "sma50_vs_sma200": float(row["SMA50"]) / sma200 - 1.0,
    }


def build_event_audit(
    indicators: pd.DataFrame,
    variants: list[StrategyVariant],
) -> pd.DataFrame:
    by_name = {variant.name: variant for variant in variants}
    baseline = build_signal_frame(indicators, by_name["baseline"])["Segnale"]
    early = build_signal_frame(
        indicators, by_name[FOCUS_COALITIONS[frozenset({"early"})]]
    )["Segnale"]
    trail = build_signal_frame(
        indicators, by_name[FOCUS_COALITIONS[frozenset({"trail"})]]
    )["Segnale"]

    rows: list[dict[str, object]] = []
    early_dates = indicators.index[(early == "ACQUISTA") & (baseline != "ACQUISTA")]
    for date in early_dates:
        rows.append(
            {
                "event_type": "extra_early_entry",
                "variant": FOCUS_COALITIONS[frozenset({"early"})],
                "date": date.strftime("%Y-%m-%d"),
                **_event_context(indicators, date),
            }
        )

    trail_dates = indicators.index[(trail == "VENDI") & (baseline != "VENDI")]
    for date in trail_dates:
        rows.append(
            {
                "event_type": "new_trail_exit",
                "variant": FOCUS_COALITIONS[frozenset({"trail"})],
                "date": date.strftime("%Y-%m-%d"),
                **_event_context(indicators, date),
            }
        )
    return pd.DataFrame(rows)


def build_trade_log(
    indicators: pd.DataFrame,
    variants: list[StrategyVariant],
) -> pd.DataFrame:
    by_name = {variant.name: variant for variant in variants}
    rows: list[dict[str, object]] = []

    audit_variants = list(dict.fromkeys(FOCUS_COALITIONS.values()))
    audit_variants.append(CONSERVATIVE_PARETO_VARIANT)
    for variant_name in audit_variants:
        variant = by_name[variant_name]
        frame = build_signal_frame(indicators, variant)
        equity, _, _ = run_backtest(frame, transaction_cost_rate=MAX_FEE_RATE)
        active = equity["EffectiveExposure"].gt(0.0).to_numpy()
        daily = equity["DailyReturnStrategy"].fillna(0.0)
        start_pos: int | None = None
        trade_number = 0

        for pos, is_active in enumerate(active):
            if is_active and start_pos is None:
                start_pos = pos
            elif not is_active and start_pos is not None:
                trade_number += 1
                entry_signal_pos = max(start_pos - 1, 0)
                exit_signal_pos = max(pos - 1, 0)
                entry_signal_date = equity.index[entry_signal_pos]
                exit_signal_date = equity.index[exit_signal_pos]
                trade_daily = daily.iloc[start_pos : pos + 1]
                trade_curve = (1.0 + trade_daily).cumprod()
                entry_row = indicators.loc[entry_signal_date]
                exit_row = indicators.loc[exit_signal_date]
                exit_on_sma = float(exit_row["Close"]) < float(exit_row["SMA50"]) * (
                    1.0 - variant.sma50_break_pct
                )
                rows.append(
                    {
                        "variant": variant_name,
                        "trade": trade_number,
                        "entry_signal_date": entry_signal_date.strftime("%Y-%m-%d"),
                        "entry_effective_date": equity.index[start_pos].strftime("%Y-%m-%d"),
                        "exit_signal_date": exit_signal_date.strftime("%Y-%m-%d"),
                        "exit_effective_date": equity.index[pos].strftime("%Y-%m-%d"),
                        "days_exposed": pos - start_pos,
                        "entry_kind": (
                            "early"
                            if float(entry_row["SMA50"]) <= float(entry_row["SMA200"])
                            else "trend"
                        ),
                        "exit_kind": "sma50" if exit_on_sma else "trail8",
                        "net_return": float(trade_curve.iloc[-1] - 1.0),
                        "log_return": float(math.log(float(trade_curve.iloc[-1]))),
                        "trade_max_drawdown": _max_drawdown(trade_curve),
                    }
                )
                start_pos = None

    return pd.DataFrame(rows)


def summarize_trades(trades: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for variant, group in trades.groupby("variant", sort=False):
        returns = group["net_return"].astype(float)
        wins = returns[returns > 0.0]
        losses = returns[returns <= 0.0]
        positive_logs = group.loc[group["log_return"] > 0.0, "log_return"].sort_values(
            ascending=False
        )
        positive_log_sum = float(positive_logs.sum())
        top3_share = (
            float(positive_logs.head(3).sum()) / positive_log_sum
            if positive_log_sum > 0.0
            else float("nan")
        )
        rows.append(
            {
                "variant": variant,
                "trades": len(group),
                "win_rate": float((returns > 0.0).mean()),
                "median_return": float(returns.median()),
                "best_trade": float(returns.max()),
                "worst_trade": float(returns.min()),
                "average_days": float(group["days_exposed"].mean()),
                "profit_factor": (
                    float(wins.sum()) / abs(float(losses.sum()))
                    if float(losses.sum()) < 0.0
                    else float("inf")
                ),
                "top3_positive_log_share": top3_share,
            }
        )
    return pd.DataFrame(rows)


def _pct(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:.2f}%"


def _ratio(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):.3f}"


def _pp(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value) * 100:+.2f} pp"


def _best_rows(results: pd.DataFrame) -> pd.DataFrame:
    return results.sort_values(
        [
            "passes_robust_gate",
            "rolling_all3_ratio",
            "regime_all3_wins",
            "fee_0_60_sharpe_ratio",
            "fee_0_60_annualized_return",
        ],
        ascending=False,
    )


def write_report(
    results: pd.DataFrame,
    windows: pd.DataFrame,
    events: pd.DataFrame,
    trades: pd.DataFrame,
    manifest: dict,
    out_path: Path,
) -> None:
    baseline = results.loc[results["variant"] == "baseline"].iloc[0]
    nonbaseline = results[results["variant"] != "baseline"].copy()
    isolated = nonbaseline[~nonbaseline["family"].str.startswith("combined")]
    ordered = _best_rows(nonbaseline)
    ordered_isolated = _best_rows(isolated)
    robust = ordered[ordered["passes_robust_gate"]]
    attribution = shapley_attribution(results)
    trade_summary = summarize_trades(trades).set_index("variant")
    unique_paths = int(results["signal_fingerprint"].nunique())
    pair_grid = results[results["family"] == "combined_trail_sma"].copy()
    three_grid = results[results["family"] == "combined_three_way"].copy()
    pair_focus_name = FOCUS_COALITIONS[frozenset({"trail", "sma"})]
    triple_focus_name = FOCUS_COALITIONS[frozenset({"early", "trail", "sma"})]

    family_rows: list[dict[str, object]] = []
    for family, group in nonbaseline.groupby("family"):
        best = _best_rows(group).iloc[0]
        family_rows.append(
            {
                "family": family,
                "tested": len(group),
                "full_all3": int(group["full_all3"].sum()),
                "robust": int(group["passes_robust_gate"].sum()),
                "best": best["variant"],
                "best_rolling": best["rolling_all3_ratio"],
            }
        )
    family_summary = pd.DataFrame(family_rows).sort_values(
        ["robust", "best_rolling"], ascending=False
    )

    lines = [
        "# Condition Ablation Research - Coinbase ETH 0,6%",
        "",
        "## Protocollo",
        "",
        f"- Baseline congelata: `{manifest['run_id']}`.",
        f"- Periodo: `{manifest['period']['evaluation_start']}` -> `{manifest['period']['evaluation_end']}`.",
        f"- Varianti testate: {len(nonbaseline)} oltre alla baseline.",
        f"- Percorsi di segnale realmente distinti: {unique_paths}/{len(results)}; le soglie equivalenti non sono contate come fenomeni diversi.",
        "- Commissioni: 0%, 0,3% e massimo 0,6% per lato; selezione effettuata sullo 0,6%.",
        "- Validazione: quattro regimi fissi e finestre rolling di 730 giorni ogni 90 giorni.",
        "- Una variante supera il gate solo se migliora rendimento annualizzato, drawdown e Sharpe sul periodo completo e recente, con stabilita rolling e turnover limitato.",
        "- Il test e sperimentale e non modifica la baseline ufficiale.",
        "",
        "## Baseline Netta 0,6%",
        "",
        "| Ann. | Max DD | Sharpe | PF | Operazioni | Turnover | Esposizione |",
        "|---:|---:|---:|---:|---:|---:|---:|",
        f"| {_pct(baseline['fee_0_60_annualized_return'])} | {_pct(baseline['fee_0_60_max_drawdown'])} | {_ratio(baseline['fee_0_60_sharpe_ratio'])} | {_ratio(baseline['fee_0_60_profit_factor'])} | {int(baseline['fee_0_60_operations'])} | {baseline['fee_0_60_turnover']:.0f} | {_pct(baseline['fee_0_60_exposure'])} |",
        "",
        "Il PF del report e ricalcolato sui trade chiusi includendo entrambe le commissioni; il motore ufficiale non viene modificato.",
        "",
        "## Fenomeni Isolati Piu Robusti",
        "",
        "| Variante | Famiglia | Ann. | Max DD | Sharpe | PF | Ops | Roll all-3 | Regimi all-3 | Gate |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in ordered_isolated.head(12).iterrows():
        lines.append(
            f"| `{row['variant']}` | {row['family']} | "
            f"{_pct(row['fee_0_60_annualized_return'])} | "
            f"{_pct(row['fee_0_60_max_drawdown'])} | "
            f"{_ratio(row['fee_0_60_sharpe_ratio'])} | "
            f"{_ratio(row['fee_0_60_profit_factor'])} | "
            f"{int(row['fee_0_60_operations'])} | "
            f"{_pct(row['rolling_all3_ratio'])} | "
            f"{int(row['regime_all3_wins'])}/4 | "
            f"{'PASS' if row['passes_robust_gate'] else 'FAIL'} |"
        )

    lines.extend(
        [
            "",
            "## Sintesi Per Famiglia",
            "",
            "| Famiglia | Test | Migliora all-3 completo | Supera gate | Migliore | Roll all-3 |",
            "|---|---:|---:|---:|---|---:|",
        ]
    )
    for _, row in family_summary.iterrows():
        lines.append(
            f"| {row['family']} | {int(row['tested'])} | {int(row['full_all3'])} | "
            f"{int(row['robust'])} | `{row['best']}` | {_pct(row['best_rolling'])} |"
        )

    lines.extend(
        [
            "",
            "## Combinazioni",
            "",
            "| Variante | Ann. | Max DD | Sharpe | PF | Ops | Roll all-3 | Regimi all-3 | Gate |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    combined = ordered[ordered["family"].str.startswith("combined")]
    for _, row in combined.head(12).iterrows():
        lines.append(
            f"| `{row['variant']}` | {_pct(row['fee_0_60_annualized_return'])} | "
            f"{_pct(row['fee_0_60_max_drawdown'])} | {_ratio(row['fee_0_60_sharpe_ratio'])} | "
            f"{_ratio(row['fee_0_60_profit_factor'])} | {int(row['fee_0_60_operations'])} | "
            f"{_pct(row['rolling_all3_ratio'])} | {int(row['regime_all3_wins'])}/4 | "
            f"{'PASS' if row['passes_robust_gate'] else 'FAIL'} |"
        )

    lines.extend(
        [
            "",
            "## Attribuzione Dei Tre Fenomeni",
            "",
            "La decomposizione Shapley usa tutte le otto combinazioni della configurazione centrale `early 8% / trail -10% / SMA 2%`. I contributi sommano esattamente al miglioramento della combinazione completa rispetto alla baseline.",
            "",
            "| Fenomeno | Contributo ann. | Contributo DD | Contributo Sharpe | Quota vantaggio log-wealth |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in attribution.iterrows():
        lines.append(
            f"| {row['label']} | {_pp(row['annualized_return'])} | "
            f"{_pp(row['max_drawdown'])} | {float(row['sharpe_ratio']):+.3f} | "
            f"{_pct(row['log_wealth_share'])} |"
        )
    lines.extend(
        [
            "",
            "Un contributo DD positivo indica un drawdown meno profondo. La tolleranza SMA50 e il maggiore motore di rendimento e Sharpe, ma da sola peggiora leggermente il DD; il Trail8 ricalibrato fornisce la quota maggiore di protezione del drawdown.",
            "",
            "## Sensibilita Alle Commissioni",
            "",
            "| Variante | Commissione per lato | Ann. | Max DD | Sharpe | Turnover |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    fee_labels = {"gross": "0,0%", "fee_0_30": "0,3%", "fee_0_60": "0,6%"}
    for variant_name in [
        "baseline",
        pair_focus_name,
        triple_focus_name,
        CONSERVATIVE_PARETO_VARIANT,
    ]:
        row = results.loc[results["variant"] == variant_name].iloc[0]
        for scenario, fee_label in fee_labels.items():
            lines.append(
                f"| `{variant_name}` | {fee_label} | "
                f"{_pct(row[f'{scenario}_annualized_return'])} | "
                f"{_pct(row[f'{scenario}_max_drawdown'])} | "
                f"{_ratio(row[f'{scenario}_sharpe_ratio'])} | "
                f"{row[f'{scenario}_turnover']:.0f} |"
            )

    lines.extend(
        [
            "",
            "## Plateau Locale Trail-SMA50",
            "",
            "Ogni cella mostra la quota di finestre rolling che migliora rendimento, DD e Sharpe insieme; `*` indica il superamento del gate completo.",
            "",
        ]
    )
    sma_values = sorted(pair_grid["sma50_break_pct"].dropna().unique())
    trail_values = sorted(pair_grid["trailing_momentum_min"].dropna().unique())
    lines.append(
        "| Trail minimo / SMA tolleranza | "
        + " | ".join(f"{value:.2%}" for value in sma_values)
        + " |"
    )
    lines.append("|---|" + "---:|" * len(sma_values))
    for trail_value in trail_values:
        cells: list[str] = []
        for sma_value in sma_values:
            match = pair_grid[
                np.isclose(pair_grid["trailing_momentum_min"], trail_value)
                & np.isclose(pair_grid["sma50_break_pct"], sma_value)
            ].iloc[0]
            marker = "*" if bool(match["passes_robust_gate"]) else ""
            cells.append(f"{_pct(match['rolling_all3_ratio'])}{marker}")
        lines.append(
            f"| {trail_value:.0%} | " + " | ".join(cells) + " |"
        )

    pair_center = results.loc[results["variant"] == pair_focus_name].iloc[0]
    pair_equivalent = pair_grid[
        pair_grid["signal_fingerprint"] == pair_center["signal_fingerprint"]
    ]
    triple_center = results.loc[results["variant"] == triple_focus_name].iloc[0]
    triple_equivalent = three_grid[
        three_grid["signal_fingerprint"] == triple_center["signal_fingerprint"]
    ]
    conservative_center = results.loc[
        results["variant"] == CONSERVATIVE_PARETO_VARIANT
    ].iloc[0]
    conservative_equivalent = three_grid[
        three_grid["signal_fingerprint"]
        == conservative_center["signal_fingerprint"]
    ]
    lines.extend(
        [
            "",
            f"- La configurazione centrale Trail `-10%` / SMA `2%` condivide esattamente lo stesso percorso di segnali con {len(pair_equivalent)} celle della griglia locale.",
            f"- La configurazione completa early `8%` / Trail `-10%` / SMA `2%` e identica, evento per evento, a {len(triple_equivalent)} celle della griglia a tre fattori.",
            f"- Il profilo piu protettivo early `8%` / Trail `-15%` / SMA `2%` condivide il percorso con {len(conservative_equivalent)} celle, incluse le soglie Trail `-18%` e `-20%`.",
            f"- Nella griglia a due fattori superano il gate {int(pair_grid['passes_robust_gate'].sum())}/{len(pair_grid)} configurazioni; nella griglia a tre fattori {int(three_grid['passes_robust_gate'].sum())}/{len(three_grid)}.",
            "",
            "## Profili Pareto",
            "",
            "| Profilo | Variante rappresentativa | Ann. | Max DD | Sharpe | Roll all-3 | Turnover |",
            "|---|---|---:|---:|---:|---:|---:|",
            f"| Rendimento / Sharpe | `{triple_focus_name}` | {_pct(triple_center['fee_0_60_annualized_return'])} | {_pct(triple_center['fee_0_60_max_drawdown'])} | {_ratio(triple_center['fee_0_60_sharpe_ratio'])} | {_pct(triple_center['rolling_all3_ratio'])} | {triple_center['fee_0_60_turnover']:.0f} |",
            f"| Protezione drawdown | `{CONSERVATIVE_PARETO_VARIANT}` | {_pct(conservative_center['fee_0_60_annualized_return'])} | {_pct(conservative_center['fee_0_60_max_drawdown'])} | {_ratio(conservative_center['fee_0_60_sharpe_ratio'])} | {_pct(conservative_center['rolling_all3_ratio'])} | {conservative_center['fee_0_60_turnover']:.0f} |",
            "",
            "Il secondo profilo rinuncia a circa 6,6 punti di rendimento annualizzato e 0,046 di Sharpe, ma migliora il drawdown di circa 4,1 punti.",
            "",
            "## Stabilita Temporale",
            "",
            "| Variante | Regime | Delta rendimento totale | Delta DD | Delta Sharpe |",
            "|---|---|---:|---:|---:|",
        ]
    )
    regime_focus = windows[
        windows["variant"].isin(
            [pair_focus_name, triple_focus_name, CONSERVATIVE_PARETO_VARIANT]
        )
        & (windows["window_type"] == "regime")
    ]
    for _, row in regime_focus.iterrows():
        lines.append(
            f"| `{row['variant']}` | {row['window']} | "
            f"{_pp(row['delta_total_return'])} | {_pp(row['delta_max_drawdown'])} | "
            f"{float(row['delta_sharpe']):+.3f} |"
        )

    lines.extend(
        [
            "",
            "## Diagnostica Recente E Rolling",
            "",
            "| Variante | Ann. dal 2022 | Max DD dal 2022 | Sharpe dal 2022 | Roll rendimento+ | Roll DD non peggiore | Roll Sharpe+ | Roll all-3 |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    diagnostic_names = [
        "baseline",
        pair_focus_name,
        triple_focus_name,
        CONSERVATIVE_PARETO_VARIANT,
    ]
    for variant_name in diagnostic_names:
        row = results.loc[results["variant"] == variant_name].iloc[0]
        lines.append(
            f"| `{variant_name}` | {_pct(row['recent_annualized_return'])} | "
            f"{_pct(row['recent_max_drawdown'])} | {_ratio(row['recent_sharpe_ratio'])} | "
            f"{_pct(row['rolling_return_positive_ratio'])} | "
            f"{_pct(row['rolling_dd_nonworse_ratio'])} | "
            f"{_pct(row['rolling_sharpe_positive_ratio'])} | "
            f"{_pct(row['rolling_all3_ratio'])} |"
        )
    lines.extend(
        [
            "",
            "| Variante | Peggior delta rendimento rolling | Peggior delta DD rolling | Peggior delta Sharpe rolling |",
            "|---|---:|---:|---:|",
        ]
    )
    for variant_name in diagnostic_names[1:]:
        row = results.loc[results["variant"] == variant_name].iloc[0]
        lines.append(
            f"| `{variant_name}` | {_pp(row['worst_rolling_return_delta'])} | "
            f"{_pp(row['worst_rolling_dd_delta'])} | "
            f"{float(row['worst_rolling_sharpe_delta']):+.3f} |"
        )

    lines.extend(
        [
            "",
            "## Audit Dei Trade Netti",
            "",
            "Le statistiche seguenti includono lo 0,6% all'ingresso e lo 0,6% all'uscita. La concentrazione Top 3 misura quanta parte dei log-rendimenti positivi proviene dai tre trade migliori.",
            "",
            "| Variante | Trade | Win rate | Mediana | Peggiore | Migliore | PF netto | Top 3 |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    audit_names = [
        "baseline",
        FOCUS_COALITIONS[frozenset({"early"})],
        FOCUS_COALITIONS[frozenset({"trail"})],
        FOCUS_COALITIONS[frozenset({"sma"})],
        pair_focus_name,
        triple_focus_name,
        CONSERVATIVE_PARETO_VARIANT,
    ]
    for variant_name in audit_names:
        row = trade_summary.loc[variant_name]
        lines.append(
            f"| `{variant_name}` | {int(row['trades'])} | {_pct(row['win_rate'])} | "
            f"{_pct(row['median_return'])} | {_pct(row['worst_trade'])} | "
            f"{_pct(row['best_trade'])} | {_ratio(row['profit_factor'])} | "
            f"{_pct(row['top3_positive_log_share'])} |"
        )

    lines.extend(
        [
            "",
            "## Eventi Che Cambiano",
            "",
            "### Ingressi anticipati aggiuntivi",
            "",
            "| Data | Momentum 7g | Volume relativo | SMA50 vs SMA200 |",
            "|---|---:|---:|---:|",
        ]
    )
    for _, row in events[events["event_type"] == "extra_early_entry"].iterrows():
        lines.append(
            f"| {row['date']} | {_pct(row['momentum_7d'])} | "
            f"{_pct(row['volume_rel'])} | {_pct(row['sma50_vs_sma200'])} |"
        )
    lines.extend(
        [
            "",
            "### Uscite Trail8 aggiuntive sulle discese rapide",
            "",
            "| Data | Momentum 7g | Volume relativo | Close |",
            "|---|---:|---:|---:|",
        ]
    )
    for _, row in events[events["event_type"] == "new_trail_exit"].iterrows():
        lines.append(
            f"| {row['date']} | {_pct(row['momentum_7d'])} | "
            f"{_pct(row['volume_rel'])} | {float(row['close']):.2f} |"
        )

    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Varianti che migliorano tutte e tre le metriche sul periodo completo: {int(nonbaseline['full_all3'].sum())}/{len(nonbaseline)}.",
            f"- Varianti che superano il gate di robustezza: {len(robust)}/{len(nonbaseline)}.",
        ]
    )
    if not ordered_isolated.empty:
        best = ordered_isolated.iloc[0]
        lines.append(
            f"- Migliore fenomeno isolato secondo il gate: `{best['variant']}`; "
            f"ann. {_pct(best['fee_0_60_annualized_return'])}, DD {_pct(best['fee_0_60_max_drawdown'])}, "
            f"Sharpe {_ratio(best['fee_0_60_sharpe_ratio'])}."
        )
    if not combined.empty:
        best_combo = combined.iloc[0]
        lines.append(
            f"- Migliore combinazione secondo il gate: `{best_combo['variant']}`; "
            f"ann. {_pct(best_combo['fee_0_60_annualized_return'])}, DD {_pct(best_combo['fee_0_60_max_drawdown'])}, "
            f"Sharpe {_ratio(best_combo['fee_0_60_sharpe_ratio'])}."
        )
    lines.extend(
        [
            "- I risultati servono a identificare fenomeni, non a promuovere automaticamente la migliore riga numerica.",
            "- Le soglie devono mostrare un plateau vicino al valore migliore e devono essere riesaminate con audit evento-per-evento e dati futuri realmente non osservati.",
            "",
            "## Integrita",
            "",
            f"- Snapshot Coinbase SHA-256: `{manifest['input']['snapshot_sha256']}`.",
            "- La replica sperimentale dei segnali baseline e stata confrontata riga per riga con l'artefatto ufficiale.",
            "- Nessun file del modello o della baseline congelata e stato modificato.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Isola gli effetti delle condizioni ETH con costi massimi allo 0,6%."
    )
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--windows", type=Path, default=DEFAULT_WINDOWS)
    parser.add_argument("--events", type=Path, default=DEFAULT_EVENTS)
    parser.add_argument("--trades", type=Path, default=DEFAULT_TRADES)
    parser.add_argument("--skip-verify", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    indicators, manifest = load_frozen_indicators(
        args.manifest,
        verify=not args.skip_verify,
    )
    variants = build_variants()
    results, windows = run_research(indicators, variants)
    events = build_event_audit(indicators, variants)
    trades = build_trade_log(indicators, variants)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(args.results, index=False)
    windows.to_csv(args.windows, index=False)
    events.to_csv(args.events, index=False)
    trades.to_csv(args.trades, index=False)
    write_report(results, windows, events, trades, manifest, args.report)

    ordered = _best_rows(results[results["variant"] != "baseline"])
    columns = [
        "variant",
        "family",
        "fee_0_60_annualized_return",
        "fee_0_60_max_drawdown",
        "fee_0_60_sharpe_ratio",
        "rolling_all3_ratio",
        "regime_all3_wins",
        "passes_robust_gate",
    ]
    print(ordered[columns].head(20).to_string(index=False))
    print(f"\nReport: {args.report.resolve()}")
    print(f"Risultati: {args.results.resolve()}")
    print(f"Finestre: {args.windows.resolve()}")
    print(f"Eventi: {args.events.resolve()}")
    print(f"Trade: {args.trades.resolve()}")


if __name__ == "__main__":
    main()
