"""
Módulo de geração de relatórios usando Template Method Pattern.

Este módulo fornece a estrutura base para geração de relatórios
através do padrão Template Method, garantindo que todas as subclasses
sigam o mesmo fluxo de execução.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
import json


class FormatoRelatorio(Enum):
    """Formatos suportados para exportação de relatórios"""
    TEXTO = "texto"
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"


class RelatorioVazioException(Exception):
    """Exceção lançada quando relatório não tem dados"""
    pass

class GeradorRelatorio(ABC):
    """
    Classe abstrata que implementa Template Method para geração de relatórios.

    Define o esqueleto do algoritmo de geração de relatórios:
    1. Coletar dados (abstrato - cada subclasse implementa)
    2. Processar dados (hook - pode ser sobrescrito)
    3. Formatar saída (abstrato - cada subclasse implementa)
    4. Exportar (conreto - suporta múltiplos formatos)

    Attributes:
        _dados_brutos: Dados coletados (para auditoria)
        _data_geracao: Timestamp da geração

    Examples:
        >>> class RelatorioTurma(GeradorRelatorio):
        ...     def coletar_dados(self):
        ...         return {'alunos': 30}
        ...     def formatar_saida(self, dados): 
        ...         return f"Total: {dados['alunos']}"
        >>> relatorio = RelatorioTurma()
        >>> resultado = relatorio.gerar()
    """

    def __init__(self):
        """Inicializa o gerador de relatório"""
        self._dados_brutos: Optional[Dict] = None
        self._data_geracao: Optional[datetime] = None


    # =================================
    # Template Method
    # =================================

    def gerar(self) -> str:
        """
        Template Method: Define esqueleto do algoritmo de geração.

        Este método NÃO deve ser sobrescrito por subclasses.
        Ele orquestra a chamada dos métodos abstratos e hooks.

        Returns:
            Relatório formatado como string

        Raises:
            RelatorioVazioException: Se nenhum dado foi coletado

        Examples:
            >>> relatorio = RelatorioTurma()
            >>> resultado = relatorio.gerar()
            >>> print(resultado)
            Relatório da Turma ES-01...
        """
        # Coleta de dados implementada por subclasse
        dados_brutos = self.coletar_dados()

        if not dados_brutos or (isinstance(dados_brutos, dict) and len(dados_brutos) == 0):
            raise RelatorioVazioException(
                "Nenhum dado foi coletado para gerar o relatório"
            )
        
        self._dados_brutos = dados_brutos
        self._data_geracao = datetime.now()

        # Hook method - pode ser sobrescrito 
        dados_processados = self.processar_dados(dados_brutos)

        # Implementado por subclasse
        relatorio_formatado = self.formatar_saida(dados_processados)

        return relatorio_formatado
    

    # =================================
    # Métodos Abstratos
    # =================================

    @abstractmethod
    def coletar_dados(self) -> Dict[str, Any]:
        """
        Coleta os dados necessários para o relatório.

        Este método DEVE ser implementado por todas as subclasses.
        Cada tipo de relatório coleta dados de forma diferente.

        Returns:
            Dicionário com dados brutos

        Examples:
            >>> def coletar_dados(self):
            ...     return {
            ...         'total_alunos': 30,
            ...         'media_geral': 7.5,
            ...         'notas': [...]
            ...     }
        """
        pass

    @abstractmethod
    def formatar_saida(self, dados_processados: Dict[str, Any]) -> str:
        """
        Formata os dados processados em string legível.

        Este método DEVE ser implementado por todas as subclasses.
        Cada tipo de relatório formata de forma diferente.

        Args:
            dados_processados: Dados já processados

        Returns:
            Relatório formatado como string

        Examples:
            >>> def formatar_saida(self, dados):
            ...     return f'''
            ...     Relatório de Turma
            ...     ==================
            ...     Total de alunos: {dados['total_alunos']}
            ...     Média geral: {dados['media_geral']}
            ...     '''
        """
        pass


    # =================================
    # Hook Methos
    # =================================

    def processar_dados(self, dados_brutos: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook method: Processa dados brutos antes da formatação.

        Implementação padrão: retorna dados sem modificação.
        Subclasses PODEM sobrescrever para adicionar processamento customizado.

        Args:
            dados_brutos: Dados coletados

        Returns:
            Dados processados (por padrão, igual aos dados brutos)

        Examples:
            >>> def processar_dados(self, dados_brutos):
            ...     dados_brutos['taxa_aprovacao'] = (
            ...         dados_brutos['aprovados'] / dados_brutos['total']
            ...     ) * 100
            ...     return dados_brutos
        """
        # Implementação padrão: sem processamento
        return dados_brutos
    

    # =================================
    # Métodos de exportação
    # =================================

    def exportar(
        self,
        conteudo: str,
        formato: FormatoRelatorio = FormatoRelatorio.TEXTO,
        nome_arquivo: Optional[str] = None
    ) -> bytes:
        """
        Exporta o relatório em diferentes formatos.

        Args:
            conteudo: Conteúdo do relatório (saída de gerar())
            formato: Formato de exportação
            nome_arquivo: Nome do arquivo (opcional)

        Returns:
            Bytes do arquivo exportado

        Raises:
            ValueError: Se formato não suportado

        Examples:
            >>> relatorio = RelatorioTurma()
            >>> conteudo = relatorio.gerar()
            >>> pdf_bytes = relatorio.exportar(conteudo, FormatoRelatorio.PDF)
        """
        if formato == FormatoRelatorio.TEXTO:
            return self._exportar_texto(conteudo)
        
        elif formato == FormatoRelatorio.PDF:
            return self._exportar_pdf(conteudo, nome_arquivo)
        
        elif formato == FormatoRelatorio.EXCEL:
            return self._exportar_excel(conteudo, nome_arquivo)
        
        elif formato == FormatoRelatorio.JSON:
            return self._exportar_json(conteudo)
        
        else:
            raise ValueError(f"Formato não suportado: {formato}")
        
    def _exportar_texto(self, conteudo: str) -> bytes:
        """Exporta como texto simples"""
        return conteudo.encode('utf-8')
    
    def _exportar_pdf(self, conteudo: str, nome_arquivo: Optional[str]) -> bytearray:
        """Exporta como PDF usando FPDF"""
        try:
            from fpdf import FPDF
        except ImportError:
            raise ImportError(
                "FPDF não instalado. Verifique a instalação de dependências"
            )
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("helvetica", size=12)
        pdf.set_left_margin(10)
        pdf.set_right_margin(10)

        for linha in conteudo.split('\n'):
            if linha.strip():
                try:
                    pdf.multi_cell(0, text=linha, align='L')
                except Exception as e:
                    pdf.cell(0, 10, text=linha[:100], ln=True)

            else:
                pdf.ln(5)

        return pdf.output()
    
    def _exportar_excel(self, conteudo: str, nome_arquivo: Optional[str]) -> bytes:
        """Exporta como Excel usando pandas"""
        try:
            import pandas as pd
            from io import BytesIO
        except ImportError:
            raise ImportError(
                "Pandas não instalado. Verifique a instalação de dependências"
            )
        
        df = pd.DataFrame({
            'Relatório': [conteudo]
        })

        output = BytesIO()
        df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)

        return output.read()
    
    def _exportar_json(self, conteudo: str) -> bytes:
        """Exporta dados como JSON"""
        dados_json = {
            'relatorio': conteudo,
            'data_geracao': self._data_geracao.isoformat() if self._data_geracao else None,
            'dados_brutos': self._dados_brutos
        }

        return json.dumps(dados_json, ensure_ascii=False, indent=2).encode('utf-8')
    
    # =================================
    # Métodos auxiliares
    # =================================

    def obter_metadados(self) -> Dict[str, Any]:
        """
        Retorna metadados do relatório gerado.

        Returns:
            Dicionário com metadados

        Examples:
            >>> relatorio.gerar()
            >>> metadados = relatorio.obter_metadados()
            >>> print(metadados['data_geracao'])
            2026-02-15T14:00:00
        """
        if not self._data_geracao:
            return {
                'status': 'nao_gerado',
                'mensagem': 'Relatório ainda não foi gerado'
            }
        
        return {
            'data_geracao': self._data_geracao.isoformat(),
            'total_dados': len(self._dados_brutos) if self._dados_brutos else 0,
            'dados_disponiveis': list(self._dados_brutos.keys()) if self._dados_brutos else []
        }
    
    def __repr__(self) -> str:
        """Representação oficial"""
        return (
            f"{self.__class__.__name__}("
            f"gerado={self._data_geracao is not None})"
        )


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

    def __init__(self, turma: 'Turma'):
        """
        Inicializa o gerador de relatório de turma.

        Args:
            turma: Instância de Turma

        Raises:
            TypeError: Se turma não for instância de Turma
        """
        super().__init__()

        if not hasattr(turma, 'codigo') or not hasattr(turma, 'alunos'):
            raise TypeError("Turma deve ter atributos 'codigo' e 'alunos'")
        
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

            if aluno_info['media'] < 6.0:
                alunos_dificuldade.append(aluno_info)

        dados['alunos'] = alunos_data
        dados['alunos_dificuldade'] = alunos_dificuldade

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
        linhas.append(f"Turma:      {dados_processados['codigo_turma']}")
        linhas.append(f"Disciplina: {dados_processados['disciplina']}")
        linhas.append(f"Semestre:   {dados_processados['semestre']}")

        # Estatísticas gerais
        linhas.append("-"*70)
        linhas.append("ESTATÍSTICAS GERAIS")
        linhas.append("-"*70)
        linhas.append(f"Total de Alunos:        {dados_processados['total_alunos']}")
        linhas.append(f"Média Geral da Turma:   {dados_processados['media_geral']:.2f}")
        linhas.append(f"Taxa de Aprovação:      {dados_processados['taxa_aprovacao']:.1f}%")
        linhas.append(f"Alunos com Dificuldade: {dados_processados['alunos_com_dificuldade']}")
        linhas.append("")

        # Ranking Top 5
        if 'ranking_top5' in dados_processados and dados_processados['ranking_top5']:
            linhas.append("-"*70)
            linhas.append("TOP 5 MELHORES ALUNOS")
            linhas.append("-"*70)

            for i, aluno in enumerate(dados_processados['ranking_top5'], 1):
                linhas.append(
                    f"{i}º - {aluno['nome']:<30} "
                    f"Matrícula: {aluno['matricula']:<10} "
                    f"Média: {aluno['media']:.2f}"
                )
            linhas.append("")

        # Alunos com dificuldade
        if dados_processados['alunos_dificuldade']:
            linhas.append("-"*70)
            linhas.append("ALUNOS QUE PRECISAM DE ATENÇÃO (Média < 6.0)")
            linhas.append("-"*70)

            for aluno in dados_processados['alunos_dificuldade']:
                linhas.append(
                    f"!  {aluno['nome']:<30} "
                    f"Matrícula: {aluno['matricula']:<10} "
                    f"Média: {aluno['media']:.2f}"
                )
            linhas.append("")
        else:
            linhas.append("-"*70)
            linhas.append("[OK] Nenhum aluno com dificuldade identificado!")
            linhas.append("")

        # Lista completa de alunos
        if dados_processados['alunos']:
            linhas.append("-"*70)
            linhas.append("LISTA COMPLETA DE ALUNOS")
            linhas.append("-"*70)

            for aluno in dados_processados['alunos']:
                status = "OK" if aluno['media'] >=6.0 else "!"
                linhas.append(
                    f"{status}  {aluno['nome']:<30} "
                    f"Matrícula: {aluno['matricula']:<10} "
                    f"Média: {aluno['media']:.2f}"
                )
            linhas.append("")

        # Rodapé
        linhas.append("="*70)
        linhas.append(f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
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
                key=lambda a: a['media'],
                reverse=True
            )

            dados_brutos['ranking_top5'] = alunos_ordenados[:5]
        else:
            dados_brutos['ranking_top5'] = []

        return dados_brutos