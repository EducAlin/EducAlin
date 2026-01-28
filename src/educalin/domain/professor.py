from usuario import Usuario
from turma import Turma
from aluno import Aluno

class Professor(Usuario):
    def __init__(self, nome: str, email: str, senha: str, turmas: Turma, registro_funcional: str):
        self.nome = nome
        self._email = email
        self.__senha = senha
        self.turmas = turmas
        self.registro_funcional = registro_funcional

    @property
    def nome(self):
        return self.nome
    
    @nome.setter
    def nome(self, novo_nome):
        self.nome = self.novo_nome
        
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, novo_email):
        self._email = self.novo_email

    @property    
    def senha(self):
        return self.__senha

    @senha.setter
    def senha(self, nova_senha):
        self.__senha = self.nova_senha

    @property
    def turmas(self):
        return self.turmas
    
    @turmas.setter
    def turmas(self, nova_turma):
        if not isinstance(nova_turma, list):
            raise ValueError("Turmas deve ser uma lista de Turma.")
        self._turmas = nova_turma

    def criar_plano_acao(Aluno):
        pass

    def registrar_notas(Aluno, avaliacao, nota):
        pass
    
    def gerar_relatorio(tipo):
        pass