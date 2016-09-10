import pytest
import pandas as pd
from scraper import scraper

def test_autodl():
    import os
    path = scraper.autodl_symbol('GOOG')
    assert os.path.exists(path)

def test_get_time_series():
    now = pd.Timestamp.now()
    start = now - 50 * pd.tseries.offsets.BDay()
    with pytest.raises(ValueError) as excinfo:
        def f():
            scraper.get_time_series('Afdsdf', start, now)
        f()
    assert 'no data found' in str(excinfo.value)

    scraper.get_time_series('A', start, now)


