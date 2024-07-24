from bs4 import BeautifulSoup
import requests


def bs_response(link: str) -> BeautifulSoup:
    response = requests.get(link).text
    soup = BeautifulSoup(response, "lxml")

    return soup


def remove_dup(seq: list) -> list:
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def parse_link_brands(link: str) -> list:
    soup = bs_response(link)

    brands = soup.find('div', class_='brands').find_all('a')

    links = []
    for link in brands:
        links.append(link.get('href'))

    return links


def parse_current_brands(link: str) -> list:
    soup = bs_response(link)
    products_pages = soup.find('ul', class_='page-numbers').find_all('a')

    pages_links = []
    for pg_link in products_pages:
        pages_links.append(pg_link['href'])

    if pages_links:
        pages_links.pop()

    pages_links.insert(0, link)

    links_product = []
    for page_link in pages_links:
        print(page_link)
        soup = bs_response(page_link)
        products = soup.find_all('div', class_='products products-catalog')

        for prod in products:
            prod_link = prod.find_all('a')
            # print(prod_link)
            for item_link in prod_link:
                if 'https' in item_link['href']:
                    print(item_link['href'])
                    links_product.append(item_link['href'])

    links_product = remove_dup(links_product)
    print(len(links_product))

    return links_product


if __name__ == '__main__':
    src = "https://septikimoskva.com/catalog/"
    link_brand = 'https://septikimoskva.com/catalog/evrolos/'
    parse_current_brands(link_brand)
