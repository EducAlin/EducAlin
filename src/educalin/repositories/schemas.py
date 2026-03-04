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
    
    conn.commit()
    print("✅ Tabela 'usuarios' criada com sucesso!")


def create_turmas_tables(conn: sqlite3.Connection):
    """
    Cria as tabelas relacionadas a turmas e seus relacionamentos.
    
    Args:
        conn: Conexão ativa com o banco de dados
    """
    cursor = conn.cursor()
    
    # Tabela de Turmas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turmas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT UNIQUE NOT NULL,
            disciplina TEXT NOT NULL,
            semestre TEXT NOT NULL,
            professor_id INTEGER,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (professor_id) REFERENCES usuarios(id) ON DELETE SET NULL,
            CHECK(codigo != ''),
            CHECK(disciplina != ''),
            CHECK(semestre != '')
        )
    """)
    
    # Tabela intermediária Turma-Aluno (Many-to-Many)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS turma_alunos (
            turma_id INTEGER NOT NULL,
            aluno_id INTEGER NOT NULL,
            data_matricula TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            PRIMARY KEY (turma_id, aluno_id),
            FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE,
            FOREIGN KEY (aluno_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
    """)
    
    # Índices para performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_turmas_codigo ON turmas(codigo)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_turmas_professor ON turmas(professor_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_turma_alunos_turma ON turma_alunos(turma_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_turma_alunos_aluno ON turma_alunos(aluno_id)")
    
    conn.commit()
    print("✅ Tabelas 'turmas' e 'turma_alunos' criadas com sucesso!")
