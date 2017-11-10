import os
import shutil
import tempfile
import datetime

import pytest

try:
    from modis_atm import params
except ImportError:
    pytestmark = pytest.mark.skip(reason='numpy, scipy, or xarray not installed')


auth = dict(
        username=os.environ.get('EARTHDATA_USERNAME'),
        password=os.environ.get('EARTHDATA_PASSWORD'))

_date_extent = dict(
            date=datetime.datetime(2016, 1, 1),
            extent=dict(xmin=10, xmax=13, ymin=54, ymax=56))


@pytest.mark.skipif(
        (auth['username'] is None or auth['password'] is None),
        reason='invalid or missing authentication')
def test_retrieve_parameters():
    tempdir = tempfile.mkdtemp()
    try:
        parameters = params.retrieve_parameters(
                credentials=auth,
                download_dir=tempdir,
                **_date_extent)
    finally:
        shutil.rmtree(tempdir)
    assert 'ozone' in parameters
    assert isinstance(parameters['AOT'], float)
