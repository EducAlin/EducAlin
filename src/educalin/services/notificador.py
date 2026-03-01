"""
Módulo de notificadores concretos implementando o padrão Observer.

Fornece implementações concretas de notificadores que reagem a eventos
do sistema, como NotificadorEmail e NotificadorPush.
"""

from typing import Dict, List, Optional
from datetime import datetime
from educalin.domain.turma import Observer


class NotificadorEmail(Observer):
    """
    Observer concreto que implementa notificações via email.

    Quando um evento ocorre em uma Turma (Subject), este notificador
    recebe a notificação e processa o envio de um email para o destinatário.

    Attributes:
        _email_destinatario (str): Email do destinatário da notificação
        _notificacoes_enviadas (List[Dict]): Histórico de notificações enviadas
    """

    def __init__(self, email_destinatario: str):
        """
        Inicializa o notificador de email.

        Args:
            email_destinatario (str): Email para o qual as notificações serão enviadas

        Raises:
            ValueError: Se o email for vazio ou inválido
        """
        if not email_destinatario or not email_destinatario.strip():
            raise ValueError("Email do destinatário não pode ser vazio")
        
        self._email_destinatario = email_destinatario.strip()
        self._notificacoes_enviadas: List[Dict] = []

    def atualizar(self, evento: Dict) -> None:
        """
        Processa uma notificação e envia um email.

        Método chamado quando um evento ocorre em uma Turma observada.
        Extrai informações do evento e processa o envio de email.

        Args:
            evento (Dict): Dicionário contendo informações do evento.
                Esperado ter chaves como:
                - 'tipo': str (ex: 'nota_registrada', 'plano_acao_criado')
                - 'descricao': str
                - 'timestamp': datetime (opcional)
                - 'turma': str (opcional)
                - 'dados_adicionais': Dict (opcional)

        Returns:
            None

        Raises:
            TypeError: Se evento não for um dicionário
        """
        # Validar estrutura do evento
        if not isinstance(evento, dict):
            raise TypeError("Evento deve ser um dicionário")

        try:

            tipo_evento = evento.get('tipo', 'evento_desconhecido')
            descricao = evento.get('descricao', 'Sem descrição')
            timestamp = evento.get('timestamp', datetime.now())
            turma = evento.get('turma', 'N/A')

            # Construir corpo do email
            assunto = f"[EducAlin] {tipo_evento}"
            corpo = self._construir_corpo_email(
                tipo_evento,
                descricao,
                timestamp,
                turma,
                evento.get('dados_adicionais', {})
            )

            # Simular envio de email
            self._enviar_email(assunto, corpo)

            # Registrar no histórico
            self._registrar_notificacao_enviada(
                'email',
                self._email_destinatario,
                tipo_evento,
                timestamp
            )
        except Exception as e:
            # Log de erro (sem interromper fluxo)
            print(f"Erro ao enviar email para {self._email_destinatario}: {str(e)}")

    def _construir_corpo_email(
        self,
        tipo_evento: str,
        descricao: str,
        timestamp: datetime,
        turma: str,
        dados_adicionais: Dict
    ) -> str:
        """
        Constrói o corpo do email a ser enviado.

        Args:
            tipo_evento: Tipo de evento que disparou a notificação
            descricao: Descrição do evento
            timestamp: Data e hora do evento
            turma: Identificador da turma (se aplicável)
            dados_adicionais: Dados extras para contexto

        Returns:
            str: Corpo formatado do email
        """
        corpo = f"""
Olá,

Uma nova notificação foi gerada no EducAlin:

Tipo de Evento: {tipo_evento}
Descrição: {descricao}
Data/Hora: {timestamp.strftime('%d/%m/%Y %H:%M:%S')}
Turma: {turma}

"""
        if dados_adicionais:
            corpo += "Informações Adicionais:\n"
            for chave, valor in dados_adicionais.items():
                corpo += f"  - {chave}: {valor}\n"

        corpo += """
---
Este é um email automático do sistema EducAlin.
Por favor, não responda este email.
"""
        return corpo

    def _enviar_email(self, assunto: str, corpo: str) -> None:
        """
        Simula o envio de um email (em produção, integrar com SMTP ou SendGrid).

        Args:
            assunto: Assunto do email
            corpo: Corpo do email

        Returns:
            None
        """
        # TODO: Integrar com serviço SMTP (ex: smtplib) ou API de email (ex: SendGrid)
        print(f"[EMAIL ENVIADO] Para: {self._email_destinatario}")
        print(f"  Assunto: {assunto}")
        print(f"  Tamanho do corpo: {len(corpo)} caracteres")

    def _registrar_notificacao_enviada(
        self,
        canal: str,
        destinatario: str,
        tipo_evento: str,
        timestamp: datetime
    ) -> None:
        """
        Registra a notificação no histórico.

        Args:
            canal: Canal de notificação (email, push, etc)
            destinatario: Destinatário (email ou user_id)
            tipo_evento: Tipo do evento enviado
            timestamp: Timestamp do evento

        Returns:
            None
        """
        registro = {
            'canal': canal,
            'destinatario': destinatario,
            'tipo_evento': tipo_evento,
            'timestamp': timestamp,
            'status': 'enviado'
        }
        self._notificacoes_enviadas.append(registro)

    def obter_historico(self) -> list:
        """
        Retorna o histórico de notificações enviadas.

        Returns:
            List[Dict]: Lista de notificações com status, timestamp, etc
        """
        return self._notificacoes_enviadas.copy()


