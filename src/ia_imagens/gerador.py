"""Geração de imagens com modelos de difusão open source (Hugging Face diffusers)."""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .config import Configuracao
from .prompts import Pedido, montar_prompt
from .seguranca import verificar_texto

if TYPE_CHECKING:  # pragma: no cover
    from PIL.Image import Image

log = logging.getLogger(__name__)

VERIFICADOR_REPO = "CompVis/stable-diffusion-safety-checker"
EXTRATOR_REPO = "openai/clip-vit-base-patch32"


@dataclass
class Resultado:
    imagens: list["Image"]
    prompt: str
    prompt_negativo: str
    semente: int
    bloqueadas: int = 0
    avisos: list[str] = field(default_factory=list)


def detectar_dispositivo() -> str:
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class GeradorDeImagens:
    """Carrega o modelo uma única vez e gera imagens a partir de pedidos."""

    def __init__(self, config: Configuracao | None = None) -> None:
        self.config = config or Configuracao()
        self.info = self.config.info
        self.dispositivo = self.config.dispositivo or detectar_dispositivo()
        self._pipe = None
        self._verificador = None
        self._extrator = None

    # ------------------------------------------------------------------ carga
    def _carregar_pipeline(self):
        if self._pipe is not None:
            return self._pipe

        import torch
        from diffusers import AutoPipelineForText2Image

        dtype = torch.float32 if self.dispositivo == "cpu" else torch.float16
        if self.info.repo_id.startswith("black-forest-labs/") and self.dispositivo == "cuda":
            dtype = torch.bfloat16

        kwargs = {"torch_dtype": dtype}
        if self.info.variante_fp16 and dtype == torch.float16:
            kwargs["variant"] = "fp16"

        log.info("Carregando %s em %s (%s)...", self.info.repo_id, self.dispositivo, dtype)
        pipe = AutoPipelineForText2Image.from_pretrained(self.info.repo_id, **kwargs)

        if self.config.economizar_memoria and self.dispositivo == "cuda":
            pipe.enable_model_cpu_offload()
        else:
            pipe = pipe.to(self.dispositivo)
        if hasattr(pipe, "enable_attention_slicing") and self.dispositivo != "cuda":
            pipe.enable_attention_slicing()

        self._pipe = pipe
        return pipe

    def _carregar_verificador(self):
        if self._verificador is None:
            from diffusers.pipelines.stable_diffusion.safety_checker import (
                StableDiffusionSafetyChecker,
            )
            from transformers import CLIPImageProcessor

            self._verificador = StableDiffusionSafetyChecker.from_pretrained(VERIFICADOR_REPO)
            self._extrator = CLIPImageProcessor.from_pretrained(EXTRATOR_REPO)
        return self._verificador, self._extrator

    # ---------------------------------------------------------------- geração
    def _filtrar_nsfw(self, imagens: list["Image"]) -> tuple[list["Image"], int]:
        import numpy as np
        import torch
        from PIL import Image as PILImage

        verificador, extrator = self._carregar_verificador()
        entrada = extrator(imagens, return_tensors="pt")
        arrays = [np.array(img, dtype=np.float32) / 255.0 for img in imagens]
        with torch.no_grad():
            _, nsfw = verificador(images=arrays, clip_input=entrada.pixel_values)

        seguras, bloqueadas = [], 0
        for img, flag in zip(imagens, nsfw):
            if flag:
                bloqueadas += 1
                seguras.append(PILImage.new("RGB", img.size, (0, 0, 0)))
            else:
                seguras.append(img)
        return seguras, bloqueadas

    def gerar(
        self,
        pedido: Pedido,
        quantidade: int = 1,
        passos: int | None = None,
        guidance: float | None = None,
        largura: int | None = None,
        altura: int | None = None,
        semente: int | None = None,
    ) -> Resultado:
        verificar_texto(pedido.descricao, pedido.cenario)
        prompt, negativo = montar_prompt(pedido)

        import torch

        pipe = self._carregar_pipeline()
        if semente is None or semente < 0:
            semente = random.randint(0, 2**32 - 1)
        gerador_dev = "cpu" if self.dispositivo == "mps" else self.dispositivo
        rng = torch.Generator(device=gerador_dev).manual_seed(int(semente))

        argumentos = dict(
            prompt=prompt,
            num_inference_steps=passos or self.info.passos_padrao,
            guidance_scale=self.info.guidance_padrao if guidance is None else guidance,
            width=largura or self.info.largura,
            height=altura or self.info.altura,
            num_images_per_prompt=quantidade,
            generator=rng,
        )
        if self.info.suporta_prompt_negativo:
            argumentos["negative_prompt"] = negativo

        imagens = pipe(**argumentos).images

        bloqueadas = 0
        avisos: list[str] = []
        if self.config.verificador_seguranca:
            imagens, bloqueadas = self._filtrar_nsfw(imagens)
            if bloqueadas:
                avisos.append(
                    f"{bloqueadas} imagem(ns) bloqueada(s) pelo verificador de conteúdo."
                )

        return Resultado(imagens, prompt, negativo, int(semente), bloqueadas, avisos)
