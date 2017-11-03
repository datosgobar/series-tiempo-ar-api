#! coding: utf-8

from django_rq import job

from series_tiempo_ar_api.apps.api.query.indexing.scraping import get_scraper


@job("scrapping")
def scrape(url):
    scrapper = get_scraper()
    scrapper.run(url)
    return scrapper.distributions
