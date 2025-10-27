from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import pandas as pd

BASE = "https://www.icmc.usp.br"
START_URL = f"{BASE}/pesquisa/grupos"

headers = {
    "User-Agent": "Mozilla/5.0",
}

def get_soup(url):
    r = requests.get(url, headers=headers)
    return BeautifulSoup(r.text, "html.parser")

def get_group_links(soup):
    links = []
    for a in soup.select('a[href*="/pesquisa/grupos/?lab="]'):
        href = a.get("href")
        text = (a.get_text() or "").strip()
        if href and text:
            full = urljoin(BASE, href)
            links.append((text, full))

    unique = []
    for name, url in links:
        unique.append((name, url))

    return list(set(unique))

def get_members(group_url):
    soup = get_soup(group_url)

    h = soup.find(["h1", "h2"])
    group_name = h.get_text(strip=True)

    rows = []
    for a in soup.select('a[href*="/pessoas?id="]'):
        text = (a.get_text() or "").strip()

        if text:
            nome_limpo = text.split('Prof', 1)[0]
            rows.append({
                "grupo": group_name,
                "professor": nome_limpo
            })
    return rows

def main():
    start = get_soup(START_URL)
    group_links = get_group_links(start)

    all_rows = []
    for idx, (name_guess, url) in enumerate(group_links, 1):
        rows = get_members(url)

        all_rows.extend(rows)

        print(f"[{idx}/{len(group_links)}] {name_guess}: {len(rows)} integrantes")

    df = pd.DataFrame(
        all_rows,
        columns=["grupo", "professor"]
    )

    df = df.sort_values(["grupo", "professor"], na_position="last").reset_index(drop=True)

    df.to_csv("icmc_grupos_professores.csv", index=False)

    return df

if __name__ == "__main__":
    df = main()
