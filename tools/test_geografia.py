import unittest
from comuni import province
from geografia import arricchisci, LUOGHI_REGIONI
from build_data import unisci


class GeographyTests(unittest.TestCase):
    def test_all_registered_provinces_have_region(self):
        self.assertEqual(set(province()) - set(LUOGHI_REGIONI), set())

    def test_regional_multiregional_and_national(self):
        places = {'regione-sicilia': {'region':'Sicilia'}, 'a1': {}, 'roma': {}}
        events = [{'place':'regione-sicilia','scope':'regionale'}, {'place':'a1'},
                  {'scope':'nazionale','source_region':'Lazio'}, {'place':'unknown'}]
        arricchisci(places, events)
        self.assertEqual(events[0]['regions'], ['Sicilia'])
        self.assertEqual(events[1]['regions'], ['Emilia-Romagna','Toscana'])
        self.assertEqual(events[2]['regions'], [])
        self.assertEqual(events[3]['regions'], [])

    def test_archive_places_have_known_geography(self):
        archive = unisci()
        self.assertTrue(all(p['regions'] for p in archive['luoghi'].values()))
        self.assertTrue(all('regions' in e for e in archive['eventi']))
