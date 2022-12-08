import asyncio
import logging
import re
import threading
from pprint import pprint as beauty_print
import time
from collections import deque
from threading import Thread

import bs4

from core.scrapper.fieldScrapper import *
from core.scrapper.absrtract.AbstractParseField import AbstractParseField

import yaml
from typing import List

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


async def get_json(client, url):
    async with client.get(url) as response:
        assert response.status == 200
        return await response.read()


def browser_request_checker_wait(url: str, driver: webdriver, time_sleep: float = 0.1):
    driver.get(url)
    while driver.page_source.find("Мы проверяем ваш браузер") != -1:
        time.sleep(time_sleep)


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
        self.driver = webdriver.Chrome(ChromeDriverManager(version="107.0.5304.62").install())
        self.driver.maximize_window()

        self.unchecked_urls_deque = deque()

        self._list_of_threads: List[Thread] = list()

    def _parse_content_object_page(self, html: dict):
        for field_scrapper in self.scrapperModules:
            field_scrapper.collect_field(html=html)

    def _collect_objects_urls_from_page(self):
        _template_any = re.compile(r".*")
        url = "https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p=1&region=4738"
        browser_request_checker_wait(url=url, driver=self.driver,
                                     time_sleep=self.configuration["scrapper"]["SleepWhileCaptcha"])

        response = self.driver.page_source
        # 28
        soup = BeautifulSoup(response, 'html.parser')
        all_cards: List[bs4.Tag] = soup.find_all("article", attrs={'data-name': 'CardComponent'})
        # Construct deque of unchecked urls
        self.unchecked_urls_deque.extend([card.findChild("a", attrs={"href": _template_any})["href"]
                                          for card in all_cards[:10]])

    def _reduce_driver_with_url(self, _collected_url):
        _tmp_driver = webdriver.Chrome(ChromeDriverManager(version="107.0.5304.62").install())
        browser_request_checker_wait(_collected_url, _tmp_driver,
                                     time_sleep=self.configuration["scrapper"]["SleepWhileCaptcha"])
        soup = BeautifulSoup(_tmp_driver.page_source, 'html.parser')
        print(len(_tmp_driver.page_source))
        del _tmp_driver
        return 'result'
        # print(soup.find("div", attrs={"data-name": "PriceLayout"}).findChild())

    def _check_objects_by_urls(self):
        """
        Должен вызываться в отдельном потоке
        :return:
        """
        while True:
            if len(self.unchecked_urls_deque) != 0:
                _collected_url_pass = self.unchecked_urls_deque[0]
                # _collected_url = "https://www.cian.ru/sale/flat/279127466/"
                self.unchecked_urls_deque.popleft()

                thread_creature = threading.Thread(target=self._reduce_driver_with_url, args=(_collected_url_pass, ))

                while len(self._list_of_threads) >= self.configuration['scrapper']['MaximumThreads']:
                    for _thread in self._list_of_threads:
                        if not _thread.is_alive():
                            self._list_of_threads.remove(_thread)
                    time.sleep(self.configuration['scrapper']['ObserverOfMaximumThreadUsageTimeUpdate'])

                thread_creature.start()
                self._list_of_threads.append(thread_creature)
                # thread_creature.join()
            else:
                time.sleep(self.configuration["scrapper"]["SleepUpdateWaiting"])


def main():
    scrapper = MainScrapper()
    Thread(target=scrapper._collect_objects_urls_from_page).start()
    scrapper._check_objects_by_urls()


if __name__ == '__main__':
    main()
