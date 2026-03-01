"""
Testes do módulo de notificadores implementando o padrão Observer.

Testa as implementações concretas do padrão Observer (NotificadorEmail e NotificadorPush)
e sua integração com a classe Turma (Subject).
"""

import pytest
from datetime import datetime
from educalin.services.notificador import NotificadorEmail, NotificadorPush
from educalin.domain.turma import Turma, Observer
from educalin.domain.professor import Professor


class TestNotificadorEmail:
    """Testes para a classe NotificadorEmail"""

    def test_notificador_email_herda_de_observer(self):
        """Verifica se NotificadorEmail implementa a interface Observer"""
        notificador = NotificadorEmail("teste@example.com")
        assert isinstance(notificador, Observer)

    def test_notificador_email_inicializacao_valida(self):
        """Deve criar notificador com email válido"""
        email = "usuario@example.com"
        notificador = NotificadorEmail(email)
        assert notificador._email_destinatario == email
        assert notificador._notificacoes_enviadas == []

    def test_notificador_email_validacao_email_vazio(self):
        """Deve lançar ValueError se email for vazio"""
        with pytest.raises(ValueError, match="Email do destinatário não pode ser vazio"):
            NotificadorEmail("")

    def test_notificador_email_validacao_email_whitespace(self):
        """Deve lançar ValueError se email for apenas whitespace"""
        with pytest.raises(ValueError, match="Email do destinatário não pode ser vazio"):
            NotificadorEmail("   ")

    def test_notificador_email_limpa_whitespace(self):
        """Deve remover espaços em branco do email"""
        email_com_espacos = "  usuario@example.com  "
        notificador = NotificadorEmail(email_com_espacos)
        assert notificador._email_destinatario == "usuario@example.com"

    def test_atualizar_evento_valido(self, capsys):
        """Deve processar um evento válido"""
        notificador = NotificadorEmail("teste@example.com")
        evento = {
            'tipo': 'nota_registrada',
            'descricao': 'Nota foi registrada',
            'timestamp': datetime.now(),
            'turma': 'ES-2025.2',
            'dados_adicionais': {'aluno': 'João', 'nota': 9.5}
        }

        notificador.atualizar(evento)

        captured = capsys.readouterr()
        assert "EMAIL ENVIADO" in captured.out
        assert "teste@example.com" in captured.out

    def test_atualizar_evento_tipo_invalido(self):
        """Deve lançar TypeError se evento não for dicionário"""
        notificador = NotificadorEmail("teste@example.com")
        
        with pytest.raises(TypeError):
            notificador.atualizar("não é um dicionário")

    def test_atualizar_evento_minimo(self, capsys):
        """Deve processar evento com dados mínimos"""
        notificador = NotificadorEmail("teste@example.com")
        evento = {}  # Evento vazio, vai usar defaults

        notificador.atualizar(evento)

        captured = capsys.readouterr()
        assert "EMAIL ENVIADO" in captured.out

    def test_construir_corpo_email(self):
        """Deve construir corpo do email adequadamente"""
        notificador = NotificadorEmail("teste@example.com")
        timestamp = datetime(2025, 3, 1, 14, 30, 0)
        corpo = notificador._construir_corpo_email(
            "nota_registrada",
            "Uma nota foi registrada",
            timestamp,
            "ES-2025.2",
            {"aluno": "João", "nota": 9.5}
        )

        assert "nota_registrada" in corpo
        assert "Uma nota foi registrada" in corpo
        assert "01/03/2025 14:30:00" in corpo
        assert "ES-2025.2" in corpo
        assert "João" in corpo
        assert "9.5" in corpo

    def test_registrar_notificacao_enviada(self):
        """Deve registrar notificações no histórico"""
        notificador = NotificadorEmail("teste@example.com")
        timestamp = datetime.now()

        notificador._registrar_notificacao_enviada(
            'email',
            'teste@example.com',
            'nota_registrada',
            timestamp
        )

        historico = notificador.obter_historico()
        assert len(historico) == 1
        assert historico[0]['canal'] == 'email'
        assert historico[0]['destinatario'] == 'teste@example.com'
        assert historico[0]['tipo_evento'] == 'nota_registrada'
        assert historico[0]['status'] == 'enviado'

    def test_obter_historico(self):
        """Deve retornar cópia do histórico"""
        notificador = NotificadorEmail("teste@example.com")
        timestamp = datetime.now()

        notificador._registrar_notificacao_enviada('email', 'teste@example.com', 'evento1', timestamp)
        notificador._registrar_notificacao_enviada('email', 'teste@example.com', 'evento2', timestamp)

        historico = notificador.obter_historico()
        assert len(historico) == 2

        # Verificar que é uma cópia
        historico.append({'fake': 'registro'})
        assert len(notificador.obter_historico()) == 2


