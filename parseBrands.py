import asyncio
import csv
import aiohttp
from time import perf_counter
from asyncio import Semaphore
from selectolax.lexbor import LexborHTMLParser
import pandas as pd


# старый результат time: 223.92
# новый результат time: 26.32 (добавили асинк)
# новый результат time: 3.96 (переписали c bs4 на selectolax и добавили запись )

async def parse_link_brands(catalog_link: str, links_brand: list) -> None:
    # Собираем ссылки на бренды
    async with aiohttp.ClientSession(trust_env=True) as session:
        response = await session.get(url=catalog_link)

        parser = LexborHTMLParser(await response.text())

        brands_div = parser.css('div.brands')

        links_brands = [node.attributes['href'] for node in brands_div[0].css('a') if 'href' in node.attributes and
                        node.attributes['href'] not in links_brand]

        with open('brands_links.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(links_brands)


async def parse_link_brands(catalog_link: str) -> None:
    # перегрузка под случай, если файл с ссылками на бренды не существует
    async with aiohttp.ClientSession(trust_env=True) as session:
        response = await session.get(url=catalog_link)

        parser = LexborHTMLParser(await response.text())

        brands_div = parser.css('div.brands')

        links_brands = [node.attributes['href'] for node in brands_div[0].css('a') if 'href' in node.attributes]

        with open('brands_links.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows([links_brands])


def write_links_csv(items_list: tuple) -> None:
    # записываем полученные ссылки в csv
    out_links = sum(items_list, [])
    df_out_links = pd.DataFrame(out_links).drop_duplicates()
    df_out_links.to_csv('all_products_link.csv', sep='\t', index=False, header=False)


async def parse_current_brands(link: str, semaphore: Semaphore) -> list:
    await semaphore.acquire()
    async with aiohttp.ClientSession(trust_env=True, connector=aiohttp.TCPConnector(limit=400)) as session:
        response = await session.get(url=link)
        parser = LexborHTMLParser(await response.text())

        # получаем ссылки на все страницы товаров конкретного бренда
        brand_pages = parser.css('ul.page-numbers')

        # сохраняем название бренда
        # могут быть суббренды, а на сайте поломанная система ссылок
        # из-за чего потом суббренд собрать будет невозможно
        sub_brand_brand_field = parser.css('#breadcrumbs > span > span.breadcrumb_last')[0].text()
        main_brand_field = parser.css('#breadcrumbs > span > span:nth-child(3)')[0].text()

        # Если нашли такой ul, собираем ссылки внутри него
        pages_links = []
        if brand_pages:
            pages_links = [node.attributes['href'] for node in brand_pages[0].css('li a') if 'href' in node.attributes]
            # Если есть меню скрола, то удаляем последний элемент перехода на следующую страницу
            # добавляем в начало первую страницу
            pages_links.pop()

        pages_links.insert(0, link)

        # с каждой страницы собираем ссылки на товары
        product_brand_links = []
        for page in pages_links:
            # print(page)
            async with session.get(page) as response:
                parser = LexborHTMLParser(await response.text())
                products_page = parser.css('body > div.content-area > div.sidebar-content > div.inner-page.row > div.sidebar-content__right > div.products.products-catalog')

                for node in products_page[0].css('div.row a:nth-child(1)'):
                    product_brand_links.append(f"{main_brand_field}*{sub_brand_brand_field}*{node.attributes['href']}")

        semaphore.release()

        return product_brand_links


async def parse_items_links_into_csv():
    semaphore = Semaphore(50)
    src = "https://septikimoskva.com/catalog/"

    try:
        with open('brands_links.csv', newline='') as f:
            reader = csv.reader(f)
            brand_links = list(reader)

            await parse_link_brands(src, brand_links)
    except:
        await parse_link_brands(src)

    with open('brands_links.csv', newline='') as f:
        reader = csv.reader(f)
        brand_links = list(reader)

    tl = 'https://septikimoskva.com/catalog/evrolos/evrolos-bio/'
    print(await parse_current_brands(tl, semaphore))

    # parse_tasks = []
    # for link in brand_links:
    #     for l in link:
    #         parse_tasks.append(asyncio.create_task(parse_current_brands(l, semaphore)))
    #
    # items_list = await asyncio.gather(*parse_tasks)

    # write_links_csv(items_list)


if __name__ == '__main__':
    start = perf_counter()
    asyncio.run(parse_items_links_into_csv())

    print(f"time: {(perf_counter() - start):.02f}")
