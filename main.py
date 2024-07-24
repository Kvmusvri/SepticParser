from parseBrands import parse_current_brands, parse_link_brands
from parseSuplies import parse_supplies
from exportExcel import excel_export
from bs4 import BeautifulSoup
import requests


def main() -> None:
    src = "https://septikimoskva.com/catalog/"
    brands_links = parse_link_brands(src)
    for link in brands_links:
        single_brand_link = parse_current_brands(link)
        for sup_link in single_brand_link:
            current_brand_supplies = parse_supplies(sup_link)
            excel_export(current_brand_supplies)


if __name__ == '__main__':
    main()