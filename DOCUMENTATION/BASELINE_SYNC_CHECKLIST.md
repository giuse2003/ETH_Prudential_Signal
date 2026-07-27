# Baseline Sync Checklist

## Dati

- [ ] Il modello usa soltanto Coinbase `ETH-USD`.
- [ ] La cache parte dal `2016-05-23`, e ordinata e senza buchi.
- [ ] La candela UTC corrente e esclusa dal DAILY.
- [ ] `ETH-EUR` e soltanto spot informativo.
- [ ] Non esistono fallback Yahoo nella pipeline runtime.

## Modello

- [ ] Sono presenti esattamente cinque condizioni `ACQUISTA` e due `VENDI`.
- [ ] RSI 65 limita solo i nuovi ingressi.
- [ ] `Close < SMA50` vende dopo una candela.
- [ ] Il trailing 8% conserva le conferme momentum/volume.
- [ ] La vendita ha precedenza.
- [ ] Le sole azioni sono `ACQUISTA`, `MANTIENI STATO ATTUALE`, `VENDI`.

## Pacchetto

- [ ] Tutti i JSON condividono lo stesso `run_id`.
- [ ] `raw_candles.csv` coincide con l'hash di provenienza.
- [ ] Ogni artefatto e presente nel manifest con hash e dimensione.
- [ ] Dashboard e Worker non ricalcolano il modello.
- [ ] Una pubblicazione incompleta non sostituisce il pacchetto precedente.

## Riproducibilita

- [ ] Python coincide con `.python-version`.
- [ ] L'installazione `--require-hashes` riesce.
- [ ] I test sono verdi.
- [ ] `reproduce.py` riesce offline da checkout pulito.
- [ ] Il tag della baseline coincide con il manifest e non viene spostato.

## Pubblicazione

- [ ] Il manifest operativo indica il commit realmente eseguito.
- [ ] GitHub Actions Linux e verde.
- [ ] GitHub Pages mostra il pacchetto ETH corrente.
- [ ] Il Worker e stato distribuito e `/segnale` verificato.
- [ ] Telegram mostra cinque buy, due sell e icone rosse/verdi.
