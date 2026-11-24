# TED 02 – Modelagem e Resolução Prática de Problemas com Grafos e Tabelas Hash

- **Disciplina:** Estruturas Avançadas de Dados
- **Atividade:** TED 02
- **Integrantes da dupla:** Pedro Paulo Teixeira de Araújo e Rafael Pontara
- **Entrega:** 25/11/2026

---

## Estrutura do repositório

```
ted-02-grafos-hash/
├── README.md                    # este arquivo
├── hash_frequencias.py          # Parte 1 – Tabela Hash: contagem de frequências
├── grafo_dijkstra.py            # Parte 2 – Grafo (lista de adjacência) + Dijkstra
├── dados/
│   └── texto_exemplo.txt        # texto de ~900 palavras usado na Parte 1
├── evidencias/                  # imagens (.png) geradas das saídas e saídas em .txt
│   ├── frequencias.png
│   ├── frequencias_exemplo_enunciado.png
│   ├── caminho_minimo.png
│   ├── caminho_minimo_nova_conexao.png
│   └── *.txt
└── docs/
    ├── documentacao.pdf         # documentação técnica
    ├── documentacao.html        # fonte da documentação
    └── banner.png               # banner usado na documentação
```

## Dependências

- **Python 3.8 ou superior** (testado no Python 3.11).
- Nenhuma biblioteca externa: são usados apenas módulos da biblioteca padrão
  (`re`, `os`, `argparse`, `pathlib`, `unicodedata`, `heapq`, `math`, `decimal`, `sys`). Não é preciso `pip install`.

## Como obter e executar

```powershell
git clone https://github.com/Jackfrost232/Grafos-e-Tabelas-Hash-Estruturas-Avan-adas-de-Dados-Documenta-o-t-cnica.git ted-02-grafos-hash
```

```powershell
cd ted-02-grafos-hash
```

Os comandos abaixo devem ser executados dentro dessa pasta.

Na tela, os acentos aparecem corretamente. Para salvar a saída em arquivo com `>` no PowerShell,
execute antes o comando abaixo, para o PowerShell ler a saída como UTF-8:

```powershell
[Console]::OutputEncoding = [Text.Encoding]::UTF8
```

## Parte 1 – Tabela Hash: contagem de frequências

O programa lê um texto, normaliza as palavras (minúsculas, sem pontuação, números ou símbolos como º e ²)
e conta as ocorrências em um `dict` do Python, que é uma tabela hash. Depois lista
todas as palavras com suas frequências e mostra o ranking das mais frequentes. Palavras com
hífen ou apóstrofo são contadas em partes ("guarda-chuva" vira "guarda" e "chuva").

```powershell
python hash_frequencias.py
```

| Opção | O que faz |
|---|---|
| `--arquivo caminho.txt` | analisa outro arquivo de texto (UTF-8, UTF-16 ou ANSI) |
| `--texto "..."` | analisa um texto digitado na linha de comando (não combina com `--arquivo`) |
| `--top N` | quantidade de palavras no ranking (padrão: 5) |
| `--sem-stopwords` | ignora palavras muito comuns (artigos, preposições...) |
| `--resumo` | mostra só o ranking, sem a lista completa |
| `--buscar p1 p2 ...` | consulta diretamente a frequência de palavras (uma frase é consultada palavra por palavra; acentos fazem diferença) |

Exemplo do enunciado:

```powershell
python hash_frequencias.py --texto "dados estrutura dados grafo estrutura dados"
```

Resultado: `dados: 3`, `estrutura: 2`, `grafo: 1`.

**Por que tabela hash?** Cada palavra é uma chave. O hash da chave leva direto à posição
onde fica o contador, então buscar, inserir e atualizar custam **O(1) em média**. Contar
*n* palavras custa **O(n)**. Sem a tabela hash, cada palavra teria de ser comparada
com todas as já vistas, o que daria O(n·k). No pior caso, quando há muitas colisões,
uma operação pode chegar a O(k), mas o `dict` do Python redimensiona a tabela para
manter o custo médio constante.

## Parte 2 – Grafo e caminho mínimo (Dijkstra)

