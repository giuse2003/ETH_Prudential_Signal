"""
Strategia prudente basata su:
- Trend principale/secondario (SMA200 e SMA50)
- RSI (14)
- Volume relativo (Volume vs VolumeAvg20)
- Distanza dalla SMA200

Output:
- punteggio 0..100
- classificazione (ACQUISTA / MANTIENI STATO ATTUALE / VENDI)
- livello di rischio informativo (BASSO / MEDIO / ALTO)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import CFG


ENTRY_RSI_MAX = 65.0
SMA50_BREAK_PCT = 0.02
TRAILING_STOP_PCT = 0.08
TRAILING_MOMENTUM_MIN = -0.15
TRAILING_VOLUME_REL_MIN = 0.20
BREAKOUT_OPERATIONAL_START = pd.Timestamp("2026-08-28")
BREAKOUT_SMA200_PROXIMITY_MIN = 0.90
BREAKOUT_VOLUME_REL_MIN = 0.20
BREAKOUT_LOOKBACK_DAYS = 5
BREAKOUT_SMA50_SLOPE_DAYS = 5
BREAKOUT_GUARD_SMA200_SLOPE_DAYS = 20
BREAKOUT_GUARD_SMA50_GAP_MAX = -0.15
HOLD_ACTION = "MANTIENI STATO ATTUALE"


def _distance_from_sma200_pct(close: pd.Series, sma200: pd.Series) -> pd.Series:
    """
    Distanza (%): (Close - SMA200) / SMA200 * 100
    """
    # Dove SMA200 è NaN o 0 la distanza diventa NaN/inf -> comparazioni gestiranno a false.
    return (close - sma200) / sma200 * 100.0


def _sma50_sell_condition(close, sma50):
    """Vero quando il Close perde la SMA50 di oltre il margine ufficiale."""
    return close < sma50 * (1.0 - SMA50_BREAK_PCT)


def score_rowwise(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcola Punteggio totale e componenti.
    Il punteggio è pensato come "somma di condizioni favorevoli".
    """
    df = df.copy()

    close = df["Close"]
    sma50 = df["SMA50"]
    sma200 = df["SMA200"]
    rsi = df["RSI"]
    volume = df["Volume"]
    volume_avg20 = df["VolumeAvg20"]

    distance_pct = _distance_from_sma200_pct(close, sma200)
    df["DistanceFromSMA200_Pct"] = distance_pct

    # Trend principale
    trend_main = (close > sma200).astype(float) * 25.0

    # Trend secondario
    trend_secondary = (sma50 > sma200).astype(float) * 25.0

    # RSI scoring (spec)
    # >= 40: +15
    # 30-40: +10
    # RSI < 30: 0
    rsi_score = np.zeros(len(df), dtype=float)
    rsi_score[rsi >= 40] = 15.0
    rsi_score[(rsi >= 30) & (rsi < 40)] = 10.0
    df["RSI_Score"] = rsi_score

    # Volume scoring (spec: volume odierno > volume medio 20 giorni)
    volume_score = (volume > volume_avg20).astype(float) * 15.0
    df["Volume_Score"] = volume_score

    # Distanza dalla SMA200 (spec)
    # 0% .. 20% => +20
    # > 40% => 0
    # (20% .. 40% => 0 implicito)
    dist_score = np.zeros(len(df), dtype=float)
    dist_score[(distance_pct >= 0) & (distance_pct <= 20)] = 20.0
    # dist_score[distance_pct > 40] resta 0
    df["Distance_Score"] = dist_score

    total = trend_main + trend_secondary + df["RSI_Score"] + df["Volume_Score"] + df["Distance_Score"]
    df["Punteggio"] = total

    return df


