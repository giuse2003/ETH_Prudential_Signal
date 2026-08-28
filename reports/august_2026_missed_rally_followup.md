# Follow-up sul rialzo ETH di agosto 2026

Data dell'analisi: `2026-08-28`  
Ultima candela chiusa: `2026-08-27`  
Mercato: `ETH-USD` Coinbase, candele daily UTC

## Scopo

Verificare perche' la Baseline ufficiale sia rimasta fuori durante il rialzo
iniziato il 17 agosto e confrontare possibili correzioni senza cambiare le
regole di uscita.

Questa sezione registra lo stato durante l'analisi. La successiva decisione di
promozione e documentata in `breakout_official_promotion_2026-08-28.md`.

## Diagnosi puntuale

| Data | Close USD | SMA50 | SMA200 | RSI14 | Prezzo > SMA200 | SMA50 > SMA200 | RSI 40-65 | Momentum 7g > 0 | Volume > media20 |
|---|---:|---:|---:|---:|---|---|---|---|---|
| 2026-08-17 | 1.911,94 | 1.843,10 | 2.008,28 | 56,61 | no | no | si | si | si |
| 2026-08-18 | 1.916,72 | 1.849,22 | 2.004,35 | 57,41 | no | no | si | si | si |
| 2026-08-19 | 2.251,69 | 1.862,87 | 2.003,36 | 82,16 | si | no | no | si | si |
| 2026-08-20 | 2.326,35 | 1.877,24 | 2.003,65 | 84,34 | si | no | no | si | si |
| 2026-08-21 | 2.515,80 | 1.893,58 | 2.004,50 | 88,27 | si | no | no | si | si |
| 2026-08-22 | 2.422,00 | 1.906,90 | 2.005,46 | 77,86 | si | no | no | si | si |
| 2026-08-23 | 2.463,39 | 1.920,58 | 2.007,06 | 79,04 | si | no | no | si | si |
| 2026-08-24 | 2.482,20 | 1.934,54 | 2.010,36 | 79,57 | si | no | no | si | si |
| 2026-08-25 | 2.442,55 | 1.947,42 | 2.012,26 | 75,24 | si | no | no | si | si |
| 2026-08-26 | 2.506,93 | 1.962,16 | 2.014,36 | 77,39 | si | no | no | si | si |
| 2026-08-27 | 2.511,67 | 1.977,56 | 2.016,48 | 77,55 | si | no | no | si | si |

Non esiste una candela in cui tutte le condizioni ufficiali siano vere:

- il 17 e 18 agosto l'RSI e' valido, ma prezzo e SMA50 non hanno ancora
  superato SMA200;
- dal 19 agosto il prezzo e' sopra SMA200, ma RSI e SMA50 sono bloccanti;
- il problema e' la sequenza temporale dei filtri, non il solo tetto RSI.

## Varianti semplici

Commissione taker Coinbase `0,16%` per lato. Le uscite restano quelle
ufficiali. I rendimenti totali molto elevati derivano dalla capitalizzazione
sull'intera serie Coinbase; annualizzato, drawdown e Sharpe sono piu' utili
per confrontare i sistemi.

| Ingresso | Ingresso agosto | Totale | Annualizzato | Max DD | Sharpe | Profit factor | Operazioni | Nuovi ingressi / loss |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline ufficiale | nessuno | +73.718,82% | 97,23% | -39,87% | 1,664 | 15,995 | 30 | 0 / 0 |
| Solo RSI >= 40 | nessuno | +215.909,13% | 120,26% | -39,44% | 1,720 | 20,472 | 34 | 8 / 4 |
| Senza gate SMA50>SMA200 | nessuno | +137.503,08% | 110,28% | -36,56% | 1,739 | 16,103 | 35 | 8 / 3 |
| Senza entrambi i blocchi | 19/08 a 2.251,69 | +423.349,08% | 136,05% | -43,03% | 1,778 | 15,754 | 42 | 19 / 8 |

Risultato: rimuovere un solo blocco non cattura il movimento. Rimuoverli
entrambi lo cattura in ritardo, aumenta le operazioni da 30 a 42 e peggiora
il drawdown massimo. Non e' la correzione prudenziale preferibile.

## Breakout protetto gia' congelato

Il percorso shadow studiato in precedenza aggiunge alla Baseline un ingresso
alternativo soltanto durante la ricostruzione del trend. Richiede:

1. `SMA50 <= SMA200`;
2. `Close > SMA50`;
3. `Close >= 90% di SMA200`;
4. slope SMA50 a 5 giorni `>= 0`;
5. RSI compreso tra `40` e `65`;
6. momentum a 7 giorni positivo;
7. volume almeno `20%` sopra la media a 20 giorni;
8. Close sopra il massimo dei cinque Close precedenti.

