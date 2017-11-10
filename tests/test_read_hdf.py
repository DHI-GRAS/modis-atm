import pytest

try:
    import numpy as np
    from modis_atm import read_hdf
except ImportError:
    pytestmark = pytest.mark.skip(reason='numpy, scipy, or xarray not installed')

try:
    import modis_atm_data
    HAS_DATA = True
except ImportError:
    HAS_DATA = False

NEED_DATA = pytest.mark.skipif(
        not HAS_DATA,
        reason='modis_atm_data not installed')


@NEED_DATA
def test_get_modis_hdf_sum_count_no_extent():
    for param_name in modis_atm_data.DATAFILES:
        infile = modis_atm_data.DATAFILES[param_name]
        dsum, dcount = read_hdf.get_modis_hdf_sum_count(
                infile, param_name, extent=None)
        assert isinstance(dsum, np.float)
        assert isinstance(dcount, np.integer)


@NEED_DATA
def test_get_modis_hdf_sum_count_extent():
    extent = modis_atm_data.EXTENT
    for param_name in modis_atm_data.DATAFILES:
        infile = modis_atm_data.DATAFILES[param_name]
        dsum, dcount = read_hdf.get_modis_hdf_sum_count(
                infile, param_name, extent=extent)
        assert isinstance(dsum, np.float)
        assert np.isfinite(dsum)
        assert isinstance(dcount, np.integer)


@NEED_DATA
def test_get_modis_hdf_mean_no_extent():
    for param_name in modis_atm_data.DATAFILES:
        infiles = [modis_atm_data.DATAFILES[param_name]]
        dmean = read_hdf.get_modis_hdf_mean(infiles, param_name, extent=None)
        assert isinstance(dmean, np.float)
        assert np.isfinite(dmean)


@NEED_DATA
def test_get_modis_hdf_sum_count_zoom():
    param_name = 'PWV'
    extent = modis_atm_data.EXTENT
    infiles = [modis_atm_data.DATAFILES[param_name]]
    dmean = read_hdf.get_modis_hdf_mean(infiles, param_name, extent=extent)
    assert isinstance(dmean, np.float)
    assert np.isfinite(dmean)
