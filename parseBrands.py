import asyncio
import aiohttp
from bs4 import BeautifulSoup
import requests
from time import perf_counter
from asyncio import Semaphore

# старый результат time: 223.92
# новый результат time: 26.32


async def parse_link_brands(link: str) -> list:
    async with aiohttp.ClientSession(trust_env=True) as session:
        response = await session.get(url=link)
        soup = BeautifulSoup(await response.text(), "lxml")
        brands = soup.find('div', class_='brands').find_all('a')

        links_brands = []
        for link in brands:
            links_brands.append(f"{link.get('href')}")

        return links_brands


async def parse_current_brands(link: str, semaphore: Semaphore) -> list:
    await semaphore.acquire()
    async with aiohttp.ClientSession(trust_env=True, connector=aiohttp.TCPConnector(limit=400)) as session:
        response = await session.get(url=link)
        soup = BeautifulSoup(await response.text(), "lxml")

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
        product_brand_links = []
        for page in pages_links:
            async with session.get(page) as response:
                soup = BeautifulSoup(await response.text(), "lxml")

                products_page = (soup.find('div', class_='products products-catalog')
                                 .find_all('div', class_='product-item'))
                for item in products_page:
                    item_link = item.find('a')['href']
                    product_brand_links.append(item_link)

    await session.close()

    semaphore.release()

    # print(product_brand_links)

    return product_brand_links


async def main():
    src = "https://septikimoskva.com/catalog/"
    brand_links = await parse_link_brands(src)
    parse_tasks = []
    count_tasks = 0
    for link in brand_links:
        parse_tasks.append(asyncio.create_task(parse_current_brands(link)))

    items_list = await asyncio.gather(*parse_tasks)



if __name__ == '__main__':
    start = perf_counter()
    asyncio.run(main())
    print(f"time: {(perf_counter() - start):.02f}")
