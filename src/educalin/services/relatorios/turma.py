"""
Relatório consolidado de desempenho da turma.
"""
from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING
from datetime import datetime
from .base import GeradorRelatorio

if TYPE_CHECKING:
    from ...domain.turma import Turma

class RelatorioTurma(GeradorRelatorio):
    """
    Gerador de relatório consolidado de uma turma.

    Coleta dados de todos os alunos da turma e gera relatório com:
    - Estatísticas gerais (média, taxa de aprovação)
    - Lista completa de alunos
    - Alunos com dificuldade (média < 6.0)
    - Ranking dos melhores alunos
    - Tópicos problemáticos (se disponível)

    Attributes:
        _turma (Turma): Turma para qual gerar o relatório

    Examples:
        >>> relatorio = RelatorioTurma(turma)
        >>> conteudo = relatorio.gerar()
        >>> pdf = relatorio.exportar(conteudo, FormatoRelatorio.PDF)
    """

    def __init__(self, turma: Turma):
        """
        Inicializa o gerador de relatório de turma.

        Args:
            turma: Instância de Turma

        Raises:
            TypeError: Se turma não for instância de Turma
        """
        super().__init__()

        # Validação defensiva: a classe depende destes atributos/métodos
        required_attrs = ("codigo", "alunos", "disciplina", "semestre")
        required_methods = ("obter_desempenho_geral",)

        missing_attrs = [attr for attr in required_attrs if not hasattr(turma, attr)]
        missing_methods = [m for m in required_methods if not hasattr(turma, m)]

        if missing_attrs or missing_methods:
            parts = []
            if missing_attrs:
                parts.append(f"atributos faltando: {', '.join(missing_attrs)}")
            if missing_methods:
                parts.append(f"métodos faltando: {', '.join(missing_methods)}")
            raise TypeError(
                f"Turma inválida: objeto não tem a interface esperada. "
                + "; ".join(parts)
            )

        self._turma = turma

    # Implementação dos métodos abstratos

    def coletar_dados(self) -> Dict[str, Any]:
        """
        Coleta todos os dados necessários da turma.

        Coleta:
        - Informações básicas da turma
        - Estatísticas gerais (via obter_desempenho_geral())
        - Lista de todos os alunos com suas médias
        - Lista de alunos com dificuldade (média < 6.0)

        Returns:
            Dicionário com dados completos da turma
        """
        dados = {
            'codigo_turma': self._turma.codigo,
            'disciplina': self._turma.disciplina,
            'semestre': self._turma.semestre,
        }

        # Estatísticas gerais
        desempenho = self._turma.obter_desempenho_geral()
        dados.update(desempenho)

        alunos_data = []
        alunos_dificuldade = []

        for aluno in self._turma.alunos:
            aluno_info = {
                'nome': aluno.nome,
                'matricula': aluno.matricula,
                'media': aluno.calcular_media() if hasattr(aluno, 'calcular_media') else 0.0
            }

            alunos_data.append(aluno_info)

            media = aluno_info['media']
            if isinstance(media, (int, float)) and media < 6.0:
                alunos_dificuldade.append(aluno_info)

        dados['alunos'] = alunos_data
        dados['alunos_dificuldade'] = alunos_dificuldade

        # TODO: Adicionar coleta de tópicos problemáticos
        # BLOCKED: Depende da implementação de 'obter_topicos_criticos' na classe Turma (Domain)
        # dados['topicos_problematicos'] = self._turma.obter_topicos_criticos()

        return dados
    
    def formatar_saida(self, dados_processados: Dict[str, Any]) -> str:
        """
        Formata os dados em relatório legivel.

        Args:
            dados_processados: Dados coletados e processados

        Returns:
            Relatório formatado como string
        """
        linhas = []

        # Cabeçalho
        linhas.append("="*70)
        linhas.append("RELATÓRIO DE DESEMPENHO DA TURMA".center(70))
        linhas.append("="*70)
        linhas.append("")

        # Informações da turma
        linhas.append(f"Turma:      {dados_processados.get('codigo_turma', 'N/A')}")
        linhas.append(f"Disciplina: {dados_processados.get('disciplina', 'N/A')}")
        linhas.append(f"Semestre:   {dados_processados.get('semestre', 'N/A')}")

        # Estatísticas gerais
        linhas.append("-"*70)
        linhas.append("ESTATÍSTICAS GERAIS")
        linhas.append("-"*70)
        linhas.append(f"Total de Alunos:        {dados_processados.get('total_alunos', 0)}")
        linhas.append(f"Média Geral da Turma:   {dados_processados.get('media_geral', 0.0):.2f}")
        linhas.append(f"Taxa de Aprovação:      {dados_processados.get('taxa_aprovacao', 0.0):.1f}%")
        
        num_dificuldade = len(dados_processados.get('alunos_dificuldade', []))
        linhas.append(f"Alunos com Dificuldade: {num_dificuldade}")
        linhas.append("")

        # Ranking Top 5
        ranking = dados_processados.get('ranking_top5', [])
        if ranking:
            linhas.append("-"*70)
            linhas.append("TOP 5 MELHORES ALUNOS")
            linhas.append("-"*70)

            for i, aluno in enumerate(ranking, 1):
                media = aluno.get('media')
                media_str = f"{media:.2f}" if isinstance(media, (int, float)) else "N/A"
                linhas.append(
                    f"{i}º - {aluno.get('nome', 'N/A'):<30} "
                    f"Matrícula: {aluno.get('matricula', 'N/A'):<10} "
                    f"Média: {media_str}"
                )
            linhas.append("")

        # Alunos com dificuldade
        alunos_dificuldade = dados_processados.get('alunos_dificuldade', [])
        if alunos_dificuldade:
            linhas.append("-"*70)
            linhas.append("ALUNOS QUE PRECISAM DE ATENÇÃO (Média < 6.0)")
            linhas.append("-"*70)

            for aluno in alunos_dificuldade:
                media = aluno.get('media')
                media_str = f"{media:.2f}" if isinstance(media, (int, float)) else "N/A"
                linhas.append(
                    f"!  {aluno.get('nome', 'N/A'):<30} "
                    f"Matrícula: {aluno.get('matricula', 'N/A'):<10} "
                    f"Média: {media_str}"
                )
            linhas.append("")
        else:
            linhas.append("-"*70)
            linhas.append("[OK] Nenhum aluno com dificuldade identificado!")
            linhas.append("")

        # Lista completa de alunos
        alunos = dados_processados.get('alunos', [])
        if alunos:
            linhas.append("-"*70)
            linhas.append("LISTA COMPLETA DE ALUNOS")
            linhas.append("-"*70)

            for aluno in alunos:
                media = aluno.get('media')
                media_str = f"{media:.2f}" if isinstance(media, (int, float)) else "N/A"
                status = "OK" if isinstance(media, (int, float)) and media >= 6.0 else "!"
                linhas.append(
                    f"{status}  {aluno.get('nome', 'N/A'):<30} "
                    f"Matrícula: {aluno.get('matricula', 'N/A'):<10} "
                    f"Média: {media_str}"
                )
            linhas.append("")

        # Rodapé
        linhas.append("="*70)
        linhas.append(f"Relatório gerado em: {(self._data_geracao or datetime.now()).strftime('%d/%m/%Y %H:%M')}")
        linhas.append("="*70)

        return "\n".join(linhas)
    
    
    # Hook method

    def processar_dados(self, dados_brutos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa dados brutos para adicionar ranking.

        Sobrescreve o hook method padrão para adicionar ranking
        dos 5 melhores alunos ordenados por média.

        Args:
            dados_brutos: Dados coletados

        Returns:
            Dados processados com ranking adicionado
        """
        if 'alunos' in dados_brutos and dados_brutos['alunos']:
            alunos_ordenados = sorted(
                dados_brutos['alunos'],
                key=lambda a: a['media'] if isinstance(a['media'], (int, float)) else -1.0,
                reverse=True
            )

            dados_brutos['ranking_top5'] = alunos_ordenados[:5]
        else:
            dados_brutos['ranking_top5'] = []

        return dados_brutos