import requests
from bs4 import BeautifulSoup
import urllib
import os
import json
import time
import random

SAVE_DIR = "C:/Users/maxch/Downloads/"
os.makedirs(SAVE_DIR, exist_ok=True)

all_rows = [
    "あ", "い", "う", "え", "お",
    "か", "き", "く", "け", "こ",
    "さ", "し", "す", "せ", "そ",
    "た", "ち", "つ", "て", "と",
    "な", "に", "ぬ", "ね", "の",
    "は", "ひ", "ふ", "へ", "ほ",
    "ま", "み", "む", "め", "も",
    "や", "ゆ", "よ",
    "ら", "り", "る", "れ", "ろ",
    "わ", "を", "ん",
    "が", "ぎ", "ぐ", "げ", "ご",
    "ざ", "じ", "ず", "ぜ", "ぞ",
    "だ", "ぢ", "づ", "で", "ど",
    "ば", "び", "ぶ", "べ", "ぼ",
    "ぱ", "ぴ", "ぷ", "ぺ", "ぽ"
]

def get_words_from_page(row_hiragana: str, page_num: int = 1):
    encoded_row = urllib.parse.quote(row_hiragana)
    url = f"https://dictionary.goo.ne.jp/jn/index/{encoded_row}/{page_num}/"
    print(f"Scraping: {url}")
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")

    word_links = []
    for a in soup.select("ul.content_list li > a"):
        href = a.get("href")
        title_tag = a.select_one("p.title")
        title = title_tag.text.strip() if title_tag else None
        if title and href:
            full_url = urllib.parse.urljoin("https://dictionary.goo.ne.jp", href)
            word_links.append({
                "word": title,
                "url": full_url
            })
    return word_links

def collect_all_word_links(start_row=None, start_page=1):
    skip = True if start_row else False

    for row in all_rows:
        if skip:
            if row == start_row:
                skip = False
            else:
                continue  # Skip until we reach the start_row

        file_path = os.path.join(SAVE_DIR, f"{row}.json")
        all_words = []

        # If file already exists, load it (in case resuming mid-file)
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                all_words = json.load(f)

        page = start_page if row == start_row else 1

        while True:
            word_links = get_words_from_page(row, page)
            if not word_links:
                break

            all_words.extend(word_links)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(all_words, f, ensure_ascii=False, indent=2)
            print(f"Saved page {page} for '{row}' ({len(word_links)} words)")

            time.sleep(random.uniform(0, 1))  # polite delay
            page += 1

        # Reset start_page for next row
        start_page = 1

if __name__ == "__main__":
    # Modify here to resume from a certain row and page
    collect_all_word_links(start_row="ぼ", start_page=38)