Il guardrail blocca questo solo percorso breakout quando sono vere insieme:

- slope SMA200 a 20 giorni `> 0%`;
- SMA50 almeno `15%` sotto SMA200.

Il 17 agosto il percorso e' ammesso: RSI `56,61`, momentum `+2,16%`, volume
`+53,06%`, slope SMA50 `+1,69%`, distanza SMA50/SMA200 `-8,22%` e slope
SMA200 `-5,63%`. Il segnale shadow entra a `1.911,94 USD`, prima
dell'accelerazione del 19 agosto.

Al 27 agosto la posizione shadow e' ancora aperta:

- Close: `2.511,67 USD`;
- rendimento netto provvisorio: `+31,16%` con costo taker;
- massimo drawdown del trade: `-3,73%`;
- massimo Close dal suo ingresso: `2.515,80 USD`;
- soglia Trail8 corrente: `2.314,54 USD`;
- nessuna uscita ufficiale e nessun Trail8 attivato.

## Metriche del breakout protetto

| Sistema | Totale | Annualizzato | Max DD | Sharpe | Profit factor | Operazioni | Win rate | Esposizione |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline, taker 0,16% | +73.718,82% | 97,23% | -39,87% | 1,664 | 15,995 | 30 | 50,00% | 26,73% |
| Breakout protetto, taker 0,16% | +319.331,04% | 129,30% | -36,56% | 1,903 | 19,020 | 32 | 59,38% | 30,48% |

Episodi aggiuntivi del breakout protetto:

| Entrata | Prezzo | Uscita | Prezzo | Rendimento netto | Stato |
|---|---:|---|---:|---:|---|
| 2017-02-01 | 10,72 | 2017-03-08 | 16,68 | +55,10% | chiuso |
| 2019-03-27 | 139,08 | 2019-04-11 | 164,92 | +18,20% | chiuso |
| 2023-01-06 | 1.268,84 | 2023-03-03 | 1.569,54 | +23,30% | chiuso |
| 2024-11-06 | 2.724,27 | 2024-12-18 | 3.624,84 | +32,63% | chiuso |
| 2026-08-17 | 1.911,94 | - | - | +31,16% | aperto al cutoff |

Il guardrail elimina il falso ingresso del `2026-01-13`, che senza protezione
avrebbe perso `-11,92%`.

## Sensibilita' ai costi

| Costo per lato | Sistema | Annualizzato | Max DD | Sharpe | Profit factor |
|---|---|---:|---:|---:|---:|
| Maker 0,07% | Baseline | 98,32% | -39,21% | 1,675 | 16,226 |
| Maker 0,07% | Breakout protetto | 130,67% | -36,04% | 1,915 | 19,285 |
| Taker 0,16% | Baseline | 97,23% | -39,87% | 1,664 | 15,995 |
| Taker 0,16% | Breakout protetto | 129,30% | -36,56% | 1,903 | 19,020 |
| Stress 0,60% | Baseline | 91,98% | -43,00% | 1,607 | 14,944 |
| Stress 0,60% | Breakout protetto | 122,70% | -39,05% | 1,845 | 17,813 |

## Conclusione provvisoria al momento del test

Il rialzo non giustifica la rimozione globale di `RSI <= 65` e
`SMA50 > SMA200`. La soluzione piu' coerente con il carattere prudenziale e'
un secondo percorso di ingresso OR, ristretto ai breakout di ricostruzione e
protetto dal guardrail di regime.

Il risultato e' favorevole ma il trade del 17 agosto e' ancora aperto e lo
stesso evento e' stato usato per sviluppare il candidato. Non costituisce da
solo una validazione indipendente definitiva.

Decisione al `2026-08-28`:

- Baseline, bot, dashboard e segnali Telegram restano invariati;
- il breakout protetto resta il candidato principale;
- evitare un ingresso retroattivo a 2.500 USD solo per inseguire il movimento;
- riesaminare il pacchetto alla chiusura del trade shadow secondo le uscite
  ufficiali oppure a una nuova attivazione indipendente;
- possibile prossimo passo operativo: mostrare sulla dashboard uno stato
  shadow separato, senza trasformarlo in `ACQUISTA` ufficiale.

## Esito successivo

Nella decisione successiva del `2026-08-28` il candidato e' stato promosso a
secondo percorso ufficiale, con attivazione operativa futura e senza acquisto
retroattivo sul 17 agosto. Il verbale definitivo e' in
`reports/breakout_official_promotion_2026-08-28.md`.
