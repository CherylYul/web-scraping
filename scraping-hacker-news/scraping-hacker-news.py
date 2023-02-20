import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

articles = []
url = "https://news.ycombinator.com/news"

r = requests.get(url)
soup = BeautifulSoup(r.text, "html.parser")

for new in soup.find_all("tr", class_="athing"):
    # title vs link
    link_title = new.find("span", class_="titleline").find("a")
    new_title = link_title.get_text(strip=True) if link_title else None
    new_link = link_title.get("href") if link_title else None

    # parent page
    parent_page = new.find("span", class_="sitestr")
    parent_page = parent_page.get_text(strip=True) if parent_page else None

    next_row = new.find_next_sibling("tr")

    # score
    score = next_row.find("span", class_="score")
    score = score.get_text(strip=True) if score else "0 points"
    # username vs userlink
    user = next_row.find("a", class_="hnuser")
    user_name = user.get_text(strip=True) if user else None
    user_link = user.get("href") if user else None
    user_link = urljoin(url, user_link)
    # posted time
    posted_time = next_row.find("span", class_="age")
    posted_time = posted_time.get("title").replace("T", " ") if posted_time else None
    # number of comments
    comments = next_row.find("a", string=re.compile("\d+(&nbsp;|\s)comment(s?)"))
    comments = (
        comments.get_text(strip=True).replace("\xa0", " ") if comments else "0 comments"
    )

    articles.append(
        {
            "new_title": new_title,
            "new_link": new_link,
            "parent_page": parent_page,
            "score": score,
            "username": user_name,
            "user_link": user_link,
            "posted_time": posted_time,
            "number_of_comments": comments,
        }
    )

df = pd.DataFrame(
    columns=[
        "new_title",
        "new_link",
        "parent_page",
        "score",
        "username",
        "user_link",
        "posted_time",
        "number_of_comments",
    ]
)
for article in articles:
    df = df.append(pd.Series(article), ignore_index=True)
df.to_csv("hacker_news.csv")
