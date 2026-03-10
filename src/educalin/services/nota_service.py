"""
Serviço de aplicação para o caso de uso de registro de notas.

Orquestra a persistência da nota via AvaliacaoRepository e o disparo
de eventos para os observers registrados via PublicadorEventos,
respeitando o princípio de inversão de dependências (DIP): o serviço
depende da abstração, não de implementações concretas de notificação.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from educalin.repositories.avaliacao_repository import AvaliacaoRepository


class EventoNotaRegistrada(TypedDict):
    """
    Schema canônico do evento ``nota_registrada``.

    Usado por ``NotaService`` ao publicar e pelos observers ao consumir,
    garantindo que produtor e consumidores compartilhem o mesmo contrato
    de dados sem acoplamento implícito por strings.

    Keys:
        evento: Identificador do tipo de evento. Sempre ``"nota_registrada"``.
        avaliacao_id: ID da avaliação à qual a nota pertence.
        aluno_id: ID do aluno que recebeu a nota.
        valor: Valor numérico da nota registrada.
        timestamp: Momento UTC do registro.
    """

    evento: str
    avaliacao_id: int
    aluno_id: int
    valor: float
    timestamp: datetime


class PublicadorEventos(ABC):
    """
    Interface (porta de saída) para publicação de eventos de domínio.

    Desacopla o ``NotaService`` das implementações concretas de
    notificação (email, push, etc.), seguindo o princípio DIP.

    Implementações concretas devem converter o evento recebido para
    o formato adequado ao canal de entrega.

    Examples:
        >>> class PublicadorFake(PublicadorEventos):
        ...     def __init__(self):
        ...         self.eventos = []
        ...     def publicar_nota_registrada(self, evento):
        ...         self.eventos.append(evento)
    """

    @abstractmethod
    def publicar_nota_registrada(self, evento: dict) -> None:
        """
        Publica o evento de nota registrada para os canais configurados.

        Args:
            evento: Dicionário com os dados do evento. Contém obrigatoriamente:
                - ``evento`` (str): ``"nota_registrada"``
                - ``avaliacao_id`` (int): ID da avaliação
                - ``aluno_id`` (int): ID do aluno
                - ``valor`` (float): Valor da nota registrada
                - ``timestamp`` (datetime): Momento do registro
        """


class NotaService:
    """
    Serviço de aplicação que orquestra o caso de uso de registro de nota.

    Responsabilidades:
    1. Delegar a persistência ao ``AvaliacaoRepository``.
    2. Disparar o evento ``nota_registrada`` via ``PublicadorEventos``
       após a persistência bem-sucedida.

    O publicador é opcional para facilitar cenários sem notificação
    (ex.: importação em lote, testes unitários puros).

    Attributes:
        _repo: Repositório de avaliações para persistência.
        _publicador: Publicador de eventos (opcional).

    Examples:
        >>> service = NotaService(repo, publicador)
        >>> nota_id = service.registrar_nota(
        ...     avaliacao_id=1, aluno_id=5, valor=8.5
        ... )
    """

    def __init__(
        self,
        repo: "AvaliacaoRepository",
        publicador: PublicadorEventos | None = None,
    ) -> None:
        """
        Inicializa o serviço com o repositório e o publicador de eventos.

        Args:
            repo: Repositório de avaliações (persiste nota).
            publicador: Publicador de eventos para disparo de notificações.
                Se ``None``, a nota é persistida sem notificações.
        """
        self._repo = repo
        self._publicador = publicador

    def registrar_nota(
        self,
        avaliacao_id: int,
        aluno_id: int,
        valor: float,
    ) -> int:
        """
        Persiste a nota e dispara o evento ``nota_registrada``.

        O evento é disparado **somente** após a persistência bem-sucedida,
        garantindo consistência: observers nunca são notificados de notas
        que falharam ao ser salvas.

        Args:
            avaliacao_id: ID da avaliação à qual a nota pertence.
            aluno_id: ID do aluno que recebeu a nota.
            valor: Valor numérico da nota (>= 0).

        Returns:
            ID (int) da nota criada no banco de dados.

        Raises:
            NotaDuplicadaError: Se já existir nota para este aluno
                nesta avaliação.
            ValorInvalidoError: Se o valor exceder o ``valor_maximo``
                da avaliação.
            ValueError: Para outros erros de validação do repositório.

        Examples:
            >>> nota_id = service.registrar_nota(
            ...     avaliacao_id=1, aluno_id=5, valor=8.5
            ... )
        """
        nota_id = self._repo.registrar_nota({
            "aluno_id": aluno_id,
            "avaliacao_id": avaliacao_id,
            "valor": valor,
        })

        if self._publicador is not None:
            evento: EventoNotaRegistrada = {
                "evento": "nota_registrada",
                "avaliacao_id": avaliacao_id,
                "aluno_id": aluno_id,
                "valor": valor,
                "timestamp": datetime.now(tz=timezone.utc),
            }
            self._publicador.publicar_nota_registrada(evento)

        return nota_id
