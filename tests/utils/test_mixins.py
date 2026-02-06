import pytest
import bcrypt
from educalin.utils.mixins import AutenticavelMixin, NotificavelMixin
from educalin.domain.professor import Professor


# Classe auxiliar

class UsuarioMockComMixins(AutenticavelMixin, NotificavelMixin):
    """Classe mock que usa os mixins para testes.
    
    Simula a estrutura de Usuario com propriedades email e senha.
    """

    def __init__(self, nome: str, email: str, senha: str):
        # Chama super().__init__() para inicializar NotificavelMixin
        super().__init__()
        
        self._nome = nome
        self._email = email
        # Armazena a senha como hash bcrypt
        senha_bytes = senha.encode('utf-8')
        salt = bcrypt.gensalt()
        hash_senha = bcrypt.hashpw(senha_bytes, salt)
        self._senha = hash_senha

    @property
    def email(self) -> str:
        """Retorna o email do usuário."""
        return self._email

    @property
    def senha(self) -> bytes:
        """Retorna o hash da senha."""
        return self._senha

    @senha.setter
    def senha(self, nova_senha: str):
        """Define uma nova senha, gerando o hash."""
        senha_bytes = nova_senha.encode('utf-8')
        salt = bcrypt.gensalt()
        self._senha = bcrypt.hashpw(senha_bytes, salt)


# Testes AutenticavelMixin

class TestAutenticavelMixin:
    """Testes do AutenticavelMixin.
    
    A issue especifica:
    - validar_senha(senha) -> Não implementado, usa validar_credenciais(email, senha)
    - alterar_senha(nova_senha) -> Não implementado, usa resetar_senha(nova_senha)
    
    Os testes cobrem a implementação atual do mixin.
    """

    @pytest.fixture
    def usuario(self):
        """Fixture com usuario mock."""
        return UsuarioMockComMixins("Joao", "joao@email.com", "senha123")

    def test_validar_credenciais_correta(self, usuario):
        """Deve retornar True para email e senha corretos."""
        assert usuario.validar_credenciais("joao@email.com", "senha123") is True

    def test_validar_credenciais_senha_incorreta(self, usuario):
        """Deve retornar False para senha incorreta."""
        assert usuario.validar_credenciais("joao@email.com", "senha_errada") is False

    def test_validar_credenciais_email_incorreto(self, usuario):
        """Deve retornar False para email incorreto."""
        assert usuario.validar_credenciais("outro@email.com", "senha123") is False

    def test_resetar_senha_com_sucesso(self, usuario):
        """Deve alterar a senha do usuário."""
        usuario.resetar_senha("nova_senha_456")
        
        assert usuario.validar_credenciais("joao@email.com", "nova_senha_456") is True
        assert usuario.validar_credenciais("joao@email.com", "senha123") is False

    def test_hash_senha_gera_hash_valido(self, usuario):
        """Deve gerar um hash bcrypt válido."""
        senha_texto = "minha_senha_teste"
        hash_gerado = usuario._hash_senha(senha_texto)
        
        assert isinstance(hash_gerado, bytes)
        assert bcrypt.checkpw(senha_texto.encode('utf-8'), hash_gerado)

    def test_hash_senha_gera_hashes_diferentes(self, usuario):
        """Deve gerar hashes diferentes para a mesma senha (devido ao salt)."""
        senha_texto = "mesma_senha"
        hash1 = usuario._hash_senha(senha_texto)
        hash2 = usuario._hash_senha(senha_texto)
        
        # Hashes diferentes mas ambos válidos
        assert hash1 != hash2
        assert bcrypt.checkpw(senha_texto.encode('utf-8'), hash1)
        assert bcrypt.checkpw(senha_texto.encode('utf-8'), hash2)

# Testes NotificavelMixin

