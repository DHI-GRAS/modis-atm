import os
import re
import glob
import json
import datetime
from collections import OrderedDict

from earthdata_download import EarthdataAPI


def date_from_fname_ydoy(fname):
    fname = os.path.basename(fname)
    try:
        datestr = re.search('\.A(\d{5})\.').group(1)
        return datetime.datetime.strptime(datestr, '%Y%j').strftime('%Y%m%d')
    except AttributeError:
        raise ValueError(
                'Unable to get date from file name \'{}\'.'.format(fname))


class MODISBookkeeper:

    def __init__(
            self, short_name, version, download_dir,
            credentials=None, index_file='data_index.json',
            date_from_fname=date_from_fname_ydoy, extension='.hdf'):
        if credentials is not None:
            self.api = self.initialize_api(credentials)
        else:
            self.api = None
        self.short_name = short_name
        self.version = version
        self.download_dir = download_dir
        self.index_file = os.path.join(self.download_dir, index_file)
        self.date_from_fname = date_from_fname
        self.extension = extension
        self.glob_pattern = '{}*{}'.format(self.short_name, self.extension)

    def initialize_api(self, credentials):
        self.api = EarthdataAPI(**credentials)

    def download_data(self, date, extent):
        try:
            start_date, end_date = date
        except TypeError:
            dt = datetime.timedelta(hours=12)
            start_date = date - dt
            end_date = date + dt

        if self.api is None:
            raise ValueError(
                    'API not initialized. Provide credentials during '
                    'instantiation or call `initialize_api`.')
        urls = self.api.find_data(
                short_name=self.short_name, version=self.version,
                start_date=start_date, end_date=end_date)

        return self.api.download_all(
                data_urls=urls, download_dir=self.download_dir)

    @staticmethod
    def _load_index_file(index_file):
        return json.load(open(index_file), object_pairs_hook=OrderedDict)

    def build_index(self):
        if os.path.isfile(self.index_file):
            index = self._load_index_file(self.index_file)
        else:
            index = {}

        pattern = os.path.join(self.download_dir, self.glob_pattern)
        all_files = glob.glob(pattern)
        if not all_files:
            raise ValueError('No data files found with pattern \'{}\'.'.format(pattern))
