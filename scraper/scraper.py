from .indices import sp500
import errno    
import os
import time

try:
    # py3
    from urllib.request import Request, urlopen
    from urllib.parse import urlencode
except ImportError:
    # py2
    from urllib2 import Request, urlopen
    from urllib import urlencode



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
