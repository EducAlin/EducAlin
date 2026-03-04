"""
Testes de integração do padrão Observer em Turma, PlanoAcao e Meta.

Valida que Turma, PlanoAcao e Meta implementam corretamente o padrão Observer
e disparam notificações apropriadas quando eventos ocorrem.
"""

import pytest
from datetime import datetime, timedelta, date
from educalin.domain.turma import Turma, Observer
from educalin.domain.professor import Professor
from educalin.domain.aluno import Aluno
from educalin.domain.avaliacao import Avaliacao
from educalin.domain.meta import Meta
from educalin.domain.material import MaterialPDF
from educalin.services.notificador import NotificadorEmail, NotificadorPush


class MockObserver(Observer):
    """Observer mock para testes de integração"""
    
    def __init__(self):
        self.eventos_recebidos = []
    
    def atualizar(self, evento: dict) -> None:
        """Registra eventos recebidos"""
        self.eventos_recebidos.append(evento)
    
    def ultimo_evento(self):
        """Retorna o último evento recebido"""
        return self.eventos_recebidos[-1] if self.eventos_recebidos else None


class TestTurmaObserverIntegracao:
    """Testes de integração do padrão Observer em Turma"""

    @pytest.fixture
    def setup(self):
        """Setup para todos os testes"""
        professor = Professor("João Professor", "joao@example.com", "senha123", "prof001")
        turma = Turma("ES-2025.2", "Engenharia de Software", "2025.2", professor)
        
        aluno = Aluno("João Aluno", "joao.aluno@example.com", "senha123", "mat001")
        turma.adicionar_aluno(aluno)
        
        avaliacao = Avaliacao("Prova 1", date.today(), 10.0, 0.5)
        turma.adicionar_avaliacao(avaliacao)
        
        observer_mock = MockObserver()
        turma.adicionar_observer(observer_mock)
        
        return {
            'turma': turma,
            'professor': professor,
            'aluno': aluno,
            'avaliacao': avaliacao,
            'observer': observer_mock
        }

    def test_turma_cria_plano_acao(self, setup):
        """Turma deve criar plano de ação e notificar observers"""
        turma = setup['turma']
        aluno = setup['aluno']
        observer = setup['observer']
        
        # Criar plano via turma
        plano = turma.criar_plano_acao(
            aluno,
            "Melhorar em algoritmos",
            30,
            "Focar em estruturas de dados"
        )
        
        # Verificar que plano foi criado
        assert plano is not None
        assert plano.aluno_alvo == aluno
        
        # Verificar que observer foi notificado
        assert len(observer.eventos_recebidos) > 0
        ultimo = observer.ultimo_evento()
        assert ultimo['evento'] == 'plano_acao_criado'
        assert ultimo['aluno_nome'] == aluno.nome
        assert ultimo['objetivo'] == "Melhorar em algoritmos"
        assert ultimo['prazo_dias'] == 30

    def test_turma_registra_nota_e_notifica(self, setup):
        """Turma deve registrar nota e notificar observers"""
        turma = setup['turma']
        aluno = setup['aluno']
        avaliacao = setup['avaliacao']
        observer = setup['observer']
        
        # Limpar eventos anteriores
        observer.eventos_recebidos.clear()
        
        # Registrar nota
        turma.registrar_nota(aluno, avaliacao, 8.5)
        
        # Verificar que observer foi notificado
        assert len(observer.eventos_recebidos) > 0
        evento = observer.eventos_recebidos[-1]
        assert evento['evento'] == 'nota_registrada'
        assert evento['aluno_nome'] == aluno.nome
        assert evento['nota_valor'] == 8.5
        assert evento['nota_maximo'] == 10.0
        assert evento['media_aluno'] == 8.5

    def test_turma_notifica_multiplos_observers(self, setup):
        """Turma deve notificar múltiplos observers"""
        turma = setup['turma']
        observer1 = MockObserver()
        observer2 = MockObserver()
        observer3 = setup['observer']
        
        # Adicionar observers
        turma.adicionar_observer(observer1)
        turma.adicionar_observer(observer2)
        
        # Registrar nota
        aluno = setup['aluno']
        avaliacao = setup['avaliacao']
        turma.registrar_nota(aluno, avaliacao, 7.5)
        
        # Verificar que todos foram notificados
        assert len(observer1.eventos_recebidos) > 0
        assert len(observer2.eventos_recebidos) > 0
        assert len(observer3.eventos_recebidos) > 0

    def test_turma_registra_nota_aluno_inexistente_fail(self, setup):
        """Turma deve rejeitar nota para aluno não matriculado"""
        turma = setup['turma']
        aluno_desconhecido = Aluno("Maria", "maria@example.com", "senha", "mat999")
        avaliacao = setup['avaliacao']
        
        with pytest.raises(ValueError, match="não está nesta turma"):
            turma.registrar_nota(aluno_desconhecido, avaliacao, 8.0)

    def test_turma_cria_plano_aluno_inexistente_fail(self, setup):
        """Turma deve rejeitar plano para aluno não matriculado"""
        turma = setup['turma']
        aluno_desconhecido = Aluno("Maria", "maria@example.com", "senha", "mat999")
        
        with pytest.raises(ValueError, match="não está nesta turma"):
            turma.criar_plano_acao(aluno_desconhecido, "Objetivo", 30)


