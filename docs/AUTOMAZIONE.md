# Funzionamento delle automazioni

## Scioperi MIT

Il workflow **Sincronizza archivio 2026** consulta ogni giorno alle 05:30 UTC il registro annuale MIT. Può essere avviato anche da GitHub Actions. Il processo acquisisce i dati disponibili, ne controlla la coerenza, ricostruisce l’archivio e pubblica la pagina con GitHub Pages.

I runner GitHub usano il [relay MIT dedicato](../tools/mit_relay.py) per il registro annuale e l'RSS. Il relay è raggiungibile pubblicamente ma risponde solo a richieste con un token temporaneo firmato da GitHub per questo repository e il ramo `main`; senza token restituisce `401`. Può consultare soltanto i due endpoint MIT previsti. Il workflow prova il collegamento diretto se il relay fallisce e, se entrambi non rispondono, conserva l'ultima copia valida e la sua data. Il controllo di freschezza segnala un errore quando entrambe le acquisizioni mancano da oltre 36 ore.

Il relay è gestito nel progetto Sites **Relay MIT per la mappa** dell'account proprietario. Se il progetto viene disattivato o cambia indirizzo, occorre aggiornare l'indirizzo sia nel client del repository sia nella verifica del token nel relay.

L’identità di una proclamazione comprende date, categoria, sindacati, territorio, proclamazione e ricezione. Gli stati ufficiali distinguono eventi in programma, effettuati e revocati. Una voce assente dall’ultima risposta rimane distinta da una revoca.

## Feed RSS integrativo

Il feed ufficiale MIT viene consultato anche quando il registro annuale non è disponibile. Usa le date di inizio e fine dello sciopero e un identificativo stabile per riconoscere le voci già archiviate.

Il collegamento con lo storico tiene conto della diversa precisione delle date tra le due fonti. Una corrispondenza ambigua viene segnalata senza fondere proclamazioni distinte o aggiungere possibili duplicati.

Il feed non sostituisce gli stati ufficiali del registro annuale. Una voce assente dall’RSS non viene cancellata né revocata.

## Ricerca delle manifestazioni

La raccolta privata consulta le fonti ogni sei ore. La ricerca alterna i gruppi editoriali e comprende feed nazionali, regionali e locali e ricerche mirate.

Le bozze che eccedono il limite delle schede aperte rimangono in una coda privata. Quando si liberano posti vengono inviate alla revisione. Le bozze in attesa non sono eventi pubblici e non mantengono automaticamente una precedente idoneità alla pubblicazione senza una nuova verifica delle fonti.

Google News serve alla scoperta; le schede pubblicate collegano gli articoli originali. I blocchi di accesso e gli abbonamenti non vengono aggirati.

## Approvazione e pubblicazione

Il proprietario o un collaboratore con permesso di scrittura può approvare una proposta completa. Il sistema rilegge la scheda, controlla dati e duplicati e prepara l’esportazione.

La pubblicazione automatica richiede dati strutturati espliciti su evento, data, luogo, organizzazione e stato. Servono una fonte ufficiale o dell’organizzatore ammessa, oppure due gruppi editoriali indipendenti concordanti. Per gli episodi eccezionali non è ammessa una data futura.

Annullamenti, rinvii, informazioni discordanti e possibili duplicati richiedono revisione. Gli aggiornamenti delle schede già pubblicate riutilizzano il relativo identificativo.

## Riservatezza

Il repository privato conserva bozze, discussioni e informazioni di revisione. L’esportazione contiene soltanto gli eventi approvati e le relative fonti pubbliche, selezionati tramite un elenco di campi ammessi.

La chiave dedicata all’esportazione autorizza la scrittura nel solo repository della mappa. La verifica dell’host SSH rimane attiva. La pubblicazione GitHub Pages comprende esclusivamente i file pubblici previsti.

## Disponibilità delle fonti

Se una fonte non risponde, vengono conservati i dati validi e la data dell’ultima verifica riuscita. Una pubblicazione della pagina può completarsi usando l’archivio conservato: il suo esito non dimostra da solo che tutte le fonti siano state aggiornate.

Le proposte validate restano recuperabili anche se l’invio fallisce. Vengono contrassegnate come pubblicate soltanto dopo l’esportazione riuscita.

La data della verifica MIT riguarda il registro ufficiale e non certifica la completezza delle manifestazioni. La pagina controlla periodicamente la revisione dei dati e conserva i filtri durante l’aggiornamento.

Le esecuzioni programmate possono subire ritardi e sono soggette ai limiti del piano GitHub. Il funzionamento non richiede che il computer dell’utente o l’app siano aperti.

