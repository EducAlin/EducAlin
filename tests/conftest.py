"""
Configuração global de testes.

Define fixtures e variáveis de ambiente necessárias para os testes.
"""

import os

# Define JWT_SECRET_KEY antes de qualquer importação dos módulos de segurança
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only")
