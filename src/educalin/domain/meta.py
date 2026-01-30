from datetime import datetime

class Meta:
    def __init__(self, id: int, aluno: str, descricao: str, valor_alvo: float, prazo: datetime, progresso_atual: float = 0.0):
        self._id = id
        self._aluno = aluno
        self._descricao = descricao
        self._valor_alvo = valor_alvo
        self._prazo = prazo
        self._progresso_atual = progresso_atual

    # ID
    @property
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, valor: int) -> None:
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("O ID deve ser um inteiro positivo.")
        self._id = valor

    # Aluno: posteriormente virá do objeto de classe Aluno
    
    # Descrição
    @property
    def descricao(self) -> str:
        return self._descricao
    
    @descricao.setter
    def descricao(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise ValueError("A descrição deve ser uma string.")
        if not valor.strip():
            raise ValueError("A descrição não pode ser vazia.")
        self._descricao = valor.strip()

    # Valor Alvo
    @property
    def valor_alvo(self) -> float:
        return self._valor_alvo
    
    @valor_alvo.setter
    def valor_alvo(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or valor <= 0:
            raise ValueError("O valor alvo deve ser um número positivo.")
        self._valor_alvo = float(valor)

    # Prazo
    @property
    def prazo(self) -> datetime:
        return self._prazo
    
    @prazo.setter
    def prazo(self, valor: datetime) -> None:
        if not isinstance(valor, datetime):
            raise ValueError("O prazo deve ser um objeto datetime.")
        self._prazo = valor

    # Progresso Atual
    @property
    def progresso_atual(self) -> float:
        return self._progresso_atual
    
    @progresso_atual.setter
    def progresso_atual(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError("O progresso atual deve ser um número não negativo.")
        if valor > self._valor_alvo:
            raise ValueError("O progresso atual não pode exceder o valor alvo.")
        self._progresso_atual = float(valor)

    #Métodos concretos
    def atualizar_progresso(self, valor: float) -> None:
        """
        Atualiza o progresso atual da meta.

        :param valor: novo valor de progresso a ser adicionado
        """
        if not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError("O valor de progresso deve ser um número não negativo.")
        novo_progresso = self._progresso_atual + float(valor)
        if novo_progresso > self._valor_alvo:
            raise ValueError("O progresso atual não pode exceder o valor alvo.")
        self._progresso_atual = novo_progresso

    def verificar_conclusao(self) -> bool:
        """
        Verifica se a meta foi concluída.

        :return: True se o progresso atual for maior ou igual ao valor alvo, False caso contrário
        """
        return self._progresso_atual >= self._valor_alvo
    
    
