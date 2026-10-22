# Piazze e scioperi d’Italia — archivio 2026

[Apri la mappa](https://pg8000.github.io/MappaMobilitazioniItaliane/)

Archivio dal **1° gennaio al 31 dicembre 2026**: proclamazioni del registro MIT (trasporti e mobilitazioni generali presenti nel registro), più manifestazioni ed eventi eccezionali curati a mano. Le fonti sono collegate nelle schede. Le iniziative future possono essere presenti solo quando annunciate: non è una previsione né un censimento esaustivo di tutte le manifestazioni italiane.

## Esplorazione

- Calendario mensile navigabile, selezione del giorno o di un intervallo; pulsanti per mese e anno intero.
- Grafico dinamico per giorno, settimana o mese, con serie distinte e tabella accessibile. Una barra filtra il periodo.
- Filtri per tipo, settore, promotore, eventi conclusi e stato ufficiale MIT.
- Le revoche sono archiviate e consultabili, escluse dalla vista iniziale. Una voce assente dall’ultima verifica è distinta da una revoca.
- Agenda paginata, mappa e schede condividono i filtri. Il calendario conta le voci attive nel giorno; il grafico conta ogni voce una volta, al primo giorno incluso nel periodo.
- I filtri si conservano nell’URL e sono condivisibili. Una pagina aperta verifica ogni 15 minuti se esiste una nuova versione e si aggiorna conservando i filtri.

Le righe MIT sono **proclamazioni distinte**, anche quando più dichiarazioni riguardano una stessa mobilitazione. I conteggi non misurano partecipanti, adesioni o disagi. Le iniziative inserite a mano non coprono sistematicamente tutti i mesi.

## Dati e fonti

Gli eventi regionali senza provincia sono visibili con un **cerchio tratteggiato** presso il capoluogo: etichetta e scheda specificano che è un indicatore regionale, non un luogo puntuale. Gli eventi nazionali e le aree non riconoscibili rimangono nell’elenco senza una città inventata. Il riepilogo distingue eventi in mappa e senza punto unico.

| File | Contenuto |
| --- | --- |
| `data/eventi.json` | Iniziative curate e vecchie schede MIT conservate come riferimento |
| `data/scioperi-mit.json` | Archivio ufficiale annuale con stato, note, provenienza e ultima verifica |
| `data/archivio.json` | Archivio effettivo unito, dati riutilizzabili della pagina |
| `data/aggiornamento.json` | Stato dell’ultima sincronizzazione riuscita e revisione della pagina |
| `data/province.json` | Coordinate approssimate dei capoluoghi |
| `tools/sorgente-artifact.html` | Sorgente dell’interfaccia; il generatore vi inserisce i dati correnti |

Quando l’archivio MIT annuale è disponibile, le vecchie schede manuali con fonte MIT sono sostituite dalle righe ufficiali. Non si eliminano proclamazioni solo perché hanno la stessa data, provincia o una sigla in comune.

## Aggiornamento e pubblicazione automatici

Il workflow **Sincronizza archivio 2026** si esegue ogni giorno alle **05:30 UTC** (06:30 in Italia con ora solare, 07:30 con ora legale), su modifica dei sorgenti/dati e manualmente da Actions. Recupera l’intero 2026 dal form storico MIT, esegue test e validazione, ricostruisce la pagina, salva i risultati e richiama esplicitamente il workflow **Pubblica la mappa**. La pubblicazione non dipende da un nuovo evento `push` generato dal bot.

Se il registro non è leggibile, il processo fallisce e conserva i dati e il sito dell’ultima esecuzione riuscita. Le manifestazioni vengono proposte per revisione; gli eventi eccezionali restano manuali. Vedi [AUTOMAZIONE](docs/AUTOMAZIONE.md).

## Prove locali

Python 3.12+, nessuna dipendenza Python esterna:

```sh
python tools/valida.py
python -m unittest discover -s tools -p 'test_*.py'
python tools/mit_scioperi.py
python tools/build_page.py
python tools/valida.py --archivio
```

Il downloader accetta anche un file HTML MIT salvato come argomento, per una prova senza rete. Aprire `index.html` per la pagina statica; la verifica automatica delle nuove versioni richiede HTTP/HTTPS.

[Segnala una correzione](https://github.com/pg8000/MappaMobilitazioniItaliane/issues/new?template=correzione.yml), sempre con una fonte.

Codice: MIT (`LICENSE`). Dati: CC BY 4.0 (`LICENSE-DATI.md`); fonti originali attribuite nelle singole voci. Nessun cookie o tracciamento dei visitatori.
