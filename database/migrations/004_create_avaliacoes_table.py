"""
Cria a tabela de avaliações.

depends: 002_create_turmas_tables
"""

from yoyo import step

__depends__ = ['002_create_turmas_tables']

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS avaliacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            data DATE NOT NULL,
            valor_maximo REAL NOT NULL CHECK(valor_maximo > 0),
            peso REAL NOT NULL CHECK(peso >= 0 AND peso <= 1),
            turma_id INTEGER NOT NULL,
            topico TEXT,
            criada_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (turma_id) REFERENCES turmas(id) ON DELETE CASCADE,
            CHECK(titulo != '')
        )
        """,
        "DROP TABLE IF EXISTS avaliacoes"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_avaliacoes_turma ON avaliacoes(turma_id)",
        "DROP INDEX IF EXISTS idx_avaliacoes_turma"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_avaliacoes_data ON avaliacoes(data)",
        "DROP INDEX IF EXISTS idx_avaliacoes_data"
    )
]