def _breakout_components(df: pd.DataFrame) -> pd.DataFrame:
    close = df["Close"]
    sma50 = df["SMA50"]
    sma200 = df["SMA200"]
    momentum_col = f"Close_{CFG.momentum_days}d_ago"
    close_momentum = df.get(momentum_col, pd.Series(np.nan, index=df.index))
    sma50_slope = sma50 / sma50.shift(BREAKOUT_SMA50_SLOPE_DAYS) - 1.0
    sma200_slope = (
        sma200 / sma200.shift(BREAKOUT_GUARD_SMA200_SLOPE_DAYS) - 1.0
    )
    sma50_gap = sma50 / sma200 - 1.0
    prior_high = (
        close.shift(1)
        .rolling(BREAKOUT_LOOKBACK_DAYS, min_periods=BREAKOUT_LOOKBACK_DAYS)
        .max()
    )

    components = pd.DataFrame(index=df.index)
    components["regime"] = sma50 <= sma200
    components["price_recovery"] = (
        (close > sma50) & (close >= sma200 * BREAKOUT_SMA200_PROXIMITY_MIN)
    )
    components["sma50_slope"] = sma50_slope >= 0.0
    components["rsi"] = df["RSI"].between(40.0, ENTRY_RSI_MAX, inclusive="both")
    components["momentum"] = close > close_momentum
    components["volume"] = (
        df["Volume"] >= df["VolumeAvg20"] * (1.0 + BREAKOUT_VOLUME_REL_MIN)
    )
    components["breakout"] = close > prior_high
    components["guard_passed"] = ~(
        (sma200_slope > 0.0) & (sma50_gap < BREAKOUT_GUARD_SMA50_GAP_MAX)
    )
    components["raw"] = components[
        [
            "regime",
            "price_recovery",
            "sma50_slope",
            "rsi",
            "momentum",
            "volume",
            "breakout",
        ]
    ].all(axis=1)
    components["entry"] = components["raw"] & components["guard_passed"]
    return components.fillna(False)


def _activation_mask(index: pd.Index, active_from: pd.Timestamp | str | None) -> pd.Series:
    if active_from is None:
        return pd.Series(True, index=index)
    if not isinstance(index, pd.DatetimeIndex):
        raise ValueError("La data di attivazione richiede un DatetimeIndex.")
    return pd.Series(index >= pd.Timestamp(active_from), index=index)


def compute_strict_signal(
    df: pd.DataFrame,
    *,
    breakout_active_from: pd.Timestamp | str | None = None,
    state_reset_date: pd.Timestamp | str | None = None,
) -> pd.DataFrame:
    """
    Classificazione stretta:
    ACQUISTA se TUTTE le condizioni rialziste sono vere.
    VENDI se il prezzo chiude oltre il 2% sotto SMA50 oppure se il trailing
    stop confermato viene attivato.
    Altrimenti MANTIENI STATO ATTUALE.
    """
    df = df.copy()

    if df.empty:
        df["Segnale"] = np.array([], dtype=object)
        return df

    close = df["Close"]
    sma50 = df["SMA50"]
    sma200 = df["SMA200"]
    rsi = df["RSI"]
    volume = df["Volume"]
    volume_avg20 = df["VolumeAvg20"]
    days = CFG.momentum_days
    close_momentum = df[f"Close_{days}d_ago"] if f"Close_{days}d_ago" in df.columns else pd.Series(np.nan, index=df.index)

    entry_rsi_filter = rsi <= ENTRY_RSI_MAX
    official_buy_cond = (
        (close > sma200) &
        (sma50 > sma200) &
        (rsi >= 40) &
        (close > close_momentum) &
        (volume > volume_avg20)
    )
    filtered_new_entry_cond = official_buy_cond & entry_rsi_filter
    breakout = _breakout_components(df)
    breakout_enabled = _activation_mask(df.index, breakout_active_from)
    breakout_entry_cond = breakout["entry"] & breakout_enabled

    official_sell_cond = _sma50_sell_condition(close, sma50)

    signal, trail_stop_hit, trail_confirmed, entry_path, position_open = _stateful_signals(
        df=df,
        official_buy_cond=official_buy_cond,
        filtered_new_entry_cond=filtered_new_entry_cond,
        breakout_entry_cond=breakout_entry_cond,
        official_sell_cond=official_sell_cond,
        state_reset_date=state_reset_date,
    )

    df["Entry_RSI_Filter_Passed"] = entry_rsi_filter
    df["Standard_Entry"] = filtered_new_entry_cond
    df["Breakout_Raw"] = breakout["raw"]
    df["Breakout_Guard_Passed"] = breakout["guard_passed"]
    df["Breakout_Enabled"] = breakout_enabled
    df["Breakout_Entry"] = breakout_entry_cond
    df["Entry_Path"] = entry_path
    df["Official_Sell"] = official_sell_cond
    df["Trail8_Stop_Hit"] = trail_stop_hit
    df["Trail8_Confirmed"] = trail_confirmed
    df["Position_Open"] = position_open
    df["Segnale"] = signal
    return df


