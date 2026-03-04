from abc import ABC, abstractmethod
from typing import Dict, List, Any
from educalin.domain.aluno import Aluno


class EstrategiaAnalise(ABC):
    """
    Classe abstrata que define o contrato para estratégias de análise de desempenho.
    
    Esta classe implementa o padrão Strategy, permitindo que diferentes algoritmos
    de análise de desempenho sejam implementados de forma intercambiável. Cada
    estratégia concreta deve implementar os métodos abstratos definidos nesta classe.
    
    O padrão Strategy permite:
    - Definir uma família de algoritmos de análise
    - Encapsular cada algoritmo de forma independente
    - Tornar os algoritmos intercambiáveis
    - Permitir que o algoritmo varie independentemente dos clientes que o utilizam
    
    Attributes:
        Nenhum atributo obrigatório na classe base.
    
    Examples:
        >>> class AnaliseSimples(EstrategiaAnalise):
        ...     def analisar(self, aluno, historico):
        ...         return {"media": 7.5}
        ...     def identificar_dificuldades(self):
        ...         return ["Matemática", "Física"]
    
    Note:
        Esta classe não pode ser instanciada diretamente. Apenas suas subclasses
        concretas que implementam todos os métodos abstratos podem ser instanciadas.
    """

    @abstractmethod
    def analisar(self, aluno: Aluno, historico: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa o desempenho de um aluno com base em seu histórico.
        
        Este método deve implementar a lógica específica de análise de desempenho,
        processando os dados do aluno e seu histórico acadêmico para gerar insights
        e métricas relevantes.
        
        Args:
            aluno (Aluno): Instância do aluno a ser analisado.
            historico (List[Dict[str, Any]]): Lista contendo o histórico de desempenho
                do aluno. Cada item pode conter informações como notas, avaliações,
                frequência, etc.
        
        Returns:
            Dict[str, Any]: Dicionário contendo os resultados da análise. A estrutura
                específica do dicionário depende da implementação concreta, mas deve
                incluir métricas relevantes sobre o desempenho do aluno.
        
        Raises:
            NotImplementedError: Se o método não for implementado pela subclasse.
        
        Examples:
            >>> estrategia = MinhaEstrategia()
            >>> aluno = Aluno(nome="João")
            >>> historico = [{"nota": 8.5, "disciplina": "Matemática"}]
            >>> resultado = estrategia.analisar(aluno, historico)
            >>> print(resultado)
            {'media': 8.5, 'status': 'aprovado'}
        """
        pass

    @abstractmethod
    def identificar_dificuldades(self) -> List[str]:
        """
        Identifica as principais dificuldades detectadas na análise.
        
        Este método deve retornar uma lista de dificuldades ou áreas problemáticas
        identificadas durante a análise do desempenho do aluno. As dificuldades
        podem incluir disciplinas com baixo desempenho, padrões de comportamento
        problemáticos, ou outras áreas que necessitem atenção.
        
        Returns:
            List[str]: Lista de strings descrevendo as dificuldades identificadas.
                Retorna uma lista vazia se nenhuma dificuldade for detectada.
        
        Raises:
            NotImplementedError: Se o método não for implementado pela subclasse.
        
        Examples:
            >>> estrategia = MinhaEstrategia()
            >>> dificuldades = estrategia.identificar_dificuldades()
            >>> print(dificuldades)
            ['Baixo desempenho em Matemática', 'Frequência irregular']
        
        Note:
            Este método geralmente deve ser chamado após o método analisar(),
            pois utiliza os resultados da análise para identificar as dificuldades.
        """
        pass
    