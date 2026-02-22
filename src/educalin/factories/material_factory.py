from datetime import datetime

from abc import ABC, abstractmethod
from typing import Any
from educalin.domain.material import MaterialEstudo, MaterialLink, MaterialPDF, MaterialVideo


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
        return MaterialPDF(
            titulo=dados['titulo'],
            descricao=dados['descricao'],
            data_criacao=dados['data_criacao'],
            autor=dados['autor'],
            num_paginas=dados['num_paginas']
            )

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
        return MaterialVideo(
            titulo=dados['titulo'],
            descricao=dados['descricao'],
            data_criacao=dados['data_criacao'],
            autor=dados['autor'],
            duracao_segundos=dados['duracao_segundos'],
            codec=dados['codec']
        )

class MaterialLinkFactory(MaterialEstudoFactory):
    """
    Factory concreta para criação de materiais de estudo no formato Link.
    """

    def criar_material(self, dados: dict) -> MaterialEstudo:
        from educalin.domain.material import MaterialLink  
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
        return MaterialLink(
            titulo=dados['titulo'],
            descricao=dados['descricao'],
            data_criacao=dados['data_criacao'],
            autor=dados['autor'],
            url=dados['url'],
            tipo_conteudo=dados['tipo_conteudo']
        )