def _stateful_signals(
    *,
    df: pd.DataFrame,
    official_buy_cond: pd.Series,
    filtered_new_entry_cond: pd.Series,
    breakout_entry_cond: pd.Series | None = None,
    official_sell_cond: pd.Series,
    state_reset_date: pd.Timestamp | str | None = None,
) -> tuple[np.ndarray, pd.Series, pd.Series, np.ndarray, pd.Series]:
    """
    Applica la Baseline ufficiale con il trailing stop confermato.

    Il trailing richiede stato di posizione: massimo Close raggiunto da quando
    la posizione e' aperta. Lo stato viene ricostruito scorrendo la serie.
    """
    signal = np.full(len(df), HOLD_ACTION, dtype=object)
    trail_stop_hit = pd.Series(False, index=df.index)
    trail_confirmed = pd.Series(False, index=df.index)
    entry_path = np.full(len(df), "", dtype=object)
    position_open = pd.Series(False, index=df.index)
    breakout_entry_cond = (
        breakout_entry_cond
        if breakout_entry_cond is not None
        else pd.Series(False, index=df.index)
    )
    reset_at = pd.Timestamp(state_reset_date) if state_reset_date is not None else None
    reset_applied = False

    exposure = False
    peak_close: float | None = None

    for pos, (date, row) in enumerate(df.iterrows()):
        if reset_at is not None and not reset_applied and pd.Timestamp(date) >= reset_at:
            exposure = False
            peak_close = None
            reset_applied = True

        close_value = float(row["Close"])
        official_buy = bool(official_buy_cond.loc[date])
        filtered_new_entry = bool(filtered_new_entry_cond.loc[date])
        breakout_new_entry = bool(breakout_entry_cond.loc[date])
        should_official_sell = bool(official_sell_cond.loc[date])
        should_trail_sell = False

        if should_official_sell:
            signal[pos] = "VENDI"
            exposure = False
            peak_close = None
            position_open.loc[date] = exposure
            continue

        if not exposure and (filtered_new_entry or breakout_new_entry):
            signal[pos] = "ACQUISTA"
            entry_path[pos] = "standard" if filtered_new_entry else "breakout_protected"
            exposure = True
            peak_close = close_value
            position_open.loc[date] = exposure
            continue

        if official_buy and exposure:
            peak_close = max(peak_close if peak_close is not None else close_value, close_value)
            position_open.loc[date] = exposure
            continue

        if exposure:
            peak_close = max(peak_close if peak_close is not None else close_value, close_value)
            stop_hit = close_value <= peak_close * (1.0 - TRAILING_STOP_PCT)
            trail_stop_hit.loc[date] = bool(stop_hit)
            if stop_hit:
                close_ago = row.get(f"Close_{CFG.momentum_days}d_ago", np.nan)
                volume_avg = row.get("VolumeAvg20", np.nan)
                momentum_7d = close_value / float(close_ago) - 1.0 if pd.notna(close_ago) and float(close_ago) != 0.0 else np.nan
                volume_rel = (
                    float(row["Volume"]) / float(volume_avg) - 1.0
                    if pd.notna(volume_avg) and float(volume_avg) != 0.0
                    else np.nan
                )
                should_trail_sell = bool(
                    pd.notna(momentum_7d)
                    and pd.notna(volume_rel)
                    and momentum_7d >= TRAILING_MOMENTUM_MIN
                    and volume_rel >= TRAILING_VOLUME_REL_MIN
                )
                trail_confirmed.loc[date] = should_trail_sell

        if should_trail_sell:
            signal[pos] = "VENDI"
            exposure = False
            peak_close = None
        position_open.loc[date] = exposure

    return signal, trail_stop_hit, trail_confirmed, entry_path, position_open


