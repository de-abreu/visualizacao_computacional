'''
    Script que itera no "pessoas.php" do site do ICMC capturando alguns dados úteis do docentes, em especial o link para o Currículo Lattes.
        > Atenção: no momento de criação do código, três dos docentes não possuíam o link para o Lattes em suas páginas, dessa forma, sua coleta teve que ser manual. 

'''

import re
import csv
import time
import requests
from pathlib import Path
from bs4 import BeautifulSoup

BASE = "https://www.icmc.usp.br"
LIST_URL = f"{BASE}/templates/icmc2015/php/pessoas.php"

headers = {
    "Host": "www.icmc.usp.br",
    "Cookie": "",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": BASE,
    "Referer": f"{BASE}/pessoas/docentes",
}

id_href_re = re.compile(r"/pessoas\?id=(\d+)")

def parse_docentes(html, pagina):
    soup = BeautifulSoup(html, "html.parser")
    resultados, vistos = [], set()

    for a in soup.select(".caption a[href*='/pessoas?id=']"):
        href = a.get("href") or ""
        m = id_href_re.search(href)
        if not m:
            continue
        docente_id = m.group(1)
        if docente_id in vistos:
            continue
        vistos.add(docente_id)

        h6 = a.find("h6")
        nome = h6.get_text(strip=True) if h6 else a.get_text(strip=True)
        link = f"{BASE}/pessoas?id={docente_id}"

        resultados.append({
            "id": str(int((int(docente_id)-3)/2)), # heuristicazinha do nusp
            "nome": nome,
            "link": link,
            "pagina": pagina,
        })
    return resultados

def extrair_lattes(html):
    soup = BeautifulSoup(html, "html.parser")

    # busca classe 'lattes'
    a = soup.select_one("a.link_pessoas.lattes[href]")
    if a and a.get("href"):
        return a["href"].strip()

    # fallback: qualquer link que contenha lattes.cnpq.br
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if "lattes.cnpq.br" in href:
            return href.strip()

    return None

def baixar_lattes_para(docentes, session):
    
    for d in docentes:
        try:
            r = session.get(d["link"], headers={**headers, "X-Requested-With": None}, timeout=30)
            r.raise_for_status()
            d["lattes"] = extrair_lattes(r.text)
        except requests.RequestException as e:
            d["lattes"] = None
            print(f"[ERRO] Falha ao abrir perfil {d['link']}: {e}")
        
        time.sleep(0.1) # evitar floodar requisicao
    return docentes

def main():
    todos = []
    with requests.Session() as s:
        for pagina in range(1, 7):
            data = {"grupo": "Docente", "depto": "", "nome": "", "pagina": str(pagina)}
            resp = s.post(LIST_URL, headers=headers, data=data, timeout=30)
            resp.raise_for_status()
            extraidos = parse_docentes(resp.text, pagina)
            todos.extend(extraidos)
            print(f"[OK] Página {pagina}: {len(extraidos)} docentes")
            time.sleep(0.4)

        # pega lattes
        print(f"\n[INFO] Visitando {len(todos)} perfis para extrair Lattes...")
        baixar_lattes_para(todos, s)

    out_path = Path("data/docentes.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "nome", "link", "pagina", "lattes"])
        w.writeheader()
        w.writerows(todos)

    com_lattes = sum(1 for d in todos if d.get("lattes"))
    print(f"\nTotal: {len(todos)} | Com Lattes: {com_lattes} | Sem Lattes: {len(todos) - com_lattes}")
    for d in todos:
        print(f"{d['id']}\t{d['nome']}\t{d['link']}\t{d.get('lattes') or ''}")

if __name__ == "__main__":
    main()
