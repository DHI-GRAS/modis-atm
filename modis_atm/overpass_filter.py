import logging
from collections import defaultdict

import numpy as np

logger = logging.getLogger(__name__)


def _average_dates(date1, date2):
    dt = date2 - date1
    date = date1 + dt / 2
    return date


def group_entries_by_date(parsed_entries):
    date_groups = defaultdict(list)
    for e in parsed_entries:
        date = _average_dates(
                e['start_date'].date(),
                e['end_date'].date())
        date_groups[date] = e
    return date_groups


def _value_date(overpass_date, target_date, max_diff_hours=48):
    """Compute value of overpass_date

    Parameters
    ----------
    overpass_date : datetime.datetime
        target data overpass overpass_date
    target_date : datetime.datetime
        reference overpass_date from scene
    max_diff_hours : float
        maximum difference in hours
        larger distance means 0 value
    """
    overpass_date = overpass_date.replace(tzinfo=None)
    diff_hours = abs((overpass_date - target_date).total_seconds() / 3600)
    logger.debug('diff_hours: %f', diff_hours)
    if diff_hours > max_diff_hours:
        return 0.0
    # 1 = perfect match, 0 = bad
    timepct = (max_diff_hours - diff_hours) / max_diff_hours
    return timepct


def _value_overlap(footprint_geom, aoi_geom):
    intersection = aoi_geom.intersection(footprint_geom)
    # 1 = complete overlap, close to 0 = hardly any
    intersectionpct = intersection.area / aoi_geom.area
    logger.debug('intersectionpct: %f', intersectionpct)
    return intersectionpct


def _combined_value(date_value, overlap_value):
    pass


def overpass_value(
        footprint_geom, date, aoi_geom,
        target_date, max_diff_hours):
    """Compute value for overpass

    Parameters
    ----------
    footprint_geom : shapely.geometry.Polygon
        footprint polygon
    overpass_date : datetime.datetime
        date from Modis overpass
    aoi_geom : shapely.geometry.Polygon
        aoi polygon in WGS coordinates
    target_date : datetime.datetime
        date for reference image
    max_diff_hours : float
        maximum time difference from reference date
        in hours
    """
    pass


def get_best_overpass(
        parsed_entries, aoi_geom,
        target_date, max_diff_hours=48):
    """Get entry / entries for best overpass

    Parameters
    ----------
    parsed_entries : list of dict
        parsed entry dictionaries
        from earthdata_download.query
    aoi_geom : shapely.geometry.Polygon
        aoi polygon in WGS coordinates
    target_date : datetime.datetime
        date for reference image
    max_diff_hours : float
        maximum time difference from reference date
        in hours

    Returns
    -------
    values : list of float
        value of each entry
    entries : list of dict
        sorted list of input parsed_entries
    """
    date_groups = group_entries_by_date(parsed_entries)

    best_date_value = 0
    best_entries = None
    for overpass_date in date_groups:
        date_value = _value_date(
                overpass_date, target_date, max_diff_hours=max_diff_hours)

        if date_value == 0:
            logger.debug('Skipping date %s (date value 0)', overpass_date)
            continue

        entries = date_groups[overpass_date]

        overlap_values = []
        for e in entries:
            overlap_values.append(
                    _value_overlap(
                        footprint_geom=e['footprint'],
                        aoi_geom=aoi_geom))
        if np.sum(overlap_values) > 0:
            pass
        else:
            logger.debug('Skipping date %s (no overlap)', overpass_date)
            continue

        if date_value > best_date_value:
            best_date_value = date_value
            best_entries = entries

    if not best_date_value:
        raise ValueError('No reasonably close overpass among entries.')

    return best_entries