def compute_risk_level(df: pd.DataFrame) -> pd.Series:
    """
    Calcola il livello di rischio (BASSO, MEDIO, ALTO) come informazione ausiliaria.
    """
    close = df["Close"]
    sma50 = df["SMA50"]
    sma200 = df["SMA200"]
    rsi = df["RSI"]
    distance_pct = df["DistanceFromSMA200_Pct"]
    
    # Inizializza a MEDIO
    risk = pd.Series("MEDIO", index=df.index, dtype=object)
    
    # Condizioni per ALTO
    alto_cond = (
        ((close < sma200) & (sma50 < sma200)) |
        (rsi > 70) |
        (distance_pct > 40.0)
    )
    
    # Condizioni per BASSO
    basso_cond = (
        (close > sma200) &
        (sma50 > sma200) &
        (rsi <= 60) &
        (distance_pct <= 20.0)
    )
    
    risk[alto_cond] = "ALTO"
    risk[basso_cond] = "BASSO"
    
    # Gestione valori mancanti
    nan_mask = close.isna() | sma50.isna() | sma200.isna() | rsi.isna()
    risk[nan_mask] = "MEDIO"
    
    return risk


def compute_signals(
    df_indicators: pd.DataFrame,
    *,
    breakout_active_from: pd.Timestamp | str | None = None,
    state_reset_date: pd.Timestamp | str | None = None,
) -> pd.DataFrame:
    """
    Pipeline completa:
    - calcola punteggio tecnico (solo per report log, non decide il segnale)
    - classifica con regole strette
    - calcola il livello di rischio informativo
    """
    df = score_rowwise(df_indicators)
    df = compute_strict_signal(
        df,
        breakout_active_from=breakout_active_from,
        state_reset_date=state_reset_date,
    )
    df["Livello_Rischio"] = compute_risk_level(df)
    return df


def format_condition_message(
    signal: str,
    price_eur: float | None,
    buy_statuses: list[bool],
    breakout_statuses: list[bool],
    sell_statuses: list[bool],
    position_open: bool | None = None,
    title: str = "ETH-USD Signal - LIVE PREVIEW",
) -> str:
    if price_eur is None:
        price_text = "ETH-EUR non disponibile"
    else:
        price_text = f"{int(float(price_eur)):,}".replace(",", ".") + " EUR"

    return "\n".join(
        [
            title,
            "",
            f"Azione: {signal}",
            *(
                [f"Stato operativo: {'DENTRO' if position_open else 'FUORI'}"]
                if position_open is not None
                else []
            ),
            "",
            "Prezzo informativo:",
            price_text,
            "",
            "(per le condizioni: /conditions)",
            "",
            "ACQUISTA - PERCORSO 1:",
            *_format_condition_numbers(buy_statuses),
            "",
            "ACQUISTA - BREAKOUT PROTETTO:",
            *_format_condition_numbers(breakout_statuses),
            "",
            "VENDI:",
            *_format_condition_numbers(sell_statuses),
        ]
    )


def format_telegram_message(
    df_with_signals: pd.DataFrame,
    price_eur: float | None = None,
    title: str = "ETH-USD Signal - LIVE PREVIEW",
) -> str:
    """
    Produce il messaggio operativo compatto per Telegram.
    """
    row = df_with_signals.iloc[-1]
    segnale = row.get("Segnale", "N/A")

    eur_val = price_eur
    if eur_val is None:
        eur_val = row.get("Close_EUR")
        if pd.isna(eur_val):
            eur_val = None

    standard, breakout, sell = live_condition_statuses(df_with_signals)
    return format_condition_message(
        signal=str(segnale),
        price_eur=eur_val,
        buy_statuses=standard,
        breakout_statuses=breakout,
        sell_statuses=sell,
        position_open=bool(row.get("Position_Open", False)),
        title=title,
    )


