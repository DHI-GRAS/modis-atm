import datetime
import logging

import shapely.geometry
import numpy as np

from modis_atm import overpass_filter
from modis_atm import query

logging.basicConfig(level='DEBUG')

_extent = dict(xmin=10, xmax=13, ymin=54, ymax=56)

_date_extent = dict(
            date=datetime.datetime(2016, 1, 1),
            extent=_extent)

_aoi_geom = shapely.geometry.box(*[_extent[k] for k in ['xmin', 'ymin', 'xmax', 'ymax']])


def test_overpass_value():
    entries = query.retrieve_entries(short_name='MOD05_L2', **_date_extent)

    target_date = datetime.datetime(2016, 1, 1)
    aoi_geom = _aoi_geom
    aoi_area = aoi_geom.area

    values = np.zeros(len(entries))
    for i, e in enumerate(entries):
        value = overpass_filter.overpass_value(
                fp=e['footprint'],
                date=e['start_date'],
                aoi_geom_wgs=aoi_geom,
                aoi_area=aoi_area,
                target_date=target_date,
                max_diff_hours=48)
        values[i] = value
    assert np.all((values >= 0) & (values <= 1))


def test_rank_overpasses():

    entries = query.retrieve_entries(short_name='MOD05_L2', **_date_extent)

    target_date = datetime.datetime(2016, 1, 1)
    aoi_geom = _aoi_geom

    values, entries = overpass_filter.rank_overpasses(
            parsed_entries=entries,
            aoi_geom_wgs=aoi_geom,
            target_date=target_date,
            max_diff_hours=48)
    assert len(values) == len(entries)
    assert values[0] > values[-1]