class TestNotificadorPush:
    """Testes para a classe NotificadorPush"""

    def test_notificador_push_herda_de_observer(self):
        """Verifica se NotificadorPush implementa a interface Observer"""
        notificador = NotificadorPush("usuario_123")
        assert isinstance(notificador, Observer)

    def test_notificador_push_inicializacao_valida(self):
        """Deve criar notificador com usuario_id válido"""
        usuario_id = "usuario_123"
        notificador = NotificadorPush(usuario_id)
        assert notificador._usuario_id == usuario_id
        assert notificador._dispositivos == []
        assert notificador._notificacoes_enviadas == []

    def test_notificador_push_inicializacao_com_dispositivos(self):
        """Deve inicializar com dispositivos"""
        usuario_id = "usuario_123"
        dispositivos = ["device_1", "device_2"]
        notificador = NotificadorPush(usuario_id, dispositivos)
        assert notificador._dispositivos == dispositivos

    def test_notificador_push_validacao_usuario_vazio(self):
        """Deve lançar ValueError se usuario_id for vazio"""
        with pytest.raises(ValueError, match="ID do usuário não pode ser vazio"):
            NotificadorPush("")

    def test_notificador_push_validacao_usuario_whitespace(self):
        """Deve lançar ValueError se usuario_id for apenas whitespace"""
        with pytest.raises(ValueError, match="ID do usuário não pode ser vazio"):
            NotificadorPush("   ")

    def test_notificador_push_limpa_whitespace(self):
        """Deve remover espaços em branco do usuario_id"""
        usuario_com_espacos = "  usuario_123  "
        notificador = NotificadorPush(usuario_com_espacos)
        assert notificador._usuario_id == "usuario_123"

    def test_registrar_dispositivo_valido(self):
        """Deve registrar um dispositivo"""
        notificador = NotificadorPush("usuario_123")
        notificador.registrar_dispositivo("device_token_123")
        
        assert "device_token_123" in notificador._dispositivos

    def test_registrar_dispositivo_duplicado(self):
        """Não deve registrar dispositivo duplicado"""
        notificador = NotificadorPush("usuario_123")
        notificador.registrar_dispositivo("device_token_123")
        notificador.registrar_dispositivo("device_token_123")
        
        assert notificador._dispositivos.count("device_token_123") == 1

    def test_registrar_dispositivo_vazio(self):
        """Deve lançar ValueError para dispositivo vazio"""
        notificador = NotificadorPush("usuario_123")
        
        with pytest.raises(ValueError, match="ID do dispositivo não pode ser vazio"):
            notificador.registrar_dispositivo("")

    def test_registrar_dispositivo_whitespace(self):
        """Deve lançar ValueError para dispositivo com apenas whitespace"""
        notificador = NotificadorPush("usuario_123")
        
        with pytest.raises(ValueError, match="ID do dispositivo não pode ser vazio"):
            notificador.registrar_dispositivo("   ")

    def test_desregistrar_dispositivo(self):
        """Deve remover um dispositivo da lista"""
        notificador = NotificadorPush("usuario_123", ["device_1", "device_2"])
        notificador.desregistrar_dispositivo("device_1")
        
        assert "device_1" not in notificador._dispositivos
        assert "device_2" in notificador._dispositivos

    def test_desregistrar_dispositivo_inexistente(self):
        """Deve silenciosamente ignorar remoção de dispositivo inexistente"""
        notificador = NotificadorPush("usuario_123", ["device_1"])
        notificador.desregistrar_dispositivo("device_inexistente")  # Não deve lançar erro
        
        assert "device_1" in notificador._dispositivos

    def test_obter_dispositivos_registrados(self):
        """Deve retornar cópia da lista de dispositivos"""
        dispositivos = ["device_1", "device_2"]
        notificador = NotificadorPush("usuario_123", dispositivos)
        
        copia = notificador.obter_dispositivos_registrados()
        assert copia == dispositivos
        
        # Verificar que é uma cópia
        copia.append("device_3")
        assert len(notificador.obter_dispositivos_registrados()) == 2

    def test_atualizar_evento_valido(self, capsys):
        """Deve processar e enviar notificação push para dispositivos registrados"""
        notificador = NotificadorPush("usuario_123", ["device_1", "device_2"])
        evento = {
            'tipo': 'nota_registrada',
            'descricao': 'Nota foi registrada',
            'timestamp': datetime.now(),
            'turma': 'ES-2025.2',
            'dados_adicionais': {'aluno': 'João', 'nota': 9.5}
        }

        notificador.atualizar(evento)

        captured = capsys.readouterr()
        assert "PUSH ENVIADO" in captured.out
        assert "usuario_123" in captured.out
        assert captured.out.count("PUSH ENVIADO") == 2  # Uma para cada dispositivo

    def test_atualizar_sem_dispositivos(self, capsys):
        """Deve informar quando não há dispositivos registrados"""
        notificador = NotificadorPush("usuario_123")  # Sem dispositivos
        evento = {'tipo': 'evento_teste', 'descricao': 'Teste'}

        notificador.atualizar(evento)

        captured = capsys.readouterr()
        assert "Nenhum dispositivo registrado" in captured.out

    def test_atualizar_evento_tipo_invalido(self):
        """Deve lançar TypeError se evento não for dicionário"""
        notificador = NotificadorPush("usuario_123", ["device_1"])
        
        with pytest.raises(TypeError):
            notificador.atualizar("não é um dicionário")

    def test_construir_payload_push(self):
        """Deve construir payload do push adequadamente"""
        notificador = NotificadorPush("usuario_123")
        timestamp = datetime(2025, 3, 1, 14, 30, 0)
        payload = notificador._construir_payload_push(
            "nota_registrada",
            "Uma nota foi registrada",
            timestamp,
            "ES-2025.2",
            {"aluno": "João", "nota": 9.5}
        )

        assert payload['titulo'] == "EducAlin - nota_registrada"
        assert payload['mensagem'] == "Uma nota foi registrada"
        assert payload['tipo'] == "nota_registrada"
        assert payload['turma'] == "ES-2025.2"
        assert payload['dados'] == {"aluno": "João", "nota": 9.5}
        assert 'timestamp' in payload

    def test_registrar_notificacao_enviada(self):
        """Deve registrar notificações no histórico"""
        notificador = NotificadorPush("usuario_123")
        timestamp = datetime.now()

        notificador._registrar_notificacao_enviada(
            'push',
            'device_token_123',
            'nota_registrada',
            timestamp
        )

        historico = notificador.obter_historico()
        assert len(historico) == 1
        assert historico[0]['canal'] == 'push'
        assert historico[0]['dispositivo_id'] == 'device_token_123'
        assert historico[0]['tipo_evento'] == 'nota_registrada'
        assert historico[0]['status'] == 'enviado'

    def test_obter_historico(self):
        """Deve retornar cópia do histórico"""
        notificador = NotificadorPush("usuario_123", ["device_1"])
        timestamp = datetime.now()

        notificador._registrar_notificacao_enviada('push', 'device_1', 'evento1', timestamp)
        notificador._registrar_notificacao_enviada('push', 'device_1', 'evento2', timestamp)

        historico = notificador.obter_historico()
        assert len(historico) == 2

        # Verificar que é uma cópia
        historico.append({'fake': 'registro'})
        assert len(notificador.obter_historico()) == 2


