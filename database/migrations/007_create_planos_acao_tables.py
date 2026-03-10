"""
Cria as tabelas de planos de ação e relacionamentos com materiais.

depends: 001_create_usuarios_table, 003_create_materiais_table
"""

from yoyo import step

__depends__ = ['001_create_usuarios_table', '003_create_materiais_table']

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS planos_acao (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            objetivo TEXT NOT NULL,
            data_criacao TIMESTAMP NOT NULL,
            data_limite TIMESTAMP NOT NULL,
            status TEXT NOT NULL DEFAULT 'rascunho' 
                CHECK(status IN ('rascunho', 'enviado', 'em_andamento', 'concluido', 'cancelado')),
            observacoes TEXT,
            
            FOREIGN KEY (aluno_id) REFERENCES usuarios(id) ON DELETE CASCADE,
            CHECK(objetivo != ''),
            CHECK(data_limite > data_criacao)
        )
        """,
        "DROP TABLE IF EXISTS planos_acao"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_planos_aluno ON planos_acao(aluno_id)",
        "DROP INDEX IF EXISTS idx_planos_aluno"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_planos_status ON planos_acao(status)",
        "DROP INDEX IF EXISTS idx_planos_status"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_planos_limite ON planos_acao(data_limite)",
        "DROP INDEX IF EXISTS idx_planos_limite"
    ),
    step(
        """
        CREATE TABLE IF NOT EXISTS plano_materiais (
            plano_id INTEGER NOT NULL,
            material_id INTEGER NOT NULL,
            data_adicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            PRIMARY KEY (plano_id, material_id),
            FOREIGN KEY (plano_id) REFERENCES planos_acao(id) ON DELETE CASCADE,
            FOREIGN KEY (material_id) REFERENCES materiais(id) ON DELETE CASCADE
        )
        """,
        "DROP TABLE IF EXISTS plano_materiais"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_plano_materiais_plano ON plano_materiais(plano_id)",
        "DROP INDEX IF EXISTS idx_plano_materiais_plano"
    ),
    step(
        "CREATE INDEX IF NOT EXISTS idx_plano_materiais_material ON plano_materiais(material_id)",
        "DROP INDEX IF EXISTS idx_plano_materiais_material"
    )
]
