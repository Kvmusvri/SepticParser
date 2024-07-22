from bs4 import BeautifulSoup
import requests
from parseBrands import *


def bs_response(link: str) -> BeautifulSoup:
    response = requests.get(link).text
    soup = BeautifulSoup(response, "lxml")

    return soup


def main() -> None:
    src = "https://septikimoskva.com/catalog/"
    brands_links = parse_link_brands(src)
    for link in brands_links:
        parse_current_brands(link)




if __name__ == '__main__':
    main()