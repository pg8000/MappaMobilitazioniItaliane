# Aggiornamento di scope — archivio annuale (22 ottobre 2026)

Su richiesta del proprietario, la versione 2 estende tutti i tipi di evento al periodo **1 gennaio–31 dicembre 2026**. Sono approvati recupero storico e aggiornamento automatico dal MIT, calendario con intervallo di date, grafico dinamico e pubblicazione automatica GitHub Pages. Queste decisioni sostituiscono le limitazioni temporali e il divieto di automazione del piano v1 riportato sotto come documento storico.

Il registro annuale copre le proclamazioni dei trasporti e le iniziative generali che vi sono registrate, inclusi stati effettuato/revocato. Manifestazioni ed eventi eccezionali restano una raccolta curata non esaustiva; ogni iniziativa richiede una fonte. Gli eventi futuri possono entrare solo dopo l’annuncio. Sono mantenuti neutralità, assenza di dati personali e distinzione tra fonte, luogo fisico e ambito.

La pagina distingue i conteggi del calendario (voci attive nel giorno) da quelli del grafico (una voce per data di inizio, o primo giorno incluso nel filtro). Le revoche sono escluse di default, senza essere cancellate dallo storico.

---

# Mappa manifestazioni e scioperi in Italia – Piano di progetto

22 ottobre 2026

## Obiettivo e prodotto

Una pagina web pubblica con una mappa dell'Italia che mostra scioperi e manifestazioni annunciati dal 22 ottobre al 30 novembre 2026, ciascuno con data, luogo, organizzatori e link alla fonte.

- **Per chi:** cittadini, pendolari e giornalisti che vogliono sapere cosa succede, dove e quando.
- **Cosa mostra:** un indicatore per evento (scioperi e manifestazioni con colori diversi), gli scioperi nazionali in una fascia dedicata (non hanno un luogo unico), filtri per tipo e settore, elenco cronologico sotto la mappa.
- **Forma:** pagina singola autonoma, pubblicata su GitHub Pages.
- **Definizione di fatto:** ogni evento in mappa ha almeno una fonte verificabile e la pagina funziona su desktop e smartphone.

## Guardrail di scope

Ogni richiesta nuova passa dal test qui sotto: se non rientra nella colonna "Dentro", va in una lista "Versione 2" e non entra in questa consegna.

| Area | Dentro (v1) | Fuori (v1) |
| --- | --- | --- |
| Territorio | Solo Italia | Eventi all'estero, anche se riguardano l'Italia |
| Periodo | 22 ottobre – 30 novembre 2026 | Archivio storico; eventi dopo il 30 novembre. Eccezione: eventi eccezionali dal 1° ottobre |
| Tipi di evento | Scioperi proclamati (nazionali, regionali, locali), manifestazioni pubbliche annunciate (cortei, presidi, sit-in) ed eventi eccezionali: manifestazioni non preavvisate o vietate e scontri riportati dalla stampa, sempre segnalati come tali | Assemblee interne, eventi online, raccolte firme, convegni |
| Dati | Snapshot curato a mano, ogni evento con link alla fonte | Aggiornamento automatico, scraping, segnalazioni degli utenti |
| Contenuto | Fatti: cosa, dove, quando, chi organizza, fonte | Commenti, giudizi politici, stime di partecipazione non ufficiali |
| Funzioni | Mappa, filtri per tipo/settore, elenco cronologico | Account, notifiche, commenti, percorsi dei cortei, previsioni di disagi |
| Tecnologia | Una pagina HTML autonoma | Backend, database, app mobile, dominio dedicato |

**Regole operative**

1. Nessun evento senza fonte: se non c'è una fonte ufficiale o una testata riconoscibile, l'evento non entra.
2. Posizione onesta: un evento senza indirizzo preciso va sul capoluogo e la scheda lo dice; uno sciopero nazionale va nella fascia "nazionali", non su una città a caso.
3. Neutralità: descrizioni brevi e riprese dalla fonte, nessun aggettivo valutativo, tutte le sigle trattate allo stesso modo.
4. Data di aggiornamento sempre visibile e avviso che i dati possono cambiare (revoche, rinvii, precettazioni).
5. Tetto di lavoro: la v1 si chiude quando la checklist delle fasi è completa; ogni idea in più va nella lista v2.

