import datetime

from modis_atm import query

_date_extent = dict(
            date=datetime.datetime(2016, 1, 1),
            extent=dict(xmin=10, xmax=13, ymin=54, ymax=56))

_query_kw = dict(
            start_date=datetime.datetime(2016, 1, 1),
            end_date=datetime.datetime(2016, 1, 2),
            extent=dict(xmin=10, xmax=13, ymin=54, ymax=56),
            short_name='MOD05_L2')


def test_retrieve_entries():
    entries = query.retrieve_entries(**_query_kw)
    assert len(entries) > 0
    e = entries[0]
    assert 'footprint' in e


def test_retrieve_entries_for_param():
    entries = query.retrieve_entries_for_param(
            param_name='ozone',
            also_myd=True,
            **_date_extent)
    assert len(entries) > 0
