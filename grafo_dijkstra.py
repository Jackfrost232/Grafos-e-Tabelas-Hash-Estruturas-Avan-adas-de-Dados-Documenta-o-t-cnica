"""
TED 02 - Parte 2: Grafos - Representação e Caminho Mínimo (Dijkstra)

Um mapa fictício de 8 cidades é representado como um grafo ponderado não
direcionado, armazenado em uma LISTA DE ADJACÊNCIA. O algoritmo de Dijkstra
(implementado neste arquivo, com fila de prioridade `heapq`) encontra a rota de
menor distância total entre uma origem e um destino.

Uso:
    python grafo_dijkstra.py                                  # menu interativo
    python grafo_dijkstra.py --origem Alvorada --destino Esmeralda
    python grafo_dijkstra.py --origem 1 --destino 5           # também aceita o número da cidade
    python grafo_dijkstra.py --demo                           # executa casos de demonstração
    python grafo_dijkstra.py --conexao Horizonte Girassol 8 --origem Alvorada --destino Horizonte
                                                              # adiciona uma ligação sem editar o código
"""

import argparse
import heapq
import math
import re
import sys

# Garante acentuação correta no terminal do Windows.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


# ---------------------------------------------------------------------------
# 1. Dados do cenário
# ---------------------------------------------------------------------------

# Cidades (nós) do mapa fictício. "Horizonte" fica isolada de propósito,
# para demonstrar o tratamento de "não existe caminho".
CIDADES = [
    "Alvorada", "Bosque", "Cascata", "Dunas",
    "Esmeralda", "Floresta", "Girassol", "Horizonte",
]

# Estradas (arestas): (cidade A, cidade B, distância em km). Pesos sempre positivos.
# Para incluir novas ligações, basta acrescentar linhas aqui (ou usar --conexao).
ESTRADAS = [
    ("Alvorada", "Bosque", 7),
    ("Alvorada", "Cascata", 9),
    ("Alvorada", "Floresta", 14),
    ("Bosque", "Cascata", 10),
    ("Bosque", "Dunas", 15),
    ("Cascata", "Dunas", 11),
    ("Cascata", "Floresta", 2),
    ("Dunas", "Esmeralda", 6),
    ("Dunas", "Girassol", 12),
    ("Esmeralda", "Floresta", 9),
    ("Esmeralda", "Girassol", 4),
]

DISTANCIA_MAXIMA = 1_000_000_000   # km; evita números grandes demais para calcular e exibir


# ---------------------------------------------------------------------------
# 2. Representação do grafo: lista de adjacência
# ---------------------------------------------------------------------------
# O grafo é um dicionário em que cada cidade (chave) aponta para a lista de
# seus vizinhos, cada um guardado como uma tupla (vizinho, distância):
#
#   {
#     "Alvorada": [("Bosque", 7), ("Cascata", 9), ("Floresta", 14)],
#     "Bosque":   [("Alvorada", 7), ("Cascata", 10), ("Dunas", 15)],
#     ...
#   }
#
# Como as estradas são de mão dupla, cada estrada aparece nas listas das duas cidades.

def criar_grafo(cidades):
    """Cria um grafo com as cidades informadas e nenhuma ligação."""
    return {cidade: [] for cidade in cidades}


def adicionar_cidade(grafo, cidade):
    """Inclui uma cidade nova (sem vizinhos), se ainda não existir."""
    grafo.setdefault(cidade, [])


def adicionar_estrada(grafo, cidade_a, cidade_b, distancia, mao_dupla=True):
    """Inclui uma aresta ponderada entre duas cidades, validando os dados."""
    if cidade_a == cidade_b:
        raise ValueError(f"Uma estrada não pode ligar '{cidade_a}' a ela mesma.")
    numero = isinstance(distancia, (int, float)) and not isinstance(distancia, bool)
    # A comparação encadeada também rejeita nan e infinito.
    if not numero or not 0 < distancia <= DISTANCIA_MAXIMA:
        raise ValueError(f"Distância inválida ({distancia!r}) entre {cidade_a} e {cidade_b}: "
                         f"deve ser um número positivo de até {DISTANCIA_MAXIMA} km.")
    for cidade in (cidade_a, cidade_b):
        if cidade not in grafo:
            raise KeyError(f"Cidade '{cidade}' não existe no mapa.")

    grafo[cidade_a].append((cidade_b, distancia))
    if mao_dupla:
        grafo[cidade_b].append((cidade_a, distancia))


