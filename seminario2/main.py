import os

import time
import pandas as pd
import signal
import dill
from utils import get_driver,recover_backup
from selenium.webdriver.common.by import By

DOCENTES_PATH = 'data/docentes.csv'
DATA_PATH = 'data/professores.pkl' ## salva o backup

df = pd.read_csv(DOCENTES_PATH)
print("Colunas df: ",df.columns)

driver = get_driver()

print("[Driver iniciado]")
time.sleep(2)


professores = recover_backup(DATA_PATH) ## relaciona cada professor como nome:(listaartigos,listapesquisa)
                                        # artigo = str,  pesquisa = namedtuple Pesquisa
                                        
## Caso você dê ctrl+c, ele tb salva
def on_ctrl_c(sig, frame):
    ## quando vc dá ctrl+C pra sair, ele roda e salva o bglh de professores
    print("Arquivo de professores salvo após ctrl+c")
    print("professores: ",professores)
    with open(DATA_PATH, "wb") as f:
        dill.dump(professores, f)
    print("Salvo com sucesso")
    exit(0)

# Registra a função para o sinal SIGINT
signal.signal(signal.SIGINT, on_ctrl_c)




## Itera sobre o dataset de professores
for i,(idx,(nusp,nome,link,pagina,link_lattes)) in enumerate(df.iterrows()):    
    ## Verifica se já não foi cadastrado
    if nome in professores.keys():
        continue ## já foi cadastrado, então pula
    
    
    link_lattes = 'http://lattes.cnpq.br/5947294509160397'
    driver.get(link_lattes)
    input("Aperte enter quanado terminar de passar pelo captcha")
    print(f"{nome} ",'-'*30)
    
    
    maindiv = driver.find_elements(By.CLASS_NAME,'title-wrapper') ## lista de todos os elementos
    div2corename = {}
    for div in maindiv:
        try:
            h1 = div.find_element(By.TAG_NAME,'h1')
            div2corename[h1.text] = div
        except:
            pass
    
    pesquisas = [] ## lista de pesquisas
    if 'Projetos de pesquisa' not in div2corename.keys(): ## caso o prof não tenha cadastrado como produções
        print(" "*4,"Campo de projetos de pesquisa não encontrado!!")
    else:
        pesquisasdiv = div2corename['Projetos de pesquisa']
        pesquisasdiv = pesquisasdiv.find_elements(By.XPATH, "./*")[-2] ## vai até o penúltimo filho
        pesquisasdiv = pesquisasdiv.find_elements(By.XPATH, "./*") ## pega todos os filhos dessa div
        
        ## itera sobre as várias pesquisas enquanto guarda as informações
        pesquisa_nome = None ## variavel auxiliar pra guardar o nome da pesquisa
        pesquisa_data = None
        pesquisa_descricao = None
        step = 0 ## variável auxiliar que marca a etapa 
        
        
        for element in pesquisasdiv:
            step+=1 ## adiciona a step
            class_name = element.tag_name ## pega a tagname
            
            if class_name == 'a':
                if pesquisa_nome is not None:
                    ## cadastra a pesquisa
                    pesquisas.append(Pesquisa(pesquisa_nome,pesquisa_data,pesquisa_descricao))
                step = 0 ## reinicia a step
            
            if step == 1: ## guarda a data
                pesquisa_data = element.find_element(By.XPATH,"./*").text ## pega o texto do primeiro filho
                
            if step == 2: ## bglh que guarda o nome da pesquisa
                pesquisa_nome = element.find_element(By.XPATH,"./*").text ## pega o texto do primeiro filho
            
            if step == 4: ## bglh que tem a descrição
                pesquisa_descricao = element.find_element(By.XPATH,"./*").text ## pega o texto do primeiro filho
                
        print(" "*4,f"{len(pesquisas)} pesquisas encontradas")
    artigos_txts = []
    if 'Produções' not in div2corename.keys():
        print(" "*4,"Campo de produções não cadastrado")
    else:
        ## Etapa de pegar somente os artigos completos
        artigosdiv = driver.find_element(By.ID,'artigos-completos') ## lista o div que guarda os artigos completos
        artigos = artigosdiv.find_elements(By.CLASS_NAME, "artigo-completo") ## todos os artigos completos
        
        for element in artigos:
            artigo_text = element.find_element(By.CLASS_NAME,'transform').text
            artigos_txts.append(artigo_text)
        print(" "*4,f"{len(artigos)} artigos encontrados")
    
    
    professores[nome] = (artigos_txts,pesquisas)
    
## salva o arquivo de professores
with open(DATA_PATH, "wb") as f:
    dill.dump(professores, f)

print("[Encerrando...]")
driver.quit()
print("[Programa finalizado]")


## Considerações:
## - tirar o break do loop de matérias
## - tirar a trava de quantidade de downloads