Mapa fictício com **8 cidades** e **11 estradas de mão dupla**, com pesos em km.
A cidade *Horizonte* fica isolada de propósito, para demonstrar o caso em que não
existe caminho.

```
Alvorada  -> Bosque (7), Cascata (9), Floresta (14)
Bosque    -> Alvorada (7), Cascata (10), Dunas (15)
Cascata   -> Alvorada (9), Bosque (10), Dunas (11), Floresta (2)
Dunas     -> Bosque (15), Cascata (11), Esmeralda (6), Girassol (12)
Esmeralda -> Dunas (6), Floresta (9), Girassol (4)
Floresta  -> Alvorada (14), Cascata (2), Esmeralda (9)
Girassol  -> Dunas (12), Esmeralda (4)
Horizonte -> (sem ligações)
```

O grafo é guardado como **lista de adjacência**: um `dict` em que cada cidade aponta para
uma lista de tuplas `(vizinho, distância)`. O algoritmo de Dijkstra foi implementado no
próprio arquivo, usando `heapq` como fila de prioridade.

```powershell
python grafo_dijkstra.py
```

Sem argumentos, abre um menu interativo: digite o nome ou o número da origem e do destino.

```powershell
python grafo_dijkstra.py --origem Alvorada --destino Esmeralda
```

```powershell
python grafo_dijkstra.py --demo
```

```powershell
python grafo_dijkstra.py --conexao Horizonte Girassol 8 --origem Alvorada --destino Horizonte
```

| Opção | O que faz |
|---|---|
| `--origem X --destino Y` | calcula o caminho mínimo (aceita nome ou número; maiúsculas não importam) |
| `--demo` | roda vários casos, inclusive "sem caminho" e entradas inválidas (não combina com `--origem`/`--destino`) |
| `--conexao A B KM` | adiciona uma estrada sem editar o código (aceita nome ou número, e `2,5` ou `2.5`; pode repetir; cidades novas são criadas, com aviso) |

Nomes com espaço devem vir entre aspas, como em `--conexao "Cidade Nova" Girassol 8`.

Para mudar o mapa de forma permanente, edite as listas `CIDADES` e `ESTRADAS` no início
de `grafo_dijkstra.py`.

### Resultados principais

| Origem | Destino | Caminho mínimo | Distância |
|---|---|---|---|
| Alvorada | Esmeralda | Alvorada → Cascata → Floresta → Esmeralda | **20 km** |
| Bosque | Girassol | Bosque → Cascata → Floresta → Esmeralda → Girassol | **25 km** |
| Alvorada | Dunas | Alvorada → Cascata → Dunas | **20 km** |
| Alvorada | Horizonte | — | **não existe caminho** |

No primeiro caso, a rota Alvorada → Floresta → Esmeralda tem só 2 trechos, mas soma
23 km. Dijkstra escolhe a rota com 3 trechos e 20 km, porque considera os **pesos** das
estradas e não a quantidade de conexões.

### Tratamento de erros

- Origem ou destino inexistente, ou número fora da faixa: mensagem de erro com a lista de cidades.
- Origem igual ao destino: distância 0.
- Destino inalcançável: "Não existe caminho entre X e Y".
- Estrada com distância zero, negativa, não numérica ou ambígua (`1.000`), ou ligando uma cidade a ela mesma: rejeitada.
- Engano ao editar `CIDADES` ou `ESTRADAS`: mensagem indicando o problema.
- Na Parte 1: arquivo inexistente ou que não é texto, texto sem palavras e `--top` inválido.

## Evidências de execução

| Parte 1 – frequências | Parte 2 – caminho mínimo |
|---|---|
| ![frequências](evidencias/frequencias.png) | ![caminho mínimo](evidencias/caminho_minimo.png) |

As saídas completas estão nos arquivos `.txt` da pasta [`evidencias/`](evidencias/).

## Documentação técnica

Veja [`docs/documentacao.pdf`](docs/documentacao.pdf). Ela cobre os problemas resolvidos,
o uso da tabela hash, a lista de adjacência, a execução passo a passo do Dijkstra, a análise
de eficiência, as dificuldades encontradas e as decisões de implementação.
