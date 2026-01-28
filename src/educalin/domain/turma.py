from typing import List, Optional
from datetime import datetime

class AlunoDuplicadoException(Exception):
    """Exceção lançada quando tenta adicionar aluno duplicado com flag strict"""
    pass
class Turma():
    """
    Representa uma turma escolar com alunos e notificações.

    Attributes:
        __codigo (str): Identificador único da turma
        _disciplina (str): Nome da disciplina
        _semestre (str): Período letivo (ex.: "2025.2")
        _professor (Professor): Professor responsável pela turma
        _alunos (List[Aluno]): Lista de alunos matriculados
        _observers (List[Observer]): Lista de observadores
        _data_criacao (datetime): Data de criação da turma
    """

    def __init__(
        self,
        codigo: str,
        disciplina: str,
        semestre: str,
        professor: Optional['Professor'] = None
    ):
        """
        Inicializa uma nova turma.

        Args:
            codigo: Código único da turma (ex.: "ES-2025.2")
            disciplina: Nome da disciplina
            semestre: Período letivo
            professor: Professor responsável (opcional inicialmente)

        Raises:
            ValueError: Se código, disciplina ou semestre forem vazios
        """
        # Validações
        if not codigo or not codigo.strip():
            raise ValueError("Código da turma não pode ser vazio")
        if not disciplina or not disciplina.strip():
            raise ValueError("Disciplina da turma não pode ser vazia")
        if not semestre or not semestre.strip():
            raise ValueError("Semestre da turma não pode ser vazio")
        
        # Atributos
        self.__codigo = codigo.strip()
        self._disciplina = disciplina.strip()
        self._semestre = semestre.strip()
        self._professor = professor

        self._alunos: List['Aluno'] = []
        self._observers: List[Observer] = []

        self._data_criacao = datetime.now()
        
    # Encapsulamento

    @property
    def codigo(self) -> str:
        """Retorna o código da turma"""
        return self.__codigo
    
    @property
    def disciplina(self) -> str:
        """Retorna o nome da disciplina"""
        return self._disciplina
    
    @property
    def semestre(self) -> str:
        """Retorna o semestre"""
        return self._semestre
    
    @property
    def professor(self) -> Optional['Professor']:
        """Retorna o professor responsável"""
        return self._professor
    
    @professor.setter
    def professor(self, professor: 'Professor') -> None:
        """
        Define o professor responsável

        Args:
            professor: Instância de professor

        Raises:
            TypeError: Se não for uma instância de Professor
        """
        # Importação local para evitar importação circular
        from educalin.domain.usuario import Professor

        if not isinstance(professor, Professor):
            raise TypeError("Professor deve ser uma instância da classe Professor")
        
        self._professor = professor
        # TODO tenho que implementar interface observer aqui possivelmente
    
    @property
    def alunos(self) -> List['Aluno']:
        """
        Retorna cópia da lista de alunos.

        Retorna uma cópia para evitar modificação externa direta.
        Use adicionar_aluno() e remover_aluno() para gerenciar.
        """
        return self._alunos.copy()
    
    @property
    def total_alunos(self) -> int:
        """Retorna o total de alunos na turma"""
        return len(self._alunos)
    
    @property
    def data_criacao(self) -> datetime:
        """Retorna a data de criação da turma"""
        return self._data_criacao
    
    # Métodos de gestãod e alunos

    def adicionar_aluno(self, aluno: 'Aluno', strict: bool = False) -> bool:
        """
        Adiciona um aluno à turma

        Args:
            aluno: Instância de Aluno a ser adicionado
            strict: Se True, lança exceção ao tentar adicionar duplicado.
                    Se False (padrão), ignora silenciosamente.

        Returns:
            True se aluno foi adicionado, False se já existia (modo não-strict)

        Raises:
            TypeError: Se aluno não for instância de Aluno
            AlunoDuplicadoException: Se aluno já existe e strict=True
        
        Examples:
            >>> turma.adicionar_aluno(aluno1)  # True
            >>> turma.adicionar_aluno(aluno1)  # False (duplicado ignorado)
            >>> turma.adicionar_aluno(aluno1, strict=True)  # Raises AlunoDuplicadoException
        """
        # Importação local para evitar importação circular
        from educalin.domain.usuario import Aluno

        # Verifica tipo
        if not isinstance(aluno, Aluno):
            raise TypeError(f"Esperado instância de Aluno, recebido {type(aluno).__name__}")
        
        # Verifica duplicação
        if self._aluno_existe(aluno):
            if strict:
                raise AlunoDuplicadoException(f"Aluno {aluno.matricula} já está na turma {self.codigo}")
            return False
        
        # Adicionar aluno
        self._alunos.append(aluno)

        # TODO implementação interface observers

        return True