"""
Esegue test sperimentali sui segnali senza modificare le regole operative.

Le varianti sono filtri di ingresso: quando il segnale ufficiale e' ACQUISTA
ma il filtro sperimentale non passa, il segnale usato solo nel backtest diventa
MANTIENI. I segnali ufficiali salvati dalla pipeline non vengono modificati.
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
OUT_CSV = PROJECT_ROOT / "reports" / "model_experiment_results.csv"
OUT_MD = PROJECT_ROOT / "reports" / "model_experiment_results.md"


def _entry_filter_frame(df: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    """
    Applica un filtro solo agli ingressi sperimentali.

    ACQUISTA bloccato diventa MANTIENI, quindi:
    - se la strategia era fuori mercato, resta fuori;
    - se era gia' dentro, mantiene l'esposizione fino al prossimo VENDI.
    """
    out = df[["Close", "Segnale"]].copy()
    blocked_buy = (out["Segnale"] == "ACQUISTA") & (~mask.fillna(False))
    out.loc[blocked_buy, "Segnale"] = "MANTIENI"
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
        "delta_sharpe_vs_baseline": gross.sharpe_ratio - baseline.sharpe_ratio,
        "delta_annualized_vs_baseline": gross.annualized_return - baseline.annualized_return,
        "delta_drawdown_vs_baseline": gross.max_drawdown - baseline.max_drawdown,
    }


def _variant_frames(df: pd.DataFrame) -> dict[str, tuple[str, pd.DataFrame]]:
    base = df[["Close", "Segnale"]].copy()
    atr_pct = df["ATR"] / df["Close"]
    vol20 = df["Close"].pct_change().rolling(20, min_periods=20).std()

    filters: dict[str, tuple[str, pd.Series]] = {
        "atr_close_le_5pct": ("Blocca nuovi ACQUISTA se ATR/Close > 5%.", atr_pct <= 0.05),
        "atr_close_le_7pct": ("Blocca nuovi ACQUISTA se ATR/Close > 7%.", atr_pct <= 0.07),
        "vol20_le_p75": (
            "Blocca nuovi ACQUISTA se volatilita' rolling 20g sopra percentile 75.",
            vol20 <= vol20.quantile(0.75),
        ),
        "vol20_le_p85": (
            "Blocca nuovi ACQUISTA se volatilita' rolling 20g sopra percentile 85.",
            vol20 <= vol20.quantile(0.85),
        ),
        "sma200_rising_10d": (
            "Blocca nuovi ACQUISTA se SMA200 non cresce rispetto a 10 giorni prima.",
            df["SMA200"] > df["SMA200"].shift(10),
        ),
        "sma200_rising_20d": (
            "Blocca nuovi ACQUISTA se SMA200 non cresce rispetto a 20 giorni prima.",
            df["SMA200"] > df["SMA200"].shift(20),
        ),
        "sma50_rising_10d": (
            "Blocca nuovi ACQUISTA se SMA50 non cresce rispetto a 10 giorni prima.",
            df["SMA50"] > df["SMA50"].shift(10),
        ),
        "close_gt_sma200_2pct": (
            "Blocca nuovi ACQUISTA se Close non supera SMA200 almeno del 2%.",
            df["Close"] > df["SMA200"] * 1.02,
        ),
        "close_gt_sma200_5pct": (
            "Blocca nuovi ACQUISTA se Close non supera SMA200 almeno del 5%.",
            df["Close"] > df["SMA200"] * 1.05,
        ),
        "atr7_and_sma200_10d": (
            "Combina ATR/Close <= 7% e SMA200 crescente a 10 giorni.",
            (atr_pct <= 0.07) & (df["SMA200"] > df["SMA200"].shift(10)),
        ),
        "atr5_and_sma200_20d": (
            "Combina ATR/Close <= 5% e SMA200 crescente a 20 giorni.",
            (atr_pct <= 0.05) & (df["SMA200"] > df["SMA200"].shift(20)),
        ),
    }

    variants = {"baseline": ("Segnali ufficiali invariati.", base)}
    variants.update(
        {
            name: (description, _entry_filter_frame(df, mask))
            for name, (description, mask) in filters.items()
        }
    )
    return variants


def _write_markdown(results: pd.DataFrame, out_path: Path) -> None:
    top = results.sort_values(["sharpe_ratio", "annualized_return"], ascending=False).head(8)
    lines = [
        "# Model Experiment Results",
        "",
        "Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.",
        "",
        "Le varianti applicano filtri solo ai nuovi ingressi `ACQUISTA`; i segnali",
        "`VENDI` ufficiali restano invariati.",
        "",
        "## Top Variants By Sharpe",
        "",
        "| Variante | Ann. | Max DD | Sharpe | Profit factor | Operazioni | Net 0,25% Sharpe |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in top.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['annualized_return'])} | "
            f"{_pct(row['max_drawdown'])} | "
            f"{_ratio(row['sharpe_ratio'])} | "
            f"{_ratio(row['profit_factor'])} | "
            f"{int(row['num_operations'])} | "
            f"{_ratio(row['net_025_sharpe_ratio'])} |"
        )

    baseline = results.loc[results["variant"] == "baseline"].iloc[0]
    best = top.iloc[0]
    lines.extend(
        [
            "",
            "## Sintesi",
            "",
            f"- Baseline Sharpe: {_ratio(baseline['sharpe_ratio'])}.",
            f"- Migliore variante testata: `{best['variant']}` con Sharpe "
            f"{_ratio(best['sharpe_ratio'])}.",
            f"- Delta Sharpe migliore vs baseline: "
            f"{_ratio(best['delta_sharpe_vs_baseline'])}.",
            "",
            "Conclusione: i filtri testati non risolvono ancora lo Sharpe sotto 1.",
            "Il filtro ATR/Close <= 7% migliora marginalmente la baseline; i filtri",
            "su SMA200 crescente riducono troppo il rendimento.",
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
        ["sharpe_ratio", "annualized_return"],
        ascending=False,
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
        "net_025_sharpe_ratio",
    ]
    print(results[display_cols].to_string(index=False))
    print("")
    print(f"CSV: {OUT_CSV}")
    print(f"Report: {OUT_MD}")


if __name__ == "__main__":
    main()
