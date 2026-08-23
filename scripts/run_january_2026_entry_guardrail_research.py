"""Ricerca di un guardrail per evitare il falso breakout di gennaio 2026.

La Baseline ufficiale e il candidato breakout congelato restano invariati.
Questo script applica filtri ex ante soltanto al percorso di ingresso breakout
e misura il danno collaterale sull'intera storia ETH-USD Coinbase.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import exposure_from_signal, run_backtest
from config import CFG
from data.coinbase import fetch_daily_candles
from indicators.technical_indicators import compute_all_indicators
from pipeline import evaluation_frame
from scripts.run_august_2026_breakout_entry_research import (
    FEE_SCENARIOS,
    TAKER_FEE,
    _entry_masks,
    _return_stats,
    baseline_variant,
    extract_trades,
)
from scripts.run_breakout_event_robustness_audit import add_context_features
from scripts.run_breakout_rsi_confirmation_research import (
    CURRENT,
    RSI40_LEGACY,
    BreakoutRule,
    add_confirmation_features,
    breakout_mask,
    build_rules,
)
from strategy.signals import (
    HOLD_ACTION,
    SMA50_BREAK_PCT,
    TRAILING_MOMENTUM_MIN,
    TRAILING_STOP_PCT,
    TRAILING_VOLUME_REL_MIN,
)


OUT_MD = PROJECT_ROOT / "reports" / "january_2026_entry_guardrail_research.md"
OUT_GRID = PROJECT_ROOT / "reports" / "january_2026_entry_guardrail_grid.csv"
OUT_TRADES = PROJECT_ROOT / "reports" / "january_2026_entry_guardrail_trades.csv"
OUT_YEARLY = PROJECT_ROOT / "reports" / "january_2026_entry_guardrail_yearly.csv"
OUT_ROBUSTNESS = (
    PROJECT_ROOT / "reports" / "january_2026_entry_guardrail_robustness.csv"
)
OUT_FEATURES = (
    PROJECT_ROOT / "reports" / "january_2026_entry_guardrail_entry_features.csv"
)

PRE_JAN_END = pd.Timestamp("2026-01-05")
JAN_START = pd.Timestamp("2026-01-01")
JAN_END = pd.Timestamp("2026-01-31")
AUGUST_EVENT = pd.Timestamp("2026-08-17")
PRE_AUGUST_END = pd.Timestamp("2026-08-16")
BASE_RULE_NAMES = (CURRENT, RSI40_LEGACY)


@dataclass(frozen=True)
class Guardrail:
    name: str
    label: str
    family: str
    slope_threshold: float | None = None
    gap_threshold: float | None = None
    return90_threshold: float | None = None

    def allowed(self, df: pd.DataFrame) -> pd.Series:
        if self.family == "none":
            return pd.Series(True, index=df.index)

        slope_risk = (
            df["SMA200Slope20"] > float(self.slope_threshold)
            if self.slope_threshold is not None
            else pd.Series(False, index=df.index)
        )
        gap_risk = (
            df["SMA50VsSMA200"] < float(self.gap_threshold)
            if self.gap_threshold is not None
            else pd.Series(False, index=df.index)
        )
        return_risk = (
            df["Return90"] < float(self.return90_threshold)
            if self.return90_threshold is not None
            else pd.Series(False, index=df.index)
        )

        if self.family == "slope":
            blocked = slope_risk
        elif self.family == "gap":
            blocked = gap_risk
        elif self.family == "return90":
            blocked = return_risk
        elif self.family == "slope_gap":
            blocked = slope_risk & gap_risk
        elif self.family == "slope_return90":
            blocked = slope_risk & return_risk
        elif self.family == "gap_return90":
            blocked = gap_risk & return_risk
        elif self.family == "risk2of3":
            risk_count = (
                slope_risk.astype(int)
                + gap_risk.astype(int)
                + return_risk.astype(int)
            )
            blocked = risk_count >= 2
        else:
            raise ValueError(f"Famiglia guardrail sconosciuta: {self.family}")
        return (~blocked).fillna(False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Test guardrail ex ante per il breakout di gennaio 2026."
    )
    parser.add_argument(
        "--as-of",
        default=(date.today() - timedelta(days=1)).isoformat(),
        help="Ultima candela daily chiusa inclusa (YYYY-MM-DD).",
    )
    parser.add_argument("--output", type=Path, default=OUT_MD)
    return parser.parse_args()


def _token(value: float) -> str:
    prefix = "m" if value < 0.0 else "p"
    body = f"{abs(value) * 100:.1f}".replace(".", "p")
    return f"{prefix}{body}"


def _guard(
    family: str,
    *,
    slope: float | None = None,
    gap: float | None = None,
    return90: float | None = None,
) -> Guardrail:
    parts = [family]
    labels: list[str] = []
    if slope is not None:
        parts.append(f"s{_token(slope)}")
        labels.append(f"slope SMA200 20g > {slope:.1%}")
    if gap is not None:
        parts.append(f"g{_token(gap)}")
        labels.append(f"SMA50/SMA200 < {gap:.1%}")
    if return90 is not None:
        parts.append(f"r{_token(return90)}")
        labels.append(f"return 90g < {return90:.1%}")
    if family == "risk2of3":
        label = "Blocca con almeno 2 rischi: " + ", ".join(labels)
    elif family in {"slope_gap", "slope_return90", "gap_return90"}:
        label = "Blocca se insieme: " + " e ".join(labels)
    else:
        label = "Blocca se " + labels[0]
    return Guardrail(
        name="__".join(parts),
        label=label,
        family=family,
        slope_threshold=slope,
        gap_threshold=gap,
        return90_threshold=return90,
    )


def build_guardrails() -> list[Guardrail]:
    guards = [Guardrail("none", "Nessun guardrail", "none")]
    slopes = (-0.02, -0.01, 0.0, 0.005, 0.01, 0.015)
    gaps = (-0.18, -0.17, -0.165, -0.16, -0.155, -0.15, -0.145, -0.14, -0.13)
    returns = (-0.25, -0.20, -0.175, -0.15, -0.125, -0.10, -0.075, -0.05)

    guards.extend(_guard("slope", slope=value) for value in slopes)
    guards.extend(_guard("gap", gap=value) for value in gaps)
    guards.extend(_guard("return90", return90=value) for value in returns)

    for slope in (-0.01, 0.0, 0.01):
        for gap in (-0.17, -0.16, -0.15, -0.14, -0.13):
            guards.append(_guard("slope_gap", slope=slope, gap=gap))
    for slope in (-0.01, 0.0, 0.01):
        for return90 in (-0.20, -0.15, -0.125, -0.10, -0.075):
            guards.append(
                _guard("slope_return90", slope=slope, return90=return90)
            )
    for gap in (-0.17, -0.16, -0.15, -0.14, -0.13):
        for return90 in (-0.20, -0.15, -0.125, -0.10, -0.075):
            guards.append(_guard("gap_return90", gap=gap, return90=return90))
    for slope in (-0.01, 0.0, 0.01):
        for gap in (-0.16, -0.15, -0.14):
            for return90 in (-0.15, -0.125, -0.10):
                guards.append(
                    _guard(
                        "risk2of3",
                        slope=slope,
                        gap=gap,
                        return90=return90,
                    )
                )
    return guards


def primary_guardrail() -> Guardrail:
    return _guard("slope_gap", slope=0.0, gap=-0.15)


def secondary_guardrail() -> Guardrail:
    return _guard("risk2of3", slope=0.0, gap=-0.15, return90=-0.10)


def build_frame_from_breakout(
    df: pd.DataFrame,
    breakout: pd.Series,
) -> pd.DataFrame:
    baseline_entry, baseline_hold_core, _, _, _ = _entry_masks(
        df, baseline_variant()
    )
    entry = baseline_entry | breakout
    official_sell = df["Close"] < df["SMA50"] * (1.0 - SMA50_BREAK_PCT)
    signals = np.full(len(df), HOLD_ACTION, dtype=object)
    origins = np.full(len(df), "", dtype=object)
    exposed = False
    peak_close: float | None = None

    for pos, (day, row) in enumerate(df.iterrows()):
        close = float(row["Close"])
        if bool(official_sell.loc[day]):
            signals[pos] = "VENDI"
            origins[pos] = "sma50_exit"
            exposed = False
            peak_close = None
            continue
        if not exposed and bool(entry.loc[day]):
            signals[pos] = "ACQUISTA"
            origins[pos] = "breakout_entry" if bool(breakout.loc[day]) else "standard"
            exposed = True
            peak_close = close
            continue
        if exposed and bool(baseline_hold_core.loc[day]):
            peak_close = max(peak_close if peak_close is not None else close, close)
            continue
        if exposed:
            peak_close = max(peak_close if peak_close is not None else close, close)
            trail_hit = close <= peak_close * (1.0 - TRAILING_STOP_PCT)
            trail_confirmed = bool(
                trail_hit
                and row["Momentum7"] >= TRAILING_MOMENTUM_MIN
                and row["VolumeRel20"] >= TRAILING_VOLUME_REL_MIN
            )
            if trail_confirmed:
                signals[pos] = "VENDI"
                origins[pos] = "trail8_exit"
                exposed = False
                peak_close = None

    return pd.DataFrame(
        {"Close": df["Close"], "Segnale": signals, "SignalOrigin": origins},
        index=df.index,
    )


def _captured_reference_wins(
    unguarded: pd.DataFrame,
    guarded: pd.DataFrame,
) -> tuple[int, list[str]]:
    references = unguarded[
        (unguarded["entry_origin"] == "breakout_entry")
        & (unguarded["status"] == "closed")
        & (unguarded["net_return"] > 0.0)
        & (pd.to_datetime(unguarded["entry_date"]) <= PRE_JAN_END)
    ]
    guarded_entries = pd.to_datetime(
        guarded.loc[guarded["entry_origin"] == "breakout_entry", "entry_date"]
    )
    missed: list[str] = []
    for _, trade in references.iterrows():
        start = pd.Timestamp(trade["entry_date"])
        end = pd.Timestamp(trade["exit_date"])
        if not ((guarded_entries >= start) & (guarded_entries <= end)).any():
            missed.append(start.date().isoformat())
    return len(references) - len(missed), missed


def _event_source(trades: pd.DataFrame, event: pd.Timestamp) -> pd.Series | None:
    alternative = trades[trades["entry_origin"] == "breakout_entry"]
    for _, trade in alternative.iterrows():
        start = pd.Timestamp(trade["entry_date"])
        end = (
            pd.Timestamp(trade["exit_date"])
            if pd.notna(trade["exit_date"])
            else pd.Timestamp.max
        )
        if start <= event <= end:
            return trade
    after = alternative[pd.to_datetime(alternative["entry_date"]) >= event]
    return None if after.empty else after.iloc[0]


def evaluate_grid(
    indicators: pd.DataFrame,
    rules: list[BreakoutRule],
    guards: list[Guardrail],
) -> tuple[pd.DataFrame, pd.DataFrame, dict[tuple[str, str], pd.DataFrame]]:
    rows: list[dict[str, object]] = []
    all_trades: list[pd.DataFrame] = []
    frames: dict[tuple[str, str], pd.DataFrame] = {}
    rule_map = {rule.name: rule for rule in rules}

    for base_name in BASE_RULE_NAMES:
        rule = rule_map[base_name]
        raw_breakout = breakout_mask(indicators, rule)
        unguarded_frame = build_frame_from_breakout(indicators, raw_breakout)
        unguarded_trades = extract_trades(
            unguarded_frame, variant=f"{base_name}__none", fee_rate=TAKER_FEE
        )
        for guard in guards:
            allowed = guard.allowed(indicators)
            guarded_breakout = raw_breakout & allowed
            frame = build_frame_from_breakout(indicators, guarded_breakout)
            key = (base_name, guard.name)
            frames[key] = frame
            equity, full, _ = run_backtest(
                frame[["Close", "Segnale"]], transaction_cost_rate=TAKER_FEE
            )
            _, pre_jan, _ = run_backtest(
                frame.loc[:PRE_JAN_END, ["Close", "Segnale"]],
                transaction_cost_rate=TAKER_FEE,
            )
            _, pre_august, _ = run_backtest(
                frame.loc[:PRE_AUGUST_END, ["Close", "Segnale"]],
                transaction_cost_rate=TAKER_FEE,
            )
            trades = extract_trades(
                frame, variant=f"{base_name}__{guard.name}", fee_rate=TAKER_FEE
            )
            tagged = trades.copy()
            tagged.insert(0, "guardrail", guard.name)
            tagged.insert(0, "base_variant", base_name)
            all_trades.append(tagged)
            alternative = trades[trades["entry_origin"] == "breakout_entry"]
            closed = alternative[alternative["status"] == "closed"]
            jan = alternative[
                pd.to_datetime(alternative["entry_date"]).between(JAN_START, JAN_END)
            ]
            event_trade = _event_source(trades, AUGUST_EVENT)
            captured, missed = _captured_reference_wins(unguarded_trades, trades)
            train = _return_stats(
                equity.loc[:"2019-12-31", "DailyReturnStrategy"]
            )
            historical_test = _return_stats(
                equity.loc["2020-01-01":PRE_JAN_END, "DailyReturnStrategy"]
            )
            rows.append(
                {
                    "base_variant": base_name,
                    "guardrail": guard.name,
                    "guardrail_label": guard.label,
                    "family": guard.family,
                    "slope_threshold": guard.slope_threshold,
                    "gap_threshold": guard.gap_threshold,
                    "return90_threshold": guard.return90_threshold,
                    **{f"full_{key}": value for key, value in asdict(full).items()},
                    **{f"pre_jan_{key}": value for key, value in asdict(pre_jan).items()},
                    **{f"pre_august_{key}": value for key, value in asdict(pre_august).items()},
                    **{f"train_{key}": value for key, value in train.items()},
                    **{
                        f"historical_test_{key}": value
                        for key, value in historical_test.items()
                    },
                    "raw_breakout_days": int(raw_breakout.sum()),
                    "allowed_breakout_days": int(guarded_breakout.sum()),
                    "breakout_entries": len(alternative),
                    "breakout_closed": len(closed),
                    "breakout_losses": int((closed["net_return"] <= 0.0).sum()),
                    "january_entries": len(jan),
                    "january_entry_date": (
                        pd.Timestamp(jan.iloc[0]["entry_date"]) if not jan.empty else pd.NaT
                    ),
                    "january_return": (
                        float(jan.iloc[0]["net_return"]) if not jan.empty else np.nan
                    ),
                    "captures_august": bool(
                        event_trade is not None
                        and pd.Timestamp(event_trade["entry_date"]) <= AUGUST_EVENT
                    ),
                    "august_source_entry": (
                        pd.Timestamp(event_trade["entry_date"])
                        if event_trade is not None
                        else pd.NaT
                    ),
                    "august_return_to_cutoff": (
                        float(event_trade["net_return"])
                        if event_trade is not None
                        else np.nan
                    ),
                    "retained_profitable_episodes": captured,
                    "missed_profitable_episodes": ",".join(missed),
                    "signals_equal_pre_jan": bool(
                        frame.loc[:PRE_JAN_END, "Segnale"].equals(
                            unguarded_frame.loc[:PRE_JAN_END, "Segnale"]
                        )
                    ),
                }
            )
    return pd.DataFrame(rows), pd.concat(all_trades, ignore_index=True), frames


def aggregate_guards(grid: pd.DataFrame) -> pd.DataFrame:
    reference = (
        grid[grid["guardrail"] == "none"]
        .set_index("base_variant")
        .to_dict(orient="index")
    )
    work = grid.copy()
    work["delta_pre_jan_ann"] = work.apply(
        lambda row: row["pre_jan_annualized_return"]
        - reference[row["base_variant"]]["pre_jan_annualized_return"],
        axis=1,
    )
    work["delta_pre_jan_sharpe"] = work.apply(
        lambda row: row["pre_jan_sharpe_ratio"]
        - reference[row["base_variant"]]["pre_jan_sharpe_ratio"],
        axis=1,
    )
    rows: list[dict[str, object]] = []

    def missed_count(value: object) -> int:
        if pd.isna(value) or not str(value).strip():
            return 0
        return len(str(value).split(","))

    for guard_name, selected in work.groupby("guardrail", sort=False):
        first = selected.iloc[0]
        rows.append(
            {
                "guardrail": guard_name,
                "label": first["guardrail_label"],
                "family": first["family"],
                "avoids_both_january_entries": bool(
                    len(selected) == len(BASE_RULE_NAMES)
                    and (selected["january_entries"] == 0).all()
                ),
                "captures_august_both": bool(selected["captures_august"].all()),
                "max_missed_profitable_episodes": int(
                    selected["missed_profitable_episodes"].map(missed_count).max()
                ),
                "min_delta_pre_jan_ann": float(selected["delta_pre_jan_ann"].min()),
                "min_delta_pre_jan_sharpe": float(
                    selected["delta_pre_jan_sharpe"].min()
                ),
                "average_full_ann": float(selected["full_annualized_return"].mean()),
                "average_full_drawdown": float(selected["full_max_drawdown"].mean()),
                "average_full_sharpe": float(selected["full_sharpe_ratio"].mean()),
            }
        )
    result = pd.DataFrame(rows)
    result["eligible"] = (
        result["avoids_both_january_entries"]
        & result["captures_august_both"]
        & (result["max_missed_profitable_episodes"] == 0)
    )
    return result.sort_values(
        ["eligible", "max_missed_profitable_episodes", "min_delta_pre_jan_ann", "average_full_sharpe"],
        ascending=[False, True, False, False],
    )


def detailed_entry_features(
    indicators: pd.DataFrame,
    grid_trades: pd.DataFrame,
    guards: set[str],
) -> pd.DataFrame:
    selected = grid_trades[
        grid_trades["guardrail"].isin(guards)
        & (grid_trades["entry_origin"] == "breakout_entry")
    ].copy()
    rows: list[dict[str, object]] = []
    for _, trade in selected.iterrows():
        day = pd.Timestamp(trade["entry_date"])
        feature = indicators.loc[day]
        rows.append(
            {
                **trade.to_dict(),
                "rsi": float(feature["RSI"]),
                "momentum_7d": float(feature["Momentum7"]),
                "volume_rel_20": float(feature["VolumeRel20"]),
                "sma200_slope_20d": float(feature["SMA200Slope20"]),
                "sma50_vs_sma200": float(feature["SMA50VsSMA200"]),
                "return_90d": float(feature["Return90"]),
                "distance_sma200": float(feature["DistanceSMA200"]),
            }
        )
    return pd.DataFrame(rows)


def yearly_comparison(
    frames: dict[tuple[str, str], pd.DataFrame],
    selected_guards: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for base_name in BASE_RULE_NAMES:
        for guard_name in selected_guards:
            frame = frames[(base_name, guard_name)]
            equity, _, _ = run_backtest(
                frame[["Close", "Segnale"]], transaction_cost_rate=TAKER_FEE
            )
            for year, returns in equity["DailyReturnStrategy"].groupby(equity.index.year):
                stats = _return_stats(returns)
                buys = frame.loc[frame.index.year == year, "Segnale"].eq("ACQUISTA").sum()
                rows.append(
                    {
                        "year": int(year),
                        "base_variant": base_name,
                        "guardrail": guard_name,
                        "buy_signals": int(buys),
                        **stats,
                    }
                )
    return pd.DataFrame(rows)


def robustness_comparison(
    frames: dict[tuple[str, str], pd.DataFrame],
    selected_guards: list[str],
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for base_name in BASE_RULE_NAMES:
        for guard_name in selected_guards:
            frame = frames[(base_name, guard_name)]
            for scenario, fee in FEE_SCENARIOS.items():
                _, metrics, _ = run_backtest(
                    frame[["Close", "Segnale"]], transaction_cost_rate=fee
                )
                rows.append(
                    {
                        "test": "cost",
                        "scenario": scenario,
                        "value": fee,
                        "base_variant": base_name,
                        "guardrail": guard_name,
                        "annualized_return": metrics.annualized_return,
                        "max_drawdown": metrics.max_drawdown,
                        "sharpe_ratio": metrics.sharpe_ratio,
                    }
                )
            desired = exposure_from_signal(
                frame["Segnale"], CFG.exposure_map
            ).ffill().fillna(0.0)
            for delay in (0, 1, 2):
                effective = desired.shift(1 + delay).fillna(0.0)
                turnover = effective.diff().abs().fillna(effective.abs())
                daily = (
                    effective * frame["Close"].pct_change()
                    - turnover * TAKER_FEE
                )
                stats = _return_stats(daily)
                rows.append(
                    {
                        "test": "delay",
                        "scenario": f"extra_delay_{delay}",
                        "value": delay,
                        "base_variant": base_name,
                        "guardrail": guard_name,
                        "annualized_return": stats["annualized_return"],
                        "max_drawdown": stats["max_drawdown"],
                        "sharpe_ratio": stats["sharpe_ratio"],
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
    indicators: pd.DataFrame,
    grid: pd.DataFrame,
    aggregate: pd.DataFrame,
    trades: pd.DataFrame,
    robustness: pd.DataFrame,
) -> None:
    primary = primary_guardrail()
    secondary = secondary_guardrail()
    selected_names = ["none", primary.name, secondary.name]
    focus = grid[grid["guardrail"].isin(selected_names)].copy()
    focus["order"] = focus["guardrail"].map(
        {"none": 0, primary.name: 1, secondary.name: 2}
    )
    focus = focus.sort_values(["base_variant", "order"])
    jan = indicators.loc[
        [pd.Timestamp("2026-01-06"), pd.Timestamp("2026-01-13")]
    ]
    eligible = aggregate[aggregate["eligible"]].head(12)
    neighborhood = aggregate[
        (aggregate["family"] == "slope_gap")
        & aggregate["guardrail"].str.contains("sp0p0|sp1p0|sm1p0", regex=True)
        & aggregate["guardrail"].str.contains("gm16p0|gm15p0|gm14p0", regex=True)
    ].sort_values("guardrail")
    lines = [
        "# Guardrail ingresso breakout - caso gennaio 2026",
        "",
        f"Data test: `{as_of}`. Mercato: `ETH-USD Coinbase`, candele daily UTC.",
        "Commissione principale: taker `0,16%` per lato.",
        "La Baseline ufficiale, il bot e la dashboard non sono stati modificati.",
        "",
        "## Obiettivo",
        "",
        "Evitare gli ingressi breakout del 6 e 13 gennaio 2026 usando soltanto",
        "informazioni disponibili alla chiusura della candela, senza una regola",
        "legata alla data e senza perdere gli episodi breakout storicamente favorevoli.",
        "",
        "## Diagnosi ex ante di gennaio 2026",
        "",
        "| Data | Close | RSI | SMA200 slope 20g | SMA50/SMA200 | Return 90g |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for day, row in jan.iterrows():
        lines.append(
            f"| {day.date().isoformat()} | {row['Close']:.2f} | {row['RSI']:.2f} | "
            f"{_pct(row['SMA200Slope20'])} | {_pct(row['SMA50VsSMA200'])} | "
            f"{_pct(row['Return90'])} |"
        )
    lines.extend(
        [
            "",
            "Entrambe le date presentano lo stesso regime: SMA200 ancora crescente",
            "e SMA50 oltre il 15% sotto SMA200. Il rendimento a 90 giorni e' inoltre",
            "fortemente negativo. Il 6 gennaio ha RSI sopra 65; il 13 gennaio rientra",
            "nel corridoio 40-65, quindi il solo tetto RSI non elimina l'episodio.",
            "",
            "## Regole confrontate",
            "",
            f"- principale: `{primary.name}` - {primary.label};",
            f"- controllo a tre fattori: `{secondary.name}` - {secondary.label};",
            "- griglia completa: filtri singoli, coppie e due rischi su tre, con",
            "  soglie adiacenti su slope SMA200, distanza SMA50/SMA200 e return 90g.",
            "",
            "Il filtro viene applicato solo al nuovo percorso breakout. Le entrate",
            "e le uscite ufficiali conservano esattamente le regole correnti.",
            "",
            "## Confronto principale",
            "",
            "| Sistema ingresso | Guardrail | Rendimento totale | Annualizzato | Max DD | Sharpe | Profit factor | Operazioni | Breakout loss | Entry gennaio | Return gennaio | Cattura 17/08 | Episodi favorevoli persi |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---|---:|---|---:|",
        ]
    )
    for _, row in focus.iterrows():
        lines.append(
            f"| {row['base_variant']} | {row['guardrail']} | "
            f"{_pct(row['full_total_return'])} | {_pct(row['full_annualized_return'])} | "
            f"{_pct(row['full_max_drawdown'])} | {_num(row['full_sharpe_ratio'])} | "
            f"{_num(row['full_profit_factor'])} | {int(row['full_num_operations'])} | "
            f"{int(row['breakout_losses'])} | {_day(row['january_entry_date'])} | "
            f"{_pct(row['january_return'])} | "
            f"{'SI' if row['captures_august'] else 'NO'} | "
            f"{row['missed_profitable_episodes'] or '0'} |"
        )
    lines.extend(
        [
            "",
            "## Migliori configurazioni ammissibili",
            "",
            "Ammissibile significa: blocca gennaio in entrambi i sistemi, conserva",
            "il movimento del 17 agosto e non perde episodi breakout favorevoli pregressi.",
            "",
            "| Guardrail | Famiglia | Delta ann. storico peggiore | Delta Sharpe storico peggiore | Ann. medio totale | DD medio totale | Sharpe medio totale |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in eligible.iterrows():
        lines.append(
            f"| {row['guardrail']} | {row['family']} | "
            f"{_pct(row['min_delta_pre_jan_ann'])} | "
            f"{_num(row['min_delta_pre_jan_sharpe'])} | "
            f"{_pct(row['average_full_ann'])} | {_pct(row['average_full_drawdown'])} | "
            f"{_num(row['average_full_sharpe'])} |"
        )
    lines.extend(
        [
            "",
            "## Stabilita' intorno alla regola principale",
            "",
            "| Guardrail | Evita gennaio | Cattura agosto | Episodi persi | Delta ann. storico peggiore |",
            "|---|---|---|---:|---:|",
        ]
    )
    for _, row in neighborhood.iterrows():
        lines.append(
            f"| {row['guardrail']} | "
            f"{'SI' if row['avoids_both_january_entries'] else 'NO'} | "
            f"{'SI' if row['captures_august_both'] else 'NO'} | "
            f"{int(row['max_missed_profitable_episodes'])} | "
            f"{_pct(row['min_delta_pre_jan_ann'])} |"
        )

    primary_rows = focus[focus["guardrail"] == primary.name]
    primary_trades = trades[
        trades["guardrail"].isin(["none", primary.name])
        & trades["base_variant"].isin(BASE_RULE_NAMES)
        & (trades["entry_origin"] == "breakout_entry")
    ]
    lines.extend(
        [
            "",
            "## Cronologia breakout senza filtro e con guardrail principale",
            "",
            "| Sistema | Guardrail | Ingresso | Uscita | Esito | Rendimento netto |",
            "|---|---|---|---|---|---:|",
        ]
    )
    for _, row in primary_trades.iterrows():
        lines.append(
            f"| {row['base_variant']} | {row['guardrail']} | "
            f"{_day(row['entry_date'])} | {_day(row['exit_date'])} | "
            f"{row['status']} | {_pct(row['net_return'])} |"
        )

    robust_primary = robustness[robustness["guardrail"] == primary.name]
    lines.extend(
        [
            "",
            "## Costi e ritardi - guardrail principale",
            "",
            "| Sistema | Test | Scenario | Ann. | Max DD | Sharpe |",
            "|---|---|---|---:|---:|---:|",
        ]
    )
    for _, row in robust_primary.iterrows():
        lines.append(
            f"| {row['base_variant']} | {row['test']} | {row['scenario']} | "
            f"{_pct(row['annualized_return'])} | {_pct(row['max_drawdown'])} | "
            f"{_num(row['sharpe_ratio'])} |"
        )

    avoids = bool((primary_rows["january_entries"] == 0).all())
    captures = bool(primary_rows["captures_august"].all())
    no_misses = bool(
        primary_rows["missed_profitable_episodes"].fillna("").eq("").all()
    )
    lines.extend(
        [
            "",
            "## Conclusione",
            "",
            f"- la regola principale evita entrambe le entrate di gennaio: {'SI' if avoids else 'NO'};",
            f"- conserva il movimento del 17 agosto: {'SI' if captures else 'NO'};",
            f"- conserva gli episodi favorevoli precedenti: {'SI' if no_misses else 'NO'};",
            "- il miglioramento dopo gennaio e' in-sample rispetto al problema osservato",
            "  e non basta, da solo, per una promozione ufficiale;",
            "- il dato piu' importante e' il comportamento fino al 5 gennaio 2026:",
            "  misura il costo storico del filtro prima del caso che lo ha motivato;",
            "- nel sistema RSI 40-65 il guardrail modifica una sola operazione storica,",
            "  proprio gennaio 2026; nel sistema RSI >=40 elimina anche l'ingresso",
            "  indipendente del 3 maggio 2018, chiuso a -12,85%; il campione resta",
            "  quindi troppo piccolo per parlare di validazione definitiva;",
            "- decisione: guardrail candidato shadow. Baseline invariata.",
            "",
            "## File generati",
            "",
            "- `reports/january_2026_entry_guardrail_grid.csv`;",
            "- `reports/january_2026_entry_guardrail_trades.csv`;",
            "- `reports/january_2026_entry_guardrail_yearly.csv`;",
            "- `reports/january_2026_entry_guardrail_robustness.csv`;",
            "- `reports/january_2026_entry_guardrail_entry_features.csv`.",
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
    grid, trades, frames = evaluate_grid(indicators, rules, guards)
    aggregate = aggregate_guards(grid)
    primary = primary_guardrail()
    secondary = secondary_guardrail()
    selected = ["none", primary.name, secondary.name]
    yearly = yearly_comparison(frames, selected)
    robustness = robustness_comparison(frames, selected)
    features = detailed_entry_features(
        indicators, trades, {"none", primary.name, secondary.name}
    )

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUT_GRID, index=False)
    trades[trades["guardrail"].isin(selected)].to_csv(OUT_TRADES, index=False)
    yearly.to_csv(OUT_YEARLY, index=False)
    robustness.to_csv(OUT_ROBUSTNESS, index=False)
    features.to_csv(OUT_FEATURES, index=False)
    write_report(
        args.output,
        as_of=args.as_of,
        indicators=indicators,
        grid=grid,
        aggregate=aggregate,
        trades=trades,
        robustness=robustness,
    )

    focus = grid[
        grid["guardrail"].isin(selected)
        & grid["base_variant"].isin(BASE_RULE_NAMES)
    ][
        [
            "base_variant",
            "guardrail",
            "full_annualized_return",
            "full_max_drawdown",
            "full_sharpe_ratio",
            "pre_jan_annualized_return",
            "january_entry_date",
            "january_return",
            "captures_august",
            "missed_profitable_episodes",
        ]
    ]
    print(f"Saved {args.output}")
    print(f"Tested guardrails: {len(guards)} x {len(BASE_RULE_NAMES)} systems")
    print(focus.to_string(index=False))
    print("\nTOP ELIGIBLE")
    print(
        aggregate[aggregate["eligible"]]
        .head(12)[
            [
                "guardrail",
                "family",
                "min_delta_pre_jan_ann",
                "min_delta_pre_jan_sharpe",
                "average_full_ann",
                "average_full_drawdown",
                "average_full_sharpe",
            ]
        ]
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
