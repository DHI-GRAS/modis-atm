from setuptools import setup, find_packages

setup(
    name='modis_atm',
    version='0.1',
    description='Get atmospheric parameters from MODIS',
    author='Jonas Solvsteen',
    author_email='josl@dhi-gras.com',
    url='https://www.dhi-gras.com',
    packages=find_packages(),
    install_requires=[
        'earthdata_download>=0.5'],
    dependency_links=[
        'https://github.com/DHI-GRAS/earthdata_download/archive/v0.5.zip#egg=earthdata_download-0.5'])
