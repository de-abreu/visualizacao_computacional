# Visualização Computacional

Repositório dos trabalhos desenvolvidos para esta matéria no segundo semestre
de 2025.

## Dependências

O nosso projeto faz uso do Jupyter Notebook para execução e apresentação das
nossas análises. Este, dentre outras bibliotecas Python, podem ser obtidos por
uma das seguintes formas:

### Criando ambiente virtual

Supondo que você tenha python instalado no seu computador, essa é a primeira maneira recomendada de rodar o projeto. 
Para isso, faça: ```python3 -m venv venv```
Depois entre no ambiente virtual fazendo: ```source venv/bin/activate```
Por fim, entre na pasta *seminario1/* e faça ```pip install -r requirements.txt```.
Com isso, você terá todas as dependências usadas no projeto. Depois basta ir até *seminario1.Bubble Plot.ipynb*, 
configurar o kernel (selecione a venv que acabou de criar e instalar as dependências), alterar a variável
*RUN_ON_DOCKER* para *False* e depois clicar em rodar tudo.

### Em ambiente docker

Para facilitar rodar depois, criamos também um docker compose que disponibiliza os serviços para já rodar tudo em docker. Para isso, primeiro certifique-se que o *RUN_ON_DOCKER* é *True* (se você não fez nenhuma alteração até agora, esse é o padrão). 
Depois, vá para a pasta principal do projeto e rode ```docker compose up```. Ele fará todo o processo e você pode verificar os gráficos em [lo](http://localhost:8051).