from setuptools import setup, find_packages

setup(name = 'scraper',
    packages = find_packages('.'),
    package_dir = {'scraper': 'scraper'},
    scripts = ['scripts/stock_scraper.py'],
    #package_data = {'scraper': ['data/*']},
    #install_requires = ['paramiko', 'numpy', 'matplotlib', 'mpld3', 'plotly', 'humanfriendly'],
    zip_safe = False)
