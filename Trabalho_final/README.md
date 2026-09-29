# MovieLens Explorer

Aplicação web local de consulta cinematográfica construída para demonstrar, na prática,
estruturas de dados implementadas do zero: **Hash Table**, **Trie** e
**Shell Sort**. A interface permite pesquisar títulos, explorar avaliações de
usuários e montar rankings a partir da base MovieLens.

## Funcionalidades

- busca de filmes por prefixo usando Trie;
- consulta das 20 melhores avaliações de um usuário;
- ranking de filmes por gênero;
- interseção de duas tags;
- melhores filmes em um intervalo de anos;
- modo de demonstração rápido e modo com a base completa;
- tempo de cada consulta exibido na interface.

## Como executar

Requer apenas Python 3.10 ou mais recente e um navegador. Não há dependências externas.

```bash
python3 gui.py
```

Também é possível iniciar pelo arquivo principal:

```bash
python3 main.py --gui
```

O console original continua disponível com:

```bash
python3 main.py
```

## Dados

A aplicação espera estes arquivos, que não são versionados por causa do tamanho:

```text
dados-trabalho-pequeno/
├── movies.csv
├── tags.csv
└── miniratings.csv

dados-trabalho-completo/
├── movies.csv
├── tags.csv
└── ratings.csv
```

Na interface, **Amostra rápida** usa `miniratings.csv` e é o modo recomendado
para demonstrações. **Base completa** usa todo o arquivo `ratings.csv`.

## Arquitetura

```text
gui.py              Servidor local e API da interface
index.html           Interface responsiva aberta no navegador
search_service.py   Regras de consulta compartilhadas
hash_table.py       Tabela hash com tratamento de colisões
trie.py             Árvore de prefixos para títulos
funcoes.py          Carga dos CSVs e Shell Sort
classes.py          Entidades Movie, Usuario e Tag
main.py             Interface original de linha de comando
```
