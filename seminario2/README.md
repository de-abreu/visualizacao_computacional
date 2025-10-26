# Seminário 2: Geração e exploração de um banco de dados acerca dos pesquisadores do ICMC-USP

## Autores

| Nome                                      | nUSP     |
| :---------------------------------------- | :------- |
| Lucas de Oliveira Ferreira                | 13695042 |
| Guilherme de Abreu Barreto                | 12543033 |
| Jhonathan Oliveira Alves                  | 11838116 |
| Lucas Pereira Franco de Almeida           | 12675020 |
| Miguel Prates Ferreira de Lima Cantanhede | 13672745 |

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

### Introdução

Conforme a proposta de seminário apresentada em enunciado, buscamos realizar um
levantamento de dados pertinentes a vivência universitária no ICMC. Em
particular, focamo-nos na exploração dos dados oferecidos pela plataforma
[Currículo Lattes](https://lattes.cnpq.br/), acerca da procução científica do
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
  as quais utilizamos em nossa pesquisa, e como obtê-las

- no tópico "_Webcrawler_" os programas que desenvolvemos tendo em vista a
  coleta (parcialmente) automatizada dos dados dos pesquisadores nos sites do
  instituto e da Plataforma Lattes.
- no tópico "Modelagem do Banco de Dados" a construção de um banco de dados
  relacional para o armazenamento estruturado destes dados.

- no tópico "Visualizações" a elaboração de _dashboards_ pelos quais realizamos
  a exibição destes dados em forma conveniente para responder aos nossos
  problemas de pesquisa.

Ao término de nossa pesquisa encontramos notável presença de colaboração entre
os docentes deste instituto, e alguns agrupamentos entre aqueles mais
colaborativos.

> [!NOTE] Adicionar conclusões do Lucas e Bom Dia
