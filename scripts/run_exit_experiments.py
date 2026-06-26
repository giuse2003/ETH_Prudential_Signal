"""
Test sperimentali di uscite protettive.

Questo script non modifica i segnali ufficiali. Crea varianti di backtest in cui
alcune condizioni forzano un segnale VENDI solo nel frame sperimentale.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backtest.backtest import BacktestMetrics, run_backtest


SOURCE_CSV = PROJECT_ROOT / "data" / "indicators_with_signals.csv"
OUT_CSV = PROJECT_ROOT / "reports" / "exit_experiment_results.csv"
OUT_MD = PROJECT_ROOT / "reports" / "exit_experiment_results.md"


def _force_exit_frame(df: pd.DataFrame, condition: pd.Series) -> pd.DataFrame:
    out = df[["Close", "Segnale"]].copy()
    out.loc[condition.fillna(False), "Segnale"] = "VENDI"
    return out


def _trailing_stop_frame(df: pd.DataFrame, stop_pct: float) -> pd.DataFrame:
    out = df[["Close", "Segnale"]].copy()
    exposure = 0.0
    peak: float | None = None
    signals: list[str] = []

    for _, row in df.iterrows():
        signal = str(row["Segnale"])
        close = float(row["Close"])

        if signal == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            peak = close if peak is None else max(peak, close)
        elif signal == "ACQUISTA":
            exposure = 1.0
            peak = close if peak is None else max(peak, close)
        elif signal == "VENDI":
            exposure = 0.0
            peak = None
        elif exposure > 0.0 and peak is not None:
            peak = max(peak, close)
            if close <= peak * (1.0 - stop_pct):
                signal = "VENDI"
                exposure = 0.0
                peak = None

        signals.append(signal)

    out["Segnale"] = signals
    return out


def _entry_loss_stop_frame(df: pd.DataFrame, stop_pct: float) -> pd.DataFrame:
    out = df[["Close", "Segnale"]].copy()
    exposure = 0.0
    entry: float | None = None
    signals: list[str] = []

    for _, row in df.iterrows():
        signal = str(row["Segnale"])
        close = float(row["Close"])

        if signal == "ACQUISTA" and exposure <= 0.0:
            exposure = 1.0
            entry = close
        elif signal == "ACQUISTA":
            exposure = 1.0
        elif signal == "VENDI":
            exposure = 0.0
            entry = None
        elif exposure > 0.0 and entry is not None:
            if close <= entry * (1.0 - stop_pct):
                signal = "VENDI"
                exposure = 0.0
                entry = None

        signals.append(signal)

    out["Segnale"] = signals
    return out


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _row(
    *,
    variant: str,
    description: str,
    gross: BacktestMetrics,
    net_025: BacktestMetrics,
    baseline: BacktestMetrics,
) -> dict:
    return {
        "variant": variant,
        "description": description,
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
        "delta_drawdown_vs_baseline": gross.max_drawdown - baseline.max_drawdown,
        "delta_annualized_vs_baseline": gross.annualized_return - baseline.annualized_return,
        "delta_sharpe_vs_baseline": gross.sharpe_ratio - baseline.sharpe_ratio,
    }


def _variant_frames(df: pd.DataFrame) -> dict[str, tuple[str, pd.DataFrame]]:
    base = df[["Close", "Segnale"]].copy()
    close = df["Close"]
    sma50 = df["SMA50"]
    sma200 = df["SMA200"]
    rsi = df["RSI"]
    volume = df["Volume"]
    volume_avg20 = df["VolumeAvg20"]
    momentum_close = df["Close_7d_ago"]
    atr_pct = df["ATR"] / df["Close"]

    conditions: dict[str, tuple[str, pd.Series]] = {
        "exit_close_below_sma50_1d": (
            "Forza VENDI appena Close scende sotto SMA50, senza attendere 2 giorni.",
            close < sma50,
        ),
        "exit_close_below_sma50_and_rsi_lt45": (
            "Forza VENDI se Close < SMA50 e RSI < 45.",
            (close < sma50) & (rsi < 45),
        ),
        "exit_close_below_sma50_and_rsi_lt40": (
            "Forza VENDI se Close < SMA50 e RSI < 40.",
            (close < sma50) & (rsi < 40),
        ),
        "exit_close_below_sma50_and_momentum_negative": (
            "Forza VENDI se Close < SMA50 e Close < Close di 7 giorni fa.",
            (close < sma50) & (close < momentum_close),
        ),
        "exit_close_below_sma50_and_volume_high": (
            "Forza VENDI se Close < SMA50 con volume sopra media 20 giorni.",
            (close < sma50) & (volume > volume_avg20),
        ),
        "exit_close_below_sma50_and_sma50_falling_5d": (
            "Forza VENDI se Close < SMA50 e SMA50 scende da 5 giorni.",
            (close < sma50) & (sma50 < sma50.shift(5)),
        ),
        "exit_close_below_sma50_and_sma50_falling_10d": (
            "Forza VENDI se Close < SMA50 e SMA50 scende da 10 giorni.",
            (close < sma50) & (sma50 < sma50.shift(10)),
        ),
        "exit_rsi_lt45": ("Forza VENDI se RSI < 45.", rsi < 45),
        "exit_rsi_lt40": ("Forza VENDI se RSI < 40.", rsi < 40),
        "exit_rsi_lt35": ("Forza VENDI se RSI < 35.", rsi < 35),
        "exit_close_below_sma200": ("Forza VENDI se Close < SMA200.", close < sma200),
        "exit_atr_pct_gt8": ("Forza VENDI se ATR/Close > 8%.", atr_pct > 0.08),
        "exit_atr_pct_gt10": ("Forza VENDI se ATR/Close > 10%.", atr_pct > 0.10),
        "exit_below_sma50_or_momentum_negative": (
            "Forza VENDI se Close < SMA50 oppure momentum 7 giorni negativo.",
            (close < sma50) | (close < momentum_close),
        ),
        "exit_below_sma50_or_rsi_lt35": (
            "Forza VENDI se Close < SMA50 oppure RSI < 35.",
            (close < sma50) | (rsi < 35),
        ),
        "exit_below_sma50_and_rsi_lt45_or_atr_gt8": (
            "Forza VENDI su Close < SMA50 e RSI < 45, oppure ATR/Close > 8%.",
            ((close < sma50) & (rsi < 45)) | (atr_pct > 0.08),
        ),
    }

    variants = {"baseline": ("Segnali ufficiali invariati.", base)}
    variants.update(
        {
            name: (description, _force_exit_frame(df, condition))
            for name, (description, condition) in conditions.items()
        }
    )

    for stop in [0.08, 0.10, 0.12, 0.15, 0.20, 0.25]:
        pct = int(stop * 100)
        variants[f"trailing_stop_{pct}pct"] = (
            f"Forza VENDI se Close perde {pct}% dal massimo del trade.",
            _trailing_stop_frame(df, stop),
        )
        variants[f"entry_loss_stop_{pct}pct"] = (
            f"Forza VENDI se Close perde {pct}% dal prezzo di ingresso.",
            _entry_loss_stop_frame(df, stop),
        )

    return variants


def _write_markdown(results: pd.DataFrame, out_path: Path) -> None:
    by_drawdown = results.sort_values(["max_drawdown", "annualized_return"], ascending=[False, False]).head(10)
    by_sharpe = results.sort_values(["sharpe_ratio", "annualized_return"], ascending=False).head(10)
    baseline = results.loc[results["variant"] == "baseline"].iloc[0]

    lines = [
        "# Exit Experiment Results",
        "",
        "Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.",
        "",
        "Le varianti forzano `VENDI` solo nel frame sperimentale del backtest.",
        "",
        "## Baseline",
        "",
        f"- Annualizzato: {_pct(baseline['annualized_return'])}",
        f"- Max drawdown: {_pct(baseline['max_drawdown'])}",
        f"- Sharpe: {_ratio(baseline['sharpe_ratio'])}",
        f"- Profit factor: {_ratio(baseline['profit_factor'])}",
        "",
        "## Migliori Varianti Per Drawdown",
        "",
        "| Variante | Ann. | Max DD | Delta DD | Sharpe | Profit factor | Operazioni | Net 0,25% DD |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in by_drawdown.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_pct(row['delta_drawdown_vs_baseline'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{_pct(row['net_025_max_drawdown'])} |"
        )

    lines.extend(
        [
            "",
            "## Migliori Varianti Per Sharpe",
            "",
            "| Variante | Ann. | Max DD | Sharpe | Delta Sharpe | Profit factor | Operazioni |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in by_sharpe.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['delta_sharpe_vs_baseline'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} |"
        )

    best_dd = by_drawdown.iloc[0]
    best_signal = results.loc[results["variant"] == "exit_close_below_sma50_1d"].iloc[0]
    best_stop = results.loc[results["variant"] == "entry_loss_stop_8pct"].iloc[0]
    lines.extend(
        [
            "",
            "## Sintesi",
            "",
            f"- Miglior drawdown assoluto: `{best_dd['variant']}` con max DD "
            f"{_pct(best_dd['max_drawdown'])}, ma rendimento annuo "
            f"{_pct(best_dd['annualized_return'])}.",
            f"- Miglior segnale tecnico semplice: `exit_close_below_sma50_1d`, "
            f"max DD {_pct(best_signal['max_drawdown'])}, ann. "
            f"{_pct(best_signal['annualized_return'])}, Sharpe "
            f"{_ratio(best_signal['sharpe_ratio'])}.",
            f"- Miglior stop sul prezzo di ingresso: `entry_loss_stop_8pct`, "
            f"max DD {_pct(best_stop['max_drawdown'])}, ann. "
            f"{_pct(best_stop['annualized_return'])}, Sharpe "
            f"{_ratio(best_stop['sharpe_ratio'])}.",
            "",
            "Nessuna variante viene promossa a regola operativa in questa fase.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`."
        )

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).set_index("Date")
    variants = _variant_frames(df)
    _, baseline_metrics, _ = run_backtest(variants["baseline"][1])

    rows: list[dict] = []
    for name, (description, frame) in variants.items():
        _, gross, _ = run_backtest(frame)
        _, net_025, _ = run_backtest(frame, transaction_cost_rate=0.0025)
        rows.append(
            _row(
                variant=name,
                description=description,
                gross=gross,
                net_025=net_025,
                baseline=baseline_metrics,
            )
        )

    results = pd.DataFrame(rows).sort_values(
        ["max_drawdown", "annualized_return"],
        ascending=[False, False],
    )
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_CSV, index=False)
    _write_markdown(results, OUT_MD)

    display_cols = [
        "variant",
        "annualized_return",
        "max_drawdown",
        "sharpe_ratio",
        "profit_factor",
        "num_operations",
        "net_025_max_drawdown",
    ]
    print(results[display_cols].head(15).to_string(index=False))
    print("")
    print(f"CSV: {OUT_CSV}")
    print(f"Report: {OUT_MD}")


if __name__ == "__main__":
    main()
