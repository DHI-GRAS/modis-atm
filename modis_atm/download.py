import logging

from earthdata_download import download as eddownload

logger = logging.getLogger(__name__)

EXTENSIONS = ['.hdf', '.zip', '.nc4', '.nc']


def _get_https_data_url(urls, extensions=EXTENSIONS):
    """Find URL that starts with https and ends with a data file extension"""
    for url in urls:
        url_lower = url.lower()
        if url_lower.startswith('https'):
            for ext in extensions:
                if url_lower.endswith(ext):
                    return url
    raise ValueError('No https data URL found among URLs {}'.format(urls))


def download_entries(entries, download_dir, credentials):
    urls = []
    for e in entries:
        url = _get_https_data_url(e['urls'])
        urls.append(url)

    local_files = []
    for url in urls:
        local_file = eddownload.download_data(
                url, download_dir=download_dir,
                skip_existing=True,
                **credentials)
        local_files.append(local_file)
    return local_files
