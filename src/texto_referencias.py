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
