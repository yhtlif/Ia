"""Gerar imagens pela linha de comando."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import MODELO_PADRAO, MODELOS, Configuracao
from .prompts import ENQUADRAMENTOS, ESTILOS, FAIXAS_ETARIAS, ILUMINACOES, Pedido, montar_prompt
from .seguranca import PromptBloqueado, verificar_texto


def criar_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Gera retratos femininos com IA open source")
    p.add_argument("descricao", nargs="?", default="", help="Descrição livre da personagem")
    p.add_argument("--estilo", choices=list(ESTILOS), default="Fotorrealista")
    p.add_argument("--idade", choices=list(FAIXAS_ETARIAS), default="20-30 anos")
    p.add_argument("--enquadramento", choices=list(ENQUADRAMENTOS), default="Busto")
    p.add_argument("--iluminacao", choices=list(ILUMINACOES), default="Natural")
    p.add_argument("--cenario", default="")
    p.add_argument("--evitar", default="", help="Prompt negativo extra")
    p.add_argument("--modelo", choices=list(MODELOS), default=MODELO_PADRAO)
    p.add_argument("--dispositivo", choices=["cuda", "mps", "cpu"], default=None)
    p.add_argument("--economizar-memoria", action="store_true")
    p.add_argument("-n", "--quantidade", type=int, default=1)
    p.add_argument("--passos", type=int, default=None)
    p.add_argument("--guidance", type=float, default=None)
    p.add_argument("--largura", type=int, default=None)
    p.add_argument("--altura", type=int, default=None)
    p.add_argument("--semente", type=int, default=None)
    p.add_argument("-o", "--saida", type=Path, default=Path("saidas"))
    p.add_argument("--so-prompt", action="store_true",
                   help="Apenas mostra o prompt montado, sem gerar imagem")
    return p


def main(argv: list[str] | None = None) -> int:
    args = criar_parser().parse_args(argv)
    pedido = Pedido(
        descricao=args.descricao,
        estilo=args.estilo,
        faixa_etaria=args.idade,
        enquadramento=args.enquadramento,
        iluminacao=args.iluminacao,
        cenario=args.cenario,
        negativo_extra=args.evitar,
    )

    try:
        verificar_texto(pedido.descricao, pedido.cenario)
    except PromptBloqueado as erro:
        print(f"Bloqueado: {erro}", file=sys.stderr)
        return 2

    if args.so_prompt:
        prompt, negativo = montar_prompt(pedido)
        print(f"Prompt:   {prompt}\nNegativo: {negativo}")
        return 0

    from .gerador import GeradorDeImagens

    gerador = GeradorDeImagens(Configuracao(
        modelo=args.modelo,
        dispositivo=args.dispositivo,
        economizar_memoria=args.economizar_memoria,
    ))
    r = gerador.gerar(
        pedido,
        quantidade=args.quantidade,
        passos=args.passos,
        guidance=args.guidance,
        largura=args.largura,
        altura=args.altura,
        semente=args.semente,
    )

    args.saida.mkdir(parents=True, exist_ok=True)
    for i, img in enumerate(r.imagens):
        caminho = args.saida / f"retrato_{r.semente}_{i}.png"
        img.save(caminho)
        print(f"Salvo: {caminho}")
    for aviso in r.avisos:
        print(f"Aviso: {aviso}", file=sys.stderr)
    print(f"Semente: {r.semente}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
