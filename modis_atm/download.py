import re
import os.path
import datetime

from earthdata_download import EarthdataAPI

short_names = ["MOD05_L2", "MOD04_3K", "MOD07_L2"]


def date_from_fname_ydoy(fname):
    fname = os.path.basename(fname)
    try:
        datestr = re.search('\.A(\d{5})\.').group(1)
        return datetime.datetime.strptime(datestr, '%Y%j').strftime('%Y%m%d')
    except AttributeError:
        raise ValueError(
                'Unable to get date from file name \'{}\'.'.format(fname))


def get_closest_overpass(urls):
    pass


def find_data(api, short_name, date, also_myd=True, **searchkwargs):
    dt = datetime.timedelta(hours=12)
    start_date = date - dt
    end_date = date + dt

    short_names = [short_name]
    if also_myd:
        short_names.append(short_name.replace('MOD', 'MYD'))

    urls = []
    for short_name in short_names:
        urls += api.find_data(short_name, start_date=start_date, end_date=end_date, **searchkwargs)
    return urls


def download_data(date, extent, credentials):

    urls = {}
    api = EarthdataAPI(**credentials)
    for short_name in short_names:
        uu = find_data(
                api, short_name=short_name,
                date=date, extent=extent)
        urls[short_name] = get_closest_overpass(uu)
