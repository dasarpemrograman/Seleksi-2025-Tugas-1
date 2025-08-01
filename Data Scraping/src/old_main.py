import json
from bs4 import Comment, NavigableString
from utils import tvtropes as tv

BASE_URL = "https://tvtropes.org"
visited_links = set()

def load_series(filepath="output.json"):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_valid_uls(article):
    # Find only ul tags inside article > div > ul or article > div > div > ul
    return article.select("article > div > ul, article > div > div > ul")

def extract_linked_items_from_article(article, depth=0):
    if not article:
        return []

    trope_entries = []
    uls = extract_valid_uls(article)

    for ul in uls:
        for li in ul.find_all("li", recursive=False):
            a = li.find("a")

            # Recurse into "Tropes ..." links but don't extract
            if a and a.text.strip().startswith("Tropes "):
                href = a.get("href")
                if href:
                    full_url = href if href.startswith("http") else BASE_URL + href
                    if full_url not in visited_links:
                        visited_links.add(full_url)
                        sub_article = tv.get_article(full_url)
                        trope_entries.extend(extract_linked_items_from_article(sub_article, depth=depth+1))
                continue

            # Extract trope_name from first <a>, and everything else as usage
            trope_name = None
            usage_parts = []
            found_first_link = False

            for node in li.children:
                if isinstance(node, Comment):
                    continue  # skip <!-- comments -->
                if node.name == "a":
                    if not found_first_link:
                        trope_name = node.text.strip()
                        found_first_link = True
                    else:
                        usage_parts.append(node.text.strip())
                elif isinstance(node, NavigableString):
                    usage_parts.append(node.strip())
                elif hasattr(node, "get_text"):
                    usage_parts.append(node.get_text(strip=True))

            if trope_name:
                usage_text = " ".join(filter(None, usage_parts)).strip().lstrip(": ")
                trope_entries.append({
                    "trope_name": trope_name,
                    "trope_usage": usage_text
                })

    return trope_entries

def get_series_items(index, series_data):
    entry = series_data[index]
    link = entry['link']
    name = entry['name']
    full_url = link if link.startswith("http") else BASE_URL + link

    if full_url in visited_links:
        return None

    visited_links.add(full_url)
    article = tv.get_article(full_url)
    tropes = extract_linked_items_from_article(article)

    return {
        "series_name": name,
        "series_link": full_url,
        "series_tropes": tropes
    }

def get_all_series_items(series_data):
    all_data = []
    total = len(series_data)

    for index, _ in enumerate(series_data):
        result = get_series_items(index, series_data)
        if result:
            all_data.append(result)

        print(f"[{index + 1}/{total}] {((index + 1)/total)*100:.2f}% — Series collected: {len(all_data)}")

    return all_data

def main():
    series_data = load_series()

    # 🔍 Only process the first 10 series
    result = get_all_series_items(series_data)

    # Save to JSON
    with open("../data/series_tropes_sample.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
