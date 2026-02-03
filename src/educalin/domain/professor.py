from .usuario import Usuario
from .aluno import Aluno
from ..utils.mixins import AutenticavelMixin

class Professor(Usuario, AutenticavelMixin):
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
        self.nome = nome
        self.email = email
        self.senha = self._hash_senha(senha)
        self._turmas = []
        self._registro_funcional = registro_funcional

    @property
    def nome(self):
        """Pega o nome do professor."""
        return self._nome
    
    @nome.setter
    def nome(self, novo_nome):
        """
        Atualiza o nome do professor.

        Args:
            novo_nome (str): O novo nome.

        Raises:
            ValueError: Se o nome for vazio ou só tiver espaços.
        """
        if not isinstance(novo_nome, str) or not novo_nome.strip():
            raise ValueError("O nome não pode ser vazio.")
        self._nome = novo_nome
        
    @property
    def email(self):
        """Pega o e-mail do professor."""
        return self._email

    import re
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @email.setter
    def email(self, novo_email):
        """
        Atualiza o e-mail do professor.
        Args:
            novo_email (str): O novo e-mail.
        Raises:
            ValueError: Se o e-mail não tiver formato válido.
        """
        if not EMAIL_PATTERN.match(novo_email.strip()):
            raise ValueError("Formato de e-mail inválido.")
        self._email = novo_email.strip()

    @property    
    def senha(self):
        """Pega o hash da senha do professor."""
        return self.__senha

    @senha.setter
    def senha(self, nova_senha):
        """
        Atualiza a senha do professor, criando um novo hash.

        Args:
            nova_senha (str): A nova senha em texto plano.
        """
        self.__senha = self._hash_senha(nova_senha)

    @property
    def turmas(self):
        """Pega a lista de turmas que o professor gerencia."""
        return self._turmas
    
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
        pass

    def registrar_notas(self, aluno: Aluno, avaliacao, nota):
        """
        Registra a nota de um aluno em uma avaliação específica.

        Args:
            aluno (Aluno): O aluno que vai receber a nota.
            avaliacao (object): A avaliação à qual a nota se refere.
            nota (float): O valor da nota.
        """
        pass
    
    def gerar_relatorio(self, tipo):
        """
        Gera um relatório de desempenho.

        Args:
            tipo (str): O tipo de relatório a ser gerado (ex: 'turma', 'individual').
        """
        pass
