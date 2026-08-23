"""Replay temporale cieco del guardrail breakout di gennaio 2026.

Le configurazioni vengono classificate usando solo dati fino al 2026-01-05.
Il blocco 2026 viene aperto soltanto dopo aver congelato la graduatoria.
La Baseline ufficiale non viene modificata.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, timedelta
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
from scripts.run_august_2026_breakout_entry_research import _return_stats
from scripts.run_breakout_event_robustness_audit import add_context_features
from scripts.run_breakout_rsi_confirmation_research import (
    CURRENT,
    RSI40_LEGACY,
    add_confirmation_features,
    build_rules,
)
from scripts.run_january_2026_entry_guardrail_research import (
    AUGUST_EVENT,
    BASE_RULE_NAMES,
    PRE_JAN_END,
    Guardrail,
    build_guardrails,
    evaluate_grid,
    primary_guardrail,
)


OUT_MD = PROJECT_ROOT / "reports" / "january_2026_guardrail_blind_validation.md"
OUT_SELECTION = (
    PROJECT_ROOT / "reports" / "january_2026_guardrail_blind_selection.csv"
)
OUT_HOLDOUT = (
    PROJECT_ROOT / "reports" / "january_2026_guardrail_blind_holdout.csv"
)
OUT_PERIODS = (
    PROJECT_ROOT / "reports" / "january_2026_guardrail_blind_periods.csv"
)
OUT_TRADES = (
    PROJECT_ROOT / "reports" / "january_2026_guardrail_blind_trades.csv"
)


@dataclass(frozen=True)
class Period:
    name: str
    start: str
    end: str


PERIODS = (
    Period("2016-2019", "2016-01-01", "2019-12-31"),
    Period("2020-2022", "2020-01-01", "2022-12-31"),
    Period("2023-2025", "2023-01-01", "2025-12-31"),
    Period("holdout_2026", "2026-01-01", "2026-08-22"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Replay cieco pre-2026 del guardrail breakout."
    )
    parser.add_argument(
        "--as-of",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Ultima candela daily chiusa inclusa (YYYY-MM-DD).",
    )
    parser.add_argument("--output", type=Path, default=OUT_MD)
    return parser.parse_args()


def _missed_count(value: object) -> int:
    if pd.isna(value) or not str(value).strip():
        return 0
    return len(str(value).split(","))


def _complexity(family: str) -> int:
    if family in {"slope", "gap", "return90"}:
        return 1
    if family in {"slope_gap", "slope_return90", "gap_return90"}:
        return 2
    if family == "risk2of3":
        return 3
    return 0


def blind_selection(grid: pd.DataFrame) -> pd.DataFrame:
    reference = (
        grid[grid["guardrail"] == "none"]
        .set_index("base_variant")
        .to_dict(orient="index")
    )
    work = grid[grid["guardrail"] != "none"].copy()
    work["delta_annualized"] = work.apply(
        lambda row: row["full_annualized_return"]
        - reference[row["base_variant"]]["full_annualized_return"],
        axis=1,
    )
    work["delta_drawdown"] = work.apply(
        lambda row: row["full_max_drawdown"]
        - reference[row["base_variant"]]["full_max_drawdown"],
        axis=1,
    )
    work["delta_sharpe"] = work.apply(
        lambda row: row["full_sharpe_ratio"]
        - reference[row["base_variant"]]["full_sharpe_ratio"],
        axis=1,
    )

    rows: list[dict[str, object]] = []
    for guardrail, selected in work.groupby("guardrail", sort=False):
        first = selected.iloc[0]
        rows.append(
            {
                "guardrail": guardrail,
                "label": first["guardrail_label"],
                "family": first["family"],
                "complexity": _complexity(str(first["family"])),
                "breakout_losses": int(selected["breakout_losses"].sum()),
                "breakout_entries": int(selected["breakout_entries"].sum()),
                "max_missed_profitable_episodes": int(
                    selected["missed_profitable_episodes"].map(_missed_count).max()
                ),
                "min_delta_annualized": float(selected["delta_annualized"].min()),
                "min_delta_drawdown": float(selected["delta_drawdown"].min()),
                "min_delta_sharpe": float(selected["delta_sharpe"].min()),
                "mean_delta_annualized": float(selected["delta_annualized"].mean()),
                "mean_delta_sharpe": float(selected["delta_sharpe"].mean()),
                "changed_systems": int((~selected["signals_equal_pre_jan"]).sum()),
            }
        )
    result = pd.DataFrame(rows)
    tolerance = 1e-12
    result["admissible_pre2026"] = (
        (result["max_missed_profitable_episodes"] == 0)
        & (result["min_delta_annualized"] >= -tolerance)
        & (result["min_delta_drawdown"] >= -tolerance)
        & (result["min_delta_sharpe"] >= -tolerance)
    )
    result = result.sort_values(
        [
            "admissible_pre2026",
            "breakout_losses",
            "mean_delta_annualized",
            "mean_delta_sharpe",
            "complexity",
            "guardrail",
        ],
        ascending=[False, True, False, False, True, True],
    ).reset_index(drop=True)
    result.insert(0, "blind_rank", np.arange(1, len(result) + 1))
    return result


def top_equivalence_class(selection: pd.DataFrame) -> pd.DataFrame:
    best = selection.iloc[0]
    mask = (
        selection["admissible_pre2026"]
        & (selection["breakout_losses"] == best["breakout_losses"])
        & (
            selection["max_missed_profitable_episodes"]
            == best["max_missed_profitable_episodes"]
        )
        & np.isclose(
            selection["min_delta_annualized"], best["min_delta_annualized"]
        )
        & np.isclose(
            selection["min_delta_drawdown"], best["min_delta_drawdown"]
        )
        & np.isclose(selection["min_delta_sharpe"], best["min_delta_sharpe"])
        & np.isclose(
            selection["mean_delta_annualized"], best["mean_delta_annualized"]
        )
        & np.isclose(selection["mean_delta_sharpe"], best["mean_delta_sharpe"])
        & (selection["complexity"] == best["complexity"])
    )
    return selection[mask].copy()


def period_comparison(
    frames: dict[tuple[str, str], pd.DataFrame],
    guardrails: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for base_name in BASE_RULE_NAMES:
        for guardrail in guardrails:
            frame = frames[(base_name, guardrail)]
            equity, _, _ = run_backtest(frame[["Close", "Segnale"]], transaction_cost_rate=0.0016)
            for period in PERIODS:
                returns = equity.loc[period.start : period.end, "DailyReturnStrategy"]
                stats = _return_stats(returns)
                buy_signals = int(
                    frame.loc[period.start : period.end, "Segnale"].eq("ACQUISTA").sum()
                )
                rows.append(
                    {
                        "period": period.name,
                        "base_variant": base_name,
                        "guardrail": guardrail,
                        "buy_signals": buy_signals,
                        **stats,
                    }
                )
    return pd.DataFrame(rows)


def _pct(value: object) -> str:
    return "-" if pd.isna(value) else f"{float(value):.2%}"


def _num(value: object) -> str:
    return "-" if pd.isna(value) else f"{float(value):.3f}"


def _day(value: object) -> str:
    return "-" if pd.isna(value) else pd.Timestamp(value).date().isoformat()


def write_report(
    path: Path,
    *,
    as_of: str,
    selection: pd.DataFrame,
    holdout: pd.DataFrame,
    periods: pd.DataFrame,
    representative_guard: Guardrail,
    top_class: pd.DataFrame,
    primary: Guardrail,
) -> None:
    primary_rank = int(
        selection.loc[selection["guardrail"] == primary.name, "blind_rank"].iloc[0]
    )
    primary_selection = selection[selection["guardrail"] == primary.name].iloc[0]
    top = selection.head(15)
    top_names = top_class["guardrail"].astype(str).tolist()
    focus_guards = list(dict.fromkeys(["none", *top_names, primary.name]))
    focus_holdout = holdout[holdout["guardrail"].isin(focus_guards)].copy()
    focus_holdout["guard_order"] = focus_holdout["guardrail"].map(
        {name: index for index, name in enumerate(focus_guards)}
    )
    focus_holdout = focus_holdout.sort_values(["base_variant", "guard_order"])

    lines = [
        "# Validazione temporale cieca del guardrail gennaio 2026",
        "",
        f"Cutoff complessivo: `{as_of}`. Selezione congelata al `2026-01-05`.",
        "Mercato: `ETH-USD Coinbase`, candele daily UTC. Commissione taker",
        "`0,16%` per lato. Baseline ufficiale invariata.",
        "",
        "## Protocollo",
        "",
        "1. La graduatoria vede soltanto dati fino al 5 gennaio 2026.",
        "2. Nessun punteggio usa l'esito del 6/13 gennaio o il movimento di agosto.",
        "3. Sono ammissibili solo regole che non perdono breakout favorevoli, non",
        "   peggiorano annualizzato, drawdown o Sharpe in nessuno dei due sistemi",
        "   e riducono per quanto possibile le perdite breakout pre-2026.",
        "4. Dopo il congelamento viene aperto il blocco 2026.",
        "",
        "Avvertenza: slope SMA200, distanza SMA50/SMA200 e return 90g sono stati",
        "scelti dopo aver studiato gennaio. Il replay e' cieco sulle soglie e sugli",
        "esiti 2026, ma non e' un fuori campione incontaminato sulle feature.",
        "",
        "## Graduatoria pre-2026",
        "",
        "| Rank | Guardrail | Famiglia | Loss breakout | Episodi favorevoli persi | Delta ann. minimo | Delta DD minimo | Delta Sharpe minimo | Ammissibile |",
        "|---:|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for _, row in top.iterrows():
        lines.append(
            f"| {int(row['blind_rank'])} | {row['guardrail']} | {row['family']} | "
            f"{int(row['breakout_losses'])} | "
            f"{int(row['max_missed_profitable_episodes'])} | "
            f"{_pct(row['min_delta_annualized'])} | {_pct(row['min_delta_drawdown'])} | "
            f"{_num(row['min_delta_sharpe'])} | "
            f"{'SI' if row['admissible_pre2026'] else 'NO'} |"
        )
    lines.extend(
        [
            "",
            f"Prima riga della classe a pari merito: `{representative_guard.name}` - {representative_guard.label}.",
            f"La classe migliore contiene `{len(top_class)}` soglie indistinguibili prima del 2026:",
            ", ".join(f"`{name}`" for name in top_names) + ".",
            f"Il guardrail principale proposto `{primary.name}` occupa il rank `{primary_rank}`",
            f"ed e' {'ammissibile' if primary_selection['admissible_pre2026'] else 'non ammissibile'}",
            "usando esclusivamente il periodo precedente al 2026.",
            "",
            "## Apertura del holdout 2026",
            "",
            "| Sistema | Guardrail | Entry gennaio | Return gennaio | Cattura agosto | Entry agosto | Annualizzato totale | Max DD | Sharpe |",
            "|---|---|---|---:|---|---|---:|---:|---:|",
        ]
    )
    for _, row in focus_holdout.iterrows():
        lines.append(
            f"| {row['base_variant']} | {row['guardrail']} | "
            f"{_day(row['january_entry_date'])} | {_pct(row['january_return'])} | "
            f"{'SI' if row['captures_august'] else 'NO'} | "
            f"{_day(row['august_source_entry'])} | "
            f"{_pct(row['full_annualized_return'])} | "
            f"{_pct(row['full_max_drawdown'])} | {_num(row['full_sharpe_ratio'])} |"
        )
    lines.extend(
        [
            "",
            "## Stabilita' per blocchi temporali del guardrail principale",
            "",
            "| Periodo | Sistema | Guardrail | Buy | Rendimento | Max DD | Sharpe |",
            "|---|---|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in periods.iterrows():
        lines.append(
            f"| {row['period']} | {row['base_variant']} | {row['guardrail']} | "
            f"{int(row['buy_signals'])} | {_pct(row['total_return'])} | "
            f"{_pct(row['max_drawdown'])} | {_num(row['sharpe_ratio'])} |"
        )

    top_holdout = holdout[holdout["guardrail"].isin(top_names)]
    top_outcomes = top_holdout.groupby("guardrail").agg(
        avoids_january=("january_entries", lambda values: bool((values == 0).all())),
        captures_august=("captures_august", "all"),
    )
    top_avoids_count = int(top_outcomes["avoids_january"].sum())
    top_august_count = int(top_outcomes["captures_august"].sum())
    primary_holdout = holdout[holdout["guardrail"] == primary.name]
    primary_avoids = bool((primary_holdout["january_entries"] == 0).all())
    primary_august = bool(primary_holdout["captures_august"].all())
    lines.extend(
        [
            "",
            "## Esito dei gate",
            "",
            f"- classe cieca che evita entrambe le entrate di gennaio: `{top_avoids_count}/{len(top_class)}`;",
            f"- classe cieca che conserva agosto: `{top_august_count}/{len(top_class)}`;",
            f"- guardrail principale evita entrambe le entrate di gennaio: {'SI' if primary_avoids else 'NO'};",
            f"- guardrail principale conserva agosto: {'SI' if primary_august else 'NO'};",
            f"- guardrail principale ammissibile prima del 2026: {'SI' if primary_selection['admissible_pre2026'] else 'NO'};",
            "- costi, ritardi e soglie vicine: gia' superati nel test precedente;",
            "- nuova attivazione live indipendente del guardrail: NON ANCORA.",
            "",
            "## Decisione",
            "",
            "Il gate retrospettivo e' superato soltanto in parte: la famiglia distanza",
            "SMA50/SMA200 emerge senza vedere il 2026, ma il periodo pre-2026 non identifica",
            "una soglia unica e non tutte le soglie equivalenti bloccano gennaio.",
            "Il guardrail combinato resta ammissibile e piu' prudente contro un blocco",
            "eccessivo, ma non viene promosso a Baseline. Deve essere congelato in shadow",
            "e valutato alla prima nuova attivazione indipendente; non serve attendere un",
            "numero fisso di mesi.",
            "",
            "## File generati",
            "",
            "- `reports/january_2026_guardrail_blind_selection.csv`;",
            "- `reports/january_2026_guardrail_blind_holdout.csv`;",
            "- `reports/january_2026_guardrail_blind_periods.csv`.",
            "- `reports/january_2026_guardrail_blind_trades.csv`.",
            "- `reports/january_2026_guardrail_shadow_spec.json`.",
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
    indicators = evaluation_frame(
        add_context_features(
            add_confirmation_features(compute_all_indicators(candles))
        )
    )
    rules = build_rules()
    guards = build_guardrails()

    blind_grid, _, _ = evaluate_grid(indicators.loc[:PRE_JAN_END], rules, guards)
    selection = blind_selection(blind_grid)
    top_class = top_equivalence_class(selection)
    selected_name = str(top_class.iloc[0]["guardrail"])
    guard_map = {guard.name: guard for guard in guards}
    selected_guard = guard_map[selected_name]
    primary = primary_guardrail()

    focus_guards = list(
        {
            guard.name: guard
            for guard in (
                guard_map["none"],
                *(guard_map[name] for name in top_class["guardrail"]),
                primary,
            )
        }.values()
    )
    holdout, focus_trades, frames = evaluate_grid(indicators, rules, focus_guards)
    focus_names = [guard.name for guard in focus_guards]
    periods = period_comparison(
        frames, list(dict.fromkeys(["none", selected_guard.name, primary.name]))
    )

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    selection.to_csv(OUT_SELECTION, index=False)
    holdout.to_csv(OUT_HOLDOUT, index=False)
    periods.to_csv(OUT_PERIODS, index=False)
    focus_trades.to_csv(OUT_TRADES, index=False)
    write_report(
        args.output,
        as_of=args.as_of,
        selection=selection,
        holdout=holdout,
        periods=periods,
        representative_guard=selected_guard,
        top_class=top_class,
        primary=primary,
    )

    print(f"Saved {args.output}")
    print(f"Blind selected: {selected_guard.name}")
    print(selection.head(15).to_string(index=False))
    print("\nHOLDOUT")
    print(
        holdout[
            [
                "base_variant",
                "guardrail",
                "january_entry_date",
                "january_return",
                "captures_august",
                "august_source_entry",
                "full_annualized_return",
                "full_max_drawdown",
                "full_sharpe_ratio",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
