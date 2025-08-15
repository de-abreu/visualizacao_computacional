# Visualização Computacional

Repositório dos trabalhos desenvolvidos para esta matéria no segundo semestre
de 2025.

## Dependências

O nosso projeto faz uso do Jupyter Notebook para execução e apresentação das
nossas análises. Este, dentre outras bibliotecas Python, podem ser obtidos por
uma das seguintes formas:

### Usando nix

Tendo instalado o gerenciador de pacotes `nix` com
[flakes habilitados](https://nixos.wiki/wiki/flakes), em seu terminal acesse a
pasta raiz do projeto e execute:

```bash
nix run github:de-abreu/visualizacao_computacional
```

Para baixar todos os arquivos e instalar a todas as dependências do projeto em
um ambiente isolado e lançar uma instância do Jupyter Notebook usando o
navegador Chromium.

### Usando Docker

#### Criando ambiente virtual

Supondo que você tenha python instalado no seu computador, essa é a primeira
maneira recomendada de rodar o projeto. Para isso, faça: `python3 -m venv venv`
Depois entre no ambiente virtual fazendo: `source venv/bin/activate` Por fim,
entre na pasta _seminario1/_ e faça `pip install -r requirements.txt`. Com isso,
você terá todas as dependências usadas no projeto. Depois basta ir até
_seminario1.Bubble Plot.ipynb_, configurar o kernel (selecione a venv que acabou
de criar e instalar as dependências), alterar a variável _RUN_ON_DOCKER_ para
_False_ e depois clicar em rodar tudo.

#### No ambiente docker

Para facilitar rodar depois, criamos também um docker compose que disponibiliza
os serviços para já rodar tudo em docker. Para isso, primeiro certifique-se que
o _RUN_ON_DOCKER_ é _True_ (se você não fez nenhuma alteração até agora, esse é
o padrão). Depois, vá para a pasta principal do projeto e rode
`docker compose up`. Ele fará todo o processo e você pode verificar os gráficos
no [localhost](http://localhost:8051).
