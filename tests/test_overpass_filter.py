import datetime
import logging

import shapely.geometry

from modis_atm import overpass_filter
from modis_atm import query

logging.basicConfig(level='DEBUG')

_extent = dict(xmin=10, xmax=13, ymin=54, ymax=56)

_date_extent = dict(
            date=datetime.datetime(2016, 1, 1),
            extent=_extent)

_aoi_geom = shapely.geometry.box(*[_extent[k] for k in ['xmin', 'ymin', 'xmax', 'ymax']])


def test_get_best_overpass(caplog):
    caplog.set_level('DEBUG')

    parsed_entries = query.retrieve_entries(short_name='MOD05_L2', **_date_extent)
    target_date = datetime.datetime(2016, 1, 1)
    aoi_geom = _aoi_geom

    best_entries = overpass_filter.get_best_overpass(
        parsed_entries, aoi_geom,
        target_date, max_diff_hours=48)

    assert isinstance(best_entries, list)
    assert len(best_entries) > 0
