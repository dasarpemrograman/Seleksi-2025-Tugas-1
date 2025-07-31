import requests
from bs4 import BeautifulSoup

def scrape_basic_html(url):
    """Basic HTML scraping function"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        return soup
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def scrape_genres():
    url = "https://tvtropes.org/pmwiki/pmwiki.php/Main/Series"
    soup = scrape_basic_html(url)

    if not soup:
        return []

    genres = []
    location = soup.find('span', class_='asscaps')
    list = location.find_next('ul')
    for genre in list.find_all('li'):
        curr = []
        genres.append({
            "name":genre.get_text().removesuffix("\n").removeprefix(" "),
        })
    return genres
print(scrape_genres())
