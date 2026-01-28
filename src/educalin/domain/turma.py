from typing import List, Optional, Dict
from datetime import datetime

class AlunoDuplicadoException(Exception):
    """Exceção lançada quando tenta adicionar aluno duplicado com flag strict"""
    pass

class AlunoNaoEncontradoException(Exception):
    """Exceção lançada quanto tenta remover aluno inexistente com flag strict"""
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
    
    # =================================
    # Métodos de gestãod e alunos
    # =================================

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
        if not hasattr(aluno, 'matricula'): # TODO substituir por isinstance(aluno, Aluno) quando implementado
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
    
    def remover_aluno(self, aluno: 'Aluno', strict: bool = False) -> bool:
        """
        Remove um aluno da turma

        Args:
            aluno: Instância de Aluno a ser removida
            strict: Se True, lança exceção se aluno não existir.
                    Se False (padrão), ignora silenciosamente.

        Returns:
            True se aluno foi removido, False se não estava na turma

        Raises:
            TypeError: Se aluno não for instância de Aluno
            AlunoNaoEncontradoException: Se aluno não existe e strict=True
        
        Examples:
            >>> turma.remover_aluno(aluno1)  # True
            >>> turma.remover_aluno(aluno1)  # False (não existe mais)
        """
        from educalin.domain.usuario import Aluno

        if not hasattr(aluno, 'matricula'): # TODO substituir por isinstance(aluno, Aluno) quando implementado
            raise TypeError(f"Esperado instância de Aluno, recebido {type(aluno).__name__}")
        
        if not self._aluno_existe(aluno):
            if strict:
                raise AlunoNaoEncontradoException(f"Aluno {aluno.matricula} não está na turma {self.codigo}")
            return False
        
        self._alunos.remove(aluno)

        # TODO implementação notificação observer

        return True
    
    def _aluno_existe(self, aluno: 'Aluno') -> bool:
        """
        Verifica se aluno já está na turma (por matrícula)

        Args:
            aluno: Instância de Aluno
        
        Returns:
            True se aluno já está na lista
        """
        return any(a.matricula == aluno.matricula for a in self._alunos)

    def buscar_aluno_por_matricula(self, matricula: str) -> Optional['Aluno']:
        """
        Busca um aluno na turma pela matrícula

        Args:
            matricula: Matrícula do aluno
        
        Returns:
            Instância de Aluno se encontrado, None caso contrário
        """
        return next(
            (aluno for aluno in self._alunos if aluno.matricula == matricula),
            None
        )
    
    # =================================
    # Métodos de desempenho
    # =================================

    def obter_desempenho_geral(self) -> Dict:
        """
        Calcula estatísticas gerais de desempenho da turma

        Returns:
            Dicionário com métricas:
            - media_geral: Média de todas as notas da turma
            - total_alunos: Número de alunos
            - alunos_com_dificuldade: Alunos com média < 6.0
            - taxa_aprovacao: Percentual de alunos com média >= 6.0

        Examples:
            >>> turma.obter_desempenho_geral()
            {
                'media_geral': 7.5,
                'total_alunos': 30,
                'alunos_com_dificuldade': 5,
                'taxa_aprovacao': 83.33
            }
        """
        if not self._alunos:
            return {
                'media_geral': 0.0,
                'total_alunos': 0,
                'alunos_com_dificuldade': 0,
                'taxa_aprovacao': 0.0
            }
        
        # Cálculo de médias individuais
        medias = []
        alunos_com_dificuldade = 0

        for aluno in self._alunos:
            if hasattr(aluno, 'calcular_media'):
                media = aluno.calcular_media()
                medias.append(media)
                if media < 6.0:
                    alunos_com_dificuldade += 1

        media_geral = sum(medias) / len(medias) if medias else 0.0
        taxa_aprovacao = (
            ((len(medias) - alunos_com_dificuldade) / len(medias)) * 100
            if medias else 0.0
        )

        return {
            'media_geral': round(media_geral, 2),
            'total_alunos': len(self._alunos),
            'alunos_com_dificuldade': alunos_com_dificuldade,
            'taxa_aprovacao': round(taxa_aprovacao, 2)
        }
    
    def obter_alunos_com_dificuldade(self, limite: float = 6.0) -> List['Aluno']:
        """
        Retorna lista de alunos com média abaixo do limite

        Args:
            limite: Nota mínima considerada satisfatória (padrão 6.0)
        
        Returns:
            Lista de alunos com dificuldade
        """
        alunos_dificuldade = []

        for aluno in self._alunos:
            if hasattr(aluno, 'calcular_media'):
                if aluno.calcular_media() < limite:
                    alunos_dificuldade.append(aluno)

        return alunos_dificuldade
    
    # =================================
    # Métodos especiais
    # =================================

    def __repr__(self) -> str:
        """Representação oficial da turma"""
        return (
            f"Turma(codigo='{self.codigo}', "
            f"disciplina='{self.disciplina}', "
            f"semestre='{self.semestre}', "
            f"alunos={len(self._alunos)})"
        )
    
    def __str__(self) -> str:
        """Representação amigável da turma"""
        return (
            f"Turma {self.codigo} - {self.disciplina} "
            f"({self.semestre}) - {len(self.alunos)} alunos"
        )
    
    def __eq__(self, other) -> bool:
        """Compara turmas pelo código"""
        if not isinstance(other, Turma):
            return False
        return self.codigo == other.codigo

    def __hash__(self) -> int:
        """Hash baseado no código (para usar em sets/dicts)"""
        return hash(self.codigo) 