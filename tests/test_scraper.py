from scraper import scraper

def test_autodl():
    import os
    path = scraper.autodl_symbol('GOOG')
    assert os.path.exists(path)
