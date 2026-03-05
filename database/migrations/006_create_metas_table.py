"""
Cria a tabela de metas de aprendizado.

depends: 001_create_usuarios_table
"""

from yoyo import step

__depends__ = ['001_create_usuarios_table']

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS metas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            descricao TEXT NOT NULL,
            valor_alvo REAL NOT NULL CHECK(valor_alvo > 0),
            prazo TIMESTAMP NOT NULL,
            progresso_atual REAL NOT NULL DEFAULT 0.0 CHECK(progresso_atual >= 0),
            meta_atingida_em TIMESTAMP,
            criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (aluno_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            CHECK(descricao != ''),
            CHECK(progresso_atual <= valor_alvo)
        )
        """,
        "DROP TABLE IF EXISTS metas"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_metas_aluno ON metas(aluno_id)",
        "DROP INDEX IF EXISTS idx_metas_aluno"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_metas_prazo ON metas(prazo)",
        "DROP INDEX IF EXISTS idx_metas_prazo"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_metas_atingida ON metas(meta_atingida_em)",
        "DROP INDEX IF EXISTS idx_metas_atingida"
    )
]
