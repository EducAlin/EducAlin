# Projeto POO - Engenharia de Software - UFCA

**UNIVERSIDADE FEDERAL DO CARIRI - UFCA**  
**PRÓ-REITORIA DE GRADUAÇÃO - PROGRAD**  
**CENTRO DE CIÊNCIA E TECNOLOGIA - CCT**  
**CURSO DE BACHARELADO EM ENGENHARIA DE SOFTWARE**  

## ESPECIFICAÇÃO PROJETO 2

**ES0008 - Programação Orientada a Objetos**  

### Visão Geral

O projeto final tem como objetivo consolidar, de forma prática, os principais conceitos de Programação Orientada a Objetos vistos ao longo da disciplina, culminando em um sistema funcional, bem modelado, testado e documentado.

O projeto final deve resultar em um **sistema orientado a objetos robusto**, extensível e bem projetado, demonstrando domínio conceitual e prático dos principais fundamentos e princípios avançados de POO.

A seguir, são apresentadas as regras gerais do projeto.

#### Linguagem e escopo

- O projeto deve ser desenvolvido em **Python**.  
- Pode ser:  
  - aplicação de linha de comando (CLI),  
  - aplicação simples com interface textual,  
  - ou um pequeno backend (sem necessidade de frontend) usando FastAPI, Flask ou similar  
  - Caso queiram desenvolver interface, ok, mas o foco é em POO. **Interfaces bonitas não ganham mais pontos**.  
- **Não é permitido usar frameworks** que abstraiam completamente a lógica de POO (ex.: Django). Use o SQLAlchemy  com moderação. Herança apenas da classe `Base` não é suficiente.

#### Trabalho em Grupo

- **Grupos de 3 a 5 alunos.**  
- Todos os membros devem contribuir efetivamente:  
  - Commits identificáveis. Coloquem mensagens claras nos commits. Nada de `git commit -m “.”`  
  - contas do github com username identificáveis, por favor. Caso não seja possível identificar o aluno, ele ficará sem nota.  
  - divisão clara de responsabilidades. Isso deve estar detalhado no README.md  
  - apresentação coletiva. Todos devem apresentar! Faltas no dia da apresentação devem ser justificadas seguindo as mesmas regras para solicitação de segunda chamada, conforme regulamento dos cursos de graduação da UFCA.

### Requisitos estruturais obrigatórios

#### 2.1. Escopo e complexidade mínima

O sistema deve:

- representar um **domínio não trivial** (ex.: não apenas CRUD simples),  
- possuir **regras de negócio explícitas**, com decisões e variações de comportamento,  
- justificar a necessidade de um design orientado a objetos (não procedural).

Sistemas “**lineares**” ou com fluxo único serão recusados.

#### 2.2. Modelagem orientada a objetos

- **Mínimo de 12 classes próprias**, sendo:  
  - pelo menos **8 classes de domínio**,  
  - classes auxiliares (serviços, fábricas, controladores) bem justificadas.  
- Cada classe deve:  
  - ter **uma responsabilidade claramente definida**,  
  - evitar “classes Deus” (God Objects),  
  - apresentar **coesão interna alta**.  
  - responsabilidade clara,  
  - atributos encapsulados,  
  - métodos coerentes com sua função.  
  - Docstrings também são items obrigatórios

A proposta deve incluir uma **justificativa textual da modelagem**, não apenas a lista de classes.

#### 2.3. Encapsulamento

- Uso obrigatório de:  
  - atributos privados ou protegidos,  
  - propriedades (`@property`) quando fizer sentido,  
  - validação de dados em setters ou construtores.  
- Acesso direto a atributos deve ser evitado.

### Herança, abstração e polimorfismo

#### 3.1. Hierarquias obrigatórias

O projeto deve conter **no mínimo duas hierarquias distintas**, sendo:

1. **Uma hierarquia de abstração conceitual**  
   - classe abstrata representando um papel ou conceito do domínio;  
   - subclasses especializadas com comportamentos diferentes.  
