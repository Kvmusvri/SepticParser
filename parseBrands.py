from bs4 import BeautifulSoup
import requests


def bs_response(link: str) -> BeautifulSoup:
    response = requests.get(link).text
    soup = BeautifulSoup(response, "lxml")

    return soup


def parse_link_brands(link: str) -> list:
    soup = bs_response(link)
    brands = soup.find('div', class_='brands').find_all('a')

    links_brands = []
    for link in brands:
        links_brands.append(f"{link.get('href')}")

    return links_brands


def parse_current_brands(link: str) -> list:
    soup = bs_response(link)

    # получаем ссылки на все страницы товаров конкретного бренда
    brand_pages = soup.find_all('a', class_='page-numbers')
    pages_links = []
    for page in brand_pages:
        pages_links.append(page.get('href'))

    # Если есть меню скрола, то удаляем последний элемент перехода на следующую страницу
    # добавляем в начало первую страницу
    if pages_links:
        pages_links.pop()
    pages_links.insert(0, link)

    # с каждой страницы собираем товары
    links_product_brand = []
    for page in pages_links:
        soup = bs_response(page)

        # получаем все товары на странице
        products = soup.find_all('div', class_='products products-catalog')
        for prod in products:
            for item in prod:
                # Проходимся по каждому товару и собираем ссылки
                page_items = item.find_all('div', class_='product-item')
                for item_link in page_items:
                    links_product_brand.append(item_link.find('a').get('href'))

    return links_product_brand


if __name__ == '__main__':
    src = "https://septikimoskva.com/catalog/"
    link_brand = 'https://septikimoskva.com/catalog/evrolos/'
    parse_current_brands(link_brand)
