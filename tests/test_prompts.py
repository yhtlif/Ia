import pytest

from ia_imagens.prompts import ESTILOS, FAIXAS_ETARIAS, Pedido, montar_prompt


def test_prompt_padrao_contem_elementos_basicos():
    prompt, negativo = montar_prompt(Pedido(descricao="long red hair, green eyes"))
    assert "young adult woman" in prompt
    assert "long red hair, green eyes" in prompt
    assert "head and shoulders portrait" in prompt
    assert "child" in negativo and "nsfw" in negativo


def test_cenario_e_negativo_extra():
    prompt, negativo = montar_prompt(Pedido(cenario="beach at sunset", negativo_extra="hat"))
    assert "background: beach at sunset" in prompt
    assert negativo.endswith(", hat")


@pytest.mark.parametrize("estilo", list(ESTILOS))
def test_todos_os_estilos(estilo):
    prompt, _ = montar_prompt(Pedido(estilo=estilo))
    assert ESTILOS[estilo] in prompt


def test_faixas_etarias_sao_adultas():
    assert all(k.startswith(("20", "30", "40", "50", "60")) for k in FAIXAS_ETARIAS)


def test_opcao_invalida():
    with pytest.raises(ValueError):
        montar_prompt(Pedido(estilo="Inexistente"))
