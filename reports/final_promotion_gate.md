# Final Promotion Gate

Data: `2026-06-28`.

Obiettivo: decidere se il candidato combinato puo' diventare nuova Baseline
ufficiale.

## Candidato Valutato

Ingresso:

- condizioni Baseline ufficiali attuali;
- filtro aggiuntivo sui nuovi acquisti: `RSI <= 65`.

Uscita:

- uscita ufficiale attuale: `Close < SMA50` per 2 giorni consecutivi;
- uscita aggiuntiva: trailing stop 8% dal massimo Close post-ingresso,
  confermato solo se:
  - momentum 7 giorni >= -5%;
  - volume relativo >= +20%.

Variante secondaria non promossa:

- `trade return >= 15%` per attivare l'uscita Trail8.

## Criteri Gate

| Criterio | Esito | Evidenza |
|---|---|---|
| Migliora rendimento annualizzato | Superato | +42,74% vs +30,26% |
| Riduce max drawdown | Superato | -45,09% vs -49,73% |
| Migliora Sharpe | Superato | 1,079 vs 0,828 |
| Migliora profit factor | Superato | 5,999 vs 4,215 |
| Non aumenta operazioni totali | Superato | 28 vs 28 |
| Tiene con costi/slippage | Superato | delta annuo ancora +11,68% con costo 1,00% |
| Non dipende da un solo evento | Superato con nota | batte Baseline in 3 finestre cronologiche su 4 |
| Peggioramenti residui accettabili | Superato | 2023: -0,45% annuo, segmento critico -0,48% |
| Regola spiegabile | Superato | ingresso evita RSI troppo esteso; uscita protegge capitale gia' acquisito |
| Rischio overfit controllato | Superato con nota | variante `gain minimo 15%` non promossa |

## Metriche Principali

| Modello | Ann. | Max DD | Sharpe | PF | Operazioni |
|---|---:|---:|---:|---:|---:|
| Baseline ufficiale | +30,26% | -49,73% | 0,828 | 4,215 | 28 |
| Candidato combinato | +42,74% | -45,09% | 1,079 | 5,999 | 28 |
| Delta | +12,48% | +4,64% | +0,251 | +1,784 | 0 |

## Validazione Cronologica

| Finestra | Delta return | Delta DD | Delta Sharpe | Esito |
|---|---:|---:|---:|---|
| 2019-2020 | +144,03% | +21,83% | +0,537 | Migliora |
| 2021-2022 | +68,34% | 0,00% | +0,185 | Migliora |
| 2023-2024 | +15,38% | +9,38% | +0,221 | Migliora |
| 2025-2026 | 0,00% | 0,00% | 0,000 | Invariato |

## Rischi Residui

1. Il campione operativo resta limitato: 28 operazioni chiuse.
2. Il vantaggio maggiore nasce da pochi eventi importanti, anche se non da uno
   solo.
3. Il 2023 contiene una piccola sottoperformance residua del candidato
   principale.
4. La regola Trail8 richiede stato operativo post-ingresso: massimo Close
   raggiunto da quando la posizione e' aperta.

## Decisione Tecnica

Il candidato combinato e' tecnicamente promuovibile a nuova Baseline ufficiale.

Motivo:

- supera il periodo completo;
- supera costi/slippage;
- supera la validazione cronologica;
- non aumenta le operazioni;
- migliora il drawdown;
- la variante piu' complessa `trade return >= 15%` non offre abbastanza valore
  aggiuntivo per essere promossa.

## Raccomandazione

Promuovere il candidato principale, non la variante secondaria.

Nuova Baseline proposta:

- `ACQUISTA` solo se le condizioni attuali sono vere e `RSI <= 65`;
- `VENDI` se esce il segnale ufficiale attuale;
- `VENDI` anche se scatta `Trail8 -5 / vol +20`.

## Condizioni Di Implementazione

Prima della promozione operativa:

- aggiungere test unitari dedicati al filtro `RSI <= 65`;
- aggiungere test unitari dedicati al trailing stop confermato;
- verificare che il monitor live salvi correttamente lo stato necessario per il
  massimo Close post-ingresso;
- aggiornare report, diario e status;
- eseguire test suite completa.

La Baseline ufficiale non e' stata modificata da questo gate.
