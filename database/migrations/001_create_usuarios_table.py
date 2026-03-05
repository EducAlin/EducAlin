"""
Cria a tabela de usuários com Single Table Inheritance (STI).

depends:
"""

from yoyo import step

__depends__ = []

steps = [
    step(
        """
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
        """,
        "DROP TABLE IF EXISTS usuarios"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)",
        "DROP INDEX IF EXISTS idx_usuarios_email"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_usuarios_tipo ON usuarios(tipo_usuario)",
        "DROP INDEX IF EXISTS idx_usuarios_tipo"
    )
]
