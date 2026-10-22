# Automazione dell'archivio 2026

## Scioperi MIT e sito pubblico

`aggiorna.yml` parte ogni giorno alle 05:30 UTC, su modifica di sorgenti/dati e manualmente da Actions. Legge l'intero 2026 dal form storico MIT, esegue test e validazione, costruisce l'archivio, salva i dati e richiama direttamente `pubblica.yml`. Se il registro non è leggibile conserva l'ultima versione valida e segnala l'errore.

L'identità di una proclamazione MIT comprende date, categoria, sindacati, territorio, proclamazione e ricezione. `official_status` distingue in programma, effettuato e revocato. L'assenza dall'ultima risposta viene segnalata con `not_in_latest`, senza inventare una revoca. I conteggi sono voci d'archivio, non necessariamente mobilitazioni distinte. Le vecchie sintesi manuali MIT sono sostituite dalle proclamazioni ufficiali quando l'archivio è disponibile.

Gli eventi regionali senza provincia hanno un indicatore tratteggiato presso il capoluogo. `map_precision: region` e la nota specificano l'approssimazione. Non si inventano città per aree sconosciute o multiple.

## Manifestazioni ed eventi eccezionali

Ricerca, proposte e revisione vengono eseguite in un **repository privato separato**, ogni sei ore e su approvazione. La chat e il computer dell'utente non sono necessari.

Il processo consulta RSS e tenta la lettura delle pagine pubbliche. Google News serve soltanto alla scoperta. Date dedotte dal titolo, fonti non leggibili, informazioni discordanti e possibili doppioni richiedono revisione. Non si aggirano paywall e non si inventano dati mancanti.

Si pubblicano automaticamente soltanto eventi con dati strutturati espliciti Schema.org Event (data, città riconosciuta, organizzazione e stato), sostenuti da una fonte ufficiale/organizzatore ammessa o da due gruppi editoriali indipendenti con dati concordanti. Per gli episodi eccezionali servono una fonte ufficiale o due redazioni indipendenti e una data non futura. Il sistema è selettivo e non garantisce la copertura di tutte le manifestazioni.

I casi dubbi diventano issue **private**, con blocco JSON modificabile e fonti. Il proprietario o un collaboratore con scrittura può applicare `approva`. Il sistema rilegge la proposta, valida i dati e invia solamente la scheda approvata e i link pubblici. Una proposta scartata si chiude senza approvarla. Nessuna proposta riservata viene aperta nelle issue pubbliche; `tools/proposte.py` e il vecchio workflow pubblico di approvazione sono disattivati.

Il passaggio usa una chiave SSH dedicata: parte pubblica come deploy key con scrittura nel solo repository della mappa; parte privata nel segreto Actions `PUBLIC_MAP_DEPLOY_KEY` del repository privato. Il normale GITHUB_TOKEN del repository privato gestisce esclusivamente stato e issue private. La chiave di esportazione è disponibile solo nel passo che invia il file pubblico, con verifica dell'host SSH attiva.

## Dati pubblicabili e riservatezza

`data/eventi-verificati.json` contiene unicamente `versione`, `fonti` ed `eventi`, esportati da una lista esplicita di campi ammessi. Corpi e numeri delle issue, commenti, nomi dei revisori e motivi di verifica restano nel privato. `build_data.py` valida e unisce l'export alle iniziative manuali e all'archivio MIT; le coordinate delle nuove città provengono dalla tabella esistente delle province. Una modifica dell'export attiva l'aggiornamento e la pubblicazione pubblica.

Gli eventi eccezionali mantengono il formato `type: manifestazione` e `exc: {kind, note}`. Non si crea una categoria pubblica per i casi incerti. `event_status` distingue confermato, annullato, rinviato e riprogrammato. Annullati e rinviati sono esclusi dalla vista iniziale, consultabili tramite Stato eventi. Un aggiornamento approvato riutilizza l'ID della scheda già esportata da questa raccolta.

La pubblicazione Pages copia soltanto un elenco esplicito di JSON pubblici, mai file di lavoro o dati di revisione. La data MIT riguarda il registro ufficiale e non certifica la completezza delle manifestazioni. `data/aggiornamento.json` contiene la revisione e permette alla pagina aperta di aggiornarsi ogni 15 minuti conservando i filtri.

## Recupero da errori

Le proposte validate vengono conservate prima dell'invio. In caso di errore del collegamento non vengono chiuse come pubblicate: un'esecuzione privata con modo `verifica` ritenta l'export. Dopo il push riuscito la proposta viene chiusa e contiene il collegamento alle esecuzioni pubbliche per verificare la pubblicazione effettiva della pagina.

Aggiornamenti MIT e pubblicazioni pubbliche hanno code serializzate. Le esportazioni ritentano su un nuovo ramo corrente in caso di aggiornamenti concorrenti, modificando soltanto il file previsto. Nessuna cronologia viene forzata.

Le esecuzioni programmate GitHub possono subire ritardi. Al repository privato si applicano i limiti del piano dell'account: non vengono attivati upgrade o acquisti.
