import requests
from bs4 import BeautifulSoup   

def scrape_goo_meaning(word):
    url = f"https://dictionary.goo.ne.jp/word/{word}/"
    #url = f"https://dictionary.goo.ne.jp/word/kanji/{word}/"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")

    # Extract the word title
    '''
    title_tag = soup.select_one("div.basic_title")
    title = title_tag.get_text(strip=True) if title_tag else "N/A"
    '''
    # title and pronunciation
    div_title = soup.find("div", class_="basic_title nolink l-pgTitle")   
    pronunciation = ""  
    if div_title:
        h1 = div_title.find("h1")   
        if h1:
            word = ''.join(t for t in h1.contents if isinstance(t, str)).strip()        
            yomi_span = h1.find("span", class_="yomi")
            pronunciation = yomi_span.get_text(strip=True) if yomi_span else ""
            pronunciation = pronunciation[1:-1]
        
    print("Word:", word)    

    content_title = None
    section = soup.find("div", class_='section cx') 
    if not section:
        print("No section found for kanji.")
        return      

    # Seperate kanji and word
    if ("kanji" in url):
        try:
            sub_title_h2 = section.find("h2", class_='nolink title nobold paddding')
            sub_title = sub_title_h2.get_text(strip=True) if sub_title_h2 else "N/A"
            content_title = sub_title
            pronunciation = sub_title.split("【")[0]
        except:
            print("No sub title found for kanji.")
    else:
        try:
            sub_title_h2 = section.find("h2", class_='nolink title paddding')
            sub_title = sub_title_h2.get_text(strip=True) if sub_title_h2 else "N/A"
            content_title = sub_title.split("の解説")[0]
        except:
            print("No sub title found for word.")
    
    print("Pronunciation:", pronunciation)
    print("Content Title:", content_title)


    # 3. Extract grammatical info and readings inside <div class="text">
    content_wrap = None
    content_wrap = section.find("div", class_='content-box contents_area meaning_area p10')
    if not content_wrap:
        print("No content wrap found for kanji.")
        return
    contents = content_wrap.find('div', class_='contents')

    grammatical_info = ''
    if contents:
        text_div = contents.find('div', class_='text')
        if text_div:
            grammatical_info = text_div.get_text(" ", strip=True)

    print("Grammatical Info + Reading Variants:", grammatical_info)

    # 4. Extract explanations
    # Case 1: multiple explanations inside <ol class="meaning cx">
    explanation_list_items = contents.find_all('ol', class_='meaning cx')

    if explanation_list_items:
        explanations = []
        for ol in explanation_list_items:
            li = ol.find('li')
            if li:
                text_p = li.find('p', class_='text')
                if text_p:
                    explanations.append(text_p.get_text(" ", strip=True))
        # Join all explanations
        explanation_text = "\n".join(explanations)
    else:
        # Case 2: single explanation inside <p class="text"> (no <ol>)
        p_single = contents.find('p', class_='text')
        explanation_text = p_single.get_text(strip=True) if p_single else ''

    print("Explanations:")
    print(explanation_text)

scrape_goo_meaning("IMO_%28International+Meteorological+Organization%29/#jn-564")
#scrape_goo_meaning("亜")

