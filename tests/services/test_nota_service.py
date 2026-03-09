"""
Testes unitários para NotaService e ObserverPublicadorEventos.

Usa mocks para isolar o serviço do repositório e dos canais de
notificação, garantindo que cada unidade seja testada individualmente.
"""
# pylint: disable=redefined-outer-name
from datetime import datetime
from unittest.mock import MagicMock

import pytest

from educalin.repositories.exceptions import NotaDuplicadaError
from educalin.services.nota_service import NotaService, PublicadorEventos
from educalin.services.observer_publicador import ObserverPublicadorEventos


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def repo_mock():
    """Repositório simulado que retorna nota_id=1 por padrão."""
    mock = MagicMock()
    mock.registrar_nota.return_value = 1
    return mock


@pytest.fixture
def publicador_mock():
    """PublicadorEventos simulado para verificar chamadas."""
    mock = MagicMock(spec=PublicadorEventos)
    return mock


@pytest.fixture
def service(repo_mock, publicador_mock):
    """NotaService com dependências simuladas."""
    return NotaService(repo_mock, publicador_mock)


@pytest.fixture
def service_sem_publicador(repo_mock):
    """NotaService sem publicador (publicador=None)."""
    return NotaService(repo_mock)


# ---------------------------------------------------------------------------
# NotaService — persistência
# ---------------------------------------------------------------------------

class TestNotaServicePersistencia:
    """Testa que o NotaService delega corretamente ao repositório."""

    def test_registrar_nota_chama_repo(self, service, repo_mock):
        """O serviço deve chamar repo.registrar_nota com os dados corretos."""
        service.registrar_nota(avaliacao_id=1, aluno_id=5, valor=8.5)
        repo_mock.registrar_nota.assert_called_once_with({
            "aluno_id": 5,
            "avaliacao_id": 1,
            "valor": 8.5,
        })

    def test_registrar_nota_retorna_id_do_repo(self, service, repo_mock):
        """O serviço deve retornar o ID gerado pelo repositório."""
        repo_mock.registrar_nota.return_value = 42
        nota_id = service.registrar_nota(avaliacao_id=1, aluno_id=5, valor=8.5)
        assert nota_id == 42

    def test_registrar_nota_repassa_nota_duplicada_error(self, service, repo_mock):
        """NotaDuplicadaError do repo deve ser propagada sem alteração."""
        repo_mock.registrar_nota.side_effect = NotaDuplicadaError("já existe")
        with pytest.raises(NotaDuplicadaError):
            service.registrar_nota(avaliacao_id=1, aluno_id=5, valor=8.5)

    def test_registrar_nota_repassa_valor_error(self, service, repo_mock):
        """ValueError do repo deve ser propagada sem alteração."""
        repo_mock.registrar_nota.side_effect = ValueError("inválido")
        with pytest.raises(ValueError):
            service.registrar_nota(avaliacao_id=1, aluno_id=5, valor=8.5)


# ---------------------------------------------------------------------------
# NotaService — publicação de eventos
# ---------------------------------------------------------------------------

class TestNotaServicePublicacao:
    """Testa que o NotaService dispara eventos após persistência."""

    def test_registrar_nota_dispara_publicador(self, service, publicador_mock):
        """O publicador deve ser chamado após a persistência bem-sucedida."""
        service.registrar_nota(avaliacao_id=1, aluno_id=5, valor=8.5)
        publicador_mock.publicar_nota_registrada.assert_called_once()

    def test_evento_contem_campos_obrigatorios(self, service, publicador_mock):
        """O evento disparado deve conter avaliacao_id, aluno_id, valor e timestamp."""
        service.registrar_nota(avaliacao_id=2, aluno_id=7, valor=6.0)
        evento = publicador_mock.publicar_nota_registrada.call_args[0][0]
        assert evento["evento"] == "nota_registrada"
        assert evento["avaliacao_id"] == 2
        assert evento["aluno_id"] == 7
        assert evento["valor"] == 6.0
        assert isinstance(evento["timestamp"], datetime)

    def test_publicador_nao_chamado_quando_repo_falha(self, service, repo_mock, publicador_mock):
        """Se o repositório falha, o publicador não deve ser chamado."""
        repo_mock.registrar_nota.side_effect = NotaDuplicadaError("já existe")
        with pytest.raises(NotaDuplicadaError):
            service.registrar_nota(avaliacao_id=1, aluno_id=5, valor=8.5)
        publicador_mock.publicar_nota_registrada.assert_not_called()

    def test_sem_publicador_nao_levanta_excecao(self, service_sem_publicador):
        """NotaService sem publicador deve funcionar normalmente."""
        nota_id = service_sem_publicador.registrar_nota(
            avaliacao_id=1, aluno_id=5, valor=8.5
        )
        assert nota_id == 1  # valor padrão do repo_mock


# ---------------------------------------------------------------------------
# ObserverPublicadorEventos
# ---------------------------------------------------------------------------

class TestObserverPublicadorEventos:
    """Testa a implementação concreta do publicador baseada em observers."""

    def test_publicar_chama_atualizar_em_todos_observers(self):
        """Todos os observers devem receber o evento via atualizar()."""
        obs1 = MagicMock()
        obs2 = MagicMock()
        publicador = ObserverPublicadorEventos([obs1, obs2])
        evento = {"evento": "nota_registrada", "valor": 7.0}

        publicador.publicar_nota_registrada(evento)

        obs1.atualizar.assert_called_once_with(evento)
        obs2.atualizar.assert_called_once_with(evento)

    def test_publicar_sem_observers_nao_levanta_excecao(self):
        """Lista vazia de observers não deve causar erro."""
        publicador = ObserverPublicadorEventos([])
        publicador.publicar_nota_registrada({"evento": "nota_registrada"})  # sem erro

    def test_init_rejeita_tipo_invalido(self):
        """Passar algo diferente de lista deve levantar TypeError."""
        with pytest.raises(TypeError):
            ObserverPublicadorEventos("nao_e_lista")

    def test_observer_que_falha_nao_impede_proximo(self):
        """Falha em um observer não deve impedir que os demais recebam o evento."""
        obs_falha = MagicMock()
        obs_falha.atualizar.side_effect = RuntimeError("canal indisponivel")
        obs_ok = MagicMock()
        publicador = ObserverPublicadorEventos([obs_falha, obs_ok])

        # ObserverPublicadorEventos captura a exceção individualmente via logging
        # e continua iterando — obs_ok DEVE ser chamado mesmo com obs_falha falhando.
        evento = {"evento": "nota_registrada"}
        publicador.publicar_nota_registrada(evento)

        obs_falha.atualizar.assert_called_once_with(evento)
        obs_ok.atualizar.assert_called_once_with(evento)
