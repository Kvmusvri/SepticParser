import asyncio
import csv

import aiohttp
from bs4 import BeautifulSoup
from time import perf_counter
from asyncio import Semaphore
from selectolax.lexbor import  LexborHTMLParser
import pandas as pd


# старый результат time: 223.92
# новый результат time: 26.32 (добавили асинк)
# новый результат time: 3.96 (переписали c bs4 на selectolax и добавили запись )

async def parse_link_brands(link: str) -> list:
    async with aiohttp.ClientSession(trust_env=True) as session:
        response = await session.get(url=link)

        parser = LexborHTMLParser(await response.text())

        brands_div = parser.css('div.brands')

        links_brands = [node.attributes['href'] for node in brands_div[0].css('a') if 'href' in node.attributes]

        return links_brands


def write_links_csv(items_list: tuple) -> None:
    with open('out.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(items_list)


async def parse_current_brands(link: str, semaphore: Semaphore) -> tuple:
    await semaphore.acquire()
    async with aiohttp.ClientSession(trust_env=True, connector=aiohttp.TCPConnector(limit=400)) as session:
        response = await session.get(url=link)
        parser = LexborHTMLParser(await response.text())

        # получаем ссылки на все страницы товаров конкретного бренда
        brand_pages = parser.css('ul.page-numbers')

        # Если нашли такой ul, собираем ссылки внутри него
        pages_links = []
        if brand_pages:
            pages_links = [node.attributes['href'] for node in brand_pages[0].css('li a') if 'href' in node.attributes]
            # Если есть меню скрола, то удаляем последний элемент перехода на следующую страницу
            # добавляем в начало первую страницу
            pages_links.pop()

        pages_links.insert(0, link)

        # с каждой страницы собираем товары
        product_brand_links = []
        for page in pages_links:
            async with session.get(page) as response:
                parser = LexborHTMLParser(await response.text())

                products_page = parser.css('div.products.products-catalog')

                product_brand_links = [node.attributes['href'] for node in products_page[0].css('div.product-item a')
                                       if 'href' in node.attributes]

        for link in product_brand_links:
            if link.startswith('?'):
                product_brand_links.remove(link)

        for link in product_brand_links:
            if link == '#popup-product':
                product_brand_links.remove(link)

        semaphore.release()

        return product_brand_links

async def main():
    semaphore = Semaphore(50)
    src = "https://septikimoskva.com/catalog/"

    brand_links = await parse_link_brands(src)

    parse_tasks = []
    for link in brand_links:
        parse_tasks.append(asyncio.create_task(parse_current_brands(link, semaphore)))

    items_list = await asyncio.gather(*parse_tasks)

    out_links = sum(items_list, [])
    df_out_links = pd.DataFrame(out_links).drop_duplicates()
    df_out_links.to_csv('out.csv', sep='\t', index=False, header=False)

if __name__ == '__main__':
    start = perf_counter()
    asyncio.run(main())

    print(f"time: {(perf_counter() - start):.02f}")
