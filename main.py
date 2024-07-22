from bs4 import BeautifulSoup
import requests
from parseBrands import parse_current_brands, parse_link_brands
from parseProducts import parse_current_brand_products


def main() -> None:
    src = "https://septikimoskva.com/catalog/"
    # Собираем бренды
    brands_links = parse_link_brands(src)

    # Проходимся по каждому бренду и собираем ссылки на товары
    for link in brands_links:
        brand_items_links = parse_current_brands(link)
        # Парсим полученный список товаров бренда
        parse_current_brand_products(brand_items_links)


if __name__ == '__main__':
    main()