from parseBrands import bs_response
from bs4 import BeautifulSoup
import requests

# собираем словарь товара, чтобы передать его дальше
def parse_supplies(link: str) -> dict:
    # получаем ссылку на конкретный товар
    # в словарь записываем характеристики
    product = {}
    soup = bs_response(link)


    return product

# собираем ссылки на изображение товара
def parse_image(link: str) -> list:
    pass

# собираем характеристики товара в текстовом формате
def parse_characteristic(link: str) -> list:
    pass

# собираем описание товара в формате html
def parse_desc(link: str) -> str:
    pass


if __name__ == '__main__':
    src = 'https://septikimoskva.com/catalog/evrolos/septik-udacha-1/'
    parse_supplies(src)
