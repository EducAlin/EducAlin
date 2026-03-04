"""
Testes para a estratégia AnaliseFrequencia.
"""
import pytest
from educalin.services.analisefrequencia import AnaliseFrequencia
from educalin.domain.aluno import Aluno


class TestAnaliseFrequencia:
    """Testes para a estratégia AnaliseFrequencia."""
    
    @pytest.fixture
    def aluno(self):
        """Fixture que cria um aluno para os testes."""
        return Aluno(nome="Maria Santos", email="maria@email.com", senha="senha123", matricula="54321")
    
    @pytest.fixture
    def estrategia_padrao(self):
        """Fixture que cria uma estratégia com configuração padrão."""
        return AnaliseFrequencia()
    
    @pytest.fixture
    def estrategia_customizada(self):
        """Fixture que cria uma estratégia com configuração customizada."""
        return AnaliseFrequencia(min_avaliacoes=5, limite_aprovacao=70.0)
    
    # Testes de Inicialização
    
    def test_inicializacao_padrao(self):
        """Testa inicialização com valores padrão."""
        estrategia = AnaliseFrequencia()
        assert estrategia.min_avaliacoes == 3
        assert estrategia.limite_aprovacao == 60.0
        assert estrategia.identificar_dificuldades() == []
    
    def test_inicializacao_customizada(self):
        """Testa inicialização com valores customizados."""
        estrategia = AnaliseFrequencia(min_avaliacoes=5, limite_aprovacao=75.0)
        assert estrategia.min_avaliacoes == 5
        assert estrategia.limite_aprovacao == 75.0
    
    def test_inicializacao_min_avaliacoes_tipo_invalido(self):
        """Testa que min_avaliacoes deve ser inteiro."""
        with pytest.raises(TypeError, match="O número mínimo de avaliações deve ser um inteiro"):
            AnaliseFrequencia(min_avaliacoes=3.5)
    
    def test_inicializacao_min_avaliacoes_menor_que_um(self):
        """Testa que min_avaliacoes deve ser pelo menos 1."""
        with pytest.raises(ValueError, match="O número mínimo de avaliações deve ser pelo menos 1"):
            AnaliseFrequencia(min_avaliacoes=0)
    
    def test_inicializacao_limite_aprovacao_tipo_invalido(self):
        """Testa que limite_aprovacao deve ser numérico."""
        with pytest.raises(TypeError, match="O limite de aprovação deve ser um número"):
            AnaliseFrequencia(limite_aprovacao="60")
    
    def test_inicializacao_limite_aprovacao_fora_range(self):
        """Testa que limite_aprovacao deve estar entre 0 e 100."""
        with pytest.raises(ValueError, match="O limite de aprovação deve estar entre 0 e 100"):
            AnaliseFrequencia(limite_aprovacao=150)
    
    # Testes dos Properties
    
    def test_getter_min_avaliacoes(self, estrategia_padrao):
        """Testa o getter do atributo min_avaliacoes."""
        assert estrategia_padrao.min_avaliacoes == 3
    
    def test_setter_min_avaliacoes_valido(self, estrategia_padrao):
        """Testa o setter com valor válido."""
        estrategia_padrao.min_avaliacoes = 5
        assert estrategia_padrao.min_avaliacoes == 5
    
    def test_setter_min_avaliacoes_tipo_invalido(self, estrategia_padrao):
        """Testa que setter valida o tipo."""
        with pytest.raises(TypeError):
            estrategia_padrao.min_avaliacoes = 3.5
    
    def test_setter_min_avaliacoes_valor_invalido(self, estrategia_padrao):
        """Testa que setter valida o valor mínimo."""
        with pytest.raises(ValueError):
            estrategia_padrao.min_avaliacoes = 0
    
    def test_getter_limite_aprovacao(self, estrategia_padrao):
        """Testa o getter do atributo limite_aprovacao."""
        assert estrategia_padrao.limite_aprovacao == 60.0
    
    def test_setter_limite_aprovacao_valido(self, estrategia_padrao):
        """Testa o setter com valor válido."""
        estrategia_padrao.limite_aprovacao = 70.0
        assert estrategia_padrao.limite_aprovacao == 70.0
    
    def test_setter_limite_aprovacao_tipo_invalido(self, estrategia_padrao):
        """Testa que setter valida o tipo."""
        with pytest.raises(TypeError):
            estrategia_padrao.limite_aprovacao = "70"
    
    def test_setter_limite_aprovacao_valor_invalido(self, estrategia_padrao):
        """Testa que setter valida o valor."""
        with pytest.raises(ValueError):
            estrategia_padrao.limite_aprovacao = 200
    
    # Testes do Método analisar() - Casos Normais
    
    def test_analisar_topico_com_acertos_suficientes(self, estrategia_padrao, aluno):
        """Testa tópico com número suficiente de acertos."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Álgebra"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Álgebra"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Álgebra"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['aluno_nome'] == "Maria Santos"
        assert resultado['total_avaliacoes'] == 3
        assert resultado['topicos_analisados'] == 1
        assert resultado['topicos_baixa_frequencia'] == 0
        assert len(resultado['detalhes']) == 1
        assert resultado['detalhes'][0]['acertos'] == 3
    
    def test_analisar_topico_com_poucos_acertos(self, estrategia_padrao, aluno):
        """Testa tópico com poucos acertos."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Geometria"},
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Geometria"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['topicos_baixa_frequencia'] == 1
        assert resultado['detalhes'][0]['acertos'] == 1  # Apenas 1 acerto (< 3)
        assert resultado['detalhes'][0]['total'] == 2
    
    def test_analisar_multiplos_topicos(self, estrategia_padrao, aluno):
        """Testa análise com múltiplos tópicos."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Matemática"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Matemática"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Matemática"},
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Física"},
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Física"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['topicos_analisados'] == 2
        assert resultado['topicos_baixa_frequencia'] == 1  # Apenas Física
    
    def test_analisar_conta_apenas_acertos(self, estrategia_padrao, aluno):
        """Testa que apenas notas >= limite são contadas como acertos."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Química"},  # 80% - acerto
            {"nota": 6.0, "valor_maximo": 10.0, "topico": "Química"},  # 60% - acerto
            {"nota": 5.9, "valor_maximo": 10.0, "topico": "Química"},  # 59% - não acerto
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Química"}   # 40% - não acerto
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['detalhes'][0]['total'] == 4
        assert resultado['detalhes'][0]['acertos'] == 2
        assert resultado['topicos_baixa_frequencia'] == 1  # 2 acertos < 3
    
    def test_analisar_com_limite_customizado(self, estrategia_customizada, aluno):
        """Testa análise com limite de aprovação customizado (70%)."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "História"},  # 80% - acerto
            {"nota": 6.5, "valor_maximo": 10.0, "topico": "História"},  # 65% - não acerto
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "História"}   # 70% - acerto
        ]
        
        resultado = estrategia_customizada.analisar(aluno, historico)
        
        # Com limite 70%, apenas 2 acertos (min é 5)
        assert resultado['detalhes'][0]['acertos'] == 2
        assert resultado['topicos_baixa_frequencia'] == 1
    
    def test_analisar_calcula_percentual_acerto_corretamente(self, estrategia_padrao, aluno):
        """Testa que o percentual de acerto é calculado corretamente."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Geografia"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Geografia"},
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Geografia"},
            {"nota": 3.0, "valor_maximo": 10.0, "topico": "Geografia"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        # 2 acertos de 4 = 50%
        assert resultado['detalhes'][0]['percentual_acerto'] == 50.0
    
    # Testes do Método analisar() - Casos Extremos
    
    def test_analisar_com_historico_vazio(self, estrategia_padrao, aluno):
        """Testa análise com histórico vazio."""
        resultado = estrategia_padrao.analisar(aluno, [])
        
        assert resultado['total_avaliacoes'] == 0
        assert resultado['topicos_analisados'] == 0
        assert resultado['topicos_baixa_frequencia'] == 0
        assert resultado['detalhes'] == []
    
    def test_analisar_topico_sem_nenhum_acerto(self, estrategia_padrao, aluno):
        """Testa tópico sem nenhum acerto."""
        historico = [
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Biologia"},
            {"nota": 3.0, "valor_maximo": 10.0, "topico": "Biologia"},
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "Biologia"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['detalhes'][0]['acertos'] == 0
        assert resultado['topicos_baixa_frequencia'] == 1
    
    def test_analisar_topico_com_todos_acertos(self, estrategia_padrao, aluno):
        """Testa tópico onde todas as avaliações são acertos."""
        historico = [
            {"nota": 10.0, "valor_maximo": 10.0, "topico": "Inglês"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Inglês"},
            {"nota": 8.5, "valor_maximo": 10.0, "topico": "Inglês"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['detalhes'][0]['acertos'] == 3
        assert resultado['detalhes'][0]['percentual_acerto'] == 100.0
        assert resultado['topicos_baixa_frequencia'] == 0
    
    def test_analisar_com_topico_nao_especificado(self, estrategia_padrao, aluno):
        """Testa análise quando tópico não é fornecido."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0},
            {"nota": 7.0, "valor_maximo": 10.0},
            {"nota": 9.0, "valor_maximo": 10.0}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['detalhes'][0]['topico'] == "Não especificado"
        assert resultado['detalhes'][0]['acertos'] == 3
    
    def test_analisar_com_valor_maximo_zero(self, estrategia_padrao, aluno):
        """Testa análise quando valor máximo é zero."""
        historico = [
            {"nota": 5.0, "valor_maximo": 0, "topico": "Teste"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        # Com valor_maximo = 0, percentual é 0, não conta como acerto
        assert resultado['detalhes'][0]['acertos'] == 0
    
    def test_analisar_com_min_avaliacoes_1(self, aluno):
        """Testa análise com mínimo de 1 avaliação."""
        estrategia = AnaliseFrequencia(min_avaliacoes=1)
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Arte"}
        ]
        
        resultado = estrategia.analisar(aluno, historico)
        
        # 1 acerto atinge o mínimo
        assert resultado['topicos_baixa_frequencia'] == 0
    
    def test_analisar_exatamente_no_minimo(self, estrategia_padrao, aluno):
        """Testa tópico com exatamente o número mínimo de acertos."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Artes"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Artes"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Artes"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        # Exatamente 3 acertos (mínimo é 3) - não é considerado problema
        assert resultado['topicos_baixa_frequencia'] == 0
    
    def test_analisar_um_acerto_a_menos_do_minimo(self, estrategia_padrao, aluno):
        """Testa tópico com um acerto a menos que o mínimo."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Filosofia"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Filosofia"},
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "Filosofia"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        # 2 acertos < 3 mínimo
        assert resultado['detalhes'][0]['acertos'] == 2
        assert resultado['topicos_baixa_frequencia'] == 1
    
    # Testes do Método identificar_dificuldades()
    
    def test_identificar_dificuldades_apos_analisar(self, estrategia_padrao, aluno):
        """Testa identificação de dificuldades após análise."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Cálculo"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Estatística"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Álgebra"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Álgebra"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Álgebra"}
        ]
        
        estrategia_padrao.analisar(aluno, historico)
        dificuldades = estrategia_padrao.identificar_dificuldades()
        
        # Cálculo (1 acerto) e Estatística (1 acerto) < 3
        assert len(dificuldades) == 2
        assert "Cálculo" in dificuldades
        assert "Estatística" in dificuldades
        assert "Álgebra" not in dificuldades
    
    def test_identificar_dificuldades_sem_analisar(self, estrategia_padrao):
        """Testa identificação antes de executar análise."""
        dificuldades = estrategia_padrao.identificar_dificuldades()
        assert dificuldades == []
    
    def test_identificar_dificuldades_retorna_copia(self, estrategia_padrao, aluno):
        """Testa que o método retorna uma cópia da lista."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Programação"}
        ]
        
        estrategia_padrao.analisar(aluno, historico)
        dificuldades1 = estrategia_padrao.identificar_dificuldades()
        dificuldades2 = estrategia_padrao.identificar_dificuldades()
        
        # Modificar uma lista não deve afetar a outra
        dificuldades1.append("Teste")
        assert "Teste" not in dificuldades2
    
    def test_identificar_dificuldades_atualiza_apos_nova_analise(self, estrategia_padrao, aluno):
        """Testa que dificuldades são atualizadas em nova análise."""
        historico1 = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Redes"}
        ]
        
        estrategia_padrao.analisar(aluno, historico1)
        dificuldades1 = estrategia_padrao.identificar_dificuldades()
        
        assert len(dificuldades1) == 1
        assert "Redes" in dificuldades1
        
        # Nova análise com histórico diferente
        historico2 = [
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Banco de Dados"}
        ]
        
        estrategia_padrao.analisar(aluno, historico2)
        dificuldades2 = estrategia_padrao.identificar_dificuldades()
        
        # Dificuldades devem ser substituídas
        assert len(dificuldades2) == 1
        assert "Banco de Dados" in dificuldades2
        assert "Redes" not in dificuldades2
    
    def test_identificar_dificuldades_sem_dificuldades(self, estrategia_padrao, aluno):
        """Testa identificação quando não há dificuldades."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Lógica"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Lógica"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Lógica"}
        ]
        
        estrategia_padrao.analisar(aluno, historico)
        dificuldades = estrategia_padrao.identificar_dificuldades()
        
        assert dificuldades == []
    
    # Testes de Integração
    
    def test_fluxo_completo_analise(self, estrategia_padrao, aluno):
        """Testa o fluxo completo de análise."""
        historico = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Python"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "Python"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "Python"},
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "Java"},
            {"nota": 4.0, "valor_maximo": 10.0, "topico": "JavaScript"},
            {"nota": 5.0, "valor_maximo": 10.0, "topico": "JavaScript"}
        ]
        
        resultado = estrategia_padrao.analisar(aluno, historico)
        
        assert resultado['aluno_nome'] == "Maria Santos"
        assert resultado['total_avaliacoes'] == 6
        assert resultado['topicos_analisados'] == 3
        assert resultado['topicos_baixa_frequencia'] == 2  # Java (1) e JavaScript (0)
        
        dificuldades = estrategia_padrao.identificar_dificuldades()
        assert len(dificuldades) == 2
        assert "Java" in dificuldades
        assert "JavaScript" in dificuldades
        assert "Python" not in dificuldades
    
    def test_multiplas_analises_sequenciais(self, estrategia_padrao, aluno):
        """Testa múltiplas análises sequenciais com o mesmo objeto."""
        # Primeira análise
        historico1 = [{"nota": 8.0, "valor_maximo": 10.0, "topico": "HTML"}]
        resultado1 = estrategia_padrao.analisar(aluno, historico1)
        assert resultado1['topicos_baixa_frequencia'] == 1
        
        # Segunda análise
        historico2 = [
            {"nota": 8.0, "valor_maximo": 10.0, "topico": "CSS"},
            {"nota": 7.0, "valor_maximo": 10.0, "topico": "CSS"},
            {"nota": 9.0, "valor_maximo": 10.0, "topico": "CSS"}
        ]
        resultado2 = estrategia_padrao.analisar(aluno, historico2)
        assert resultado2['topicos_baixa_frequencia'] == 0
        
        # Verifica que dificuldades foram limpas
        dificuldades = estrategia_padrao.identificar_dificuldades()
        assert len(dificuldades) == 0
