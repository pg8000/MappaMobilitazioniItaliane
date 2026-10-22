# Aggiornamento automatico (v2)

Tre tipi di evento, tre regole diverse.

| Tipo | Come entra nella mappa | Chi decide |
| --- | --- | --- |
| Scioperi | Ogni giorno una GitHub Action legge il [calendario MIT](https://scioperi.mit.gov.it/mit2/public/scioperi) e li aggiunge da sola | Nessuno: è la fonte ufficiale |
| Manifestazioni | L'Action cerca notizie e apre una *issue* "Proposta: …" con una bozza | Tu: correggi la bozza e metti l'etichetta `approva` |
| Eventi eccezionali (non preavvisati, vietati, scontri) | Solo a mano, modificando `data/eventi.json` | Tu, sempre |

## Come funziona

- `data/eventi.json` contiene gli eventi **curati a mano**. Non viene mai riscritto dall'automazione, se non quando approvi una proposta.
- `data/scioperi-mit.json` è generato ogni giorno da `tools/mit_scioperi.py`. Non modificarlo a mano: viene sovrascritto.
- `tools/build_page.py` unisce i due file e rigenera `index.html`. Se uno sciopero è già in `eventi.json` (stessa data, luogo e sigla) quello manuale vince e il doppione del MIT viene saltato.
- Se uno sciopero manuale con fonte MIT sparisce dal calendario (possibile revoca), il riepilogo dell'esecuzione (scheda *Actions*) lo segnala con "ATTENZIONE"; non viene cancellato da solo.
- Se il calendario MIT cambia struttura e non si legge più, l'esecuzione fallisce, GitHub ti manda una mail e la mappa resta all'ultimo aggiornamento buono.

## Approvare una manifestazione

1. Apri la issue "Proposta: …" (etichetta `proposta`) e la fonte collegata.
2. Controlla data, luogo e organizzatore. Se ne manca uno, chiudi la issue.
3. Modifica il blocco JSON nella issue: titolo neutro, `sector`, `who`, `orgs` (chiavi di `promotori` in `eventi.json`), `time`, `where`. Niente nomi di persone né numeri di partecipanti. I campi con "DA COMPILARE" bloccano l'approvazione.
4. Aggiungi l'etichetta `approva`. Entro un minuto l'evento è in `eventi.json`, la pagina si ricostruisce e la issue si chiude con un commento. Se qualcosa non va, il commento spiega cosa correggere e l'etichetta viene tolta.

Solo le issue create dall'automazione o dal proprietario del repo possono essere approvate. Le proposte non hanno `exc`: una manifestazione eccezionale non si approva da qui.

## Aggiungere un evento eccezionale

Apri `data/eventi.json`, copia un evento esistente con `exc` e cambia i campi. Servono: `exc.kind`, `exc.note` (cosa è successo, dove e quando, con la fonte; niente numeri di feriti o fermati, niente nomi), almeno una fonte in `src` (aggiungila prima in `fonti`) e `place` presente in `luoghi` (se manca, aggiungi coordinate). Al commit parte `valida.py`: se c'è un errore l'Action fallisce e la pagina non cambia.

## Provare in locale

```
python tools/valida.py
python tools/mit_scioperi.py          # scarica il calendario MIT (o: python tools/mit_scioperi.py pagina.html)
python tools/build_page.py            # rigenera index.html
python tools/proposte.py              # senza GITHUB_TOKEN stampa soltanto le proposte
```

## Limiti noti

- Il parser del calendario MIT è stato scritto sulla struttura descritta dalla pagina (tabella con colonne Inizio, Fine, Sindacati, Settore, …). Alla prima esecuzione controlla il riepilogo: "righe lette" deve essere simile al numero di scioperi nel calendario.
- Gli scioperi locali sono posizionati sul capoluogo di provincia (`data/province.json`); quelli senza provincia riconosciuta finiscono nella fascia degli scioperi senza punto, con l'area nel testo.
- Le proposte vengono da titoli di Google News: servono per accorgersi di un evento, non sostituiscono la verifica sulla fonte. Il link è quello di Google News e porta all'articolo.
- Le sigle dei sindacati sono riconosciute da un elenco; quelle non presenti compaiono come "Nessuna sigla identificata" con il testo originale in `who`. Per aggiungerne una: `ALIAS` in `tools/mit_scioperi.py` e `promotori` in `data/eventi.json`.