def condition_state_key(df_with_signals: pd.DataFrame) -> str:
    """
    Restituisce un'impronta stabile delle condizioni operative mostrate su Telegram.

    Serve al monitor automatico per inviare una notifica solo quando cambia
    almeno una condizione, ignorando le oscillazioni del solo prezzo live.
    """
    standard, breakout, sell = live_condition_statuses(df_with_signals)
    return (
        f"BUY_STANDARD:{_bools_to_key(standard)}|"
        f"BUY_BREAKOUT:{_bools_to_key(breakout)}|SELL:{_bools_to_key(sell)}"
    )


def condition_key_from_statuses(
    buy_statuses: list[bool],
    breakout_statuses: list[bool],
    sell_statuses: list[bool],
) -> str:
    return (
        f"BUY_STANDARD:{_bools_to_key(buy_statuses)}|"
        f"BUY_BREAKOUT:{_bools_to_key(breakout_statuses)}|"
        f"SELL:{_bools_to_key(sell_statuses)}"
    )


def signal_from_condition_statuses(
    buy_statuses: list[bool],
    breakout_statuses: list[bool],
    sell_statuses: list[bool],
) -> str:
    if any(sell_statuses):
        return "VENDI"
    if all(buy_statuses) or all(breakout_statuses):
        return "ACQUISTA"
    return HOLD_ACTION


def live_condition_statuses(
    df_with_signals: pd.DataFrame,
) -> tuple[list[bool], list[bool], list[bool]]:
    row = df_with_signals.iloc[-1]
    previous = df_with_signals.iloc[-2] if len(df_with_signals) >= 2 else None
    momentum_col = f"Close_{CFG.momentum_days}d_ago"

    buy_statuses = [
        bool(row["Close"] > row["SMA200"]),
        bool(row["SMA50"] > row["SMA200"]),
        bool(40 <= row["RSI"] <= ENTRY_RSI_MAX),
        bool(row["Close"] > row[momentum_col]),
        bool(row["Volume"] > row["VolumeAvg20"]),
    ]
    breakout = _breakout_components(df_with_signals).iloc[-1]
    breakout_statuses = [
        bool(breakout["regime"]),
        bool(breakout["price_recovery"]),
        bool(breakout["sma50_slope"]),
        bool(breakout["rsi"]),
        bool(breakout["momentum"]),
        bool(breakout["volume"]),
        bool(breakout["breakout"]),
        bool(breakout["guard_passed"]),
    ]
    sell_statuses = [
        bool(_sma50_sell_condition(row["Close"], row["SMA50"])),
        bool(row.get("Trail8_Confirmed", False)),
    ]
    return buy_statuses, breakout_statuses, sell_statuses


