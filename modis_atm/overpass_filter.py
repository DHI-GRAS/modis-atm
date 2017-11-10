import logging
from collections import defaultdict
from collections import OrderedDict

from modis_atm import utils

logger = logging.getLogger(__name__)


def group_entries_by_date(parsed_entries):
    date_groups = defaultdict(list)
    for e in parsed_entries:
        date = utils.average_datetime(
                e['start_date'],
                e['end_date'])
        date_groups[date].append(e)
    return date_groups


def _value_date(overpass_date, target_date, max_diff_hours):
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
    ddiff = utils.date_diff(overpass_date, target_date)
    diff_hours = ddiff.total_seconds() / 3600
    logger.debug('diff_hours: %f', diff_hours)
    abs_diff_hours = abs(diff_hours)
    if abs_diff_hours > max_diff_hours:
        return 0.0
    # 1 = perfect match, 0 = bad
    timepct = (max_diff_hours - abs_diff_hours) / max_diff_hours
    return timepct


def _value_overlap(footprint_geom, aoi_geom):
    intersection = aoi_geom.intersection(footprint_geom)
    # 1 = complete overlap, close to 0 = hardly any
    intersectionpct = intersection.area / aoi_geom.area
    logger.debug('intersectionpct: %f', intersectionpct)
    return intersectionpct


def get_best_overpass(
        parsed_entries, aoi_geom, target_date,
        max_diff_hours=48, min_overlap_pct=0.3):
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
    min_overlap_pct : float
        minimum overlap

    Returns
    -------
    OrderedDict datetime.datetime -> list of str
        sorted date groups of parsed entries
    """
    date_groups = group_entries_by_date(parsed_entries)
    logger.debug('Found entries from %d different dates.', len(date_groups))
    logger.debug('dates are %s', list(date_groups))

    ranked_entries = []
    for overpass_date in date_groups:
        date_value = _value_date(
                overpass_date, target_date, max_diff_hours=max_diff_hours)

        if date_value == 0:
            logger.debug('Skipping date %s (date value 0)', overpass_date)
            continue

        entries = date_groups[overpass_date]

        overlap_values = []
        for e in entries:
            v = _value_overlap(
                    footprint_geom=e['footprint'],
                    aoi_geom=aoi_geom)
            overlap_values.append(v)
        if sum(overlap_values) < min_overlap_pct:
            logger.debug('Skipping date %s (insufficient overlap)', overpass_date)
            continue

        ranked_entries.append((date_value, (overpass_date, entries)))

    if not ranked_entries:
        logger.warn('No reasonably close overpass among entries.')

    sorted_date_groups = [e[1] for e in sorted(ranked_entries)[::-1]]
    return OrderedDict(sorted_date_groups)
