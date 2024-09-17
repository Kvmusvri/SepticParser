import asyncio
import aiohttp
from time import perf_counter
from asyncio import Semaphore
import csv
from selectolax.lexbor import LexborHTMLParser


async def parse_current_brand_products(link: str, main_brand: str, sub_brand: str, semaphore: Semaphore) -> dict:
    """
    Собираем следующие поля с переданной карточки товара
    name - имя
    price - цена
    card_pics - изображения товара
    work_principle - принцип работы, собирается в формате HTML
    feature - характеристики товара

    :param link: ссылка на карточку товара
    :type link: str

    :param main_brand: основной бренд товара
    :type main_brand: str

    :param sub_brand: суббренд товара
    :type sub_brand: str

    :rtype: dict:
    :return: card_char - словарь данных карточки товара
    """
    await semaphore.acquire()
    async with aiohttp.ClientSession(trust_env=True, connector=aiohttp.TCPConnector(limit=100)) as session:
        response = await session.get(url=link)
        parser = LexborHTMLParser(await response.text())

        # brand_name = await parse_brand(parser)
        main_brand_name = main_brand

        sub_brand_name = sub_brand

        name = await parce_name_current_brand_product(parser)

        price = await parce_price_current_brand_product(parser)

        card_pics = await parse_pics_current_brand_product(parser)

        work_principle = await parse_work_principle(parser)

        docs_links = await parse_dock(parser)

        card_char = {
            'Бренд': main_brand_name,
            'Суббренд': sub_brand_name,
            'Ссылка': link,
            'Наименование': name,
            'Цена ₽': price,
            'Изображение': card_pics,
            'Документация': docs_links,
            'Принцип работы': work_principle,
        }

        card_char = parce_feature_current_brand_product(parser, card_char)

    await session.close()

    print(card_char)

    semaphore.release()

    return card_char


async def parse_brand(parser: LexborHTMLParser) -> str:
    brand_name = ''

    brand_field = parser.css('#breadcrumbs > span > span:nth-child(3) > a')

    if brand_field:
        brand_name = brand_field[0].text()

    return brand_name


async def parse_work_principle(parser: LexborHTMLParser) -> str:
    # сохраняем принцип работы в формате html
    work_principle = ''

    work_principle_field = parser.css('div.woocommerce-tabs .woocommerce-Tabs-panel')

    if work_principle_field:
        work_principle = work_principle_field[0].html

    return work_principle


async def parse_dock(parser: LexborHTMLParser) -> list:
    docs_links = []

    docs_field = parser.css('#tab-docs > p')

    if docs_field:
        docs_links = [node.attributes['href'] for node in docs_field[0].css('a') if 'href' in node.attributes]

    return docs_links


async def parse_pics_current_brand_product(parser: LexborHTMLParser) -> list:
    # Сохраняем изображение в виде ссылок
    img_links = []
    card_pics = parser.css('div.sidebar-content__img')

    if card_pics:
        img_links = [node.attributes['href'] for node in card_pics[0].css('a') if 'href' in node.attributes]

    return img_links


def parce_feature_current_brand_product(parser: LexborHTMLParser, card_char: dict) -> dict:
    # Сохраняем характеристики товара
    rows = parser.css('tr.woocommerce-product-attributes-item')

    for row in rows:
        label = row.css_first('th.woocommerce-product-attributes-item__label').text(strip=True)
        value = row.css_first('td.woocommerce-product-attributes-item__value').text(strip=True)
        card_char[label] = value

    return card_char


async def parce_name_current_brand_product(parser: LexborHTMLParser) -> str:
    name = ''
    # сохраняем имя и цену
    name_field = parser.css('h1')
    if name_field:
        name = name_field[0].text()

    return name


async def parce_price_current_brand_product(parser: LexborHTMLParser) -> int:
    # Цены может не быть, тогда на сайте будет указано По заказу
    price = 'По заказу'
    price_field = parser.css('div.sidebar-content__product')

    if price_field:
        sale_price = price_field[0].css('ins')
        if sale_price:
            price = int(''.join(sale_price[0].text()[:-2].split()))
        else:
            normal_price = price_field[0].css('bdi')
            if normal_price:
                price = int(''.join(normal_price[0].text()[:-2].split()))

    return price


async def main():
    semaphore_items = Semaphore(25)
    # semaphore_links = Semaphore(25)

    with open('out.csv', 'r') as read_obj:
        csv_reader = csv.reader(read_obj)
        list_of_csv = list(csv_reader)

    parse_items_from_links_tasks = []
    for list_links in list_of_csv:
        for item_link in list_links:
            parse_items_from_links_tasks.append(asyncio.create_task(parse_current_brand_products(item_link,

                                                                                                 semaphore_items)))
    await asyncio.gather(*parse_items_from_links_tasks)


if __name__ == '__main__':
    start = perf_counter()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    print(f"time: {(perf_counter() - start):.02f}")