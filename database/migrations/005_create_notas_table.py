"""
Cria a tabela de notas (classe de associação entre aluno e avaliação).

depends: 001_create_usuarios_table, 004_create_avaliacoes_table
"""

from yoyo import step

__depends__ = ['001_create_usuarios_table', '004_create_avaliacoes_table']

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS notas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            avaliacao_id INTEGER NOT NULL,
            valor REAL NOT NULL CHECK(valor >= 0),
            data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (aluno_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            FOREIGN KEY (avaliacao_id) REFERENCES avaliacoes(id) ON DELETE CASCADE,
            UNIQUE(aluno_id, avaliacao_id)
        )
        """,
        "DROP TABLE IF EXISTS notas"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_notas_aluno ON notas(aluno_id)",
        "DROP INDEX IF EXISTS idx_notas_aluno"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_notas_avaliacao ON notas(avaliacao_id)",
        "DROP INDEX IF EXISTS idx_notas_avaliacao"
    )
]
