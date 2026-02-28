import pytest
import json
from abc import ABC
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

from educalin.services.relatorios.base import (
    GeradorRelatorio,
    FormatoRelatorio,
    RelatorioVazioException
)


class RelatorioMock(GeradorRelatorio):
    """Implementação concreta para testar a classe abstrata"""

    def __init__(self):
        super().__init__()
        self.dados_coletados = None
        self.dados_processados = None
        self.saida_formatada = None

    def coletar_dados(self):
        """Simula coleta de dados"""
        return {'total_alunos': 30, 'media_geral': 7.5}
    
    def formatar_saida(self, dados_processados):
        """Simula formatação"""
        return f"Relatório: {dados_processados['total_alunos']} alunos"
    
class TestGeradorRelatorioAbstrato:
    """Testes da estrutura abstrata do GeradorRelatorio"""

    def test_classe_eh_abstrata(self):
        """GeradorRelatorio deve ser abstrata (não instanciável)"""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            GeradorRelatorio()

    def test_tem_metodos_abstratos(self):
        """Deve ter métodos abstratos obrigatórios"""
        metodos_abstratos = GeradorRelatorio.__abstractmethods__

        assert 'coletar_dados' in metodos_abstratos
        assert 'formatar_saida' in metodos_abstratos

    def test_subclasse_sem_implementar_abstratos_falha(self):
        """Subclasse que não implementa abstratos não pode ser instanciada"""

        class RelatorioIncompleto(GeradorRelatorio):
            pass

        with pytest.raises(TypeError):
            RelatorioIncompleto()

    def test_subclasse_implementando_abstratos_funciona(self):
        """Subclasse que implementa abstratos pode ser instanciada"""
        relatorio = RelatorioMock()

        assert isinstance(relatorio, GeradorRelatorio)


class TestGeradorRelatorioTemplateMethod:
    """Testes do método template gerar()"""

    @pytest.fixture
    def relatorio(self):
        """Fixture com relatório mock"""
        return RelatorioMock()
    
    def test_gerar_executa_passos_na_ordem(self, relatorio):
        """Template method deve chamar métodos na ordem correta"""
        relatorio.coletar_dados = Mock(return_value={'dados': 'teste'})
        relatorio.processar_dados = Mock(return_value={'dados': 'processados'})
        relatorio.formatar_saida = Mock(return_value={"Relatório formatado"})

        resultado = relatorio.gerar()

        assert relatorio.coletar_dados.call_count == 1
        assert relatorio.processar_dados.call_count == 1
        assert relatorio.formatar_saida.call_count == 1

        call_order = [
            relatorio.coletar_dados,
            relatorio.processar_dados,
            relatorio.formatar_saida
        ]

        for mock in call_order:
            assert mock.called

    def test_gerar_retorna_saida_formatada(self, relatorio):
        """gerar() deve retornar resultado de formatar_saida()"""
        resultado = relatorio.gerar()

        assert isinstance(resultado, str)
        assert "Relatório" in resultado

    def test_gerar_passa_dados_entre_etapas(self, relatorio):
        """Dados devem fluir: coletar -> processar -> formatar"""
        relatorio.coletar_dados = Mock(return_value={'raw': 'data'})
        relatorio.processar_dados = Mock(return_value={'processed': 'data'})
        relatorio.formatar_saida = Mock(return_value="output")

        relatorio.gerar()

        relatorio.processar_dados.assert_called_once_with({'raw': 'data'})
        relatorio.formatar_saida.assert_called_once_with({'processed': 'data'})

    def test_gerar_nao_pode_ser_sobrescrito(self):
        """Template method não deve ser sobrescrito por subclasses"""

        class RelatorioTentaSobrescrever(GeradorRelatorio):
            def coletar_dados(self):
                return {}
            
            def formatar_saida(self, dados):
                return ""
            
            def gerar(self):
                return "sobrescrito"
            
        relatorio = RelatorioTentaSobrescrever()


class TestGeradorRelatorioProcessarDados:
    """Testes do hook method processar_dados()""" 

    def test_processar_dados_eh_hook_method(self):
        """processar_dados() deve ter implementação padrão (hook)"""
        relatorio = RelatorioMock()

        dados_entrada = {'valor': 100}
        dados_saida = relatorio.processar_dados(dados_entrada)

        assert dados_saida == dados_entrada

    def test_subclasse_pode_sobrescrever_hook(self):
        """Subclasses podem opcionalmente sobrescrever processar_dados()"""

        class RelatorioComProcessamento(RelatorioMock):
            def processar_dados(self, dados_brutos):
                return {
                    **dados_brutos,
                    'media_geral': dados_brutos.get('media_geral', 0) + 1
                }
            
        relatorio = RelatorioComProcessamento()
        dados = {'media_geral': 7.5}

        processados = relatorio.processar_dados(dados)

        assert processados['media_geral'] == 8.5

    
