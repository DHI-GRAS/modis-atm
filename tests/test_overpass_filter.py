import datetime

import shapely.geometry

from modis_atm import overpass_filter
from modis_atm import download


_date_extent = dict(
            date=datetime.datetime(2016, 1, 1),
            extent=dict(xmin=10, xmax=13, ymin=54, ymax=56))

_aoi_geom = shapely.geometry.box(10, 54, 13, 56)


def test_overpass_value():

    reference_date = datetime.datetime(2016, 1, 1)

    aoi_geom = _aoi_geom
    aoi_area = aoi_geom.area

    entries = download.retrieve_entries(**_date_extent)
    e = entries[0]

    value = overpass_filter.overpass_value(
            fp=e['footprint'],
            date=e['start_date'],
            aoi_geom_wgs=aoi_geom,
            aoi_area=aoi_area,
            reference_date=reference_date,
            max_diff_hours=48)
    assert 0 < value < 1
