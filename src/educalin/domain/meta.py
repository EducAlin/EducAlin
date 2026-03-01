from __future__ import annotations

from datetime import datetime
from typing import List, Dict
from educalin.domain.turma import Subject, Observer


class Meta(Subject):
    """
    Representa uma meta de aprendizado de um aluno.
    Atributos:
    - descricao: Uma descrição da meta (string não vazia).
    - valor_alvo: O valor numérico que representa o objetivo a ser alcançado (float positivo).
    - prazo: A data e hora limite para alcançar a meta (datetime).
    - progresso_atual: O valor numérico que representa o progresso atual em direção à meta (float, 0 <= progresso_atual <= valor_alvo).


    Regras:
    - valor_alvo > 0
    - 0 <= progresso_atual <= valor_alvo
    - A meta é concluída quando progresso_atual >= valor_alvo
    """

    def __init__(
        self,
        descricao: str,
        valor_alvo: float,
        prazo: datetime,
        progresso_atual: float = 0.0,
    ) -> None:
        self.descricao = descricao
        self.valor_alvo = valor_alvo
        self.prazo = prazo
        self.progresso_atual = progresso_atual
        
        # Padrão Observer
        self._observers: List[Observer] = []
        self._meta_atingida_em: datetime = None

    @property
    def descricao(self) -> str:
        """A descrição da meta (deve ser uma string não vazia)."""
        return self._descricao

    @descricao.setter
    def descricao(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("A descrição deve ser uma string não vazia.")
        self._descricao = valor.strip()

    @property
    def valor_alvo(self) -> float:
        """O valor alvo da meta (deve ser um número positivo)."""
        return self._valor_alvo

    @valor_alvo.setter
    def valor_alvo(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ValueError("O valor alvo deve ser um número positivo.")
        self._valor_alvo = float(valor)

        # Se já existia progresso e agora alvo ficou menor, mantém consistência.
        if hasattr(self, "_progresso_atual") and self._progresso_atual > self._valor_alvo:
            raise ValueError("O valor alvo não pode ser menor que o progresso atual.")

    @property
    def prazo(self) -> datetime:
        """O prazo da meta (deve ser um objeto datetime)."""
        return self._prazo

    @prazo.setter
    def prazo(self, valor: datetime) -> None:
        if not isinstance(valor, datetime):
            raise ValueError("O prazo deve ser um objeto datetime.")
        self._prazo = valor

    @property
    def progresso_atual(self) -> float:
        """O progresso atual da meta (deve ser um número entre 0 e valor_alvo)."""
        return self._progresso_atual

    @progresso_atual.setter
    def progresso_atual(self, valor: float) -> None:
        if not isinstance(valor, (int, float)):
            raise ValueError("O progresso atual deve ser um número.")
        valor_float = float(valor)

        if valor_float < 0:
            raise ValueError("O progresso atual deve ser não negativo.")
        if valor_float > self.valor_alvo:
            raise ValueError("O progresso atual não pode exceder o valor alvo.")

        self._progresso_atual = valor_float

    def atualizar_progresso(self, novo_valor: float) -> None:
        """
        Atualiza o progresso atual para um valor absoluto.

        Notifica observers quando a meta é atingida.

        Args:
            novo_valor: Novo valor de progresso (0 <= novo_valor <= valor_alvo).
        """
        # Verificar se a meta será atingida nesta atualização
        meta_estava_atingida = self.verificar_conclusao()
        
        # Atualizar o progresso (usa setter que valida)
        self.progresso_atual = novo_valor
        
        # Se a meta acaba de ser atingida, notificar observers
        if not meta_estava_atingida and self.verificar_conclusao():
            self._meta_atingida_em = datetime.now()
            self.notificar_observers({
                'evento': 'meta_atingida',
                'descricao': self.descricao,
                'valor_alvo': self.valor_alvo,
                'progresso_atual': self.progresso_atual,
                'percentual_concluido': self.percentual_concluido,
                'timestamp': self._meta_atingida_em
            })

    def verificar_conclusao(self) -> bool:
        """
        Indica se a meta foi concluída.

        Returns:
            True se progresso_atual >= valor_alvo, caso contrário False.
        """
        return self.progresso_atual >= self.valor_alvo

    @property
    def percentual_concluido(self) -> float:
        """Retorna o percentual concluído como fração entre 0 e 1.

        Notes:
            - É limitado a 1.0 (100%).
            - `valor_alvo` é sempre > 0 pelas validações da classe.
        """

        return min(self.progresso_atual / self.valor_alvo, 1.0)

    @property
    def esta_atrasada(self) -> bool:
        """
        Indica se a meta está atrasada (prazo vencido e não concluída).
        """
        return datetime.now() > self.prazo and not self.verificar_conclusao()

    def __str__(self) -> str:
        return (
            f"Meta(descricao={self.descricao}, valor_alvo={self.valor_alvo}, "
            f"prazo={self.prazo.isoformat()}, progresso_atual={self.progresso_atual})"
        )

    # =================================
    # Padrão Observer
    # =================================

    def adicionar_observer(self, observer: Observer) -> None:
        """
        Adiciona um observer à lista de observadores.

        Args:
            observer: Instância que implementa Observer

        Raises:
            TypeError: Se observer não implementa a interface Observer
        """
        if not isinstance(observer, Observer):
            raise TypeError(
                f"Observer deve implementar a interface Observer, "
                f"recebido {type(observer).__name__}"
            )
        
        if observer not in self._observers:
            self._observers.append(observer)

    def remover_observer(self, observer: Observer) -> None:
        """
        Remove um observer da lista de observadores.

        Args:
            observer: Instância a ser removida
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notificar_observers(self, evento: Dict) -> None:
        """
        Notifica todos os observers sobre um evento.

        Args:
            evento: Dicionário com informações do evento
        """
        for observer in self._observers:
            observer.atualizar(evento)
