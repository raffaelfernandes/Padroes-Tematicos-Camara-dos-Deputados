"""
texto_referencias.py

Remove números e datas de referências legais do texto que vai para o modelo de
embedding, mantendo os nomes das normas ("Lei", "Código Penal", "Estatuto do Idoso")
e todo o conteúdo. Motivo: na rodada 3 da Fase 3, os modelos agruparam ementas que
citavam leis de números parecidos (12.850 e 12.852, por exemplo), sem relação de assunto.

Exemplo:
    "Altera a Lei nº 12.850, de 2 de agosto de 2013 (Lei de Combate às Organizações
     Criminosas), para aumentar a pena."
    -> "Altera a Lei (Lei de Combate às Organizações Criminosas), para aumentar a pena."

Desde 15/11/2026, remover_formulas também tira do texto do embedding as expressões e palavras de
fórmula legislativa (altera, revoga, institui, dispõe sobre, dá nova redação, e dá outras
providências, artigo, inciso...), preservando os nomes de leis. Motivo: com elas, o e5 formou um
tópico pega-tudo de 3.974 ementas, e sem elas o BERTimbau ficou acima nas cinco sementes do UMAP
(experimento em src/experimentos/variantes_texto.py e data/processed/exp_texto/).
    "Altera a Lei (Lei Maria da Penha), para dispor sobre medidas protetivas, e dá outras providências."
    -> "(Lei Maria da Penha), para medidas protetivas"
"""

import re

_NUM = r"\d+(?:[.\-/]\d+)*[ºo°]?(?:-[A-Z]\b)?"          # 12.850 | 2.158-35/2001 | 5º | 84-C
_NRO = r"(?:n\.?\s?[º°]s?\.?|nos?\.?(?=\s*\d)|n\.(?=\s*\d)|nr\.?(?=\s*\d)|número(?=\s*\d))"

_MESES = r"(?:janeiro|fevereiro|mar[çc]o|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)"
_REF_LEGAL = [
    # data completa: ", de 2 de agosto de 2013" / "de 1º de maio de 1943"
    (re.compile(rf",?\s*de\s+\d{{1,2}}[ºo°]?\s+de\s+{_MESES}\s+de\s+\d{{4}}", re.I), ""),
    (re.compile(rf"\b\d{{1,2}}[ºo°]?\s+de\s+{_MESES}\s+de\s+\d{{4}}", re.I), ""),
    # tipo de norma + número: "Lei nº 12.850", "Decreto-Lei 2.848/1940", "Lei n. 9.504/97", "LC 101"
    (re.compile(r"\b((?:lei|leis|decreto(?:-?\s?lei)?|medida\s+provis[óo]ria|emenda\s+constitucional|"
                r"lei\s+complementar|resolu[çc][ãa]o|portaria)(?:\s+complementar|\s+federal)?)"
                rf"\s*{_NRO}?\s*{_NUM}(?:\s*(?:,|e)\s*{_NUM})*", re.I), r"\1"),
    # "nº 123" solto e listas "e 10.833/2003"
    (re.compile(rf"\b{_NRO}\s*{_NUM}", re.I), ""),
    (re.compile(r"\bn\.?\s?[º°]s?\.?(?=[\s,.;)]|$)", re.I), ""),
    (re.compile(r"\b\d{1,3}(?:\.\d{3})+(?:/\d{2,4})?(?:-[A-Z]\b)?"), ""),
    (re.compile(r"\b\d{1,5}/\d{2,4}\b"), ""),
    # dispositivos: "art. 121-A", "arts. 28 e 30", "§ 2º", "inciso XIV", "alínea 'a'"
    (re.compile(r"\b(arts?\.?|artigos?)\s*\d+[ºo°]?(?:-[A-Z])?(?:\s*(?:,|e)\s*\d+[ºo°]?(?:-[A-Z])?)*", re.I), r"\1"),
    (re.compile(r"(§§?)\s*\d+[ºo°]?(?:-[A-Z])?(?:\s*(?:,|e)\s*\d+[ºo°]?)*"), r"\1"),
    (re.compile(r"\b(incisos?)\s+[IVXLC]+(?:-[A-Z])?(?:\s*(?:,|e|a)\s*[IVXLC]+)*\b", re.I), r"\1"),
    (re.compile(r"\b(al[íi]neas?)\s+[\"'“”‘’]?[a-z][\"'“”‘’]?(?=[\s,.;)]|$)", re.I), r"\1"),
    (re.compile(r"\b\d+[ºo°](?:-[A-Z])?(?=[\s,.;)]|$)"), ""),
    # ano solto depois de referência: "de 1940", ", de 2019"
    (re.compile(r",?\s*de\s+(?:18|19|20)\d{2}\b", re.I), ""),
]


