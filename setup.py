from setuptools import setup, find_packages

setup(
    name='modis_atm',
    version='0.1.3',
    description='Get atmospheric parameters from MODIS',
    author='Jonas Solvsteen',
    author_email='josl@dhi-gras.com',
    url='https://www.dhi-gras.com',
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    modis_atm=modis_atm.scripts.modis_atm:main
    """,
    install_requires=[
        'earthdata_download>=0.7',
        'ftputil'],
    dependency_links=[
        'https://github.com/DHI-GRAS/earthdata_download/archive/v0.7.zip#egg=earthdata_download-0.7'])
