from parseBrands import parse_current_brands, parse_link_brands
from parseProducts import parse_current_brand_products
from time import perf_counter
from asyncio import Semaphore
import csv
import asyncio
from exportExcel import excel_export
from parseBrands import parse_items_links_into_csv
import pandas as pd


async def main() -> None:
    semaphore_items = Semaphore(25)

    await parse_items_links_into_csv()

    with open('all_products_link.csv', newline='') as f:
        reader = csv.reader(f)
        items_links_list = list(reader)

    parse_items_from_links_tasks = []
    for item_link in items_links_list:
        parse_items_from_links_tasks.append(asyncio.create_task(parse_current_brand_products(item_link[0], semaphore_items)))

    items_cards = await asyncio.gather(*parse_items_from_links_tasks)

    excel_export(items_cards)


if __name__ == '__main__':
    start = perf_counter()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    print(f"time: {(perf_counter() - start):.02f}")