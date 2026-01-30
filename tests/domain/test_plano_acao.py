import pytest
from unittest.mock import Mock
from datetime import datetime, timedelta

from educalin.domain.plano_acao import (
    PlanoAcao, 
    StatusPlano,
    PlanoJaConcluidoException,
    TransicaoStatusInvalidaException, # Sem testes pra transição status?
    MaterialObrigatorioException
)


class TestPlanoAcaoInicializacao:
    """Testes de criação e inicialização do PlanoAcao"""

    @pytest.fixture
    def aluno_mock(self):
        """Fixture com mock de aluno"""
        aluno = Mock()
        aluno.matricula = "12345"
        aluno.nome = "Fulano de Tal da Silva"
        return aluno

    def test_plano_inicializacao_valida(self, aluno_mock):
        """Deve criar PlanoAcao com dados obrigatórios"""
        plano = PlanoAcao(
            aluno_alvo=aluno_mock,
            objetivo="Melhorar desempenho em álgebra",
            prazo_dias=30
        )

        assert plano.aluno_alvo == aluno_mock
        assert plano.objetivo == "Melhorar desempenho em álgebra"
        assert plano.status == StatusPlano.RASCUNHO
        assert plano.materiais == []
        assert isinstance(plano.data_criacao, datetime)
        assert plano.data_limite is not None
        assert plano.observacoes is None

    def test_plano_com_observacoes(self, aluno_mock):
        """Deve aceitar observações opcionais"""
        plano = PlanoAcao(
            aluno_alvo=aluno_mock,
            objetivo="Reforço em matemática",
            prazo_dias=15,
            observacoes="Foco em equações do 2º grau"
        )

        assert plano.observacoes == "Foco em equações do 2º grau"

    def test_plano_sem_aluno_deve_falhar(self):
        """Deve lançar ValueError se aluno não for fornecido"""
        with pytest.raises(ValueError, match="Aluno alvo é obrigatório"):
            PlanoAcao(
                aluno_alvo=None,
                objetivo="Teste",
                prazo_dias=30
            )

    def test_plano_sem_objetivo_deve_falhar(self, aluno_mock):
        """Deve lançar ValueError se objetivo não for fornecido"""
        with pytest.raises(ValueError, match="Objetivo não pode ser vazio"):
            PlanoAcao(
                aluno_alvo=aluno_mock,
                objetivo="",
                prazo_dias=30
            )

    def test_plano_prazo_invalido_deve_falhar(self, aluno_mock):
        """Deve lançar ValueError se prazo <= 0"""
        with pytest.raises(ValueError, match="Prazo deve ser maior que zero"):
            PlanoAcao(
                aluno_alvo=aluno_mock,
                objetivo="Teste",
                prazo_dias=0
            )

    def test_plano_gera_id_automaticamente(self, aluno_mock):
        """Deve gerar ID único automaticamente"""
        plano1 = PlanoAcao(aluno_mock, "Objetivo 1", 30)
        plano2 = PlanoAcao(aluno_mock, "Objetivo 2", 30)

        assert plano1.id != plano2.id
        assert plano1.id is not None


class TestPlanoAcaoComposicaoMateirais:
    """Testes de composição: PlanoAcao *-- MaterialEstudo"""
    
    @pytest.fixture
    def plano(self):
        """Fixture com PlanoAcao padrão"""
        aluno_mock = Mock()
        return PlanoAcao(aluno_mock, "Reforço matemática", 30)
    
    @pytest.fixture
    def material_pdf_mock(self):
        """Mock de MaterialPDF"""
        material = Mock()
        material.titulo = "Apostila de Álgebra"
        material.tipo = "pdf"
        return material
    
    @pytest.fixture
    def material_video_mock(self):
        """Mock de MaterialVideo"""
        material = Mock()
        material.titulo = "Vídeo sobre equações"
        material.tipo = "video"
        return material
    
    def test_adicionar_material_com_sucesso(self, plano, material_pdf_mock):
        """Deve adicionar material à composição"""
        resultado = plano.adicionar_material(material_pdf_mock)

        assert resultado is True
        assert len(plano.materiais) == 1
        assert material_pdf_mock in plano.materiais
        assert plano.total_materiais == 1

    def test_adicionar_multiplos_materiais(self, plano, material_pdf_mock, material_video_mock):
        """Deve permitir composição com múltiplos materiais"""
        plano.adicionar_material(material_pdf_mock)
        plano.adicionar_material(material_video_mock)

        assert plano.total_materiais == 1

    def test_nao_deve_adicionar_material_duplicado(self, plano, material_pdf_mock):
        """Deve ignorar tentativa de adicionar mesmo material duas vezes"""
        plano.adicionar_material(material_pdf_mock)
        resultado = plano.adicionar_material(material_pdf_mock)

        assert resultado is False
        assert len(plano.materiais) == 1

    def test_adicionar_material_invalido_deve_falhar(self, plano):
        """Deve lançar TypeError se não for MaterialEstudo"""
        with pytest.raises(TypeError, match="Esperado instância de MaterialEstudo"):
            plano.adicionar_material("não é material")

    def test_remover_material_existente(self, plano, material_pdf_mock):
        """Deve remover material da composição"""
        plano.adicionar_material(material_pdf_mock)

        resultado = plano.remover_material(material_pdf_mock)

        assert resultado is True
        assert len(plano.materiais) == 0

    def test_remover_material_inexistente(self, plano, material_pdf_mock):
        """Deve retornar False ao remover material que não existe"""
        resultado = plano.remover_material(material_pdf_mock)

        assert resultado is False

    def test_composicao_ciclo_vida_dependente(self, plano, material_pdf_mock):
        """Materiais devem ter ciclo de vida dependente do PlanoAcao"""
        plano.adicionar_material(material_pdf_mock)

        plano_id = plano.id
        del plano

        assert material_pdf_mock is not None


