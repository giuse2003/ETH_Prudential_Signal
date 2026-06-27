"""
Analisi sperimentale del trailing stop adattivo RSI a tre livelli.

Questo script non modifica i segnali ufficiali. Forza VENDI solo nel frame di
backtest in base alla distanza dalla SMA200 e all'RSI corrente.
L'esecuzione dello stop avviene esclusivamente sulla chiusura giornaliera (Close).
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
OUT_GRID_CSV = PROJECT_ROOT / "reports" / "rsi_adaptive_trailing_grid.csv"
OUT_PERIOD_CSV = PROJECT_ROOT / "reports" / "rsi_adaptive_trailing_periods.csv"
OUT_EVENTS_CSV = PROJECT_ROOT / "reports" / "rsi_adaptive_trailing_event_analysis.csv"
OUT_MD = PROJECT_ROOT / "reports" / "rsi_adaptive_trailing_results.md"


def _simulate_rsi_adaptive_trailing_stop_frame(
    df: pd.DataFrame,
    *,
    variant_type: str,  # "baseline", "dynamic_15_8", or "rsi_adaptive"
    soglia_rsi: float | None = None,
    stop_stretto: float | None = None,
    label: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    out = df[["Close", "Segnale"]].copy()

    if variant_type == "baseline":
        return out, pd.DataFrame(columns=[
            "variant", "date", "close", "peak_close", "stop_pct", "stop_level",
            "drawdown_from_peak", "rsi", "dist_sma200", "momentum_7d", "volume_rel",
            "confirmed", "useful", "next_buy_date", "next_buy_close", "next_buy_pct"
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
            
            # Determina la percentuale di trailing stop
            if variant_type == "dynamic_15_8":
                if dist_sma200 > 60.0:
                    stop_pct = 0.15
                else:
                    stop_pct = 0.08
            elif variant_type == "rsi_adaptive":
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
                # Calcola conferme momentum/volume
                momentum_7d = float(row["Close"] / row["Close_7d_ago"] - 1.0) if pd.notna(row.get("Close_7d_ago")) else 0.0
                volume_rel = float(row["Volume"] / row["VolumeAvg20"] - 1.0) if pd.notna(row.get("VolumeAvg20")) and float(row.get("VolumeAvg20", 1.0)) != 0.0 else 0.0
                
                momentum_ok = momentum_7d >= -0.05
                volume_ok = volume_rel >= 0.10
                confirmed = momentum_ok and volume_ok

                # Calcola utilità dell'uscita basandosi sul prossimo ACQUISTA ufficiale
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
                        "stop_pct": stop_pct,
                        "stop_level": stop_level,
                        "drawdown_from_peak": close / peak_close - 1.0,
                        "rsi": rsi,
                        "dist_sma200": dist_sma200,
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
                else:
                    signal = "MANTIENI"
            else:
                signal = "MANTIENI"

        signals.append(signal)

    out["Segnale"] = signals
    if not events:
        columns = [
            "variant", "date", "close", "peak_close", "stop_pct", "stop_level",
            "drawdown_from_peak", "rsi", "dist_sma200", "momentum_7d", "volume_rel",
            "confirmed", "useful", "next_buy_date", "next_buy_close", "next_buy_pct"
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
    out_path: Path,
) -> None:
    # Ordina varianti
    grid_sorted = grid.copy()
    # Metti baseline e trail_dynamic_15_8 in testa per riferimento, seguiti dalle altre varianti per Sharpe
    ref_mask = grid_sorted["variant"].isin(["baseline", "trail_dynamic_15_8"])
    refs = grid_sorted[ref_mask]
    others = grid_sorted[~ref_mask].sort_values(["net_025_sharpe_ratio", "sharpe_ratio"], ascending=False)
    grid_display = pd.concat([refs, others], ignore_index=True)

    lines = [
        "# RSI Adaptive Trailing Stop Experiment Results",
        "",
        "Questi risultati sono frutto di test sperimentali di ricerca e non modificano la strategia ufficiale.",
        "La verifica dello stop avviene esclusivamente sulla chiusura giornaliera (Close).",
        "",
        "## Metriche Periodo Completo",
        "",
        "| Variante | Ann. Lordo | Max DD Lordo | Sharpe Lordo | Sharpe Netto 0,25% | PF | Operazioni | Mediana Sharpe | Min Sharpe |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
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
            f"{_ratio(row['min_period_sharpe'])} |"
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
    # Ordina le righe nello stesso ordine della griglia
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

    # Analisi Eventi Uscita
    lines.extend(
        [
            "",
            "## Analisi degli Eventi di Uscita",
            "",
            "La tabella seguente mostra il numero di uscite tentate (prezzo sotto stop level), quante sono state effettivamente confermate da momentum/volume e quante di queste si sono rivelate utili (riacquisto a prezzo inferiore).",
            "",
            "| Variante | Uscite Tentate | Uscite Confermate | Di cui Utili | Di cui Inutili | Win Rate Uscite |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )

    for variant in grid_display["variant"]:
        var_events = events[events["variant"] == variant]
        if not var_events.empty:
            tentate = len(var_events)
            confermate = int(var_events["confirmed"].sum())
            utili = int((var_events["confirmed"] & var_events["useful"]).sum())
            inutili = confermate - utili
            wr = utili / confermate if confermate > 0 else 0.0
            lines.append(
                "| "
                f"{variant} | "
                f"{tentate} | "
                f"{confermate} | "
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
            "1. Riduzione del Max Drawdown sotto **-52.57%** (baseline) o almeno sotto **-56.50%** (candidato precedente).",
            "2. Sharpe Netto 0.25% **>= 1.050**.",
            "3. Numero operazioni **<= 30**.",
            "4. Funzionalità positiva (Sharpe > 0) in almeno **3 sottoperiodi su 4**.",
            "",
        ]
    )

    # Trova la migliore variante (escluse baseline e trail_dynamic_15_8)
    candidates = grid_sorted[~grid_sorted["variant"].isin(["baseline", "trail_dynamic_15_8"])]
    if not candidates.empty:
        best_candidate = candidates.sort_values("net_025_sharpe_ratio", ascending=False).iloc[0]
        name = best_candidate["variant"]
        dd_val = best_candidate["net_025_max_drawdown"] # Usa max drawdown netto per verificare contro i criteri di accettazione
        sharpe_val = best_candidate["net_025_sharpe_ratio"]
        ops_val = best_candidate["num_operations"]
        
        # Sottoperiodi positivi
        cand_periods = periods[periods["variant"] == name]
        pos_periods = int((cand_periods["period_sharpe_ratio"] > 0).sum())
        total_periods = len(cand_periods)

        lines.extend(
            [
                f"La variante migliore della griglia per Sharpe Netto è **{name}**:",
                f"- **Sharpe Netto 0.25%**: `{_ratio(sharpe_val)}` (Target: >= 1.050)",
                f"- **Max Drawdown Netto 0.25%**: `{_pct(dd_val)}` (Target: < -56.50% o < -52.57%)",
                f"- **Operazioni**: `{int(ops_val)}` (Target: <= 30)",
                f"- **Sottoperiodi Positivi**: `{pos_periods}/{total_periods}` (Target: >= 3/4)",
                "",
            ]
        )
        
        # Verifica se rispetta i criteri
        # Criteri: DD sotto -52.57% (baseline) o almeno sotto -56.50% (candidato precedente).
        respects_dd = dd_val > -0.5650
        respects_sharpe = sharpe_val >= 1.050
        respects_ops = ops_val <= 30
        respects_periods = pos_periods >= 3

        if respects_dd and respects_sharpe and respects_ops and respects_periods:
            lines.append("✔️ **La variante soddisfa TUTTI i criteri di accettazione ed è promossa come nuovo candidato principale.**")
        else:
            reasons = []
            if not respects_dd:
                reasons.append(f"drawdown netto troppo elevato ({_pct(dd_val)})")
            if not respects_sharpe:
                reasons.append(f"Sharpe netto insufficiente ({_ratio(sharpe_val)})")
            if not respects_ops:
                reasons.append(f"troppe operazioni ({int(ops_val)})")
            if not respects_periods:
                reasons.append(f"insufficiente stabilità nei sottoperiodi ({pos_periods}/{total_periods})")
            lines.append(f"⚠️ **La variante non soddisfa pienamente tutti i criteri per i seguenti motivi**: {', '.join(reasons)}.")
    else:
        lines.append("Nessun candidato trovato nella griglia.")

    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`."
        )

    source = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).set_index("Date")
    last_date_str = source.index[-1].strftime("%Y-%m-%d")
    
    periods_def = {
        "2017-2020": ("2017-11-11", "2020-12-31"),
        "2021-2022": ("2021-01-01", "2022-12-31"),
        "2023-2026": ("2023-01-01", last_date_str),
        "2025-2026": ("2025-01-01", last_date_str),
    }

    # Definisci le specifiche delle varianti
    variants_specs = [
        # (label, type, soglia_rsi, stop_stretto)
        ("baseline", "baseline", None, None),
        ("trail_dynamic_15_8", "dynamic_15_8", None, None),
    ]
    for rsi_th in [70, 75, 80]:
        for stop_str in [0.08, 0.10]:
            label = f"rsi_adaptive_rsi_{rsi_th}_stop_{int(stop_str * 100)}"
            variants_specs.append((label, "rsi_adaptive", rsi_th, stop_str))

    grid_rows: list[dict] = []
    period_rows: list[dict] = []
    event_frames: list[pd.DataFrame] = []

    for label, v_type, rsi_th, stop_str in variants_specs:
        frame, events = _simulate_rsi_adaptive_trailing_stop_frame(
            source,
            variant_type=v_type,
            soglia_rsi=rsi_th,
            stop_stretto=stop_str,
            label=label,
        )

        equity, gross, _ = run_backtest(frame)
        _, net_025, _ = run_backtest(frame, transaction_cost_rate=0.0025)

        # Calcola le metriche per sottoperiodi
        variant_period_metrics = []
        for period_name, (start, end) in periods_def.items():
            p_metrics = _period_metrics(equity, start, end)
            variant_period_metrics.append(p_metrics)
            period_rows.append(
                {
                    "variant": label,
                    "period": period_name,
                    **p_metrics,
                }
            )

        # Calcola stabilità nei sottoperiodi
        period_sharpes = [m["period_sharpe_ratio"] for m in variant_period_metrics if not pd.isna(m["period_sharpe_ratio"])]
        median_sharpe = float(np.median(period_sharpes)) if period_sharpes else float("nan")
        min_sharpe = float(np.min(period_sharpes)) if period_sharpes else float("nan")

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
            }
        )

        if not events.empty:
            event_frames.append(events)

    grid = pd.DataFrame(grid_rows)
    periods = pd.DataFrame(period_rows)
    events = pd.concat(event_frames, ignore_index=True) if event_frames else pd.DataFrame()

    # Salva file CSV
    OUT_GRID_CSV.parent.mkdir(parents=True, exist_ok=True)
    grid.to_csv(OUT_GRID_CSV, index=False)
    periods.to_csv(OUT_PERIOD_CSV, index=False)
    events.to_csv(OUT_EVENTS_CSV, index=False)

    # Salva report Markdown
    _write_markdown(grid, periods, events, OUT_MD)

    # Stampa tabella riepilogativa in console
    display_cols = [
        "variant",
        "annualized_return",
        "max_drawdown",
        "sharpe_ratio",
        "net_025_sharpe_ratio",
        "profit_factor",
        "num_operations",
        "median_period_sharpe",
        "min_period_sharpe",
    ]
    
    # Ordina per mostrare i risultati ordinati
    ref_mask = grid["variant"].isin(["baseline", "trail_dynamic_15_8"])
    refs = grid[ref_mask]
    others = grid[~ref_mask].sort_values(["net_025_sharpe_ratio", "sharpe_ratio"], ascending=False)
    print("\nRISULTATI ESPERIMENTI ADATTIVI RSI:")
    print("-" * 140)
    print(pd.concat([refs, others], ignore_index=True)[display_cols].to_string(index=False))
    print("-" * 140)
    print(f"Grid CSV: {OUT_GRID_CSV}")
    print(f"Period CSV: {OUT_PERIOD_CSV}")
    print(f"Event CSV: {OUT_EVENTS_CSV}")
    print(f"Report: {OUT_MD}")


if __name__ == "__main__":
    main()
