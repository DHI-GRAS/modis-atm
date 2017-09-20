import shutil
import tempfile
import datetime

import click


def _get_extent(gdf):
    p = gdf.geometry[0]
    xmin, ymin, xmax, ymax = p.bounds
    return dict(xmin=xmin, ymin=ymin, xmax=xmax, ymax=ymax)


@click.command()
@click.argument(
        'shpfile', type=click.Path(file_okay=True))
@click.argument(
        '--date', '-d', help='Date string in some reasonable format (default: now)')
@click.argument(
        '--username', '-u', required=True, help='EarthData username')
@click.argument(
        '--password', '-p', required=True, help='EarthData password')
@click.argument(
        '--download-dir', type=click.Path(dir_okay=True), help='Download directory (optional)')
def main(shpfile, date=None, download_dir=None, **credentials):
    import geopandas as gpd
    import dateutil
    import modis_atm.params

    gdf = gpd.read_file(shpfile).to_crs({'init': 'epsg:4326'})
    extent = _get_extent(gdf)

    if date is None:
        date = datetime.datetime.now()
    else:
        date = dateutil.parser.parse(date)

    if download_dir is None:
        tempdir = tempfile.mkdtemp()
    try:
        params = modis_atm.params.retrieve_parameters(
                date, extent, credentials, download_dir=tempdir)
        click.echo(params)
    finally:
        if download_dir is None:
            shutil.rmtree(tempdir)