class TestGeradorRelatorioExportar:
    """Testes do método exportar()"""

    @pytest.fixture
    def relatorio(self):
        return RelatorioMock()
    
    def test_exportar_formato_texto(self, relatorio):
        """Deve exportar como texto(padrão)"""
        conteudo = "Relatório de Teste"

        resultado = relatorio.exportar(conteudo, formato=FormatoRelatorio.TEXTO)

        assert resultado == conteudo.encode('utf-8')
        assert isinstance(resultado, bytes)
    
    @patch('fpdf.FPDF')
    def test_exportar_formato_pdf(self, mock_fpdf, relatorio):
        """Deve exportar como PDF usando FPDF"""
        conteudo = "Relatório de Teste"

        # Mock PDF
        mock_pdf_instance = MagicMock()
        mock_fpdf.return_value = mock_pdf_instance
        mock_pdf_instance.output.return_value = b"PDF Content"

        resultado = relatorio.exportar(conteudo, formato=FormatoRelatorio.PDF)

        mock_fpdf.assert_called_once()
        mock_pdf_instance.add_page.assert_called_once()
        mock_pdf_instance.set_font.assert_called_once_with("helvetica", size=12)
        mock_pdf_instance.multi_cell.assert_called_once()

        assert isinstance(resultado, bytes)
        assert resultado == b"PDF Content"

    @patch('pandas.DataFrame')
    def test_exportar_formato_excel(self, mock_dataframe, relatorio):
        """Deve exportar como Excel usando Pandas"""
        conteudo = "Relatório de Teste"

        mock_df = MagicMock()
        mock_dataframe.return_value = mock_df

        resultado = relatorio.exportar(conteudo, formato=FormatoRelatorio.EXCEL)

        mock_df.to_excel.assert_called_once()

        assert isinstance(resultado, bytes)

    def test_exportar_formato_invalido(self, relatorio):
        """Deve lançar erro para formato inválido"""
        with pytest.raises(ValueError, match="Formato não suportado"):
            relatorio.exportar("conteúdo", formato="formato_invalido")


class TestGeradorRelatorioValidacoes:
    """Teste de validações e exceções"""

    def test_coletar_dados_vazio_deve_lancar_excecao(self):
        """Deve lançar exceção se coletar_dados retornar vazio"""

        class RelatorioVazio(GeradorRelatorio):
            def coletar_dados(self):
                return {}
            
            def formatar_saida(self, dados):
                return ""
            
        relatorio = RelatorioVazio()

        with pytest.raises(RelatorioVazioException, match="Nenhum dado foi coletado"):
            relatorio.gerar()
    
    def test_dados_none_deve_lancar_excecao(self):
        """Deve lançar exceção se coletar_dados retornar None"""

        class RelatorioNone(GeradorRelatorio):
            def coletar_dados(self):
                return None
            
            def formatar_saida(self, dados):
                return ""
            
        relatorio = RelatorioNone()

        with pytest.raises(RelatorioVazioException):
            relatorio.gerar()

    
class TestGeradorRelatorioMetadados:
    """Testes de metadados do relatório"""

    def test_relatorio_tem_timestamp(self):
        """Relatório criado deve ter timestamp de criação"""
        relatorio = RelatorioMock()

        resultado = relatorio.gerar()

        assert hasattr(relatorio, '_data_geracao')
        assert relatorio._data_geracao is not None

    def test_relatorio_armazena_dados_brutos(self):
        """Deve armazenar dados brutos para auditoria"""
        relatorio = RelatorioMock()

        relatorio.gerar()

        assert hasattr(relatorio, '_dados_brutos')
        assert relatorio._dados_brutos is not None

    def test_obter_metadados(self):
        """Deve retornar metadados do relatório gerado"""
        relatorio = RelatorioMock()
        relatorio.gerar()

        metadados = relatorio.obter_metadados()

        assert 'data_geracao' in metadados
        assert 'total_dados' in metadados
        assert isinstance(metadados['data_geracao'], str)

    def test_obter_metadados_antes_de_gerar_retorna_status_nao_gerado(self):
        """obter_metadados() antes de gerar() deve indicar status 'nao_gerado'"""
        relatorio = RelatorioMock()

        metadados = relatorio.obter_metadados()

        assert metadados['status'] == 'nao_gerado'
        assert 'mensagem' in metadados

    def test_obter_metadados_lista_chaves_dos_dados(self):
        """obter_metadados() deve listar as chaves dos dados brutos"""
        relatorio = RelatorioMock()
        relatorio.gerar()

        metadados = relatorio.obter_metadados()

        assert 'dados_disponiveis' in metadados
        assert isinstance(metadados['dados_disponiveis'], list)
        assert 'total_alunos' in metadados['dados_disponiveis']


class TestGeradorRelatorioRepr:
    """Testes do método __repr__"""

    def test_repr_antes_de_gerar(self):
        """__repr__ deve indicar relatório não gerado"""
        relatorio = RelatorioMock()

        resultado = repr(relatorio)

        assert 'RelatorioMock' in resultado
        assert 'gerado=False' in resultado

    def test_repr_apos_gerar(self):
        """__repr__ deve indicar relatório gerado"""
        relatorio = RelatorioMock()
        relatorio.gerar()

        resultado = repr(relatorio)

        assert 'RelatorioMock' in resultado
        assert 'gerado=True' in resultado


