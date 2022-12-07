from core.scrapper.fieldScrapper import *
from core.scrapper.absrtract.AbstractParseField import AbstractParseField

import yaml
from typing import List

from bs4 import BeautifulSoup
import requests


def map_scrapper(scrapper_name: str) -> AbstractParseField:
    match scrapper_name:
        case "id_cian":
            return IdCianField()
        case "price":
            return PriceField()
        case _:
            raise NotImplementedError


class MainScrapper:
    scrapperModules: List[AbstractParseField] = []

    def __init__(self):
        with open("scrapperConfiguration.yaml", "r") as ymlfile:
            self.configuration = yaml.load(ymlfile, Loader=yaml.FullLoader)
        del ymlfile

        for key in ["SystemFields", "MetaPropertyFields", "LocationFields", "MetaAdFields"]:
            self.scrapperModules.extend(map(map_scrapper, self.configuration["scrapper"][key]))

        print(self.scrapperModules)

    def _parse_content_object_page(self, html: dict):
        for field_scrapper in self.scrapperModules:
            field_scrapper.collect_field(html=html)

    def _collect_objects_urls_from_page(self):
        url = "https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=1"
        result = requests.get(url)
        content = result.content

        soup = BeautifulSoup(content, 'html.parser')

if __name__ == '__main__':
    scrapper = MainScrapper()
