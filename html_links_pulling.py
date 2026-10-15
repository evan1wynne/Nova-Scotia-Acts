from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import json
import unicodedata

BASE_URL = "https://nslegislature.ca"
ACTS_URL = r"https://nslegislature.ca/legislative-business/bills-statutes/consolidated-public-statutes"
response = requests.get(ACTS_URL)
response.encoding = "utf-8"

soup = BeautifulSoup(response.text, 'html.parser')

anchor_list = soup.find('ul', class_='anchor-list')

if not anchor_list:
    raise KeyError("Could not find anchor list, check the url")

catalog = {}

for li in anchor_list.find_all('li'):

    html_anchor = li.find("a", href=lambda h: h and ('htm' in h.lower() or 'html' in h.lower()))
    if not html_anchor:
        continue

    clean_li = li.__copy__()
    anchors = clean_li.find_all('a')
    for a in anchors:
        a.extract()

    act_title = clean_li.get_text(strip=True)
    clean_act_title = None

    # Only ones that aren't Acts
    for candidate, canonical in {
        "Halifax Regional Municipality Charter": "Halifax Regional Municipality Charter",
        "Labour Standards Code": "Labour Standards Code",
        "Statute of Frauds": "Statute of Frauds",
    }.items():
        if candidate in act_title:
            clean_act_title = canonical
            break

    if clean_act_title is None:
        act_index = act_title.find("Act")
        if act_index != -1:
            clean_act_title = act_title[:act_index + 3]
        else:
            for a in li.find_all("a"):
                clean_act_title = a.get_text(strip=True)
                if clean_act_title:
                    break
            else:
                clean_act_title = act_title

    if clean_act_title == "Achd Fonndas Colaisde na G\u00e0idhlig (Gaelic College Foundation Act":
        clean_act_title = "Achd Fonndas Colaisde na G\u00e0idhlig (Gaelic College Foundation Act)"

    relative_path = html_anchor['href']
    full_html_url = urljoin(BASE_URL, relative_path)
    full_html_url = full_html_url.replace(" ", "%20")

    catalog[clean_act_title] = full_html_url

with open("./acts-urls.json", "w") as f:    
    json.dump(catalog, f, indent=2)




