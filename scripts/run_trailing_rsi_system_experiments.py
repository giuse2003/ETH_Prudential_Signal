"""
Analisi sperimentale del sistema Trailing Stop 8% + RSI Adattivo (Uscite Alternative).

Questo script non modifica i segnali ufficiali. Esegue il backtest del sistema di
uscita alternativo (Trailing stop con RSI adattivo e lock permanente, senza conferma
momentum/volume) mantenendo l'ingresso della baseline.
Calcola inoltre una validazione Walk-Forward su tre split temporali.
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
OUT_GRID_CSV = PROJECT_ROOT / "reports" / "trailing_rsi_system_grid.csv"
OUT_PERIOD_CSV = PROJECT_ROOT / "reports" / "trailing_rsi_system_periods.csv"
OUT_WF_CSV = PROJECT_ROOT / "reports" / "trailing_rsi_system_walkforward.csv"
OUT_EVENTS_CSV = PROJECT_ROOT / "reports" / "trailing_rsi_system_event_analysis.csv"
OUT_MD = PROJECT_ROOT / "reports" / "trailing_rsi_system_results.md"


def _simulate_trailing_rsi_system_frame(
    df: pd.DataFrame,
    variant_type: str,
    soglia_rsi: float | None = None,
    stop_stretto: float | None = None,
    label: str = "",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df[["Close", "Segnale"]].copy()

    if variant_type == "baseline":
        return out, pd.DataFrame(columns=[
            "variant", "date", "close", "peak_close", "stop_pct", "stop_level",
            "drawdown_from_peak", "rsi", "dist_sma200", "phase", "useful"
        ])

    exposure = 0.0
    peak_close: float | None = None
    stop_stretto_triggered = False
    signals: list[str] = []
    events: list[dict] = []

    for date, row in df.iterrows():
        official = str(row["Segnale"])
        signal = "MANTIENI"
        close = float(row["Close"])
        rsi = float(row["RSI"]) if pd.notna(row.get("RSI")) else float("nan")
        dist_sma200 = float(row["DistanceFromSMA200_Pct"]) if pd.notna(row.get("DistanceFromSMA200_Pct")) else 0.0

        if not exposure:
            if official == "ACQUISTA":
                exposure = 1.0
                peak_close = close
                stop_stretto_triggered = False
                signal = "ACQUISTA"
            else:
                signal = "MANTIENI"
        else:
            peak_close = max(peak_close, close)
            
            if variant_type == "trailing_8_pure":
                stop_pct = 0.08
            elif variant_type == "rsi_adaptive_system":
                if dist_sma200 > 60.0 and pd.notna(rsi) and rsi >= soglia_rsi:
                    stop_stretto_triggered = True

                if dist_sma200 <= 60.0:
                    stop_pct = 0.08
                elif stop_stretto_triggered:
                    stop_pct = stop_stretto
                else:
                    stop_pct = 0.15
            else:
                raise ValueError(f"Tipo variante sconosciuto: {variant_type}")

            stop_level = peak_close * (1.0 - stop_pct)
            
            if close <= stop_level:
                signal = "VENDI"
                exposure = 0.0
                
                # Classificazione fase
                if dist_sma200 <= 60.0:
                    phase = "normale"
                elif stop_stretto_triggered:
                    phase = "parabolica+lock"
                else:
                    phase = "parabolica"

                # Classificazione utilità (prezzo 10 giorni dopo inferiore)
                exit_row_idx = df.index.get_loc(date)
                if exit_row_idx + 10 < len(df):
                    price_10d_later = float(df.iloc[exit_row_idx + 10]["Close"])
                    useful = price_10d_later < close
                else:
                    price_10d_later = float("nan")
                    useful = False

                events.append(
                    {
                        "variant": label,
                        "date": date.strftime("%Y-%m-%d"),
                        "close": close,
                        "peak_close": peak_close,
                        "stop_pct": stop_pct,
                        "stop_level": stop_level,
                        "drawdown_from_peak": close / peak_close - 1.0,
                        "rsi": rsi,
                        "dist_sma200": dist_sma200,
                        "phase": phase,
                        "useful": useful,
                    }
                )
                peak_close = None
            else:
                signal = "MANTIENI"

        signals.append(signal)

    out["Segnale"] = signals
    if not events:
        columns = [
            "variant", "date", "close", "peak_close", "stop_pct", "stop_level",
            "drawdown_from_peak", "rsi", "dist_sma200", "phase", "useful"
        ]
        return out, pd.DataFrame(columns=columns)
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


def _write_markdown(
    grid: pd.DataFrame,
    periods: pd.DataFrame,
    events: pd.DataFrame,
    wf: pd.DataFrame,
    out_path: Path,
) -> None:
    grid_sorted = grid.copy()
    ref_mask = grid_sorted["variant"].isin(["baseline", "trailing_8_pure"])
    refs = grid_sorted[ref_mask]
    others = grid_sorted[~ref_mask].sort_values(["net_025_sharpe_ratio", "sharpe_ratio"], ascending=False)
    grid_display = pd.concat([refs, others], ignore_index=True)

    lines = [
        "# Trailing Stop 8% + RSI Adattivo System Results",
        "",
        "Questi risultati sono frutto di test sperimentali di ricerca e non modificano la strategia ufficiale.",
        "La verifica dello stop avviene esclusivamente sulla chiusura giornaliera (Close).",
        "",
        "## Metriche Periodo Completo",
        "",
        "| Variante | Ann. Lordo | Max DD Lordo | Sharpe Lordo | Sharpe Netto 0,25% | PF | Operazioni | Mediana Sharpe | Min Sharpe | Periodi Positivi |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for _, row in grid_display.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['net_025_sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{_ratio(row['median_period_sharpe'])} | "
            f"{_ratio(row['min_period_sharpe'])} | "
            f"{int(row['pos_periods_count'])}/4 |"
        )

    lines.extend(
        [
            "",
            "## Dettaglio Sottoperiodi: Sharpe Ratio",
            "",
            "| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |",
            "|---|---:|---:|---:|---:|",
        ]
    )

    sharpe_table = periods.pivot(index="variant", columns="period", values="period_sharpe_ratio")
    for variant in grid_display["variant"]:
        if variant in sharpe_table.index:
            row = sharpe_table.loc[variant]
            lines.append(
                "| "
                f"{variant} | "
                f"{_ratio(row.get('2017-2020'))} | "
                f"{_ratio(row.get('2021-2022'))} | "
                f"{_ratio(row.get('2023-2026'))} | "
                f"{_ratio(row.get('2025-2026'))} |"
            )

    lines.extend(
        [
            "",
            "## Dettaglio Sottoperiodi: Max Drawdown",
            "",
            "| Variante | 2017-2020 | 2021-2022 | 2023-2026 | 2025-2026 |",
            "|---|---:|---:|---:|---:|",
        ]
    )

    dd_table = periods.pivot(index="variant", columns="period", values="period_max_drawdown")
    for variant in grid_display["variant"]:
        if variant in dd_table.index:
            row = dd_table.loc[variant]
            lines.append(
                "| "
                f"{variant} | "
                f"{_pct(row.get('2017-2020'))} | "
                f"{_pct(row.get('2021-2022'))} | "
                f"{_pct(row.get('2023-2026'))} | "
                f"{_pct(row.get('2025-2026'))} |"
            )

    # Walk-Forward Table
    lines.extend(
        [
            "",
            "## Risultati Walk-Forward",
            "",
            "| Split | Periodo Train | Periodo Test | Variante Selezionata | Sharpe Train Netto | Ann. Test Netto | Max DD Test Netto | Sharpe Test Netto |",
            "|---|---|---|---|---:|---:|---:|---:|",
        ]
    )
    for _, row in wf.iterrows():
        lines.append(
            "| "
            f"{int(row['split'])} | "
            f"{row['train_range']} | "
            f"{row['test_range']} | "
            f"{row['best_variant']} | "
            f"{_ratio(row['train_sharpe'])} | "
            f"{_pct(row['test_annualized_return'])} | "
            f"{_pct(row['test_max_drawdown'])} | "
            f"{_ratio(row['test_sharpe_ratio'])} |"
        )

    # Analisi Eventi Uscita
    lines.extend(
        [
            "",
            "## Analisi degli Eventi di Uscita",
            "",
            "| Variante | Uscite Tentate | Uscite Effettive | Di cui Utili | Di cui Inutili | Win Rate Uscite |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )

    for variant in grid_display["variant"]:
        var_events = events[events["variant"] == variant]
        if not var_events.empty:
            tentate = len(var_events)
            effettive = len(var_events)
            utili = int(var_events["useful"].sum())
            inutili = effettive - utili
            wr = utili / effettive if effettive > 0 else 0.0
            lines.append(
                "| "
                f"{variant} | "
                f"{tentate} | "
                f"{effettive} | "
                f"{utili} | "
                f"{inutili} | "
                f"{_pct(wr)} |"
            )
        else:
            lines.append(f"| {variant} | 0 | 0 | 0 | 0 | n/a |")

    # Conclusioni automatiche basate sui criteri di accettazione
    lines.extend(
        [
            "",
            "## Conclusioni",
            "",
            "### Criteri di Accettazione:",
            "1. Sharpe Netto 0.25% **>= 1.050** (rispetto a 0.812 della baseline).",
            "2. Max Drawdown Netto **<= -52.57%** (non peggiora la baseline).",
            "3. Numero operazioni **<= 35**.",
            "4. Funzionalità positiva (Sharpe > 0) in almeno **3 sottoperiodi su 4**.",
            "5. Walk-Forward: Sharpe positivo in almeno **2 split su 3**.",
            "",
        ]
    )

    candidates = grid_sorted[~grid_sorted["variant"].isin(["baseline", "trailing_8_pure"])]
    if not candidates.empty:
        best_candidate = candidates.sort_values("net_025_sharpe_ratio", ascending=False).iloc[0]
        name = best_candidate["variant"]
        dd_val = best_candidate["net_025_max_drawdown"]
        sharpe_val = best_candidate["net_025_sharpe_ratio"]
        ops_val = best_candidate["num_operations"]
        pos_periods = int(best_candidate["pos_periods_count"])
        
        wf_pos_splits = int((wf["test_sharpe_ratio"] > 0).sum())

        lines.extend(
            [
                f"La variante migliore della griglia per Sharpe Netto è **{name}**:",
                f"- **Sharpe Netto 0.25%**: `{_ratio(sharpe_val)}` (Target: >= 1.050)",
                f"- **Max Drawdown Netto 0.25%**: `{_pct(dd_val)}` (Target: <= -52.57%)",
                f"- **Operazioni**: `{int(ops_val)}` (Target: <= 35)",
                f"- **Sottoperiodi Positivi**: `{pos_periods}/4` (Target: >= 3/4)",
                f"- **Split Walk-Forward Positivi**: `{wf_pos_splits}/3` (Target: >= 2/3)",
                "",
            ]
        )
        
        respects_dd = dd_val >= -0.525744
        respects_sharpe = sharpe_val >= 1.050
        respects_ops = ops_val <= 35
        respects_periods = pos_periods >= 3
        respects_wf = wf_pos_splits >= 2

        if respects_dd and respects_sharpe and respects_ops and respects_periods and respects_wf:
            lines.append("✔️ **La variante soddisfa TUTTI i criteri di accettazione ed è promossa come nuovo candidato principale.**")
        else:
            reasons = []
            if not respects_dd:
                reasons.append(f"drawdown netto peggiore della baseline ({_pct(dd_val)} > -52.57%)")
            if not respects_sharpe:
                reasons.append(f"Sharpe netto insufficiente ({_ratio(sharpe_val)} < 1.050)")
            if not respects_ops:
                reasons.append(f"troppe operazioni ({int(ops_val)} > 35)")
            if not respects_periods:
                reasons.append(f"insufficiente stabilità nei sottoperiodi ({pos_periods}/4)")
            if not respects_wf:
                reasons.append(f"insufficiente stabilità nel Walk-Forward ({wf_pos_splits}/3)")
            lines.append(f"⚠️ **La variante non soddisfa pienamente tutti i criteri per i seguenti motivi**: {', '.join(reasons)}.")
    else:
        lines.append("Nessun candidato trovato nella griglia.")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py`."
        )

    source = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).set_index("Date")
    last_date_str = source.index[-1].strftime("%Y-%m-%d")
    
    periods_def = {
        "2017-2020": ("2017-11-11", "2020-12-31"),
        "2021-2022": ("2021-01-01", "2022-12-31"),
        "2023-2026": ("2023-01-01", last_date_str),
        "2025-2026": ("2025-01-01", last_date_str),
    }

    variants_specs = [
        ("baseline", "baseline", None, None),
        ("trailing_8_pure", "trailing_8_pure", None, None),
    ]
    for rsi_th in [70, 75, 80]:
        for stop_str in [0.08, 0.10]:
            label = f"rsi_adaptive_system_rsi_{rsi_th}_stop_{int(stop_str * 100)}"
            variants_specs.append((label, "rsi_adaptive_system", rsi_th, stop_str))

    grid_rows: list[dict] = []
    period_rows: list[dict] = []
    event_frames: list[pd.DataFrame] = []
    
    variant_results: dict[str, tuple[pd.DataFrame, pd.DataFrame]] = {}

    for label, v_type, rsi_th, stop_str in variants_specs:
        frame, events = _simulate_trailing_rsi_system_frame(
            source,
            variant_type=v_type,
            soglia_rsi=rsi_th,
            stop_stretto=stop_str,
            label=label,
        )

        equity, gross, _ = run_backtest(frame)
        equity_net, net_025, _ = run_backtest(frame, transaction_cost_rate=0.0025)
        
        variant_results[label] = (equity_net, frame)

        # Calcola le metriche per sottoperiodi
        variant_period_metrics = []
        for period_name, (start, end) in periods_def.items():
            p_metrics = _period_metrics(equity_net, start, end)
            variant_period_metrics.append(p_metrics)
            period_rows.append(
                {
                    "variant": label,
                    "period": period_name,
                    **p_metrics,
                }
            )

        period_sharpes = [m["period_sharpe_ratio"] for m in variant_period_metrics if not pd.isna(m["period_sharpe_ratio"])]
        median_sharpe = float(np.median(period_sharpes)) if period_sharpes else float("nan")
        min_sharpe = float(np.min(period_sharpes)) if period_sharpes else float("nan")
        pos_periods_count = int(sum(1 for s in period_sharpes if s > 0))

        grid_rows.append(
            {
                "variant": label,
                "variant_type": v_type,
                "soglia_rsi": rsi_th,
                "stop_stretto": stop_str,
                "total_return": gross.total_return,
                "annualized_return": gross.annualized_return,
                "max_drawdown": gross.max_drawdown,
                "sharpe_ratio": gross.sharpe_ratio,
                "profit_factor": gross.profit_factor,
                "num_operations": gross.num_operations,
                "win_rate": gross.win_rate,
                "exposure_ratio": gross.exposure_ratio,
                "net_025_total_return": net_025.total_return,
                "net_025_annualized_return": net_025.annualized_return,
                "net_025_max_drawdown": net_025.max_drawdown,
                "net_025_sharpe_ratio": net_025.sharpe_ratio,
                "median_period_sharpe": median_sharpe,
                "min_period_sharpe": min_sharpe,
                "pos_periods_count": pos_periods_count,
            }
        )

        if not events.empty:
            event_frames.append(events)

    grid = pd.DataFrame(grid_rows)
    periods = pd.DataFrame(period_rows)
    events = pd.concat(event_frames, ignore_index=True) if event_frames else pd.DataFrame()

    # Walk-Forward Simulation
    wf_splits = [
        (1, "2017-11-11", "2020-12-31", "2021-01-01", "2022-12-31"),
        (2, "2017-11-11", "2022-12-31", "2023-01-01", "2024-12-31"),
        (3, "2017-11-11", "2024-12-31", "2025-01-01", last_date_str),
    ]
    
    wf_rows: list[dict] = []
    
    for split_id, train_start, train_end, test_start, test_end in wf_splits:
        best_variant = None
        best_train_sharpe = -9999.0
        
        for label, v_type, rsi_th, stop_str in variants_specs:
            if v_type not in ["rsi_adaptive_system"]:
                continue
            
            equity_net, _ = variant_results[label]
            train_subset = equity_net.loc[train_start:train_end]
            if len(train_subset) >= 2:
                train_sharpe = _sharpe(train_subset["DailyReturnStrategy"])
                if not pd.isna(train_sharpe) and train_sharpe > best_train_sharpe:
                    best_train_sharpe = train_sharpe
                    best_variant = label
        
        if best_variant is not None:
            equity_net, _ = variant_results[best_variant]
            test_metrics = _period_metrics(equity_net, test_start, test_end)
            
            wf_rows.append(
                {
                    "split": split_id,
                    "train_range": f"{train_start} -> {train_end}",
                    "test_range": f"{test_start} -> {test_end}",
                    "best_variant": best_variant,
                    "train_sharpe": best_train_sharpe,
                    "test_total_return": test_metrics["period_total_return"],
                    "test_annualized_return": test_metrics["period_annualized_return"],
                    "test_max_drawdown": test_metrics["period_max_drawdown"],
                    "test_sharpe_ratio": test_metrics["period_sharpe_ratio"],
                }
            )
        else:
            wf_rows.append(
                {
                    "split": split_id,
                    "train_range": f"{train_start} -> {train_end}",
                    "test_range": f"{test_start} -> {test_end}",
                    "best_variant": "none",
                    "train_sharpe": float("nan"),
                    "test_total_return": float("nan"),
                    "test_annualized_return": float("nan"),
                    "test_max_drawdown": float("nan"),
                    "test_sharpe_ratio": float("nan"),
                }
            )
            
    wf = pd.DataFrame(wf_rows)

    # Salva file CSV
    Path(OUT_GRID_CSV).parent.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUT_GRID_CSV, index=False)
    periods.to_csv(OUT_PERIOD_CSV, index=False)
    wf.to_csv(OUT_WF_CSV, index=False)
    events.to_csv(OUT_EVENTS_CSV, index=False)

    # Salva report Markdown
    _write_markdown(grid, periods, events, wf, OUT_MD)

    # Stampa tabella riepilogativa in console
    display_cols = [
        "variant",
        "net_025_annualized_return",
        "net_025_max_drawdown",
        "net_025_sharpe_ratio",
        "profit_factor",
        "num_operations",
        "median_period_sharpe",
        "min_period_sharpe",
        "pos_periods_count",
    ]
    
    ref_mask = grid["variant"].isin(["baseline", "trailing_8_pure"])
    refs = grid[ref_mask]
    others = grid[~ref_mask].sort_values(["net_025_sharpe_ratio", "sharpe_ratio"], ascending=False)
    print("\nRISULTATI SISTEMA DI USCITA ALTERNATIVO TRAILING 8% + RSI ADATTIVO (NETTI 0.25%):")
    print("-" * 140)
    print(pd.concat([refs, others], ignore_index=True)[display_cols].to_string(index=False))
    print("-" * 140)
    print(f"Grid CSV: {OUT_GRID_CSV}")
    print(f"Period CSV: {OUT_PERIOD_CSV}")
    print(f"Walk-Forward CSV: {OUT_WF_CSV}")
    print(f"Event CSV: {OUT_EVENTS_CSV}")
    print(f"Report: {OUT_MD}")


if __name__ == "__main__":
    main()
