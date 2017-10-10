import os
import shutil
import posixpath
import logging

import ftputil
import ftputil.error
import requests

try:
    from urllib.parse import urlparse
except ImportError:
    # Python 2
    from urlparse import urlparse

logger = logging.getLogger(__name__)

EXTENSIONS = ['.hdf', '.zip', '.nc4', '.nc']
SCHEMES = ['https', 'ftp']


def _get_data_url(urls, extensions=EXTENSIONS):
    """Find URL that starts with https and ends with a data file extension"""
    urls_schemes = {}
    for url in urls:
        o = urlparse(url)
        if o.scheme in SCHEMES:
            if posixpath.splitext(o.path)[1] in EXTENSIONS:
                urls_schemes[o.scheme] = url
    for scheme in SCHEMES:
        # prefer https
        if scheme in urls_schemes:
            return urls_schemes[scheme]
    raise ValueError('No https data URL found among URLs {}'.format(urls))


def download_file_https(url, target, username, password):
    session = requests.Session()
    session.auth = requests.auth.HTTPBasicAuth(username, password)
    with session.get(url, stream=True) as response:
        response.raise_for_status()
        with open(target, "wb") as target_file:
            shutil.copyfileobj(response.raw, target_file)
    logger.info("Saved file {local_filename} ({local_filesize:d})".format(
        local_filename=target,
        local_filesize=os.path.getsize(target)))
    return target


def _hostname_path_from_url(url):
    o = urlparse(url)
    return o.netloc, o.path


def download_file_ftp(url, target, username, password):
    hostname, path = _hostname_path_from_url(url)
    try:
        with ftputil.FTPHost(hostname, username, password) as host:
            host.download(path, target)
    except ftputil.error.PermanentError:
        raise ValueError(
                'Unable to connect to this ftp server \'{}\'. '
                'Consider downloading manually \'{}\'.'
                .format(hostname, url))


def download_entries(entries, download_dir, credentials, reuse_existing=True):
    """Download files for all entries

    Parameters
    ----------
    entries : list of dict
        parsed entries
    download_dir : str
        path to store data
    credentials : dict(username='', password='')
        EarthData credentials
    reuse_existing : bool
        do not re-download existing files

    Returns
    -------
    list of str : downloaded files
    """
    # determine data urls
    urls = []
    for e in entries:
        url = _get_data_url(e['urls'])
        urls.append(url)

    local_files = []
    for url in urls:
        o = urlparse(url)
        local_file = os.path.join(download_dir, posixpath.basename(o.path))

        if os.path.isfile(local_file) and reuse_existing:
            # use existing
            pass
        else:
            if o.scheme == 'ftp':
                download_file_ftp(url, local_file, **credentials)
            else:
                download_file_https(url, local_file, **credentials)

        local_files.append(local_file)
    return local_files
