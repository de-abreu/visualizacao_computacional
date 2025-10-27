from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.manifold import TSNE
import plotly.express as px

DATABASE_PATH = f"{Path().resolve()}/database/lattes.db"
ENGINE = create_engine(f"sqlite:///{DATABASE_PATH}")

# Carregando os Dados
def load_articles(engine = ENGINE):
    """Lê professores e artigos do banco de dados."""
    query = """
        SELECT 
            r.name  AS professor, 
            a.title AS article
        FROM authorship au
        JOIN articles    a ON au.article_id = a.id
        JOIN researchers r ON au.author_id  = r.lattes_id
    """
    df = pd.read_sql_query(query, engine)

    arts = (
        df.groupby("professor", as_index=False)["article"]
        .agg(list)
    )

    return arts

def load_groups(path="webcrawlers/icmc_grupos_professores.csv"):
    '''Carrega arquivo de grupos de pesquisa dos professores. Obtido fazendo webscrapping do site do icmc
    usando o código "extracao_grupos_prof.py".'''
    groups = pd.read_csv(path)
    groups = groups.rename(columns={c: c.strip().lower() for c in groups.columns})
    return groups

def load_macros_faltantes(path = "webcrawlers/professores_sem_grupo.txt"):
    '''Alguns professores não tinham grupos de pesquisa no site do icmc e também não achamos de maneira
    simples em outras fontes, então coletamos manualmente pelo menos os dados das macro áreas de cada um
    (tendo como base o site do icmc). Juntamos isso em um arquivo nomeado professores_sem_grupo.txt.'''
    macros = {}

    f = open(path, "r")
    for line in f:
        parts = [p.strip() for p in line.strip().split(",") if p.strip()]
        if not parts:
            continue
        macros[parts[0]] = parts[1:]

    return macros

# 
def prepare_articles(df, groups):
    """Explode artigos."""

    arts = (
        df[["professor", "article"]]
        .explode("article")
        .reset_index(drop=True)
    )

    print(f"Artigos: {len(arts)} | Professores: {len(set(arts['professor']))}")
    return arts

# Gerando embeddings
def embeddings(arts, groups, macros):
    """Gera embeddings para artigos e grupos (Alguns professores estão em mais de 1 grupo, então
    usamos similaridade de cosseno com as embeddings para decidir nesses casos)."""
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    emb_articles = model.encode(arts["article"].tolist(), normalize_embeddings=True, show_progress_bar=True)

    all_groups = list(set(groups["grupo"].tolist()))
    embeddings_groups = model.encode(all_groups, normalize_embeddings=True, show_progress_bar=False)
    emb_groups = {group: emb for group, emb in zip(all_groups, embeddings_groups)}

    all_macros = list(set(m for ms in macros.values() for m in ms))
    embeddings_macros = model.encode(all_macros, normalize_embeddings=True, show_progress_bar=False)
    emb_macros = {macro: emb for macro, emb in zip(all_macros, embeddings_macros)}

    return emb_articles, emb_groups, emb_macros

# Ligando grupos de pesquisa aos artigos através dos professores
def get_groups(arts, emb_articles, groups, emb_groups):
    """Associa cada artigo ao grupo mais similar do professor (Alguns professores estão em mais de
    1 grupo, então usamos similaridade de cosseno com as embeddings para decidir nesses casos)."""
    prof_groups = (
        groups.groupby("professor")["grupo"]
              .apply(lambda s: sorted(set(s.tolist())))
              .to_dict()
    )

    best_group = []
    for i, row in arts.iterrows():
        possible_groups = prof_groups.get(row["professor"], [])

        if not possible_groups:
            best_group.append("Sem grupo de pesquisa")
            continue
        
        emb = []
        for group in possible_groups:
            emb.append(emb_groups[group])

        sims = cosine_similarity(emb_articles[i].reshape(1, -1), emb)[0]
        best_group.append(possible_groups[np.argmax(sims)])

    arts["grupo"] = best_group
    return arts

# Reduzindo Dimensionalidade usando t-SNE
def dim_reduction(embeddings):
    """Reduz embeddings para 2D via t-SNE."""
    tsne = TSNE(n_components=2, metric="cosine", random_state=42)
    return tsne.fit_transform(embeddings)

