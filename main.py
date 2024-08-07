from parseBrands import parse_current_brands, parse_link_brands
from parseProducts import parse_current_brand_products
from time import perf_counter
from asyncio import Semaphore
import csv
import asyncio
from exportExcel import excel_export
import pandas as pd




async def main() -> None:
    semaphore_items = Semaphore(25)
    semaphore_links = Semaphore(25)

    with open('out.csv', newline='') as f:
        reader = csv.reader(f)
        list_of_csv = list(reader)

    parse_items_from_links_tasks = []
    for list_links in list_of_csv:
        for item_link in list_links:
            parse_items_from_links_tasks.append(asyncio.create_task(parse_current_brand_products(item_link,
                                                                                                 semaphore_items)))
    items_dict = await asyncio.gather(*parse_items_from_links_tasks)

    excel_export(items_dict)



if __name__ == '__main__':
    start = perf_counter()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

    # link_test = ['https://septikimoskva.com/catalog/evrolos/septik-udacha-1/']
    # asyncio.run(test_one_septic(link_test))

    print(f"time: {(perf_counter() - start):.02f}")