"""Montagem de prompts para retratos femininos."""

from __future__ import annotations

from dataclasses import dataclass

ESTILOS: dict[str, str] = {
    "Fotorrealista": (
        "photorealistic photograph, 85mm lens, shallow depth of field, "
        "natural skin texture, sharp focus"
    ),
    "Estúdio": (
        "professional studio portrait, softbox lighting, clean seamless background, "
        "high-end photography, sharp focus"
    ),
    "Editorial de moda": (
        "fashion editorial photography, vogue style, elegant pose, "
        "dramatic composition, magazine cover quality"
    ),
    "Cinematográfico": (
        "cinematic film still, anamorphic lens, color graded, moody atmosphere, "
        "35mm film grain"
    ),
    "Anime": (
        "anime illustration, detailed line art, vibrant colors, "
        "studio quality cel shading"
    ),
    "Pintura a óleo": (
        "oil painting on canvas, classical portrait, visible brush strokes, "
        "renaissance lighting, museum quality"
    ),
    "Aquarela": (
        "watercolor painting, soft washes of color, delicate paper texture, "
        "artistic and dreamy"
    ),
    "Fantasia": (
        "epic fantasy art, ethereal glow, intricate details, digital painting, "
        "artstation trending"
    ),
    "Cyberpunk": (
        "cyberpunk portrait, neon lights, futuristic city at night, "
        "reflective surfaces, high detail"
    ),
    "Arte 3D": (
        "3d render, octane render, subsurface scattering, stylized character, "
        "soft studio lighting"
    ),
}

# Somente faixas etárias adultas.
FAIXAS_ETARIAS: dict[str, str] = {
    "20-30 anos": "young adult woman in her twenties",
    "30-40 anos": "adult woman in her thirties",
    "40-50 anos": "mature woman in her forties",
    "50-60 anos": "woman in her fifties",
    "60+ anos": "elderly woman, graceful aging",
}

ENQUADRAMENTOS: dict[str, str] = {
    "Close no rosto": "close-up headshot",
    "Busto": "head and shoulders portrait",
    "Meio corpo": "half-body portrait",
    "Corpo inteiro": "full-body shot",
}

ILUMINACOES: dict[str, str] = {
    "Natural": "soft natural daylight",
    "Hora dourada": "golden hour sunlight",
    "Estúdio": "three-point studio lighting",
    "Dramática": "dramatic chiaroscuro lighting",
    "Neon": "colorful neon lighting",
    "Luz de velas": "warm candlelight",
}

PROMPT_NEGATIVO_BASE = (
    "child, minor, teen, underage, nsfw, nude, naked, explicit, "
    "lowres, blurry, bad anatomy, deformed, disfigured, extra fingers, "
    "extra limbs, mutated hands, poorly drawn face, watermark, text, signature, "
    "jpeg artifacts, out of frame, cropped"
)


@dataclass
class Pedido:
    """Parâmetros escolhidos pelo usuário para uma imagem."""

    descricao: str = ""
    estilo: str = "Fotorrealista"
    faixa_etaria: str = "20-30 anos"
    enquadramento: str = "Busto"
    iluminacao: str = "Natural"
    cenario: str = ""
    negativo_extra: str = ""


def _escolher(opcoes: dict[str, str], chave: str, campo: str) -> str:
    if chave not in opcoes:
        validas = ", ".join(opcoes)
        raise ValueError(f"{campo} inválido: {chave!r}. Opções: {validas}")
    return opcoes[chave]


def montar_prompt(pedido: Pedido) -> tuple[str, str]:
    """Retorna (prompt, prompt_negativo) a partir de um pedido."""
    enquadramento = _escolher(ENQUADRAMENTOS, pedido.enquadramento, "Enquadramento")
    pessoa = _escolher(FAIXAS_ETARIAS, pedido.faixa_etaria, "Faixa etária")
    # Os encoders CLIP do SDXL leem só ~77 tokens: o mais importante vem primeiro.
    partes = [f"{enquadramento} of a beautiful {pessoa}, fully clothed"]
    descricao = pedido.descricao.strip()
    if descricao:
        partes.append(descricao)
    partes.append(_escolher(ESTILOS, pedido.estilo, "Estilo"))
    partes.append(_escolher(ILUMINACOES, pedido.iluminacao, "Iluminação"))
    cenario = pedido.cenario.strip()
    if cenario:
        partes.append(f"background: {cenario}")

    negativo = PROMPT_NEGATIVO_BASE
    extra = pedido.negativo_extra.strip()
    if extra:
        negativo = f"{negativo}, {extra}"

    return ", ".join(partes), negativo