# Mapeando Macro Áreas
def map_macro(arts, emb_articles, macros_faltantes, emb_macros):
    """
    Adiciona as macro áreas dos artigos. Definido de acordo com o site do icmc.
    """
    macro_groups = {
        "Computação": [
            "Bases de Dados e Imagens",
            "Computação Aplicada à Educação",
            "Engenharia de Software e Sistemas de Informação",
            "Inteligência Artificial (Aprendizado de Máquina e Mineração de Dados)",
            "Inteligência Artificial (Computação Bioinspirada)",
            "Inteligência Artificial (Linguística Computacional)",
            "Jogos Digitais",
            "Redes Inteligentes",
            "Robotica Móvel",
            "Sistemas Distribuídos e Programação Concorrente",
            "Sistemas Embarcados e Evolutivos",
            "Sistemas Web e Multimídia Interativos",
            "Visualização, Imagens e Computação Gráfica",
        ],
        "Estatística": [
            "Ciência de Dados e Estatística",
            "Estatística",
            "Modelagem de Risco",
            "Modelos de Variáveis Latentes",
        ],
        "Matemática": [
            "Álgebra e Geometria Algébrica",
            "Ánálise Funcional Aplicada",
            "Educação Matemática",
            "Equações Diferenciais Parciais Lineares",
            "Equações Diferenciais, Sistemas Dinâmicos e Integração Não Absoluta",
            "Geometria Diferencial",
            "Singularidades",
            "Sistemas Dinâmicos e Teoria Ergódica",
            "Sistemas Dinâmicos Não Lineares",
            "Topologia",
        ],
        "Matemática Aplicada": [
            "Ánálise Aplicada e Geométrica",
            "Mecânica dos Fluidos Computacional",
            "Otimização",
            "Processamento Visual e Geométrico",
            "Sistemas Complexos, Partículas e Controle",
        ],
    }

    # Mapeande o macro com o grupo de pesquisa
    subgroup_macro = {}
    for macro, sublist in macro_groups.items():
        for g in sublist:
            subgroup_macro[g] = macro

    arts["macro"] = arts["grupo"].map(subgroup_macro)

    # Mapeando o macro com os professores sem grupo de pesquisa (alguns deles tem 2 macros)
    mask_sem = arts["grupo"].fillna("").str.startswith("Sem grupo")

    for row in np.where(mask_sem.values)[0]:
        prof = arts.at[row, "professor"]
        possible_macros = macros_faltantes.get(prof, [])
        if not possible_macros:
            arts.at[row, "macro"] = "Sem macro definido"
            continue
        if len(possible_macros) == 1:
            arts.at[row, "macro"] = possible_macros[0]
        else:
            emb = []
            for macro in possible_macros:
                emb.append(emb_macros[macro])

            sims = cosine_similarity(emb_articles[row].reshape(1, -1), emb)[0]
            arts.at[row, "macro"] = possible_macros[np.argmax(sims)]

    # Mapeando quem não foi mapeado (idealmente ninguém deve ficar sem macro)
    arts["macro"] = arts["macro"].fillna("Sem macro definido")
    
    return arts

# Cria as bolhas do Bubble Plot
def create_bubble(arts):
    '''Separa os pontos de cada grupo de pesquisa por 'macro' e 'grupo' e adiciona as médias
    das posições e quantidade de pontos do grupo'''
    bubbles = (
        arts.groupby(["macro", "grupo"], as_index=False)
            .agg(x=("x", "mean"), y=("y", "mean"), n=("article", "size"))
    )
    return bubbles

# Plotagem
def plotting_bubbles(bubbles):
    """Gera visualização interativa."""
    fig = px.scatter(
        bubbles, x="x", y="y", color="macro", size="n", size_max=30,
        text="grupo", hover_name="grupo",
        hover_data={"macro": True, "n": True, "x": False, "y": False, "grupo": False},
        title="Centroides por Grupo de Pesquisa, com tamanho proporcional ao número de artigos",
        labels={
        "n": "Número de Artigos",
        "macro": "Macro área",
        },
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(width=1000, height=700, legend_title_text="Macro área")
    fig.show()