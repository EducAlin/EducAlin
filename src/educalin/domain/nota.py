from datetime import datetime
from .aluno import Aluno
from .avaliacao import Avaliacao

class Nota:
    """
    Representa a nota de um aluno em uma avaliação específica,
    servindo como uma classe de associação.
    """
    def __init__(self, aluno: Aluno, avaliacao: Avaliacao, valor: float):
        if not isinstance(aluno, Aluno):
            raise TypeError("O aluno deve ser uma instância da classe Aluno.")

        if not isinstance(avaliacao, Avaliacao):
            raise TypeError("A avaliação deve ser uma instância da classe Avaliacao.")

        if not isinstance(valor, (int, float)):
             raise TypeError("O valor da nota deve ser um número.")

        if valor < 0:
            raise ValueError("O valor da nota não pode ser negativo.")

        if valor > avaliacao.valor_maximo:
            raise ValueError("O valor da nota não pode ser maior que o valor máximo da avaliação.")

        self.aluno = aluno
        self.avaliacao = avaliacao
        self.valor = valor
        self.data_registro = datetime.now()

    def calcular_percentual(self) -> float:
        """
        Calcula o percentual de acerto da nota em relação ao valor máximo da avaliação.

        Returns:
            float: O percentual da nota (0 a 100).
        """
        if self.avaliacao.valor_maximo == 0:
            return 0.0
        return (self.valor / self.avaliacao.valor_maximo) * 100