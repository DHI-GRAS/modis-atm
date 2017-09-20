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


def retrieve_entries(short_name, date, extent=None, day_night_flags=['DAY'], **searchkwargs):
    dt = datetime.timedelta(hours=12)
    start_date = date - dt
    end_date = date + dt
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


def retrieve_entries_for_param(param_name, date, extent, also_myd=True):
    if also_myd:
        short_names = SHORT_NAMES_WITH_MYD[param_name]
    else:
        short_names = SHORT_NAMES[param_name]
    entries = []
    for short_name in short_names:
        entries += retrieve_entries(short_name, date, extent)
    return entries
