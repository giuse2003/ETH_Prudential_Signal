"""
Test ipotesi filtri di ingresso derivate dall'analisi dei trade.

Questo script non modifica i segnali ufficiali. Blocca in modo sperimentale
alcuni segnali ACQUISTA e confronta le varianti contro la Baseline.

Le performance sono misurate in EUR tramite Close_EUR.
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
OUT_CSV = PROJECT_ROOT / "reports" / "entry_filter_hypotheses.csv"
OUT_MD = PROJECT_ROOT / "reports" / "entry_filter_hypotheses.md"

RECENT_START = "2022-01-01"


def _entry_filter_frame(df: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    out = df[["Close_EUR", "Segnale"]].rename(columns={"Close_EUR": "Close"}).copy()
    blocked_buy = (out["Segnale"] == "ACQUISTA") & (~mask.fillna(False))
    out.loc[blocked_buy, "Segnale"] = "MANTIENI"
    return out


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


def _slice_metrics(equity: pd.DataFrame, start: str) -> dict[str, float]:
    subset = equity.loc[start:].copy()
    normalized = subset["EquityStrategy"] / float(subset["EquityStrategy"].iloc[0])
    daily_returns = normalized.pct_change()
    n_days = max((subset.index[-1] - subset.index[0]).days, 1)
    total_return = float(normalized.iloc[-1] - 1.0)
    annualized_return = float((1.0 + total_return) ** (CFG.periods_per_year / n_days) - 1.0)
    return {
        "recent_total_return": total_return,
        "recent_annualized_return": annualized_return,
        "recent_max_drawdown": _max_drawdown(normalized),
        "recent_sharpe_ratio": _sharpe(daily_returns),
        "recent_exposure_ratio": float(subset["EffectiveExposure"].gt(0.0).mean()),
        "recent_turnover": float(subset["Turnover"].sum()),
    }


def _variants(df: pd.DataFrame) -> dict[str, tuple[str, pd.DataFrame]]:
    dist_sma200 = df["Close"] / df["SMA200"] - 1.0
    volume_rel = df["Volume"] / df["VolumeAvg20"] - 1.0
    momentum_7d = df["Close"] / df["Close_7d_ago"] - 1.0
    position_52w = (df["Close"] - df["Low52w"]) / (df["High52w"] - df["Low52w"])

    masks: dict[str, tuple[str, pd.Series]] = {
        "baseline": ("Segnali ufficiali invariati.", pd.Series(True, index=df.index)),
        "rsi_le_65": ("Blocca ACQUISTA se RSI > 65.", df["RSI"] <= 65),
        "rsi_le_62": ("Blocca ACQUISTA se RSI > 62.", df["RSI"] <= 62),
        "dist_sma200_le_30": ("Blocca ACQUISTA se Close dista oltre +30% da SMA200.", dist_sma200 <= 0.30),
        "dist_sma200_le_25": ("Blocca ACQUISTA se Close dista oltre +25% da SMA200.", dist_sma200 <= 0.25),
        "vol_rel_le_100": ("Blocca ACQUISTA se volume relativo > +100%.", volume_rel <= 1.00),
        "vol_rel_le_60": ("Blocca ACQUISTA se volume relativo > +60%.", volume_rel <= 0.60),
        "mom7_le_8": ("Blocca ACQUISTA se momentum 7g > +8%.", momentum_7d <= 0.08),
        "mom7_le_6": ("Blocca ACQUISTA se momentum 7g > +6%.", momentum_7d <= 0.06),
        "pos52_le_85": ("Blocca ACQUISTA se posizione nel range 52w > 85%.", position_52w <= 0.85),
        "rsi65_dist30": (
            "Combina RSI <= 65 e distanza da SMA200 <= +30%.",
            (df["RSI"] <= 65) & (dist_sma200 <= 0.30),
        ),
        "rsi65_dist30_vol100": (
            "Combina RSI <= 65, distanza SMA200 <= +30%, volume relativo <= +100%.",
            (df["RSI"] <= 65) & (dist_sma200 <= 0.30) & (volume_rel <= 1.00),
        ),
        "rsi65_dist30_mom7_8": (
            "Combina RSI <= 65, distanza SMA200 <= +30%, momentum 7g <= +8%.",
            (df["RSI"] <= 65) & (dist_sma200 <= 0.30) & (momentum_7d <= 0.08),
        ),
        "dist30_mom7_8_vol100": (
            "Combina distanza SMA200 <= +30%, momentum 7g <= +8%, volume relativo <= +100%.",
            (dist_sma200 <= 0.30) & (momentum_7d <= 0.08) & (volume_rel <= 1.00),
        ),
    }

    return {name: (description, _entry_filter_frame(df, mask)) for name, (description, mask) in masks.items()}


def _pct(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value * 100:.2f}%"


def _ratio(value: float | None) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{value:.3f}"


def _write_markdown(results: pd.DataFrame, out_path: Path) -> None:
    baseline = results.loc[results["variant"] == "baseline"].iloc[0]
    recent_sorted = results.sort_values(["recent_sharpe_ratio", "recent_annualized_return"], ascending=False)
    full_sorted = results.sort_values(["full_sharpe_ratio", "full_annualized_return"], ascending=False)

    lines = [
        "# Entry Filter Hypotheses",
        "",
        "Questi risultati sono solo test di ricerca. Non modificano i segnali ufficiali.",
        "",
        "Le performance sono misurate in EUR con `Close_EUR`; gli indicatori e i segnali",
        "sono quelli ufficiali della Baseline.",
        "",
        "## Periodo 2022-Oggi",
        "",
        "| Variante | Ann. | Max DD | Sharpe | Esposizione | Turnover |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in recent_sorted.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['recent_annualized_return'])} | "
            f"{_pct(row['recent_max_drawdown'])} | "
            f"{_ratio(row['recent_sharpe_ratio'])} | "
            f"{_pct(row['recent_exposure_ratio'])} | "
            f"{int(row['recent_turnover'])} |"
        )

    lines.extend(
        [
            "",
            "## Periodo Completo",
            "",
            "| Variante | Ann. | Max DD | Sharpe | PF | Operazioni |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for _, row in full_sorted.iterrows():
        lines.append(
            "| "
            f"{row['variant']} | "
            f"{_pct(row['full_annualized_return'])} | "
            f"{_pct(row['full_max_drawdown'])} | "
            f"{_ratio(row['full_sharpe_ratio'])} | "
            f"{_ratio(row['full_profit_factor'])} | "
            f"{int(row['full_num_operations'])} |"
        )

    best_recent = recent_sorted.iloc[0]
    lines.extend(
        [
            "",
            "## Lettura",
            "",
            f"- Baseline 2022-oggi: ann. {_pct(baseline['recent_annualized_return'])}, "
            f"max DD {_pct(baseline['recent_max_drawdown'])}, Sharpe {_ratio(baseline['recent_sharpe_ratio'])}.",
            f"- Migliore ipotesi 2022-oggi: `{best_recent['variant']}` con ann. "
            f"{_pct(best_recent['recent_annualized_return'])}, max DD "
            f"{_pct(best_recent['recent_max_drawdown'])}, Sharpe {_ratio(best_recent['recent_sharpe_ratio'])}.",
            "- Le ipotesi migliori sul periodo recente tagliano pero' troppo rendimento sul periodo completo.",
            "- Nessuna ipotesi va promossa: servono test annuali, costi e verifica che i grandi trade non vengano eliminati.",
            "",
        ]
    )
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    if not SOURCE_CSV.exists():
        raise FileNotFoundError(
            f"File mancante: {SOURCE_CSV}. Esegui prima `python main.py --force-download`."
        )

    df = pd.read_csv(SOURCE_CSV, parse_dates=["Date"]).sort_values("Date").set_index("Date")
    rows: list[dict[str, float | int | str]] = []

    for name, (description, frame) in _variants(df).items():
        equity, metrics, _ = run_backtest(frame)
        row = {
            "variant": name,
            "description": description,
            "full_total_return": metrics.total_return,
            "full_annualized_return": metrics.annualized_return,
            "full_max_drawdown": metrics.max_drawdown,
            "full_sharpe_ratio": metrics.sharpe_ratio,
            "full_profit_factor": metrics.profit_factor,
            "full_num_operations": metrics.num_operations,
            "full_win_rate": metrics.win_rate,
            "full_exposure_ratio": metrics.exposure_ratio,
            "full_turnover": metrics.turnover,
            **_slice_metrics(equity, RECENT_START),
        }
        rows.append(row)

    results = pd.DataFrame(rows)
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUT_CSV, index=False)
    _write_markdown(results, OUT_MD)

    display = results.sort_values(["recent_sharpe_ratio", "recent_annualized_return"], ascending=False)
    print(f"Saved {OUT_CSV}")
    print(f"Saved {OUT_MD}")
    print("")
    print(
        display[
            [
                "variant",
                "recent_annualized_return",
                "recent_max_drawdown",
                "recent_sharpe_ratio",
                "full_annualized_return",
                "full_max_drawdown",
                "full_sharpe_ratio",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
