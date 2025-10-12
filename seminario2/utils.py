from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from collections import namedtuple
import os
import dill

Pesquisa = namedtuple('Pesquisa',['nome','data','descricao'])

def get_driver():
    chrome_options = Options()
    chrome_options.add_experimental_option('prefs', {
        # "download.default_directory": os.path.abspath(DOWNLOAD_DIR),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True  # Impede que o Chrome abra PDFs no navegador
    })
    # chrome_options.add_argument("--headless")  # Modo invisível (opcional)
    chrome_options.add_argument("--no-sandbox")  # Necessário para executar como root
    chrome_options.add_argument("--disable-dev-shm-usage")  # Evita problemas de memória

    # Configurar o serviço do ChromeDriver
    service = Service(ChromeDriverManager().install())
    print("[Service iniciado]")
    
    
    # Iniciar o WebDriver com as opções
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def recover_backup(data_path:str):
    data = {}
    if not os.path.exists(data_path):
        print("Arquivo de backup não encontrado. Criando novo...")
        with open(data_path, "wb") as f:
            dill.dump(data, f) ## inicia vazio
    
    # Carrega o conteúdo
    with open(data_path, "rb") as f:
        data = dill.load(f)
    return data