"""Configuração dos modelos open source suportados."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModeloInfo:
    """Descreve um modelo de geração de imagens disponível no Hugging Face."""

    repo_id: str
    nome: str
    licenca: str
    passos_padrao: int
    guidance_padrao: float
    largura: int
    altura: int
    suporta_prompt_negativo: bool = True
    variante_fp16: bool = True


MODELOS: dict[str, ModeloInfo] = {
    "sdxl": ModeloInfo(
        repo_id="stabilityai/stable-diffusion-xl-base-1.0",
        nome="Stable Diffusion XL 1.0",
        licenca="CreativeML Open RAIL++-M (permite uso comercial)",
        passos_padrao=30,
        guidance_padrao=7.0,
        largura=1024,
        altura=1024,
    ),
    "sdxl-turbo": ModeloInfo(
        repo_id="stabilityai/sdxl-turbo",
        nome="SDXL Turbo (rápido, 1-4 passos)",
        licenca="Stability AI Non-Commercial (apenas uso não comercial)",
        passos_padrao=4,
        guidance_padrao=0.0,
        largura=512,
        altura=512,
    ),
    "flux-schnell": ModeloInfo(
        repo_id="black-forest-labs/FLUX.1-schnell",
        nome="FLUX.1 [schnell] (alta qualidade, exige GPU forte)",
        licenca="Apache 2.0",
        passos_padrao=4,
        guidance_padrao=0.0,
        largura=1024,
        altura=1024,
        suporta_prompt_negativo=False,
        variante_fp16=False,
    ),
}

MODELO_PADRAO = "sdxl"


@dataclass
class Configuracao:
    """Opções de execução do gerador."""

    modelo: str = MODELO_PADRAO
    dispositivo: str | None = None  # "cuda", "mps", "cpu" ou None para detectar
    economizar_memoria: bool = False  # liga CPU offload (GPUs com pouca VRAM)
    verificador_seguranca: bool = True  # checa imagens geradas contra conteúdo NSFW

    @property
    def info(self) -> ModeloInfo:
        try:
            return MODELOS[self.modelo]
        except KeyError as exc:
            opcoes = ", ".join(MODELOS)
            raise ValueError(
                f"Modelo desconhecido: {self.modelo!r}. Opções: {opcoes}"
            ) from exc
