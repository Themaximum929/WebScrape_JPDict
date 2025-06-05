import os
import json
import requests
import time
import random
from bs4 import BeautifulSoup

BASE_DIR = "C:/Users/maxch/Downloads"
LINKS_DIR = BASE_DIR
SAVE_DIR = os.path.join(BASE_DIR, "meanings")
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

def scrape_goo_meaning(url):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.content, "html.parser")

        # Word and pronunciation
        div_title = soup.find("div", class_="basic_title nolink l-pgTitle")
        word = ""
        pronunciation = ""
        if div_title:
            h1 = div_title.find("h1")
            if h1:
                word = ''.join(t for t in h1.contents if isinstance(t, str)).strip()
                yomi_span = h1.find("span", class_="yomi")
                if yomi_span:
                    pronunciation = yomi_span.get_text(strip=True)[1:-1]  # Remove 「」

        # Section wrapper
        section = soup.find("div", class_='section cx')
        if not section:
            return {
                "word": word,
                "pronunciation": pronunciation,
                "content_title": "",
                "verb_type": "",
                "meanings": []
            }

        # Determine if it's a kanji or word page
        content_title = ""
        if "/kanji/" in url:
            sub_title_h2 = section.find("h2", class_='nolink title nobold paddding')
            if sub_title_h2:
                sub_title = sub_title_h2.get_text(strip=True)
                content_title = sub_title
                pronunciation = sub_title.split("【")[0]
        else:
            sub_title_h2 = section.find("h2", class_='nolink title paddding')
            if sub_title_h2:
                sub_title = sub_title_h2.get_text(strip=True)
                content_title = sub_title.split("の解説")[0]

        # Grammatical info and contents
        content_wrap = section.find('div', class_='content-box contents_area meaning_area p10')
        contents = content_wrap.find('div', class_='contents') if content_wrap else None

        verb_type = ""
        if contents:
            text_div = contents.find('div', class_='text')
            if text_div:
                verb_type = text_div.get_text(" ", strip=True)

        # Extract meanings
        meanings = []
        if contents:
            explanation_list_items = contents.find_all('ol', class_='meaning cx')
            if explanation_list_items:
                for ol in explanation_list_items:
                    li = ol.find('li')
                    if li:
                        text_p = li.find('p', class_='text')
                        if text_p:
                            meanings.append(text_p.get_text(" ", strip=True))
            else:
                # fallback
                p_single = contents.find('p', class_='text')
                if p_single:
                    meanings.append(p_single.get_text(strip=True))

        return {
            "word": word,
            "pronunciation": pronunciation,
            "content_title": content_title,
            "verb_type": verb_type,
            "meanings": meanings
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {
            "word": "Error",
            "pronunciation": "",
            "content_title": "",
            "verb_type": "",
            "meanings": []
        }

def is_empty_entry(entry):
    return (
        not entry["word"]
        and not entry["pronunciation"]
        and not entry["content_title"]
        and not entry["verb_type"]
        and not entry["meanings"]
    )

def scrape_all_meanings(start_row=None, start_index=0, start_url=None):
    skip_row = True if start_row else False

    for row in all_rows:
        if skip_row:
            if row == start_row:
                skip_row = False
            else:
                continue

        input_path = os.path.join(LINKS_DIR, f"{row}.json")
        output_path = os.path.join(SAVE_DIR, f"{row}.json")

        if not os.path.exists(input_path):
            print(f"Missing link file for '{row}', skipping...")
            continue

        with open(input_path, "r", encoding="utf-8") as f:
            word_links = json.load(f)

        existing_results = []
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                existing_results = json.load(f)

        print(f"\nProcessing '{row}' ({len(word_links)} words)...")

        # Determine starting index if URL is specified
        start_i = 0
        if row == start_row:
            if start_url:
                for idx, entry in enumerate(word_links):
                    if entry["url"] == start_url:
                        start_i = idx
                        break
                else:
                    print(f"URL {start_url} not found in {row}.json. Aborting.")
                    return
            else:
                start_i = start_index

        for i in range(start_i, len(word_links)):
            entry = word_links[i]

            if i < len(existing_results):
                existing_entry = existing_results[i]
                if not is_empty_entry(existing_entry):
                    continue  # Already scraped and valid
                else:
                    print(f"[{row}] Replacing empty record at index {i + 1}: {entry['word']}")
            else:
                print(f"[{row}] Scraping {i + 1}/{len(word_links)}: {entry['word']}")

            meaning_data = scrape_goo_meaning(entry["url"])

            if is_empty_entry(meaning_data):
                print(f"Empty result detected. Possible IP block. Terminating scraping at [{row}] index {i}.")
                return

            result_entry = {
                "original_word": entry["word"],
                "url": entry["url"],
                "word": meaning_data["word"],
                "pronunciation": meaning_data["pronunciation"],
                "content_title": meaning_data["content_title"],
                "verb_type": meaning_data["verb_type"],
                "meanings": meaning_data["meanings"]
            }

            if i < len(existing_results):
                existing_results[i] = result_entry
            else:
                existing_results.append(result_entry)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(existing_results, f, ensure_ascii=False, indent=2)

            #time.sleep(random.uniform(0, 0.3))

        start_index = 0  # Reset for next row

if __name__ == "__main__":
    scrape_all_meanings(start_row="あ", start_index=1848)
    #scrape_all_meanings(start_row="あ", start_url="https://dictionary.goo.ne.jp/word/IMO_%28International+Meteorological+Organization%29/#jn-564")
