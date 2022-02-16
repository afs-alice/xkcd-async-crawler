# **DESAFIO XKCD**

Repositório para apresentar a solução da etapa 2 (metodologia assíncrona) do desafio proposto por Justiça Fácil.

## **Descrição**

Este desafio tem como objetivo a construção de um programa assíncrono que
- Baixe todas as imagens do site xkcd;
- Salve as imagens localmente.

- O nome de cada arquivo deve ser o título md5 do quadrinho (ex.: o nome do arquivo referente ao quadrinho ```https://xkcd.com/2563/``` é throat_and_nasal_passages.png _dda012759b877051aba034de87eaef58.png_)
- Numa segunda vez que o programa for rodado, deve haver um verificador para que, caso o arquivo já exista, ele não seja salvo/sobrescrito localmente;
- O programa deve ter teste unitários.

## Versões das aplicações utilizadas

1. Python 3.7.12
2. AioFiles 0.8.0
3. AioHttp 3.8.1
4. AsyncClass 0.5.0
5. Pytest 6.2.5

## Preparação do ambiente de desenvolvimento

1. Clone o repositório
```bash
git clone https://github.com/afs-alice/xkcd-async-crawler.git
```
2. Crie um ambiente virtual com o Python 3.7

Exemplo com ```virtualenv```
```bash
mkvirtualenv NOME -p python3.7
```
3. Instale as dependências do projeto
```bash
pip install -r requirements/base.txt
```
4. Para executar os testes, instale as dependências do projeto
```bash
pip install -r requirements/dev.txt
```

## Como executar o script
Execute no terminal
```bash
python run.py
```

## Execução de testes

Execute o seguinte comando no terminal

```bash
pytest -v
```
