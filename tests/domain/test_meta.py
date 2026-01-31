import pytest
from datetime import datetime, timedelta

from src.educalin.domain.meta import Meta


@pytest.fixture
def agora():
    return datetime.now()


@pytest.fixture
def meta_valida(agora):
    return Meta(
        meta_id=1,
        aluno="Pedro",
        descricao="Ler 10 capítulos",
        valor_alvo=10,
        prazo=agora + timedelta(days=7),
        progresso_atual=0,
    )


# -----------------------
# Criação / validação no __init__
# -----------------------
@pytest.mark.parametrize("meta_id", [0, -1, "1", None])
def test_meta_id_invalido_no_init(agora, meta_id):
    with pytest.raises(ValueError):
        Meta(meta_id=meta_id, aluno="A", descricao="D", valor_alvo=10, prazo=agora)


@pytest.mark.parametrize("aluno", ["", "   ", None, 123])
def test_meta_aluno_invalido_no_init(agora, aluno):
    with pytest.raises(ValueError):
        Meta(meta_id=1, aluno=aluno, descricao="D", valor_alvo=10, prazo=agora)


@pytest.mark.parametrize("descricao", ["", "   ", None, 123])
def test_meta_descricao_invalida_no_init(agora, descricao):
    with pytest.raises(ValueError):
        Meta(meta_id=1, aluno="A", descricao=descricao, valor_alvo=10, prazo=agora)


@pytest.mark.parametrize("valor_alvo", [0, -1, "10", None])
def test_meta_valor_alvo_invalido_no_init(agora, valor_alvo):
    with pytest.raises(ValueError):
        Meta(meta_id=1, aluno="A", descricao="D", valor_alvo=valor_alvo, prazo=agora)


@pytest.mark.parametrize("prazo", ["2026-01-01", None, 123])
def test_meta_prazo_invalido_no_init(prazo):
    with pytest.raises(ValueError):
        Meta(meta_id=1, aluno="A", descricao="D", valor_alvo=10, prazo=prazo)


@pytest.mark.parametrize("progresso", [-1, "0", None])
def test_meta_progresso_invalido_no_init(agora, progresso):
    with pytest.raises(ValueError):
        Meta(meta_id=1, aluno="A", descricao="D", valor_alvo=10, prazo=agora, progresso_atual=progresso)


def test_meta_progresso_nao_pode_exceder_alvo_no_init(agora):
    with pytest.raises(ValueError):
        Meta(meta_id=1, aluno="A", descricao="D", valor_alvo=10, prazo=agora, progresso_atual=11)


# -----------------------
# Imutabilidade do ID
# -----------------------
def test_id_nao_pode_ser_alterado(meta_valida):
    with pytest.raises(ValueError, match="não pode ser alterado"):
        meta_valida.id = 2


# -----------------------
# Setters básicos
# -----------------------
def test_setters_removem_espacos(meta_valida):
    meta_valida.aluno = "  Ana  "
    meta_valida.descricao = "  Estudar  "
    assert meta_valida.aluno == "Ana"
    assert meta_valida.descricao == "Estudar"


def test_valor_alvo_nao_pode_ser_menor_que_progresso(agora):
    m = Meta(meta_id=1, aluno="A", descricao="D", valor_alvo=10, prazo=agora, progresso_atual=5)
    with pytest.raises(ValueError):
        m.valor_alvo = 4


# -----------------------
# atualizar_progresso
# -----------------------
def test_atualizar_progresso_ok(meta_valida):
    meta_valida.atualizar_progresso(3)
    assert meta_valida.progresso_atual == 3.0


def test_atualizar_progresso_nao_permite_negativo(meta_valida):
    with pytest.raises(ValueError):
        meta_valida.atualizar_progresso(-1)


def test_atualizar_progresso_nao_pode_exceder_alvo(meta_valida):
    with pytest.raises(ValueError):
        meta_valida.atualizar_progresso(999)


# -----------------------
# verificar_conclusao / propriedades
# -----------------------
def test_verificar_conclusao_false(meta_valida):
    assert meta_valida.verificar_conclusao() is False


def test_verificar_conclusao_true(agora):
    m = Meta(meta_id=1, aluno="A", descricao="D", valor_alvo=10, prazo=agora, progresso_atual=10)
    assert m.verificar_conclusao() is True


def test_faltante(meta_valida):
    meta_valida.atualizar_progresso(4)
    assert meta_valida.faltante == 6.0


def test_percentual_concluido(meta_valida):
    meta_valida.atualizar_progresso(2)
    assert meta_valida.percentual_concluido == 0.2


def test_esta_atrasada_quando_prazo_passou_e_nao_concluiu(agora):
    m = Meta(meta_id=1, aluno="A", descricao="D", valor_alvo=10, prazo=agora - timedelta(days=1), progresso_atual=5)
    assert m.esta_atrasada is True


def test_nao_esta_atrasada_se_concluida_mesmo_com_prazo_passado(agora):
    m = Meta(meta_id=1, aluno="A", descricao="D", valor_alvo=10, prazo=agora - timedelta(days=1), progresso_atual=10)
    assert m.esta_atrasada is False


# -----------------------
# __str__
# -----------------------
def test_str_contem_campos(meta_valida):
    texto = str(meta_valida)
    assert "Meta(" in texto
    assert "id=" in texto
    assert "aluno=" in texto
    assert "descricao=" in texto
