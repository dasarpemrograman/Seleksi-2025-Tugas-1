import requests
import json
from bs4 import BeautifulSoup

def scrape(url):
    """Scrape the URL"""

    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "lxml")
        return soup
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def get_article(url):
    soup = scrape(url)
    article = soup.find(id="main-article")
    return article

def get_table(article):
    article = article.find("table")
    contents = []
    for row in article.find_all("td"):
        contents.append({
            "link":row.find('a').get('href'),
            "name":row.text.replace("\xa0", " ").strip()
        })
    return contents

def get_every_series():
    url = "https://tvtropes.org/pmwiki/pagelist_having_pagetype_in_namespace.php?n=Series&t=work&page=1"
    soup = scrape(url)
    number_of_pages = int(soup.select_one("#wikimiddle > nav").get("data-total-pages"))
    url = url.removesuffix("1")
    contents = []
    for i in range(number_of_pages):
        curr_page = int(i + 1)
        curr_url = url + str(curr_page)
        article = get_article(curr_url)
        table = get_table(article)
        contents.extend(table)
    return contents

def save_as_json(a_list):

    # Save to a file
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(a_list, f, indent=2, ensure_ascii=False)
