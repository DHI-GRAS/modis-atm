from setuptools import setup, find_packages

setup(
    name='modis_atm',
    version='0.2',
    description='Get atmospheric parameters from MODIS',
    author='Jonas Solvsteen',
    author_email='josl@dhi-gras.com',
    url='https://www.dhi-gras.com',
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    modis_atm=modis_atm.scripts.modis_atm:main
    """)