def montar_mapa():
    """Constrói o grafo do cenário padrão a partir de CIDADES e ESTRADAS."""
    grafo = criar_grafo(CIDADES)
    for estrada in ESTRADAS:
        if len(estrada) != 3:
            raise ValueError(f"Estrada {estrada!r} deve ter duas cidades e uma distância.")
        cidade_a, cidade_b, distancia = estrada
        adicionar_estrada(grafo, cidade_a, cidade_b, distancia)
    return grafo


def exibir_lista_adjacencia(grafo):
    print("=" * 64)
    print(" MAPA (LISTA DE ADJACÊNCIA)  -  cidade -> [(vizinho, km), ...]")
    print("=" * 64)
    for numero, (cidade, vizinhos) in enumerate(grafo.items(), start=1):
        texto = ", ".join(f"{v} ({formatar_km(d)})" for v, d in vizinhos) or "(sem ligações)"
        print(f"  {numero}. {cidade:<10} -> {texto}")
    total_arestas = sum(len(v) for v in grafo.values()) // 2
    print(f"\n  {len(grafo)} cidades, {total_arestas} estradas (mão dupla)")
    print("=" * 64)


# ---------------------------------------------------------------------------
# 3. Algoritmo de Dijkstra
# ---------------------------------------------------------------------------

def dijkstra(grafo, origem):
    """Calcula a menor distância da origem até todas as cidades.

    Retorna:
      distancias -> {cidade: menor distância conhecida (math.inf se inalcançável)}
      anteriores -> {cidade: cidade que vem antes dela no melhor caminho}

    Funcionamento:
      - todas as distâncias começam em infinito, exceto a origem (0);
      - a fila de prioridade (heap) sempre entrega a cidade com a menor distância
        provisória ainda não finalizada;
      - para cada vizinho dessa cidade, tenta-se "relaxar" a aresta: se passar pela
        cidade atual for mais curto, atualiza a distância e o anterior do vizinho.
    Como os pesos são positivos, quando uma cidade sai do heap sua distância já é a
    definitiva. Complexidade: O((V + E) log V).
    """
    distancias = {cidade: math.inf for cidade in grafo}
    anteriores = {cidade: None for cidade in grafo}
    distancias[origem] = 0

    fila = [(0, origem)]          # heap de tuplas (distância, cidade)
    visitadas = set()

    while fila:
        distancia_atual, cidade = heapq.heappop(fila)
        if cidade in visitadas:   # entrada antiga/desatualizada no heap: ignora
            continue
        visitadas.add(cidade)

        for vizinho, peso in grafo[cidade]:
            nova_distancia = distancia_atual + peso
            if nova_distancia < distancias[vizinho]:      # relaxamento
                distancias[vizinho] = nova_distancia
                anteriores[vizinho] = cidade
                heapq.heappush(fila, (nova_distancia, vizinho))

    return distancias, anteriores


def reconstruir_caminho(anteriores, origem, destino):
    """Volta do destino até a origem seguindo `anteriores` e inverte a sequência."""
    caminho = []
    cidade = destino
    while cidade is not None:
        caminho.append(cidade)
        cidade = anteriores[cidade]
    caminho.reverse()
    return caminho if caminho and caminho[0] == origem else []


def menor_caminho(grafo, origem, destino):
    """Retorna (caminho, distância_total). Se não houver caminho: ([], math.inf)."""
    if origem not in grafo:
        raise KeyError(f"Origem '{origem}' não existe no mapa.")
    if destino not in grafo:
        raise KeyError(f"Destino '{destino}' não existe no mapa.")

    distancias, anteriores = dijkstra(grafo, origem)
    if distancias[destino] == math.inf:
        return [], math.inf
    return reconstruir_caminho(anteriores, origem, destino), distancias[destino]


