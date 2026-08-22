"""Validazione nested walk-forward dei guardrail sperimentali Trail8.

La Baseline ufficiale resta in sola lettura. Ogni anno di test usa una regola
selezionata esclusivamente sui dati disponibili fino al 31 dicembre precedente.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import date, timedelta
import hashlib
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import run_backtest
from data.coinbase import fetch_daily_candles
from indicators.technical_indicators import compute_all_indicators
from pipeline import evaluation_frame
from scripts.run_trail8_guardrail_research import (
    Rule,
    candidate_signal_frame,
    rules_to_test,
)
from scripts.run_walk_forward_research import (
    build_stitched_stream,
    performance_stats,
    select_training_candidate,
    training_metrics,
)
from strategy.signals import compute_signals


FIRST_TEST_YEAR = 2020
TAKER_COST = 0.0016
PRUDENT_NAME = "Combo Trail11 slope<=4.00% ext>=5%"
AGGRESSIVE_NAME = "Combo Trail11 slope<=4% ext>=5% momentum>=-10%"

OUT_MD = PROJECT_ROOT / "reports" / "trail8_guardrail_walkforward.md"
OUT_SELECTIONS = PROJECT_ROOT / "reports" / "trail8_guardrail_walkforward_selections.csv"
OUT_METRICS = PROJECT_ROOT / "reports" / "trail8_guardrail_walkforward_metrics.csv"
OUT_YEARLY = PROJECT_ROOT / "reports" / "trail8_guardrail_walkforward_yearly.csv"
OUT_BOOTSTRAP = PROJECT_ROOT / "reports" / "trail8_guardrail_walkforward_bootstrap.csv"
OUT_EQUITY = PROJECT_ROOT / "reports" / "trail8_guardrail_walkforward_equity.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Nested walk-forward dei guardrail Trail8.")
    parser.add_argument(
        "--as-of",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Ultima candela chiusa inclusa (YYYY-MM-DD).",
    )
    parser.add_argument("--first-test-year", type=int, default=FIRST_TEST_YEAR)
    parser.add_argument("--output", type=Path, default=OUT_MD)
    return parser.parse_args()


def _fingerprint(signals: pd.Series) -> str:
    payload = "\x1f".join(signals.astype(str).tolist()).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def _rule_complexity(rule: Rule) -> int:
    base = Rule("base")
    ignored = {"name"}
    return sum(
        getattr(rule, key) != getattr(base, key)
        for key in asdict(rule)
        if key not in ignored
    )


def _family(rule: Rule) -> str:
    name = rule.name
    if name == "Trail8 ufficiale":
        return "baseline"
    if name == "Senza trailing":
        return "no_trailing"
    if name.startswith("Combo"):
        return "combo"
    if name.startswith("Momentum"):
        return "momentum"
    if name.startswith("Volume"):
        return "volume"
    if "estensione" in name:
        return "extension"
    if "slope" in name and rule.widen_to is not None:
        return "dynamic_slope"
    if "ATR" in name and rule.widen_to is not None:
        return "dynamic_atr"
    if name.startswith("Trail") and rule.widen_to is None:
        return "fixed_width"
    return "other_guardrail"


def _conservative_family(rule: Rule) -> bool:
    return bool(
        rule.momentum_min == Rule("base").momentum_min
        and rule.volume_min == Rule("base").volume_min
        and rule.min_atr_pct is None
        and rule.min_sma_gap is None
        and rule.min_slope5 is None
        and (rule.min_extension is None or rule.min_extension in {0.03, 0.05, 0.08})
        and (rule.widen_to is None or rule.widen_to in {0.11, 0.12, 0.13})
        and (rule.widen_if_atr_below is None)
    )


def prepare_unique_paths(
    indicators: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, int]:
    official = evaluation_frame(compute_signals(indicators))
    aligned = indicators.loc[official.index].copy()
    preferred = {"baseline": 0, PRUDENT_NAME: 1, AGGRESSIVE_NAME: 2}
    representatives: dict[str, dict[str, object]] = {}
    raw_rules = rules_to_test()

    for position, source_rule in enumerate(raw_rules):
        name = "baseline" if source_rule.name == "Trail8 ufficiale" else source_rule.name
        rule = Rule(**{**asdict(source_rule), "name": name})
        frame = candidate_signal_frame(aligned, rule)
        fingerprint = _fingerprint(frame["Segnale"])
        rank = (preferred.get(name, len(preferred)), _rule_complexity(rule), position)
        current = representatives.get(fingerprint)
        if current is None:
            representatives[fingerprint] = {
                "name": name,
                "rule": rule,
                "frame": frame,
                "rank": rank,
                "equivalent_names": [name],
            }
        else:
            current["equivalent_names"].append(name)
            if rank < current["rank"]:
                current.update({"name": name, "rule": rule, "frame": frame, "rank": rank})

    names = {str(item["name"]) for item in representatives.values()}
    required = {"baseline", PRUDENT_NAME, AGGRESSIVE_NAME}
    if missing := required - names:
        raise ValueError(f"Percorsi focus non rappresentati: {sorted(missing)}")

    baseline_frame = next(
        item["frame"] for item in representatives.values() if item["name"] == "baseline"
    )
    if not baseline_frame["Segnale"].astype(str).equals(official["Segnale"].astype(str)):
        raise ValueError("La replica sperimentale diverge dalla Baseline ufficiale.")

    returns: dict[str, pd.Series] = {}
    exposures: dict[str, pd.Series] = {}
    metadata_rows: list[dict[str, object]] = []
    for fingerprint, item in representatives.items():
        name = str(item["name"])
        rule = item["rule"]
        frame = item["frame"]
        equity, _, _ = run_backtest(
            frame[["Close", "Segnale"]], transaction_cost_rate=TAKER_COST
        )
        returns[name] = equity["DailyReturnStrategy"].fillna(0.0)
        exposures[name] = equity["EffectiveExposure"].fillna(0.0)
        metadata_rows.append(
            {
                "variant": name,
                "family": _family(rule),
                "complexity": _rule_complexity(rule),
                "exit_only": True,
                "conservative_family": _conservative_family(rule),
                "fingerprint": fingerprint,
                "equivalent_paths": len(item["equivalent_names"]),
                "equivalent_names": "|".join(sorted(item["equivalent_names"])),
            }
        )
    metadata = pd.DataFrame(metadata_rows).set_index("variant")
    return (
        pd.DataFrame(returns, index=official.index),
        pd.DataFrame(exposures, index=official.index),
        metadata,
        len(raw_rules),
    )


def walk_forward_selections(
    returns: pd.DataFrame,
    exposures: pd.DataFrame,
    metadata: pd.DataFrame,
    *,
    first_test_year: int,
) -> pd.DataFrame:
    conservative = [
        name for name in returns if name == "baseline" or bool(metadata.loc[name, "conservative_family"])
    ]
    policies = {
        "wf_pair_gate": ["baseline", PRUDENT_NAME],
        "wf_conservative_family": conservative,
        "wf_full_grid": list(returns.columns),
    }
    rows: list[dict[str, object]] = []
    last_date = returns.index.max()
    for test_year in range(first_test_year, last_date.year + 1):
        test_start = pd.Timestamp(test_year, 1, 1)
        if test_start > last_date:
            break
        train_end = test_start - pd.Timedelta(days=1)
        test_end = min(pd.Timestamp(test_year, 12, 31), last_date)
        metrics = training_metrics(returns, exposures, metadata, train_end)
        for policy, universe in policies.items():
            selected, eligible = select_training_candidate(metrics, universe)
            chosen = metrics.loc[selected]
            baseline = metrics.loc["baseline"]
            rows.append(
                {
                    "policy": policy,
                    "test_year": test_year,
                    "train_start": returns.index.min().date().isoformat(),
                    "train_end": train_end.date().isoformat(),
                    "test_start": test_start.date().isoformat(),
                    "test_end": test_end.date().isoformat(),
                    "universe_paths": len(universe),
                    "eligible_paths": len(eligible) if selected != "baseline" else 0,
                    "selected_variant": selected,
                    "selected_family": metadata.loc[selected, "family"],
                    "selected_complexity": int(metadata.loc[selected, "complexity"]),
                    "train_annualized_return": chosen["annualized_return"],
                    "train_max_drawdown": chosen["max_drawdown"],
                    "train_sharpe": chosen["sharpe_ratio"],
                    "train_trades": int(chosen["completed_trades"]),
                    "baseline_train_annualized_return": baseline["annualized_return"],
                    "baseline_train_max_drawdown": baseline["max_drawdown"],
                    "baseline_train_sharpe": baseline["sharpe_ratio"],
                }
            )
    return pd.DataFrame(rows)


def _selection_map(selections: pd.DataFrame, policy: str) -> dict[int, str]:
    subset = selections[selections["policy"] == policy]
    return {
        int(row["test_year"]): str(row["selected_variant"])
        for _, row in subset.iterrows()
    }


def build_streams(
    close: pd.Series,
    exposures: pd.DataFrame,
    selections: pd.DataFrame,
    *,
    first_test_year: int,
    fee_rate: float,
    extra_delay_days: int = 0,
) -> dict[str, pd.DataFrame]:
    start = pd.Timestamp(first_test_year, 1, 1)
    end = close.index.max()
    years = range(first_test_year, end.year + 1)
    eth_returns = close.pct_change()
    maps = {
        "baseline": {year: "baseline" for year in years},
        "fixed_prudent": {year: PRUDENT_NAME for year in years},
        "fixed_aggressive": {year: AGGRESSIVE_NAME for year in years},
        "wf_pair_gate": _selection_map(selections, "wf_pair_gate"),
        "wf_conservative_family": _selection_map(selections, "wf_conservative_family"),
        "wf_full_grid": _selection_map(selections, "wf_full_grid"),
    }
    return {
        name: build_stitched_stream(
            eth_returns,
            exposures,
            selection,
            start=start,
            end=end,
            fee_rate=fee_rate,
            extra_delay_days=extra_delay_days,
        )
        for name, selection in maps.items()
    }


def summarize_streams(
    streams: dict[str, pd.DataFrame], scenario: str
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for name, stream in streams.items():
        stats = performance_stats(stream["DailyReturn"], stream["Exposure"], stream["Turnover"])
        rows.append({"scenario": scenario, "model": name, **asdict(stats)})
    return pd.DataFrame(rows)


def yearly_metrics(streams: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for name, stream in streams.items():
        for year, subset in stream.groupby(stream.index.year):
            stats = performance_stats(
                subset["DailyReturn"], subset["Exposure"], subset["Turnover"]
            )
            rows.append({"model": name, "year": int(year), **asdict(stats)})
    out = pd.DataFrame(rows)
    baseline = out[out["model"] == "baseline"].set_index("year")
    out["delta_return"] = out.apply(
        lambda row: row["total_return"] - float(baseline.loc[int(row["year"]), "total_return"]),
        axis=1,
    )
    out["delta_drawdown"] = out.apply(
        lambda row: row["max_drawdown"] - float(baseline.loc[int(row["year"]), "max_drawdown"]),
        axis=1,
    )
    out["delta_sharpe"] = out.apply(
        lambda row: row["sharpe_ratio"] - float(baseline.loc[int(row["year"]), "sharpe_ratio"]),
        axis=1,
    )
    out["status"] = out.apply(_status, axis=1)
    return out


def _status(row: pd.Series, tolerance: float = 1e-12) -> str:
    if row["model"] == "baseline":
        return "BASELINE"
    delta_return = float(row["delta_return"])
    delta_drawdown = float(row["delta_drawdown"])
    delta_sharpe = (
        float(row["delta_sharpe"])
        if pd.notna(row["delta_sharpe"])
        else float("nan")
    )
    neutral_sharpe = pd.isna(delta_sharpe) or abs(delta_sharpe) <= tolerance
    if (
        abs(delta_return) <= tolerance
        and abs(delta_drawdown) <= tolerance
        and neutral_sharpe
    ):
        return "INVARIATO"
    if delta_return > 0.0 and delta_drawdown >= 0.0 and pd.notna(delta_sharpe) and delta_sharpe > 0.0:
        return "MIGLIORA"
    if delta_return < 0.0 and delta_drawdown < 0.0 and pd.notna(delta_sharpe) and delta_sharpe < 0.0:
        return "PEGGIORA"
    return "MISTO"


def attach_test_results(selections: pd.DataFrame, yearly: pd.DataFrame) -> pd.DataFrame:
    out = selections.copy()
    indexed = yearly.set_index(["model", "year"])
    for field in (
        "total_return",
        "max_drawdown",
        "sharpe_ratio",
        "delta_return",
        "delta_drawdown",
        "delta_sharpe",
        "status",
    ):
        out[f"test_{field}"] = out.apply(
            lambda row: indexed.loc[(str(row["policy"]), int(row["test_year"])), field],
            axis=1,
        )
    return out


def circular_block_bootstrap(
    streams: dict[str, pd.DataFrame],
    *,
    block_days: int,
    samples: int = 2000,
    seed: int = 20260822,
) -> pd.DataFrame:
    baseline = streams["baseline"]["DailyReturn"].to_numpy(dtype=float)
    n = len(baseline)
    blocks = int(np.ceil(n / block_days))
    rng = np.random.default_rng(seed + block_days)
    rows: list[dict[str, object]] = []
    for name, stream in streams.items():
        if name == "baseline":
            continue
        candidate = stream["DailyReturn"].to_numpy(dtype=float)
        observed = float(np.prod(1.0 + candidate) / np.prod(1.0 + baseline) - 1.0)
        advantages = np.empty(samples, dtype=float)
        for sample in range(samples):
            starts = rng.integers(0, n, size=blocks)
            positions = np.concatenate(
                [(start + np.arange(block_days)) % n for start in starts]
            )[:n]
            log_advantage = float(
                np.log1p(candidate[positions]).sum() - np.log1p(baseline[positions]).sum()
            )
            advantages[sample] = np.expm1(log_advantage)
        rows.append(
            {
                "model": name,
                "block_days": block_days,
                "samples": samples,
                "observed_wealth_advantage": observed,
                "probability_outperform": float((advantages > 0.0).mean()),
                "median_wealth_advantage": float(np.median(advantages)),
                "p05_wealth_advantage": float(np.quantile(advantages, 0.05)),
                "p95_wealth_advantage": float(np.quantile(advantages, 0.95)),
            }
        )
    return pd.DataFrame(rows)


def pct(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value * 100:.2f}%"


def ratio(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value:.3f}"


def write_report(
    path: Path,
    *,
    as_of: str,
    raw_rules: int,
    unique_paths: int,
    metrics: pd.DataFrame,
    yearly: pd.DataFrame,
    selections: pd.DataFrame,
    bootstrap: pd.DataFrame,
) -> None:
    primary = metrics[metrics["scenario"] == "taker_0_16pct"].set_index("model")
    baseline = primary.loc["baseline"]
    labels = {
        "baseline": "Baseline",
        "fixed_prudent": "Candidato prudente fisso",
        "fixed_aggressive": "Candidato tutte-6 fisso",
        "wf_pair_gate": "WF Baseline/candidato",
        "wf_conservative_family": "WF famiglia prudente",
        "wf_full_grid": "WF griglia completa",
    }
    lines = [
        "# Trail8 Guardrail - Nested Walk-Forward",
        "",
        f"Data test: `{date.today().isoformat()}`. Cutoff: `{as_of}`.",
        "Mercato: `ETH-USD` Coinbase, daily UTC chiuso.",
        "La Baseline ufficiale non e' stata modificata.",
        "",
        "## Metodo",
        "",
        "- primo anno fuori campione: `2020`;",
        "- per ogni anno, training expanding fino al 31 dicembre precedente;",
        "- un candidato e' eleggibile solo se nel training supera la Baseline in",
        "  annualizzato, max drawdown e Sharpe, completa almeno 5 trade e non",
        "  aggiunge piu di 12 lati di turnover;",
        "- fra gli eleggibili viene scelto il rango medio migliore delle tre metriche;",
        "- al cambio anno l'esposizione viene riallineata e il turnover viene addebitato;",
        f"- regole generate: `{raw_rules}`; percorsi di segnale unici: `{unique_paths}`.",
        "",
        "`fixed_prudent` e `fixed_aggressive` sono replay temporali, non veri risultati",
        "fuori campione, perche le regole sono state formulate dopo avere visto tutta",
        "la storia. I tre selettori `WF` sono la prova pseudo out-of-sample principale.",
        "",
        "## Risultato aggregato 2020-oggi",
        "",
        "Commissione taker `0,16%` per lato.",
        "",
        "| Modello | Totale | Ann. | Max DD | Sharpe | Trade | Turnover | Delta ann. | Delta DD | Delta Sharpe |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name, row in primary.iterrows():
        lines.append(
            f"| {labels[name]} | {pct(row['total_return'])} | {pct(row['annualized_return'])} | "
            f"{pct(row['max_drawdown'])} | {ratio(row['sharpe_ratio'])} | "
            f"{int(row['completed_trades'])} | {row['turnover']:.1f} | "
            f"{pct(row['annualized_return'] - baseline['annualized_return'])} | "
            f"{pct(row['max_drawdown'] - baseline['max_drawdown'])} | "
            f"{ratio(row['sharpe_ratio'] - baseline['sharpe_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Selezioni annuali",
            "",
            "Tutte le metriche `train` precedono integralmente l'anno di test.",
            "",
            "| Policy | Test | Universo | Eleggibili | Scelto | Ann. train | DD train | Sharpe train | Delta return test | Delta DD test | Delta Sharpe test | Esito |",
            "|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for _, row in selections.sort_values(["test_year", "policy"]).iterrows():
        lines.append(
            f"| {row['policy']} | {int(row['test_year'])} | {int(row['universe_paths'])} | "
            f"{int(row['eligible_paths'])} | `{row['selected_variant']}` | "
            f"{pct(row['train_annualized_return'])} | {pct(row['train_max_drawdown'])} | "
            f"{ratio(row['train_sharpe'])} | {pct(row['test_delta_return'])} | "
            f"{pct(row['test_delta_drawdown'])} | {ratio(row['test_delta_sharpe'])} | "
            f"{row['test_status']} |"
        )

    lines.extend(
        [
            "",
            "## Esiti annuali",
            "",
            "| Modello | Migliora | Invariato | Misto | Peggiora | Anni return migliori | Anni DD migliori | Anni Sharpe migliori |",
            "|---|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for name in labels:
        if name == "baseline":
            continue
        subset = yearly[yearly["model"] == name]
        counts = subset["status"].value_counts()
        lines.append(
            f"| {labels[name]} | {int(counts.get('MIGLIORA', 0))} | "
            f"{int(counts.get('INVARIATO', 0))} | {int(counts.get('MISTO', 0))} | "
            f"{int(counts.get('PEGGIORA', 0))} | {int((subset['delta_return'] > 0).sum())} | "
            f"{int((subset['delta_drawdown'] > 0).sum())} | "
            f"{int((subset['delta_sharpe'] > 0).sum())} |"
        )

    lines.extend(
        [
            "",
            "## Stress esecuzione e sensibilita temporale",
            "",
            "Le selezioni annuali restano congelate; cambiano soltanto costi, ritardo",
            "oppure l'anno iniziale della curva aggregata.",
            "",
            "| Scenario | Modello | Ann. | Max DD | Sharpe |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for _, row in metrics.iterrows():
        if row["model"] not in {"baseline", "fixed_prudent", "wf_pair_gate", "wf_conservative_family", "wf_full_grid"}:
            continue
        lines.append(
            f"| {row['scenario']} | {labels[row['model']]} | "
            f"{pct(row['annualized_return'])} | {pct(row['max_drawdown'])} | "
            f"{ratio(row['sharpe_ratio'])} |"
        )

    lines.extend(
        [
            "",
            "## Bootstrap a blocchi",
            "",
            "Bootstrap circolare appaiato sui rendimenti giornalieri fuori campione.",
            "Il vantaggio misura il rapporto tra ricchezza finale del modello e Baseline.",
            "",
            "| Modello | Blocco | Prob. sovraperformance | Vantaggio osservato | Mediana | 5% | 95% |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in bootstrap.iterrows():
        lines.append(
            f"| {labels[row['model']]} | {int(row['block_days'])}g | "
            f"{pct(row['probability_outperform'])} | "
            f"{pct(row['observed_wealth_advantage'])} | "
            f"{pct(row['median_wealth_advantage'])} | "
            f"{pct(row['p05_wealth_advantage'])} | {pct(row['p95_wealth_advantage'])} |"
        )

    selector_names = ["wf_pair_gate", "wf_conservative_family", "wf_full_grid"]
    best_name = max(selector_names, key=lambda name: float(primary.loc[name, "sharpe_ratio"]))
    best = primary.loc[best_name]
    all3 = bool(
        best["annualized_return"] > baseline["annualized_return"]
        and best["max_drawdown"] >= baseline["max_drawdown"]
        and best["sharpe_ratio"] > baseline["sharpe_ratio"]
    )
    best_boot = bootstrap[(bootstrap["model"] == best_name) & (bootstrap["block_days"] == 30)].iloc[0]
    delayed = metrics[metrics["scenario"] == "taker_0_16pct_delay_1d"].set_index("model")
    start_2021 = metrics[metrics["scenario"] == "taker_0_16pct_start_2021"].set_index("model")
    start_2023 = metrics[metrics["scenario"] == "taker_0_16pct_start_2023"].set_index("model")
    pair_always_selected = bool(
        (selections[selections["policy"] == "wf_pair_gate"]["selected_variant"] == PRUDENT_NAME).all()
    )
    lines.extend(
        [
            "",
            "## Conclusione",
            "",
            f"- Miglior selettore per Sharpe pseudo out-of-sample: `{best_name}`.",
            f"- Metriche: ann. `{pct(best['annualized_return'])}`, max DD `{pct(best['max_drawdown'])}`, Sharpe `{ratio(best['sharpe_ratio'])}`.",
            f"- Rispetto alla Baseline {'migliora simultaneamente annualizzato, drawdown e Sharpe' if all3 else 'non migliora simultaneamente tutte e tre le metriche'}.",
            f"- Bootstrap 30 giorni: probabilita di sovraperformance `{pct(best_boot['probability_outperform'])}`.",
            f"- Il gate a due modelli ha selezionato il candidato prudente in tutti gli anni: `{'si' if pair_always_selected else 'no'}`.",
            f"- Partendo dal 2021 il candidato/gate rende ann. `{pct(start_2021.loc['wf_pair_gate', 'annualized_return'])}` contro `{pct(start_2021.loc['baseline', 'annualized_return'])}`; dal 2023 `{pct(start_2023.loc['wf_pair_gate', 'annualized_return'])}` contro `{pct(start_2023.loc['baseline', 'annualized_return'])}`.",
            f"- Con una candela ulteriore di ritardo il candidato scende a ann. `{pct(delayed.loc['wf_pair_gate', 'annualized_return'])}`, DD `{pct(delayed.loc['wf_pair_gate', 'max_drawdown'])}` e Sharpe `{ratio(delayed.loc['wf_pair_gate', 'sharpe_ratio'])}`, contro Baseline `{pct(delayed.loc['baseline', 'annualized_return'])}`, `{pct(delayed.loc['baseline', 'max_drawdown'])}`, `{ratio(delayed.loc['baseline', 'sharpe_ratio'])}`: il vantaggio non sopravvive.",
            f"- La selezione su tutta la griglia fallisce: ann. `{pct(primary.loc['wf_full_grid', 'annualized_return'])}`, DD `{pct(primary.loc['wf_full_grid', 'max_drawdown'])}`, Sharpe `{ratio(primary.loc['wf_full_grid', 'sharpe_ratio'])}`.",
            "- Anche il gate a due modelli resta pseudo out-of-sample: la regola candidata e l'universo sono stati formulati dopo avere osservato l'intera storia.",
            "- Decisione: candidato promettente ma non promosso. Va congelato ora e osservato in paper/shadow mode su candele future realmente mai viste.",
            "- La Baseline resta invariata.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main() -> None:
    args = parse_args()
    with TemporaryDirectory() as temp_dir:
        candles = fetch_daily_candles(
            as_of=args.as_of,
            refresh_all=True,
            cache_path=Path(temp_dir) / "ETH-USD.csv",
        )
    indicators = compute_all_indicators(candles)
    returns, exposures, metadata, raw_rules = prepare_unique_paths(indicators)
    selections = walk_forward_selections(
        returns,
        exposures,
        metadata,
        first_test_year=args.first_test_year,
    )
    close = indicators.loc[returns.index, "Close"]
    primary_streams = build_streams(
        close,
        exposures,
        selections,
        first_test_year=args.first_test_year,
        fee_rate=TAKER_COST,
    )
    scenario_rows = [summarize_streams(primary_streams, "taker_0_16pct")]
    for scenario, fee, delay in (
        ("maker_0_07pct", 0.0007, 0),
        ("prudenziale_0_60pct", 0.006, 0),
        ("taker_0_16pct_delay_1d", TAKER_COST, 1),
    ):
        streams = build_streams(
            close,
            exposures,
            selections,
            first_test_year=args.first_test_year,
            fee_rate=fee,
            extra_delay_days=delay,
        )
        scenario_rows.append(summarize_streams(streams, scenario))
    for start_year in (2021, 2023):
        streams = build_streams(
            close,
            exposures,
            selections,
            first_test_year=start_year,
            fee_rate=TAKER_COST,
        )
        scenario_rows.append(
            summarize_streams(streams, f"taker_0_16pct_start_{start_year}")
        )
    metrics = pd.concat(scenario_rows, ignore_index=True)
    yearly = yearly_metrics(primary_streams)
    selections = attach_test_results(selections, yearly)
    bootstrap = pd.concat(
        [
            circular_block_bootstrap(primary_streams, block_days=30),
            circular_block_bootstrap(primary_streams, block_days=90),
        ],
        ignore_index=True,
    )

    OUT_SELECTIONS.parent.mkdir(parents=True, exist_ok=True)
    selections.to_csv(OUT_SELECTIONS, index=False)
    metrics.to_csv(OUT_METRICS, index=False)
    yearly.to_csv(OUT_YEARLY, index=False)
    bootstrap.to_csv(OUT_BOOTSTRAP, index=False)
    pd.DataFrame(
        {
            f"{name}_equity": stream["Equity"]
            for name, stream in primary_streams.items()
        }
    ).to_csv(OUT_EQUITY, index_label="Date")
    write_report(
        args.output,
        as_of=args.as_of,
        raw_rules=raw_rules,
        unique_paths=len(returns.columns),
        metrics=metrics,
        yearly=yearly,
        selections=selections,
        bootstrap=bootstrap,
    )
    print(f"Saved {args.output}")
    print(metrics[metrics["scenario"] == "taker_0_16pct"].to_string(index=False))
    print(selections[["policy", "test_year", "selected_variant", "test_status"]].to_string(index=False))


if __name__ == "__main__":
    main()
