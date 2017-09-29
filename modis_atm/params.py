from __future__ import division
import logging

import shapely.geometry

from modis_atm import query
from modis_atm import overpass_filter
from modis_atm import download
from modis_atm import read_hdf
from modis_atm import utils

logger = logging.getLogger(__name__)

CONVERSION_FACTORS = {
        'ozone': 0.001}  # to cm atm


def retrieve_parameters(date, extent, credentials, download_dir, max_diff_hours=24):
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
    max_diff_hours : int
        maximum difference in hours from target date

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
        params[param_name] = None
        # query
        logger.info('Retrieving %s', param_name)
        entries = query.retrieve_entries_for_param(
                param_name, date, extent, pad_hours=max_diff_hours, also_myd=False)
        logger.debug('Total number of entries: %d', len(entries))

        # get best entries
        sorted_date_groups = overpass_filter.get_best_overpass(
                parsed_entries=entries,
                aoi_geom=aoi_geom,
                target_date=date,
                max_diff_hours=max_diff_hours)

        for overpass_date in sorted_date_groups:
            logger.debug('Trying parameters from %s', overpass_date)
            best_entries = sorted_date_groups[overpass_date]

            # download data for best entries
            local_files = download.download_entries(
                    best_entries, download_dir, credentials)

            # read and merge data
            logger.debug('Using data from %d files', len(local_files))
            dmean = read_hdf.get_modis_hdf_mean(
                    infiles=local_files, param_name=param_name, extent=extent)

            # convert
            if dmean is not None and param_name in CONVERSION_FACTORS:
                dmean *= CONVERSION_FACTORS[param_name]

            if dmean is None:
                logger.debug('Got no data from this date group.')
                continue
            else:
                params[param_name] = dmean
                dhours = utils.date_diff(date, overpass_date).total_seconds() // 3600
                logger.info(
                        'Found valid data from date %s (dhours is %d)',
                        overpass_date, dhours)
                break

    return params
