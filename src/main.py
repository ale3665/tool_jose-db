import requests
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Any, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import click
from pandas import DataFrame
from progress.bar import Bar

from src.db import DB

ARTICLES_URL_TEMPLATE = "https://jose.theoj.org/papers?page={}"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def download_listing_pages(total_pages: int = 12) -> DataFrame:
    data = {"url": [], "html": [], "page": []}
    print("⚡ Downloading listing pages from JOSE...")

    for page in range(1, total_pages + 1):
        url = ARTICLES_URL_TEMPLATE.format(page)
        print(f"📄 Fetching listing page {page}: {url}")
        try:
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                data["url"].append(url)
                data["html"].append(response.text)
                data["page"].append(page)
        except Exception as e:
            print(f"[ERROR] Failed to fetch page {page}: {e}")

    print(f"✅ Downloaded {len(data['url'])} listing pages successfully.")
    return DataFrame(data)


def get_all_article_urls() -> List[Tuple[str, int]]:
    print("🔎 Scraping article URLs from JOSE...")
    all_urls: List[Tuple[str, int]] = []

    for page in range(1, 13):
        url = ARTICLES_URL_TEMPLATE.format(page)
        response = requests.get(url, headers=HEADERS, timeout=60)
        if response.status_code != 200:
            print(f"[WARN] Failed to load page {page}")
            continue

        soup = BeautifulSoup(response.content, "lxml")
        cards = soup.find_all("div", class_="paper-card")

        page_urls = [
            (card.find("a")["href"], page)
            for card in cards
            if card.find("a") and card.find("a")["href"].startswith("https://jose.theoj.org/papers/")
        ]

        all_urls.extend(page_urls)
        print(f"✅ Found {len(page_urls)} articles on page {page}")

    unique_urls = list(set(all_urls))
    print(f"✅ Total unique articles found: {len(unique_urls)}")
    return unique_urls


def download_article_pages(urls_with_pages: List[Tuple[str, int]]) -> DataFrame:
    data = {"url": [], "html": [], "page": []}
    print("⚡ Downloading HTML front matter of JOSE articles...")

    def fetch(index: int, url: str, page: int) -> Tuple[str, bytes | None, int]:
        try:
            print(f"📄 Fetching {index + 1}/{len(urls_with_pages)}: {url}")
            response = requests.get(url, headers=HEADERS, timeout=30)
            if response.status_code == 200:
                return url, response.content, page
            else:
                return url, None, page
        except Exception as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            return url, None, page

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(fetch, i, url, page) for i, (url, page) in enumerate(urls_with_pages)]
        for future in as_completed(futures):
            url, content, page = future.result()
            if content:
                data["url"].append(url)
                data["html"].append(content)
                data["page"].append(page)

    print(f"✅ Downloaded {len(data['url'])} articles successfully.")
    return DataFrame(data)


def extract_metadata(df: DataFrame) -> DataFrame:
    data: List[dict[str, Any]] = []

    with Bar("Extracting paper metadata from HTML...", max=df.shape[0]) as bar:
        for idx, row in df.iterrows():
            soup = BeautifulSoup(row["html"], "lxml")

            try:
                # Title
                title_tag = soup.find("meta", attrs={"name": "citation_title"})
                
                if title_tag and title_tag.get("content"):
                    title = title_tag["content"].strip()
                else:
                    h2_title = soup.find("h2", class_="paper-title")
                    if h2_title and h2_title.text.strip():
                        title = h2_title.text.strip()
                    else:
                        html_title = soup.find("title")
                        title = html_title.text.strip().split("·")[0] if html_title else ""

                # Authors
                author_tags = soup.find_all("meta", attrs={"name": "citation_author"})
                if not author_tags:
                    submitted_by = soup.find("div", class_="submitted_by")
                    author = submitted_by.text.strip() if submitted_by else ""
                    authors = author
                else:
                    authors = "; ".join(tag["content"].strip() for tag in author_tags if tag.get("content"))

                # Publication date
                pub_date_tag = soup.find("meta", attrs={"name": "citation_publication_date"})
                if not pub_date_tag:
                    time_tag = soup.find("span", class_="time")
                    pub_date = time_tag.text.strip() if time_tag else ""
                else:
                    pub_date = pub_date_tag["content"].strip()

                # Status
                badge_tags = soup.find_all("span", class_="badge")
                status = ""
                for tag in badge_tags:
                    if "badge-lang" not in tag.get("class", []):
                        status = tag.text.strip().lower()
                        break

                data.append({
                    "url": row["url"],
                    "title": title,
                    "publication_date": pub_date,
                    "authors": authors,
                    "status": status,
                })

            except Exception as e:
                print(f"[ERROR] Failed to parse {row['url']}: {e}")

            bar.next()

    print(f"✅ Extracted metadata for {len(data)} articles")
    return DataFrame(data)


@click.command()
@click.option(
    "-o", "--output", "outputFP",
    help="Path to output SQLite3 database",
    required=False,
    type=click.Path(
        exists=False,
        file_okay=True,
        writable=True,
        resolve_path=True,
        path_type=Path,
    ),
    default=Path("./jose.db"),
)
def main(outputFP: Path) -> None:
    db: DB = DB(fp=outputFP)
    db.create_tables()

    listing_pages_df = download_listing_pages()
    db.df2table(df=listing_pages_df, table="front_matter")

    article_urls = get_all_article_urls()
    article_pages_df = download_article_pages(article_urls)
    metadf = extract_metadata(article_pages_df)
    db.df2table(df=metadf, table="metadata")


if __name__ == "__main__":
    main()