## Fonti dati e criteri di inclusione

Gli scioperi vengono dai calendari ufficiali e dalle testate che li riprendono; le manifestazioni solo da comunicati degli organizzatori o da testate che ne riportano luogo e orario.

| Tipo | Fonte primaria | Fonti di controllo |
| --- | --- | --- |
| Scioperi trasporti | [Calendario scioperi MIT](https://scioperi.mit.gov.it/mit2/public/scioperi) | Meteo.it, Studenti.it, Virgilio, Scioperometro |
| Scioperi pubblico impiego | [Cruscotto scioperi PA](https://crusc-gepas.perlapa.gov.it/detail/2d0aea06-f6a4-44da-9da7-a2954e97f434) | Lentepubblica.it |
| Scioperi generali | Comunicati dei sindacati proclamanti (es. [USB](https://www.usb.it/leggi-notizia/30-ottobre-e-sciopero-generale-0817.html)) | ANSA, Sky TG24 |
| Manifestazioni | Comunicati degli organizzatori | ANSA, testate locali con luogo e orario |

**Un evento entra se:** ha data certa, luogo almeno a livello di comune (o è nazionale), un soggetto che lo organizza o lo proclama, e una fonte apribile.

**Un evento resta fuori se:** è solo un'ipotesi, non ha organizzatore noto, o la fonte è un post social non ripreso da nessuna testata. Fa eccezione un raduno annunciato e già riportato dalla stampa: entra con l'etichetta "da confermare".

## Modello dati e architettura

Tutto sta in una sola pagina HTML: i dati sono una lista di eventi scritta nella pagina, la mappa è disegnata in SVG senza servizi esterni.

| Campo | Contenuto | Esempio |
| --- | --- | --- |
| type | sciopero o manifestazione | sciopero |
| scope | locale, regionale, nazionale, multiregionale | locale |
| sector | settore o tema | Trasporto locale |
| place | chiave di PLACES (assente se nazionale) | napoli |
| start / end | date ISO | 2026-11-16 |
| time | testo come da fonte | 11:00–15:00 |
| title, who | testo breve dalla fonte | ANM Napoli; Filt-Cgil, Fit-Cisl… |
| where | dettaglio luogo/percorso (facoltativo) | Piazza della Repubblica → Fori Imperiali |
| src | chiavi di SRC (una o più) | meteo, studenti |
| tbc | evento non ancora confermato (facoltativo) | true per il Circo Massimo del 24/10 |
| pending | dettagli mancanti di un evento confermato | "città e orari non ancora annunciati" |
| area | area reale quando il punto è rappresentativo | "Tutta l'Emilia-Romagna; punto su Bologna" |
| exc | evento eccezionale: {kind, note} | {kind: "Scontri", note: descrizione con fonte} |
| orgs | promotori normalizzati (chiavi di ORGS) | ["filt-cgil", "fit-cisl"] |

- **Stato automatico:** la pagina calcola "in arrivo", "oggi" o "concluso" con la data di Roma, ricalcolata se la pagina resta aperta; i conclusi sono visibili ma sbiaditi, e un filtro li nasconde.
- **Mappa:** contorno dell'Italia semplificato incluso nella pagina; più eventi nello stesso luogo diventano un cerchio con il numero; gli eventi eccezionali hanno un rombo arancione separato.
- **Aggiornare:** si modifica la lista eventi e si ripubblica allo stesso link.

## Fasi di lavoro e checklist

1. **Definizione** — obiettivo, periodo, guardrail.
   - [x] Scope e regole di inclusione scritti in questo piano
2. **Raccolta dati** — calendari scioperi e notizie su manifestazioni.
   - [x] 36 eventi raccolti (v1.1), ognuno con almeno una fonte aperta; scioperi dei trasporti confrontati con il calendario MIT
   - [x] Esclusi gli eventi senza organizzatore noto (es. presidio in Piazza Santi Apostoli del 24/10)
3. **Costruzione** — mappa, filtri, pannello dettagli, fascia nazionale, agenda.
   - [x] Filtri per tipo, settore, conclusi
   - [x] Versione chiara e scura
4. **Verifica** — controllo su desktop (1280 px) e telefono (390 px).
   - [x] Nessun errore JavaScript, nessuno scorrimento orizzontale
   - [x] Etichette della mappa non sovrapposte
5. **Consegna**
   - [x] Pagina pronta per la pubblicazione
   - [ ] Validazione del responsabile
   - [ ] Condivisione pubblica (a scelta)

## Rischi, note legali e manutenzione

| Rischio | Effetto | Contromisura |
| --- | --- | --- |
| Sciopero revocato o precettato | La mappa mostra un evento che non c'è | Avviso in pagina, link al calendario MIT, aggiornamento settimanale |
| Manifestazioni non preavvisate | La mappa è incompleta | Dichiarato nel testo: solo eventi annunciati |
| Percezione di parzialità | Contestazioni sulla neutralità | Criteri uguali per tutti, testo preso dalle fonti, nessun commento |
| Dati personali | Rischio privacy | Solo organizzazioni, nessun nome di persone fisiche |
| Precisione geografica | Punto in un luogo sbagliato | Punto sul comune, dettaglio del percorso solo nel testo |

**Manutenzione:** un aggiornamento a settimana (lista eventi + data in testata) finché la mappa resta pubblica. Alla scadenza del 30 novembre si decide se estendere il periodo o archiviare la pagina.

## Modifiche di scope

Il 22 ottobre il responsabile del progetto ha esteso lo scope della v1 agli eventi eccezionali; la decisione è registrata qui, come previsto dai guardrail.

| Data | Decisione | Regole aggiunte |
| --- | --- | --- |
| 22 ottobre 2026 | Inserire manifestazioni non autorizzate e scontri, a partire dal 1° ottobre | Simbolo a rombo arancione sulla mappa, riquadro "Evento eccezionale" in ogni scheda, filtro dedicato |
| 22 ottobre 2026 | Aggiungere il filtro per promotore (singola sigla o famiglia sindacale) | Sigle normalizzate in ORGS; conteggio degli scioperi per sigla nel menu |
| 22 ottobre 2026 | Applicare le 9 correzioni della revisione Codex | Dati allineati al calendario MIT, esclusioni separate per sigla, area reale per i punti rappresentativi |

**Criteri per un evento eccezionale:** almeno una testata nazionale riporta che la manifestazione non era preavvisata o era vietata, oppure riporta scontri con le forze dell'ordine o devastazioni. Niente numeri di feriti, fermati, arresti o partecipanti: non è lo scopo della mappa. Si descrive solo cosa è successo, dove e quando, con la fonte. Nessun nome di persone fisiche.

## Consegna per validazione

La versione 1.1 contiene 36 eventi: 9 eccezionali, 18 scioperi e manifestazioni locali o regionali e 9 nazionali o multiregionali.

**Da verificare in validazione**

- [ ] Il periodo (22 ottobre – 30 novembre) va bene
- [ ] Gli eventi "da confermare" (Circo Massimo, corteo anarchico e Blocco Studentesco a Milano, tutti del 24/10) devono restare visibili
- [ ] La resa degli eventi eccezionali (rombo arancione, riquadro nella scheda) è abbastanza chiara

**Versione 2 (avviata il 22 ottobre 2026):** aggiornamento automatico degli scioperi dal calendario MIT, manifestazioni come proposte da approvare, eventi eccezionali sempre manuali. Vedi `docs/AUTOMAZIONE.md`. Resta fuori: confini regionali dettagliati, percorsi dei cortei.
