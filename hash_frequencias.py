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
import unicodedata
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

# Símbolos que o Python trata como letra ou número, mas não formam palavras: 1º, 2ª, m², H₂O, ½.
SIMBOLOS = re.compile("[ºª¹²³¼½¾⁰-⁹₀-₉]")

# Caracteres invisíveis que partiriam uma palavra em duas: hífen opcional (comum em PDFs),
# marcas de junção e BOM. Mapeados para None, são apagados por str.translate.
INVISIVEIS = dict.fromkeys((0x00AD, 0x200C, 0x200D, 0x2060, 0xFEFF))


def normalizar_texto(texto):
    """Converte o texto em uma lista de palavras normalizadas.

    - transforma tudo em minúsculas ("Dados" e "dados" viram a mesma chave);
    - remove pontuação e números, mantendo apenas sequências de letras
      (letras acentuadas são preservadas: "estrutura", "árvore", "função");
    - unifica a forma dos acentos (NFC): "é" pode vir como um único caractere ou
      como "e" + acento, o que acontece em textos copiados de PDF ou do Mac.
    """
    texto = texto.translate(INVISIVEIS)
    texto = unicodedata.normalize("NFC", texto).lower()
    texto = SIMBOLOS.sub(" ", texto)
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


def chave_alfabetica(palavra):
    """Chave de ordenação que ignora acentos: "água" fica junto do "a", e não depois do "z"."""
    decomposta = unicodedata.normalize("NFD", palavra)
    sem_acentos = "".join(c for c in decomposta if not unicodedata.combining(c))
    return (sem_acentos, palavra)


def mais_frequentes(frequencias, quantidade=5):
    """Retorna as `quantidade` palavras mais frequentes.

    Ordena por frequência decrescente; em caso de empate, por ordem alfabética,
    para que o resultado seja sempre o mesmo. Custo O(k log k), k = palavras distintas.
    """
    itens = sorted(frequencias.items(), key=lambda item: (-item[1], chave_alfabetica(item[0])))
    return itens[:quantidade]


def consultar(frequencias, palavra):
    """Consulta a frequência de uma palavra já normalizada: acesso direto pela chave, O(1) em média."""
    return frequencias.get(palavra, 0)


def exibir_consultas(frequencias, termos, ignorar_stopwords=False):
    """Mostra a frequência de cada palavra buscada; uma frase é consultada palavra por palavra."""
    print("\n--- Consultas diretas na Tabela Hash ---")
    for termo in termos:
        palavras = normalizar_texto(termo)
        if not palavras:
            print(f"  '{termo}': não contém nenhuma palavra para buscar")
        for palavra in palavras:
            if ignorar_stopwords and palavra in STOPWORDS:
                print(f"  '{palavra}': não contada (stopword)")
            else:
                print(f"  '{palavra}': {formatar_ocorrencias(consultar(frequencias, palavra))}")


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
        for palavra in sorted(frequencias, key=chave_alfabetica):
            print(f"  {palavra:<22} {formatar_ocorrencias(frequencias[palavra])}")

    ranking = mais_frequentes(frequencias, top)
    print(f"\n--- Top {len(ranking)} palavras mais frequentes ---")
    if len(frequencias) < top:
        if len(frequencias) == 1:
            print("  (aviso: só existe 1 palavra distinta)")
        else:
            print(f"  (aviso: só existem {len(frequencias)} palavras distintas)")
    for posicao, (palavra, quantidade) in enumerate(ranking, start=1):
        print(f"  {posicao:>2}º {palavra:<20} {formatar_ocorrencias(quantidade)}")
    print("=" * 60)


def decodificar(dados):
    """Converte os bytes do arquivo em texto, aceitando UTF-8, UTF-16 e ANSI (cp1252)."""
    if dados.startswith((b"\xff\xfe", b"\xfe\xff")):   # marca (BOM) do UTF-16
        return dados.decode("utf-16")
    if b"\x00" in dados:                                # ex.: .pdf, .docx, imagens
        raise ValueError("o arquivo não parece ser um texto simples (.txt).")
    try:
        return dados.decode("utf-8-sig")
    except UnicodeDecodeError:
        return dados.decode("cp1252")                   # "ANSI" do Bloco de Notas


def carregar_texto(args):
    """Obtém o texto a partir dos argumentos, tratando erros de entrada."""
    if args.texto is not None:
        return args.texto
    if args.arquivo is not None and not args.arquivo.strip():
        raise ValueError("o caminho do arquivo está vazio.")
    caminho = Path(args.arquivo) if args.arquivo else ARQUIVO_PADRAO
    if not caminho.is_file():
        raise ValueError(f"arquivo não encontrado: {caminho}")
    return decodificar(caminho.read_bytes())


def main():
    parser = argparse.ArgumentParser(description="Contagem de frequências com Tabela Hash.")
    entrada = parser.add_mutually_exclusive_group()   # só uma fonte de texto por vez
    entrada.add_argument("--arquivo", help="caminho de um arquivo .txt para analisar")
    entrada.add_argument("--texto", help="texto informado diretamente na linha de comando")
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
    except UnicodeDecodeError:   # é um tipo de ValueError, por isso vem antes
        print("Erro ao ler a entrada: não foi possível reconhecer a codificação do arquivo (salve-o em UTF-8).")
        return 1
    except (ValueError, OSError) as erro:
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
        exibir_consultas(frequencias, args.buscar, ignorar_stopwords=args.sem_stopwords)
    return 0


if __name__ == "__main__":
    sys.exit(main())
