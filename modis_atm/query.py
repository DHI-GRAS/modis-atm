import datetime

from earthdata_download import query as edquery

SHORT_NAMES = {
        'AOT': ['MOD04_3K'],
        'PWV': ['MOD05_L2'],
        'ozone': ['MOD07_L2']}

SHORT_NAMES_WITH_MYD = {
        'PWV': ['MOD05_L2', 'MYD05_L2'],
        'AOT': ['MOD04_3K', 'MYD04_3K'],
        'ozone': ['MOD07_L2', 'MYD07_L2']}

DEFAULT_DHOURS = 48


def retrieve_entries(
        short_name, start_date, end_date,
        extent=None, pad_hours=DEFAULT_DHOURS,
        day_night_flags=['DAY'], **searchkwargs):
    """Retrieve entries for short name

    Parameters
    ----------
    short_name : str
        MODIS short name
    start_date, end_date : datetime.datetime
        date range
    extent : dict
        xmin, xmax, ymin, ymax
    day_night_flags : list of str
        accepted day_night_flag values
    **searchkwargs : additional keyword arguments
        passed to earthdata_download.query.find_data_entries
    """
    entries = edquery.find_data_entries(
                short_name,
                start_date=start_date,
                end_date=end_date,
                extent=extent,
                parse_entries=True,
                **searchkwargs)
    if day_night_flags:
        entries = [
                e for e in entries
                if e['original_response']['day_night_flag'] in day_night_flags]
    return entries


def retrieve_entries_for_param(
        param_name, date, extent, pad_hours=DEFAULT_DHOURS, also_myd=True):
    """Retrieve entries for parameter

    Parameters
    ----------
    param_name : str
        AOT, ozone, PWV
    date : datetime.datetime
        reference data
    pad_hours : int
        number of hours to pad date with
    also_myd : bool
        also get MYD in addition to MOD
    """
    dt = datetime.timedelta(hours=pad_hours)
    start_date = date - dt
    end_date = date + dt
    if also_myd:
        short_names = SHORT_NAMES_WITH_MYD[param_name]
    else:
        short_names = SHORT_NAMES[param_name]
    entries = []
    for short_name in short_names:
        entries += retrieve_entries(
                short_name=short_name,
                extent=extent,
                start_date=start_date,
                end_date=end_date)
    return entries
