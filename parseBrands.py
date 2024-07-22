from main import bs_response


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
    products = soup.find_all('div', class_='product-item')
    links_product = []
    for prod in products:
        prod_link = prod.find_all('a')
        for link in prod_link:
            if 'http' in link.get('href'):
                links_product.append(link.get('href'))

    links_product = remove_dup(links_product)

    return links_product


if __name__ == '__main__':
    src = "https://septikimoskva.com/catalog/"
    link_brand = 'https://septikimoskva.com/catalog/evrolos/'
    parse_current_brands(link_brand)
