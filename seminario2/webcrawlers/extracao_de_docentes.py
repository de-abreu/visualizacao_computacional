'''
    Script que itera no "pessoas.php" do site do ICMC capturando alguns dados úteis dos docentes, em especial o link para o Currículo Lattes.
        > Atenção: no momento de criação do código, três dos docentes não possuíam o link para o Lattes em suas páginas, dessa forma, sua coleta teve que ser manual. 

'''

import re
import csv
import time
import requests
from tqdm import tqdm
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


def _extrair_id(href):
    partes = href.split("id=")
    return partes[1]

def parse_docentes(html, pagina):
    soup = BeautifulSoup(html, "html.parser")
    resultados, vistos = [], set()

    # continua usando seletor CSS (sem regex)
    for a in soup.select(".caption a[href]"):
        href = a.get("href") or ""
        if "/pessoas?id=" not in href:
            continue

        docente_id = _extrair_id(href)
        if not docente_id:
            continue
        if docente_id in vistos:
            continue
        vistos.add(docente_id)

        # os nomes aparecem dentro de cabeçalhos "h6"
        h6 = a.find("h6")
        nome = h6.get_text(strip=True) if h6 else a.get_text(strip=True)

        link = href if href.startswith("http") else f"{BASE}{href}"

        resultados.append({
            "id": str(int((int(docente_id)-3)/2)),  # heuristicazinha do nusp
            "nome": nome,
            "link": link,
            "pagina": pagina,
        })
    return resultados

def extrair_lattes(html):
    soup = BeautifulSoup(html, "html.parser")

    #global contador
    #contador += 1
    #print(f"Entrei no perfil {contador}")

    # busca classe 'lattes'
    a = soup.select_one("a.link_pessoas.lattes[href]")
    if a and a.get("href"):
        return a["href"].strip()

    #print(f"NÃO ACHEI -> {contador}")
    return None

def baixar_lattes(docentes, session):
    found = 0
    with tqdm(total=len(docentes), desc="Perfis", unit="perfil") as pbar: # barra de progresso bonitinha :)
        for d in docentes:
            r = session.get(d["link"], headers={**headers, "X-Requested-With": None}, timeout=30)
            d["lattes"] = extrair_lattes(r.text)
            if d["lattes"]:
                found += 1
            pbar.set_postfix(lattes=found)
            pbar.update(1)
            time.sleep(0.1)
    return docentes

def main():
    todos = []
    with requests.Session() as s:

        # loop inicial pegando as infos básicas
        for pagina in range(1, 7):
            data = {"grupo": "Docente", "depto": "", "nome": "", "pagina": str(pagina)}
            resp = s.post(LIST_URL, headers=headers, data=data, timeout=30)
            extraidos = parse_docentes(resp.text, pagina)
            todos.extend(extraidos)
            print(f"{pagina}ª Página: {len(extraidos)} docentes")
            time.sleep(0.3)

        # entra no perfil de cada um e pega o lattes
        # inclusive, essa é a etapa que mais demora, além de ser suscetível a problemas de trafego
        # em caso de erro, aguardar e rodar novamente
        print(f"\nIniciando tentativa de extração dos {len(todos)} Lattes! (Essa fase demora um pouco)")
        baixar_lattes(todos, s)

    out_path = Path("docentes.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    #                                   definir o encoding pra não quebrar os acentos
    with out_path.open("w", newline="", encoding="UTF-8") as f: 
        w = csv.DictWriter(f, fieldnames=["id", "nome", "link", "pagina", "lattes"])
        w.writeheader()
        w.writerows(todos)

    com_lattes = sum(1 for d in todos if d.get("lattes"))
    print(f"\nTotal: {len(todos)} | Com Lattes: {com_lattes} | Sem Lattes: {len(todos) - com_lattes}")

if __name__ == "__main__":
    main()