# ---------------------------------------------------------------------------
# 4. Interface (entrada/saída)
# ---------------------------------------------------------------------------

def limpar_entrada(entrada):
    """Remove espaços das pontas e a marca BOM que alguns terminais inserem."""
    return entrada.replace("\ufeff", "").strip()


def resolver_nome_cidade(grafo, entrada):
    """Aceita o nome (sem diferenciar maiúsculas/minúsculas) ou o número da cidade."""
    entrada = limpar_entrada(entrada)
    cidades = list(grafo)
    if entrada.isdecimal():   # isdecimal, e não isdigit: "²" é dígito, mas int("²") falha
        # Números com mais de 9 algarismos nunca são válidos e nem precisam ser convertidos.
        indice = int(entrada) - 1 if len(entrada) <= 9 else -1
        if 0 <= indice < len(cidades):
            return cidades[indice]
        raise KeyError(f"Número de cidade inválido: {entrada[:20]} (use 1 a {len(cidades)}).")
    for cidade in cidades:
        if cidade.lower() == entrada.lower():
            return cidade
    raise KeyError(f"Cidade '{entrada}' não existe no mapa.")


def resolver_ou_criar_cidade(grafo, entrada):
    """Usada em --conexao: aceita nome ou número existente; um nome novo cria a cidade."""
    entrada = limpar_entrada(entrada)
    if not entrada:
        raise ValueError("o nome da cidade não pode ficar vazio.")
    try:
        return resolver_nome_cidade(grafo, entrada)
    except KeyError as erro:
        if entrada.isdecimal():   # número fora da faixa: não vira nome de cidade
            raise ValueError(erro.args[0]) from None
    adicionar_cidade(grafo, entrada)
    return entrada


def ler_distancia(texto):
    """Converte "8", "2,5" ou "2.5" em número; recusa o que não for um número claro."""
    texto = texto.strip()
    if not re.fullmatch(r"[+-]?[0-9]+([.,][0-9]+)?", texto):
        raise ValueError(f"distância '{texto}' não é um número.")
    if re.fullmatch(r"[+-]?[1-9][0-9]{0,2}[.,][0-9]{3}", texto):
        raise ValueError(f"distância '{texto}' é ambígua (milhar ou decimal?): escreva, por exemplo, 1000 ou 1,5.")
    distancia = float(texto.replace(",", "."))
    return int(distancia) if distancia.is_integer() else distancia   # "8 km" em vez de "8.0 km"


def formatar_km(valor):
    # 12 algarismos significativos: mostra 1234567 km por inteiro e 0.1 + 0.2 como 0.3 km
    return f"{valor:.12g} km"


def formatar_trechos(quantidade):
    return "1 trecho" if quantidade == 1 else f"{quantidade} trechos"


def exibir_resultado(grafo, origem, destino):
    print(f"\nOrigem : {origem}\nDestino: {destino}")
    if origem == destino:
        print("Origem e destino são a mesma cidade: distância 0 km.")
        return

    caminho, distancia = menor_caminho(grafo, origem, destino)
    if not caminho:
        print(f"Não existe caminho entre {origem} e {destino}.")
        return

    # Detalha cada trecho, consultando o peso de cada aresta na lista de adjacência.
    print(f"Caminho mínimo: {' -> '.join(caminho)}")
    print("Trechos:")
    for atual, proxima in zip(caminho, caminho[1:]):
        # Se houver mais de uma estrada entre as duas cidades, Dijkstra usa a mais curta.
        peso = min(d for v, d in grafo[atual] if v == proxima)
        print(f"  {atual:<10} -> {proxima:<10} {formatar_km(peso):>7}")
    print(f"Distância total: {formatar_km(distancia)}  ({formatar_trechos(len(caminho) - 1)})")


