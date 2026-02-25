# tests/services/test_gerador_relatorio_integracao.py

import pytest
from educalin.services.relatorio import GeradorRelatorio, FormatoRelatorio

# ✅ Marca registrada no pytest.ini
pytestmark = pytest.mark.integration


class RelatorioSimples(GeradorRelatorio):
    def coletar_dados(self):
        return {'total': 100}
    
    def formatar_saida(self, dados):
        return f"Total: {dados['total']}\nMédia: 7.5"


class TestExportacaoReal:
    """Testes de integração com bibliotecas reais"""
    
    @pytest.fixture
    def relatorio(self):
        rel = RelatorioSimples()
        rel.gerar()  # Gerar para ter metadados
        return rel
    
    def test_exportar_texto_real(self, relatorio):
        """Teste real de exportação texto"""
        conteudo = "Relatório de Teste\nLinha 2\nLinha 3"
        
        resultado = relatorio.exportar(conteudo, FormatoRelatorio.TEXTO)
        
        assert isinstance(resultado, bytes)
        assert b"Relat" in resultado
        assert b"Linha 2" in resultado
    
    @pytest.mark.skipif(
        not pytest.importorskip("fpdf", minversion="2.0"),
        reason="FPDF2 não instalado"
    )
    def test_exportar_pdf_real(self, relatorio):
        """Teste real de exportação PDF"""
        conteudo = "Relatório de Teste\nTotal: 100\nMédia: 7.5"
        
        resultado = relatorio.exportar(conteudo, FormatoRelatorio.PDF)
        
        assert isinstance(resultado, bytearray)
        assert len(resultado) > 0
        # PDFs começam com %PDF
        assert resultado.startswith(b'%PDF')
    
    @pytest.mark.skipif(
        not pytest.importorskip("pandas", minversion="1.0"),
        reason="Pandas não instalado"
    )
    def test_exportar_excel_real(self, relatorio):
        """Teste real de exportação Excel"""
        conteudo = "Relatório de Teste"
        
        resultado = relatorio.exportar(conteudo, FormatoRelatorio.EXCEL)
        
        assert isinstance(resultado, bytes)
        assert len(resultado) > 0
        # Excel (XLSX) é um arquivo ZIP
        assert resultado.startswith(b'PK')
    
    def test_exportar_json_real(self, relatorio):
        """Teste real de exportação JSON"""
        conteudo = "Relatório de Teste"
        
        resultado = relatorio.exportar(conteudo, FormatoRelatorio.JSON)
        
        import json
        dados = json.loads(resultado.decode('utf-8'))
        
        assert dados['relatorio'] == conteudo
        assert 'data_geracao' in dados
        assert 'dados_brutos' in dados