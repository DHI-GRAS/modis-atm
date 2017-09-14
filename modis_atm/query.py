import datetime

from earthdata_download import query as edquery

SHORT_NAMES = ['MOD05_L2', 'MOD04_3K', 'MOD07_L2']
SHORT_NAMES_WITH_MYD = ['MOD05_L2', 'MYD05_L2', 'MOD04_3K', 'MYD04_3K', 'MOD07_L2', 'MYD07_L2']


def retrieve_entries(short_name, date, extent=None, **searchkwargs):
    dt = datetime.timedelta(hours=12)
    start_date = date - dt
    end_date = date + dt
    return edquery.find_data_entries(
                short_name,
                start_date=start_date,
                end_date=end_date,
                extent=extent,
                parse_entries=True,
                **searchkwargs)


def retrieve_entries_all_short_names(date, extent, also_myd=True):
    if also_myd:
        short_names = SHORT_NAMES_WITH_MYD
    else:
        short_names = SHORT_NAMES

    entries = {}
    for short_name in short_names:
        entries[short_name] = retrieve_entries(
                short_name, date, extent)
    return entries
