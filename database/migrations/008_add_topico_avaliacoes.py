from yoyo import step

__depends__ = ['004_create_avaliacoes_table']

steps = [
    step(
        "ALTER TABLE avaliacoes ADD COLUMN topico TEXT",
        "SELECT 1"
    )
]
