# Seminário 2: Geração e exploração de um banco de dados acerca dos pesquisadores do ICMC-USP

## Autores

| Nome                                      | nUSP     |
| :---------------------------------------- | :------- |
| Lucas de Oliveira Ferreira                | 13695042 |
| Guilherme de Abreu Barreto                | 12543033 |
| Jhonathan Oliveira Alves                  | 11838116 |
| Lucas Pereira Franco de Almeida           | 12675020 |
| Miguel Prates Ferreira de Lima Cantanhede | 13672745 |

## Sumário

<!--toc:start-->

- [Resumo](#resumo)
- [Introdução](#introdução)
- [Ambiente de desenvolvimento](#ambiente-de-desenvolvimento)
  - [Carregamento dos dados](#carregamento-dos-dados)
  - [Instalação de dependências](#instalação-de-dependências)
    - [Usando DevEnv](#usando-devenv)
    - [Usando `pip`](#usando-pip)
- [Webcrawlers](#webcrawlers)
- [Modelagem do Banco de Dados](#modelagem-do-banco-de-dados)
- [Visualizações](#visualizações)
  - [Diagrama de Arcos](#diagrama-de-arcos)
    - [Premissa](#premissa)
    - [Pré-processamento dos dados](#pré-processamento-dos-dados)
    - [Funcionalidades](#funcionalidades)
  - [Gráfico de Dispersão](#gráfico-de-dispersão)
  - [Gráfico de linhas](#gráfico-de-linhas)
- [Conclusões](#conclusões)
<!--toc:end-->

## Resumo

No presente trabalho, realizamos um estudo de caso onde, a partir de um
levantamento acerca dos pesquisadores do Instituto de Ciências Matemáticas e de
Computação da Universidade de São Paulo (ICMC-USP), avaliamos a produção destes
em termos (1.) do número de vezes em que estes colaboraram entre si; (2.) das
áreas do conhecimento e especializações abarcadas; (3.) e dos resultados
apresentatos em função do tempo. Para tal, empregamos e descrevemos técnicas
pelas quais pode ser feita a coleta, modelagem e finalmente a visualização
interativa de dados de maneira a favorável a análise dos mesmos.

**Palavras-chave:** _webscrapping_, banco de dados relacional, dashboards,
visualização de dados.

## Introdução

Conforme a proposta de seminário apresentada em enunciado, buscamos realizar um
levantamento de dados pertinentes a vivência universitária no ICMC. Em
particular, focamo-nos na exploração dos dados oferecidos pela plataforma
[Currículo Lattes](https://lattes.cnpq.br/), acerca da produção científica do
atual corpo docente deste instituto, conforme consta no
[site](https://icmc.usp.br/pessoas) deste. Pretendeu-se, ao final, responder as
seguintes perguntas:

1. Quais projetos de pesquisa ou artigos científicos foram resultados da
   colaboração entre os pesquisadores do ICMC e,

   - quais os professores mais colaborativos?
   - com quem estes colaboram?
   - quantas vezes estes já colaboraram?

2. Quais as áreas do conhecimento e especialidades abarcadas pelas pesquisas
   conduzidas no ICMC e,

   - quais os principais temas no geral?
   - quais os principais temas para cada grupo de pesquisa?

3. Qual a produtividade dos docentes em função do tempo e,

   - como esta se compara aos demais docentes deste mesmo instituto?

Para responder a estas perguntas realizamos uma pesquisa que consistiu em três
etapas: (1.) levantamento dos dados dos pesquisadores, (2.) estruturação dos
dados coletados em um banco de dados local, (3.) geração de visualizações
congruentes com os objetivos da análise. Neste relatório, descrevemos

- no tópico "Ambiente de desenvolvimento" destacamos as aplicações e bilbiotecas
  as quais utilizamos em nossa pesquisa, assim como obtê-las e executá-las;

- no tópico "_Webcrawler_" os programas que desenvolvemos tendo em vista a
  coleta (parcialmente) automatizada dos dados dos pesquisadores nos sites do
  instituto e da Plataforma Lattes;

- no tópico "Modelagem do Banco de Dados" a construção de um banco de dados
  relacional para o armazenamento estruturado destes dados;

- no tópico "Visualizações" a elaboração de _dashboards_ pelos quais realizamos
  a exibição destes dados em forma conveniente para responder aos nossos
  problemas de pesquisa;

Ao término de nossa pesquisa encontramos notável presença de colaboração entre
os docentes deste instituto, e alguns agrupamentos entre aqueles mais
colaborativos.

> [!WARNING]
>
> Adicionar conclusões do Lucas e Bom Dia

## Ambiente de desenvolvimento

Para gerar localmente as visualizações descritas neste relatório em um notebook
jupyter, ou mesmo modificar este projeto tendo acesso as mesmas ferramentas das
quais fizemos uso, faz-se necessário o carregamento de seus dados e a reprodução
do ambiente de desenvolvimento.

### Carregamento dos dados

Todos os dados e programas gerados nesta pesquisa encontram-se armazenados em um
[repositório git](https://github.com/de-abreu/visualizacao_computacional.git).
Recomenda-se que a obtenção destes seja feita diretamente pelo uso da ferramenta
git:

```bash
git clone https://github.com/de-abreu/visualizacao_computacional.git
```

> [!TIP] Dica
>
> [Instruções para a instalação do git](https://github.com/git-guides/install-git)

### Instalação de dependências

#### Usando DevEnv

> Recomendado

Para instalar as dependências deste projeto de forma isolada e temporária,
utilize o seguinte comando a partir da raiz do projeto:

```bash
devenv shell
```

Para acessar um ambiente virtual com todas as dependências instaladas.

> [!TIP] Dica
>
> [Instruções para a instalação do DevEnv](https://devenv.sh/getting-started/)

#### Usando `pip`

Instale as dependências python executando o seguinte comando na raiz do projeto:

```bash
pip install -r requirements.txt
```

Com isso já é possível acessar o jupyter notebook para executar as
visualizações. Entretanto, se se pretende reproduzir a raspagem dos dados no
site do ICMC e da Plataforma Lattes, ou a geração do banco de dados relacional a
partir destes dados, faz-se necessária a instalação do navegador Chromium (ou
outro baseado neste), o chromedriver, e SQLite. Recomenda-se que a instalação
destes requerimentos e o `pip` seja feita a partir do gerenciador de pacotes
disponível em seus sistema operacional.

## Webcrawlers

A raspagem de dados em nosso projeto foi feita nas seguintes etapas:

- Geração do arquivo `webcrawlers/docentes.csv` contendo os links para o
  Currículo Lattes dos docentes, extraídos do site do ICMC. Isso foi feito pela
  execução do script `webcrawlers/extracao_de_docentes.py`. Senão por três
  docentes para os quais tal link não constava, e por isso tiveram de ser
  buscados manualmente, todos os demais links foram capturados desta forma.

- Geração da lista de dicionários `webcrawlers/professores_all.pkl`, descrevendo
  os nomes dos docentes e seus respectivos projetos de pesquisa e artigos
  científicos; assim como os anos em que estes foram iniciados ou terminados.
  Esta raspagem de dados foi conduzida na plataforma Lattes usando o script
  `webcrawlers/lattes_crawler.py` de forma parcialmente automatizada, tido que
  Captchas necessitavam ser solucionados manualmente. Dois integrantes do grupo
  realizaram esta raspagem percorrendo a lista de professores em ordens
  alfabéticas opostas.

## Modelagem do Banco de Dados

Com SQLite e a biblioteca SQLAlchemy geramos, pela transformação da lista de
dicionários dos docentes o arquivo `database/lattes.db`, um banco de dados
modelado conforme ilustra o seguinte diagrama.

![Diagrama da modelagem do banco de dados](imgs/database_diagram.png)

O script utilizado para este propósito foi o `database/migration.py`

## Visualizações

As visualizações podem ser acessadas com o uso do jupyter notebook:

```bash
jupyter notebook seminario2/seminario2.ipynb
```

### Diagrama de Arcos

#### Premissa

![Diagrama de Arcos](imgs/arc_diagram_start.png)

> Visualização do Diagrama de arcos imediatamente após esta ter sido carregada

O Diagrama de arcos trata-se de uma visualização em que entidades são
representadas por pontos, enquanto relações entre estas são representadas por
arcos que os conectam. Assim sendo, esta trata-se de uma visualização adequada
para a representação de redes cujas relações se dão de forma não direcionada,
como é o caso das colaborações entre os docentes.

#### Pré-processamento dos dados

Nosso banco de dados foi prontificado a nos fornecer uma tabela cujas colunas e
tipos de dados são

| researcher_1 | researcher_2 | collaboration | type | start | end         |
| :----------- | :----------- | :------------ | :--- | :---- | :---------- |
| String       | String       | String        | Enum | Int   | Int ou NULL |

A diagrama de arcos, para ser gerado, faz uso das duas primeiras colunas apenas
para criar uma matriz simétrica $S_{n \times n}$ em que:

- $n$ é o número de pesquisadores distintos.
- $S_{ij} = S{ji}$ é o número de vezes em que o pesquisador $i$ colaborou em um
  projeto de pesquisa ou artigo científico com o pesquisador $j$.

tal que

- todo elemento $S_{ij} \ne 0$ corresponde a um arco, cuja espessura varia em
  função do seu valor normalizado.
- toda somatória $\sum^n_{k=1} S_{ik}$ corresponde a um ponto, cuja espessura
  varia em função do seu valor normalizado.

A ordem em que os pontos figuram no diagrama correspondem a ordenação espectral
[^1] das linhas da matriz, que garante uma sequência com a menor distância
possível entre nós altamente conectados. Como resultado, os arcos que conectam
os pontos são os menores possíveis e tendem a formação de grupos.

#### Funcionalidades

Não encontramos uma biblioteca que gerasse diagramas de arco dotados de
interatividade, então recorremos desenvolver nossa própria. Fizemos uso das
bibliotecas `pandas` e `numpy` para o pré-processamento dos dados, `plotly` para
a geração das formas geométricas, e `dash` para a atualização do diagrama
conforme interações do usuário via _callbacks_.

![Interação com o Diagrama de Arco](imgs/arc_diagram_interaction.png)

Nosso diagrama implementa uma interação quando o o usuário posiciona o mouse
sobre um ponto. Ao fazê-lo, todos os demais pontos e arcos não conectados a ele
têm sua opacidade reduzida, dando destaque apenas às conexões relevantes ao
pesquisador pelo ponto representado. Ainda, uma tabela sob o diagrama é
atualizada com os valores filtrados do Data Frame que lista os projetos para os
quais este pesquisador colaborou em ordem cronológica.

### Gráfico de Dispersão

> [!WARNING]
>
> Adicionar descrição por parte do Lucas

### Gráfico de linhas

> [!WARNING]
>
> Adicionar descrição por parte do Bom Dia

## Conclusões

Nossas visualizações foram capazes de responder às perguntas que se propuseram.

O diagrama de arcos revelou significativa interação entre os pesquisadores do
Instituto, onde a grande maioria destes (105 de 128), realizaram trabalhos
colaborativos pelo menos uma vez. Dentre estes, quatro pesquisadores se
destacaram como sendo os mais colaborativos: Francisco Louzada Neto (111
colaborações), Agma Juci Machado Traina (95 colaborações), Caetano Traina Junior
(85 colaborações) e Vicente Garibay Cancho. O diagrama nos permite identificar
grupos que frequentemente colaboram entre si, ressaltados pela largura dos arcos
e a posição que ocupam no diagrama. Dentre os pesquisadores já citados,
Francisco colabora com Vicente (36 ocasiões) mais que com qualquer outro
pesquisador, e por vez o mesmo é verdadeiro entre Agma e Caetano (53 ocasiões).

> [!WARNING]
>
> Adicionar conclusões das visualizações do Lucas e Bom Dia

O acréscimo de novas formas de interações pode auxiliar na visualização. Por
exemplo, a adição de um _slider_ que permita a filtragem por período de tempo
pode permitir avaliar a ocorrência de colaborações se avolumar em função do
tempo, ou simplesmente tornar menos poluída a esta visualização considerando um
período.

> [!WARNING]
>
> Adicionar possibilidades de novas interações para as visualizações do Lucas e
> Bom Dia

[^1]: LEVY, Bruno; ZHANG, Richard. Spectral Geometry Processing. 1 jan. 2009.