class TestGeradorRelatorioExportarJSON:
    """Testes de exportação no formato JSON"""

    @pytest.fixture
    def relatorio(self):
        return RelatorioMock()

    def test_exportar_json_retorna_bytes(self, relatorio):
        """Exportar JSON deve retornar bytes"""
        conteudo = "Relatório de Teste"

        resultado = relatorio.exportar(conteudo, formato=FormatoRelatorio.JSON)

        assert isinstance(resultado, bytes)

    def test_exportar_json_conteudo_valido(self, relatorio):
        """JSON exportado deve ser decodificável e ter chave 'relatorio'"""
        conteudo = "Relatório de Teste"

        resultado = relatorio.exportar(conteudo, formato=FormatoRelatorio.JSON)
        dados = json.loads(resultado.decode('utf-8'))

        assert 'relatorio' in dados
        assert dados['relatorio'] == conteudo

    def test_exportar_json_sem_data_geracao(self, relatorio):
        """JSON exportado antes de gerar() deve ter data_geracao como None"""
        conteudo = "Relatório"

        resultado = relatorio.exportar(conteudo, formato=FormatoRelatorio.JSON)
        dados = json.loads(resultado.decode('utf-8'))

        assert dados['data_geracao'] is None

    def test_exportar_json_com_data_geracao(self, relatorio):
        """JSON exportado após gerar() deve ter data_geracao preenchida"""
        relatorio.gerar()
        conteudo = "Relatório"

        resultado = relatorio.exportar(conteudo, formato=FormatoRelatorio.JSON)
        dados = json.loads(resultado.decode('utf-8'))

        assert dados['data_geracao'] is not None
        assert isinstance(dados['data_geracao'], str)

    def test_exportar_json_inclui_dados_brutos(self, relatorio):
        """JSON exportado após gerar() deve incluir dados_brutos"""
        relatorio.gerar()
        conteudo = "Relatório"

        resultado = relatorio.exportar(conteudo, formato=FormatoRelatorio.JSON)
        dados = json.loads(resultado.decode('utf-8'))

        assert 'dados_brutos' in dados
        assert dados['dados_brutos'] is not None

    def test_exportar_json_caracteres_especiais(self, relatorio):
        """JSON exportado deve preservar caracteres especiais (ensure_ascii=False)"""
        conteudo = "Relatório com acentuação: ção"

        resultado = relatorio.exportar(conteudo, formato=FormatoRelatorio.JSON)
        dados = json.loads(resultado.decode('utf-8'))

        assert dados['relatorio'] == conteudo


class TestGeradorRelatorioExportarPDFErros:
    """Testes de tratamento de erros na exportação PDF"""

    @pytest.fixture
    def relatorio(self):
        return RelatorioMock()

    def test_exportar_pdf_sem_fpdf_lanca_import_error(self, relatorio):
        """Deve lançar ImportError se fpdf não estiver instalado"""
        with patch.dict('sys.modules', {'fpdf': None}):
            with pytest.raises(ImportError, match="FPDF não instalado"):
                relatorio.exportar("conteudo", formato=FormatoRelatorio.PDF)

    @patch('fpdf.FPDF')
    def test_exportar_pdf_lida_com_linha_vazia(self, mock_fpdf, relatorio):
        """Deve chamar pdf.ln() para linhas vazias no conteúdo"""
        mock_pdf_instance = MagicMock()
        mock_fpdf.return_value = mock_pdf_instance
        mock_pdf_instance.output.return_value = b"PDF Content"

        conteudo = "Linha com conteúdo\n\nLinha após vazia"

        resultado = relatorio.exportar(conteudo, formato=FormatoRelatorio.PDF)

        mock_pdf_instance.ln.assert_called()
        assert isinstance(resultado, bytes)

    @patch('fpdf.FPDF')
    def test_exportar_pdf_fallback_ao_falhar_multi_cell(self, mock_fpdf, relatorio):
        """Deve usar cell() como fallback se multi_cell() lançar exceção"""
        mock_pdf_instance = MagicMock()
        mock_fpdf.return_value = mock_pdf_instance
        mock_pdf_instance.multi_cell.side_effect = Exception("Erro de codificação")
        mock_pdf_instance.output.return_value = b"PDF Fallback"

        conteudo = "Linha com erro"

        resultado = relatorio.exportar(conteudo, formato=FormatoRelatorio.PDF)

        mock_pdf_instance.cell.assert_called()
        assert isinstance(resultado, bytes)


class TestGeradorRelatorioExportarExcelErros:
    """Testes de tratamento de erros na exportação Excel"""

    @pytest.fixture
    def relatorio(self):
        return RelatorioMock()

    def test_exportar_excel_sem_pandas_lanca_import_error(self, relatorio):
        """Deve lançar ImportError se pandas não estiver instalado"""
        with patch.dict('sys.modules', {'pandas': None}):
            with pytest.raises(ImportError, match="Pandas não instalado"):
                relatorio.exportar("conteudo", formato=FormatoRelatorio.EXCEL)