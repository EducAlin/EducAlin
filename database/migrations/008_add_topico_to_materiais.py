"""
Migration: Adiciona campo 'topico' à tabela 'materiais' para suportar busca por tópico.

Este campo permite categorizar materiais por tópicos específicos, 
possibilitando análise e recomendação de materiais por area de conhecimento.

depends: 003_create_materiais_table
"""

from yoyo import step

__depends__ = ['003_create_materiais_table']

steps = [
    step(
        """
        ALTER TABLE materiais 
        ADD COLUMN topico TEXT DEFAULT NULL
        """,
        """
        ALTER TABLE materiais 
        DROP COLUMN topico
        """
    ),
    step(
        """
        CREATE INDEX IF NOT EXISTS idx_materiais_topico 
        ON materiais(topico)
        """,
        "DROP INDEX IF EXISTS idx_materiais_topico"
    )
]
