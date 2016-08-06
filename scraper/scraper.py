from .indices import sp500
import errno    
import time

import pandas as pd
import os
from io import StringIO

from . import utils

# TODO: move this to config.py
PKG_NAME = __name__.split(u'.')[0]
#data_prefix = os.environ['HOME'] + '/Dropbox/projects/financial/data_scraper/data'
data_prefix = utils.resource_path('', pkg_name = PKG_NAME)
print(data_prefix)

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

class StockDay:
    """
    Structure for accessing stock data associated with a single CSV
    file.
    """
    def __init__(self, path):
        self.time = self.path_to_timestamp(path)
        self.ticker = self.path_to_ticker(path)
        self.path = path
        
    def load(self):
        """
        Load data from a single csv file, corresponding to prices for
        one ticker during a single trading day.

        Returns a DataFrame instance with these columns:
            Timestamp,close,high,low,open,volume
        """
        with open(self.path) as f:
            full = f.read()
        header = 'Timestamp,close,high,low,open,volume\n'
        csv_str = header + '\n'.join(full.split('\n')[17:])
        return pd.read_csv(StringIO(csv_str))

    @staticmethod
    def path_to_timestamp(path):
        fname = os.path.basename(path)
        time_uct = float(fname.split('_')[0])
        return pd.Timestamp.utcfromtimestamp(time_uct)
    
    @staticmethod
    def path_to_ticker(path):
        fname = os.path.basename(path)
        return fname.split('_')[1]
    
def stockdays_to_timeseries(stockdays):
    """
    Process a sequence of StockDay instances, loading their stock data
    into a single DataFrame time series.
    """
    df = pd.concat([s.load() for s in stockdays]).sort_values(by = 'Timestamp')
    df = df.drop_duplicates(subset = 'Timestamp')
    df.index = pd.to_datetime(df['Timestamp'], unit = 's')
    del df['Timestamp']
    return df
    
def get_ticker_stocks(ticker, prefix = data_prefix):
    """Return a list of StockDay instances for the given stock ticker and data directory prefix"""
    from glob import glob
    paths = glob(prefix + '/%s/*_*csv' % ticker)
    if not paths:
        raise ValueError("ticker %s: no data found" % ticker)
    else:
        return map(StockDay, paths)



def get_time_series(ticker, start, end):
    def stock_matches(stock):
        return (stock.time > start) and (stock.time < end)
    return stockdays_to_timeseries(filter(stock_matches, get_ticker_stocks(ticker)))
    # TODO: abstraction violation?
