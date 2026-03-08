"""
Módulo de utilitários de segurança para autenticação.

Este módulo fornece funções para hash de senhas usando bcrypt e
gerenciamento de tokens JWT para autenticação.
"""

import os
import warnings
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import bcrypt
import jwt


# Configuração JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY environment variable must be set for JWT operations."
    )
ALGORITHM = "HS256"
TOKEN_EXPIRATION_HOURS = 24


def _obter_secret_key() -> str:
    """Retorna a chave secreta JWT, emitindo aviso se usar o valor padrão."""
    chave = os.getenv("JWT_SECRET_KEY")
    if not chave:
        warnings.warn(
            "JWT_SECRET_KEY não configurada. Usando chave padrão insegura. "
            "Defina a variável de ambiente JWT_SECRET_KEY em produção.",
            stacklevel=2,
        )
        return _FALLBACK_SECRET_KEY
    return chave


def hash_senha(senha: str) -> str:
    """
    Gera um hash bcrypt para a senha fornecida.

    Args:
        senha: A senha em texto plano para ser hasheada.

    Returns:
        O hash bcrypt da senha como string.

    Example:
        >>> hash_resultado = hash_senha("minha_senha_123")
        >>> isinstance(hash_resultado, str)
        True
    """
    senha_bytes = senha.encode("utf-8")
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(senha_bytes, salt)
    return hash_bytes.decode("utf-8")


def verificar_senha(senha: str, hash_senha: str) -> bool:
    """
    Verifica se uma senha corresponde ao hash bcrypt fornecido.

    Args:
        senha: A senha em texto plano para verificar.
        hash_senha: O hash bcrypt para comparar.

    Returns:
        True se a senha corresponder ao hash, False caso contrário.

    Example:
        >>> hash_senha_teste = hash_senha("senha123")
        >>> verificar_senha("senha123", hash_senha_teste)
        True
        >>> verificar_senha("senha_errada", hash_senha_teste)
        False
    """
    senha_bytes = senha.encode("utf-8")
    hash_bytes = hash_senha.encode("utf-8")
    return bcrypt.checkpw(senha_bytes, hash_bytes)


def criar_token_jwt(usuario_id: int, perfil: str) -> str:
    """
    Cria um token JWT para autenticação do usuário.

    Args:
        usuario_id: ID único do usuário.
        perfil: Perfil/role do usuário (ex: 'aluno', 'professor', 'coordenador').

    Returns:
        Token JWT codificado como string.

    Example:
        >>> token = criar_token_jwt(1, "aluno")
        >>> isinstance(token, str)
        True
    """
    expiracao = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRATION_HOURS)
    
    payload = {
        "usuario_id": usuario_id,
        "perfil": perfil,
        "exp": expiracao,
        "iat": datetime.now(timezone.utc)
    }
    
    token = jwt.encode(payload, _obter_secret_key(), algorithm=ALGORITHM)
    return token


def decodificar_token_jwt(token: str) -> Optional[Dict]:
    """
    Decodifica e valida um token JWT.

    Args:
        token: Token JWT a ser decodificado.

    Returns:
        Dicionário com os dados do payload se o token for válido,
        None se o token for inválido ou expirado.

    Example:
        >>> token = criar_token_jwt(1, "professor")
        >>> payload = decodificar_token_jwt(token)
        >>> payload is not None
        True
        >>> payload["usuario_id"]
        1
    """
    try:
        payload = jwt.decode(token, _obter_secret_key(), algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        # Token expirado
        return None
    except jwt.InvalidTokenError:
        # Token inválido
        return None
