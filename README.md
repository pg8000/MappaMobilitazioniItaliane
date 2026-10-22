# Piazze e scioperi d'Italia

Mappa di scioperi proclamati e manifestazioni annunciate in Italia, con gli eventi eccezionali
(manifestazioni non preavvisate o vietate, scontri) segnalati come tali. Ogni evento riporta la fonte.

**Sito:** https://pg8000.github.io/MappaMobilitazioniItaliane/

## Cosa contiene

| Percorso | Cosa è |
| --- | --- |
| `index.html` | La pagina pubblicata: un solo file, senza dipendenze esterne, senza cookie né tracciamento |
| `data/eventi.json` | Gli stessi dati in formato JSON, riutilizzabili (licenza CC BY 4.0) |
| `docs/PIANO.md` | Piano del progetto, con i criteri di inclusione degli eventi |
| `docs/RICERCA-E-FONTI.md` | Fonti consultate, eventi esclusi e motivazioni |
| `data/scioperi-mit.json` | Scioperi dal calendario MIT, aggiornati ogni giorno in automatico |
| `tools/` | Script dell'aggiornamento automatico e sorgente della pagina (`sorgente-artifact.html`) |
| `docs/AUTOMAZIONE.md` | Come funzionano scioperi automatici, proposte di manifestazioni ed eventi eccezionali |

## Criteri

- Solo eventi in Italia con data certa, luogo, promotore (o "non identificato") e almeno una fonte apribile.
- Scioperi verificati sul [calendario del Ministero dei Trasporti](https://scioperi.mit.gov.it/mit2/public/scioperi) quando vi compaiono.
- Descrizioni brevi e neutre; nessun nome di persone, nessun numero di feriti, fermati o partecipanti.

## Segnalare un errore

Usa il pulsante "Segnalalo qui" in fondo alla pagina o apri una [segnalazione](../../issues/new?template=correzione.yml).
Serve sempre il link a una fonte.

## Aggiornare la mappa

- **Scioperi**: automatico, ogni giorno, dal calendario MIT.
- **Manifestazioni**: l'automazione apre una issue "Proposta"; correggi la bozza e aggiungi l'etichetta `approva`.
- **Eventi eccezionali**: sempre a mano in `data/eventi.json`.

Dettagli in [docs/AUTOMAZIONE.md](docs/AUTOMAZIONE.md). Dopo ogni modifica a `data/eventi.json` la pagina si ricostruisce da sola.

## Licenze

Codice: MIT (`LICENSE`). Dati: CC BY 4.0 (`LICENSE-DATI.md`).
