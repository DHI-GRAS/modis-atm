import re
import posixpath
import datetime

from earthdata_download import query as edquery
from earthdata_download import download as eddownload

short_names = ['MOD05_L2', 'MOD04_3K', 'MOD07_L2']


def date_from_fname_ydoy(fname):
    fname = posixpath.basename(fname)
    try:
        datestr = re.search('\.A(\d{7}\.\d{4})\.', fname).group(1)
        return datetime.datetime.strptime(datestr, '%Y%j.%H%M')
    except AttributeError:
        raise ValueError(
                'Unable to get date from file name \'{}\'.'.format(fname))


def get_closest_overpass(urls):
    pass


def find_data(short_name, date, extent, also_myd=True, **searchkwargs):
    dt = datetime.timedelta(hours=12)
    start_date = date - dt
    end_date = date + dt

    short_names = [short_name]
    if also_myd:
        short_names.append(short_name.replace('MOD', 'MYD'))

    urls = []
    for short_name in short_names:
        urls += edquery.find_data(
                short_name,
                start_date=start_date,
                end_date=end_date,
                extent=extent,
                **searchkwargs)
    return urls


def find_data_all_short_names(date, extent):
    urls = {}
    for short_name in short_names:
        uu = find_data(
                short_name=short_name,
                date=date, extent=extent)
        urls[short_name] = get_closest_overpass(uu)
    return urls


def download_data(date, extent, credentials, download_dir):

    urls = find_data_all_short_names(date, extent)

    downloaded = {}
    for short_name in urls:
        local_files = []
        for url in urls[short_name]:
            local_file = eddownload.download_data(
                    url, download_dir=download_dir,
                    skip_existing=True,
                    **credentials)
            local_files.append(local_file)
        downloaded[short_name] = local_files

    return downloaded
