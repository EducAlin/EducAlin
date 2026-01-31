from __future__ import annotations

from datetime import datetime


class Meta:
    def __init__(
        self,
        meta_id: int,
        aluno: str,
        descricao: str,
        valor_alvo: float,
        prazo: datetime,
        progresso_atual: float = 0.0,
    ) -> None:
        # Validar e atribuir via setters
        self._id: int | None = None
        self._valor_alvo: float = 0.0
        self._progresso_atual: float = 0.0

        self.id = meta_id
        self.aluno = aluno
        self.descricao = descricao
        self.valor_alvo = valor_alvo
        self.prazo = prazo
        self.progresso_atual = progresso_atual

    # ID (imutável)
    @property
    def id(self) -> int:
        return self._id  # type: ignore[return-value]

    @id.setter
    def id(self, valor: int) -> None:
        if self._id is not None:
            raise ValueError("O ID não pode ser alterado após a criação da meta.")
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("O ID deve ser um inteiro positivo.")
        self._id = valor

    # Aluno
    @property
    def aluno(self) -> str:
        return self._aluno

    @aluno.setter
    def aluno(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("O aluno deve ser uma string não vazia.")
        self._aluno = valor.strip()

    # Descrição
    @property
    def descricao(self) -> str:
        return self._descricao

    @descricao.setter
    def descricao(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("A descrição deve ser uma string não vazia.")
        self._descricao = valor.strip()

    # Valor alvo (deve ser > 0 e >= progresso_atual)
    @property
    def valor_alvo(self) -> float:
        return self._valor_alvo

    @valor_alvo.setter
    def valor_alvo(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ValueError("O valor alvo deve ser um número positivo.")
        valor_float = float(valor)

        # se já existe progresso, alvo não pode ficar menor que progresso
        if hasattr(self, "_progresso_atual") and self._progresso_atual > valor_float:
            raise ValueError("O valor alvo não pode ser menor que o progresso atual.")

        self._valor_alvo = valor_float

    # Prazo
    @property
    def prazo(self) -> datetime:
        return self._prazo

    @prazo.setter
    def prazo(self, valor: datetime) -> None:
        if not isinstance(valor, datetime):
            raise ValueError("O prazo deve ser um objeto datetime.")
        self._prazo = valor

    # Progresso atual (0 <= progresso <= valor_alvo)
    @property
    def progresso_atual(self) -> float:
        return self._progresso_atual

    @progresso_atual.setter
    def progresso_atual(self, valor: float) -> None:
        if not isinstance(valor, (int, float)):
            raise ValueError("O progresso atual deve ser um número.")
        valor_float = float(valor)
        if valor_float < 0:
            raise ValueError("O progresso atual deve ser um número não negativo.")
        if valor_float > self.valor_alvo:
            raise ValueError("O progresso atual não pode exceder o valor alvo.")
        self._progresso_atual = valor_float


    # Métodos de negócio
    def atualizar_progresso(self, incremento: float) -> None:
        if not isinstance(incremento, (int, float)):
            raise ValueError("O incremento deve ser numérico.")
        incremento_float = float(incremento)
        if incremento_float < 0:
            raise ValueError("O incremento deve ser um número não negativo.")

        self.progresso_atual = self._progresso_atual + incremento_float  # usa setter

    def verificar_conclusao(self) -> bool:
        return self._progresso_atual >= self._valor_alvo

    @property
    def faltante(self) -> float:
        """Quanto falta para atingir o valor alvo."""
        return max(0.0, self._valor_alvo - self._progresso_atual)

    @property
    def percentual_concluido(self) -> float:
        """0.0 a 1.0"""
        if self._valor_alvo == 0:
            return 0.0
        return min(1.0, self._progresso_atual / self._valor_alvo)

    @property
    def esta_atrasada(self) -> bool:
        """Atrasada = passou do prazo e ainda não foi concluída."""
        return datetime.now() > self._prazo and not self.verificar_conclusao()

    def __str__(self) -> str:
        return (
            f"Meta(id={self.id}, aluno={self.aluno}, descricao={self.descricao}, "
            f"valor_alvo={self.valor_alvo}, prazo={self.prazo.isoformat()}, "
            f"progresso_atual={self.progresso_atual})"
        )
