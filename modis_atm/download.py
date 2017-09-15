import logging

import shapely.geometry
from earthdata_download import download as eddownload

from modis_atm import overpass_filter
from modis_atm import query

logger = logging.getLogger(__name__)


def download_entries(entries, download_dir, credentials):
    urls = [e['urls'][0] for e in entries]
    local_files = []
    for url in urls:
        local_file = eddownload.download_data(
                url, download_dir=download_dir,
                skip_existing=True,
                **credentials)
        local_files.append(local_file)
    return local_files


def find_and_download_data(date, extent, credentials, download_dir):

    aoi_geom_wgs = shapely.geometry.box(
            *[extent[k] for k in ['xmin', 'ymin', 'xmax', 'ymax']])

    param_names_entries = query.retrieve_entries_all_parameters(date, extent, also_myd=True)

    for param_name in param_names_entries:
        entries = param_names_entries[param_name]

        values, entries = overpass_filter.rank_overpasses(
                entries,
                aoi_geom_wgs,
                target_date=date,
                max_diff_hours=48)

        best_entry = entries[0]
        best_value = values[0]
        logger.info('Best entry has value %f', best_value)
