"""
Hierarquia de exceções de domínio do EducaLin.

Cada exceção mapeia para um status HTTP específico na camada de API,
eliminando a necessidade de detecção de erro por análise de string.

Mapeamento HTTP sugerido:
    EntidadeNaoEncontradaError  → 404 Not Found
    NotaDuplicadaError          → 409 Conflict
    ValorInvalidoError          → 422 Unprocessable Entity
"""

from __future__ import annotations


class EducalinError(Exception):
    """
    Exceção base de todos os erros de domínio do EducaLin.

    Permite capturar qualquer erro de domínio com um único ``except``:

    Examples:
        >>> try:
        ...     repo.registrar_nota(...)
        ... except EducalinError as exc:
        ...     logger.error("Erro de domínio: %s", exc)
    """


class EntidadeNaoEncontradaError(EducalinError):
    """
    Lançada quando uma entidade solicitada não existe no banco.

    Mapeia para HTTP 404 Not Found.

    Examples:
        >>> raise EntidadeNaoEncontradaError("Turma 99 não encontrada")
    """


class NotaDuplicadaError(EducalinError):
    """
    Lançada quando já existe uma nota para o mesmo aluno na mesma avaliação.

    Mapeia para HTTP 409 Conflict.

    Examples:
        >>> raise NotaDuplicadaError(
        ...     "Já existe nota para o aluno 5 na avaliação 2."
        ... )
    """


class ValorInvalidoError(EducalinError):
    """
    Lançada quando um valor de negócio está fora dos limites permitidos.

    Mapeia para HTTP 422 Unprocessable Entity.

    Examples:
        >>> raise ValorInvalidoError(
        ...     "Valor 12.0 excede o valor máximo da avaliação (10.0)."
        ... )
    """