class NotificadorPush(Observer):
    """
    Observer concreto que implementa notificações via push (dispositivos móveis/web).

    Quando um evento ocorre em uma Turma (Subject), este notificador
    recebe a notificação e processa o envio de uma notificação push
    para o usuário em seus dispositivos registrados.

    Attributes:
        _usuario_id (str): Identificador do usuário que receberá as notificações
        _dispositivos (List[str]): Lista de IDs de dispositivos registrados
        _notificacoes_enviadas (List[Dict]): Histórico de notificações enviadas
    """

    def __init__(self, usuario_id: str, dispositivos: Optional[list] = None):
        """
        Inicializa o notificador push.

        Args:
            usuario_id (str): ID único do usuário no sistema
            dispositivos (List[str], optional): Lista de IDs de dispositivos registrados.
                Se não fornecido, inicia como lista vazia.

        Raises:
            ValueError: Se usuario_id for vazio
        """
        if not usuario_id or not usuario_id.strip():
            raise ValueError("ID do usuário não pode ser vazio")

        self._usuario_id = usuario_id.strip()
        self._dispositivos: list = dispositivos if dispositivos else []
        self._notificacoes_enviadas: list = []

    def atualizar(self, evento: Dict) -> None:
        """
        Processa uma notificação e envia push para todos os dispositivos do usuário.

        Método chamado quando um evento ocorre em uma Turma observada.
        Extrai informações do evento e envia notificações push para todos
        os dispositivos registrados do usuário.

        Args:
            evento (Dict): Dicionário contendo informações do evento.
                Esperado ter chaves como:
                - 'tipo': str (ex: 'nota_registrada', 'plano_acao_criado')
                - 'descricao': str
                - 'timestamp': datetime (opcional)
                - 'turma': str (opcional)
                - 'dados_adicionais': Dict (opcional)

        Returns:
            None

        Raises:
            TypeError: Se evento não for um dicionário
        """
        # Validar estrutura do evento
        if not isinstance(evento, dict):
            raise TypeError("Evento deve ser um dicionário")

        try:

            if not self._dispositivos:
                print(f"[PUSH] Nenhum dispositivo registrado para usuário {self._usuario_id}")
                return

            # Extrair informações do evento
            tipo_evento = evento.get('tipo', 'evento_desconhecido')
            descricao = evento.get('descricao', 'Sem descrição')
            timestamp = evento.get('timestamp', datetime.now())
            turma = evento.get('turma', 'N/A')

            # Construir payload do push
            payload = self._construir_payload_push(
                tipo_evento,
                descricao,
                timestamp,
                turma,
                evento.get('dados_adicionais', {})
            )

            # Enviar para todos os dispositivos
            for dispositivo_id in self._dispositivos:
                self._enviar_push(dispositivo_id, payload)

                # Registrar no histórico
                self._registrar_notificacao_enviada(
                    'push',
                    dispositivo_id,
                    tipo_evento,
                    timestamp
                )
        except Exception as e:
            # Log de erro (sem interromper fluxo)
            print(f"Erro ao enviar push para usuário {self._usuario_id}: {str(e)}")

    def _construir_payload_push(
        self,
        tipo_evento: str,
        descricao: str,
        timestamp: datetime,
        turma: str,
        dados_adicionais: Dict
    ) -> Dict:
        """
        Constrói o payload (carga útil) da notificação push.

        Args:
            tipo_evento: Tipo de evento que disparou a notificação
            descricao: Descrição do evento
            timestamp: Data e hora do evento
            turma: Identificador da turma (se aplicável)
            dados_adicionais: Dados extras para contexto

        Returns:
            Dict: Payload estruturado para envio via serviço de push
        """
        payload = {
            'titulo': f"EducAlin - {tipo_evento}",
            'mensagem': descricao,
            'tipo': tipo_evento,
            'timestamp': timestamp.isoformat(),
            'turma': turma,
            'dados': dados_adicionais,
            'icone': 'ic_notificacao_educalin'
        }
        return payload

    def _enviar_push(self, dispositivo_id: str, payload: Dict) -> None:
        """
        Simula o envio de uma notificação push para um dispositivo.
        (Em produção, integrar com Firebase Cloud Messaging, OneSignal, etc.)

        Args:
            dispositivo_id: ID do dispositivo (ex: FCM token)
            payload: Dados da notificação

        Returns:
            None
        """
        # TODO: Integrar com Firebase Cloud Messaging (FCM) ou OneSignal
        print(f"[PUSH ENVIADO] Usuário: {self._usuario_id}, Dispositivo: {dispositivo_id}")
        print(f"  Título: {payload.get('titulo')}")
        print(f"  Mensagem: {payload.get('mensagem')}")

    def _registrar_notificacao_enviada(
        self,
        canal: str,
        dispositivo_id: str,
        tipo_evento: str,
        timestamp: datetime
    ) -> None:
        """
        Registra a notificação no histórico.

        Args:
            canal: Canal de notificação (email, push, etc)
            dispositivo_id: ID do dispositivo para o qual foi enviado
            tipo_evento: Tipo do evento enviado
            timestamp: Timestamp do evento

        Returns:
            None
        """
        registro = {
            'canal': canal,
            'dispositivo_id': dispositivo_id,
            'tipo_evento': tipo_evento,
            'timestamp': timestamp,
            'status': 'enviado'
        }
        self._notificacoes_enviadas.append(registro)

    def registrar_dispositivo(self, dispositivo_id: str) -> None:
        """
        Registra um novo dispositivo para receber notificações push.

        Args:
            dispositivo_id (str): ID único do dispositivo (ex: FCM token)

        Raises:
            ValueError: Se dispositivo_id for vazio
        """
        if not dispositivo_id or not dispositivo_id.strip():
            raise ValueError("ID do dispositivo não pode ser vazio")

        dispositivo_id = dispositivo_id.strip()
        if dispositivo_id not in self._dispositivos:
            self._dispositivos.append(dispositivo_id)

    def desregistrar_dispositivo(self, dispositivo_id: str) -> None:
        """
        Remove um dispositivo da lista de notificações push.

        Args:
            dispositivo_id (str): ID do dispositivo a remover

        Returns:
            None (silenciosamente ignora se não encontrado)
        """
        if dispositivo_id in self._dispositivos:
            self._dispositivos.remove(dispositivo_id)

    def obter_dispositivos_registrados(self) -> list:
        """
        Retorna lista de dispositivos registrados.

        Returns:
            List[str]: IDs dos dispositivos registrados
        """
        return self._dispositivos.copy()

    def obter_historico(self) -> list:
        """
        Retorna o histórico de notificações push enviadas.

        Returns:
            List[Dict]: Lista de notificações com status, timestamp, etc
        """
        return self._notificacoes_enviadas.copy()
