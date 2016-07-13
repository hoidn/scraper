from .indices import sp500
import errno    
import time

import pandas as pd
import os
from StringIO import StringIO

# TODO: move this to config.py
data_prefix = os.environ['HOME'] + '/Dropbox/projects/financial/data_scraper/data'

try:
    # py3
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
except ImportError:
    # py2
    from urllib2 import Request, urlopen
    from urllib import urlencode

def today_bday():
    """"Return True if `now` falls within a business day"""
    return is_bday(pd.Timestamp.utcnow())

def is_bday(now):
    """
    now : pandas.tslib.Timestamp
        Return True if `now` is during a business day
    """
    closest_bday = now - pd.tseries.offsets.BDay() + pd.tseries.offsets.BDay()
    return now == closest_bday

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def _request(symbol):
    #url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, stat)
    url = 'http://chartapi.finance.yahoo.com/instrument/1.0/%s/chartdata;type=quote;range=1d/csv' % symbol
    req = Request(url)
    resp = urlopen(req)
    content = resp.read().decode().strip()
    return content

def autodl_symbol(symbol):
    directory = 'data/' + symbol + '/'
    name = "%d_%s.csv" % (time.time(), symbol)
    mkdir_p(directory)
    path = directory + name

    with open(path, 'w') as f:
        f.write(_request(symbol))
    return path


def read_csv(path):
    """
    Load data from a single csv file, corresponding to
    prices for one ticker during a single trading day.
    """
    with open(path) as f:
        full = f.read()
    header = 'Timestamp,close,high,low,open,volume\n'
    return header + '\n'.join(full.split('\n')[17:])

class StockDay:
    def __init__(self, path):
        self.time = self.path_to_timestamp(path)
        self.ticker = self.path_to_ticker(path)
        self.path = path
        
    def load(self):
        return pd.read_csv(StringIO(read_csv(self.path)))

    @staticmethod
    def path_to_timestamp(path):
        fname = os.path.basename(path)
        time_uct = float(fname.split('_')[0])
        return pd.Timestamp.utcfromtimestamp(time_uct)
    
    @staticmethod
    def path_to_ticker(path):
        fname = os.path.basename(path)
        return fname.split('_')[1]
    
def merge_stockdays(stockdays):
    """
    Merge a sequence of StockDay instances,
    returning a pandas dataframe.
    """
    return pd.concat([s.load() for s in stockdays])
    
def get_ticker_stocks(ticker, prefix = data_prefix):
    """Return a list of StockDay instances for the given stock ticker and data directory prefix"""
    from glob import glob
    paths = glob(prefix + '/%s/*_*csv' % ticker)
    return map(StockDay, paths)


def get_time_series(ticker, start, end):
    def stock_matches(stock):
        return (stock.time > start) and (stock.time < end)
    merged = merge_stockdays(filter(stock_matches, get_ticker_stocks(ticker)))
    # TODO: abstraction violation?
    return merged.drop_duplicates(subset = 'Timestamp')
