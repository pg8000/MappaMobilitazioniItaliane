# Automazione dell’archivio 2026

## Percorso completo

1. `aggiorna.yml`: ogni giorno alle 05:30 UTC, oppure da Actions → Sincronizza archivio 2026 → Run workflow. Parte anche quando cambiano sorgenti e dati curati.
2. Validazione delle iniziative manuali e test senza rete.
3. `mit_scioperi.py`: invia al form pubblico MIT le date 01/01/2026–31/12/2026, con tutti gli stati. Legge anche gli eventi effettuati e revocati; normalizza intestazioni come `Settore*` e `Modalità`. Tre tentativi per gli errori di rete.
4. La risposta deve avere una tabella riconoscibile e date valide. In caso contrario non sovrascrive l’archivio precedente e interrompe la pubblicazione.
5. Le voci si identificano per data, categoria, sindacati, territorio, proclamazione e ricezione. Proclamazioni distinte restano distinte; una voce non riscontrata nella nuova risposta viene conservata con `not_in_latest`, senza inventarne la revoca.
6. `build_data.py` usa le righe MIT per gli scioperi già riassunti a mano, conservando le altre iniziative curate. `build_page.py` genera pagina, archivio unito e metadati della sincronizzazione.
7. `valida.py --archivio` controlla date, ID e riferimenti dell’archivio unito. Il bot salva dati e pagina nel ramo `main`.
8. Il workflow riutilizzabile `pubblica.yml` carica solo pagina e JSON pubblici e richiama `deploy-pages`. È richiamato direttamente sia dall’aggiornamento sia dall’approvazione: i commit del bot non devono generare un secondo workflow.

## Stati e conteggi

`official_status` distingue `in programma`, `effettuato`, `revocato`. La dicitura MIT «revocato» include sospensione e differimento: non si può inferire quale dei tre sia avvenuto senza un approfondimento. `not_in_latest` significa soltanto assenza nell’ultima risposta.

La vista iniziale esclude revoche e voci da riverificare. Il grafico conta voci dell’archivio, una volta ciascuna al primo giorno compreso nel filtro. Nel calendario, invece, uno sciopero di più giorni compare in ogni giorno in cui è attivo. Le due misure sono spiegate nella pagina.

La data di sincronizzazione indica l’ultima lettura riuscita del registro. Il timestamp non certifica la completezza delle manifestazioni curate a mano. `data/aggiornamento.json` consente a una pagina aperta di riconoscere una nuova versione ogni 15 minuti e al ritorno sulla scheda, conservando i filtri nell’URL.

## Manifestazioni ed eventi eccezionali

Nell’esecuzione programmata si cercano anche proposte di manifestazioni tramite notizie RSS. Non diventano eventi finché non vengono verificate. Nell’avvio manuale questa ricerca è facoltativa (`cerca_proposte`, inizialmente disattivata).

Per approvare una proposta: verificare la fonte, correggere il JSON nella issue, completare luogo/data/promotore e applicare `approva`. Il workflow controlla l’autore, rifiuta i dati incompleti, aggiunge l’evento, ricostruisce e pubblica. Gli eventi eccezionali vengono inseriti esclusivamente a mano in `data/eventi.json` con la relativa fonte; non si approvano automaticamente.

Le nuove iniziative devono ricadere nel 2026. Non si inventano date mancanti o informazioni non presenti nelle fonti.

## Recupero da un errore

Aprire l’esecuzione fallita in Actions, correggere fonte/parser/dati e avviare di nuovo il workflow. I dati precedenti restano nel repository e su Pages. Una nuova esecuzione riuscita aggiorna la dicitura in pagina. Concorrenza serializzata fra aggiornamenti e approvazioni; pubblicazioni serializzate separatamente.

Permessi dei workflow: scrittura contenuti per i commit, issue per le proposte, Pages e token OIDC per la pubblicazione. Si usa soltanto `GITHUB_TOKEN` fornito da GitHub, senza chiavi aggiuntive nei file.