class TestObserverPatternIntegracao:
    """Testes de integração do padrão Observer com Turma"""

    @pytest.fixture
    def turma(self):
        """Cria uma turma para testes"""
        professor = Professor("João Professor", "joao@example.com", "senha123", "prof123")
        return Turma("ES-2025.2", "Engenharia de Software", "2025.2", professor)

    def test_turma_adiciona_notificador_email(self, turma):
        """Turma deve adicionar NotificadorEmail como observer"""
        notificador = NotificadorEmail("admin@example.com")
        turma.adicionar_observer(notificador)
        
        assert notificador in turma._observers

    def test_turma_adiciona_notificador_push(self, turma):
        """Turma deve adicionar NotificadorPush como observer"""
        notificador = NotificadorPush("usuario_123", ["device_1"])
        turma.adicionar_observer(notificador)
        
        assert notificador in turma._observers

    def test_turma_adiciona_multiplos_observers(self, turma):
        """Turma deve adicionar múltiplos observers"""
        email_notificador = NotificadorEmail("admin@example.com")
        push_notificador = NotificadorPush("usuario_123", ["device_1"])
        
        turma.adicionar_observer(email_notificador)
        turma.adicionar_observer(push_notificador)
        
        assert len(turma._observers) == 2
        assert email_notificador in turma._observers
        assert push_notificador in turma._observers

    def test_turma_notifica_observers(self, turma, capsys):
        """Turma deve notificar os observers quando um evento ocorre"""
        email_notificador = NotificadorEmail("admin@example.com")
        turma.adicionar_observer(email_notificador)
        
        evento = {
            'tipo': 'turma_criada',
            'descricao': 'Turma foi criada',
            'timestamp': datetime.now()
        }
        
        turma.notificar_observers(evento)
        
        captured = capsys.readouterr()
        assert "EMAIL ENVIADO" in captured.out

    def test_turma_remove_observer(self, turma):
        """Turma deve remover um observer da lista"""
        notificador = NotificadorEmail("admin@example.com")
        turma.adicionar_observer(notificador)
        turma.remover_observer(notificador)
        
        assert notificador not in turma._observers

    def test_observer_removido_nao_recebe_notificacoes(self, turma, capsys):
        """Observer removido não deve receber notificações"""
        notificador = NotificadorEmail("admin@example.com")
        turma.adicionar_observer(notificador)
        turma.remover_observer(notificador)
        
        evento = {'tipo': 'teste', 'descricao': 'Teste'}
        turma.notificar_observers(evento)
        
        captured = capsys.readouterr()
        assert "EMAIL ENVIADO" not in captured.out
