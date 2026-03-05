"""
Cria a tabela de materiais de estudo com Single Table Inheritance (STI).

depends: 001_create_usuarios_table
"""

from yoyo import step

__depends__ = ['001_create_usuarios_table']

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS materiais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_material TEXT NOT NULL CHECK(tipo_material IN ('pdf', 'video', 'link')),
            
            -- Campos comuns a todos os materiais
            titulo TEXT NOT NULL,
            descricao TEXT NOT NULL,
            autor_id INTEGER NOT NULL,
            data_upload TIMESTAMP NOT NULL,
            
            -- Campos específicos (podem ser NULL dependendo do tipo)
            num_paginas INTEGER,          -- PDF
            duracao_segundos INTEGER,     -- Video
            codec TEXT,                   -- Video
            url TEXT,                     -- Link
            tipo_conteudo TEXT,           -- Link
            
            FOREIGN KEY (autor_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            CHECK(titulo != ''),
            CHECK(descricao != '')
        )
        """,
        "DROP TABLE IF EXISTS materiais"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_materiais_tipo ON materiais(tipo_material)",
        "DROP INDEX IF EXISTS idx_materiais_tipo"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_materiais_autor ON materiais(autor_id)",
        "DROP INDEX IF EXISTS idx_materiais_autor"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_materiais_data ON materiais(data_upload)",
        "DROP INDEX IF EXISTS idx_materiais_data"
    )
]
