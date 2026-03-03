"""
Relatório comparativo de desempenho entre turmas.
"""

from __future__ import annotations
import copy
from typing import Dict, Any, List, TYPE_CHECKING
from datetime import datetime
from .base import GeradorRelatorio

if TYPE_CHECKING:
    from ...domain.turma import Turma


class RelatorioComparativo(GeradorRelatorio):
    """
    Gerador de relatório comparativo de desempenho entre múltiplas turmas.

    Destinado ao uso por coordenadores, consolida métricas de todas as turmas
    fornecidas e apresentadas lado a lado, permitindo identificar as turmas
    com melhor e pior desempenho e comparar taxas de aprovação.

    O fluxo segue o Template Method herdado de GeradorRelatorio:
    coletar_dados() -> processar_dados() -> formatar_saida()

    Attributes:
        _turmas (List[Turma]): Lista de turmas a serem comparadas
        _LARGURA_LINHA (int): Largura padrão das linhas do relatório (70 chars)

    Examples:
        >>> from educalin.services.relatorios import RelatorioComparativo
        >>> relatorio = RelatorioComparativo([turma_a, turma_b, turma_c])
        >>> conteudo = relatorio.gerar()
        >>> print(conteudo)
    """

    _LARGURA_LINHA: int = 70
    _ATRIBUTOS_OBRIGATORIOS = ('codigo', 'disciplina', 'semestre', 'obter_desempenho_geral')

    def __init__(self, turmas: List[Turma]):
        """
        Inicializa o gerador de relatório comparativo.

        Args:
            turmas: Lista de instâncias de Turma a serem comparadas

        Raises:
            TypeError: Se turmas não for uma lista ou contiver itens sem os
                atributos obrigatórios (codigo, disciplina, semestre, obter_desempenho_geral)
            ValueError: Se turmas for uma lista vazia
        """
        super().__init__()

        if turmas is None or not isinstance(turmas, list):
            raise TypeError("turmas deve ser uma lista de instâncias de Turma")
        if len(turmas) == 0:
            raise ValueError("É necessário pelo menos uma turma para gerar o relatório")
        for item in turmas:
            for attr in self._ATRIBUTOS_OBRIGATORIOS:
                if not hasattr(item, attr):
                    raise TypeError(
                        f"todos os itens devem ser Turma (atributo '{attr}' ausente)"
                    )
        self._turmas = list(turmas)

    # Métodos abstratos

    def coletar_dados(self) -> Dict[str, Any]:
        """
        Coleta e agrega métricas de desempenho de cada turma.

        Para cada turma, delega o cálculo ao método obter_desempenho_geral()
        já definido na entidade Turma, respeitando o SRP. As turmas são
        ordenadas por média decrescente para facilitar o processamento posterior.

        Returns:
            Dicionário com informações das turmas analisadas e métricas

        Raises:
            RuntimeError: Se obter_desempenho_geral() lançar exceção para alguma turma,
                encapsula o erro com o código da turma para facilitar o diagnóstico
        """
        turmas_dados = []

        for turma in self._turmas:
            try:
                desempenho = turma.obter_desempenho_geral()
            except Exception as exc:
                raise RuntimeError(
                    f"Falha ao obter desempenho da turma '{turma.codigo}'"
                ) from exc
            turmas_dados.append({
                'codigo': turma.codigo,
                'disciplina': turma.disciplina,
                'semestre': turma.semestre,
                'media_geral': desempenho.get('media_geral', 0.0),
                'total_alunos': desempenho.get('total_alunos', 0),
                'alunos_com_dificuldade': desempenho.get('alunos_com_dificuldade', 0),
                'taxa_aprovacao': desempenho.get('taxa_aprovacao', 0.0)
            })

        turmas_dados.sort(key=lambda t: t['media_geral'], reverse=True)

        medias = [t['media_geral'] for t in turmas_dados]
        media_global = round(sum(medias) / len(medias), 2) if medias else 0.0

        semestres = sorted({t.semestre for t in self._turmas})
        semestre_label = semestres[0] if len(semestres) == 1 else ", ".join(semestres)
        # Válido somente para casos onde a diferenciação de semestre é feita ao fim.
        # Caso a diferenciação passe para algo como "1/2025", "2/2025", ordenação poderá quebrar

        return {
            'total_turmas': len(turmas_dados),
            'semestre': semestre_label,
            'media_geral_global': media_global,
            'turmas': turmas_dados
        }

    def formatar_saida(self, dados_processados: Dict[str, Any]) -> str:
        """
        Formata os dados em relatório comparativo legível.

        Seções geradas:
        - Cabeçalho com semestre e totais
        - Estatísticas globais (média global, melhor turma, turma mais crítica)
        - Gráfico ASCII comparativo de médias
        - Ranking completo com posição, código, média e taxa de aprovação
        - Rodapé com timestamp de geração

        Args:
            dados_processados: Dicionário retornado por processar_dados

        Returns:
            Relatório formatado como string pronto para exibição em terminal ou exportação
        """
        L = self._LARGURA_LINHA
        linhas = []

        # Cabeçalho
        linhas.append("=" * L)
        linhas.append("RELATÓRIO COMPARATIVO DE DESEMPENHO ENTRE TURMAS".center(L))
        linhas.append("=" * L)
        linhas.append("")
        linhas.append(f"Semestre:           {dados_processados.get('semestre', 'N/A')}")
        linhas.append(f"Total de Turmas:    {dados_processados.get('total_turmas', 0)}")
        linhas.append("")

        # Estatísticas globais
        linhas.append("-" * L)
        linhas.append("ESTATÍSTICAS GLOBAIS")
        linhas.append("-" * L)
        linhas.append(f"Média Global:       {dados_processados.get('media_geral_global', 0.0):.2f}")
        linhas.append(f"Melhor Turma:       {dados_processados.get('melhor_turma', 'N/A')}")
        linhas.append(f"Turma Mais Crítica: {dados_processados.get('turma_mais_critica', 'N/A')}")

        # Gráfico comparativo
        if 'grafico_ascii' in dados_processados:
            linhas.append("-" * L)
            linhas.append("GRÁFICO COMPARATIVO DE MÉDIAS")
            linhas.append("-" * L)
            linhas.append(dados_processados['grafico_ascii'])
            linhas.append("")

        # Ranking
        ranking = dados_processados.get('ranking', [])
        if ranking:
            linhas.append("-" * L)
            linhas.append("RANKING DE TURMAS")
            linhas.append("-" * L)
            linhas.append(
                f"  {'Pos':<4} {'Turma':<10} {'Disciplina':<25}"
                f"{'Média':>6}  {'Aprovação':>9}    {'Alunos':>6}"
            )
            linhas.append("  " + "-" * (L - 4))
            for item in ranking:
                linhas.append(
                    f"  {item['posicao']:<4} "
                    f"{item['codigo']:<10} "
                    f"{item['disciplina']:<25} "
                    f"{item['media_geral']:>6.2f} "
                    f"{item['taxa_aprovacao']:>8.1f}% "
                    f"{item['total_alunos']:>6}"
                )
            linhas.append("")

        # Rodapé
        linhas.append("=" * L)
        linhas.append(f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        linhas.append("=" * L)


        return "\n".join(linhas)

    # Hook method
    def processar_dados(self, dados_brutos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook method: enriquece os dados brutos com ranking e gráfico comparativo.

        Sobrescreve o hook padrão da classe base para adicionar:
        - Ranking das turmas por média decrescente (com campo posicao)
        - Identificação da melhor turma (maior média)
        - Identificação da turma mais crítica (maior número de alunos com dificuldade)
        - Gráfico ASCII de barras horizontais comparando médias

        Args: 
            dados_brutos: Dicionário retornado por coletar_dados

        Returns:
            Cópia do dicionário de entrada enriquecida com:
            - ranking (List[Dict]): turmas com campo posicao adicionado,
              ordenadas por média decrescente
            - melhor_turma (str): código da turma com maior média
            - turma_mais_critica (str): código da turma com mais alunos 
             com dificuldade; em caso de empate, a de menor média vence
            - grafico_ascii (str): gráfico de barras horizontais ASCII
        
        Examples:
            >>> dados = relatorio.coletar_dados()
            >>> processado = relatorio.processar_dados(dados)
            >>> processado['melhor_turma']
            'ES001'
        """
        dados = copy.deepcopy(dados_brutos)
        turmas = dados.get('turmas', [])

        # Ranking
        ranking = []
        for posicao, turma in enumerate(turmas, start=1):
            entrada = turma.copy()
            entrada['posicao'] = posicao
            ranking.append(entrada)

        dados['ranking'] = ranking

        dados['melhor_turma'] = ranking[0]['codigo'] if ranking else 'N/A'

        dados['turma_mais_critica'] = self._identificar_turma_critica(turmas)

        dados['grafico_ascii'] = self._gerar_grafico_ascii(turmas)

        return dados

    # Métodos auxiliares

    def _identificar_turma_critica(self, turmas: List[Dict]) -> str:
        """
        Identifica a turma com maior número de alunos com dificuldade.

        Em caso de empate no número de alunos com dificuldade, a turma com
        menor média geral é considerada a mais crítica.

        Args:
            turmas: Lista de dicts de turmas

        Returns:
            Código da turma mais crítica, ou 'N/A' se a lista estiver vazia

        Examples:
            >>> turmas = [
            ...     {'codigo': 'T1', 'alunos_com_dificuldade': 3, 'media_geral': 6.0},
            ...     {'codigo': 'T2', 'alunos_com_dificuldade': 5, 'media_geral': 5.0}
            ... ]
            >>> relatorio._identificar_turma_critica(turmas)
            'T2'
        """
        if not turmas:
            return 'N/A'

        mais_critica = max(
            turmas,
            key=lambda t: (t.get('alunos_com_dificuldade', 0), -t.get('media_geral', 0.0))
        )
        return mais_critica['codigo']

    def _gerar_grafico_ascii(self, turmas: List[Dict]) -> str:
        """
        Gera um gráfico de barras horizontais ASCII comparando as médias das turmas.

        Cada turma é representada por uma linha com seu código à esquerda e uma
        barra proporcional à sua média (escala 0-10, largura média de 40 chars).
        A média é exibida numericamente ao final da barra.

        Args:
            turmas: Lista de dicts de turmas, cada um com ao menos media_geral e codigo.
             Se a lista estiver vazia, retorna mensagem informativa

        Returns:
            String multilinha com o gráfico pronto para exibição em terminal,
            ou "  (sem turmas para comparar)" se não houver turmas

        Examples:
            >>> turmas = [
            ...     {'codigo': 'ES001', 'media_geral': 8.0},
            ...     {'codigo': 'ES002', 'media_geral': 5.0},
            ... ]
            >>> print(relatorio._gerar_grafico_ascii(turmas))
            ES001 | ████████████████████████████████  8.00
            ES002 | ████████████████████              5.00
        """
        if not turmas:
            return "  (sem turmas para comparar)"

        MAX_LARGURA = 40
        BLOCO = "█"
        linhas = []

        for turma in turmas:
            codigo = turma.get('codigo', '??')[:8]
            media = turma.get('media_geral', 0.0)
            tamanho_barra = min(round((media / 10.0) * MAX_LARGURA), MAX_LARGURA)
            barra = BLOCO * tamanho_barra
            linhas.append(f"{codigo:<8} | {barra:<{MAX_LARGURA}}  {media:.2f}")

        return "\n".join(linhas)
