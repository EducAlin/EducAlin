"""
Implementação concreta de PublicadorEventos baseada no padrão Observer.

Fornece ObserverPublicadorEventos, que delega o despacho de eventos para
uma lista de instâncias Observer (NotificadorEmail, NotificadorPush, etc.),
mantendo o serviço de aplicação desacoplado dos canais de notificação.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from educalin.services.nota_service import PublicadorEventos

if TYPE_CHECKING:
    from educalin.domain.turma import Observer

logger = logging.getLogger(__name__)


class ObserverPublicadorEventos(PublicadorEventos):
    """
    Publicador de eventos que despacha para uma lista de Observers.

    Implementa ``PublicadorEventos`` traduzindo a chamada de alto nível
    ``publicar_nota_registrada()`` para o método ``atualizar()`` de cada
    ``Observer`` registrado (ex.: ``NotificadorEmail``, ``NotificadorPush``).

    Falhas individuais de um observer são registradas via logging e **não**
    interrompem os demais — o publicador garante que todos os observers
    recebam o evento independentemente de falhas individuais.

    Attributes:
        _observers: Lista de observers que receberão o evento.

    Examples:
        >>> from educalin.services.notificador import NotificadorEmail
        >>> publicador = ObserverPublicadorEventos([
        ...     NotificadorEmail("aluno@escola.edu.br"),
        ... ])
        >>> service = NotaService(repo, publicador)
    """

    def __init__(self, observers: list["Observer"]) -> None:
        """
        Inicializa o publicador com a lista de observers.

        Args:
            observers: Lista de instâncias que implementam a interface
                ``Observer`` (possuem método ``atualizar(evento)``).

        Raises:
            TypeError: Se ``observers`` não for uma lista.
        """
        if not isinstance(observers, list):
            raise TypeError("observers deve ser uma lista")
        self._observers = observers

    def publicar_nota_registrada(self, evento: dict) -> None:
        """
        Despacha o evento ``nota_registrada`` para todos os observers.

        Itera sobre todos os observers chamando ``atualizar(evento)`` em
        cada um. Falhas individuais são capturadas e registradas via
        ``logging.error``, garantindo que os demais observers continuem
        sendo notificados mesmo em caso de erro parcial.

        Args:
            evento: Dicionário com os dados do evento, conforme definido
                em ``PublicadorEventos.publicar_nota_registrada()``.

        Examples:
            >>> publicador.publicar_nota_registrada({
            ...     "evento": "nota_registrada",
            ...     "avaliacao_id": 1,
            ...     "aluno_id": 5,
            ...     "valor": 8.5,
            ...     "timestamp": datetime.now(tz=timezone.utc),
            ... })
        """
        for observer in self._observers:
            try:
                observer.atualizar(evento)
            except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
                logger.error(
                    "Observer %s falhou ao processar evento '%s': %s",
                    type(observer).__name__,
                    evento.get("evento"),
                    exc,
                    exc_info=True,
                )
