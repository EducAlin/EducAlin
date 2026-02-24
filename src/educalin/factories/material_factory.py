from abc import ABC, abstractmethod
from datetime import datetime
from urllib.parse import urlparse
from educalin.domain.material import MaterialEstudo, MaterialLink, MaterialPDF, MaterialVideo


class MaterialEstudoFactory(ABC):
    """
    Factory abstrata para criação de materiais de estudo.
    Cada subclasse decide qual tipo concreto de MaterialEstudo será criado.

    Subclasses devem ser implementadas como objetos sem estado (stateless),
    pois as instâncias são reutilizadas pelo MaterialEstudoFactoryManager.
    """

    @abstractmethod
    def criar_material(self, dados: dict) -> MaterialEstudo:
        """
        Cria e retorna um objeto do tipo MaterialEstudo.

        :param dados: dicionário contendo os dados necessários para criação do material
            Chaves esperadas no dicionário:
                - 'titulo': str
                - 'descricao': str
                - 'data_upload': datetime
                - 'autor': str
                - Outros campos específicos dependendo do tipo de material
        :return: instância de MaterialEstudo
        """
        pass

    @staticmethod
    def _validar_chaves_obrigatorias(dados: dict, chaves_obrigatorias: set) -> None:
        """
        Valida se todas as chaves obrigatórias estão presentes no dicionário.

        :param dados: dicionário com os dados do material
        :param chaves_obrigatorias: conjunto de chaves que devem estar presentes
        :raises KeyError: Se alguma chave obrigatória estiver faltando
        """
        if not chaves_obrigatorias.issubset(dados.keys()):
            faltantes = chaves_obrigatorias - set(dados.keys())
            raise KeyError(f"Chaves obrigatórias faltando: {faltantes}")

class MaterialPDFFactory(MaterialEstudoFactory):
    """
    Factory concreta para criação de materiais de estudo no formato PDF.
    """

    def criar_material(self, dados: dict) -> MaterialEstudo: 
        """
        Cria e retorna um objeto do tipo MaterialPDF.

        Valida o número de páginas

        :param dados: dicionário contendo os dados necessários para criação do material
            Chaves esperadas no dicionário:
                - 'titulo': str
                - 'descricao': str
                - 'data_upload': datetime
                - 'autor': str
                - 'num_paginas': int
        :raises ValueError: Se num_paginas for inválido
        :raises TypeError: Se tipos estiverem incorretos
        :raises KeyError: Se chaves obrigatórias faltarem
        """
        # Validação de chaves obrigatórias
        self._validar_chaves_obrigatorias(dados, {'titulo', 'descricao', 'data_upload', 'autor', 'num_paginas'})
        
        # Validação de tipos
        if isinstance(dados['num_paginas'], bool) or not isinstance(dados['num_paginas'], int):
            raise TypeError(f"num_paginas deve ser int, recebido {type(dados['num_paginas']).__name__}")
        
        # Validação de valor
        if dados['num_paginas'] <= 0:
            raise ValueError(f"num_paginas deve ser positivo, recebido {dados['num_paginas']}")

        return MaterialPDF(
            titulo=dados['titulo'],
            descricao=dados['descricao'],
            data_upload=dados['data_upload'],
            autor=dados['autor'],
            num_paginas=dados['num_paginas']
            )

class MaterialVideoFactory(MaterialEstudoFactory):
    """
    Factory concreta para criação de materiais de estudo no formato Vídeo.
    """

    def criar_material(self, dados: dict) -> MaterialEstudo:
        """
        Cria e retorna um objeto do tipo MaterialVideo.

        Valida duração e codec.

        :param dados: dicionário contendo os dados necessários para criação do material
            Chaves esperadas no dicionário:
                - 'titulo': str
                - 'descricao': str
                - 'data_upload': datetime
                - 'autor': str
                - 'duracao_segundos': int
                - 'codec': str
        :raises ValueError: Se duração ou codec forem inválidos
        :raises TypeError: Se tipos estiverem incorretos
        :raises KeyError: Se chaves obrigatórias faltarem
        :return: instância de MaterialVideo
        """

        # Validação de chaves obrigatórias
        self._validar_chaves_obrigatorias(dados, {'titulo', 'descricao', 'data_upload', 'autor', 'duracao_segundos', 'codec'})
        
        # Validação de tipos
        if isinstance(dados['duracao_segundos'], bool) or not isinstance(dados['duracao_segundos'], int):
            raise TypeError(f"duracao_segundos deve ser int, recebido {type(dados['duracao_segundos']).__name__}")
        
        if not isinstance(dados['codec'], str):
            raise TypeError(f"codec deve ser str, recebido {type(dados['codec']).__name__}")
        
        # Validação de valores
        if dados['duracao_segundos'] <= 0:
            raise ValueError(f"duracao_segundos deve ser positiva, recebido {dados['duracao_segundos']}")
        
        if not dados['codec'].strip():
            raise ValueError("codec não pode ser vazio")

        return MaterialVideo(
            titulo=dados['titulo'],
            descricao=dados['descricao'],
            data_upload=dados['data_upload'],
            autor=dados['autor'],
            duracao_segundos=dados['duracao_segundos'],
            codec=dados['codec']
        )

