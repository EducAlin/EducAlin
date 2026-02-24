from typing import Dict, List, Any
from educalin.domain.aluno import Aluno
from educalin.services.estrategiaanalise import EstrategiaAnalise


class AnaliseNotasBaixas(EstrategiaAnalise):
    """
    Estratégia de análise que identifica dificuldades baseada em notas abaixo de um limite.
    
    Esta estratégia filtra as avaliações onde o aluno obteve notas abaixo de um limite
    configurável (padrão 60% da nota máxima) e identifica os tópicos/disciplinas onde
    o aluno apresenta dificuldades.
    
    Attributes:
        _limite_nota (float): Percentual mínimo de aproveitamento (0-100).
            Notas abaixo deste percentual são consideradas problemáticas.
        _dificuldades (List[str]): Lista de tópicos onde foram identificadas dificuldades.
    
    Examples:
        >>> estrategia = AnaliseNotasBaixas(limite_nota=60.0)
        >>> aluno = Aluno(nome="Maria")
        >>> historico = [
        ...     {"nota": 5.0, "valor_maximo": 10.0, "topico": "Álgebra"},
        ...     {"nota": 8.0, "valor_maximo": 10.0, "topico": "Geometria"}
        ... ]
        >>> resultado = estrategia.analisar(aluno, historico)
        >>> dificuldades = estrategia.identificar_dificuldades()
        >>> print(dificuldades)
        ['Álgebra']
    """
    
    def __init__(self, limite_nota: float = 60.0):
        """
        Inicializa a estratégia de análise de notas baixas.
        
        Args:
            limite_nota (float): Percentual mínimo de aproveitamento (0-100).
                Padrão é 60.0%.
        
        Raises:
            TypeError: Se limite_nota não for um número.
            ValueError: Se limite_nota não estiver entre 0 e 100.
        """
        if not isinstance(limite_nota, (int, float)):
            raise TypeError("O limite de nota deve ser um número.")
        
        if not 0 <= limite_nota <= 100:
            raise ValueError("O limite de nota deve estar entre 0 e 100.")
        
        self._limite_nota = limite_nota
        self._dificuldades = []
    
    @property
    def limite_nota(self) -> float:
        """Retorna o limite de nota configurado."""
        return self._limite_nota
    
    @limite_nota.setter
    def limite_nota(self, valor: float):
        """
        Define um novo limite de nota.
        
        Args:
            valor (float): Novo percentual mínimo (0-100).
        
        Raises:
            TypeError: Se valor não for um número.
            ValueError: Se valor não estiver entre 0 e 100.
        """
        if not isinstance(valor, (int, float)):
            raise TypeError("O limite de nota deve ser um número.")
        
        if not 0 <= valor <= 100:
            raise ValueError("O limite de nota deve estar entre 0 e 100.")
        
        self._limite_nota = valor
    
    def analisar(self, aluno: Aluno, historico: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa o desempenho do aluno identificando notas abaixo do limite.
        
        Filtra as avaliações onde a nota obtida é inferior ao percentual mínimo
        estabelecido e armazena os tópicos problemáticos para posterior consulta.
        
        Args:
            aluno (Aluno): Instância do aluno a ser analisado.
            historico (List[Dict[str, Any]]): Lista de dicionários contendo:
                - nota (float): Valor da nota obtida
                - valor_maximo (float): Valor máximo possível
                - topico (str): Nome do tópico/disciplina avaliado
        
        Returns:
            Dict[str, Any]: Dicionário com os resultados da análise contendo:
                - aluno_nome (str): Nome do aluno analisado
                - total_avaliacoes (int): Total de avaliações no histórico
                - notas_baixas (int): Quantidade de notas abaixo do limite
                - percentual_dificuldade (float): Percentual de notas baixas
                - detalhes (List[Dict]): Lista com detalhes das notas baixas
        
        Examples:
            >>> estrategia = AnaliseNotasBaixas()
            >>> aluno = Aluno(nome="João")
            >>> historico = [{"nota": 4.0, "valor_maximo": 10.0, "topico": "Matemática"}]
            >>> resultado = estrategia.analisar(aluno, historico)
            >>> resultado['notas_baixas']
            1
        """
        self._dificuldades = []
        notas_baixas = []
        
        for item in historico:
            nota = item.get('nota', 0)
            valor_maximo = item.get('valor_maximo', 10)
            topico = item.get('topico', 'Não especificado')
            
            # Calcula o percentual de aproveitamento
            percentual = (nota / valor_maximo * 100) if valor_maximo > 0 else 0
            
            # Verifica se está abaixo do limite
            if percentual < self._limite_nota:
                self._dificuldades.append(topico)
                notas_baixas.append({
                    'topico': topico,
                    'nota': nota,
                    'valor_maximo': valor_maximo,
                    'percentual': round(percentual, 2)
                })
        
        total = len(historico)
        percentual_dificuldade = (len(notas_baixas) / total * 100) if total > 0 else 0
        
        return {
            'aluno_nome': aluno.nome,
            'total_avaliacoes': total,
            'notas_baixas': len(notas_baixas),
            'percentual_dificuldade': round(percentual_dificuldade, 2),
            'detalhes': notas_baixas
        }
    
    def identificar_dificuldades(self) -> List[str]:
        """
        Retorna a lista de tópicos onde foram identificadas dificuldades.
        
        Este método retorna os tópicos das avaliações que tiveram notas abaixo
        do limite estabelecido, conforme identificado na última execução do
        método analisar().
        
        Returns:
            List[str]: Lista de tópicos com dificuldades. Retorna lista vazia
                se nenhuma dificuldade foi identificada ou se analisar() ainda
                não foi executado.
        
        Examples:
            >>> estrategia = AnaliseNotasBaixas()
            >>> dificuldades = estrategia.identificar_dificuldades()
            >>> print(dificuldades)
            ['Álgebra', 'Cálculo']
        
        Note:
            Este método deve ser chamado após analisar() para obter resultados
            relevantes.
        """
        return self._dificuldades.copy()
