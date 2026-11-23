"""
TED 02 - Parte 1: Tabelas Hash - Contagem de Frequências

Lê um texto (arquivo ou string), normaliza as palavras e conta quantas vezes
cada uma aparece usando uma Tabela Hash (o dicionário nativo do Python, `dict`).

Uso:
    python hash_frequencias.py                              # usa dados/texto_exemplo.txt
    python hash_frequencias.py --arquivo outro_texto.txt
    python hash_frequencias.py --texto "dados estrutura dados grafo estrutura dados"
    python hash_frequencias.py --top 10 --sem-stopwords     # ignora artigos, preposições etc.
"""

import argparse
import re
import sys
from pathlib import Path

# Garante acentuação correta no terminal do Windows.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ARQUIVO_PADRAO = Path(__file__).parent / "dados" / "texto_exemplo.txt"

# Palavras muito comuns que podem ser ignoradas (opção --sem-stopwords).
# Usamos um `set`, que também é uma tabela hash: o teste "palavra in STOPWORDS" é O(1) em média.
STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das",
    "em", "no", "na", "nos", "nas", "por", "pelo", "pela", "pelos", "pelas", "para",
    "com", "sem", "e", "ou", "que", "se", "ao", "aos", "à", "às", "é", "são", "mais",
    "como", "mas", "também", "seu", "sua", "seus", "suas", "isso", "esse", "essa",
    "este", "esta", "quando", "entre", "cada", "já", "não", "muito", "pode", "ser",
}


def normalizar_texto(texto):
    """Converte o texto em uma lista de palavras normalizadas.

    - transforma tudo em minúsculas ("Dados" e "dados" viram a mesma chave);
    - remove pontuação e números, mantendo apenas sequências de letras
      (letras acentuadas são preservadas: "estrutura", "árvore", "função").
    """
    texto = texto.lower()
    # [^\W\d_]+  = uma ou mais "letras" (caractere de palavra que não é dígito nem "_")
    return re.findall(r"[^\W\d_]+", texto)


def contar_frequencias(palavras, ignorar_stopwords=False):
    """Conta as ocorrências de cada palavra usando uma Tabela Hash (dict).

    Para cada palavra:
      1. calcula-se o hash da palavra para achar sua posição na tabela;
      2. se a chave já existe, o valor (contador) é incrementado;
      3. senão, a chave é inserida com valor 1.
    Busca, inserção e atualização custam O(1) em média, então o total é O(n).
    """
    frequencias = {}  # Tabela Hash: chave = palavra, valor = quantidade
    for palavra in palavras:
        if ignorar_stopwords and palavra in STOPWORDS:
            continue
        frequencias[palavra] = frequencias.get(palavra, 0) + 1
    return frequencias


def mais_frequentes(frequencias, quantidade=5):
    """Retorna as `quantidade` palavras mais frequentes.

    Ordena por frequência decrescente; em caso de empate, por ordem alfabética,
    para que o resultado seja sempre o mesmo. Custo O(k log k), k = palavras distintas.
    """
    itens = sorted(frequencias.items(), key=lambda item: (-item[1], item[0]))
    return itens[:quantidade]


def consultar(frequencias, palavra):
    """Consulta a frequência de uma palavra: acesso direto pela chave, O(1) em média."""
    chave = normalizar_texto(palavra)
    if not chave:
        return 0
    return frequencias.get(chave[0], 0)


def formatar_ocorrencias(n):
    return f"{n} ocorrência" if n == 1 else f"{n} ocorrências"


def exibir_relatorio(frequencias, total_palavras, top=5, mostrar_todas=True):
    """Imprime as frequências de forma organizada."""
    print("=" * 60)
    print(" CONTAGEM DE FREQUÊNCIAS COM TABELA HASH (dict)")
    print("=" * 60)
    print(f"Total de palavras no texto   : {total_palavras}")
    contabilizadas = sum(frequencias.values())
    if contabilizadas != total_palavras:
        print(f"Contabilizadas (sem stopwords): {contabilizadas}")
    print(f"Palavras distintas (chaves)  : {len(frequencias)}")

    if mostrar_todas:
        print("\n--- Todas as palavras (ordem alfabética) ---")
        for palavra in sorted(frequencias):
            print(f"  {palavra:<22} {formatar_ocorrencias(frequencias[palavra])}")

    ranking = mais_frequentes(frequencias, top)
    print(f"\n--- Top {len(ranking)} palavras mais frequentes ---")
    if len(frequencias) < top:
        print(f"  (aviso: só existem {len(frequencias)} palavras distintas)")
    for posicao, (palavra, quantidade) in enumerate(ranking, start=1):
        print(f"  {posicao:>2}º {palavra:<20} {formatar_ocorrencias(quantidade)}")
    print("=" * 60)


def carregar_texto(args):
    """Obtém o texto a partir dos argumentos, tratando erros de entrada."""
    if args.texto is not None:
        return args.texto
    caminho = Path(args.arquivo) if args.arquivo else ARQUIVO_PADRAO
    if not caminho.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    return caminho.read_text(encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Contagem de frequências com Tabela Hash.")
    parser.add_argument("--arquivo", help="caminho de um arquivo .txt (UTF-8) para analisar")
    parser.add_argument("--texto", help="texto informado diretamente na linha de comando")
    parser.add_argument("--top", type=int, default=5, help="quantas palavras mostrar no ranking (padrão 5)")
    parser.add_argument("--sem-stopwords", action="store_true", help="ignora palavras muito comuns")
    parser.add_argument("--resumo", action="store_true", help="não lista todas as palavras, só o ranking")
    parser.add_argument("--buscar", nargs="+", metavar="PALAVRA", help="consulta a frequência de palavras")
    args = parser.parse_args()

    if args.top < 1:
        print("Erro: --top deve ser um número inteiro maior que zero.")
        return 1

    try:
        texto = carregar_texto(args)
    except (FileNotFoundError, UnicodeDecodeError) as erro:
        print(f"Erro ao ler a entrada: {erro}")
        return 1

    palavras = normalizar_texto(texto)
    if not palavras:
        print("Erro: o texto informado não contém nenhuma palavra para analisar.")
        return 1

    frequencias = contar_frequencias(palavras, ignorar_stopwords=args.sem_stopwords)
    if not frequencias:
        print("Nenhuma palavra restou após remover as stopwords.")
        return 1

    exibir_relatorio(frequencias, len(palavras), top=args.top, mostrar_todas=not args.resumo)

    if args.buscar:
        print("\n--- Consultas diretas na Tabela Hash ---")
        for palavra in args.buscar:
            print(f"  '{palavra}': {formatar_ocorrencias(consultar(frequencias, palavra))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
