"""
Schema da tabela de usuários com Single Table Inheritance (STI).

Define apenas a tabela 'usuarios' que armazena Professor, Coordenador e Aluno
em uma única tabela usando o padrão Single Table Inheritance.
"""

import sqlite3


def create_usuarios_table(conn: sqlite3.Connection):
    """
    Cria a tabela de usuários com Single Table Inheritance.
    
    Args:
        conn: Conexão ativa com o banco de dados
    """
    cursor = conn.cursor()
    
    # Tabela de Usuários com Single Table Inheritance
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_usuario TEXT NOT NULL CHECK(tipo_usuario IN ('professor', 'coordenador', 'aluno')),
            
            -- Campos comuns a todos os usuários
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            
            -- Campos específicos (podem ser NULL dependendo do tipo)
            registro_funcional TEXT UNIQUE,  -- Professor
            codigo_coordenacao TEXT UNIQUE,  -- Coordenador
            matricula TEXT UNIQUE,           -- Aluno
            
            -- Timestamps
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios(tipo_usuario)")
    
    print("✅ Tabela 'usuarios' criada com sucesso!")