class TestNotificavelMixin:
    """Testes do NotificavelMixin"""
    
    @pytest.fixture
    def usuario(self):
        """Fixture com usuário mock"""
        return UsuarioMockComMixins("Maria", "maria@email.com", "senha123")
    
    def test_inicializacao_notificacoes_vazia(self, usuario):
        """Deve inicializar com lista vazia de notificações"""
        assert usuario.obter_notificacoes() == []
        assert usuario.total_notificacoes_nao_lidas == 0
    
    def test_receber_notificacao(self, usuario):
        """Deve armazenar notificação corretamente"""
        usuario.receber_notificacao("Teste de notificação", tipo="info")
        
        notifs = usuario.obter_notificacoes()
        
        assert len(notifs) == 1
        assert notifs[0]['mensagem'] == "Teste de notificação"
        assert notifs[0]['tipo'] == "info"
        assert notifs[0]['lida'] is False
    
    def test_receber_notificacao_tipo_invalido(self, usuario):
        """Deve lançar erro para tipo inválido"""
        with pytest.raises(ValueError, match="Tipo inválido. Use:"):
            usuario.receber_notificacao("Teste", tipo="invalido")
    
    def test_obter_apenas_nao_lidas(self, usuario):
        """Deve filtrar apenas notificações não lidas"""
        usuario.receber_notificacao("Notif 1", tipo="info")
        usuario.receber_notificacao("Notif 2", tipo="aviso")
        
        # Marcar primeira como lida
        notifs = usuario.obter_notificacoes()
        usuario.marcar_como_lida(notifs[0]['id'])
        
        nao_lidas = usuario.obter_notificacoes(apenas_nao_lidas=True)
        
        assert len(nao_lidas) == 1
        assert nao_lidas[0]['mensagem'] == "Notif 2"
    
    def test_marcar_como_lida(self, usuario):
        """Deve marcar notificação específica como lida"""
        usuario.receber_notificacao("Teste", tipo="info")
        
        notifs = usuario.obter_notificacoes()
        notif_id = notifs[0]['id']
        
        resultado = usuario.marcar_como_lida(notif_id)
        
        assert resultado is True
        assert usuario.obter_notificacoes()[0]['lida'] is True
    
    def test_marcar_todas_como_lidas(self, usuario):
        """Deve marcar todas as notificações como lidas"""
        usuario.receber_notificacao("Notif 1", tipo="info")
        usuario.receber_notificacao("Notif 2", tipo="aviso")
        usuario.receber_notificacao("Notif 3", tipo="urgente")
        
        marcadas = usuario.marcar_todas_como_lidas()
        
        assert marcadas == 3
        assert usuario.total_notificacoes_nao_lidas == 0
    
    def test_configurar_preferencias(self, usuario):
        """Deve atualizar preferências de canal"""
        usuario.configurar_preferencias(email=False, push=True, sms=True)
        
        prefs = usuario.obter_preferencias()
        
        assert prefs['email'] is False
        assert prefs['push'] is True
        assert prefs['sms'] is True
    
    def test_limpar_notificacoes_lidas(self, usuario):
        """Deve remover apenas notificações lidas"""
        usuario.receber_notificacao("Notif 1", tipo="info")
        usuario.receber_notificacao("Notif 2", tipo="info")
        usuario.receber_notificacao("Notif 3", tipo="info")
        
        # Marcar 2 como lidas
        notifs = usuario.obter_notificacoes()
        usuario.marcar_como_lida(notifs[0]['id'])
        usuario.marcar_como_lida(notifs[1]['id'])
        
        removidas = usuario.limpar_notificacoes(apenas_lidas=True)
        
        assert removidas == 2
        assert len(usuario.obter_notificacoes()) == 1
    
    def test_limpar_todas_notificacoes(self, usuario):
        """Deve remover todas as notificações"""
        usuario.receber_notificacao("Notif 1", tipo="info")
        usuario.receber_notificacao("Notif 2", tipo="info")
        
        removidas = usuario.limpar_notificacoes(apenas_lidas=False)
        
        assert removidas == 2
        assert len(usuario.obter_notificacoes()) == 0

def test_integracao_professor_com_notificacoes():
    """Testa se Professor inicializa NotificavelMixin corretamente."""
    prof = Professor(
        nome="João Silva",
        email="joao@escola.com",
        senha="senha123",
        registro_funcional="PROF001"
    )
    
    # ✅ Deve funcionar sem AttributeError
    prof.receber_notificacao("Nova turma atribuída", tipo="info")
    
    notifs = prof.obter_notificacoes()
    assert len(notifs) == 1
    assert notifs[0]['mensagem'] == "Nova turma atribuída"
    assert prof.total_notificacoes_nao_lidas == 1
