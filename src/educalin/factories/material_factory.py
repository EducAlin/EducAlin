from datetime import datetime

from abc import ABC, abstractmethod
from typing import Any
from material_estudo import MaterialEstudo


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
        :return: instância de MaterialPDF
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
        :return: instância de MaterialLink
        """
        pass