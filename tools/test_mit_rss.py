"""Regressioni RSS MIT: GUID, archivio storico, stati e guasti di rete."""
import copy
import datetime as dt
import io
import unittest
from contextlib import redirect_stdout, redirect_stderr
from unittest.mock import patch
from comuni import carica, province
import mit_scioperi as mit


def item(guid="8587", start="27/10/2026", end="27/10/2026", category="PERSONALE TEST"):
    return f'''<item><title>Data inizio: {start} - Settore: Ferroviario - Rilevanza: Nazionale - Regione: Italia - Provincia: Tutte</title>
    <description><![CDATA[modalità: 4 ORE: DALLE 08.00 ALLE 12.00<br/>Data fine: {end}<br/>Settore: Ferroviario<br/>Rilevanza: Nazionale<br/>Regione: Italia<br/>Provincia: Tutte<br/>Sindacati: USB<br/>Categoria interessata: {category}<br/>Data proclamazione: 05/10/2026<br/>Data ricezione: 05/10/2026]]></description>
    <pubDate>Mon, 26 Oct 2026 23:00:00 +0000</pubDate><guid>http://scioperi.mit.gov.it/{guid}</guid></item>'''


def feed(*items):
    return '<rss version="2.0"><channel>' + ''.join(items) + '</channel></rss>'


class RssTests(unittest.TestCase):
    def setUp(self):
        self.base, self.prov = carica('eventi.json'), province()
        self.rows = mit.leggi_rss(feed(item()))
        self.events, self.places, _ = mit.converti(self.rows, self.base, self.prov, dt.date(2026, 10, 26))
        self.previous = {'eventi': [], 'luoghi': {}, 'anno': 2026,
                         'sincronizzato': '2026-10-23T10:23:04+00:00', 'righe_lette': 494}

    def merge(self, previous=None, events=None, stamp='2026-10-26T20:00:00+00:00'):
        return mit.fondi_rss(previous if previous is not None else self.previous,
                            events if events is not None else self.events, self.places, 1, stamp)

    def test_event_dates_not_publication_date(self):
        self.assertEqual(self.events[0]['start'], '2026-10-27')
        self.assertEqual(self.events[0]['time'], '4 ore: dalle 08.00 alle 12.00')
        self.assertEqual(self.events[0]['mit_guid'], '8587')

    def test_guid_required_valid_unique(self):
        for xml in (feed(item(guid='')), feed(item(guid='../evil')), feed(item(), item()),
                    feed(item(end='26/10/2026')), feed(item(start='31/02/2026'))):
            with self.subTest(xml=xml), self.assertRaises(ValueError):
                mit.leggi_rss(xml)
        self.assertEqual(mit.normalizza_guid('https://scioperi.mit.gov.it/8587'), '8587')

    def test_unsafe_or_wrong_xml_rejected(self):
        for xml in ('<html/>', '<rss><channel/></rss>', '<!DOCTYPE rss><rss/>', 'x' * 2_000_001):
            with self.assertRaises(ValueError):
                mit.leggi_rss(xml)

    def test_repeated_feed_and_changed_description_use_same_guid(self):
        first = self.merge()
        changed = dict(self.events[0], source_category='PERSONALE TEST AGGIORNATO', title='Test aggiornato')
        second = self.merge(first, [changed])
        self.assertEqual(len(second['eventi']), 1)
        self.assertEqual(second['eventi'][0]['id'], 'mit-rss-8587')
        self.assertEqual(second['eventi'][0]['title'], 'Test aggiornato')
        self.assertEqual(second['rss_added'], 0)

    def test_historical_receipt_time_whitespace_and_revocation_preserved(self):
        old = dict(self.events[0], id='mit-storico', received_at='05/10/2026 16:37',
                   source_category='PERSONALE  TEST', official_status='revocato', verified_at='2026-10-23')
        old.pop('mit_guid')
        previous = dict(self.previous, eventi=[old])
        before = copy.deepcopy(previous)
        result = self.merge(previous)
        self.assertEqual(len(result['eventi']), 1)
        linked = result['eventi'][0]
        self.assertEqual(linked['id'], old['id'])
        self.assertEqual(linked['mit_guid'], '8587')
        for key in old:
            self.assertEqual(linked[key], old[key])
        self.assertEqual(previous, before)
        self.assertEqual(result['sincronizzato'], previous['sincronizzato'])
        self.assertEqual(result['righe_lette'], 494)

    def test_absence_does_not_remove_or_revoke(self):
        old = dict(self.events[0], id='mit-other', start='2026-01-01', end='2026-01-01', official_status='effettuato')
        old.pop('mit_guid')
        result = self.merge(dict(self.previous, eventi=[old]))
        self.assertIn(old, result['eventi'])
        self.assertEqual(len(result['eventi']), 2)

    def test_ambiguous_historical_matches_not_merged_or_duplicated(self):
        a = dict(self.events[0], id='mit-a', received_at='05/10/2026 10:00')
        b = dict(a, id='mit-b', received_at='05/10/2026 11:00')
        a.pop('mit_guid'); b.pop('mit_guid')
        result = self.merge(dict(self.previous, eventi=[a, b]))
        self.assertEqual(result['eventi'], [a, b])
        self.assertEqual(result['rss_ambiguous'], 1)

    def test_different_guids_not_merged(self):
        first = self.merge()
        result = self.merge(first, [dict(self.events[0], mit_guid='8588')])
        self.assertEqual(len(result['eventi']), 2)

    def test_full_search_promotes_rss_record_and_restores_official_status(self):
        first = self.merge()
        annual = dict(self.events[0], id='mit-annual', official_status='revocato', received_at='05/10/2026 16:37')
        annual.pop('mit_guid')
        result = mit.riconcilia_annuale([annual], first['eventi'])
        self.assertEqual(result[0]['id'], 'mit-rss-8587')
        self.assertEqual(result[0]['mit_guid'], '8587')
        self.assertEqual(result[0]['official_status'], 'revocato')
        self.assertNotIn('source_feed', result[0])
        self.assertEqual(self.merge(dict(self.previous, eventi=result))['eventi'][0]['official_status'], 'revocato')

    def test_full_search_distinct_receipt_times_remain_distinct(self):
        first = self.merge()
        annual = [dict(self.events[0], id='mit-a', received_at='05/10/2026 10:00'),
                  dict(self.events[0], id='mit-b', received_at='05/10/2026 11:00')]
        for e in annual:
            e.pop('mit_guid')
        result = mit.riconcilia_annuale(annual, first['eventi'])
        self.assertEqual([e['id'] for e in result], ['mit-a', 'mit-b'])

    def test_outage_and_invalid_xml_do_not_save(self):
        for failure in (TimeoutError('test'), ValueError('test')):
            with patch.object(mit, 'scarica_rss', side_effect=failure), patch.object(mit, 'salva') as save, \
                    redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertFalse(mit.integra_rss())
                save.assert_not_called()

    def test_no_new_events_still_records_successful_check(self):
        first = self.merge()
        second = self.merge(first, stamp='2026-10-27T08:00:00+00:00')
        self.assertEqual(second['rss_checked_at'], '2026-10-27T08:00:00+00:00')
        self.assertEqual(second['rss_added'], 0)
        self.assertEqual(second['sincronizzato'], self.previous['sincronizzato'])

    def test_next_year_not_imported(self):
        rows = mit.leggi_rss(feed(item(start='15/01/2027', end='15/01/2027')))
        events, _, bad = mit.converti(rows, self.base, self.prov, dt.date(2026, 10, 26))
        self.assertEqual((events, bad), ([], 0))


if __name__ == '__main__':
    unittest.main()

