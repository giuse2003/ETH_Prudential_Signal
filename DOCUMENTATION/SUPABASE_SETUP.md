# Configurazione Supabase per gli iscritti Telegram

Questa guida copre la Fase 1 della roadmap:

- creazione del progetto Supabase;
- creazione sicura della tabella degli iscritti;
- recupero delle credenziali server;
- verifica iniziale.

Non inserire token o chiavi Supabase nei file del repository.

## 1. Accedi a Supabase

1. Apri <https://supabase.com/dashboard>.
2. Accedi oppure crea un account.
3. Seleziona il progetto Supabase condiviso. Se oggi si chiama
   `btc-prudential-signal`, rinominalo con un nome neutro, ad esempio
   `crypto-prudential-signal`.

## 2. Progetto Supabase

Per il progetto ETH non e obbligatorio creare un secondo progetto Supabase.
La configurazione corrente usa una tabella dedicata:

```text
public.telegram_subscribers_eth
```

Quindi puoi riusare lo stesso progetto Supabase senza mescolare gli iscritti
BTC e ETH. Se il progetto esistente si chiama `btc-prudential-signal`,
rinominalo in `crypto-prudential-signal` o in un altro nome neutro prima di
proseguire.

Se invece vuoi isolamento totale tra i due progetti, crea un nuovo progetto
Supabase con:

```text
Name: eth-prudential-signal
Region: una regione europea vicina, ad esempio Frankfurt
```

La password del database non serve al codice attuale, ma va conservata in un
password manager se crei un nuovo progetto.

### Rinominare il progetto Supabase esistente

Nel pannello Supabase:

1. apri il progetto `btc-prudential-signal`;
2. vai in **Project Settings**;
3. apri la sezione **General**;
4. modifica il nome del progetto in `crypto-prudential-signal`;
5. salva.

Il rename cambia il nome visualizzato nel pannello Supabase. Non dovrebbe
cambiare il Project URL o il project ref usato dalle API.

## 3. Crea la tabella

1. Nel progetto Supabase apri **SQL Editor**.
2. Premi **New query**.
3. Apri nel repository:

```text
supabase/telegram_subscribers.sql
```

4. Copia l'intero contenuto nel SQL Editor del progetto Supabase scelto.
5. Premi **Run**.

Lo script:

- crea `public.telegram_subscribers_eth`;
- usa una tabella ETH dedicata, cosi gli iscritti non si mescolano con
  eventuali iscritti del progetto BTC anche se viene riusato lo stesso progetto
  Supabase;
- usa `telegram_chat_id` come chiave primaria e impedisce duplicati;
- registra consenso, iscrizione e disiscrizione;
- prepara campi per errori di consegna;
- aggiorna automaticamente `updated_at`;
- abilita e forza Row Level Security;
- revoca ogni accesso ad `anon` e `authenticated`;
- concede accesso soltanto a `service_role`.

## 4. Verifica il risultato

Alla fine dello script, la prima query deve restituire:

```text
table_name                rls_enabled   rls_forced
telegram_subscribers_eth  true          true
```

La seconda query, relativa alle policy, deve restituire zero righe.

Puoi anche aprire **Table Editor** e verificare la presenza della tabella:

```text
telegram_subscribers_eth
```

La tabella inizialmente deve essere vuota.

## 5. Recupera URL e chiave server

Nel pannello Supabase apri:

```text
Project Settings > API
```

Recupera:

```text
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
```

Nel pannello piu recente i nomi possono apparire come:

```text
Project URL
service_role secret
```

La service role:

- deve essere usata soltanto dal Cloudflare Worker e da eventuali job backend
  GitHub Actions esplicitamente autorizzati;
- non deve essere inserita nella dashboard web;
- non deve essere aggiunta al repository;
- non deve essere inviata in chat;
- non deve essere mostrata nei log.

Non usare la chiave `anon` o `publishable` per il backend degli iscritti.

## 6. Cosa non fare ancora

Non aggiungere le credenziali al frontend o ai file versionati. La
configurazione operativa va eseguita nei secret del Worker Cloudflare, dopo
aver verificato lo script SQL.

Non inserire manualmente righe nella tabella. La prima iscrizione verra creata
dal comando `/iscrivimi`.

## 7. Conferma necessaria

Quando hai completato i passaggi, comunica soltanto:

```text
Progetto Supabase rinominato in crypto-prudential-signal.
Script SQL eseguito.
Tabella telegram_subscribers_eth presente.
RLS enabled: true.
RLS forced: true.
Policy trovate: 0.
```

Non comunicare URL, chiavi, password o altri secret.

## 8. Verifica dopo i secret Cloudflare

Dopo aver configurato `SUPABASE_URL` e `SUPABASE_SERVICE_ROLE_KEY` nel Worker,
questi endpoint devono rispondere:

```text
GET https://eth-prudential-signal.giuse2003.workers.dev/subscribers/health
GET https://eth-prudential-signal.giuse2003.workers.dev/subscribers/count
```

`/subscribers/health` non espone secret: mostra solo booleani di configurazione
e il nome tabella. `/subscribers/count` deve restituire:

```json
{"active_subscribers": 0}
```

oppure un numero maggiore se esistono gia iscritti attivi.

### Caricamento secret da variabili d'ambiente locali

Se vuoi evitare di incollare secret nella chat, imposta le variabili in una
console PowerShell locale:

```powershell
$env:SUPABASE_URL="https://<project-ref>.supabase.co"
$env:SUPABASE_SERVICE_ROLE_KEY="<service-role-secret>"
```

Poi esegui:

```powershell
.\scripts\configure_supabase_worker_secrets.ps1
```

Lo script carica i secret nel Worker Cloudflare tramite Wrangler e non stampa i
valori.

## Motivazione della sicurezza

La tabella si trova nel schema `public`, esposto dalle API Supabase, ma RLS e
attiva senza policy per utenti pubblici. Le chiavi client non possono quindi
leggere o modificare gli iscritti.

L'accesso avverra esclusivamente dal backend con la service role. La
documentazione Supabase specifica che le service key possono bypassare RLS e
non devono mai essere esposte nel browser o ai clienti.

Fonti ufficiali:

- <https://supabase.com/docs/guides/database/postgres/row-level-security>
- <https://supabase.com/docs/guides/getting-started/api-keys>