def menu_interativo(grafo):
    # Se a entrada vier de um arquivo ou de outro programa (e não do teclado), lê como UTF-8.
    if not sys.stdin.isatty() and hasattr(sys.stdin, "reconfigure"):
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    exibir_lista_adjacencia(grafo)
    print("Digite o nome ou o número da cidade. Deixe em branco (ou 'sair') para encerrar.")
    while True:
        try:
            entrada_origem = limpar_entrada(input("\nOrigem : "))
            if entrada_origem.lower() in ("", "sair"):
                break
            entrada_destino = limpar_entrada(input("Destino: "))
            if entrada_destino.lower() in ("", "sair"):
                break
            origem = resolver_nome_cidade(grafo, entrada_origem)
            destino = resolver_nome_cidade(grafo, entrada_destino)
            exibir_resultado(grafo, origem, destino)
        except KeyError as erro:
            print(f"Erro: {erro.args[0]}")
            print("Cidades disponíveis: " + ", ".join(grafo))
        except (EOFError, KeyboardInterrupt):
            print()
            break


def executar_demo(grafo):
    exibir_lista_adjacencia(grafo)
    casos = [
        ("Alvorada", "Esmeralda"),   # menor caminho tem MAIS trechos que a rota direta
        ("Bosque", "Girassol"),
        ("Alvorada", "Dunas"),
        ("Alvorada", "Horizonte"),   # cidade isolada: sem caminho
    ]
    for origem, destino in casos:
        print("-" * 64)
        exibir_resultado(grafo, origem, destino)
    print("-" * 64)
    print("\nTratamento de entrada inválida:")
    for entrada in ("Atlantida", "99"):
        try:
            resolver_nome_cidade(grafo, entrada)
        except KeyError as erro:
            print(f"  Erro: {erro.args[0]}")


def main():
    parser = argparse.ArgumentParser(description="Caminho mínimo com Dijkstra em um mapa fictício.")
    parser.add_argument("--origem", help="nome ou número da cidade de origem")
    parser.add_argument("--destino", help="nome ou número da cidade de destino")
    parser.add_argument("--demo", action="store_true", help="executa casos de demonstração")
    parser.add_argument("--conexao", nargs=3, action="append", metavar=("CIDADE_A", "CIDADE_B", "KM"),
                        help="adiciona uma estrada (pode repetir); cidades novas são criadas")
    # "-0,5" vira "-0.5": com vírgula, o argparse o confundiria com o nome de uma opção.
    args = parser.parse_args([re.sub(r"^(-[0-9]+),([0-9]+)$", r"\1.\2", a) for a in sys.argv[1:]])

    if args.demo and (args.origem is not None or args.destino is not None):
        print("Erro: --demo usa casos prontos; não combine com --origem e --destino.")
        return 1

    try:
        grafo = montar_mapa()
    except (KeyError, ValueError) as erro:
        print(f"Erro nas listas CIDADES/ESTRADAS: {erro.args[0]}")
        return 1

    # Ligações extras informadas na linha de comando.
    for cidade_a, cidade_b, km in args.conexao or []:
        existentes = set(grafo)
        try:
            distancia = ler_distancia(km)
            cidade_a = resolver_ou_criar_cidade(grafo, cidade_a)
            cidade_b = resolver_ou_criar_cidade(grafo, cidade_b)
            adicionar_estrada(grafo, cidade_a, cidade_b, distancia)
            print(f"Estrada adicionada: {cidade_a} <-> {cidade_b} ({formatar_km(distancia)})")
        except ValueError as erro:
            print(f"Erro ao adicionar estrada: {erro.args[0]}")
            return 1
        for cidade in (cidade_a, cidade_b):
            if cidade not in existentes:
                print(f"Aviso: a cidade '{cidade}' não existia e foi criada. Confira se o nome está certo.")

    if args.demo:
        executar_demo(grafo)
        return 0

    if args.origem is not None or args.destino is not None:
        if not (args.origem and args.destino):
            print("Erro: informe --origem e --destino juntos, sem deixar nenhum vazio.")
            return 1
        try:
            origem = resolver_nome_cidade(grafo, args.origem)
            destino = resolver_nome_cidade(grafo, args.destino)
        except KeyError as erro:
            print(f"Erro: {erro.args[0]}")
            print("Cidades disponíveis: " + ", ".join(grafo))
            return 1
        exibir_lista_adjacencia(grafo)
        exibir_resultado(grafo, origem, destino)
        return 0

    menu_interativo(grafo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
