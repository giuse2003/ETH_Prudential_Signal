# Implementazione della Baseline ufficiale

Data di promozione: `2026-07-27`.

## Decisione

Il candidato fisso identificato internamente come
`combo_trail_mom_15_sma_break_2_0` viene promosso a **Baseline ufficiale** di
ETH-USD Signal.

Il numero di versione resta un dettaglio interno al progetto:

- la Baseline ufficiale usa internamente `model_version = 2.0`;
- la precedente `model_version = 1.0` diventa la **vecchia baseline**;
- Telegram, dashboard e report operativi non mostrano `v2` nel nome del modello.

## Regole ufficiali

### Acquisto

Un nuovo `ACQUISTA` richiede tutte le condizioni:

1. `Close > SMA200`;
2. `SMA50 > SMA200`;
3. `40 <= RSI(14) <= 65`;
4. `Close > Close.shift(7)`;
5. `Volume ETH-USD > VolumeAvg20`.

Le cinque regole di acquisto sono identiche a quelle della vecchia baseline.
Il limite RSI 65 vale soltanto sui nuovi ingressi e non chiude una posizione.

### Vendita

`VENDI` richiede almeno una condizione:

1. `Close < SMA50 * 0,98` nella candela corrente;
2. perdita di almeno l'8% dal massimo Close post-ingresso e conferma simultanea:
   momentum a 7 giorni `>= -15%` e volume relativo `>= +20%`.

Rispetto alla vecchia baseline cambiano soltanto:

- la soglia SMA50, da `Close < SMA50` a `Close < SMA50 * 0,98`;
- il momentum di conferma Trail8, da `-5%` a `-15%`.

Trailing 8%, conferma volume, precedenza della vendita, esposizione binaria e
azione `MANTIENI STATO ATTUALE` restano invariati.

## Costi ed esecuzione

- segnale calcolato alla chiusura `t` e applicato al rendimento `t+1`;
- commissione strategia: `0,6%` su ogni ingresso e uscita;
- Buy & Hold: `0,6%` all'acquisto e `0,6%` alla vendita finale;
- spread, slippage, imposte e rendimento cash: esclusi;
- trade aperti al cutoff: esclusi da numero operazioni e win rate.

## Evidenza della promozione

### Periodo completo 2016-2026

Con gli stessi dati Coinbase e commissione dello 0,6% per lato:

| Metrica | Vecchia baseline | Baseline ufficiale | Buy & Hold |
|---|---:|---:|---:|
| Rendimento totale | 12.080,48% | 56.672,64% | 23.431,28% |
| Annualizzato | 64,61% | 93,12% | 76,25% |
| Max drawdown | -51,57% | -43,00% | -94,01% |
| Sharpe | 1,265 | 1,615 | 1,074 |
| Trade completati | 36 | 30 | n/a |

### Periodo retrospettivo 2021-2026

| Metrica | Vecchia baseline | Baseline ufficiale | Buy & Hold |
|---|---:|---:|---:|
| Rendimento totale | 194,63% | 834,01% | 161,63% |
| Annualizzato | 21,41% | 49,35% | 18,85% |
| Max drawdown | -51,57% | -43,00% | -79,35% |
| Sharpe | 0,672 | 1,197 | 0,610 |

Nel test con un'ulteriore candela di ritardo la Baseline ufficiale mantiene
annualizzato 37,44%, drawdown -47,25% e Sharpe 0,983.

Il Deflated Sharpe del candidato sul periodo cucito e 96,80%. Il PBO segnala
invece instabilita nel ranking delle sole varianti di uscita, motivo per cui non
viene adottata una riottimizzazione annuale. La regola fissa e piu semplice,
mantiene i cinque ingressi originali e supera il candidato alternativo nel test
di ritardo.

Queste analisi sono retrospettive. L'universo delle ipotesi e stato costruito
dopo avere osservato la serie e non costituisce un vero futuro non visto.

## Stato al cutoff

Alla candela conclusa `2026-07-26`:

- azione Baseline ufficiale: `MANTIENI STATO ATTUALE`;
- esposizione ricostruita: `0%`;
- ultima vendita effettiva: `2026-07-09`;
- l'attivazione non richiede un acquisto o una vendita immediata.

## Artefatti e reversibilita

- Baseline ufficiale: `docs/runs/baseline-v2-2026-07-26/`;
- vecchia baseline: `docs/runs/baseline-v1-2026-07-26/`;
- snapshot Coinbase condiviso SHA-256:
  `09504484b0d115c6b130dbfc82f05f5dc9137ce11b1cf12604f9a1c96132c357`;
- il manifest e gli artefatti della vecchia baseline non sono stati modificati;
- il rollback richiede il ripristino del tag storico e del relativo manifest,
  non la riscrittura della Baseline ufficiale.

## Componenti allineati

- `strategy/signals.py`: soglie e stato posizione;
- `backtest/backtest.py`: commissioni strategia e Buy & Hold;
- `reports/generate.py` e `reports/publication.py`: etichette e manifest;
- `cloudflare-worker/src/worker.js`: testo `/conditions`;
- `tests/`: confini delle soglie, costi, manifest e riproducibilita;
- `README.md`, `DOCUMENTATION/` e `REPRODUCIBILITY.md`: contratto corrente.

## Riferimenti

- `reports/condition_ablation_coinbase_0_6.md`;
- `reports/walk_forward_coinbase_0_6.md`;
- `reports/coinbase_fee_0_6_comparison.md`;
- `DOCUMENTATION/DECISION_LOG.md`.
