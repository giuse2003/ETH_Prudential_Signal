# Coinbase ETH Backtest - Commissione 0.60%

## Perimetro

- Mercato: `ETH-USD` da `Coinbase Advanced Trade`.
- Periodo comune: `2016-12-08` -> `2026-07-26`.
- Osservazioni giornaliere: 3518.
- Capitale iniziale ipotetico: USD 10,000.00.
- Commissione per lato: 0.60%.
- Costo composto acquisto + vendita: 1.20%.
- Strategia: costo applicato dal motore a ogni cambio completo di esposizione.
- Buy & Hold: un acquisto alla data iniziale e una vendita alla data finale.
- Per Buy & Hold i costi iniziale e finale incidono su rendimento e capitale; max drawdown e Sharpe descrivono la serie del prezzo detenuto.
- Slippage, spread e imposte: esclusi.

## Confronto Netto

| Metrica | Strategia prudenziale | Buy & Hold | Delta strategia - B&H |
|---|---:|---:|---:|
| Rendimento totale | 12080.48% | 23431.28% | -11350.80 p.p. |
| Rendimento annualizzato | 64.61% | 76.25% | -11.64 p.p. |
| Max drawdown | -51.57% | -94.01% | 42.44 p.p. |
| Sharpe | 1.265 | 1.076 | 0.189 |
| Capitale finale | USD 1,218,048.04 | USD 2,353,128.23 | -USD 1,135,080.18 |

## Operativita Strategia

- Operazioni complete: 36.
- Lati soggetti a commissione: 72.
- Win rate netto: 33.33%.
- Profit factor netto: 12.321.
- Esposizione media: 26.15%.
- Posizione finale: chiusa; la commissione dell'ultima vendita e inclusa.

## Impatto Commissioni

| Modello | Capitale finale lordo | Capitale finale netto | Riduzione finale |
|---|---:|---:|---:|
| Strategia prudenziale | USD 1,876,352.43 | USD 1,218,048.04 | USD 658,304.38 |
| Buy & Hold | USD 2,381,621.95 | USD 2,353,128.23 | USD 28,493.73 |

La riduzione finale include anche il rendimento composto non maturato sul capitale assorbito dalle commissioni; non rappresenta soltanto la somma nominale degli addebiti.

## Lettura

- Buy & Hold prevale sul rendimento netto totale di 11350.80 p.p. e sul rendimento annualizzato di 11.64 p.p..
- La strategia riduce il max drawdown di 42.44 p.p. rispetto al Buy & Hold.
- La strategia mantiene uno Sharpe superiore di 0.189.
- Il costo dello 0,6% per lato penalizza sensibilmente la strategia perche viene applicato su 72 cambi di esposizione, contro i due soli lati del Buy & Hold.

## Integrita Baseline

- Baseline letta in sola lettura: `baseline-v1-2026-07-26`.
- Snapshot Coinbase SHA-256: `09504484b0d115c6b130dbfc82f05f5dc9137ce11b1cf12604f9a1c96132c357`.
- Regole, sorgenti, manifest e artefatti congelati non sono stati modificati.
