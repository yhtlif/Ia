# IA de Retratos Femininos (open source)

Gerador de imagens de mulheres (retratos, moda, arte, fantasia) que roda **localmente** usando modelos de difusão open source do Hugging Face:

| Chave          | Modelo                                   | Licença do modelo                  | Indicado para |
|----------------|------------------------------------------|------------------------------------|---------------|
| `sdxl` (padrão)| Stable Diffusion XL 1.0                  | CreativeML Open RAIL++-M (comercial ok) | GPU com 8 GB+ |
| `sdxl-turbo`   | SDXL Turbo                               | Stability AI Non-Commercial        | Rápido, GPUs menores |
| `flux-schnell` | FLUX.1 [schnell]                         | Apache 2.0                         | Melhor qualidade, GPU 16–24 GB+ |

O código deste projeto é MIT. Os pesos dos modelos seguem a licença de cada um.

## Recursos

- **Interface web** (Gradio) e **linha de comando**
- 10 estilos prontos: fotorrealista, estúdio, editorial de moda, cinematográfico, anime, pintura a óleo, aquarela, fantasia, cyberpunk, arte 3D
- Controles de faixa etária (somente adultas), enquadramento, iluminação e cenário
- Semente reprodutível, quantidade, passos, guidance e resolução ajustáveis
- Funciona em GPU NVIDIA (CUDA), Apple Silicon (MPS) ou CPU (lento)

## Uso responsável

O projeto tem proteções embutidas:

1. **Filtro de texto** (`seguranca.py`) bloqueia pedidos com menores de idade (incluindo idades < 18), conteúdo sexual/nudez e recriação de pessoas reais (deepfake).
2. **Prompt negativo** fixo contra menores e NSFW em todas as gerações.
3. **Verificador de imagem** (`CompVis/stable-diffusion-safety-checker`) substitui por uma imagem preta qualquer resultado detectado como NSFW.

Não remova essas proteções para gerar conteúdo ilegal ou não consensual. Você é responsável pelo uso das imagens.

## Instalação

Requer Python 3.10+.

```bash
git clone https://github.com/yhtlif/Ia.git
cd Ia
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# GPU NVIDIA: instale antes o PyTorch com CUDA (veja https://pytorch.org/get-started/locally/)
# ex.: pip install torch --index-url https://download.pytorch.org/whl/cu124

pip install -e .
```

Na primeira execução o modelo é baixado automaticamente (SDXL ≈ 7 GB).
O FLUX.1 exige aceitar os termos na página do modelo e fazer login: `huggingface-cli login`.

## Interface web

```bash
ia-imagens-web                         # SDXL, abre em http://localhost:7860
ia-imagens-web --modelo sdxl-turbo     # mais rápido
ia-imagens-web --economizar-memoria    # GPUs com pouca VRAM
ia-imagens-web --compartilhar          # gera link público temporário
```

## Linha de comando

```bash
ia-imagens "long curly red hair, green eyes, freckles, white linen dress" \
    --estilo "Editorial de moda" --idade "30-40 anos" \
    --enquadramento "Meio corpo" --iluminacao "Hora dourada" \
    --cenario "lavender field in Provence" -n 2 --semente 42

# Ver o prompt montado sem gerar imagem
ia-imagens "short black hair, red lipstick" --estilo Cyberpunk --so-prompt
```

As imagens são salvas em `saidas/`.

Dicas:
- Descrições em **inglês** geram resultados melhores.
- O SDXL lê só ~77 tokens do prompt; seja direto na descrição (use `--so-prompt` para conferir o que será enviado).

## Uso em Python

```python
from ia_imagens import Configuracao, Pedido
from ia_imagens.gerador import GeradorDeImagens

gerador = GeradorDeImagens(Configuracao(modelo="sdxl"))
r = gerador.gerar(Pedido(descricao="braided blonde hair, warrior armor", estilo="Fantasia"))
r.imagens[0].save("guerreira.png")
```

## Estrutura

```
src/ia_imagens/
  config.py     # modelos suportados e opções
  prompts.py    # estilos e montagem do prompt
  seguranca.py  # filtro de texto
  gerador.py    # pipeline diffusers + verificador NSFW
  app.py        # interface Gradio
  cli.py        # linha de comando
tests/          # testes (não precisam de GPU)
```

## Testes

```bash
pip install -e ".[dev]"
pytest
```

## Licença

MIT — veja [LICENSE](LICENSE).
