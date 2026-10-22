"""Regressioni dell'import annuale e della fusione dei dati (senza rete)."""
import datetime as dt
import unittest
from unittest.mock import patch
from comuni import carica, province, posizione_regionale, REGIONI
from mit_scioperi import leggi_righe, converti
from build_data import unisci


class ArchiveTests(unittest.TestCase):
    def setUp(self):
        self.base = carica("eventi.json")
        self.prov = province()

    def row(self, **extra):
        return {"inizio": "07/01/2026", "fine": "07/01/2026", "sindacati": "FILT-CGIL",
                "settore": "Ferroviario", "categoria": "PERSONALE FERROVIARIO",
                "modalita": "8 ORE: DALLE 09.00 ALLE 17.00", "rilevanza": "Locale",
                "regione": "Emilia-Romagna", "provincia": "Bologna", "stato": "Effettuato", **extra}

    def test_heading_star_and_accent(self):
        rows = leggi_righe('<table><tr><th>Stato</th><th>Inizio</th><th>Sindacati</th><th>Settore*</th><th>Modalità</th></tr><tr><td>Effettuato</td><td>07/01/2026</td><td>USB</td><td>Aereo</td><td>4 ore</td></tr></table>')
        self.assertEqual(rows[0]["settore"], "Aereo")
        self.assertEqual(rows[0]["modalita"], "4 ore")

    def test_not_a_result_table(self):
        self.assertEqual(leggi_righe('<html><h1>Manutenzione</h1></html>'), [])

    def test_january_is_not_discarded_in_october(self):
        es, _, bad = converti([self.row()], self.base, self.prov, dt.date(2026, 10, 22))
        self.assertEqual(bad, 0)
        self.assertEqual(es[0]["start"], "2026-01-07")
        self.assertEqual(es[0]["sector"], "Treni")
        self.assertEqual(es[0]["time"], "8 ORE: DALLE 09.00 ALLE 17.00".capitalize())

    def test_revocation_kept(self):
        es, _, _ = converti([self.row(stato="Revocato (sospeso)")], self.base, self.prov, dt.date(2026, 10, 22))
        self.assertEqual(es[0]["official_status"], "revocato")

    def test_declarations_same_date_are_distinct(self):
        a = self.row(**{"data ricezione": "01/01/2026 10:00"})
        b = self.row(**{"data ricezione": "02/01/2026 10:00"})
        es, _, _ = converti([a, b], self.base, self.prov, dt.date(2026, 10, 22))
        self.assertNotEqual(es[0]["id"], es[1]["id"])

    def test_no_silent_invalid_date(self):
        es, _, bad = converti([self.row(inizio="31/02/2026")], self.base, self.prov, dt.date(2026, 10, 22))
        self.assertEqual(es, [])
        self.assertEqual(bad, 1)

    def test_notes_and_source_retained(self):
        es, _, _ = converti([self.row(note="ESCLUSO IL SETTORE AEREO")], self.base, self.prov, dt.date(2026, 10, 22))
        self.assertEqual(es[0]["note"], "ESCLUSO IL SETTORE AEREO")
        self.assertEqual(es[0]["src"], ["mit"])

    def test_year_boundaries(self):
        es, _, _ = converti([self.row(inizio="04/12/2026", fine="04/12/2026"), self.row(inizio="15/01/2027", fine="15/01/2027")], self.base, self.prov, dt.date(2026, 10, 22))
        self.assertEqual(len(es), 1)
        self.assertEqual(es[0]["start"], "2026-12-04")

    def test_regional_strikes_without_province_have_markers(self):
        for region in REGIONI:
            with self.subTest(region=region):
                es, places, _ = converti([self.row(regione=region, provincia="Tutte", rilevanza="Regionale")], self.base, self.prov, dt.date(2026, 10, 22))
                self.assertEqual(places[es[0]["place"]]["kind"], "region")
                self.assertEqual(places[es[0]["place"]]["region"], region)
                self.assertIn("non luogo puntuale", es[0]["area"])

    def test_local_marker_and_national_scope_are_preserved(self):
        es, places, _ = converti([self.row(), self.row(rilevanza="Nazionale", regione="Italia", provincia="Tutte")], self.base, self.prov, dt.date(2026, 10, 22))
        self.assertEqual(es[0]["place"], "bologna")
        self.assertNotIn("place", es[1])
        self.assertNotIn("kind", places[es[0]["place"]])

    def test_regional_fallback_is_idempotent_and_not_guessed(self):
        places = {}
        original = {"scope": "regionale", "source_region": "Sicilia", "area": "Sicilia"}
        result = posizione_regionale(original, places, self.prov)
        self.assertNotIn("place", original)
        self.assertEqual(posizione_regionale(result, places, self.prov), result)
        unknown = {"scope": "regionale", "source_region": "Sicilia e Calabria"}
        self.assertEqual(posizione_regionale(unknown, places, self.prov), unknown)

    def test_official_rows_replace_old_summaries_only_when_available(self):
        mit_event = self.row()
        with patch('build_data.carica', side_effect=lambda n: self.base if n == 'eventi.json' else {"fonti": {}, "eventi": []} if n == 'eventi-verificati.json' else {"eventi": [dict(mit_event, id="test", start="2026-01-07", official_status="effettuato")]}):
            result = unisci()
        expected = 1 + sum(not (e['type'] == 'sciopero' and 'mit' in e.get('src', [])) for e in self.base['eventi'])
        self.assertEqual(len(result['eventi']), expected)
        self.assertTrue(all(not (e.get('type') == 'sciopero' and 'mit' in e.get('src', [])) for e in result['eventi'] if e['id'] != 'test'))


if __name__ == '__main__':
    unittest.main()
