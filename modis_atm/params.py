from __future__ import division
import logging

import shapely.geometry

from modis_atm import query
from modis_atm import overpass_filter
from modis_atm import download
from modis_atm import read_hdf

logger = logging.getLogger(__name__)

CONVERSION_FACTORS = {
        'ozone': 0.001}  # to cm atm


def retrieve_parameters(date, extent, credentials, download_dir):
    """Load parameters from MODIS data

    Parameters
    ----------
    date : datetime.datetime
        target date and time
    extent : dict
        xmin, xmax, ymin, ymax
        area of interest in geographic coordinates
    credentials : dict
        username, password
        credentials for EarthData
    download_dir : str
        path to find / save data in

    Returns
    -------
    dict of float
        ozone, AOT, PWV
        parameter values
    """
    aoi_geom = shapely.geometry.box(
            *[extent[k] for k in ['xmin', 'ymin', 'xmax', 'ymax']])

    param_names = ['AOT', 'ozone', 'PWV']

    params = {}
    for param_name in param_names:
        # query
        logger.info('Finding entries for %s ...', param_name)
        entries = query.retrieve_entries_for_param(param_name, date, extent, also_myd=False)
        logger.info('Total number of entries: %d', len(entries))

        # get best entries
        best_entries = overpass_filter.get_best_overpass(
                parsed_entries=entries,
                aoi_geom=aoi_geom,
                target_date=date)

        # download data for best entries
        local_files = download.download_entries(
                best_entries, download_dir, credentials)

        # read and merge data
        logger.info('Using data from %d files', len(local_files))
        dmean = read_hdf.get_modis_hdf_mean(
                infiles=local_files, param_name=param_name, extent=extent)

        # convert
        if dmean is not None and param_name in CONVERSION_FACTORS:
            dmean *= CONVERSION_FACTORS[param_name]

        params[param_name] = dmean

    return params