class TestPlanoAcaoObserverIntegracao:
    """Testes de integração do padrão Observer em PlanoAcao"""

    @pytest.fixture
    def setup(self):
        """Setup para os testes"""
        from educalin.domain.plano_acao import PlanoAcao
        
        aluno = Aluno("João Aluno", "joao@example.com", "senha123", "mat001")
        plano = PlanoAcao(aluno, "Melhorar em álgebra", 30)
        
        observer_mock = MockObserver()
        plano.adicionar_observer(observer_mock)
        
        return {
            'plano': plano,
            'aluno': aluno,
            'observer': observer_mock
        }

    def test_plano_notifica_quando_enviado(self, setup):
        """PlanoAcao deve notificar quando é enviado"""
        plano = setup['plano']
        observer = setup['observer']
        
        # Adicionar material (obrigatório para enviar)
        material = MaterialPDF("Material 1", "Descrição do PDF", "Prof", datetime.now(), 10)
        plano.adicionar_material(material)
        
        # Limpar eventos anteriores
        observer.eventos_recebidos.clear()
        
        # Enviar plano
        plano.enviar()
        
        # Verificar notificação
        eventos = [e for e in observer.eventos_recebidos if e['evento'] == 'plano_enviado']
        assert len(eventos) > 0
        assert eventos[0]['aluno_nome'] == setup['aluno'].nome

    def test_plano_notifica_quando_concluido(self, setup):
        """PlanoAcao deve notificar quando é concluído"""
        plano = setup['plano']
        observer = setup['observer']
        
        # Preparar plano
        material = MaterialPDF("Material", "Descrição", "Prof", datetime.now(), 15)
        plano.adicionar_material(material)
        plano.enviar()
        plano.iniciar()
        
        # Limpar eventos anteriores
        observer.eventos_recebidos.clear()
        
        # Concluir
        plano.concluir()
        
        # Verificar notificação
        eventos = [e for e in observer.eventos_recebidos if e['evento'] == 'plano_concluido']
        assert len(eventos) > 0


