import pytest
from datetime import datetime, timedelta

from src.educalin.domain.meta import Meta


@pytest.fixture
def agora():
    return datetime.now()


@pytest.fixture
def meta_padrao(agora):
    return Meta(
        descricao="Completar 10 exercícios",
        valor_alvo=10,
        prazo=agora + timedelta(days=7),
        progresso_atual=0,
    )


# -----------------------
# Progresso percentual (0 a 100)
# -----------------------
def test_progresso_percentual_inicial_zero(meta_padrao):
    assert meta_padrao.percentual_concluido * 100 == 0.0


def test_progresso_percentual_meio(meta_padrao):
    meta_padrao.atualizar_progresso(5)
    assert meta_padrao.percentual_concluido * 100 == 50.0


def test_progresso_percentual_exato_100_borda(meta_padrao):
    meta_padrao.atualizar_progresso(10)
    assert meta_padrao.percentual_concluido * 100 == 100.0


def test_progresso_percentual_nunca_ultrapassa_100(agora):
    """
    Mesmo que o domínio permita setar progresso > alvo (se você permitir no futuro),
    o percentual deve se manter no máximo em 100.
    Se atualmente você BLOQUEIA progresso > alvo, este teste continua válido,
    porque aqui usamos exatamente o alvo.
    """
    meta = Meta("Meta", 10, agora + timedelta(days=1), 10)
    assert meta.percentual_concluido * 100 == 100.0


# -----------------------
# verificar_conclusao True/False + borda
# -----------------------
def test_verificar_conclusao_false_quando_nao_atingiu(meta_padrao):
    meta_padrao.atualizar_progresso(9)
    assert meta_padrao.verificar_conclusao() is False


def test_verificar_conclusao_true_quando_atingiu_exato_borda(meta_padrao):
    meta_padrao.atualizar_progresso(10)
    assert meta_padrao.verificar_conclusao() is True


# -----------------------
# Prazos: vencido vs no prazo
# -----------------------
def test_meta_no_prazo_quando_prazo_futuro(meta_padrao):
    assert meta_padrao.esta_atrasada is False


def test_meta_atrasada_quando_prazo_passou_e_nao_concluiu(agora):
    meta = Meta(
        descricao="Meta",
        valor_alvo=10,
        prazo=agora - timedelta(days=1),
        progresso_atual=9,
    )
    assert meta.verificar_conclusao() is False
    assert meta.esta_atrasada is True


def test_meta_nao_atrasada_se_concluida_mesmo_com_prazo_passado(agora):
    meta = Meta(
        descricao="Meta",
        valor_alvo=10,
        prazo=agora - timedelta(days=1),
        progresso_atual=10,
    )
    assert meta.verificar_conclusao() is True
    assert meta.esta_atrasada is False


# -----------------------
# Cenários de borda / validação de domínio
# -----------------------
def test_borda_progresso_zero(meta_padrao):
    meta_padrao.atualizar_progresso(0)
    assert meta_padrao.percentual_concluido * 100 == 0.0
    assert meta_padrao.verificar_conclusao() is False


def test_nao_permite_progresso_negativo(meta_padrao):
    with pytest.raises(ValueError):
        meta_padrao.atualizar_progresso(-1)


def test_nao_permite_progresso_acima_do_alvo(meta_padrao):
    with pytest.raises(ValueError):
        meta_padrao.atualizar_progresso(11)