class TestPlanoAcaoGerenciamentoStatus:
    """Testes de transição de status"""

    @pytest.fixture
    def plano_com_material(self):
        """PlanoAcao com pelo menos 1 material"""
        aluno_mock = Mock()
        plano = PlanoAcao(aluno_mock, "Reforço", 30)

        material_mock = Mock()
        material_mock.titulo = "Material 1"
        plano.adicionar_material(material_mock)

        return plano
    
    def test_status_inicial_rascunho(self):
        """PlanoAcao deve iniciar com status RASCUNHO"""
        aluno_mock = Mock()
        plano = PlanoAcao(aluno_mock, "Teste", 30)

        assert plano.status == StatusPlano.RASCUNHO

    def test_enviar_plano_com_material(self, plano_com_material):
        """Deve permitir enviar plano que tem material"""
        plano_com_material.enviar()

        assert plano_com_material.status == StatusPlano.ENVIADO
        assert plano_com_material.data_envio is not None

    def test_enviar_plano_sem_material_deve_falhar(self):
        """Deve lançar exceção ao enviar plano sem materiais"""
        aluno_mock = Mock()
        plano = PlanoAcao(aluno_mock, "Teste", 30)

        with pytest.raises(MaterialObrigatorioException, match="pelo menos 1 material"):
            plano.enviar()

    def test_iniciar_plano_enviado(self, plano_com_material):
        """Deve permitir iniciar plano que está ENVIADO"""
        plano_com_material.enviar()
        plano_com_material.iniciar()

        assert plano_com_material.status == StatusPlano.EM_ANDAMENTO
        assert plano_com_material.data_inicio is not None

    def test_iniciar_plano_nao_enviado_deve_falhar(self, plano_com_material):
        """Não deve permitir iniciar plano que não foi enviado"""
        with pytest.raises():
            plano_com_material.iniciar(TansicaoStatusInvalidaException)

    def test_concluir_plano_em_andamento(self, plano_com_material):
        """Deve permitir concluir plano EM_ANDAMENTO"""
        plano_com_material.enviar()
        plano_com_material.iniciar()
        resultado = plano_com_material.concluir()

        assert plano_com_material.status == StatusPlano.CONCLUIDO
        assert plano_com_material.data_conclusao is not None

    def test_concluir_plano_enviado_direto(self, plano_com_material):
        """Deve permitir concluir plano ENVIADO (sem passar por EM_ANDAMENTO)"""
        plano_com_material.enviar()
        resultado = plano_com_material.concluir()

        assert plano_com_material.status == StatusPlano.CONCLUIDO
        assert plano_com_material.data_conclusao is not None # checar se será isso mesmo

    def test_cancelar_plano_nao_concluido(self, plano_com_material):
        """Deve permitir cancelar plano que não está concluido"""
        plano_com_material.cancelar(motivo="Aluno mudou de escola")

        assert plano_com_material.status == StatusPlano.CANCELADO
        assert plano_com_material.motivo_cancelamento == "Aluno mudou de escola"

    def test_nao_pode_modificar_plano_concluido(self, plano_com_material):
        """Não deve permitir adicionar material em plano concluído"""
        plano_com_material.enviar()
        plano_com_material.concluir()

        material_novo = Mock()
        
        with pytest.raises(PlanoJaConcluidoException):
            plano_com_material.adicionar_material(material_novo)

    def test_historico_status(self, plano_com_material):
        """Deve manter histórico de transições de status"""
        plano_com_material.enviar()
        plano_com_material.iniciar()

        historico = plano_com_material.historico_status

        assert len(historico) >= 3
        assert historico[0]['status'] == StatusPlano.RASCUNHO
        assert historico[1]['status'] == StatusPlano.ENVIADO
        assert historico[2]['status'] == StatusPlano.EM_ANDAMENTO