class MaterialLinkFactory(MaterialEstudoFactory):
    """
    Factory concreta para criação de materiais de estudo no formato Link.
    """

    def criar_material(self, dados: dict) -> MaterialEstudo:
        """
        Cria e retorna um objeto do tipo MaterialLink.

        Valida tipo de conteúdo e URL.

        :param dados: dicionário contendo os dados necessários para criação do material
            Chaves esperadas no dicionário:
                - 'titulo': str
                - 'descricao': str
                - 'data_upload': datetime
                - 'autor': str
                - 'url': str
                - 'tipo_conteudo': str
        :raises ValueError: Se URL ou tipo_conteudo forem inválidos
        :raises TypeError: Se tipos estiverem incorretos
        :raises KeyError: Se chaves obrigatórias faltarem
        :return: instância de MaterialLink
        """

        # Validação de chaves obrigatórias
        self._validar_chaves_obrigatorias(dados, {'titulo', 'descricao', 'data_upload', 'autor', 'url', 'tipo_conteudo'})
        
        # Validação de tipos
        if not isinstance(dados['url'], str):
            raise TypeError(f"url deve ser str, recebido {type(dados['url']).__name__}")
        
        if not isinstance(dados['tipo_conteudo'], str):
            raise TypeError(f"tipo_conteudo deve ser str, recebido {type(dados['tipo_conteudo']).__name__}")
        
        # Validação de valores
        if not dados['url'].strip():
            raise ValueError("url não pode ser vazia")

        parsed = urlparse(dados['url'])
        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"url '{dados['url']}' não é uma URL válida (deve conter esquema e domínio)")
        
        if not dados['tipo_conteudo'].strip():
            raise ValueError("tipo_conteudo não pode ser vazio")

        return MaterialLink(
            titulo=dados['titulo'],
            descricao=dados['descricao'],
            data_upload=dados['data_upload'],
            autor=dados['autor'],
            url=dados['url'],
            tipo_conteudo=dados['tipo_conteudo']
        )
    
class MaterialEstudoFactoryManager:
    """
    Manager para detectar e criar materiais automaticamente por extensão.
    Centraliza a lógica de factory selection.
    """
    
    # Mapear extensões para factories
    EXTENSOES_SUPORTADAS = {
        'pdf': MaterialPDFFactory(),
        'mp4': MaterialVideoFactory(),
        'avi': MaterialVideoFactory(),
        'mkv': MaterialVideoFactory(),
        'mov': MaterialVideoFactory(),
        'webm': MaterialVideoFactory(),
        'mp3': MaterialVideoFactory(),  # Arquivos MP3 são tratados como mídia pela MaterialVideoFactory; use o codec de áudio apropriado (por exemplo, 'mp3') no campo 'codec'.
    }
    
    @classmethod
    def criar_por_extensao(cls, extensao: str, dados: dict) -> MaterialEstudo:
        """
        Cria material automaticamente detectando tipo pela extensão.
        
        :param extensao: extensão do arquivo (ex: 'pdf', 'mp4')
        :param dados: dicionário com dados do material
        :return: MaterialEstudo do tipo apropriado
        :raises ValueError: Se extensão não for suportada
        """
        extensao_normalizada = extensao.lower().lstrip('.')
        
        if extensao_normalizada not in cls.EXTENSOES_SUPORTADAS:
            tipos_validos = ', '.join(sorted(cls.EXTENSOES_SUPORTADAS.keys()))
            raise ValueError(
                f"Extensão '{extensao_normalizada}' não suportada. "
                f"Tipos válidos: {tipos_validos}"
            )
        
        factory = cls.EXTENSOES_SUPORTADAS[extensao_normalizada]
        return factory.criar_material(dados)
    
    @classmethod
    def registrar_extensao(cls, extensao: str, factory: MaterialEstudoFactory) -> None:
        """
        Registra uma nova extensão com sua factory correspondente.
        Permite extensibilidade do sistema.
        
        :param extensao: extensão do arquivo (ex: 'docx', 'pptx')
        :param factory: instância de MaterialEstudoFactory
        """
        cls.EXTENSOES_SUPORTADAS[extensao.lower().lstrip('.')] = factory
    
    @classmethod
    def extensoes_suportadas(cls) -> list[str]:
        """Retorna lista de extensões suportadas."""
        return list(cls.EXTENSOES_SUPORTADAS.keys())