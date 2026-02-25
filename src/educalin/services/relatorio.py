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