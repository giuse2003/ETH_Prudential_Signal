# Project Status

Ultimo aggiornamento: 2026-07-27

## Stato corrente

- Nome metodologico pubblico: **ETH-USD Signal**.
- Repository e infrastruttura: `ETH_Prudential_Signal` e
  `eth-prudential-signal`.
- Fonte unica del modello: Coinbase Advanced Trade `ETH-USD`, candele DAILY UTC.
- Storico continuo canonico: dal `2016-05-23`.
- `ETH-EUR`: solo spot informativo nei contenuti LIVE.
- Baseline ETH invariata: cinque condizioni buy e due condizioni sell.
- Azioni pubbliche: `ACQUISTA`, `MANTIENI STATO ATTUALE`, `VENDI`.
- Baseline v1 congelata al `2026-07-26`, riproducibile offline.
- Run operativo: aggiornabile quotidianamente e tracciato da manifest/hash/run_id.

## Baseline v1

- directory: `docs/runs/baseline-v1-2026-07-26/`;
- valutazione: `2016-12-08`–`2026-07-26`;
- osservazioni: 3.518;
- rendimento totale strategia: `186.63524277301624`;
- rendimento annualizzato: `0.7215842468567129`;
- max drawdown: `-0.45887949067964284`;
- Sharpe: `1.3573838337263227`;
- trade completati: 36;
- win rate: `0.3611111111111111`;
- profit factor: `14.00916695086703`.

## Componenti operative

- `pipeline.py`: unica pipeline dati/modello/backtest/pubblicazione;
- `data/coinbase.py`: download a blocchi, retry, validazione e cache Coinbase;
- `reports/publication.py`: staging, manifest, hash e promozione transazionale;
- `freeze_baseline.py` e `reproduce.py`: congelamento e verifica offline;
- dashboard GitHub Pages: legge manifest e JSON dello stesso run;
- Cloudflare Worker: legge `live-status.json`, senza logica del modello;
- Telegram: solo LIVE PREVIEW stabilizzata, con cinque condizioni buy e due sell.

## Verifiche

- installazione da `requirements.lock` con `--require-hashes`;
- test unitari locali;
- sintassi JavaScript dashboard e Worker;
- riproduzione offline byte per byte;
- workflow Linux predisposto per test e riproduzione.

## Limiti aperti

- il deployment del Worker e la verifica Telegram pubblica richiedono il push e
  l'esecuzione dell'infrastruttura remota;
- nessun vero out-of-sample separato;
- costi, spread, slippage, imposte e rendimento cash esclusi;
- rischio di overfitting e dipendenza dalla qualita Coinbase.
