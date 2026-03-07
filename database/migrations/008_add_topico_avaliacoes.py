from yoyo import step

__depends__ = ['004_create_avaliacoes_table']


def _rollback_add_topico_avaliacoes(conn):
    """
    Rollback for the migration that adds 'topico' to 'avaliacoes'.
    This rollback is intentionally irreversible: SQLite does not support
    DROP COLUMN natively in older versions, and removing the column safely
    would require reconstructing the full table schema, risking data loss.
    """
    raise RuntimeError(
        "Irreversible migration: cannot automatically remove column "
        "'topico' from table 'avaliacoes'."
    )


steps = [
    step(
        "ALTER TABLE avaliacoes ADD COLUMN topico TEXT",
        _rollback_add_topico_avaliacoes,
    )
]
