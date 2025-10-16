from utils import recover_backup

DATA_PATH = 'data/professores_all.pkl' ## salva o backup

professores = recover_backup(DATA_PATH) ## relaciona cada professor como nome:(listaartigos,listapesquisa)
                                        # artigo = str,  pesquisa = namedtuple Pesquisa
                                        
for i,(name,(artigos,pesquisas)) in enumerate(professores.items()):
    print(f"{i:3} {name} ",'-'*(80-len(name)))
    print(" "*6,f"{len(artigos)} artigos encontrados.")
    print(" "*6,f"{len(pesquisas)} pesquisas encontradas. ")
    print("\n")
    