"""
Testes para a classe AnalisadorDesempenho (Context do padrão Strategy).
"""
import pytest
from educalin.services.analisadordesempenho import AnalisadorDesempenho
from educalin.services.estrategiaanalise import EstrategiaAnalise
from educalin.services.analisefrequencia import AnaliseFrequencia
from educalin.services.analisenotasbaixas import AnaliseNotasBaixas
from educalin.services.analiseregressao import AnaliseRegressao
from educalin.domain.aluno import Aluno


class TestAnalisadorDesempenho:
    """Testes para a classe AnalisadorDesempenho."""
    
    @pytest.fixture
    def aluno(self):
        """Fixture que cria um aluno para os testes."""
        return Aluno(nome="João Silva", email="joao@email.com", senha="senha123", matricula="12345")
    
    @pytest.fixture
    def estrategia_frequencia(self):
        """Fixture que cria uma estratégia de frequência."""
        return AnaliseFrequencia(min_avaliacoes=3)
    
    @pytest.fixture
    def estrategia_notas_baixas(self):
        """Fixture que cria uma estratégia de notas baixas."""
        return AnaliseNotasBaixas(limite_nota=60.0)
    
    @pytest.fixture
    def estrategia_regressao(self):
        """Fixture que cria uma estratégia de regressão."""
        return AnaliseRegressao(min_avaliacoes=3)
    
    @pytest.fixture
    def historico_regressao(self):
        """Fixture com histórico que apresenta regressão."""
        return [
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Matemática"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Matemática"},
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Matemática"},
        ]
    
    @pytest.fixture
    def historico_notas_baixas(self):
        """Fixture com histórico que apresenta notas baixas."""
        return [
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Física"},
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Física"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Química"},
        ]
    
    # Testes de Inicialização
    
    def test_inicializacao_com_estrategia_valida(self, estrategia_frequencia):
        """Testa inicialização com estratégia válida."""
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        assert analisador.estrategia == estrategia_frequencia
    
    def test_inicializacao_sem_estrategia(self):
        """Testa que é possível criar analisador sem estratégia inicial."""
        analisador = AnalisadorDesempenho()
        assert analisador.estrategia is None
    
    def test_inicializacao_estrategia_tipo_invalido(self):
        """Testa que rejeita estratégia que não herda de EstrategiaAnalise."""
        with pytest.raises(TypeError, match="A estratégia deve ser uma instância de EstrategiaAnalise"):
            AnalisadorDesempenho(estrategia="não é uma estratégia")
    
    # Testes do Property estrategia
    
    def test_getter_estrategia(self, estrategia_frequencia):
        """Testa o getter da estratégia."""
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        assert analisador.estrategia == estrategia_frequencia
    
    def test_setter_estrategia_valido(self, estrategia_frequencia, estrategia_notas_baixas):
        """Testa troca de estratégia em tempo de execução."""
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        analisador.estrategia = estrategia_notas_baixas
        assert analisador.estrategia == estrategia_notas_baixas
    
    def test_setter_estrategia_tipo_invalido(self, estrategia_frequencia):
        """Testa que setter valida o tipo da estratégia."""
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        with pytest.raises(TypeError, match="A estratégia deve ser uma instância de EstrategiaAnalise"):
            analisador.estrategia = "inválido"
    
    def test_setter_estrategia_none(self, estrategia_frequencia):
        """Testa que é possível definir estratégia como None."""
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        analisador.estrategia = None
        assert analisador.estrategia is None
    
    # Testes do método analisar
    
    def test_analisar_delega_para_estrategia(self, aluno, estrategia_frequencia, historico_notas_baixas):
        """Testa que analisar delega corretamente para a estratégia."""
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        resultado = analisador.analisar(aluno, historico_notas_baixas)
        
        # Deve conter os campos da estratégia de frequência
        assert 'aluno_nome' in resultado
        assert resultado['aluno_nome'] == "João Silva"
        assert 'topicos_baixa_frequencia' in resultado
    
    def test_analisar_sem_estrategia_definida(self, aluno, historico_notas_baixas):
        """Testa erro ao analisar sem estratégia definida."""
        analisador = AnalisadorDesempenho()
        with pytest.raises(ValueError, match="Nenhuma estratégia foi definida"):
            analisador.analisar(aluno, historico_notas_baixas)
    
    def test_analisar_com_diferentes_estrategias(self, aluno, estrategia_frequencia, 
                                                   estrategia_notas_baixas, historico_notas_baixas):
        """Testa que trocar estratégia muda o comportamento da análise."""
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        
        # Análise com estratégia de frequência
        resultado1 = analisador.analisar(aluno, historico_notas_baixas)
        assert 'topicos_baixa_frequencia' in resultado1
        
        # Troca para estratégia de notas baixas
        analisador.estrategia = estrategia_notas_baixas
        
        # Análise com estratégia de notas baixas
        resultado2 = analisador.analisar(aluno, historico_notas_baixas)
        assert 'notas_baixas' in resultado2
    
    def test_analisar_com_estrategia_regressao(self, aluno, estrategia_regressao, historico_regressao):
        """Testa análise com estratégia de regressão."""
        analisador = AnalisadorDesempenho(estrategia_regressao)
        resultado = analisador.analisar(aluno, historico_regressao)
        
        assert 'topicos_com_regressao' in resultado
        assert resultado['topicos_com_regressao'] > 0
    
    # Testes do método identificar_dificuldades
    
    def test_identificar_dificuldades_delega_para_estrategia(self, aluno, estrategia_regressao, 
                                                               historico_regressao):
        """Testa que identificar_dificuldades delega para a estratégia."""
        analisador = AnalisadorDesempenho(estrategia_regressao)
        
        # Primeiro precisa analisar
        analisador.analisar(aluno, historico_regressao)
        
        # Depois identificar dificuldades
        dificuldades = analisador.identificar_dificuldades()
        
        assert isinstance(dificuldades, list)
        assert len(dificuldades) > 0
        assert "Matemática" in dificuldades
    
    def test_identificar_dificuldades_sem_estrategia(self):
        """Testa erro ao identificar dificuldades sem estratégia."""
        analisador = AnalisadorDesempenho()
        with pytest.raises(ValueError, match="Nenhuma estratégia foi definida"):
            analisador.identificar_dificuldades()
    
    def test_identificar_dificuldades_sem_analise_previa(self, estrategia_frequencia):
        """Testa que pode chamar identificar_dificuldades sem analisar antes."""
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        dificuldades = analisador.identificar_dificuldades()
        
        # Deve retornar lista vazia se não analisou ainda
        assert dificuldades == []
    
    # Testes de Integração
    
    def test_fluxo_completo_analise(self, aluno, estrategia_notas_baixas, historico_notas_baixas):
        """Testa fluxo completo: criar, analisar, identificar dificuldades."""
        # 1. Criar analisador com estratégia
        analisador = AnalisadorDesempenho(estrategia_notas_baixas)
        
        # 2. Analisar desempenho
        resultado = analisador.analisar(aluno, historico_notas_baixas)
        assert 'aluno_nome' in resultado
        
        # 3. Identificar dificuldades
        dificuldades = analisador.identificar_dificuldades()
        assert isinstance(dificuldades, list)
        assert "Física" in dificuldades  # Nota baixa em Física
    
    def test_reutilizar_analisador_multiplas_analises(self, aluno, estrategia_frequencia):
        """Testa que o analisador pode ser reutilizado para múltiplas análises."""
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        
        # Primeira análise
        historico1 = [
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Álgebra"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Álgebra"},
        ]
        resultado1 = analisador.analisar(aluno, historico1)
        dificuldades1 = analisador.identificar_dificuldades()
        
        # Segunda análise (diferente)
        historico2 = [
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Geometria"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Geometria"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Geometria"},
        ]
        resultado2 = analisador.analisar(aluno, historico2)
        dificuldades2 = analisador.identificar_dificuldades()
        
        # Resultados devem ser diferentes
        assert resultado1 != resultado2
        # Segunda análise não tem dificuldades (muitos acertos)
        assert len(dificuldades2) == 0
    
    def test_trocar_estrategia_entre_analises(self, aluno, estrategia_frequencia, 
                                                estrategia_regressao, historico_regressao):
        """Testa troca de estratégia entre análises sucessivas."""
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        
        # Análise com primeira estratégia
        resultado1 = analisador.analisar(aluno, historico_regressao)
        
        # Troca estratégia
        analisador.estrategia = estrategia_regressao
        
        # Análise com segunda estratégia
        resultado2 = analisador.analisar(aluno, historico_regressao)
        
        # Resultados devem ter estruturas diferentes
        assert 'topicos_baixa_frequencia' in resultado1
        assert 'topicos_com_regressao' in resultado2
    
    def test_todas_estrategias_disponiveis(self, aluno):
        """Testa que o analisador funciona com todas as estratégias disponíveis."""
        historico = [
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Teste"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Teste"},
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Teste"},
        ]
        
        estrategias = [
            AnaliseFrequencia(),
            AnaliseNotasBaixas(),
            AnaliseRegressao(),
        ]
        
        for estrategia in estrategias:
            analisador = AnalisadorDesempenho(estrategia)
            resultado = analisador.analisar(aluno, historico)
            dificuldades = analisador.identificar_dificuldades()
            
            # Todas devem retornar estruturas válidas
            assert isinstance(resultado, dict)
            assert isinstance(dificuldades, list)
            assert 'aluno_nome' in resultado
    
    # Testes do método definir_estrategia
    
    def test_definir_estrategia_valida(self, estrategia_frequencia):
        """Testa definir estratégia com tipo válido."""
        analisador = AnalisadorDesempenho()
        analisador.definir_estrategia(estrategia_frequencia)
        assert analisador.estrategia == estrategia_frequencia
    
    def test_definir_estrategia_aceita_qualquer_estrategia(self):
        """Testa que aceita qualquer implementação de EstrategiaAnalise."""
        analisador = AnalisadorDesempenho()
        
        estrategias = [
            AnaliseFrequencia(min_avaliacoes=2),
            AnaliseNotasBaixas(limite_nota=50.0),
            AnaliseRegressao(min_avaliacoes=4),
        ]
        
        for estrategia in estrategias:
            analisador.definir_estrategia(estrategia)
            assert analisador.estrategia == estrategia
    
    def test_definir_estrategia_tipo_invalido(self):
        """Testa que rejeita tipo inválido."""
        analisador = AnalisadorDesempenho()
        with pytest.raises(TypeError, match="A estratégia deve ser uma instância de EstrategiaAnalise"):
            analisador.definir_estrategia("não é estratégia")
    
    def test_definir_estrategia_trocar_em_runtime(self, estrategia_frequencia, estrategia_notas_baixas):
        """Testa trocar estratégia em tempo de execução usando definir_estrategia."""
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        assert analisador.estrategia == estrategia_frequencia
        
        # Troca a estratégia em runtime
        analisador.definir_estrategia(estrategia_notas_baixas)
        assert analisador.estrategia == estrategia_notas_baixas
    
    # Testes do método executar_analise
    
    def test_executar_analise_com_aluno(self, aluno, estrategia_regressao):
        """Testa executar_analise que extrai histórico do aluno automaticamente."""
        from educalin.domain.avaliacao import Avaliacao
        from educalin.domain.nota import Nota
        from datetime import date
        
        # Adiciona notas ao aluno
        aval1 = Avaliacao("Prova 1", date(2026, 1, 10), 10.0, 0.4)
        aval2 = Avaliacao("Prova 2", date(2026, 1, 20), 10.0, 0.3)
        aval3 = Avaliacao("Prova 3", date(2026, 2, 1), 10.0, 0.3)
        
        nota1 = Nota(aluno, aval1, 9.0)
        nota2 = Nota(aluno, aval2, 7.0)
        nota3 = Nota(aluno, aval3, 5.0)
        
        aluno.adicionar_nota(nota1)
        aluno.adicionar_nota(nota2)
        aluno.adicionar_nota(nota3)
        
        analisador = AnalisadorDesempenho(estrategia_regressao)
        resultado = analisador.executar_analise(aluno)
        
        # Verifica que a análise foi realizada
        assert 'aluno_nome' in resultado
        assert resultado['aluno_nome'] == "João Silva"
        assert 'topicos_com_regressao' in resultado
    
    def test_executar_analise_sem_estrategia(self, aluno):
        """Testa erro ao executar análise sem estratégia definida."""
        analisador = AnalisadorDesempenho()
        with pytest.raises(ValueError, match="Nenhuma estratégia foi definida"):
            analisador.executar_analise(aluno)
    
    def test_executar_analise_aluno_sem_notas(self, aluno, estrategia_frequencia):
        """Testa erro ao analisar aluno sem notas."""
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        with pytest.raises(ValueError, match="não possui notas registradas"):
            analisador.executar_analise(aluno)
    
    def test_executar_analise_delega_para_estrategia(self, aluno, estrategia_notas_baixas):
        """Testa que executar_analise delega corretamente para a estratégia."""
        from educalin.domain.avaliacao import Avaliacao
        from educalin.domain.nota import Nota
        from datetime import date
        
        # Adiciona notas baixas
        aval1 = Avaliacao("Física", date(2026, 1, 10), 10.0, 0.5)
        aval2 = Avaliacao("Física", date(2026, 1, 20), 10.0, 0.5)
        
        nota1 = Nota(aluno, aval1, 5.0)
        nota2 = Nota(aluno, aval2, 4.0)
        
        aluno.adicionar_nota(nota1)
        aluno.adicionar_nota(nota2)
        
        analisador = AnalisadorDesempenho(estrategia_notas_baixas)
        resultado = analisador.executar_analise(aluno)
        
        # Verifica que delegou para estratégia de notas baixas
        assert 'notas_baixas' in resultado
        assert resultado['notas_baixas'] > 0
    
    # Testes do método gerar_sugestoes
    
    def test_gerar_sugestoes_com_dificuldades(self, aluno, estrategia_regressao):
        """Testa geração de sugestões quando há dificuldades."""
        from educalin.domain.avaliacao import Avaliacao
        from educalin.domain.nota import Nota
        from datetime import date
        
        # Adiciona notas com regressão em Matemática
        aval1 = Avaliacao("Matemática", date(2026, 1, 10), 10.0, 0.4)
        aval2 = Avaliacao("Matemática", date(2026, 1, 20), 10.0, 0.3)
        aval3 = Avaliacao("Matemática", date(2026, 2, 1), 10.0, 0.3)
        
        nota1 = Nota(aluno, aval1, 9.0)
        nota2 = Nota(aluno, aval2, 7.0)
        nota3 = Nota(aluno, aval3, 5.0)
        
        aluno.adicionar_nota(nota1)
        aluno.adicionar_nota(nota2)
        aluno.adicionar_nota(nota3)
        
        analisador = AnalisadorDesempenho(estrategia_regressao)
        analisador.executar_analise(aluno)
        
        sugestoes = analisador.gerar_sugestoes()
        
        assert isinstance(sugestoes, list)
        assert len(sugestoes) > 0
        # Deve conter sugestões relacionadas à Matemática
        assert any("Matemática" in s for s in sugestoes)
    
    def test_gerar_sugestoes_sem_dificuldades(self, aluno, estrategia_frequencia):
        """Testa geração de sugestões quando não há dificuldades."""
        from educalin.domain.avaliacao import Avaliacao
        from educalin.domain.nota import Nota
        from datetime import date
        
        # Adiciona notas boas
        aval1 = Avaliacao("Química", date(2026, 1, 10), 10.0, 0.4)
        aval2 = Avaliacao("Química", date(2026, 1, 20), 10.0, 0.3)
        aval3 = Avaliacao("Química", date(2026, 2, 1), 10.0, 0.3)
        
        nota1 = Nota(aluno, aval1, 9.0)
        nota2 = Nota(aluno, aval2, 9.0)
        nota3 = Nota(aluno, aval3, 9.0)
        
        aluno.adicionar_nota(nota1)
        aluno.adicionar_nota(nota2)
        aluno.adicionar_nota(nota3)
        
        analisador = AnalisadorDesempenho(estrategia_frequencia)
        analisador.executar_analise(aluno)
        
        sugestoes = analisador.gerar_sugestoes()
        
        assert isinstance(sugestoes, list)
        assert len(sugestoes) > 0
        assert "bom desempenho" in sugestoes[0].lower()
    
    def test_gerar_sugestoes_sem_estrategia(self):
        """Testa erro ao gerar sugestões sem estratégia definida."""
        analisador = AnalisadorDesempenho()
        with pytest.raises(ValueError, match="Nenhuma estratégia foi definida"):
            analisador.gerar_sugestoes()
    
    def test_gerar_sugestoes_formato_correto(self, aluno, estrategia_notas_baixas):
        """Testa que as sugestões têm formato correto."""
        from educalin.domain.avaliacao import Avaliacao
        from educalin.domain.nota import Nota
        from datetime import date
        
        # Adiciona notas baixas em Física
        aval = Avaliacao("Física", date(2026, 1, 10), 10.0, 1.0)
        nota = Nota(aluno, aval, 4.0)
        aluno.adicionar_nota(nota)
        
        analisador = AnalisadorDesempenho(estrategia_notas_baixas)
        analisador.executar_analise(aluno)
        
        sugestoes = analisador.gerar_sugestoes()
        
        # Cada sugestão deve ser uma string
        for sugestao in sugestoes:
            assert isinstance(sugestao, str)
            assert len(sugestao) > 0
