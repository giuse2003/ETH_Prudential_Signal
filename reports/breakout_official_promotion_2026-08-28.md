# Promozione del breakout protetto

Data della decisione: `2026-08-28`  
Ultima candela chiusa: `2026-08-27`  
Mercato: Coinbase Advanced Trade `ETH-USD`, candele daily UTC

## Decisione

Il breakout protetto viene promosso da candidato shadow a secondo percorso
ufficiale di ingresso. La strategia acquista quando e' completo il percorso
standard **oppure** il percorso breakout protetto.

Non vengono modificate le due condizioni di vendita, la loro precedenza, la
gestione long/cash o il calcolo del backtest.

## Percorsi di ingresso

Il percorso standard richiede insieme:

1. `Close > SMA200`;
2. `SMA50 > SMA200`;
3. `40 <= RSI14 <= 65`;
4. `Close > Close.shift(7)`;
5. `Volume > VolumeAvg20`.

Il breakout protetto richiede insieme:

1. `SMA50 <= SMA200`;
2. `Close > SMA50` e `Close >= SMA200 * 0,90`;
3. `SMA50 >= SMA50.shift(5)`;
4. `40 <= RSI14 <= 65`;
5. `Close > Close.shift(7)`;
6. `Volume >= VolumeAvg20 * 1,20`;
7. `Close` sopra il massimo dei cinque Close precedenti;
8. guardrail superato.

Il guardrail blocca soltanto il secondo percorso quando sono vere insieme:

- `SMA200 / SMA200.shift(20) - 1 > 0`;
- `SMA50 / SMA200 - 1 < -0,15`.

Questa protezione elimina il falso ingresso del gennaio 2026 senza perdere i
breakout favorevoli identificati nella serie storica.

## Motivo della promozione

Il percorso standard non poteva intercettare il rialzo iniziato il 17 agosto
2026: nelle prime due candele RSI, momentum e volume erano validi, ma Close e
SMA50 erano ancora sotto SMA200; dal 19 agosto il prezzo era sopra SMA200, ma
RSI era gia' oltre 65 e SMA50 restava sotto SMA200.

La rimozione globale dei due filtri avrebbe aumentato molto il numero di
operazioni e peggiorato il drawdown. Il percorso separato conserva quindi le
regole prudenziali standard e ammette soltanto una configurazione di recupero
con prezzo, trend breve, momentum e volume concordi.

## Metriche congelate

Periodo `2016-12-08` - `2026-08-27`, 3.550 osservazioni. Il confronto ufficiale
usa un costo prudenziale dello `0,60%` per lato.

| Metrica | Baseline v3 | Buy & Hold |
|---|---:|---:|
| Rendimento totale | +240.310,55% | +30.163,66% |
| Rendimento annualizzato | 122,70% | 79,95% |
| Max drawdown | -39,05% | -94,01% |
| Sharpe | 1,845 | 1,097 |
| Profit factor | 17,813 | n/a |
| Trade completati | 32 | n/a |
| Win rate | 59,38% | n/a |
| Esposizione | 30,48% | 100,00% |

Sensibilita' ai costi del modello promosso:

| Costo per lato | Annualizzato | Max DD | Sharpe | Profit factor |
|---|---:|---:|---:|---:|
| Maker 0,07% | 130,67% | -36,04% | 1,915 | 19,285 |
| Taker 0,16% | 129,30% | -36,56% | 1,903 | 19,020 |
| Stress 0,60% | 122,70% | -39,05% | 1,845 | 17,813 |

Il pacchetto riproducibile e' in
`docs/runs/baseline-v3-2026-08-27/manifest.json`.

## Gestione della data di attivazione

Il backtest storico completo include il segnale breakout del `2026-08-17` a
`1.911,94 USD`; al cutoff il relativo trade e' ancora aperto. Questo serve a
misurare la regola su tutta la storia, ma non equivale a un acquisto reale.

Operativamente il secondo percorso e' attivo dalle candele chiuse del
`2026-08-28`. Lo stato reale riparte **FUORI** e non ricostruisce l'acquisto del
17 agosto. Un futuro `ACQUISTA` richiede una nuova candela che soddisfi per
intero uno dei due percorsi ufficiali.

## Limiti e controlli futuri

- il rialzo di agosto ha contribuito a formulare il nuovo percorso e non e'
  una validazione futura indipendente;
- i risultati sono retrospettivi e non costituiscono una previsione;
- spread, slippage, imposte e rendimento della liquidita' sono esclusi;
- ogni nuovo ingresso breakout deve essere registrato nel diario con esito,
  drawdown e confronto con il percorso standard;
- le baseline v1 e v2 restano congelate e riproducibili per consentire il
  confronto e l'eventuale reversibilita' della decisione.

## Riferimenti

- `reports/august_2026_missed_rally_followup.md`;
- `reports/january_2026_entry_guardrail_research.md`;
- `reports/january_2026_guardrail_blind_validation.md`;
- `DOCUMENTATION/ETH_MODEL_RESEARCH_DIARY.md`;
- `DOCUMENTATION/DECISION_LOG.md`.
