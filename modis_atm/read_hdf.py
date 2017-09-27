from __future__ import division
import os
import logging

import xarray as xr
import numpy as np
import scipy.ndimage.interpolation

logger = logging.getLogger(__name__)

FIELDS = {
        'PWV': 'Water_Vapor_Near_Infrared',
        'AOT': 'Optical_Depth_Land_And_Ocean',
        'ozone': 'Total_Ozone'}


def get_lon_lat_mask(lon, lat, xmin, xmax, ymin, ymax, do_buffer=True):
    if do_buffer:
        dlon = 0.001
        dlat = 0.001
        xmin = xmin - dlon
        xmax = xmax + dlon
        ymin = ymin - dlat
        ymax = ymax + dlat
    mask = (
            (lon >= xmin) & (lon <= xmax) &
            (lat >= ymin) & (lat <= ymax))
    return mask


def get_modis_hdf_sum_count(infile, param_name, extent=None):
    """Read MODIS HDF file and return sum and count within extent

    Parameters
    ----------
    infile : str
        path to MODIS HDF5 file
    param_name : str
        parameter name for FIELDS dict
    extent : dict, optional
        xmin, xmax, ymin, ymax
        extent in geographic coordinates

    Returns
    -------
    float, float
        sum and count over valid data
        inside extent (if provided)
    """
    field_name = FIELDS[param_name]
    logger.info('Loading file %s field %s', os.path.basename(infile), field_name)
    with xr.open_dataset(infile) as ds:
        data = ds[field_name]
        isnan = np.isnan(data)
        if isnan.all():
            raise ValueError('Data is all NaN.')
        nanpct = isnan.sum() / isnan.size
        logger.debug('Percentage of NaN elements: %f', nanpct)
        if extent is not None:
            lon = ds['Longitude']
            lat = ds['Latitude']
            logger.debug('getting mask for extent ...')
            mask = get_lon_lat_mask(
                    lon=lon,
                    lat=lat,
                    **extent)
            if mask.shape != data.shape:
                logger.debug('data shape: %s', data.shape)
                logger.debug('mask shape: %s', mask.shape)
                nm = np.array(mask.shape) / np.array(data.shape)
                mask = scipy.ndimage.interpolation.zoom(mask.values, zoom=(1/nm))
                logger.debug('mask new shape: %s', mask.shape)
            data = data.where(mask)
        dsum = data.sum().values[()]
        dcount = data.count().values[()]
        logger.debug('Number of pixels from this file: %d', dcount)
    return dsum, dcount


def get_modis_hdf_mean(infiles, param_name, extent=None):
    """Get sum and count for all infiles and compute mean

    Parameters
    ----------
    infiles : list of str
        paths to MODIS HDF5 files
    param_name : str
        parameter name for FIELDS dict
    extent : dict, optional
        xmin, xmax, ymin, ymax
        extent in geographic coordinates

    Returns
    -------
    float or None
        mean computed from sums and counts
        None if no data was found
    """
    dsum_total = 0.0
    dcount_total = 0
    for infile in infiles:
        dsum, dcount = get_modis_hdf_sum_count(
                infile, param_name=param_name, extent=extent)
        dsum_total += dsum
        dcount_total += dcount

    logger.info('Total number of pixels in mean: %d', dcount_total)
    if dcount_total == 0:
        dmean = None
    else:
        dmean = dsum_total / dcount
    return dmean
