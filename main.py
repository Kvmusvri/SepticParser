from bs4 import BeautifulSoup
import requests
from parseBrands import parse_current_brands, parse_link_brands
from parseProducts import parse_current_brand_products
import time

def main() -> None:
    start = time.time()
    # заменить на конструкцию try\except
    broken_page = ['https://septikimoskva.com/catalog/kit/',
                   'https://septikimoskva.com/catalog/kit/kit-bio/',
                   'https://septikimoskva.com/catalog/kit/kit-pro/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-bio-3-vrezka-425mm/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-bio-3-vrezka-635mm/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-bio-3-vrezka-825mm/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-bio-5-vrezka-515mm/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-4-500/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-bio-5-vrezka-725mm/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-4-700/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-bio-5-vrezka-925mm/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-5-500/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-5-700/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-4-1300/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-5-1300/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-8-500/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-8-700/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-8-1300/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-10-500/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-10-700/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-10-1300/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-15-500/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-pro-15-700/',
                   'https://septikimoskva.com/catalog/septiki/filter/0-5-m/septik-kit-4s-1300/']

    # broken_page=[]
    src = "https://septikimoskva.com/catalog/"
    # Собираем бренды
    brands_links = parse_link_brands(src)

    # Проходимся по каждому бренду и собираем ссылки на товары
    for link in brands_links:
        print(link)
        brand_items_links = parse_current_brands(link)
        # Парсим полученный список товаров бренда
        for brand_link in brand_items_links:
            # try:
            #     if brand_link in broken_page:
            #         continue
            #     parse_current_brand_products(brand_link)
            # except AttributeError:
            #     broken_page.append(brand_link)
            #     print(f"Сломанные страницы: {broken_page}")
            #     continue
            if brand_link in broken_page:
                continue
            parse_current_brand_products(brand_link)

    print(f"Время выполнения в секундах {(time.time() - start)}")
    print(f"Время выполнения в минутах {(time.time() - start)/60}")




if __name__ == '__main__':
    main()