import copy
import unittest
from unittest.mock import patch
from comuni import carica
from build_data import unisci


class VerifiedImportTests(unittest.TestCase):
    def setUp(self):
        self.base = carica("eventi.json")
        self.event = {"id": "ver-test", "type": "manifestazione", "scope": "locale", "sector": "Studenti", "start": "2026-10-24", "end": "2026-10-24", "place": "roma", "title": "Corteo verificato", "who": "Associazione", "orgs": ["non-identificato"], "src": ["ver-fonte"], "event_status": "annullato"}
        self.payload = {"versione": 1, "fonti": {"ver-fonte": {"nome": "Fonte pubblica", "url": "https://www.comune.roma.it/evento"}}, "eventi": [self.event]}

    def merge(self, payload):
        def read(name):
            return copy.deepcopy(self.base if name == "eventi.json" else payload if name == "eventi-verificati.json" else {"eventi": [], "luoghi": {}})
        with patch("build_data.DATA") as data, patch("build_data.carica", side_effect=read):
            data.__truediv__.return_value.exists.return_value = True
            return unisci()

    def test_valid_event_sources_status_and_existing_data_preserved(self):
        out = self.merge(self.payload)
        self.assertEqual(len(out["eventi"]), len(self.base["eventi"]) + 1)
        self.assertEqual(out["archive"]["verifiedCount"], 1)
        self.assertEqual(next(x for x in out["eventi"] if x["id"] == "ver-test")["event_status"], "annullato")
        self.assertIn("ver-fonte", out["base"]["fonti"])

    def test_missing_sources_and_unknown_type_abort_build(self):
        for change in ({"src": ["assente"]}, {"type": "sciopero"}, {"start": "2026-02-31"}):
            with self.subTest(change=change):
                payload = copy.deepcopy(self.payload)
                payload["eventi"][0].update(change)
                with self.assertRaises(ValueError):
                    self.merge(payload)

    def test_duplicate_id_aborts_build(self):
        payload = copy.deepcopy(self.payload)
        payload["eventi"].append(copy.deepcopy(self.event))
        with self.assertRaises(ValueError):
            self.merge(payload)


if __name__ == "__main__":
    unittest.main()
