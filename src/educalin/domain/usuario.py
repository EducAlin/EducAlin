from typing import Optional

class Usuario:
    """Classe base - stub temporário"""
    def __init__(self, nome: str):
        self.nome = nome

class Aluno(Usuario):
    """Stub temporário da classe Aluno"""
    def __init__(self, matricula: str, nome: str):
        super().__init__(nome)
        self.matricula = matricula
    
    def calcular_media(self) -> float:
        """Será implementado pela equipe responsável"""
        return 0.0

class Professor(Usuario):
    """Stub temporário da classe Professor"""
    def __init__(self, nome: str, registro: Optional[str] = None):
        super().__init__(nome)
        self.registro = registro
