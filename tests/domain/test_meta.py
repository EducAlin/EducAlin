import pytest
from datetime import datetime, timedelta

from educalin.domain.meta import Meta


@pytest.fixture
def agora():
    return datetime.now()


@pytest.fixture
def meta_valida(agora):
    return Meta(
        descricao="Ler 10 capítulos",
        valor_alvo=10,
        prazo=agora + timedelta(days=7),
        progresso_atual=0,
    )


# -----------------------
# Criação / validações
# -----------------------
@pytest.mark.parametrize("descricao", ["", "   ", None, 123])
def test_descricao_invalida(agora, descricao):
    with pytest.raises(ValueError):
        Meta(descricao=descricao, valor_alvo=10, prazo=agora)


@pytest.mark.parametrize("valor_alvo", [0, -1, None, "10"])
def test_valor_alvo_invalido(agora, valor_alvo):
    with pytest.raises(ValueError):
        Meta(descricao="Ok", valor_alvo=valor_alvo, prazo=agora)


@pytest.mark.parametrize("prazo", [None, "2026-01-01", 123])
def test_prazo_invalido(prazo):
    with pytest.raises(ValueError):
        Meta(descricao="Ok", valor_alvo=10, prazo=prazo)


def test_progresso_inicial_nao_pode_exceder_alvo(agora):
    with pytest.raises(ValueError):
        Meta(descricao="Ok", valor_alvo=10, prazo=agora, progresso_atual=11)


# -----------------------
# Critérios: atualizar progresso + atingir meta automaticamente
# -----------------------
def test_atualizar_progresso_define_valor_absoluto(meta_valida):
    meta_valida.atualizar_progresso(3)
    assert meta_valida.progresso_atual == 3.0

    # não é incremento: troca para 5 (não vira 8)
    meta_valida.atualizar_progresso(5)
    assert meta_valida.progresso_atual == 5.0


def test_meta_identifica_quando_foi_atingida(meta_valida):
    assert meta_valida.verificar_conclusao() is False

    meta_valida.atualizar_progresso(10)
    assert meta_valida.verificar_conclusao() is True


def test_atualizar_progresso_nao_permite_valor_invalido(meta_valida):
    with pytest.raises(ValueError):
        meta_valida.atualizar_progresso(-1)

    with pytest.raises(ValueError):
        meta_valida.atualizar_progresso(999)


# -----------------------
# Critério: verificação de prazo
# -----------------------
def test_meta_atrasada_quando_prazo_passou_e_nao_concluiu(agora):
    meta = Meta(descricao="Ok", valor_alvo=10, prazo=agora - timedelta(days=1), progresso_atual=5)
    assert meta.esta_atrasada is True


def test_meta_nao_atrasada_se_concluida_mesmo_com_prazo_passado(agora):
    meta = Meta(descricao="Ok", valor_alvo=10, prazo=agora - timedelta(days=1), progresso_atual=10)
    assert meta.esta_atrasada is False
