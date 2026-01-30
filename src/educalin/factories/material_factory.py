from datetime import datetime

from abc import ABC, abstractmethod
from typing import Any
from domain.material import MaterialEstudo


class MaterialEstudoFactory(ABC):
    """
    Factory abstrata para criação de materiais de estudo.
    Cada subclasse decide qual tipo concreto de MaterialEstudo será criado.
    """

    @abstractmethod
    def criar_material(self, dados: dict) -> MaterialEstudo:
        """
        Cria e retorna um objeto do tipo MaterialEstudo.

        :param dados: dicionário contendo os dados necessários para criação do material
            Chaves esperadas no dicionário:
                - 'titulo': str
                - 'descricao': str
                - 'data_criacao': datetime
                - 'autor': str
                - Outros campos específicos dependendo do tipo de material
        :return: instância de MaterialEstudo
        """
        pass

class MaterialPDFFactory(MaterialEstudoFactory):
    """
    Factory concreta para criação de materiais de estudo no formato PDF.
    """

    def criar_material(self, dados: dict) -> MaterialEstudo:
        from domain.material import MaterialPDF  
        """
        Cria e retorna um objeto do tipo MaterialPDF.

        :param dados: dicionário contendo os dados necessários para criação do material
            Chaves esperadas no dicionário:
                - 'titulo': str
                - 'descricao': str
                - 'data_criacao': datetime
                - 'autor': str
                - 'num_paginas': int
        """
        pass

class MaterialVideoFactory(MaterialEstudoFactory):
    """
    Factory concreta para criação de materiais de estudo no formato Vídeo.
    """

    def criar_material(self, dados: dict) -> MaterialEstudo:
        from domain.material import MaterialVideo  
        """
        Cria e retorna um objeto do tipo MaterialVideo.

        :param dados: dicionário contendo os dados necessários para criação do material
            Chaves esperadas no dicionário:
                - 'titulo': str
                - 'descricao': str
                - 'data_criacao': datetime
                - 'autor': str
                - 'duracao_segundos': int
                - 'codec': str
        :return: instância de MaterialVideo
        """
        pass

class MaterialLinkFactory(MaterialEstudoFactory):
    """
    Factory concreta para criação de materiais de estudo no formato Link.
    """

    def criar_material(self, dados: dict) -> MaterialEstudo:
        from domain.material import MaterialLink  
        """
        Cria e retorna um objeto do tipo MaterialLink.

        :param dados: dicionário contendo os dados necessários para criação do material
            Chaves esperadas no dicionário:
                - 'titulo': str
                - 'descricao': str
                - 'data_criacao': datetime
                - 'autor': str
                - 'url': str
                - 'tipo_conteudo': str
        :return: instância de MaterialLink
        """
        pass