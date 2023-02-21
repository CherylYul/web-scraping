import requests
import pandas as pd
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from datetime import datetime

base_url = "http://books.toscrape.com/"
columns = [
    "book_id",
    "url",
    "title",
    "image",
    "price",
    "stock_status",
    "rating",
    "description",
    "tech_specs",
    "date_time",
]
df = pd.DataFrame(columns=columns)
books = {}


def scrape_book_id(html_soup, base_url, books_id=[]):
    for book in html_soup.find_all("article", class_="product_pod"):
        book_url = book.find("h3").find("a").get("href")
        if len(book_url.split("/")) < 3:
            book_url = "catalogue/" + book_url
        book_url = urljoin(base_url, book_url)
        book_path = urlparse(book_url).path
        book_id = book_path.split("/")[2]
        books_id.append([book_id, book_url])
    return books_id


def scrape_details(html_soup):
    main = html_soup.find(class_="product_main")
    title = main.find("h1").get_text(strip=True)
    price = main.find(class_="price_color").get_text(strip=True)
    stock_status = main.find(class_="availability").get_text(strip=True)
    rating = (
        " ".join(main.find(class_="star-rating").get("class"))
        .replace("star-rating", "")
        .strip()
    )

    image = html_soup.find(id="product_gallery").find("img").get("src")
    desc_check = html_soup.find(id="product_description")
    desc = desc_check.find_next_sibling("p").get_text(strip=True) if desc_check else ""
    table_info_check = html_soup.find(string="Product Information")
    if table_info_check:
        table_info = table_info_check.find_next("table")
        tech_specs = {}
        for row in table_info.find_all("tr"):
            name = row.find("th").get_text(strip=True)
            name = re.sub("[^a-zA-Z]+", "_", name)
            value = row.find("td").get_text(strip=True)
            tech_specs[name] = value
    else:
        tech_specs = ""
    date_time = datetime.now()
    return title, image, price, stock_status, rating, desc, tech_specs, date_time


url = base_url
books_id = []
while True:
    print("scraping: ", url)
    r = requests.get(url)
    html_soup = BeautifulSoup(r.text, "html.parser")
    books_id = scrape_book_id(html_soup, base_url, books_id)
    next_page = html_soup.select("li.next > a")
    print("we will scrape: ", next_page)
    if not next_page or not next_page[0].get("href"):
        break
    next_page_path = next_page[0].get("href")
    if len(next_page_path.split("/")) < 2:
        next_page_path = "catalogue/" + next_page[0].get("href")
    print("fix the path", next_page_path)
    url = urljoin(base_url, next_page_path)

for book in books_id:
    book_id, book_url = book[0], book[1]
    print(book_id, book_url)
    r = requests.get(book_url)
    html_soup = BeautifulSoup(r.text, "html.parser")
    (
        title,
        image,
        price,
        stock_status,
        rating,
        desc,
        tech_specs,
        date_time,
    ) = scrape_details(html_soup)
    df = pd.concat(
        [
            df,
            pd.Series(
                {
                    "book_id": book_id,
                    "url": book_url,
                    "title": title,
                    "image": image,
                    "price": price,
                    "stock_status": stock_status,
                    "rating": rating,
                    "description": desc,
                    "tech_specs": tech_specs,
                    "date_time": date_time,
                }
            )
            .to_frame()
            .T,
        ],
        ignore_index=True,
    )
df.to_csv("books_retailer.csv")
