"""
Repository para operações de banco de dados com Materiais de Estudo.

Implementa o padrão Repository para abstrair operações de persistência
de materiais usando SQL puro (SQLite3).
Suporta Single Table Inheritance (STI) para diferentes tipos de materiais.
"""

import sqlite3
from typing import Optional, Dict, Any, List
from datetime import datetime

from .base_model import BaseModel
from .material_models import MaterialModel, MaterialPDFModel, MaterialVideoModel, MaterialLinkModel
from .base import get_connection


class MaterialRepository:
    """
    Repository para operações CRUD de materiais de estudo.
    
    Utiliza SQL puro para interagir com a tabela 'materiais'.
    Suporta Single Table Inheritance (STI) para diferentes tipos de materiais:
    - PDF: com num_paginas
    - Vídeo: com duracao_segundos e codec
    - Link: com url e tipo_conteudo
    
    Example:
        >>> repo = MaterialRepository()
        >>> material_id = repo.criar({
        ...     'tipo_material': 'pdf',
        ...     'titulo': 'Introdução POO',
        ...     'descricao': 'Conceitos básicos de POO',
        ...     'autor_id': 1,
        ...     'topico': 'Programação',
        ...     'num_paginas': 50
        ... })
        >>> material = repo.buscar_por_id(material_id)
    """
    
    def __init__(self, conn: Optional[sqlite3.Connection] = None):
        """
        Inicializa o repository.
        
        Args:
            conn: Conexão SQLite opcional. Se não fornecida, cria uma nova.
        """
        self.conn = conn or get_connection()
        self._own_connection = conn is None
    
    def __enter__(self):
        """Suporte para context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Fecha conexão ao sair do context manager (se for própria)."""
        if self._own_connection:
            self.conn.close()
    
    def criar(self, material_data: Dict[str, Any]) -> int:
        """
        Cria um novo material no banco de dados.
        
        Detecta o tipo de material baseado nos campos presentes no dicionário
        e cria a instância apropriada.
        
        Args:
            material_data: Dicionário com os dados do material:
                - tipo_material: 'pdf', 'video' ou 'link' (obrigatório)
                - titulo: Título do material (obrigatório)
                - descricao: Descrição do material (obrigatório)
                - autor_id: ID do professor que criou (obrigatório, FK)
                - topico: Tópico/área do material (opcional)
                - Campos específicos por tipo:
                    PDF: num_paginas (int, obrigatório)
                    Vídeo: duracao_segundos (int), codec (str) (obrigatório)
                    Link: url (str), tipo_conteudo (str) (obrigatório)
        
        Returns:
            int: ID do material criado
        
        Raises:
            ValueError: Se dados obrigatórios estiverem faltando ou inválidos
            sqlite3.IntegrityError: Se houver violação de constraints
        
        Example (PDF):
            >>> repo = MaterialRepository()
            >>> pdf_id = repo.criar({
            ...     'tipo_material': 'pdf',
            ...     'titulo': 'POO Avançado',
            ...     'descricao': 'Padrões de design',
            ...     'autor_id': 5,
            ...     'topico': 'Design Patterns',
            ...     'num_paginas': 120
            ... })
        
        Example (Vídeo):
            >>> video_id = repo.criar({
            ...     'tipo_material': 'video',
            ...     'titulo': 'Tutorial Python',
            ...     'descricao': 'Introdução a Python',
            ...     'autor_id': 5,
            ...     'topico': 'Linguagens',
            ...     'duracao_segundos': 3600,
            ...     'codec': 'h264'
            ... })
        
        Example (Link):
            >>> link_id = repo.criar({
            ...     'tipo_material': 'link',
            ...     'titulo': 'Artigo sobre POO',
            ...     'descricao': 'Referência completa',
            ...     'autor_id': 5,
            ...     'topico': 'Referências',
            ...     'url': 'https://example.com/poo',
            ...     'tipo_conteudo': 'artigo'
            ... })
        """
        # Validações de campos obrigatórios comuns
        tipo_material = material_data.get('tipo_material')
        titulo = material_data.get('titulo')
        descricao = material_data.get('descricao')
        autor_id = material_data.get('autor_id')
        
        if not all([tipo_material, titulo, descricao, autor_id]):
            raise ValueError(
                "Campos obrigatórios: tipo_material, titulo, descricao, autor_id"
            )
        
        if tipo_material not in ('pdf', 'video', 'link'):
            raise ValueError("tipo_material deve ser: 'pdf', 'video' ou 'link'")
        
        # Validações básicas
        titulo = BaseModel._validate_not_empty(titulo, "Título")
        descricao = BaseModel._validate_not_empty(descricao, "Descrição")
        
        if not isinstance(autor_id, int) or autor_id <= 0:
            raise ValueError("autor_id deve ser um inteiro positivo")
        
        # Validar tópico se fornecido
        topico = material_data.get('topico')
        if topico is not None:
            topico = BaseModel._validate_not_empty(topico, "Tópico")
        
        # Validações e parâmetros específicos por tipo
        num_paginas = None
        duracao_segundos = None
        codec = None
        url = None
        tipo_conteudo = None
        
        if tipo_material == 'pdf':
            num_paginas = material_data.get('num_paginas')
            if num_paginas is None:
                raise ValueError("num_paginas é obrigatório para materiais PDF")
            if not isinstance(num_paginas, int) or num_paginas <= 0:
                raise ValueError("num_paginas deve ser um inteiro positivo")
        
        elif tipo_material == 'video':
            duracao_segundos = material_data.get('duracao_segundos')
            codec = material_data.get('codec')
            
            if duracao_segundos is None:
                raise ValueError("duracao_segundos é obrigatório para materiais Vídeo")
            if not isinstance(duracao_segundos, int) or duracao_segundos <= 0:
                raise ValueError("duracao_segundos deve ser um inteiro positivo")
            
            if not codec:
                raise ValueError("codec é obrigatório para materiais Vídeo")
            codec = BaseModel._validate_not_empty(codec, "Codec")
        
        elif tipo_material == 'link':
            url = material_data.get('url')
            tipo_conteudo = material_data.get('tipo_conteudo')
            
            if not url:
                raise ValueError("url é obrigatória para materiais Link")
            url = BaseModel._validate_not_empty(url, "URL")
            
            # Validação básica de URL
            if not ('://' in url):
                raise ValueError("url deve conter um protocolo válido (ex: https://)")
            
            if not tipo_conteudo:
                raise ValueError("tipo_conteudo é obrigatório para materiais Link")
            tipo_conteudo = BaseModel._validate_not_empty(tipo_conteudo, "Tipo de conteúdo")
        
        # Inserir no banco
        try:
            cursor = self.conn.execute(
                """
                INSERT INTO materiais 
                (tipo_material, titulo, descricao, autor_id, topico, data_upload,
                 num_paginas, duracao_segundos, codec, url, tipo_conteudo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tipo_material, titulo, descricao, autor_id, topico,
                    datetime.now().isoformat(),
                    num_paginas, duracao_segundos, codec, url, tipo_conteudo
                )
            )
            self.conn.commit()
            return cursor.lastrowid
        
        except sqlite3.IntegrityError as e:
            self.conn.rollback()
            if 'autor_id' in str(e):
                raise ValueError(f"Autor com ID {autor_id} não existe")
            else:
                raise ValueError(f"Erro de integridade: {e}")
    
    def buscar_por_id(self, material_id: int) -> Optional[MaterialModel]:
        """
        Busca um material por ID.
        
        Retorna a subclasse polimórfica correta (PDF, Vídeo ou Link)
        baseada no tipo_material armazenado.
        
        Args:
            material_id: ID do material
        
        Returns:
            MaterialModel (ou subclasse) se encontrado, None caso contrário
        
        Example:
            >>> repo = MaterialRepository()
            >>> material = repo.buscar_por_id(5)
            >>> if material:
            ...     print(f"{material.tipo_material}: {material.titulo}")
            ...     if isinstance(material, MaterialPDFModel):
            ...         print(f"Páginas: {material.num_paginas}")
        """
        cursor = self.conn.execute(
            "SELECT * FROM materiais WHERE id = ?",
            (material_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return MaterialModel._criar_instancia_polimórfica(row)
        return None
    
    def listar_por_professor(self, professor_id: int) -> List[MaterialModel]:
        """
        Lista todos os materiais criados por um professor específico.
        
        Retorna os materiais em ordem decrescente de data de upload.
        
        Args:
            professor_id: ID do professor (autor_id)
        
        Returns:
            Lista de MaterialModel (com subclasses apropriadas)
        
        Example:
            >>> repo = MaterialRepository()
            >>> materiais = repo.listar_por_professor(5)
            >>> for material in materiais:
            ...     print(f"{material.titulo} ({material.tipo_material})")
        """
        if not isinstance(professor_id, int) or professor_id <= 0:
            raise ValueError("professor_id deve ser um inteiro positivo")
        
        cursor = self.conn.execute(
            """
            SELECT * FROM materiais 
            WHERE autor_id = ? 
            ORDER BY data_upload DESC
            """,
            (professor_id,)
        )
        
        return [MaterialModel._criar_instancia_polimórfica(row) for row in cursor.fetchall()]
    
    def buscar_por_topico(self, topico: str) -> List[MaterialModel]:
        """
        Lista todos os materiais de um tópico específico.
        
        A busca é case-insensitive e retorna resultados
        em ordem decrescente de data de upload.
        
        Args:
            topico: Tópico/área do material (ex: 'Programação', 'Design Patterns')
        
        Returns:
            Lista de MaterialModel (com subclasses apropriadas)
        
        Example:
            >>> repo = MaterialRepository()
            >>> materiais = repo.buscar_por_topico('Programação')
            >>> print(f"Encontrados {len(materiais)} materiais")
        """
        if not topico or not isinstance(topico, str):
            raise ValueError("topico deve ser uma string não-vazia")
        
        topico = topico.strip()
        
        cursor = self.conn.execute(
            """
            SELECT * FROM materiais 
            WHERE LOWER(topico) = LOWER(?) 
            ORDER BY data_upload DESC
            """,
            (topico,)
        )
        
        return [MaterialModel._criar_instancia_polimórfica(row) for row in cursor.fetchall()]
    
    def excluir(self, material_id: int) -> bool:
        """
        Exclui um material do banco de dados.
        
        Args:
            material_id: ID do material a ser deletado
        
        Returns:
            bool: True se deletou com sucesso, False se material não existe
        
        Raises:
            ValueError: Se material_id for inválido
        
        Example:
            >>> repo = MaterialRepository()
            >>> sucesso = repo.excluir(5)
            >>> if sucesso:
            ...     print("Material deletado")
            ... else:
            ...     print("Material não encontrado")
        """
        if not isinstance(material_id, int) or material_id <= 0:
            raise ValueError("material_id deve ser um inteiro positivo")
        
        # Verificar se existe
        material = self.buscar_por_id(material_id)
        if not material:
            return False
        
        try:
            cursor = self.conn.execute(
                "DELETE FROM materiais WHERE id = ?",
                (material_id,)
            )
            self.conn.commit()
            return cursor.rowcount > 0
        
        except sqlite3.Error as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao deletar material: {e}")
    
    def listar_todos(self, tipo_material: Optional[str] = None) -> List[MaterialModel]:
        """
        Lista todos os materiais, opcionalmente filtrados por tipo.
        
        Args:
            tipo_material: (opcional) Filtrar por tipo: 'pdf', 'video' ou 'link'
        
        Returns:
            Lista de MaterialModel (com subclasses apropriadas)
        
        Example:
            >>> repo = MaterialRepository()
            >>> todos = repo.listar_todos()
            >>> pdfs = repo.listar_todos('pdf')
        """
        if tipo_material:
            if tipo_material not in ('pdf', 'video', 'link'):
                raise ValueError("tipo_material deve ser: 'pdf', 'video' ou 'link'")
            
            cursor = self.conn.execute(
                """
                SELECT * FROM materiais 
                WHERE tipo_material = ? 
                ORDER BY data_upload DESC
                """,
                (tipo_material,)
            )
        else:
            cursor = self.conn.execute(
                "SELECT * FROM materiais ORDER BY data_upload DESC"
            )
        
        return [MaterialModel._criar_instancia_polimórfica(row) for row in cursor.fetchall()]
    
    def contar(self, tipo_material: Optional[str] = None, professor_id: Optional[int] = None) -> int:
        """
        Conta a quantidade de materiais, opcionalmente filtrados.
        
        Args:
            tipo_material: (opcional) Filtrar por tipo: 'pdf', 'video' ou 'link'
            professor_id: (opcional) Filtrar por professor (autor)
        
        Returns:
            int: Quantidade de materiais encontrados
        
        Example:
            >>> repo = MaterialRepository()
            >>> total = repo.contar()
            >>> pdfs = repo.contar(tipo_material='pdf')
            >>> materiais_prof = repo.contar(professor_id=5)
        """
        query = "SELECT COUNT(*) as total FROM materiais WHERE 1=1"
        params = []
        
        if tipo_material:
            if tipo_material not in ('pdf', 'video', 'link'):
                raise ValueError("tipo_material deve ser: 'pdf', 'video' ou 'link'")
            query += " AND tipo_material = ?"
            params.append(tipo_material)
        
        if professor_id:
            if not isinstance(professor_id, int) or professor_id <= 0:
                raise ValueError("professor_id deve ser um inteiro positivo")
            query += " AND autor_id = ?"
            params.append(professor_id)
        
        cursor = self.conn.execute(query, params)
        result = cursor.fetchone()
        return result['total'] if result else 0
    
    def atualizar_topico(self, material_id: int, novo_topico: Optional[str]) -> bool:
        """
        Atualiza o tópico de um material existente.
        
        Args:
            material_id: ID do material
            novo_topico: Novo tópico (pode ser None para limpar)
        
        Returns:
            bool: True se atualizou com sucesso, False se não encontrou
        
        Raises:
            ValueError: Se dados inválidos forem fornecidos
        
        Example:
            >>> repo = MaterialRepository()
            >>> sucesso = repo.atualizar_topico(5, 'Programação Avançada')
            >>> repo.atualizar_topico(5, None)  # Remove tópico
        """
        if not isinstance(material_id, int) or material_id <= 0:
            raise ValueError("material_id deve ser um inteiro positivo")
        
        # Validar tópico se fornecido
        if novo_topico is not None:
            if not isinstance(novo_topico, str):
                raise ValueError("novo_topico deve ser string ou None")
            novo_topico = novo_topico.strip() if novo_topico else None
        
        # Verificar existência
        material = self.buscar_por_id(material_id)
        if not material:
            return False
        
        try:
            self.conn.execute(
                "UPDATE materiais SET topico = ? WHERE id = ?",
                (novo_topico, material_id)
            )
            self.conn.commit()
            return True
        
        except sqlite3.Error as e:
            self.conn.rollback()
            raise ValueError(f"Erro ao atualizar tópico: {e}")
