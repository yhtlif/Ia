import pytest

from ia_imagens.seguranca import PromptBloqueado, normalizar, verificar_texto


@pytest.mark.parametrize("texto", [
    "long curly hair, freckles, blue dress",
    "mulher elegante com vestido vermelho num café em Paris",
    "woman, 25 years old, business suit",
    "mulher de 35 anos sorrindo",
    # moda, roupa de banho e maquiagem
    "sexy red dress",
    "sensual pose, evening gown",
    "lingerie photoshoot, elegant",
    "biquíni na praia",
    "swimsuit, beach, summer",
    "maiô preto, piscina",
    "crop top and jeans",
    "tight leather pants",
    "vestido decotado",
    # "nude" como cor
    "batom nude",
    "nude lipstick, soft makeup",
    "vestido nude",
    "tom nude na maquiagem",
    "nude heels",
    # palavras que antes davam falso positivo
    "sexo feminino",
    "detalhes menores",
    "minor imperfections on the skin",
    "estilo anos 80",
    "moda dos anos 90",
    "foto de 2 anos atrás",
    "baby blue dress",
    "sexta-feira, nuance de cores, kidney beans",
    "Nu Metal concert",
])
def test_textos_permitidos(texto):
    verificar_texto(texto)


@pytest.mark.parametrize("texto", [
    "uma criança brincando",
    "teen girl at school",
    "garota de 16 anos",
    "menina 15 anos de idade",
    "girl, 15 years old",
    "16-year-old girl",
    "17yo woman",
    "aged 14",
    "estilo colegial",
    "Mulher NUA na praia",
    "mulher nu",
    "naked woman",
    "nude woman",
    "fully nude",
    "topless on the beach",
    "sem roupa",
    "having sex",
    "deepfake de uma atriz",
    "Sósia de uma cantora famosa",
])
def test_textos_bloqueados(texto):
    with pytest.raises(PromptBloqueado):
        verificar_texto(texto)


def test_normalizar_remove_acentos():
    assert normalizar("  Criança   NUA ") == "crianca nua"


def test_texto_vazio():
    verificar_texto("", "")
