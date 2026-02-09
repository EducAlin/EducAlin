from datetime import date

class Avaliacao:
    """
    Representa uma avaliação no sistema, como uma prova ou trabalho.
    """
    def __init__(self, titulo: str, data: date, valor_maximo: float, peso: float):
        """
        Cria uma nova instância de Avaliação.

        Args:
            titulo (str): O titulo da avaliação.
            data (date): A data de realização da avaliação.
            valor_maximo (float): O valor máximo a ser atingido na avaliação.
            peso (float): O peso de cada avaliação.
        """
        if not isinstance(titulo, str) or not titulo.strip():
            raise ValueError("O título não pode ser vazio.")

        if not isinstance(data, date):
            raise TypeError("O atributo data deve ser um objeto date.")

        if not isinstance(valor_maximo, (int, float)) or valor_maximo <= 0:
            raise ValueError("O valor máximo deve ser um número positivo.")

        if not isinstance(peso, (int, float)) or not (0 <= peso <= 1):
            raise ValueError("O peso deve estar no intervalo de 0 a 1.")

        self.titulo = titulo
        self.data = data
        self.valor_maximo = valor_maximo
        self.peso = peso
