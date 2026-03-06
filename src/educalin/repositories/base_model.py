"""
Classe base para todos os modelos do banco de dados.

Fornece métodos utilitários comuns para validação e segurança.
"""

import re
import bcrypt

# Padrão de validação de email
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


class BaseModel:
    """
    Classe base com métodos utilitários para todos os modelos.
    
    Fornece validações comuns e operações de segurança (hash de senha).
    """
    
    @staticmethod
    def _validate_email(email: str) -> str:
        """
        Valida e normaliza um email.
        
        Args:
            email: Email a ser validado
        
        Returns:
            str: Email normalizado (lowercase e stripped)
        
        Raises:
            ValueError: Se o email for inválido
        """
        email = email.strip().lower()
        if not EMAIL_PATTERN.match(email):
            raise ValueError(f"Formato de e-mail inválido: {email}")
        return email
    
    @staticmethod
    def _validate_not_empty(value: str, field_name: str) -> str:
        """
        Valida que um campo não está vazio.
        
        Args:
            value: Valor a ser validado
            field_name: Nome do campo (para mensagem de erro)
        
        Returns:
            str: Valor normalizado (stripped)
        
        Raises:
            ValueError: Se o valor estiver vazio
        """
        if not value or not value.strip():
            raise ValueError(f"{field_name} não pode ser vazio.")
        return value.strip()
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Cria um hash bcrypt da senha.
        
        Args:
            password: Senha em texto plano
        
        Returns:
            str: Hash bcrypt da senha
        """
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """
        Verifica se uma senha corresponde ao hash.
        
        Args:
            password: Senha em texto plano
            password_hash: Hash bcrypt armazenado
        
        Returns:
            bool: True se a senha corresponde ao hash
        """
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
