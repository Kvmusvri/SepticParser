from bs4 import BeautifulSoup
from parseBrands import parse_current_brands, parse_link_brands
import asyncio
import aiohttp
import requests
from time import perf_counter
from asyncio import Semaphore

# старый результат 25 минут
# новый результат 1223.91 (20 минут) c просто асинком
# новый результат 310.03 (5 минут) после увеличения количества подключений с 100 до 200 с vpn с выводом
# новый результат 282.03 (4,7 минутs) после увеличения количества подключений с 200 до 400 с vpn с выводом
# новый результат 378.80 (6.3 минуты) 400 подключений без впн без вывода


async def parse_current_brand_products(link: str, semaphore: Semaphore) -> dict:
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
    await semaphore.acquire()
    async with aiohttp.ClientSession(trust_env=True, connector=aiohttp.TCPConnector(limit=400)) as session:
        response = await session.get(url=link)
        soup = BeautifulSoup(await response.text(), 'lxml')

        name = await parce_name_current_brand_product(soup)
        price = await parce_price_current_brand_product(soup)
        card_pics = await parse_pics_current_brand_product(soup)

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

    await session.close()

    semaphore.release()

    # print(card_char)

    return card_char


async def parse_pics_current_brand_product(soup: BeautifulSoup) -> list:
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
    feature = soup.find('div', class_='sidebar-content__info')
    if feature:
        feature_tabe = feature.find().find('table')
        if feature_tabe:
            for row in feature:
                card_char[row.find('th').get_text()] = row.find('td').get_text()

    return card_char


async def parce_name_current_brand_product(soup: BeautifulSoup) -> str:
    name = ''
    # сохраняем имя и цену
    name_field = soup.find('h1', class_='product_title entry-title')
    if name_field:
        name = name_field.get_text()

    return name


async def parce_price_current_brand_product(soup: BeautifulSoup) -> int:
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


async def main():
    semaphore_itmes = Semaphore(25)
    semaphore_links = Semaphore(25)
    src = "https://septikimoskva.com/catalog/"
    brand_links = await parse_link_brands(src)

    parse_items_links_from_brands_tasks = []
    for link in brand_links:
        parse_items_links_from_brands_tasks.append(asyncio.create_task(parse_current_brands(link, semaphore_links)))

    items_list = await asyncio.gather(*parse_items_links_from_brands_tasks)

    parse_items_from_links_tasks = []
    for list_links in items_list:
        # сильно тормозит добавление
        for item_link in list_links:
            parse_items_from_links_tasks.append(asyncio.create_task(parse_current_brand_products(item_link,
                                                                                                 semaphore_itmes)))

        await asyncio.gather(*parse_items_from_links_tasks)
        parse_items_from_links_tasks.clear()


if __name__ == '__main__':
    start = perf_counter()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    print(f"time: {(perf_counter() - start):.02f}")