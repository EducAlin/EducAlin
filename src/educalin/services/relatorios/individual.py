"""
Relatório individual de desempenho de aluno.
"""

from __future__ import annotations
import copy
from typing import Dict, Any, List, TYPE_CHECKING
from datetime import datetime

from .base import GeradorRelatorio

if TYPE_CHECKING:
    from ...domain.aluno import Aluno
    from ...domain.turma import Turma

class RelatorioIndividual(GeradorRelatorio):
    """
    Gerador de relatório individual de desempenho de aluno.

    Analisa o histórico completo de um aluno específico, mostrando:
    - Evolução temporal das notas
    - Tendência de desempenho (crescente/estável/decrescente)
    - Pontos fortes e pontos de atenção
    - Gráfico ASCII da evolução

    Attributes:
        LIMIAR_APROVACAO (float): Nota mínima para classificar tópico como ponto forte (7.0)
        _aluno (Aluno): Aluno para o qual gerar relatório
        _turma (Turma): Turma do aluno (contexto)

    Examples:
        >>> from educalin.services.relatorios import RelatorioIndividual
        >>> relatorio = RelatorioIndividual(aluno, turma)
        >>> conteudo = relatorio.gerar()
        >>> print(conteudo)
    """

    LIMIAR_APROVACAO: float = 7.0

    def __init__(self, aluno: Aluno, turma: Turma):
        """
        Inicializa o gerador de relatório individual.

        Args:
            aluno: Instância de Aluno
            turma: Instância de Turma (para contexto)

        Raises:
            TypeError: Se aluno ou turma não forem válidos
        """
        super().__init__()

        if not hasattr(aluno, 'nome') or not hasattr(aluno, 'matricula'):
            raise TypeError("Aluno deve ter atributos 'nome' e 'matricula'")
        
        if not all(hasattr(turma, attr) for attr in ('codigo', 'disciplina', 'semestre')):
            raise TypeError("Turma deve ter atributos 'codigo', 'disciplina' e 'semestre'")
        
        self._aluno = aluno
        self._turma = turma

    
    # Métodos abstratos

    def coletar_dados(self) -> Dict[str, Any]:
        """
        Coleta histórico completo do aluno.

        Coleta:
        - Informações básicas do aluno 
        - Informações da turma (contexto)
        - Histórico completo de notas (cronológico) via propriedade `desempenho`
        - Ordenação cronológica por `data_registro` de cada nota

        Returns:
            Dicionário com dados completos do aluno
        """
        dados = {
            'nome_aluno': self._aluno.nome,
            'matricula': self._aluno.matricula,
            'media_geral': (
                self._aluno.calcular_media() if hasattr(self._aluno, 'calcular_media') else 0.0
            ),
            'codigo_turma': self._turma.codigo,
            'disciplina': self._turma.disciplina,
            'semestre': self._turma.semestre,
        }

        historico_completo = []

        # Usa a propriedade `desempenho` da classe Aluno (retorna List[Nota])
        notas = self._aluno.desempenho if hasattr(self._aluno, 'desempenho') else []

        for nota in notas:
            historico_completo.append({
                'valor': nota.valor,
                'avaliacao': nota.avaliacao.titulo,
                'topico': getattr(nota.avaliacao, 'topico', getattr(nota.avaliacao, 'titulo', 'N/A')),
                'data': nota.data_registro,
            })

        historico_completo.sort(key=lambda n: n['data'])
        dados['historico_notas'] = historico_completo
        dados['total_avaliacoes'] = len(historico_completo)

        return dados

    def formatar_saida(self, dados_processados: Dict[str, Any]) -> str:
        """
        Formata os dados em relatório individual legível.

        Args:
            dados_processados: Dados coletados e processados

        Returns:
            Relatório formatado como string
        """
        linhas = []

        # Cabeçalho
        linhas.append("="*70)
        linhas.append("RELATÓRIO INDIVIDUAL DE DESEMPENHO".center(70))
        linhas.append("="*70)
        linhas.append("")

        # Informações do aluno
        linhas.append(f"Aluno:      {dados_processados.get('nome_aluno', 'N/A')}")
        linhas.append(f"Matrícula:  {dados_processados.get('matricula', 'N/A')}")
        linhas.append(f"Turma:      {dados_processados.get('codigo_turma', 'N/A')}")
        linhas.append(f"Disciplina: {dados_processados.get('disciplina', 'N/A')}")
        linhas.append(f"Semestre:   {dados_processados.get('semestre', 'N/A')}")
        linhas.append("")

        # Estatísticas gerais
        linhas.append("-"*70)
        linhas.append("ESTATÍSTICAS GERAIS")
        linhas.append("-"*70)
        linhas.append(f"Média Geral:            {dados_processados.get('media_geral', 0.0):.2f}")
        linhas.append(f"Total de Avaliações:    {dados_processados.get('total_avaliacoes', 0)}")

        tendencia = dados_processados.get('tendencia', 'estavel')
        emoji_tendencia = {
            'crescente': '^',    # tendência de alta
            'estavel': '->',     # tendência estável
            'decrescente': 'v',  # tendência de baixa
        }.get(tendencia, '->')

        nome_tendencia = {
            'crescente': 'CRESCENTE (Melhorando!)',
            'estavel': 'ESTÁVEL',
            'decrescente': 'DECRESCENTE (Atenção!)',
        }.get(tendencia, 'ESTÁVEL')

        linhas.append(f"Tendência:              {emoji_tendencia} {nome_tendencia}")
        linhas.append("")

        # Gráfico de evolução
        if 'grafico_ascii' in dados_processados:
            linhas.append("-"*70)
            linhas.append("EVOLUÇÃO DAS NOTAS")
            linhas.append("-"*70)
            linhas.append(dados_processados['grafico_ascii'])
            linhas.append("")

        # Pontos fortes
        pontos_fortes = dados_processados.get('pontos_fortes', [])
        if pontos_fortes:
            linhas.append("-"*70)
            linhas.append("PONTOS FORTES")
            linhas.append("-"*70)
            
            for ponto in pontos_fortes:
                linhas.append(
                    f"  - {ponto['topico']:<25} "
                    f"Média: {ponto['media']:.2f} "
                    f"({ponto['avaliacoes']} avaliações)"
                )
            linhas.append("")

        # Pontos de atenção
        pontos_atencao = dados_processados.get('pontos_atencao', [])
        if pontos_atencao:
            linhas.append("-"*70)
            linhas.append("PONTOS QUE NECESSITAM DE ATENÇÃO")
            linhas.append("-"*70)
            
            for ponto in pontos_atencao:
                linhas.append(
                    f"  - {ponto['topico']:<25} "
                    f"Média: {ponto['media']:.2f} "
                    f"({ponto['avaliacoes']} avaliações)"
                )
            linhas.append("")

        # Histórico completo
        historico = dados_processados.get('historico_notas', [])
        if historico:
            linhas.append("-"*70)
            linhas.append("HISTÓRICO COMPLETO DE AVALIAÇÕES")
            linhas.append("-"*70)

            for nota in historico:
                data = nota.get('data')
                data_str = data.strftime('%d/%m/%Y') if isinstance(data, datetime) else str(data or 'N/A')
                valor = nota.get('valor') or 0.0
                status = "[OK]" if valor >= self.LIMIAR_APROVACAO else "[!]"

                linhas.append(
                    f"{status} {data_str}  "
                    f"{nota['avaliacao']:<20}  "
                    f"{nota['topico']:>15}  "
                    f"Nota: {valor:.1f}"
                )
            linhas.append("")

        # Rodapé
        linhas.append("="*70)
        linhas.append(
            f"Relatório gerado em : "
            f"{(self._data_geracao or datetime.now()).strftime('%d/%m/%Y %H:%M')}"
        )
        linhas.append("="*70)

        return "\n".join(linhas)


    # Hook method
    def processar_dados(self, dados_brutos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processa os dados brutos para adicionar tendência e gráfico ASCII.

        Sobrescreve o hook padrão da classe base para adicionar:
        - Tendência de desempenho calculada sobre o histórico completo
        - Pontos fortes e pontos de atenção por tópico (recalculados sobre os dados brutos)
        - Gráfico ASCII de barras com a evolução das notas

        Utiliza deepcopy para não mutar o dicionário original nem as listas internas.

        Args:
            dados_brutos: Dados coletados

        Returns:
            Dados processados com tendência e gráfico ASCII
        """
        dados = copy.deepcopy(dados_brutos)
        historico: List[Dict] = dados.get('historico_notas', [])

        dados['tendencia'] = self._calcular_tendencia(historico)

        analise = self._analisar_por_topico(historico)
        dados['pontos_fortes'] = analise['fortes']
        dados['pontos_atencao'] = analise['atencao']

        dados['grafico_ascii'] = self._gerar_grafico_ascii(historico)

        return dados
    
    # Métodos auxiliares

    def _analisar_por_topico(self, historico: List[Dict]) -> Dict[str, List]:
        """
        Agrupa as notas por tópico e classifica em pontos fortes e de atenção.

        Cada tópico é avaliado pela sua média aritmética:
        - média >= LIMIAR_APROVACAO (7.0) -> ponto forte
        - média < LIMIAR_APROVACAO (7.0)  -> ponto de atenção

        Args:
            historico: Lista de dicts de notas

        Returns:
            Dict com listas de pontos fortes e de atenção
        """
        topicos: Dict[str, List[float]] = {}

        for nota in historico:
            topico = nota.get('topico', '')
            if not topico: 
                continue
            if topico not in topicos:
                topicos[topico] = []
            topicos[topico].append(nota['valor'])

        pontos_fortes = []
        pontos_atencao = []

        for topico, notas in topicos.items():
            media = sum(notas) / len(notas)

            info_topico = {
                'topico': topico,
                'media': round(media, 2),
                'avaliacoes': len(notas)
            }

            if media >= self.LIMIAR_APROVACAO:
                pontos_fortes.append(info_topico)
            else:
                pontos_atencao.append(info_topico)

        pontos_fortes.sort(key=lambda t: t['media'], reverse=True)
        pontos_atencao.sort(key=lambda t: t['media'])

        return {
            'fortes': pontos_fortes,
            'atencao': pontos_atencao
        }
    
    def _calcular_tendencia(self, historico: List[Dict]) -> str:
        """
        Calcula a tendência de desempenho comparando as metades do histórico.

        Usa as primeiras N/2 entradas como primeira metade e as últimas N/2
        como segunda metade, garantindo comparação simétrica mesmo para
        históricos com tamanho ímpar (a entrada central é descartada).

        Args:
            historico: Lista de dicts de notas ordenadas cronologicamente

        Returns:
            'crescente' se diferença entre metades > +0.5
            'decrescente' se diferença entre metades < -0.5
            'estavel' em qualquer outro caso
        """
        if len(historico) < 2:
            return 'estavel'
        
        meio = len(historico) // 2
        # Divisão simétrica: primeiras N//2 vs últimas N//2
        # Para histórico ímpar, a entrada central é ignorada (neutro)
        primeira_metade = historico[:meio]
        segunda_metade = historico[len(historico) - meio:]

        media_primeira = sum(n['valor'] for n in primeira_metade) / len(primeira_metade)
        media_segunda = sum(n['valor'] for n in segunda_metade) / len(segunda_metade)

        diferenca = media_segunda - media_primeira

        if diferenca > 0.5:
            return 'crescente'
        elif diferenca < -0.5:
            return 'decrescente'
        else:
            return 'estavel'

    def _gerar_grafico_ascii(self, historico: List[Dict]) -> str:
        """
        Gera um gráfico de barras ASCII com a evolução das notas ao longo do tempo.

        Cada barra representa uma avaliação. Os rótulos do eixo X usam índice
        sequencial (A1, A2, ...) para garantir legibilidade independente do
        comprimento do título da avaliação.

        Args:
            historico: Lista de dicts de notas ordenado cronologicamente

        Returns:
            String multilinha com gráfico pronto para exibição.
        """
        if not historico:
            return "  (sem avaliações registradas)"
        
        ALTURA = 10
        LARGURA_BARRA = 3
        linhas_grafico = []

        celula_cheia = "█" * (LARGURA_BARRA - 1) + " "
        celula_vazia = " " * LARGURA_BARRA

        for altura_linha in range(ALTURA, 0, -1):
            celulas = []
            for nota in historico:
                valor_normalizado = (nota['valor'] / 10.0) * ALTURA
                celula = celula_cheia if valor_normalizado >= altura_linha else celula_vazia
                celulas.append(celula)

            prefixo = (
                f"{altura_linha * 10 // ALTURA:2d} |"
                if altura_linha in (ALTURA, ALTURA // 2, 1)
                else "   |"
            )
            linhas_grafico.append(prefixo + "".join(celulas))

        separador = "   +" + "─" * (len(historico) * LARGURA_BARRA + 1)
        linhas_grafico.append(separador)

        rotulos = [f"A{i+1:<2}" for i, _ in enumerate(historico)]
        linhas_grafico.append("    " + "".join(rotulos))

        return "\n".join(linhas_grafico)
