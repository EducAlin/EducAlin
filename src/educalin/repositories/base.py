"""
Configuração base do banco de dados SQLite (sem SQLAlchemy).

Este módulo fornece funções para conexão e inicialização do banco usando sqlite3.
"""

import sqlite3
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

# Diretório do banco de dados
DB_DIR = Path(__file__).parent.parent.parent.parent / "database"
DB_DIR.mkdir(exist_ok=True)

# Caminho do banco de dados SQLite
DATABASE_PATH = DB_DIR / "educalin.db"


def get_connection() -> sqlite3.Connection:
    """
    Cria e retorna uma conexão com o banco de dados SQLite.
    
    A conexão é configurada para:
    - Retornar resultados como dicionários (Row Factory)
    - Habilitar foreign keys
    
    Returns:
        sqlite3.Connection: Conexão ativa com o banco
    """
    conn = sqlite3.connect(str(DATABASE_PATH))

    # Permite acessar colunas por nome
    conn.row_factory = sqlite3.Row  

    # Habilita foreign keys
    conn.execute("PRAGMA foreign_keys = ON")  
    
    return conn


@contextmanager
def get_db():
    """
    Context manager que fornece uma conexão de banco de dados.
    
    Uso recomendado:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuarios")
            # ...
        # Conexão fecha automaticamente
    
    Yields:
        sqlite3.Connection: Conexão com o banco de dados
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """
    Inicializa o banco de dados, criando todas as tabelas.
    
    Esta função deve ser chamada uma vez na inicialização da aplicação.
    Importa e executa todos os schemas dos modelos.
    """
    from .schemas import create_all_tables
    
    with get_db() as conn:
        create_all_tables(conn)
        conn.commit()
    
    print(f"[OK] Banco de dados inicializado em: {DATABASE_PATH}")
