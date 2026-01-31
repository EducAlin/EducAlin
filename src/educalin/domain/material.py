from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass, field

#----------------------------------------------------------------#
#               CLASSE ABSTRATA MATERIAL DE ESTUDO               #
#----------------------------------------------------------------#

@dataclass
class MaterialEstudo(ABC):
    _titulo: str = field(init=False, repr=False)
    _descricao: str = field(init=False, repr=False)
    _data_upload: datetime 
    _autor: str = field(init=False, repr=False) # autor deve vir da classe Professor (autor: Professor)

    def __init__(self, titulo: str, descricao: str, autor: str, data_upload: datetime):
        self._titulo = titulo
        self._descricao = descricao
        self._autor = autor
        self._validar_data_upload(data_upload) 
        self._data_upload = data_upload

    # Titulo
    @property
    def titulo(self) -> str:
        return self._titulo
    
    @titulo.setter
    def titulo(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("O título deve ser uma string não vazia.")
        if not valor.strip():
            raise ValueError("O título não pode ser vazio.")
        self._titulo = valor.strip()

    # Descrição
    @property
    def descricao(self) -> str:
        return self._descricao
    
    @descricao.setter
    def descricao(self, valor: str) -> None:
        if not isinstance(valor, str):
            raise ValueError("A descrição deve ser uma string.")
        if not valor.strip():
            raise ValueError("A descrição não pode ser vazia.")
        self._descricao = valor.strip()

    # Autor
    @property
    def autor(self) -> str:
        return self._autor
    
    @autor.setter
    def autor(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("O autor deve ser uma string não vazia.")
        if not valor.strip():
            raise ValueError("O autor não pode ser vazio.")
        self._autor = valor.strip()


    # Data de Upload (IMUTÁVEL)
    @property
    def data_upload(self) -> datetime:
        return self._data_upload
    
    def _validar_data_upload(self, data: datetime) -> None:
        if not isinstance(data, datetime):
            raise ValueError("A data de upload deve ser um objeto datetime.")
        if data > datetime.now():
            raise ValueError("A data de upload não pode ser no futuro.")
        
    # Métodos abstratos
    @abstractmethod
    def validar_formato(self) -> bool:
        """
        Método abstrato para validar o formato específico do material de estudo.
        Deve ser implementado por subclasses concretas.
        """
        pass
    
    @abstractmethod
    def obter_tamanho(self) -> int:
        """
        Método abstrato para obter o tamanho do material de estudo.
        Deve ser implementado por subclasses concretas.
        """
        pass

    # Representação
    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"Título: {self.titulo}, "
            f"Descrição: {self.descricao}, "
            f"Autor: {self.autor}, "
            f"Data de Upload: {self.data_upload.strftime('%Y-%m-%d %H:%M:%S')}"
        )

#----------------------------------------------------------------#
#                     SUBCLASSE MATERIAL PDF                     #
#----------------------------------------------------------------#

@dataclass
class MaterialPDF(MaterialEstudo):
    _num_paginas: int = 0

    def __init__(self, titulo: str, descricao: str, autor: str, data_upload: datetime, num_paginas: int):
        super().__init__(titulo, descricao, autor, data_upload)
        self._num_paginas = num_paginas

    # Número de páginas
    @property
    def num_paginas(self) -> int:
        return self._num_paginas
    
    @num_paginas.setter
    def num_paginas(self, valor: int) -> None:
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("O número de páginas deve ser um inteiro positivo.")
        self._num_paginas = valor

    # Métodos abstratos
    def validar_formato(self) -> bool:
        """
        Validação do formato PDF a partir do número de páginas.
        """
        if not isinstance(self.num_paginas, int) or self.num_paginas <= 0:
            raise ValueError("O número de páginas deve ser um inteiro positivo.")
        return True
    
    def obter_tamanho(self) -> int:
        """
        Para PDF, o tamanho é representado pelo número de páginas.
        """
        return self.num_paginas
    
    # Método específico
    def extrair_texto(self) -> str:
        """
        Método específico para extrair texto de um PDF(Lógica simulada).
        """
        return "Texto extraído do PDF."
    
#----------------------------------------------------------------#
#                  SUBCLASSE MATERIAL VÍDEO                      #
#----------------------------------------------------------------#

@dataclass
class MaterialVideo(MaterialEstudo):
    _codec: str = ""
    _duracao_segundos: int = 0

    def __init__(self, titulo: str, descricao: str, autor: str, data_upload: datetime, duracao_segundos: int, codec: str):
        super().__init__(titulo, descricao, autor, data_upload)
        self._duracao_segundos = duracao_segundos
        self._codec = codec

    # Duração em segundos
    @property
    def duracao_segundos(self) -> int:
        return self._duracao_segundos
    
    @duracao_segundos.setter
    def duracao_segundos(self, valor: int) -> None:
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("A duração em segundos deve ser um inteiro positivo.")
        self._duracao_segundos = valor

    # codec
    @property
    def codec(self) -> str:
        return self._codec

    @codec.setter
    def codec(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("O codec deve ser uma string não vazia.")
        self._codec = valor.strip()            

    # Métodos específicos
    def validar_formato(self) -> bool:
        """
        Validação do formato de vídeo a apartir do codec.
        """
        if not isinstance(self.codec, str) or not self.codec.strip():
            raise ValueError("O codec deve ser uma string não vazia.")
        return True
    
    def gerar_thumbnail(self) -> str:
        """
        Método específico para gerar uma miniatura do vídeo(Simulado).
        """
        return "Caminho/para/thumbnail.jpg"
    
    def obter_tamanho(self) -> int:
        """
        Para vídeo, o tamanho é representado pela duração em segundos.
        """
        return self.duracao_segundos
    
#----------------------------------------------------------------#
#                 SUBCLASSE MATERIAL LINK                        #
#----------------------------------------------------------------#

@dataclass
class MaterialLink(MaterialEstudo):
    _url: str
    _tipo_conteudo: str

    def __init__(self, titulo: str, descricao: str, autor: str, data_upload: datetime, url: str, tipo_conteudo: str):
        super().__init__(titulo, descricao, autor, data_upload)
        self._url = url
        self._tipo_conteudo = tipo_conteudo

    # URL
    @property
    def url(self) -> str:
        return self._url
    
    @url.setter
    def url(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("A URL deve ser uma string não vazia.")
        self._url = valor.strip()

    # Tipo de conteúdo
    @property
    def tipo_conteudo(self) -> str:
        return self._tipo_conteudo
    
    @tipo_conteudo.setter
    def tipo_conteudo(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("O tipo de conteúdo deve ser uma string não vazia.")
        self._tipo_conteudo = valor.strip()

    # Métodos específicos
    def validar_formato(self) -> bool:
        """
        Validação do formato do link a partir da URL.
        """
        if not isinstance(self.url, str) or not self.url.strip():
            raise ValueError("A URL deve ser uma string não vazia.")
        return True
    
    def verificar_disponibilidade(self) -> bool:
        """
        Método específico para verificar a disponibilidade do link(Simulado).
        """
        return True
    
    def obter_tamanho(self) -> int:
        """
        Para link, o tamanho é representado pelo comprimento da URL.
        """
        return len(self.url)