class TestPlanoAcaoObserverPatter:
    """Testes do padrão Observer (Subject)"""

    @pytest.fixture
    def plano(self):
        """Fixture com PlanoAcao padrão"""
        aluno_mock = Mock()
        return PlanoAcao(aluno_mock, "Teste", 30)
    
    @pytest.fixture
    def observer_mock(self):
        from educalin.domain.turma import Observer
        observer = Mock(spec=Observer)
        return observer
    
    def test_implementa_interface_subject(self, plano):
        """Deve implementar métodos do Subject"""
        assert hasattr(plano, 'adicionar_observer')
        assert hasattr(plano, 'remover_observer')
        assert hasattr(plano, 'notificar_observers')
    
    def test_adicionar_material_notifica_observers(self, plano, observer_mock):
        """Deve notificar ao adicionar material"""
        plano.adicionar_observer(observer_mock)

        material_mock = Mock()
        material_mock.titulo = "Material teste"

        plano.adicionar_material(material_mock)

        observer_mock.atualizar.assert_called_once()
        evento = observer_mock.atualizar.call_args[0][0]
        assert evento['evento'] == 'material_adicionado'

    def test_enviar_plano_notifica_observers(self, plano, observer_mock):
        """Deve notificar ao enviar plano"""
        plano.adicionar_observer(observer_mock)

        material_mock = Mock()
        plano.adicionar_material(material_mock)

        observer_mock.reset_mock()

        plano.enviar()

        observer_mock.atualizar.assert_called()
        evento = observer_mock.atualizar.call_args[0][0]
        assert evento['evento'] == "plano_enviado"

    def test_concluir_plano_notifica_observers(self, plano, observer_mock):
        """Deve notificar ao concluir plano"""
        plano.adicionar_observer(observer_mock)

        material_mock = Mock()
        plano.adicionar_material(material_mock)
        plano.enviar()

        observer_mock.reset_mock()

        plano.concluir()

        observer_mock.atualizar.assert_called()
        evento = observer_mock.atualizar.call_args[0][0]
        assert evento['evento'] == 'plano_concluido'


class TestPlanoAcaoMetodosUtilitarios:
    """Testes de métodos auxiliares"""

    @pytest.fixture
    def aluno_mock(self):
        """Fixture com mock de aluno"""
        aluno = Mock()
        aluno.matricula = "12345"
        aluno.nome = "Fulano de Tal da Silva"
        return aluno

    def test_esta_vencido_false(self, aluno_mock):
        """Plano dentro do prazo não deve estar vencido"""
        plano = PlanoAcao(aluno_mock, "Teste", prazo_dias=30)

        assert plano.esta_vencido() is False

    def test_esta_vencido_true(self, aluno_mock):
        """Plano fora do prazo deve estar vencido"""
        plano = PlanoAcao(aluno_mock, "Teste", prazo_dias=30)

        plano._data_limite = datetime.now() - timedelta(days=1)

        assert plano.esta_vencido() is True

    def test_dias_restantes(self, aluno_mock):
        """Deve calcular dias restantes corretamente"""
        plano = PlanoAcao(aluno_mock, "Teste", prazo_dias=7)

        dias = plano.dias_restantes()

        assert dias >= 6
        assert dias <= 7

    def test_progresso_percentual_sem_materiais(self, aluno_mock):
        """Progresso deve ser 0% sem materiais"""
        plano = PlanoAcao(aluno_mock, "Teste", 30)

        assert plano.calcular_progresso() == 0.0

    @pytest.mark.skip(reason="#BLOCKED: Depende da implementação de rastreamento")
    def test_progresso_percentual_com_materiais(self):
        """Deve calcular progresso baseado em materiais 'visualizado'"""
        # BLOCKED
        # Depende da implementação de rastreamento
        # Feito apenas estrutura
        pass

    def test_pode_ser_editado_rascunho(self, aluno_mock):
        """Plano RASCUNHO pode ser editado"""
        plano = PlanoAcao(aluno_mock, "Teste", 30)

        assert plano.pode_ser_editado() is True

    def test_nao_pode_ser_editado_concluido(self, aluno_mock):
        """Plano CONCLUIDO não pode ser editado"""
        material = Mock()
        plano = PlanoAcao(aluno_mock, "Teste", 30)
        
        plano.adicionar_material(material)
        plano.enviar()
        plano.concluir()

        assert plano.pode_ser_editado() is False


class TestPlanoAcaoMetodosEspeciais:
    """Testes de __repr__, __str__, __eq__"""

    def test_repr(self):
        """Deve retornar representação oficial"""
        aluno_mock = Mock()
        aluno_mock.matricula = "12345"
        
        plano = PlanoAcao(aluno_mock, "Reforço Álgebre", 30)

        repr_str = repr(plano)

        assert "PlanoAcao" in repr_str
        assert plano.id in repr_str

    def test_str(self):
        """Deve retornar representação amigável"""
        aluno_mock = Mock()
        aluno_mock.nome = "Fulano de Tal"

        plano = PlanoAcao(aluno_mock, "Reforço Álgebra", 30)

        str_repr = str(plano)

        assert "Plano de Ação" in str_repr
        assert "Fulano de Tal" in str_repr
        assert "Reforço Álgebra" in str_repr

    def test_igualdade_por_id(self):
        """Planos com mesmo ID devem ser iguais"""
        aluno_mock = Mock()

        plano1 = PlanoAcao(aluno_mock, "Teste 1", 30)
        plano2 = PlanoAcao(aluno_mock, "Teste 2", 30)

        plano2.__id = plano1.id

        assert plano1 == plano2