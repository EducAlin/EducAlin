"""
Modelos de Material usando Single Table Inheritance (STI).

Hierarquia: MaterialModel -> MaterialPDFModel, MaterialVideoModel, MaterialLinkModel
Todos armazenados na mesma tabela 'materiais' com discriminador 'tipo_material'.
"""

import sqlite3
from typing import Optional
from datetime import datetime
from .base_model import BaseModel


class MaterialModel(BaseModel):
    """
    Classe base para materiais de estudo usando Single Table Inheritance.
    
    O discriminador 'tipo_material' determina o tipo concreto:
    - 'pdf' -> MaterialPDFModel
    - 'video' -> MaterialVideoModel
    - 'link' -> MaterialLinkModel
    """
    
    def __init__(
        self,
        id: int,
        tipo_material: str,
        titulo: str,
        descricao: str,
        autor_id: int,  # ForeignKey para usuarios (professor)
        data_upload: datetime,
        # Campos específicos de cada tipo (podem ser None)
        num_paginas: Optional[int] = None,  # PDF
        duracao_segundos: Optional[int] = None,  # Video
        codec: Optional[str] = None,  # Video
        url: Optional[str] = None,  # Link
        tipo_conteudo: Optional[str] = None,  # Link
    ):
        self.id = id
        self.tipo_material = tipo_material
        self.titulo = titulo
        self.descricao = descricao
        self.autor_id = autor_id
        self.data_upload = data_upload
        self.num_paginas = num_paginas
        self.duracao_segundos = duracao_segundos
        self.codec = codec
        self.url = url
        self.tipo_conteudo = tipo_conteudo
    
    @staticmethod
    def _criar_instancia_polimórfica(row: sqlite3.Row) -> 'MaterialModel':
        """
        Factory method que retorna a subclasse correta baseada em tipo_material.
        Implementa polimorfismo em consultas.
        """
        tipo = row['tipo_material']
        
        if tipo == 'pdf':
            return MaterialPDFModel(
                id=row['id'],
                tipo_material=row['tipo_material'],
                titulo=row['titulo'],
                descricao=row['descricao'],
                autor_id=row['autor_id'],
                data_upload=datetime.fromisoformat(row['data_upload']),
                num_paginas=row['num_paginas'],
            )
        elif tipo == 'video':
            return MaterialVideoModel(
                id=row['id'],
                tipo_material=row['tipo_material'],
                titulo=row['titulo'],
                descricao=row['descricao'],
                autor_id=row['autor_id'],
                data_upload=datetime.fromisoformat(row['data_upload']),
                duracao_segundos=row['duracao_segundos'],
                codec=row['codec'],
            )
        elif tipo == 'link':
            return MaterialLinkModel(
                id=row['id'],
                tipo_material=row['tipo_material'],
                titulo=row['titulo'],
                descricao=row['descricao'],
                autor_id=row['autor_id'],
                data_upload=datetime.fromisoformat(row['data_upload']),
                url=row['url'],
                tipo_conteudo=row['tipo_conteudo'],
            )
        else:
            # Fallback para MaterialModel genérico
            return MaterialModel(
                id=row['id'],
                tipo_material=row['tipo_material'],
                titulo=row['titulo'],
                descricao=row['descricao'],
                autor_id=row['autor_id'],
                data_upload=datetime.fromisoformat(row['data_upload']),
            )
    
    @classmethod
    def buscar_por_id(cls, conn: sqlite3.Connection, material_id: int) -> Optional['MaterialModel']:
        """Busca material por ID, retornando a subclasse correta."""
        cursor = conn.execute(
            "SELECT * FROM materiais WHERE id = ?",
            (material_id,)
        )
        row = cursor.fetchone()
        return cls._criar_instancia_polimórfica(row) if row else None
    
    @classmethod
    def listar_todos(cls, conn: sqlite3.Connection, tipo_material: Optional[str] = None) -> list['MaterialModel']:
        """
        Lista todos os materiais, opcionalmente filtrados por tipo.
        Retorna instâncias polimórficas corretas.
        """
        if tipo_material:
            cursor = conn.execute(
                "SELECT * FROM materiais WHERE tipo_material = ? ORDER BY data_upload DESC",
                (tipo_material,)
            )
        else:
            cursor = conn.execute("SELECT * FROM materiais ORDER BY data_upload DESC")
        
        return [cls._criar_instancia_polimórfica(row) for row in cursor.fetchall()]
    
    @classmethod
    def listar_por_autor(cls, conn: sqlite3.Connection, autor_id: int) -> list['MaterialModel']:
        """Lista todos os materiais de um autor específico."""
        cursor = conn.execute(
            "SELECT * FROM materiais WHERE autor_id = ? ORDER BY data_upload DESC",
            (autor_id,)
        )
        return [cls._criar_instancia_polimórfica(row) for row in cursor.fetchall()]
    
    def deletar(self, conn: sqlite3.Connection) -> None:
        """Deleta o material do banco de dados."""
        conn.execute("DELETE FROM materiais WHERE id = ?", (self.id,))
        conn.commit()


