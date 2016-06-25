from scraper.indices import sp500
from scraper import scraper

def main():
    if scraper.today_bday():
        for s in sp500:
            scraper.autodl_symbol(s)

if __name__ == '__main__':
    main()
