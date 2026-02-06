from .usuario import Usuario
from .aluno import Aluno
from ..utils.mixins import AutenticavelMixin, NotificavelMixin

class Professor(Usuario, AutenticavelMixin, NotificavelMixin):
    """
    Representa um professor no sistema.

    Além de ser um usuário que pode se autenticar, o professor gerencia turmas,
    cria planos de ação, registra notas e gera relatórios.
    """
    def __init__(self, nome: str, email: str, senha: str, registro_funcional: str):
        """
        Cria uma nova instância de Professor.

        Args:
            nome (str): O nome completo do professor.
            email (str): O e-mail de login.
            senha (str): A senha, que será armazenada com hash.
            registro_funcional (str): O registro único do professor.
        """
        # Chama super().__init__ para inicializar Usuario e mixins via MRO
        super().__init__(nome, email, senha)
        
        # Inicializa atributos específicos do Professor
        self._turmas = []
        self._registro_funcional = registro_funcional

    @property
    def turmas(self):
        """Pega a lista de turmas que o professor gerencia."""
        return self._turmas.copy()
    
    @property
    def registro_funcional(self):
        """Pega o registro funcional do professor."""
        return self._registro_funcional

    def adicionar_turma(self, turma):
        """
        Adiciona uma turma à lista de turmas do professor.

        A gente usa Duck Typing aqui, então qualquer objeto que se pareça
        com uma turma (tenha os métodos e atributos certos) pode ser adicionado.

        Args:
            turma (object): O objeto da turma a ser adicionado.
        """
        if turma not in self._turmas:
            self._turmas.append(turma)

    def criar_plano_acao(self, aluno: Aluno):
        """
        Cria um plano de ação personalizado para um aluno.

        Args:
            aluno (Aluno): O aluno que vai receber o plano de ação.
        """
        raise NotImplementedError("Funcionalidade a ser implementada")

    def registrar_notas(self, aluno: Aluno, avaliacao, nota):
        """
        Registra a nota de um aluno em uma avaliação específica.

        Args:
            aluno (Aluno): O aluno que vai receber a nota.
            avaliacao (object): A avaliação à qual a nota se refere.
            nota (float): O valor da nota.
        """
        raise NotImplementedError("Funcionalidade a ser implementada")
    
    def gerar_relatorio(self, tipo):
        """
        Gera um relatório de desempenho.

        Args:
            tipo (str): O tipo de relatório a ser gerado (ex: 'turma', 'individual').
        """
        raise NotImplementedError("Funcionalidade a ser implementada")    
