# EducAlin

## Nome da equipe

EducAlin

## Nomes dos integrantes

| Nome | GitHub |
| :---- | :---- |
| Elder Rayan Oliveira Silva | [@eldrayan](https://github.com/eldrayan) |
| Samuel Wagner Tiburi Silveira | [@samsilveira](https://github.com/samsilveira) |
| Pedro Yan Alcantara Palacio | [@pedropalacioo](https://github.com/pedropalacioo) |

## Descrição detalhada do domínio

O cenário educacional de base no Brasil enfrenta um desafio significativo: a ausência de um acompanhamento individualizado do aluno. Em um modelo de sala de aula tradicional, os professores encontram dificuldade para identificar e sanar as dificuldades particulares de cada estudante, especialmente a falta de base em conteúdos fundamentais. Essa lacuna resulta em uma queda no desempenho, com alunos progredindo entre os anos escolares sem o domínio de conhecimentos essenciais e gera o que é descrito como uma "relação alienada" entre professor e aluno.

O sistema EducAlin surge como uma ferramenta tecnológica auxiliar para endereçar este problema através de:

1. Análise Individualizada de Dados: Sistema inteligente que processa notas, frequência e desempenho em tópicos específicos para identificar padrões e dificuldades de cada aluno.
2. Geração Dinâmica de Conteúdo: Recomendação automática de materiais de estudo personalizados baseada nas dificuldades identificadas, utilizando diferentes estratégias de análise.
3. Múltiplos atores e Regras Complexas:
    - Professores: Criam turmas, registram notas associadas a tópicos, geram relatórios, criam Planos de Ação personalizados
    - Alunos: Visualizam desempenho, acessam materiais recomendados, interagem em fóruns, acompanham metas
    - Coordenadores: Geram relatórios consolidados e comparativos entre turmas

A complexidade do sistema justifica POO através de:

- Hierarquias de abstração (usuários, materiais, relatórios, estratégias de análise)
- Polimorfismo estratégico (diferentes tipos de análise, materiais e relatórios processados uniformemente)
- Regras de negócio variáveis (critérios de identificação de dificuldades, permissões por perfil, validações contextuais)
- Composição dinâmica (Planos de Ação agregam materiais, Turmas agregam alunos)

## Estrutura de pastas
```
educalin/
│
├── src/
│   └── educalin/
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── usuario.py
│       │   ├── turma.py
│       │   ├── material.py
│       │   ├── avaliacao.py
│       │   ├── plano_acao.py
│       │   └── meta.py
│       │
│       ├── services/
│       │   ├── __init__.py
│       │   ├── analisador.py
│       │   ├── relatorio.py
│       │   └── notificador.py
│       │
│       ├── factories/
│       │   ├── __init__.py
│       │   └── material_factory.py
│       │
│       ├── repositories/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── models.py
│       │
│       ├── api/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── dependencies.py
│       │   └── routes/
│       │       ├── auth.py
│       │       ├── turmas.py
│       │       └── materiais.py
│       │
│       └── utils/
│           ├── __init__.py
│           └── mixins.py
│
├── tests/
│   ├── domain/
│   ├── services/
│   └── integration/
│
├── templates/
│   ├── base.html
│   ├── login.html
│   └── dashboard/
│
├── static/
│   ├── css/
│   └── js/
│
├── database/
│   └── educalin.db
│
├── docs/
│   ├── poo_especificacao_projeto.md
│   ├── Requisitos_EducAlin.md
│   └── proposta.md
│
├── .gitignore
├── LICENSE
├── poetry.lock
├── pyproject.toml
└── README.md
```
## Justificativa da complexidade do sistema

1. Análisde de Dados Individualizada:

    - Identificação automática de dificuldade por múltiplos critérios (nota < 60%, frequência baixa, regressão temporal)
    - Aplicação de diferentes estratégias de análise (Strategy Pattern) configuráveis por professor
    - Cálculos de indicadores de desempenho agregados (por tópico, disciplina, período)
    - Geração de sugestões personalizadas baseadas em regra de negócio

2. Geração Dinâmica de Conteúdo

    - Criação polimórfica de diferentes tipos de materiais (PDF, Vídeo, Link) via Factory Method
    - Validação específica por tipo de material
    - Composição dinâmica de Planos de Ação com materiais heterogêneos
    - Sistema de recomendação que cruza dificuldade dos alunos com materiais disponíveis

3. Múltiplos Atores e Regras

   - 3 perfis de usuário com permissões e funcionalidades distintas
   - Hierarquia múltipa (AutenticavelMixin + NotificavelMixin + Usuario)
   - Fluxos condicionais baseados em perfil, status, dados históricos
   - Eventos e notificações assíncronas (Observer Pattern) para múltiplos interessados

4. Arquitetura em Camadas

    - Domínio: Entidades (Usuario, Turma, PlanoAcao, MaterialEstudo)
    - Aplicação: Serviços (AnalisadorDesempenho, GeradorRelatorio)
    - Infraestrutura: Repositórios, Notificadores, Factories

## Diagrama UML (classes e relações)

```mermaid
classDiagram
    %% Hierarquia de Usuários
    class Usuario {
        <<abstract>>
        -str _nome
        -str _email
        -str __senha
        +autenticar()*
        +validar_credenciais()
    }
    
    class AutenticavelMixin {
        +validar_credenciais()
        +resetar_senha()
    }
    
    class NotificavelMixin {
        +receber_notificacao(mensagem)
        +configurar_preferencias_notificacao()
    }
    
    class Professor {
        -str _registro_funcional
        -List~Turma~ _turmas
        +criar_plano_acao(aluno)
        +registrar_nota(aluno, avaliacao, nota)
        +gerar_relatorio(tipo)
    }
    
    class Aluno {
        -str _matricula
        -Dict~str,float~ _desempenho
        +visualizar_desempenho()
        +acessar_material(material_id)
    }
    
    class Coordenador {
        -str _codigo_coordenacao
        +gerar_relatorio_consolidado()
        +comparar_turmas()
    }
    
    Usuario <|-- Professor
    Usuario <|-- Aluno
    Usuario <|-- Coordenador
    AutenticavelMixin <|-- Professor
    AutenticavelMixin <|-- Aluno
    AutenticavelMixin <|-- Coordenador
    NotificavelMixin <|-- Aluno
    NotificavelMixin <|-- Professor

    %% Hierarquia de Materiais
    class MaterialEstudo {
        <<abstract>>
        -str _titulo
        -str _descricao
        -datetime _data_upload
        -Professor _autor
        +validar_formato()*
        +obter_tamanho()
    }
    
    class MaterialPDF {
        -int _num_paginas
        +validar_formato()
        +extrair_texto()
    }
    
    class MaterialVideo {
        -int _duracao_segundos
        -str _codec
        +validar_formato()
        +gerar_thumbnail()
    }
    
    class MaterialLink {
        -str _url
        -str _tipo_conteudo
        +validar_formato()
        +verificar_disponibilidade()
    }
    
    MaterialEstudo <|-- MaterialPDF
    MaterialEstudo <|-- MaterialVideo
    MaterialEstudo <|-- MaterialLink

    %% Hierarquia: Estratégias de Análise
    class EstrategiaAnalise {
        <<abstract>>
        +analisar(aluno, historico)*
        +identificar_dificuldades()*
    }
    
    class AnaliseNotasBaixas {
        -float _limite_nota
        +analisar(aluno, historico)
        +identificar_dificuldades()
    }
    
    class AnaliseFrequencia {
        -int _min_avaliacoes
        +analisar(aluno, historico)
        +identificar_dificuldades()
    }
    
    class AnaliseRegressao {
        +analisar(aluno, historico)
        +identificar_dificuldades()
        +calcular_tendencia()
    }
    
    EstrategiaAnalise <|-- AnaliseNotasBaixas
    EstrategiaAnalise <|-- AnaliseFrequencia
    EstrategiaAnalise <|-- AnaliseRegressao

    %% Hierarquia: Relatórios
    class GeradorRelatorio {
        <<abstract>>
        +gerar()*
        #coletar_dados()*
        #processar_dados()
        #formatar_saida()*
        #exportar(formato)
    }
    
    class RelatorioTurma {
        -Turma _turma
        +gerar()
        #coletar_dados()
        #formatar_saida()
    }
    
    class RelatorioIndividual {
        -Aluno _aluno
        +gerar()
        #coletar_dados()
        #formatar_saida()
    }
    
    class RelatorioComparativo {
        -List~Turma~ _turmas
        +gerar()
        #coletar_dados()
        #formatar_saida()
    }
    
    GeradorRelatorio <|-- RelatorioTurma
    GeradorRelatorio <|-- RelatorioIndividual
    GeradorRelatorio <|-- RelatorioComparativo

    %% Classes de Domínio
    class Turma {
        -str _codigo
        -str _nome
        -Professor _professor
        -List~Aluno~ _alunos
        +adicionar_aluno(aluno)
        +remover_aluno(aluno)
        +obter_desempenho_geral()
    }
    
    class PlanoAcao {
        -str _id
        -Aluno _aluno_alvo
        -datetime _data_criacao
        -datetime _data_limite
        -List~MaterialEstudo~ _materiais
        -str _observacoes
        -str _status
        +adicionar_material(material)
        +marcar_concluido()
    }
    
    class Avaliacao {
        -str _titulo
        -str _tipo
        -datetime _data
        -float _valor_maximo
        -str _topico
        +validar_nota(nota)
    }
    
    class Nota {
        -Aluno _aluno
        -Avaliacao _avaliacao
        -float _valor
        -datetime _data_registro
        +calcular_percentual()
    }
    
    class Meta {
        -str _id
        -Aluno _aluno
        -str _descricao
        -float _valor_alvo
        -datetime _prazo
        -float _progresso_atual
        +atualizar_progresso()
        +verificar_conclusao()
    }

    %% Factory Pattern
    class MaterialEstudoFactory {
        <<abstract>>
        +criar_material(dados)*
    }
    
    class MaterialPDFFactory {
        +criar_material(dados)
    }
    
    class MaterialVideoFactory {
        +criar_material(dados)
    }
    
    class MaterialLinkFactory {
        +criar_material(dados)
    }
    
    MaterialEstudoFactory <|-- MaterialPDFFactory
    MaterialEstudoFactory <|-- MaterialVideoFactory
    MaterialEstudoFactory <|-- MaterialLinkFactory
    MaterialEstudoFactory ..> MaterialEstudo : cria

    %% Observer Pattern
    class Subject {
        <<interface>>
        +adicionar_observer(observer)
        +remover_observer(observer)
        +notificar_observers()
    }
    
    class Observer {
        <<interface>>
        +atualizar(evento)
    }
    
    class NotificadorEmail {
        +atualizar(evento)
        -enviar_email(destinatario, mensagem)
    }
    
    class NotificadorPush {
        +atualizar(evento)
        -enviar_push(usuario, mensagem)
    }
    
    Subject <|.. Turma
    Subject <|.. PlanoAcao
    Observer <|.. NotificadorEmail
    Observer <|.. NotificadorPush
    Subject o-- Observer

    %% Strategy Pattern
    class AnalisadorDesempenho {
        -EstrategiaAnalise _estrategia
        +definir_estrategia(estrategia)
        +executar_analise(aluno)
        +gerar_sugestoes()
    }
    
    AnalisadorDesempenho o-- EstrategiaAnalise

    %% Relacionamentos principais
    Professor "1" -- "*" Turma : gerencia
    Turma o-- "*" Aluno : contém
    Professor "1" -- "*" PlanoAcao : cria
    PlanoAcao "*" -- "1" Aluno : destinado a
    PlanoAcao *-- "*" MaterialEstudo : contém
    Professor "1" -- "*" MaterialEstudo : publica
    Avaliacao "1" -- "*" Nota : gera
    Aluno "1" -- "*" Nota : possui
    Professor "1" -- "*" Meta : define
    Meta "*" -- "1" Aluno : atribuída a
```

## Hierarquias previstas

1. Hierarquia de Abstração Conceitual: Usuários

    Classe abstrata: `Usuario`
    Subclasses: `Professor`, `Aluno` e `Coordenador`

    Representa o conceito abstrato de "usuário do sistema" com comportamentos comuns (autenticação, perfil) e especializações (professor cria planos, aluno visualiza desempenho, coordenador gera consolidados)
    Método `autenticar()` implementado diferentemente por perfil (professor redireciona para painel de turmas, aluno para dashboard de desempenho).

2. Hierarquia de Variação de Comportamento: Materiais de Estudo

    Classe abstrata: `MaterialEstudo`
    Subclasses: `MaterialPDF`, `MaterialVideo` e `MaterialLink`

    Cada tipo de material tem regras de validação e processamento específicas (PDF valida número de páginas, Vídeo gera thumbnail, Link verifica disponibilidade).
    Método polimórfico `validar_formato()` chamado durante upload independentemente do tipo, com comportamento específico por subclasse.

3. Hierarquia de Estratégia de Análise

    Classe abstrata: `EstrategiaAnalise`
    Subclasses: `AnaliseNotasBaixas`, `AnaliseFrequencia`, `AnaliseRegressao`

    Diferentes critérios para identificar dificuldades permitem personalização de análise pelo professor. Strategy Pattern permite trocar algoritmo em tempo de execução.
    `AnalisadorDesempenho` executa estratégia configurada para gerar sugestões de materiais no Plano de Ação.

4. Hierarquia de Geração de Relatórios

    Classe abstrata: `GeradorRelatorio`
    Subclasses: `RelatorioTurma`, `RelatorioIndividual`, `RelatorioComparativo`

    Todos os relatórios seguem processo comum (coletar -> processar -> formatar -> exportar), mas com variações nas etapas.
    Professor solicita relatório de turma ou individual através da mesma interface mas a coleta e formatação mudam conforme o tipo.

5. Herança Múltipla: Mixin

    Mixins: `AutenticavelMixin`, `NotificavelMixin`
    Classes que utilizam: `Professor`, `Aluno`, `Coordenador`

    Funcionalidades ortogonais (autenticação e notificação) são compartilhadas entre perfis sem duplicação de código.
    Mixins não dependem de `Usuario`, apenas adicionam comportamentos reutilizáveis.

## Padrões de projeto planejados

### Factory Method

Criar diferentes tipos de materiais de estudo sem acoplar código às classes concretas.
Hierarquia de factories que instanciam o tipo correto baseado em metadados do arquivo.

Classes participantes:

- `MaterialEstudoFactory` como abstract factory
- `MaterialPDFFactory`, `MaterialVideoFactory`, `MaterialLinkFactory` como concrete factories
- Hierarquia `MaterialEstudo`

Quando o professor faz upload de arquivo, o sistema detecta a extensão e chama a factory correspondente para criar instância válida.

### Strategy

Variar algoritmo de análise de desempenho sem modificar `AnalisadorDesempenho`.
Encapsular cada critério de análise (notas baixas, frequência, regressão) em classes de estratégia intercambiáveis.

Classes participantes:

- `EstrategiaAnalise` como strategy interface
- `AnaliseNotasBaixas`, `AnaliseFrequencia`, `AnaliseRegressao` como concrete strategies
- `AnalisadorDesempenho` como context

Professor (ou escola) configura critério preferido para identificar dificuldades. Sistema aplica estratégia correspondente ao gerar sugestões de Plano de Ação.

### Observer

Notificar múltiplos componentes quando eventos ocorrerem (nota registrada, material publicado, meta atingida) sem acoplamento forte.
Subjects (Turma, PlanoAcao) mantêm lista de observers (NotificadorEmail, NotificadorPush, AtualizadorRelatorio) e os notificam em eventos.

Classes participantes:

- `Subject` como observable interface
- `Turma`, `PlanoAcao` como concrete subjects
- `NotificadorEmail`, `NotificadorPush`, `AtualizadorRelatorio` como concrete observers

Professor registra nova nota -> Turma notifica observers -> Email enviado ao aluno + Dashboard atualizado + Relatório recalculado.

## Princípios SOLID que serão aplicados

### Single Responsability Principle (SRP)

Aplicação:

- `Aluno`: Apenas dados e comportamentos do aluno (perfil, matrícula, desempenho)
- `AnalisadorDesempenho`: Apenas lógica de análise de dados
- `NotificadorEmail`: Apenas envio de notificação por email
- `PlanoAcao`: Apenas orquestração de materiais para um aluno

Lógica de análise de desempenho não fica em `Aluno`, mas em serviço dedicado `AnalisadorDesempenho`.

### Open/Closed Principle (OCP)

Aplicação:

- Hierarquia `MaterialEstudo`: Sistema aberto para novos tipos de material (MaterialAudio, MaterialQuiz) sem modificar código existente.
- Strategy de Análise: Novas estratégias adicionadas sem alterar `AnalisadorDesempenho`.
- Observer: Novos observers (NotificadorSMS) adicionados sem alterar subjects.

Adicionar MaterialAudio apenas requer criar subclasse de `MaterialEstudo` e factory correspondente. Nenhuma linha de código existente é modificada.

### Liskov Substitution Principle (LSP)

Aplicação:

- Qualquer `MaterialEstudo` (PDF, Vídeo, Link) pode substituir a abstração sem quebrar o sistema.
- `PlanoAcao.adicionar_material(material: MaterialEstudo)` funciona com qualquer subtipo.
- Subclasses mantêm contrato da superclasse (todas implementam `validar_formato()`)

Método que recebe `List[MaterialEstudo]` processa corretamente PDFs, Vídeos e Links.

### Interface Segregation Principle (ISP)

Aplicação:

- `Autenticavel`: `login()`, `logou()`, `validar_credenciais()`
- `Notificavel`: `receber_notificacao()`, `configurar_preferencias()`
- `Relatoravel`: `gerar_relatorio()`, `exportar_dados()`

Classes implementam apenas interfaces necessárias:

- `Aluno`: `Autenticavel + Notificavel`
- `Professor`: `Autenticavel + Notificavel + Relatoravel`
- `Coordenador`: `Autenticavel + Relatoravel`

`Aluno` não é forçado a implementar `gerar_relatorio()` que não usa.
