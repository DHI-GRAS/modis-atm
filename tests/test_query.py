import datetime

from modis_atm import download


_date_extent = dict(
            date=datetime.datetime(2016, 1, 1),
            extent=dict(xmin=10, xmax=13, ymin=54, ymax=56))


_query_kw = dict(
            _date_extent,
            short_name='MOD05_L2')


def test_retrieve_entries():
    entries = download.retrieve_entries(**_query_kw)
    assert len(entries) > 0
    e = entries[0]
    assert 'footprint' in e


def test_retrieve_entries_all_short_names():
    entries = download.retrieve_entries_all_short_names(
            also_myd=True,
            **_date_extent)
    some_short_name = 'MOD05_L2'
    assert some_short_name in entries
    assert len(entries[some_short_name]) > 0
