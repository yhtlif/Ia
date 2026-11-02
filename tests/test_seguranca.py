import pytest

from ia_imagens.seguranca import PromptBloqueado, normalizar, verificar_texto


@pytest.mark.parametrize("texto", [
    "long curly hair, freckles, blue dress",
    "mulher elegante com vestido vermelho num café em Paris",
    "woman, 25 years old, business suit",
    "mulher de 35 anos sorrindo",
])
def test_textos_permitidos(texto):
    verificar_texto(texto)


@pytest.mark.parametrize("texto", [
    "uma criança brincando",
    "teen girl at school",
    "garota de 16 anos",
    "girl, 15 years old",
    "17yo woman",
    "Mulher NUA na praia",
    "naked woman",
    "sexy lingerie",
    "deepfake de uma atriz",
    "Sósia de uma cantora famosa",
])
def test_textos_bloqueados(texto):
    with pytest.raises(PromptBloqueado):
        verificar_texto(texto)


def test_nao_bloqueia_palavras_que_contem_termos():
    # "sexta", "nuance" e "kidney" contêm termos bloqueados como substring
    verificar_texto("sexta-feira, nuance de cores, kidney beans")


def test_normalizar_remove_acentos():
    assert normalizar("  Criança   NUA ") == "crianca nua"


def test_texto_vazio():
    verificar_texto("", "")
