"""
Configurazione centralizzata.

Obiettivo:
- rendere facile modificare finestre (SMA, RSI, ecc.)
- rendere facile estendere la logica futura (on-chain, Fear & Greed, ecc.)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    model_name: str = "ETH-USD Signal"
    # Versione interna. Non viene mostrata nei messaggi operativi pubblici.
    model_version: str = "3.0"
    data_source: str = "Coinbase Advanced Trade"
    transaction_cost_rate: float = 0.006

    # Intervallo dati
    # Prima data della serie Coinbase continua: 2016-05-21 e 2016-05-22
    # sono assenti nello storico precedente.
    start_date: str = "2016-05-23"
    end_date: str = "today"

    # Mercato Coinbase usato per candele, indicatori, segnali e backtest.
    product_id: str = "ETH-USD"
    informational_product_id: str = "ETH-EUR"

    # Indicatori tecnici
    sma_fast: int = 50
    sma_slow: int = 200
    rsi_period: int = 14
    vol_avg_period: int = 20
    atr_period: int = 14
    periods_per_year: int = 365  # Ethereum scambia 7 giorni su 7
    weeks_52_days: int = 365
    momentum_days: int = 7    # Confronto prezzo con 7 giorni fa

    # Punteggio (0..100)
    # Nota: i pesi sono implementati direttamente nella strategia per chiarezza.

    # Esposizione prudente (mappatura segnale -> peso capitale).
    # MANTIENI STATO ATTUALE usa NaN: conserva l'esposizione precedente.
    # - ACQUISTA -> 100%
    # - MANTIENI STATO ATTUALE -> esposizione precedente
    # - VENDI -> 0%
    exposure_map: dict[str, float] = None  # impostato in __post_init__

    def __post_init__(self) -> None:
        # dataclass frozen => usiamo object.__setattr__
        object.__setattr__(
            self,
            "exposure_map",
            {
                "ACQUISTA": 1.0,
                "MANTIENI STATO ATTUALE": float("nan"),
                "VENDI": 0.0,
            },
        )


CFG = Config()

