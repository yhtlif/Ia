"""Interface web (Gradio) do gerador de retratos femininos."""

from __future__ import annotations

import argparse

from .config import MODELO_PADRAO, MODELOS, Configuracao
from .gerador import GeradorDeImagens
from .prompts import ENQUADRAMENTOS, ESTILOS, FAIXAS_ETARIAS, ILUMINACOES, Pedido
from .seguranca import PromptBloqueado

AVISO = (
    "Gere apenas retratos de **mulheres adultas** e **fictícias**. "
    "Conteúdo sexual, imagens de menores e recriações de pessoas reais são bloqueados."
)


def criar_interface(gerador: GeradorDeImagens):
    import gradio as gr

    info = gerador.info

    def gerar(descricao, estilo, faixa, enquadramento, iluminacao, cenario,
              negativo, quantidade, passos, guidance, largura, altura, semente):
        pedido = Pedido(
            descricao=descricao,
            estilo=estilo,
            faixa_etaria=faixa,
            enquadramento=enquadramento,
            iluminacao=iluminacao,
            cenario=cenario,
            negativo_extra=negativo,
        )
        try:
            r = gerador.gerar(
                pedido,
                quantidade=int(quantidade),
                passos=int(passos),
                guidance=float(guidance),
                largura=int(largura),
                altura=int(altura),
                semente=int(semente),
            )
        except PromptBloqueado as erro:
            raise gr.Error(str(erro)) from erro
        detalhes = f"**Semente:** {r.semente}\n\n**Prompt:** {r.prompt}"
        if r.avisos:
            detalhes = "⚠️ " + " ".join(r.avisos) + "\n\n" + detalhes
        return r.imagens, detalhes

    with gr.Blocks(title="IA de Retratos Femininos") as demo:
        gr.Markdown(f"# IA de Retratos Femininos\nModelo: **{info.nome}** — {info.licenca}\n\n{AVISO}")
        with gr.Row():
            with gr.Column(scale=1):
                descricao = gr.Textbox(
                    label="Descrição (em inglês dá melhores resultados)",
                    placeholder="long curly red hair, green eyes, freckles, wearing a white linen dress",
                    lines=3,
                )
                estilo = gr.Dropdown(list(ESTILOS), value="Fotorrealista", label="Estilo")
                faixa = gr.Dropdown(list(FAIXAS_ETARIAS), value="20-30 anos", label="Faixa etária")
                enquadramento = gr.Dropdown(list(ENQUADRAMENTOS), value="Busto", label="Enquadramento")
                iluminacao = gr.Dropdown(list(ILUMINACOES), value="Natural", label="Iluminação")
                cenario = gr.Textbox(label="Cenário", placeholder="flower garden in Paris")
                with gr.Accordion("Avançado", open=False):
                    negativo = gr.Textbox(label="Evitar (prompt negativo extra)")
                    quantidade = gr.Slider(1, 4, value=1, step=1, label="Quantidade")
                    passos = gr.Slider(1, 60, value=info.passos_padrao, step=1, label="Passos")
                    guidance = gr.Slider(0, 15, value=info.guidance_padrao, step=0.5, label="Guidance")
                    largura = gr.Slider(512, 1536, value=info.largura, step=64, label="Largura")
                    altura = gr.Slider(512, 1536, value=info.altura, step=64, label="Altura")
                    semente = gr.Number(value=-1, precision=0, label="Semente (-1 = aleatória)")
                botao = gr.Button("Gerar", variant="primary")
            with gr.Column(scale=1):
                galeria = gr.Gallery(label="Resultado", columns=2, height="auto")
                detalhes = gr.Markdown()

        botao.click(
            gerar,
            inputs=[descricao, estilo, faixa, enquadramento, iluminacao, cenario,
                    negativo, quantidade, passos, guidance, largura, altura, semente],
            outputs=[galeria, detalhes],
        )
    return demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Interface web da IA de retratos femininos")
    parser.add_argument("--modelo", choices=list(MODELOS), default=MODELO_PADRAO)
    parser.add_argument("--dispositivo", choices=["cuda", "mps", "cpu"], default=None)
    parser.add_argument("--economizar-memoria", action="store_true",
                        help="Ativa CPU offload para GPUs com pouca VRAM")
    parser.add_argument("--porta", type=int, default=7860)
    parser.add_argument("--compartilhar", action="store_true",
                        help="Cria um link público temporário do Gradio")
    args = parser.parse_args()

    config = Configuracao(
        modelo=args.modelo,
        dispositivo=args.dispositivo,
        economizar_memoria=args.economizar_memoria,
    )
    demo = criar_interface(GeradorDeImagens(config))
    demo.queue().launch(server_port=args.porta, share=args.compartilhar)


if __name__ == "__main__":
    main()