2. **Uma hierarquia voltada à variação de comportamento**  
   - onde o polimorfismo seja essencial para o funcionamento do sistema.

Cada hierarquia deve ser:

- justificada conceitualmente,  
- demonstrada no fluxo real do sistema.

#### 3.2. Herança múltipla (uso consciente)

- Deve haver **ao menos um uso de herança múltipla**, respeitando:  
  - baixo acoplamento,  
  - ausência de ambiguidade conceitual.

Uma possibilidade aqui é o uso de Mixins.

#### 3.3. Polimorfismo como eixo central

- O sistema deve possuir **pontos polimórficos estratégicos**, por exemplo:  
  - processamento de regras,  
  - execução de ações,  
  - cálculo, validação ou resposta a eventos.  
- O código principal deve depender **de abstrações**, não de classes concretas.

### Composição, agregação e ciclos de vida

#### 4.1. Relações obrigatórias

O projeto deve conter:

- **mínimo de 2 relações de composição**, com ciclo de vida dependente,  
- **mínimo de 2 relações de agregação**, com independência de objetos.

Essas relações devem:

- impactar o comportamento do sistema,  
- não ser apenas ilustrativas.

### Modularização e arquitetura

#### 5.1. Arquitetura em camadas

O projeto deve adotar uma arquitetura clara, como:

- domínio / aplicação / infraestrutura, ou  
- modelos / serviços / interfaces.

Regras:

- Camadas inferiores **não podem depender** das superiores.

Sugestão (quase regra): usar o poetry para gerenciamento de dependências e empacotamento.

### Princípios SOLID e Padrões de projeto

#### 6.1. SOLID

O projeto deve:

- aplicar **no mínimo 4 princípios SOLID**, sendo:  
  - **SRP** e **OCP obrigatórios**,  
  - mais dois à escolha.

com exemplos concretos esperados.

#### 6.2. Padrões de Projeto

O projeto deve empregar **pelo menos dois padrões de projeto**, por exemplo:

- Factory / Abstract Factory,  
- Strategy,  
- Template Method,  
- Observer,  
- State,  
- Decorator.

Regras:

- Padrões devem ser **necessários ao problema**, não decorativos.  
- A proposta deve indicar:  
  - qual problema o padrão resolve,  
  - quais classes participam.

### Testes, qualidade e robustez

#### 7.1. Testes automatizados

- **Mínimo de 12 testes automatizados**, cobrindo:  
  - regras de negócio,  
  - comportamento polimórfico,  
  - exceções e erros esperados.  
- Pelo menos:  
  - 2 testes devem usar **mocks ou stubs simples**.

#### 7.2. Boas práticas

- Código deve seguir:  
  - PEP 8,  
  - nomes expressivos,  
  - documentação mínima (docstrings).  
- Exceções devem ser tratadas de forma explícita.

### Entregas e checkpoints

#### 20/01/2026 – Proposta

Deve conter:

1. Nome da equipe
2. Nomes dos integrantes - Acompanhado do username no GitHub  
3. Descrição detalhada do domínio.  
4. Justificativa da complexidade do sistema.  
5. Diagrama UML (classes e relações).  
6. Hierarquias previstas.

Propostas superficiais **serão devolvidas para revisão**.

---

#### 10/02/2026 – Checkpoint técnico

- Código funcional parcial.  
- Evidências claras de:  
  - abstração,  
  - polimorfismo,  
  - arquitetura em camadas.  
- Discussão crítica do que foi ajustado em relação à proposta inicial.  
- Cada equipe tem 5 minutos para apresentar o que fez até então  
  
---

#### 10/03/2026 e 17/03/2026 – Apresentação final

- Demonstração do sistema.  
- Defesa técnica:  
  - decisões de design,  
  - padrões utilizados,  
  - trade-offs.  
- Apresentação do Código  
- Perguntas técnicas para qualquer membro do grupo.
