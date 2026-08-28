# Model Documentation Index

Ultimo aggiornamento: 2026-08-28

## Fonti dello stato corrente

| Documento | Contenuto |
|---|---|
| `../README.md` | Regole, risultati e uso del progetto |
| `PROJECT_STATUS.md` | Stato operativo corrente |
| `PROJECT_OVERVIEW.md` | Architettura dati, modello e pubblicazione |
| `../EVALUATION_VALUES.md` | Metriche canoniche non arrotondate |
| `../REPRODUCIBILITY.md` | Riproduzione e versionamento interno |
| `../reports/breakout_official_promotion_2026-08-28.md` | Dossier della promozione v3 |
| `SIGNAL_RULE_VERIFICATION_LOG.md` | Verifica delle regole correnti |

Questi documenti descrivono la **Baseline ufficiale**. Il numero `v3` e usato
soltanto internamente per directory, manifest, tag e metadati.

## Contratto corrente

- nome pubblico: **ETH-USD Signal**;
- dati modello: Coinbase Advanced Trade `ETH-USD`;
- dati informativi: spot Coinbase `ETH-EUR`;
- storico canonico: dal `2016-05-23`;
- pacchetto ufficiale interno: `../docs/runs/baseline-v3-2026-08-27/`;
- baseline precedente: `../docs/runs/baseline-v2-2026-07-26/`;
- vecchia baseline: `../docs/runs/baseline-v1-2026-07-26/`;
- run operativo: `../docs/manifest.json`;
- commissione backtest: `0,6%` per lato.

## Regole ufficiali

### Acquisto - percorso 1

1. `Close > SMA200`;
2. `SMA50 > SMA200`;
3. `40 <= RSI14 <= 65` sui nuovi ingressi;
4. `Close > Close.shift(7)`;
5. `Volume > VolumeAvg20`.

### Acquisto - percorso 2

1. `SMA50 <= SMA200`;
2. `Close > SMA50` e `Close >= SMA200 * 0,90`;
3. SMA50 non in calo a cinque giorni;
4. `40 <= RSI14 <= 65`;
5. momentum a sette giorni positivo;
6. volume almeno 20% sopra la media a 20 giorni;
7. Close sopra i cinque Close precedenti;
8. guardrail di regime superato.

### Vendita

1. `Close < SMA50 * 0,98`;
2. Trail8 dal massimo post-ingresso, confermato da momentum 7 giorni
   `>= -15%` e volume relativo `>= +20%`.

La vendita ha precedenza. In assenza di una nuova azione viene pubblicato
`MANTIENI STATO ATTUALE`.

## Ricerca e decisioni

- `ETH_MODEL_RESEARCH_DIARY.md`: diario cronologico completo;
- `DECISION_LOG.md`: decisioni che cambiano modello o infrastruttura;
- `MODEL_IMPROVEMENT_ROADMAP.md`: stato della ricerca e prossime verifiche;
- `../reports/condition_ablation_coinbase_0_6.md`: isolamento delle condizioni;
- `../reports/walk_forward_coinbase_0_6.md`: walk-forward, PBO, DSR e ritardo;
- `../reports/coinbase_fee_0_6_comparison.md`: vecchia baseline e Buy & Hold con
  commissioni.

I report precedenti al 2026-07-27 sono archivio storico. Quando usano la parola
"baseline" si riferiscono alla baseline vigente alla data del singolo report,
non necessariamente alla Baseline ufficiale corrente.

## Cronologia essenziale

| Data | Decisione |
|---|---|
| 2026-06-28 | Promozione del filtro RSI65 e Trail8 confermato |
| 2026-06-30 | Uscita SMA50 portata a una candela |
| 2026-07-22 | Telegram reso esclusivamente LIVE |
| 2026-07-27 | Migrazione completa a Coinbase e congelamento vecchia baseline |
| 2026-07-27 | Promozione della nuova Baseline ufficiale dopo test completi allo 0,6% |
| 2026-08-28 | Promozione del breakout protetto come secondo percorso di ingresso |

## Controlli trasversali

Prima di ogni modifica ufficiale usare `BASELINE_SYNC_CHECKLIST.md`. Ogni
promozione deve aggiornare codice, test, `/conditions`, manifest, dashboard,
documenti correnti e pacchetto congelato, lasciando intatti i pacchetti storici.