def mascarar_referencias(t: str) -> str:
    """Remove números e datas de referências legais, mantendo os nomes (Lei, Código Penal...)."""
    if not isinstance(t, str):
        return t
    for rx, sub in _REF_LEGAL:
        t = rx.sub(sub, t)
    t = re.sub(r"\(\s*[,;.]?\s*\)", " ", t)
    t = re.sub(r"\s+([,.;:)])", r"\1", t)
    t = re.sub(r"([,;])(\s*[,;])+", r"\1", t)
    t = re.sub(r"\(\s+", "(", t)
    return re.sub(r"\s{2,}", " ", t).strip()


# Fórmulas legislativas (desde 15/11/2026): expressões e palavras de fórmula que saem do texto do embedding. Usa as palavras de fórmula da lista
# dos rótulos (fase3_clustering.STOP_PT) que são verbos de alteração ou estrutura legal, mais "revoga" e as
# expressões fixas das ementas; ficam de fora as palavras genéricas da lista (nacional, federal, novo, forma...),
# que fazem parte de nomes como "Política Nacional de...". Nomes de leis ("Lei Maria da Penha",
# "Consolidação das Leis do Trabalho", "Lei de Diretrizes e Bases") são preservados.
EXPRESSOES = [
    r"e dá outras providências", r"dá outras providências", r"outras providências",
    r"dá nova redação (?:a|ao|à|aos|às)", r"dá nova redação", r"nova redação",
    r"dispõe sobre", r"dispor sobre", r"passam? a vigorar", r"com a seguinte redação",
    r"entra em vigor na data de sua publicação", r"entra em vigor", r"na data de sua publicação",
    r"decreto-lei", r"medida provisória",
]
FORMULAS = set("""art arts artigo artigos lei leis decreto dispõe dispor dispositivo dispositivos altera alterar
alterada alteradas alterado alterados acrescenta acrescentar acrescido acrescida inclui incluir institui instituir
estabelece estabelecer revoga revogar revogado revogada redação parágrafo parágrafos inciso incisos alínea alíneas
caput vigor vigorar publicação""".split())
# nome de lei: "Lei"/"Leis" seguido de palavra com maiúscula, direto ou depois de de/do/da/dos/das
_NOME_LEI = re.compile(r"\b(Leis?)(?=\s+(?:d[aeo]s?\s+)?[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")
_EXP_RE = re.compile(r"(?<![\w-])(?:" + "|".join(EXPRESSOES) + r")(?![\w])", re.IGNORECASE)
_FORM_RE = re.compile(r"(?<![\w-])(?:" + "|".join(sorted(map(re.escape, FORMULAS), key=len, reverse=True)) + r")(?![\w])\.?",
                      re.IGNORECASE)
_FUNC = r"(?:a|o|as|os|ao|aos|à|às|de|do|da|dos|das|no|na|nos|nas|pelo|pela|pelos|pelas|e|ambos|ambas|que|em|único|referida|referido)"


def remover_formulas(texto: str) -> str:
    """Tira as expressões e palavras de fórmula (sem diferenciar maiúsculas), preservando nomes de leis, e
    limpa o que sobra delas: artigos e preposições soltos antes de pontuação, hífens e pontos órfãos,
    vírgulas repetidas. O resto do texto fica como está, com a ordem e a gramática originais."""
    if not isinstance(texto, str):
        return texto
    s = _NOME_LEI.sub(lambda m: m.group(1).replace("L", "\x00"), texto or "")   # protege nomes de leis
    s = _EXP_RE.sub(" ", s)
    s = _FORM_RE.sub(" ", s)
    s = s.replace("\x00", "L")
    s = re.sub(r"(?<=\s)[-–]+(?=\s)|(?<=\s)[-–]+$|^\s*[-–]+", " ", s)       # travessões e hífens órfãos
    s = re.sub(r"\s+", " ", s)
    for _ in range(4):                                                    # palavras gramaticais órfãs
        s = re.sub(r"(?i)\b" + _FUNC + r"\s*(?=[,.;:)–-]|$)", "", s)
        s = re.sub(r"(?i)^\s*(?:" + _FUNC + r"\b\s*|[,.;:–-]\s*)+", "", s)
        s = re.sub(r"\s+([,.;:)])", r"\1", s)
        s = re.sub(r"([,.;:])(?:\s*[,.;:–-])+", r"\1", s)
        s = re.sub(r"\(\s+", "(", s)
        s = re.sub(r"\(\s*\)", "", s)
        s = re.sub(r"\s+", " ", s)
    s = s.strip(" ,;:-–")
    return s[:1].upper() + s[1:] if s else s