class MaterialPDFModel(MaterialModel):
    """
    Modelo para Material no formato PDF.
    
    Atributos específicos:
    - num_paginas: Número de páginas do PDF
    """
    
    def __init__(
        self,
        id: int,
        tipo_material: str,
        titulo: str,
        descricao: str,
        autor_id: int,
        data_upload: datetime,
        num_paginas: int,
    ):
        super().__init__(
            id=id,
            tipo_material=tipo_material,
            titulo=titulo,
            descricao=descricao,
            autor_id=autor_id,
            data_upload=data_upload,
            num_paginas=num_paginas,
        )
    
    @classmethod
    def criar(
        cls,
        conn: sqlite3.Connection,
        titulo: str,
        descricao: str,
        autor_id: int,
        num_paginas: int,
    ) -> int:
        """Cria um novo material PDF."""
        cursor = conn.execute(
            """
            INSERT INTO materiais (tipo_material, titulo, descricao, autor_id, data_upload, num_paginas)
            VALUES ('pdf', ?, ?, ?, ?, ?)
            """,
            (titulo, descricao, autor_id, datetime.now().isoformat(), num_paginas)
        )
        conn.commit()
        return cursor.lastrowid


class MaterialVideoModel(MaterialModel):
    """
    Modelo para Material no formato Vídeo.
    
    Atributos específicos:
    - duracao_segundos: Duração do vídeo em segundos
    - codec: Codec do vídeo
    """
    
    def __init__(
        self,
        id: int,
        tipo_material: str,
        titulo: str,
        descricao: str,
        autor_id: int,
        data_upload: datetime,
        duracao_segundos: int,
        codec: str,
    ):
        super().__init__(
            id=id,
            tipo_material=tipo_material,
            titulo=titulo,
            descricao=descricao,
            autor_id=autor_id,
            data_upload=data_upload,
            duracao_segundos=duracao_segundos,
            codec=codec,
        )
    
    @classmethod
    def criar(
        cls,
        conn: sqlite3.Connection,
        titulo: str,
        descricao: str,
        autor_id: int,
        duracao_segundos: int,
        codec: str,
    ) -> int:
        """Cria um novo material de vídeo."""
        cursor = conn.execute(
            """
            INSERT INTO materiais (tipo_material, titulo, descricao, autor_id, data_upload, duracao_segundos, codec)
            VALUES ('video', ?, ?, ?, ?, ?, ?)
            """,
            (titulo, descricao, autor_id, datetime.now().isoformat(), duracao_segundos, codec)
        )
        conn.commit()
        return cursor.lastrowid


class MaterialLinkModel(MaterialModel):
    """
    Modelo para Material no formato Link.
    
    Atributos específicos:
    - url: URL do material
    - tipo_conteudo: Tipo de conteúdo (artigo, vídeo, curso, etc)
    """
    
    def __init__(
        self,
        id: int,
        tipo_material: str,
        titulo: str,
        descricao: str,
        autor_id: int,
        data_upload: datetime,
        url: str,
        tipo_conteudo: str,
    ):
        super().__init__(
            id=id,
            tipo_material=tipo_material,
            titulo=titulo,
            descricao=descricao,
            autor_id=autor_id,
            data_upload=data_upload,
            url=url,
            tipo_conteudo=tipo_conteudo,
        )
    
    @classmethod
    def criar(
        cls,
        conn: sqlite3.Connection,
        titulo: str,
        descricao: str,
        autor_id: int,
        url: str,
        tipo_conteudo: str,
    ) -> int:
        """Cria um novo material link."""
        cursor = conn.execute(
            """
            INSERT INTO materiais (tipo_material, titulo, descricao, autor_id, data_upload, url, tipo_conteudo)
            VALUES ('link', ?, ?, ?, ?, ?, ?)
            """,
            (titulo, descricao, autor_id, datetime.now().isoformat(), url, tipo_conteudo)
        )
        conn.commit()
        return cursor.lastrowid
