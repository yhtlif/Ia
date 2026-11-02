"""Filtros de segurança aplicados ao texto antes da geração.

O filtro é propositalmente enxuto: bloqueia apenas o essencial para evitar
abusos e deixa passar moda, roupa de banho, maquiagem etc.

Continua bloqueado:
- qualquer referência a menores de idade (incluindo idades < 18);
- nudez e sexo explícito;
- recriação de pessoas reais (deepfake).

As imagens geradas também passam por um verificador NSFW (ver gerador.py).
"""

from __future__ import annotations

import re
import unicodedata

# Termos que indicam menores de idade (português e inglês).
TERMOS_MENORES = [
    "crianca", "criancas", "infantil", "menor de idade", "menores de idade",
    "adolescente", "adolescentes", "novinha", "novinhas", "garotinha",
    "menininha", "colegial", "pre adolescente", "pre-adolescente", "juvenil",
    "child", "children", "kid", "kids", "underage", "teen", "teens",
    "teenage", "teenager", "teenagers", "preteen", "loli", "lolita",
    "schoolgirl", "toddler", "infant", "little girl", "young girl", "juvenile",
]

# Nudez e sexo explícito. Palavras soltas como "sexy", "lingerie",
# "sensual" ou "biquíni" são permitidas.
TERMOS_EXPLICITOS = [
    "nua", "nuas", "pelada", "peladas", "nudez", "nudismo", "sem roupa",
    "sem roupas", "seios a mostra", "seios de fora", "topless",
    "pornografia", "porno", "pornografico", "erotico", "erotica",
    "fazendo sexo", "cena de sexo", "ato sexual", "sexo explicito",
    "naked", "nudes", "nudity", "fully nude", "completely nude", "nsfw", "porn",
    "pornographic", "hentai", "erotic", "undressed", "nipple", "nipples",
    "genitals", "having sex", "sex scene", "sex act", "sexual intercourse",
    "sexually explicit", "xxx",
]

# Pedidos para recriar pessoas reais (deepfake).
TERMOS_PESSOA_REAL = [
    "deepfake", "deep fake", "sosia", "lookalike", "look-alike",
    "in the likeness of", "rosto da atriz", "rosto da cantora",
]

# "nude"/"nu" só bloqueiam quando não se referem a cor (batom nude, tom nude...).
_CORES = (
    "lipstick|lips|lip|makeup|make-up|color|colour|colored|coloured|tone|tones|"
    "shade|heels|shoes|dress|gown|nails|nail|eyeshadow|palette|blush|top|"
    "outfit|suit|sweater|bag|pink|beige"
)
_ANTES_COR = ("batom", "tom", "cor", "maquiagem", "salto", "vestido", "unhas", "unha",
              "esmalte", "sombra", "sapato", "bolsa", "blusa", "look", "paleta")
_NUDE = re.compile(
    "".join(rf"(?<!{p} )" for p in _ANTES_COR)
    + rf"(?<![a-z0-9])nude(?![a-z0-9])(?! (?:{_CORES})(?![a-z]))"
)
# "nu" em português: só em expressões claras.
_NU = re.compile(r"(?<![a-z0-9])(?:homem|mulher|corpo|ficar|esta|todo|toda) nu(?![a-z0-9])")


class PromptBloqueado(ValueError):
    """Levantada quando o pedido viola as regras de uso."""


def normalizar(texto: str) -> str:
    """Minúsculas, sem acentos e com espaços simples."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", sem_acento.lower()).strip()


def _compilar(termos: list[str]) -> re.Pattern[str]:
    unicos = sorted({normalizar(t) for t in termos}, key=len, reverse=True)
    alternativas = "|".join(re.escape(t) for t in unicos)
    return re.compile(rf"(?<![a-z0-9])(?:{alternativas})(?![a-z0-9])")


MSG_MENORES = "Não é permitido gerar imagens de menores de idade."
MSG_EXPLICITO = "Nudez e conteúdo sexual explícito não são permitidos."
MSG_PESSOA_REAL = "Não é permitido recriar a aparência de pessoas reais."

_REGRAS = [
    (_compilar(TERMOS_MENORES), MSG_MENORES),
    (_compilar(TERMOS_EXPLICITOS), MSG_EXPLICITO),
    (_NUDE, MSG_EXPLICITO),
    (_NU, MSG_EXPLICITO),
    (_compilar(TERMOS_PESSOA_REAL), MSG_PESSOA_REAL),
]

# Idades explícitas: "de 16 anos", "16 anos de idade", "15 years old",
# "16-year-old", "17yo", "aged 15", "idade 15". Não pega "anos 80".
_IDADES = [
    re.compile(r"(?<![a-z0-9])de (\d{1,2}) anos?(?![a-z])(?! atras)"),
    re.compile(r"(?<!\d)(\d{1,2}) anos? de idade"),
    re.compile(r"(?<!\d)(\d{1,2})[\s-]*years?[\s-]*old"),
    re.compile(r"(?<!\d)(\d{1,2})[\s-]*(?:yo|y/o|yrs? old)(?![a-z])"),
    re.compile(r"(?<![a-z])(?:aged|age|idade|idade de) (\d{1,2})(?!\d)"),
]


def verificar_texto(*textos: str) -> None:
    """Levanta PromptBloqueado se algum texto violar as regras."""
    completo = normalizar(" ".join(t for t in textos if t))
    if not completo:
        return
    for padrao in _IDADES:
        for idade in padrao.finditer(completo):
            if int(idade.group(1)) < 18:
                raise PromptBloqueado(MSG_MENORES)
    for padrao, motivo in _REGRAS:
        encontrado = padrao.search(completo)
        if encontrado:
            raise PromptBloqueado(f"{motivo} (termo: '{encontrado.group(0).strip()}')")
