"""
Migration: Adiciona campo 'topico' à tabela 'materiais' para suportar busca por tópico.

Este campo permite categorizar materiais por tópicos específicos, 
possibilitando análise e recomendação de materiais por area de conhecimento.
"""

from yoyo import step

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
        """
    )
]
