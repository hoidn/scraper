from setuptools import setup, find_packages
import os
from operator import add
from functools import reduce

datafiles = reduce(add, [['../' + os.path.join(root, f) for f in files]
    for root, dirs, files in os.walk('data/')])

setup(name = 'scraper',
    packages = find_packages('.'),
    package_dir = {'scraper': 'scraper'},
    scripts = ['scripts/stock_scraper.py'],
    #package_data = {'scraper': ['../data/*']},
    package_data = {'scraper': datafiles},
    #install_requires = ['paramiko', 'numpy', 'matplotlib', 'mpld3', 'plotly', 'humanfriendly'],
    zip_safe = False)