class TestMetaObserverIntegracao:
    """Testes de integração do padrão Observer em Meta"""

    @pytest.fixture
    def setup(self):
        """Setup para os testes"""
        meta = Meta(
            "Atingir média 8.0",
            valor_alvo=8.0,
            prazo=datetime.now() + timedelta(days=30)
        )
        
        observer_mock = MockObserver()
        meta.adicionar_observer(observer_mock)
        
        return {
            'meta': meta,
            'observer': observer_mock
        }

    def test_meta_notifica_quando_atingida(self, setup):
        """Meta deve notificar quando é atingida"""
        meta = setup['meta']
        observer = setup['observer']
        
        # Limpar eventos iniciais
        observer.eventos_recebidos.clear()
        
        # Atualizar progresso para atingir a meta
        meta.atualizar_progresso(8.0)
        
        # Verificar notificação
        eventos = [e for e in observer.eventos_recebidos if e['evento'] == 'meta_atingida']
        assert len(eventos) == 1
        assert eventos[0]['descricao'] == "Atingir média 8.0"
        assert eventos[0]['progresso_atual'] == 8.0
        assert eventos[0]['percentual_concluido'] == 1.0

    def test_meta_notifica_apenas_na_primeira_atingida(self, setup):
        """Meta deve notificar apenas uma vez quando atingida"""
        meta = setup['meta']
        observer = setup['observer']
        
        # Limpar eventos iniciais
        observer.eventos_recebidos.clear()
        
        # Atualizar para atingir
        meta.atualizar_progresso(8.0)
        eventos_primeiro = len([e for e in observer.eventos_recebidos if e['evento'] == 'meta_atingida'])
        
        # Não pode atualizar acima do alvo, então manter no alvo
        meta.atualizar_progresso(8.0)
        eventos_segundo = len([e for e in observer.eventos_recebidos if e['evento'] == 'meta_atingida'])
        
        assert eventos_primeiro == 1
        assert eventos_segundo == 1  # Não deve disparar novamente

    def test_meta_nao_notifica_se_nao_atinge(self, setup):
        """Meta não deve notificar se não atingir o objetivo"""
        meta = setup['meta']
        observer = setup['observer']
        
        # Limpar eventos iniciais
        observer.eventos_recebidos.clear()
        
        # Atualizar com valor abaixo do objetivo
        meta.atualizar_progresso(5.0)
        
        # Verificar que não notificou
        eventos = [e for e in observer.eventos_recebidos if e['evento'] == 'meta_atingida']
        assert len(eventos) == 0


class TestObserverIntegracaoCompleta:
    """Testes de integração completa com múltiplas entidades"""

    def test_fluxo_completo_com_notificadores(self):
        """Teste de fluxo completo: criar turma, aluno, nota, plano e meta"""
        # Setup
        professor = Professor("Prof", "prof@example.com", "senha", "prof001")
        turma = Turma("ES-2025.2", "ES", "2025.2", professor)
        
        aluno = Aluno("João", "joao@example.com", "senha", "mat001")
        turma.adicionar_aluno(aluno)
        
        avaliacao = Avaliacao("Prova", date.today(), 10.0, 0.5)
        turma.adicionar_avaliacao(avaliacao)
        
        # Adicionar notificadores
        email_notif = NotificadorEmail("admin@example.com")
        push_notif = NotificadorPush("usuario_123", ["device_1"])
        
        turma.adicionar_observer(email_notif)
        turma.adicionar_observer(push_notif)
        
        # Registrar nota (deve notificar)
        turma.registrar_nota(aluno, avaliacao, 8.0)
        
        # Criar plano (deve notificar)
        plano = turma.criar_plano_acao(aluno, "Melhorar", 30)
        
        # Adicionar observer à meta
        meta = Meta("Média 8.0", 8.0, datetime.now() + timedelta(days=30))
        meta.adicionar_observer(email_notif)
        
        # Atingir meta (deve notificar)
        meta.atualizar_progresso(8.0)
        
        # Verificar que tudo funcionou sem erros
        assert len(turma.alunos) == 1
        assert plano is not None
        assert meta.verificar_conclusao()
        
        # Verificar que notificadores registraram os tipos corretos no histórico
        historico_email = email_notif.obter_historico()
        tipos_evento_email = [h['tipo_evento'] for h in historico_email]
        assert 'nota_registrada' in tipos_evento_email
        assert 'plano_acao_criado' in tipos_evento_email
        assert 'meta_atingida' in tipos_evento_email
        
        historico_push = push_notif.obter_historico()
        tipos_evento_push = [h['tipo_evento'] for h in historico_push]
        assert 'nota_registrada' in tipos_evento_push
        assert 'plano_acao_criado' in tipos_evento_push
        # push_notif não é observer de meta (apenas email_notif foi adicionado)
        assert 'meta_atingida' not in tipos_evento_push
