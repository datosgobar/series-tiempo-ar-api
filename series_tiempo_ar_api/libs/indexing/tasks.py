#! coding: utf-8

from django_rq import job

from series_tiempo_ar_api.apps.api.query.catalog_reader import Scraper


@job("scrapping")
def scrap(url):
    scrapper = Scraper()
    scrapper.run(url)
    return scrapper.distributions