def build_live_signal_frame(
    df_closed_daily: pd.DataFrame,
    live_price_usd: float,
    live_volume_24h: float,
    live_time_utc: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """
    Costruisce un frame LIVE provvisorio e ricalcola indicatori/segnale.

    La riga LIVE usa:
    - Close provvisorio = prezzo live aggregato
    - Volume provvisorio = volume aggregato rolling 24h
    - VolumeAvg20 = media dei 20 volumi delle candele chiuse precedenti

    La dashboard continua a usare solo il frame DAILY chiuso.
    """
    from indicators.technical_indicators import compute_all_indicators

    if df_closed_daily.empty:
        raise ValueError("Servono candele daily chiuse per costruire il segnale LIVE.")

    live_ts = live_time_utc or pd.Timestamp.utcnow()
    live_ts = pd.Timestamp(live_ts)
    if live_ts.tzinfo is not None:
        live_ts = live_ts.tz_convert("UTC").tz_localize(None)
    live_day = live_ts.normalize()

    df_live = df_closed_daily.copy()
    previous_close = float(df_live.iloc[-1]["Close"])
    live_row = df_live.iloc[-1].copy()
    live_row["Open"] = previous_close
    live_row["High"] = max(previous_close, float(live_price_usd))
    live_row["Low"] = min(previous_close, float(live_price_usd))
    live_row["Close"] = float(live_price_usd)
    live_row["Volume"] = float(live_volume_24h)
    if "Close_EUR" in live_row:
        live_row["Close_EUR"] = float("nan")

    df_live = pd.concat([df_live, pd.DataFrame([live_row], index=[live_day])])
    df_live = df_live[~df_live.index.duplicated(keep="last")].sort_index()

    df_ind = compute_all_indicators(df_live)
    df_ind.loc[live_day, "VolumeAvg20"] = df_closed_daily["Volume"].tail(CFG.vol_avg_period).mean()
    return compute_signals(
        df_ind,
        breakout_active_from=BREAKOUT_OPERATIONAL_START,
        state_reset_date=BREAKOUT_OPERATIONAL_START,
    )


def _bools_to_key(statuses: list[bool]) -> str:
    return "".join("1" if passed else "0" for passed in statuses)


def _format_condition_numbers(statuses: list[bool]) -> list[str]:
    return [
        f"{'🟩' if passed else '🟥'} {index}."
        for index, passed in enumerate(statuses, start=1)
    ]


def _buy_condition_statuses(df_with_signals: pd.DataFrame) -> list[bool]:
    row = df_with_signals.iloc[-1]
    momentum_col = f"Close_{CFG.momentum_days}d_ago"
    return [
        bool(row["Close"] > row["SMA200"]),
        bool(row["SMA50"] > row["SMA200"]),
        bool(40 <= row["RSI"] <= ENTRY_RSI_MAX),
        bool(row["Close"] > row[momentum_col]),
        bool(row["Volume"] > row["VolumeAvg20"]),
    ]


def _sell_condition_statuses(df_with_signals: pd.DataFrame) -> list[bool]:
    if len(df_with_signals) < 1:
        return [False]

    row = df_with_signals.iloc[-1]
    return [
        bool(_sma50_sell_condition(row["Close"], row["SMA50"])),
        bool(row.get("Trail8_Confirmed", False)),
    ]


def explain_latest_row(
    df_with_signals: pd.DataFrame,
    price_eur: float | None = None,
    price_usd: float | None = None,
) -> str:
    """
    Produce una sintesi testuale estesa per il report locale.
    """
    row = df_with_signals.iloc[-1]
    segnale = row.get("Segnale", "N/A")
    rischio = row.get("Livello_Rischio", "MEDIO")
    close_usd = row["Close"]

    usd_val = price_usd if price_usd is not None else float(close_usd)

    eur_val = price_eur
    if eur_val is None:
        eur_val = row.get("Close_EUR")
        if pd.isna(eur_val):
            eur_val = None

    def fmt_curr(val: float | None) -> str:
        if val is None or np.isnan(val):
            return "non disponibile"
        return f"{int(val):,}".replace(",", ".")

    usd_str = f"{fmt_curr(usd_val)} USD"
    eur_str = f"{fmt_curr(eur_val)} EUR" if eur_val is not None else "ETH-EUR non disponibile"

    trend_lungo_txt = "positivo" if usd_val > row["SMA200"] else "negativo"

    rsi = row["RSI"]
    if rsi >= 70:
        rsi_zone = "in zona ipercomprato"
    elif rsi < 30:
        rsi_zone = "in zona ipervenduto"
    else:
        rsi_zone = "in zona neutrale"

    sintesi_lines = [
        f"Trend lungo periodo {trend_lungo_txt}.",
        f"RSI {rsi_zone}.",
    ]
    if segnale == "ACQUISTA":
        sintesi_lines.append("Tutte le conferme rialziste sono allineate.")
    elif segnale == "VENDI":
        sintesi_lines.append("Debolezza tecnica o uscita protettiva confermata.")
    else:
        sintesi_lines.append("Nessuna conferma sufficiente per acquistare.")

    if segnale == "ACQUISTA":
        indicazione = "Accumulare o acquistare posizioni."
    elif segnale == "VENDI":
        indicazione = "Valutare la riduzione del rischio o vendita."
    else:
        indicazione = "Attendere. Nessuna nuova operazione consigliata."

    lines = [
        "ETH MONITOR",
        "",
        f"Azione: {segnale}",
        f"Rischio: {rischio}",
        "",
        "Prezzo:",
        usd_str,
        eur_str,
        "",
        "Sintesi:",
        "\n".join(sintesi_lines),
        "",
        "Indicazione:",
        indicazione,
    ]

    return "\n".join(lines)

