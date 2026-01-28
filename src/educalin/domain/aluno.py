from usuario import Usuario
from material import Material

class Aluno(Usuario):
    def __init__(self, nome: str, email: str, senha: str, matricula: str, desempenho: dict):
        self.nome = nome
        self._email = email
        self.__senha = senha
        self.matricula = matricula
        self.__desempenho = desempenho

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
    def desempenho(self):
        return self.__desempenho

    @desempenho.setter
    def desempenho(self, novo_desempenho):
        self.__desempenho = novo_desempenho 
        
    def visualizar_desempenho(self):
        return print(self.desempenho)
    
    def acessar_material(material_id):
        pass