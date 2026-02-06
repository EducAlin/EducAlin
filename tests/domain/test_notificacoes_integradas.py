import pytest
from educalin.domain.aluno import Aluno
from educalin.domain.professor import Professor
from educalin.domain.coordenador import Coordenador


class TestNotificacoesAluno:
    """Testa integração de notificações com Aluno."""
    
    @pytest.fixture
    def aluno(self):
        """Fixture com um aluno."""
        return Aluno(
            nome="Maria Silva",
            email="maria@escola.com",
            senha="senha123",
            matricula="20241234"
        )
    
    def test_aluno_recebe_notificacao(self, aluno):
        """Aluno deve receber notificações corretamente."""
        notif_id = aluno.receber_notificacao("Nova nota disponível", tipo="info")
        
        assert notif_id is not None
        assert aluno.total_notificacoes_nao_lidas == 1
        
        notifs = aluno.obter_notificacoes()
        assert len(notifs) == 1
        assert notifs[0]['mensagem'] == "Nova nota disponível"
    
    def test_aluno_marca_notificacao_como_lida(self, aluno):
        """Aluno deve marcar notificação como lida."""
        notif_id = aluno.receber_notificacao("Material novo", tipo="aviso")
        
        aluno.marcar_como_lida(notif_id)
        
        assert aluno.total_notificacoes_nao_lidas == 0
    
    def test_aluno_configura_preferencias(self, aluno):
        """Aluno deve configurar preferências de notificação."""
        aluno.configurar_preferencias(email=False, sms=True)
        
        prefs = aluno.obter_preferencias()
        assert prefs['email'] is False
        assert prefs['sms'] is True
        assert prefs['push'] is True  # Mantém o padrão


class TestNotificacoesProfessor:
    """Testa integração de notificações com Professor."""
    
    @pytest.fixture
    def professor(self):
        """Fixture com um professor."""
        return Professor(
            nome="João Santos",
            email="joao@escola.com",
            senha="senha456",
            registro_funcional="PROF001"
        )
    
    def test_professor_recebe_notificacao(self, professor):
        """Professor deve receber notificações corretamente."""
        notif_id = professor.receber_notificacao(
            "Novo aluno na turma",
            tipo="info",
            dados_adicionais={'turma': 'MAT101'}
        )
        
        assert notif_id is not None
        assert professor.total_notificacoes_nao_lidas == 1
        
        notifs = professor.obter_notificacoes()
        assert notifs[0]['dados']['turma'] == 'MAT101'
    
    def test_professor_limpa_notificacoes_lidas(self, professor):
        """Professor deve limpar notificações lidas."""
        id1 = professor.receber_notificacao("Notif 1", tipo="info")
        id2 = professor.receber_notificacao("Notif 2", tipo="info")
        id3 = professor.receber_notificacao("Notif 3", tipo="info")
        
        # Marca 2 como lidas
        professor.marcar_como_lida(id1)
        professor.marcar_como_lida(id2)
        
        # Limpa apenas lidas
        removidas = professor.limpar_notificacoes(apenas_lidas=True)
        
        assert removidas == 2
        assert len(professor.obter_notificacoes()) == 1
    
    def test_professor_marca_todas_como_lidas(self, professor):
        """Professor deve marcar todas as notificações como lidas."""
        professor.receber_notificacao("Notif 1", tipo="info")
        professor.receber_notificacao("Notif 2", tipo="aviso")
        professor.receber_notificacao("Notif 3", tipo="urgente")
        
        marcadas = professor.marcar_todas_como_lidas()
        
        assert marcadas == 3
        assert professor.total_notificacoes_nao_lidas == 0


class TestNotificacoesCoordenador:
    """Testa integração de notificações com Coordenador."""
    
    @pytest.fixture
    def coordenador(self):
        """Fixture com um coordenador."""
        return Coordenador(
            nome="Ana Paula",
            email="ana@escola.com",
            senha="senha789"
        )
    
    def test_coordenador_recebe_notificacao(self, coordenador):
        """Coordenador deve receber notificações corretamente."""
        notif_id = coordenador.receber_notificacao(
            "Relatório pronto",
            tipo="sucesso"
        )
        
        assert notif_id is not None
        assert coordenador.total_notificacoes_nao_lidas == 1
    
    def test_coordenador_obter_apenas_nao_lidas(self, coordenador):
        """Coordenador deve filtrar notificações não lidas."""
        id1 = coordenador.receber_notificacao("Notif 1", tipo="info")
        coordenador.receber_notificacao("Notif 2", tipo="aviso")
        
        # Marca primeira como lida
        coordenador.marcar_como_lida(id1)
        
        nao_lidas = coordenador.obter_notificacoes(apenas_nao_lidas=True)
        
        assert len(nao_lidas) == 1
        assert nao_lidas[0]['mensagem'] == "Notif 2"
    
    def test_coordenador_notificacao_urgente(self, coordenador):
        """Coordenador deve receber notificações urgentes."""
        notif_id = coordenador.receber_notificacao(
            "Problema crítico detectado",
            tipo="urgente",
            dados_adicionais={'prioridade': 'alta'}
        )
        
        notifs = coordenador.obter_notificacoes()
        
        assert notifs[0]['tipo'] == "urgente"
        assert notifs[0]['dados']['prioridade'] == 'alta'


class TestValidacaoTiposNotificacao:
    """Testa validação de tipos em todas as classes."""
    
    def test_aluno_rejeita_tipo_invalido(self):
        """Aluno deve rejeitar tipo de notificação inválido."""
        aluno = Aluno("Ana", "ana@email.com", "senha", "123")
        
        with pytest.raises(ValueError, match="Tipo inválido"):
            aluno.receber_notificacao("Teste", tipo="tipo_inexistente")
    
    def test_professor_rejeita_tipo_invalido(self):
        """Professor deve rejeitar tipo de notificação inválido."""
        prof = Professor("João", "joao@email.com", "senha", "PROF001")
        
        with pytest.raises(ValueError, match="Tipo inválido"):
            prof.receber_notificacao("Teste", tipo="erro")
    
    def test_coordenador_rejeita_tipo_invalido(self):
        """Coordenador deve rejeitar tipo de notificação inválido."""
        coord = Coordenador("Maria", "maria@email.com", "senha")
        
        with pytest.raises(ValueError, match="Tipo inválido"):
            coord.receber_notificacao("Teste", tipo="warning")
