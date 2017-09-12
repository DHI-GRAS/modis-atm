import datetime

from modis_atm import download


def test_find_data():
    urls = download.find_data(
            short_name='MOD05_L2',
            date=datetime.datetime(2016, 1, 1),
            linkno=0)
    assert isinstance(urls, list)
    assert len(urls) > 0
