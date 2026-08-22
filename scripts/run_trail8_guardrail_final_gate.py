"""Gate statistico finale per il candidato prudente Trail8.

Non modifica la Baseline. Misura PBO/CSCV, Deflated Sharpe, vantaggio
incrementale, walk-forward con purge e stabilita' dei parametri vicini.
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
from scripts.run_trail8_guardrail_research import Rule, candidate_signal_frame
from scripts.run_trail8_guardrail_walkforward import (
    PRUDENT_NAME,
    TAKER_COST,
    build_streams,
    prepare_unique_paths,
    summarize_streams,
)
from scripts.run_walk_forward_research import (
    build_stitched_stream,
    cscv_pbo,
    daily_sharpe_values,
    expected_max_sharpe,
    performance_stats,
    probabilistic_sharpe,
    select_training_candidate,
    training_metrics,
)
from strategy.signals import compute_signals


FIRST_TEST_YEAR = 2020
OUT_MD = PROJECT_ROOT / "reports" / "trail8_guardrail_final_gate.md"
OUT_CHECKS = PROJECT_ROOT / "reports" / "trail8_guardrail_final_gate_checks.csv"
OUT_PBO = PROJECT_ROOT / "reports" / "trail8_guardrail_final_gate_pbo.csv"
OUT_DSR = PROJECT_ROOT / "reports" / "trail8_guardrail_final_gate_dsr.csv"
OUT_PURGED = PROJECT_ROOT / "reports" / "trail8_guardrail_final_gate_purged.csv"
OUT_PLATEAU = PROJECT_ROOT / "reports" / "trail8_guardrail_parameter_plateau.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gate finale del guardrail Trail8.")
    parser.add_argument(
        "--as-of",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Ultima candela chiusa inclusa (YYYY-MM-DD).",
    )
    parser.add_argument("--output", type=Path, default=OUT_MD)
    return parser.parse_args()


def _fingerprint(signals: pd.Series) -> str:
    payload = "\x1f".join(signals.astype(str).tolist()).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:16]


def purged_selections(
    returns: pd.DataFrame,
    exposures: pd.DataFrame,
    metadata: pd.DataFrame,
    *,
    purge_days: int,
) -> pd.DataFrame:
    conservative = [
        name
        for name in returns
        if name == "baseline" or bool(metadata.loc[name, "conservative_family"])
    ]
    policies = {
        "wf_pair_gate": ["baseline", PRUDENT_NAME],
        "wf_conservative_family": conservative,
        "wf_full_grid": list(returns.columns),
    }
    rows: list[dict[str, object]] = []
    last_date = returns.index.max()
    for test_year in range(FIRST_TEST_YEAR, last_date.year + 1):
        test_start = pd.Timestamp(test_year, 1, 1)
        if test_start > last_date:
            break
        train_end = test_start - pd.Timedelta(days=purge_days + 1)
        test_end = min(pd.Timestamp(test_year, 12, 31), last_date)
        metrics = training_metrics(returns, exposures, metadata, train_end)
        for policy, universe in policies.items():
            selected, eligible = select_training_candidate(metrics, universe)
            chosen = metrics.loc[selected]
            baseline = metrics.loc["baseline"]
            rows.append(
                {
                    "purge_days": purge_days,
                    "policy": policy,
                    "test_year": test_year,
                    "train_end": train_end.date().isoformat(),
                    "test_start": test_start.date().isoformat(),
                    "test_end": test_end.date().isoformat(),
                    "universe_paths": len(universe),
                    "eligible_paths": len(eligible) if selected != "baseline" else 0,
                    "selected_variant": selected,
                    "train_annualized_return": chosen["annualized_return"],
                    "train_max_drawdown": chosen["max_drawdown"],
                    "train_sharpe": chosen["sharpe_ratio"],
                    "baseline_train_annualized_return": baseline["annualized_return"],
                    "baseline_train_max_drawdown": baseline["max_drawdown"],
                    "baseline_train_sharpe": baseline["sharpe_ratio"],
                }
            )
    return pd.DataFrame(rows)


def parameter_plateau(
    indicators: pd.DataFrame,
    baseline_exposure: pd.Series,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    official = evaluation_frame(compute_signals(indicators))
    aligned = indicators.loc[official.index].copy()
    close = aligned["Close"]
    years = range(FIRST_TEST_YEAR, close.index.max().year + 1)
    exposure_paths: dict[str, pd.Series] = {"baseline": baseline_exposure}
    return_paths: dict[str, pd.Series] = {}
    rows: list[dict[str, object]] = []

    baseline_stream = build_stitched_stream(
        close.pct_change(),
        pd.DataFrame({"baseline": baseline_exposure}),
        {year: "baseline" for year in years},
        start=pd.Timestamp(FIRST_TEST_YEAR, 1, 1),
        end=close.index.max(),
        fee_rate=TAKER_COST,
    )
    baseline_stats = performance_stats(
        baseline_stream["DailyReturn"],
        baseline_stream["Exposure"],
        baseline_stream["Turnover"],
    )

    for width in (0.10, 0.105, 0.11, 0.115, 0.12):
        for slope in (0.0375, 0.04, 0.0425):
            for extension in (0.04, 0.05, 0.06):
                name = (
                    f"Trail{width * 100:.1f}_slope{100 * slope:.2f}_ext{100 * extension:.0f}"
                )
                rule = Rule(
                    name=name,
                    min_extension=extension,
                    widen_to=width,
                    widen_if_slope_below=slope,
                )
                frame = candidate_signal_frame(aligned, rule)
                equity, full, _ = run_backtest(
                    frame[["Close", "Segnale"]], transaction_cost_rate=TAKER_COST
                )
                exposure = equity["EffectiveExposure"].fillna(0.0)
                exposure_paths[name] = exposure
                return_paths[name] = equity["DailyReturnStrategy"].fillna(0.0)
                stream = build_stitched_stream(
                    close.pct_change(),
                    pd.DataFrame({name: exposure}),
                    {year: name for year in years},
                    start=pd.Timestamp(FIRST_TEST_YEAR, 1, 1),
                    end=close.index.max(),
                    fee_rate=TAKER_COST,
                )
                oos = performance_stats(
                    stream["DailyReturn"], stream["Exposure"], stream["Turnover"]
                )
                strict = bool(
                    oos.annualized_return > baseline_stats.annualized_return
                    and oos.max_drawdown >= baseline_stats.max_drawdown
                    and oos.sharpe_ratio > baseline_stats.sharpe_ratio
                )
                tolerant = bool(
                    oos.annualized_return >= baseline_stats.annualized_return
                    and oos.max_drawdown >= baseline_stats.max_drawdown - 0.02
                    and oos.sharpe_ratio >= baseline_stats.sharpe_ratio
                )
                rows.append(
                    {
                        "variant": name,
                        "trail_width": width,
                        "sma50_slope_threshold": slope,
                        "extension_threshold": extension,
                        "signal_fingerprint": _fingerprint(frame["Segnale"]),
                        "full_annualized_return": full.annualized_return,
                        "full_max_drawdown": full.max_drawdown,
                        "full_sharpe": full.sharpe_ratio,
                        "oos_annualized_return": oos.annualized_return,
                        "oos_max_drawdown": oos.max_drawdown,
                        "oos_sharpe": oos.sharpe_ratio,
                        "delta_oos_annualized": oos.annualized_return
                        - baseline_stats.annualized_return,
                        "delta_oos_drawdown": oos.max_drawdown
                        - baseline_stats.max_drawdown,
                        "delta_oos_sharpe": oos.sharpe_ratio
                        - baseline_stats.sharpe_ratio,
                        "strict_pass": strict,
                        "tolerant_pass": tolerant,
                    }
                )
    plateau = pd.DataFrame(rows)
    unique_returns: dict[str, pd.Series] = {"baseline": pd.Series(dtype=float)}
    seen: set[str] = set()
    for _, row in plateau.iterrows():
        fingerprint = str(row["signal_fingerprint"])
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        name = str(row["variant"])
        unique_returns[name] = return_paths[name]
    unique_returns["baseline"] = (
        baseline_exposure * close.pct_change().fillna(0.0)
        - baseline_exposure.diff().abs().fillna(baseline_exposure.abs()) * TAKER_COST
    )
    neighborhood_returns = pd.DataFrame(unique_returns, index=aligned.index).fillna(0.0)
    return plateau, neighborhood_returns


def statistical_tests(
    returns: pd.DataFrame,
    metadata: pd.DataFrame,
    neighborhood_returns: pd.DataFrame,
    primary_streams: dict[str, pd.DataFrame],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    conservative = [
        name
        for name in returns
        if name == "baseline" or bool(metadata.loc[name, "conservative_family"])
    ]
    pbo_jobs = [
        ("full_70_paths", returns),
        ("pre2020_70_paths", returns.loc[:"2019-12-31"]),
        ("full_conservative_family", returns[conservative]),
        ("full_parameter_neighborhood", neighborhood_returns),
    ]
    pbo_summaries: list[dict[str, object]] = []
    pbo_details: list[pd.DataFrame] = []
    for label, frame in pbo_jobs:
        summary, details = cscv_pbo(frame, blocks=10, label=label)
        pbo_summaries.append(summary)
        pbo_details.append(details)

    trial_sharpes = daily_sharpe_values(returns)
    benchmark_70 = expected_max_sharpe(trial_sharpes, trials=70)
    benchmark_274 = expected_max_sharpe(trial_sharpes, trials=274)
    series = {
        "full_baseline": returns["baseline"],
        "full_prudent": returns[PRUDENT_NAME],
        "oos_baseline": primary_streams["baseline"]["DailyReturn"],
        "oos_prudent": primary_streams["fixed_prudent"]["DailyReturn"],
        "oos_pair_gate": primary_streams["wf_pair_gate"]["DailyReturn"],
    }
    dsr_rows: list[dict[str, object]] = []
    for label, values in series.items():
        psr = probabilistic_sharpe(values, benchmark_daily_sharpe=0.0)
        dsr_70 = probabilistic_sharpe(values, benchmark_daily_sharpe=benchmark_70)
        dsr_274 = probabilistic_sharpe(values, benchmark_daily_sharpe=benchmark_274)
        dsr_rows.append(
            {
                "label": label,
                "observations": psr["observations"],
                "annualized_sharpe": psr["annualized_sharpe"],
                "psr_above_zero": psr["probability"],
                "dsr_probability_70_trials": dsr_70["probability"],
                "dsr_probability_274_trials": dsr_274["probability"],
                "benchmark_70_annualized": benchmark_70 * np.sqrt(365.0),
                "benchmark_274_annualized": benchmark_274 * np.sqrt(365.0),
                "skewness": psr["skewness"],
                "kurtosis": psr["kurtosis"],
            }
        )
    incremental = (
        primary_streams["wf_pair_gate"]["DailyReturn"]
        - primary_streams["baseline"]["DailyReturn"]
    )
    incremental_psr = probabilistic_sharpe(
        incremental, benchmark_daily_sharpe=0.0
    )
    dsr_rows.append(
        {
            "label": "oos_incremental_pair_minus_baseline",
            "observations": incremental_psr["observations"],
            "annualized_sharpe": incremental_psr["annualized_sharpe"],
            "psr_above_zero": incremental_psr["probability"],
            "dsr_probability_70_trials": np.nan,
            "dsr_probability_274_trials": np.nan,
            "benchmark_70_annualized": 0.0,
            "benchmark_274_annualized": 0.0,
            "skewness": incremental_psr["skewness"],
            "kurtosis": incremental_psr["kurtosis"],
        }
    )
    return (
        pd.DataFrame(pbo_summaries),
        pd.concat(pbo_details, ignore_index=True),
        pd.DataFrame(dsr_rows),
    )


def attach_purged_test_results(
    selections: pd.DataFrame,
    streams: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for _, selection in selections.iterrows():
        year = int(selection["test_year"])
        policy = str(selection["policy"])
        test = streams[policy].loc[str(year)]
        baseline = streams["baseline"].loc[str(year)]
        test_stats = performance_stats(test["DailyReturn"], test["Exposure"], test["Turnover"])
        base_stats = performance_stats(
            baseline["DailyReturn"], baseline["Exposure"], baseline["Turnover"]
        )
        item = selection.to_dict()
        item.update(
            {
                "test_total_return": test_stats.total_return,
                "test_max_drawdown": test_stats.max_drawdown,
                "test_sharpe": test_stats.sharpe_ratio,
                "test_delta_return": test_stats.total_return - base_stats.total_return,
                "test_delta_drawdown": test_stats.max_drawdown - base_stats.max_drawdown,
                "test_delta_sharpe": test_stats.sharpe_ratio - base_stats.sharpe_ratio,
            }
        )
        rows.append(item)
    return pd.DataFrame(rows)


def _all3(candidate: pd.Series, baseline: pd.Series) -> bool:
    return bool(
        candidate["annualized_return"] > baseline["annualized_return"]
        and candidate["max_drawdown"] >= baseline["max_drawdown"]
        and candidate["sharpe_ratio"] > baseline["sharpe_ratio"]
    )


def pct(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value * 100:.2f}%"


def ratio(value: float) -> str:
    return "n/a" if pd.isna(value) else f"{value:.3f}"


def write_report(
    path: Path,
    *,
    as_of: str,
    pbo: pd.DataFrame,
    dsr: pd.DataFrame,
    plateau: pd.DataFrame,
    purged_metrics: pd.DataFrame,
    checks: pd.DataFrame,
    verdict: str,
) -> None:
    lines = [
        "# Trail8 Guardrail - Gate Statistico Finale",
        "",
        f"Data test: `{date.today().isoformat()}`. Cutoff: `{as_of}`.",
        "Mercato: `ETH-USD` Coinbase, daily UTC chiuso. Commissione taker `0,16%`.",
        "La Baseline ufficiale non e' stata modificata.",
        "",
        "## Verdetto",
        "",
        f"**{verdict}**",
        "",
        "## Controlli",
        "",
        "| Controllo | Soglia | Risultato | Stato |",
        "|---|---|---|---|",
    ]
    for _, row in checks.iterrows():
        lines.append(
            f"| {row['check']} | {row['threshold']} | {row['result']} | {row['status']} |"
        )

    lines.extend(
        [
            "",
            "## PBO / CSCV",
            "",
            "PBO sotto il 50% indica che il vincitore scelto sul training finisce",
            "sotto la mediana nel test in meno della meta' delle suddivisioni.",
            "",
            "| Universo | Percorsi | Split | PBO | Rank test mediano | Sharpe train | Sharpe test |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in pbo.iterrows():
        lines.append(
            f"| {row['label']} | {int(row['paths'])} | {int(row['splits'])} | "
            f"{pct(row['pbo'])} | {pct(row['median_test_rank'])} | "
            f"{ratio(row['mean_selected_train_sharpe'])} | "
            f"{ratio(row['mean_selected_test_sharpe'])} |"
        )

    lines.extend(
        [
            "",
            "## Sharpe corretto",
            "",
            "| Serie | Sharpe | Prob. Sharpe > 0 | DSR 70 prove | DSR 274 prove | Benchmark 274 |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in dsr.iterrows():
        lines.append(
            f"| {row['label']} | {ratio(row['annualized_sharpe'])} | "
            f"{pct(row['psr_above_zero'])} | {pct(row['dsr_probability_70_trials'])} | "
            f"{pct(row['dsr_probability_274_trials'])} | "
            f"{ratio(row['benchmark_274_annualized'])} |"
        )

    strict_ratio = float(plateau["strict_pass"].mean())
    tolerant_ratio = float(plateau["tolerant_pass"].mean())
    lines.extend(
        [
            "",
            "## Stabilita parametri",
            "",
            "Griglia locale: Trail `10-12%`, slope SMA50 `3,75-4,25%`,",
            "estensione `4-6%`: 45 combinazioni.",
            "Le metriche indicate come 2020+ sono pseudo-fuori-campione: il periodo",
            "parte dal 2020, ma la famiglia di regole e' stata definita conoscendo lo storico.",
            "",
            f"- combinazioni che migliorano annualizzato, DD e Sharpe: `{pct(strict_ratio)}`;",
            f"- combinazioni accettabili con tolleranza DD di 2 punti: `{pct(tolerant_ratio)}`;",
            f"- percorsi di segnale distinti nella griglia locale: `{plateau['signal_fingerprint'].nunique()}`.",
            "",
            "| Trail | Slope | Estensione | Ann. 2020+ | DD 2020+ | Sharpe 2020+ | Delta ann. | Delta DD | Delta Sharpe | Pass |",
            "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    focus = plateau.sort_values(
        ["strict_pass", "oos_sharpe"], ascending=[False, False]
    ).head(12)
    for _, row in focus.iterrows():
        lines.append(
            f"| {pct(row['trail_width'])} | {pct(row['sma50_slope_threshold'])} | "
            f"{pct(row['extension_threshold'])} | {pct(row['oos_annualized_return'])} | "
            f"{pct(row['oos_max_drawdown'])} | {ratio(row['oos_sharpe'])} | "
            f"{pct(row['delta_oos_annualized'])} | {pct(row['delta_oos_drawdown'])} | "
            f"{ratio(row['delta_oos_sharpe'])} | "
            f"{'PASS' if row['strict_pass'] else 'FAIL'} |"
        )

    lines.extend(
        [
            "",
            "## Walk-forward con purge",
            "",
            "Gli ultimi 30 o 90 giorni prima di ogni anno di test non partecipano",
            "alla scelta dei parametri. Le candele restano disponibili durante il test",
            "per calcolare normalmente indicatori e stato della posizione.",
            "",
            "| Purge | Modello | Ann. | Max DD | Sharpe | Delta ann. | Delta DD | Delta Sharpe |",
            "|---:|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in purged_metrics.iterrows():
        lines.append(
            f"| {int(row['purge_days'])}g | {row['model']} | "
            f"{pct(row['annualized_return'])} | {pct(row['max_drawdown'])} | "
            f"{ratio(row['sharpe_ratio'])} | {pct(row['delta_annualized'])} | "
            f"{pct(row['delta_drawdown'])} | {ratio(row['delta_sharpe'])} |"
        )

    hard_failures = int(((checks["severity"] == "HARD") & (checks["status"] == "FAIL")).sum())
    warnings = int((checks["status"] == "WARN").sum())
    lines.extend(
        [
            "",
            "## Decisione",
            "",
            f"- fallimenti obbligatori: `{hard_failures}`; avvertimenti: `{warnings}`;",
            "- `PASS` autorizzerebbe la promozione; `PASS PROVVISORIO` richiede",
            "  monitoraggio e rollback; `FAIL` mantiene la Baseline;",
            "- il gate resta retrospettivo: anche una promozione autorizzata non",
            "  trasformerebbe lo storico in vero futuro mai osservato;",
            "- la Baseline resta invariata fino a decisione esplicita.",
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
    close = indicators.loc[returns.index, "Close"]

    unpurged_rows: list[pd.DataFrame] = []
    purged_selection_rows: list[pd.DataFrame] = []
    primary_streams: dict[str, pd.DataFrame] | None = None
    primary_selections: pd.DataFrame | None = None
    for purge_days in (0, 30, 90):
        selections = purged_selections(
            returns, exposures, metadata, purge_days=purge_days
        )
        streams = build_streams(
            close,
            exposures,
            selections,
            first_test_year=FIRST_TEST_YEAR,
            fee_rate=TAKER_COST,
        )
        if purge_days == 0:
            primary_streams = streams
            primary_selections = selections.copy()
        metrics = summarize_streams(streams, f"purge_{purge_days}d")
        baseline = metrics[metrics["model"] == "baseline"].iloc[0]
        metrics["purge_days"] = purge_days
        metrics["delta_annualized"] = metrics["annualized_return"] - baseline["annualized_return"]
        metrics["delta_drawdown"] = metrics["max_drawdown"] - baseline["max_drawdown"]
        metrics["delta_sharpe"] = metrics["sharpe_ratio"] - baseline["sharpe_ratio"]
        unpurged_rows.append(metrics)
        purged_selection_rows.append(attach_purged_test_results(selections, streams))
    if primary_streams is None or primary_selections is None:
        raise RuntimeError("Stream primario non costruito.")
    purged_metrics_all = pd.concat(unpurged_rows, ignore_index=True)
    purged_metrics = purged_metrics_all[
        purged_metrics_all["model"].isin(
            ["baseline", "wf_pair_gate", "wf_conservative_family", "wf_full_grid"]
        )
    ].copy()
    purged_details = pd.concat(purged_selection_rows, ignore_index=True)

    plateau, neighborhood_returns = parameter_plateau(
        indicators, exposures["baseline"]
    )
    pbo, pbo_details, dsr = statistical_tests(
        returns, metadata, neighborhood_returns, primary_streams
    )

    primary = purged_metrics_all[purged_metrics_all["purge_days"] == 0].set_index("model")
    pair = primary.loc["wf_pair_gate"]
    baseline = primary.loc["baseline"]
    dsr_oos = dsr[dsr["label"] == "oos_pair_gate"].iloc[0]
    incremental = dsr[dsr["label"] == "oos_incremental_pair_minus_baseline"].iloc[0]
    pbo_neighborhood = pbo[pbo["label"] == "full_parameter_neighborhood"].iloc[0]
    pbo_full = pbo[pbo["label"] == "full_70_paths"].iloc[0]
    pbo_family = pbo[pbo["label"] == "full_conservative_family"].iloc[0]
    strict_plateau = float(plateau["strict_pass"].mean())

    check_rows: list[dict[str, object]] = []

    def add_check(
        check: str,
        threshold: str,
        result: str,
        passed: bool,
        *,
        severity: str = "HARD",
    ) -> None:
        check_rows.append(
            {
                "check": check,
                "threshold": threshold,
                "result": result,
                "status": "PASS" if passed else ("WARN" if severity == "WARN" else "FAIL"),
                "severity": severity,
            }
        )

    add_check(
        "Metriche aggregate candidato",
        "Ann., DD e Sharpe > Baseline",
        f"{pct(pair['annualized_return'])} / {pct(pair['max_drawdown'])} / {ratio(pair['sharpe_ratio'])}",
        _all3(pair, baseline),
    )
    add_check(
        "Deflated Sharpe 274 prove",
        ">= 95%",
        pct(float(dsr_oos["dsr_probability_274_trials"])),
        float(dsr_oos["dsr_probability_274_trials"]) >= 0.95,
    )
    add_check(
        "Probabilita vantaggio incrementale",
        ">= 90%",
        pct(float(incremental["psr_above_zero"])),
        float(incremental["psr_above_zero"]) >= 0.90,
    )
    add_check(
        "PBO griglia locale",
        "< 50%",
        pct(float(pbo_neighborhood["pbo"])),
        float(pbo_neighborhood["pbo"]) < 0.50,
    )
    broad_pbo_pass = bool(
        float(pbo_full["pbo"]) < 0.50 and float(pbo_family["pbo"]) < 0.50
    )
    add_check(
        "PBO ricerca ampia",
        "Diagnostica: entrambi < 50%",
        f"70 percorsi {pct(float(pbo_full['pbo']))}; famiglia "
        f"{pct(float(pbo_family['pbo']))}",
        broad_pbo_pass,
        severity="WARN",
    )
    add_check(
        "Stabilita valori vicini",
        ">= 70% migliorano tutte le metriche",
        pct(strict_plateau),
        strict_plateau >= 0.70,
    )
    for purge_days in (30, 90):
        subset = purged_metrics_all[purged_metrics_all["purge_days"] == purge_days].set_index("model")
        add_check(
            f"Walk-forward purge {purge_days}g",
            "Ann., DD e Sharpe > Baseline",
            f"{pct(subset.loc['wf_pair_gate', 'annualized_return'])} / "
            f"{pct(subset.loc['wf_pair_gate', 'max_drawdown'])} / "
            f"{ratio(subset.loc['wf_pair_gate', 'sharpe_ratio'])}",
            _all3(subset.loc["wf_pair_gate"], subset.loc["baseline"]),
        )

    delayed_streams = build_streams(
        close,
        exposures,
        primary_selections,
        first_test_year=FIRST_TEST_YEAR,
        fee_rate=TAKER_COST,
        extra_delay_days=1,
    )
    delayed = summarize_streams(
        delayed_streams, "taker_0_16pct_delay_1d"
    ).set_index("model")
    delayed_pass = _all3(delayed.loc["wf_pair_gate"], delayed.loc["baseline"])
    add_check(
        "Ritardo aggiuntivo 1 giorno",
        "Stress informativo: preferibile PASS",
        f"Ann. {pct(delayed.loc['wf_pair_gate', 'annualized_return'])} vs "
        f"{pct(delayed.loc['baseline', 'annualized_return'])}",
        delayed_pass,
        severity="WARN",
    )
    full_grid_pass = _all3(primary.loc["wf_full_grid"], baseline)
    add_check(
        "Selettore 70 percorsi",
        "Diagnostica: preferibile PASS",
        f"Ann. {pct(primary.loc['wf_full_grid', 'annualized_return'])} vs "
        f"{pct(baseline['annualized_return'])}",
        full_grid_pass,
        severity="WARN",
    )

    checks = pd.DataFrame(check_rows)
    hard_failures = int(
        ((checks["severity"] == "HARD") & (checks["status"] == "FAIL")).sum()
    )
    warnings = int((checks["status"] == "WARN").sum())
    verdict = "FAIL" if hard_failures else ("PASS PROVVISORIO" if warnings else "PASS")

    OUT_CHECKS.parent.mkdir(parents=True, exist_ok=True)
    checks.to_csv(OUT_CHECKS, index=False)
    pbo.to_csv(OUT_PBO, index=False)
    pbo_details.to_csv(
        PROJECT_ROOT / "reports" / "trail8_guardrail_final_gate_pbo_details.csv",
        index=False,
    )
    dsr.to_csv(OUT_DSR, index=False)
    purged_metrics.to_csv(OUT_PURGED, index=False)
    purged_details.to_csv(
        PROJECT_ROOT / "reports" / "trail8_guardrail_final_gate_purged_yearly.csv",
        index=False,
    )
    plateau.to_csv(OUT_PLATEAU, index=False)
    write_report(
        args.output,
        as_of=args.as_of,
        pbo=pbo,
        dsr=dsr,
        plateau=plateau,
        purged_metrics=purged_metrics,
        checks=checks,
        verdict=verdict,
    )
    print(f"Saved {args.output}")
    print(f"Raw rules: {raw_rules}; unique paths: {len(returns.columns)}")
    print(checks.to_string(index=False))
    print(f"VERDICT: {verdict}")


if __name__ == "__main__":
    main()
