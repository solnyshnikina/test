import json
import time
from typing import Any
from bs4 import BeautifulSoup

import scrapy
from pydantic import BaseModel

class Item(BaseModel):
    timestamp: Any
    RPC: Any
    url: Any
    title: Any
    marketing_tags: Any
    brand: Any
    section: Any
    price_data: Any
    stock: Any
    assets: Any
    metadata: Any


def apteka(html):
    soup = BeautifulSoup(html, 'lxml')
    items = soup.find('div', {'class': 'goods-grid__inner'}).find_all('div', {
        'class': 'ui-card ui-card_size_default ui-card_outlined goods-card goods-grid__cell goods-grid__cell_size_3'})

    return_list = []

    for item in items:
        try:
            timestamp = int(time.time())
            RPC = item.find("div",
                            {"class": "goods-card__name text text_size_default text_weight_medium"}
                            ).find("a")["href"].split("_")[-1]

            url = "https://apteka-ot-sklada.ru" + item.find("div",
                                                            {
                                                                "class": "goods-card__name text text_size_default text_weight_medium"}
                                                            ).find("a")["href"]

            title = item.find('span', {'itemprop': 'name'}).text
            marketing_tags = [i.strip() for i in
                              item.find('ul', {'class': 'goods-tags__list goods-tags__list_direction_vertical'}).text.split(
                                  '\n') if i.strip()]

            brand = item.find('div', {'class': 'goods-card__producer text'}).find("span", {"itemtype": "legalName"}).text

            section = soup.find('ul', {'class': 'ui-breadcrumbs__list'}).find_all("li")
            section = [item.text.strip() for item in section]

            price_data = {"current": item.find("span", {"class": "goods-card__cost text text_size_title text_weight_bold"}
                                               ).text.replace("₽", "").replace("\n", "").strip(),
                          "original": item.find("span", {"class": "goods-card__cost text text_size_title text_weight_bold"}
                                                ).text.replace("₽", "").replace("\n", "").strip(),
                          "sale_tag": None

                          }

            stock = {"count": 0}

            assets = {
                "main_image": "https://apteka-ot-sklada.ru" + item.find("img")["src"],
                "set_images": ["https://apteka-ot-sklada.ru" + item.find("img")["src"]],

                "view360": [None],
                "video": [None]
            }

            metadata = {
                "__description": "",
            }
            return_list.append({'timestamp': timestamp,
                                "RPC": RPC,
                                "url": url,
                                'marketing_tags': marketing_tags,
                                'title': title,
                                'section': section,
                                'brand': brand,
                                'price_data': price_data,
                                "stock": stock,
                                "assests": assets,
                                "metadata": metadata}
            )
            #         break
        except:
            pass
    return return_list


def parse_detailed_information(html):
    soup = BeautifulSoup(html, features="lxml")

    main_body = soup.find("div", {"class": "ui-collapsed-content__content"})

    return main_body.text


class AntibioticsSpider(scrapy.Spider):
    name = "antibiotics"

    def start_requests(self):
        urls = []
        for page_number in range(0, 36, 12):
            urls.append(f"https://apteka-ot-sklada.ru/catalog/medikamenty-i-bady%2Fantibiotiki?start={page_number}")

        for page_number in range(0, 36, 12):
            urls.append(f"https://apteka-ot-sklada.ru/catalog/kosmetika/dlya-muzhchin?start={page_number}")

        for page_number in range(0, 36, 12):
            urls.append(f"https://apteka-ot-sklada.ru/catalog/medikamenty-i-bady/allergiya?start={page_number}")

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, cookies= {'city': '92'})

    def parse(self, response):

        json_items = apteka(response.text)
        # print(json_items)
        for item in json_items:
            yield scrapy.Request(item["url"], callback=self.parse_detailed, meta=item)


    def parse_detailed(self, response):
        item = response.meta
        soup = BeautifulSoup(response.text, features="lxml")

        main_body = soup.find("div", {"class": "ui-collapsed-content__content"})

        text = main_body.text


        item["metadata"]["__description"] = text

        yield Item(**item).dict()