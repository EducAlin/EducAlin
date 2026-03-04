"""
Testes do módulo de notificadores implementando o padrão Observer.

Testa as implementações concretas do padrão Observer (NotificadorEmail e NotificadorPush)
e sua integração com a classe Turma (Subject).
"""

import pytest
from datetime import datetime
from unittest.mock import Mock
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
        """Deve processar um evento válido com chave 'evento' (payload real do domínio)"""
        notificador = NotificadorEmail("teste@example.com")
        evento = {
            'evento': 'nota_registrada',
            'descricao': 'Nota foi registrada',
            'timestamp': datetime.now(),
            'turma': 'ES-2025.2',
            'dados_adicionais': {'aluno': 'João', 'nota': 9.5}
        }

        notificador.atualizar(evento)

        captured = capsys.readouterr()
        assert "EMAIL ENVIADO" in captured.out
        assert "teste@example.com" in captured.out

    def test_atualizar_evento_valido_chave_tipo(self, capsys):
        """Deve processar um evento válido com chave 'tipo' (compatibilidade legada)"""
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
        """Deve processar e enviar notificação push com chave 'evento' (payload real do domínio)"""
        notificador = NotificadorPush("usuario_123", ["device_1", "device_2"])
        evento = {
            'evento': 'nota_registrada',
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

    def test_atualizar_evento_valido_chave_tipo(self, capsys):
        """Deve processar evento push com chave 'tipo' (compatibilidade legada)"""
        notificador = NotificadorPush("usuario_123", ["device_1"])
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


# =================================
# Testes com Mocks
# =================================

class TestNotificadorEmailComMocks:
    """Testes do NotificadorEmail usando mocks para validar comportamento sem enviar emails reais"""

    def test_email_notificador_chama_enviar_email(self):
        """Deve chamar _enviar_email quando evento é recebido"""
        notificador = NotificadorEmail("test@example.com")
        
        # Mockar o método _enviar_email
        notificador._enviar_email = Mock()
        
        evento = {
            'tipo': 'nota_registrada',
            'descricao': 'Nota foi registrada',
            'timestamp': datetime.now()
        }
        
        notificador.atualizar(evento)
        
        # Verificar que _enviar_email foi chamado
        assert notificador._enviar_email.called
        assert notificador._enviar_email.call_count == 1
        
        # Verificar argumentos passados
        call_args = notificador._enviar_email.call_args
        assert '[EducAlin]' in call_args[0][0]  # assunto
        assert 'nota_registrada' in call_args[0][0]

    def test_email_notificador_registra_no_historico(self):
        """Deve registrar no histórico quando evento é processado"""
        notificador = NotificadorEmail("test@example.com")
        notificador._enviar_email = Mock()
        
        evento = {
            'tipo': 'nota_registrada',
            'descricao': 'Nota foi registrada',
            'timestamp': datetime.now(),
            'turma': 'ES-2025.2',
            'dados_adicionais': {'aluno': 'João'}
        }
        
        notificador.atualizar(evento)
        
        # Verificar histórico
        historico = notificador.obter_historico()
        assert len(historico) > 0
        assert historico[0]['canal'] == 'email'
        assert historico[0]['tipo_evento'] == 'nota_registrada'
        assert historico[0]['status'] == 'enviado'

    def test_email_notificador_corpo_bem_formatado(self):
        """Deve construir corpo do email com informações corretas"""
        notificador = NotificadorEmail("test@example.com")
        notificador._enviar_email = Mock()
        
        evento = {
            'tipo': 'nota_registrada',
            'descricao': 'Nota 9.5 registrada para João',
            'timestamp': datetime(2025, 3, 1, 10, 30),
            'turma': 'ES-2025.2',
            'dados_adicionais': {
                'aluno': 'João Silva',
                'nota': 9.5,
                'avaliacao': 'Prova 1'
            }
        }
        
        notificador.atualizar(evento)
        
        # Obter o corpo que foi passado para _enviar_email
        corpo = notificador._enviar_email.call_args[0][1]
        
        assert 'nota_registrada' in corpo
        assert 'João Silva' in corpo
        assert '9.5' in corpo
        assert 'Prova 1' in corpo

    def test_email_notificador_multiplos_eventos(self):
        """Deve processar múltiplos eventos mantendo histórico"""
        notificador = NotificadorEmail("test@example.com")
        notificador._enviar_email = Mock()
        
        evento1 = {'tipo': 'evento1', 'descricao': 'Evento 1'}
        evento2 = {'tipo': 'evento2', 'descricao': 'Evento 2'}
        evento3 = {'tipo': 'evento3', 'descricao': 'Evento 3'}
        
        notificador.atualizar(evento1)
        notificador.atualizar(evento2)
        notificador.atualizar(evento3)
        
        # Verificar que _enviar_email foi chamado 3 vezes
        assert notificador._enviar_email.call_count == 3
        
        # Verificar histórico
        historico = notificador.obter_historico()
        assert len(historico) == 3
        assert historico[0]['tipo_evento'] == 'evento1'
        assert historico[1]['tipo_evento'] == 'evento2'
        assert historico[2]['tipo_evento'] == 'evento3'


class TestNotificadorPushComMocks:
    """Testes do NotificadorPush usando mocks para validar comportamento sem enviar push real"""

    def test_push_notificador_chama_enviar_push(self):
        """Deve chamar _enviar_push para cada dispositivo"""
        notificador = NotificadorPush("usuario_123", ["device_1", "device_2"])
        
        # Mockar o método _enviar_push
        notificador._enviar_push = Mock()
        
        evento = {
            'tipo': 'nota_registrada',
            'descricao': 'Nota foi registrada',
            'timestamp': datetime.now()
        }
        
        notificador.atualizar(evento)
        
        # Verificar que _enviar_push foi chamado para cada dispositivo
        assert notificador._enviar_push.called
        assert notificador._enviar_push.call_count == 2
        
        # Verificar que foi chamado com os IDs corretos
        calls = notificador._enviar_push.call_args_list
        assert calls[0][0][0] == "device_1"
        assert calls[1][0][0] == "device_2"

    def test_push_notificador_payload_estruturado(self):
        """Deve construir payload corretamente"""
        notificador = NotificadorPush("usuario_123", ["device_1"])
        notificador._enviar_push = Mock()
        
        evento = {
            'tipo': 'nota_registrada',
            'descricao': 'Nota 8.5 registrada',
            'timestamp': datetime.now(),
            'turma': 'ES-2025.2',
            'dados_adicionais': {'aluno': 'Maria', 'nota': 8.5}
        }
        
        notificador.atualizar(evento)
        
        # Obter o payload que foi passado
        payload = notificador._enviar_push.call_args[0][1]
        
        assert payload['titulo'] == 'EducAlin - nota_registrada'
        assert payload['mensagem'] == 'Nota 8.5 registrada'
        assert payload['tipo'] == 'nota_registrada'
        assert payload['turma'] == 'ES-2025.2'
        assert 'aluno' in payload['dados']
        assert 'nota' in payload['dados']

    def test_push_notificador_sem_dispositivos(self):
        """Não deve enviar push se não há dispositivos registrados"""
        notificador = NotificadorPush("usuario_123")  # Sem dispositivos
        notificador._enviar_push = Mock()
        
        evento = {'tipo': 'evento', 'descricao': 'Teste'}
        
        notificador.atualizar(evento)
        
        # Verificar que _enviar_push NÃO foi chamado
        assert not notificador._enviar_push.called

    def test_push_notificador_registra_historico(self):
        """Deve registrar cada envio no histórico"""
        notificador = NotificadorPush("usuario_123", ["device_1", "device_2", "device_3"])
        notificador._enviar_push = Mock()
        
        evento = {
            'tipo': 'plano_enviado',
            'descricao': 'Plano foi enviado',
            'timestamp': datetime.now()
        }
        
        notificador.atualizar(evento)
        
        # Verificar histórico
        historico = notificador.obter_historico()
        assert len(historico) == 3
        assert all(h['canal'] == 'push' for h in historico)
        assert all(h['tipo_evento'] == 'plano_enviado' for h in historico)
        assert historico[0]['dispositivo_id'] == 'device_1'
        assert historico[1]['dispositivo_id'] == 'device_2'
        assert historico[2]['dispositivo_id'] == 'device_3'


class TestObserverPatternComMocks:
    """Testes do padrão Observer com mocks para validar integração"""

    def test_turma_notifica_email_com_mock(self):
        """Turma deve notificar NotificadorEmail corretamente"""
        professor = Professor("Prof", "prof@example.com", "senha", "prof001")
        turma = Turma("ES-2025.2", "ES", "2025.2", professor)
        
        # Criar notificador mock
        notificador_mock = Mock(spec=Observer)
        turma.adicionar_observer(notificador_mock)
        
        evento = {
            'tipo': 'aluno_adicionado',
            'descricao': 'Aluno foi adicionado',
            'turma': 'ES-2025.2'
        }
        
        turma.notificar_observers(evento)
        
        # Verificar que o observer foi notificado
        assert notificador_mock.atualizar.called
        assert notificador_mock.atualizar.call_count == 1
        
        # Verificar que o evento foi passado corretamente
        call_args = notificador_mock.atualizar.call_args[0][0]
        assert call_args['tipo'] == 'aluno_adicionado'
        assert call_args['turma'] == 'ES-2025.2'

    def test_subject_notifica_todos_observers(self):
        """Subject deve notificar todos os observers registrados"""
        professor = Professor("Prof", "prof@example.com", "senha", "prof001")
        turma = Turma("ES-2025.2", "ES", "2025.2", professor)
        
        # Adicionar 3 observers mocks
        observer_mocks = [Mock(spec=Observer) for _ in range(3)]
        for obs in observer_mocks:
            turma.adicionar_observer(obs)
        
        evento = {'tipo': 'teste', 'descricao': 'Teste notificação'}
        
        turma.notificar_observers(evento)
        
        # Verificar que todos foram notificados
        for obs in observer_mocks:
            assert obs.atualizar.called
            assert obs.atualizar.call_count == 1

    def test_observer_removido_nao_e_notificado(self):
        """Observer removido não deve receber notificações"""
        professor = Professor("Prof", "prof@example.com", "senha", "prof001")
        turma = Turma("ES-2025.2", "ES", "2025.2", professor)
        
        observer_mock = Mock(spec=Observer)
        turma.adicionar_observer(observer_mock)
        
        # Primeiro evento - deve ser notificado
        evento1 = {'tipo': 'evento1', 'descricao': 'Teste'}
        turma.notificar_observers(evento1)
        assert observer_mock.atualizar.call_count == 1
        
        # Remover observer
        turma.remover_observer(observer_mock)
        
        # Segundo evento - NÃO deve ser notificado
        evento2 = {'tipo': 'evento2', 'descricao': 'Teste'}
        turma.notificar_observers(evento2)
        
        # Ainda deve estar 1 (não aumentou)
        assert observer_mock.atualizar.call_count == 1

    def test_notificador_email_real_com_eventos(self):
        """Testar NotificadorEmail real recebendo eventos de Turma"""
        professor = Professor("Prof", "prof@example.com", "senha", "prof001")
        turma = Turma("ES-2025.2", "ES", "2025.2", professor)
        
        # Criar notificador real com mock interno
        notificador = NotificadorEmail("admin@example.com")
        notificador._enviar_email = Mock()
        
        turma.adicionar_observer(notificador)
        
        evento = {
            'tipo': 'professor_atribuido',
            'turma': 'ES-2025.2',
            'professor': 'João Silva'
        }
        
        turma.notificar_observers(evento)
        
        # Verificar que email foi preparado
        assert notificador._enviar_email.called
        call_args = notificador._enviar_email.call_args[0]
        assert 'professor_atribuido' in call_args[0]  # Assunto

    def test_notificador_push_real_com_eventos(self):
        """Testar NotificadorPush real recebendo eventos de Turma"""
        professor = Professor("Prof", "prof@example.com", "senha", "prof001")
        turma = Turma("ES-2025.2", "ES", "2025.2", professor)
        
        # Criar notificador real com mock interno
        notificador = NotificadorPush("usuario_123", ["device_1"])
        notificador._enviar_push = Mock()
        
        turma.adicionar_observer(notificador)
        
        evento = {
            'tipo': 'avaliacao_criada',
            'turma': 'ES-2025.2',
            'descricao': 'Avaliação criada'
        }
        
        turma.notificar_observers(evento)
        
        # Verificar que push foi preparado
        assert notificador._enviar_push.called
        payload = notificador._enviar_push.call_args[0][1]
        assert 'avaliacao_criada' in payload['titulo']
