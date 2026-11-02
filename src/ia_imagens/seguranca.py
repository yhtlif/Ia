"""Filtros de segurança aplicados ao texto antes da geração.

O objetivo é impedir usos abusivos: conteúdo sexual explícito, qualquer
representação de menores de idade e deepfakes de pessoas reais.
As imagens geradas também passam por um verificador NSFW (ver gerador.py).
"""

from __future__ import annotations

import re
import unicodedata

# Termos que indicam menores de idade (português e inglês).
TERMOS_MENORES = [
    "crianca", "criancas", "infantil", "menor de idade", "menores",
    "adolescente", "adolescentes", "novinha", "novinhas", "garotinha",
    "menininha", "colegial", "pre adolescente", "pre-adolescente",
    "child", "children", "kid", "kids", "minor", "underage", "teen", "teens",
    "teenager", "preteen", "loli", "lolita", "schoolgirl", "toddler", "infant",
    "little girl", "young girl", "juvenile",
]

# Termos de conteúdo sexual explícito / nudez.
TERMOS_EXPLICITOS = [
    "nua", "nuas", "nu", "pelada", "peladas", "nudez", "sexo", "sexual",
    "porno", "pornografia", "erotico", "erotica", "seios a mostra",
    "topless", "sem roupa", "sem roupas",
    "nude", "nudes", "naked", "nsfw", "porn", "pornographic", "sex",
    "sexy", "explicit", "hentai", "erotic", "lingerie", "undressed", "nipple",
    "nipples", "genitals", "fetish", "bdsm", "xxx",
]

# Pedidos para recriar pessoas reais (deepfake).
TERMOS_PESSOA_REAL = [
    "deepfake", "deep fake", "sosia", "lookalike", "look-alike",
    "in the likeness of", "rosto da atriz", "rosto da cantora",
]


class PromptBloqueado(ValueError):
    """Levantada quando o pedido viola as regras de uso."""


def normalizar(texto: str) -> str:
    """Minúsculas, sem acentos e com espaços simples."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento.lower()).strip()


def _compilar(termos: list[str]) -> re.Pattern[str]:
    alternativas = "|".join(re.escape(normalizar(t)) for t in sorted(set(termos), key=len, reverse=True))
    return re.compile(rf"(?<![a-z0-9])(?:{alternativas})(?![a-z0-9])")


_REGRAS = [
    (_compilar(TERMOS_MENORES), "Não é permitido gerar imagens de menores de idade."),
    (_compilar(TERMOS_EXPLICITOS), "Conteúdo sexual ou de nudez não é permitido."),
    (_compilar(TERMOS_PESSOA_REAL), "Não é permitido recriar a aparência de pessoas reais."),
]

# Idades numéricas abaixo de 18 ("16 anos", "15 years old", "17yo").
_IDADE = re.compile(r"(?<!\d)(\d{1,2})\s*(?:anos|ano|years?(?: old)?|yo|y/o)(?![a-z])")


def verificar_texto(*textos: str) -> None:
    """Levanta PromptBloqueado se algum texto violar as regras."""
    completo = normalizar(" ".join(t for t in textos if t))
    if not completo:
        return
    for padrao, motivo in _REGRAS:
        encontrado = padrao.search(completo)
        if encontrado:
            raise PromptBloqueado(f"{motivo} (termo: '{encontrado.group(0)}')")
    for idade in _IDADE.finditer(completo):
        if int(idade.group(1)) < 18:
            raise PromptBloqueado("Não é permitido gerar imagens de menores de idade.")
