from bs4 import BeautifulSoup
from parseBrands import bs_response
import requests


def parse_current_brand_products(link: str) -> dict:
    """
    Собираем следующие поля с переданной карточки товара
    name - имя
    price - цена
    card_pics - изображения товара
    work_principle - принцип работы, собирается в формате HTML
    feature - характеристики товара

    :param link:
    :type link: str

    :rtype: dict:
    :return: card_char - словарь данных карточки товара
    """
    soup = bs_response(link)
    name = parce_name_current_brand_product(soup)
    price = parce_price_current_brand_product(soup)
    card_pics = parse_pics_current_brand_product(soup)

    # сохраняем принцип работы в формате html
    work_principle = soup.find('div',
                               class_='woocommerce-Tabs-panel woocommerce-Tabs-panel--description panel entry-content wc-tab')

    card_char = {
        'Ссылка': link,
        'Наименование': name,
        'Цена ₽': price,
        'Изображение': card_pics,
        'Принцип работы': work_principle
    }

    card_char = parce_feature_current_brand_product(soup, card_char)

    print(card_char)

    return card_char


def parse_pics_current_brand_product(soup: BeautifulSoup) -> list:
    # Сохраняем изображение в виде ссылок
    img_links =[]
    card_pics = soup.find_all('div',
                              class_='woocommerce-product-gallery woocommerce-product-gallery--with-images woocommerce-product-gallery--columns-4 images')
    if card_pics:
        for card in card_pics:
            img_link = card.find_all('a')
            for link in img_link:
                img_links.append(link['href'])

    return img_links


def parce_feature_current_brand_product(soup: BeautifulSoup, card_char: dict) -> dict:
    # Сохраняем характеристики товара
    feature = soup.find('div', class_='sidebar-content__info').find('table')
    if feature:
        for row in feature:
            card_char[row.find('th').get_text()] = row.find('td').get_text()

    return card_char


def parce_name_current_brand_product(soup: BeautifulSoup) -> str:
    name = ''
    # сохраняем имя и цену
    name_field = soup.find('h1', class_='product_title entry-title')
    if name_field:
        name = name_field.get_text()

    return name


def parce_price_current_brand_product(soup: BeautifulSoup) -> int:
    # Цены может не быть, тогда на сайте будет указано По заказу
    price = 'По заказу'
    price_field = soup.find('div', class_='row price-row')

    if price_field:
        # Цена может быть со скидкой, тогда собираем вариант со скидкой
        sale_price_field = price_field.find('ins')
        if sale_price_field:
            price = int(''.join(sale_price_field.get_text()[0:-2].split()))
        else:
            # Если цена указана без скидки, то собираем ее
            normal_price_field = price_field.find('bdi')
            if normal_price_field:
                price = int(''.join(normal_price_field.get_text()[0:-2].split()))

    return price


if __name__ == '__main__':
    src = 'https://septikimoskva.com/catalog/multplast/septik-termit-profi-0-7-s/'
    parse_current_brand_products(src)