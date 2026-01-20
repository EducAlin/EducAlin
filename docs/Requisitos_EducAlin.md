# EducAlin

Documento de Requisitos

| Projeto EducAlin Revisão Nº 3 |
| :---: |

Elaboração omitida para fins práticos

**Registro de Alterações**:

| Versão | Responsável | Data | Alterações |
| :---: | :---: | :---: | :---: |
| 1.0 | Elder Rayan Oliveira Silva | 09/08/2025 | Adicionada a descrição de minimundo |
| 1.1 | Pedro Yan Alcantara Palacio | 17/08/2025 | Adicionadas as regras de negócio baseadas nos requisitos funcionais |
| 1.2 | Lucas Daniel Dias de Sousa | 17/08/2025 | Adicionado o diagrama de Casos de Uso |
| 1.3 | Davi Maia Soares | 06/10/2025 | Atualização dos requisitos funcionais após alguns feedbacks |
| 1.4 | Lucas Daniel Dias de Sousa | 06/10/2025 | Atualização do diagrama de Casos de Uso |
| 1.5 | Lucas Daniel Dias de Sousa | 12/10/2025 | Correção do diagrama de Casos de Uso |
| 2.0 | Análise Técnica | 19/01/2026 | Correções estruturais, padronização terminológica, adição de requisitos de autenticação, reformulação dos Casos de Uso para padrão UML |
| 3.0 | Análise Técnica | 19/01/2026 | Adição dos Casos de Uso pendentes: CU008 (Cadastro), CU009 (Login), CU010 (Recuperar Senha), CU011 (Materiais), CU012 (Metas) |

## Documento de Requisitos

### 1. Introdução

Este documento apresenta os requisitos de usuário do sistema EducAlin e está organizado da seguinte forma: a seção 2 contém uma descrição do propósito do sistema; a seção 3 apresenta uma descrição do minimundo apresentando o problema; a seção 4 apresenta a lista de requisitos de usuário levantados junto ao cliente; a seção 5 apresenta o Modelo de Casos de Uso; a seção 6 apresenta os protótipos de tela do sistema; a seção 7 apresenta o glossário de termos; e a seção 8 apresenta a matriz de rastreabilidade.

### 2. Descrição do Propósito do Sistema

Auxiliar ativamente o professor no acompanhamento individual dos alunos, fornecendo ferramentas para identificar as principais dificuldades de cada um e facilitar o caminho para superá-las, além de simplificar processos exaustivos do dia a dia do professor.

### 3. Descrição do Minimundo

O cenário educacional de base no Brasil enfrenta um desafio significativo: a ausência de um acompanhamento individualizado do aluno. Em um modelo de sala de aula tradicional, os professores encontram dificuldade para identificar e sanar as dificuldades particulares de cada estudante, especialmente a falta de base em conteúdos fundamentais. Essa lacuna resulta em uma queda no desempenho, com alunos progredindo entre os anos escolares sem o domínio de conhecimentos essenciais e gera o que é descrito como uma "relação alienada" entre professor e aluno. A necessidade de dinamizar o ensino, identificar os pontos fracos dos estudantes e intensificar seus resultados é, portanto, evidente.

O sistema EducAlin surge como uma ferramenta tecnológica auxiliar para endereçar este problema. Ele atuará como uma ponte digital que viabiliza uma integração completa entre professor e aluno, focada na perspectiva individual e na ascensão acadêmica do estudante.

O processo central do sistema envolve a criação de perfis individuais para professores e alunos. A partir daí, a plataforma realiza o registro e o rastreamento em tempo real das notas e, principalmente, das dificuldades de cada aluno. Com base nessas informações coletadas, o sistema entrega de forma gradual e dinâmica materiais de estudo e questões personalizadas para as necessidades de cada um.

Ao mesmo tempo, fornece ao professor dados detalhados que permitem um acompanhamento direcionado, seja da turma toda ou de um aluno específico. Isso possibilita que o planejamento de aula seja otimizado, permitindo que o professor atue diretamente nos problemas identificados, como mencionado por uma docente afetada pelo problema, que vê grande diferença no aprendizado quando consegue ter um momento focado com o aluno para corrigir suas falhas.

A ideia central é superar a carência na base educacional através de uma ferramenta que oferece suporte contínuo e dados para uma intervenção pedagógica precisa e individualizada.

### 4. Requisitos de Usuário

Tomando por base o contexto do sistema, foram identificados os seguintes requisitos de usuário:

#### 4.1 User Stories

| Identificador | Descrição | Prioridade | Depende de |
| :---: | :--- | :---: | :---: |
| US01 | Como usuário, eu quero me cadastrar no sistema informando meus dados pessoais e credenciais, para ter acesso às funcionalidades da plataforma. | Alta | Nenhum |
| US02 | Como usuário, eu quero fazer login com e-mail e senha, para acessar minha área personalizada no sistema. | Alta | US01 |
| US03 | Como usuário, eu quero recuperar minha senha via e-mail, para restabelecer o acesso caso a esqueça. | Média | US01 |
| US04 | Como professor, eu quero criar e organizar minhas turmas, para gerenciar meus alunos de forma eficiente. | Alta | US02 |
| US05 | Como professor, eu quero registrar as notas de provas e trabalhos, para ter um histórico completo do desempenho de cada aluno. | Alta | US04 |
| US06 | Como professor, eu quero associar as notas a assuntos específicos da matéria, para que o sistema me mostre quais tópicos são mais difíceis para a turma. | Alta | US04, US05 |
| US07 | Como professor, eu quero gerar um relatório de desempenho da turma, para identificar rapidamente os alunos que precisam de mais atenção e as dificuldades gerais. | Alta | US05, US06 |
| US08 | Como professor, eu quero gerar um gráfico de desempenho individual do aluno ao longo do tempo, para identificar facilmente a evolução dele. | Média | US06 |
| US09 | Como professor, eu quero fazer upload de materiais de estudo (PDFs, vídeos, áudios), para que os alunos possam acessá-los 24 horas por dia, 7 dias por semana. | Média | US04 |
| US10 | Como professor, eu quero enviar mensagens privadas para um aluno, para poder discutir assuntos pessoais sobre o desempenho dele. | Alta | US04 |
| US11 | Como aluno, eu quero postar dúvidas sobre um tópico no fórum da turma, para que o professor e meus colegas possam me ajudar e eu entenda a matéria. | Média | US04 |
| US12 | Como professor, eu quero sugerir materiais de reforço personalizados para um aluno com base nos tópicos com desempenho inferior a 60% nas últimas 3 avaliações, para ajudá-lo a superar os desafios. | Alta | US05, US08, US09 |
| US13 | Como professor, eu quero definir metas de aprendizado para os alunos, para motivá-los e monitorar o progresso individual. | Baixa | US05 |
| US14 | Como aluno, eu quero poder ver meu desempenho nas diversas matérias por meio de um relatório geral, para ter um controle sobre meu rendimento escolar. | Média | US05 |
| US15 | Como aluno, eu quero poder visualizar os meus pontos fracos em cada matéria, para saber onde preciso melhorar. | Média | US06 |
| US16 | Como aluno, eu quero poder visualizar e interagir com os materiais selecionados e enviados pelo professor. | Média | US12 |
| US17 | Como aluno, eu quero poder mandar mensagens para o professor, para eventuais dúvidas ou observações. | Baixa | US02 |
| US18 | Como coordenador, eu quero visualizar relatórios consolidados de todas as turmas, para acompanhar o desempenho geral da escola. | Alta | US07 |
| US19 | Como coordenador, eu quero gerar relatórios comparativos entre turmas, para identificar padrões e boas práticas. | Média | US07, US18 |

#### 4.2 Regras de Negócio

| Identificador | Descrição | Prioridade | Requisitos Relacionados |
| :---: | :--- | :---: | :---: |
| RN01 | O sistema deve validar o CPF ou RG do usuário no momento do cadastro, verificando formato e dígitos verificadores. | Média | US01 |
| RN02 | O sistema deve restringir o acesso a uma única sessão ativa por usuário, encerrando sessões anteriores ao detectar novo login. | Alta | US02 |
| RN03 | O sistema deve gerar relatórios de desempenho acessíveis apenas para usuários com perfil de professor ou coordenador. | Alta | US06, US07, US08 |
| RN04 | O sistema deve suportar upload e download de arquivos nos formatos: PDF, DOC, DOCX, MP4, MP3, PNG, JPG, com tamanho máximo de 50MB por arquivo. | Média | US09, US11, US12 |
| RN05 | O sistema deve possuir criptografia ativa (TLS 1.3 ou superior) para todas as comunicações em chats de sala de aula e mensagens particulares. | Alta | US10, US17 |
| RN06 | O professor cadastrado deve possuir acesso a uma tela de personalização para cada turma, permitindo configurar cores, ícones e organização de conteúdos. | Média | US04, US05, US13 |

#### 4.3 Requisitos Não Funcionais

| Identificador | Descrição | Categoria | Prioridade | Requisitos Relacionados |
| :---: | :--- | :---: | :---: | :---: |
| RNF01 | O sistema deve garantir que usuários acessem apenas funcionalidades compatíveis com seu perfil (professor, aluno, coordenador), negando acesso a áreas restritas e gerando logs de tentativas de acesso não autorizado. | Segurança | Alta | US01, US10, RN02 |
| RNF02 | O sistema deve validar todos os dados de entrada antes do armazenamento (login, cadastro, anexos), rejeitando dados inválidos e exibindo mensagens de erro apropriadas. | Segurança | Alta | RN01 |
| RNF03 | O sistema deve possuir criptografia ativa para todas as comunicações em chats de sala de aula e mensagens particulares, garantindo a privacidade das conversas. | Segurança | Alta | US10, US11, RN05 |
| RNF04 | O sistema deve estar em conformidade com a Lei Geral de Proteção de Dados (LGPD), garantindo a proteção dos dados pessoais de alunos e professores, com auditoria confirmando a conformidade. | Segurança | Alta | US01, US05 |
| RNF05 | O sistema deve permitir que usuários acessem as principais funcionalidades (Planos de Ação, relatórios, materiais) em até 3 cliques a partir do painel principal. | Usabilidade | Alta | Nenhum |
| RNF06 | O sistema deve fornecer menus e rótulos claros, organizados e compreensíveis para todos os perfis de usuários (professor, aluno, administrador) sem necessidade de treinamento prévio. | Usabilidade | Alta | Nenhum |
| RNF07 | O sistema deve permitir que pelo menos 85% dos usuários concluam as tarefas principais (criar Plano de Ação, registrar notas, acessar relatórios) em até 2 minutos durante testes de usabilidade. | Usabilidade | Média | RNF05 |
| RNF08 | O sistema deve fornecer uma interface intuitiva com menus claros, organização lógica e telas consistentes em todas as seções (painel principal, relatórios, Planos de Ação), com taxa de sucesso de tarefas ≥90%. | Usabilidade | Média | RNF05, RNF06 |
| RNF09 | O sistema deve garantir tempo de resposta inferior a 2 segundos nas operações mais frequentes (login, abertura de planos, acesso a relatórios) com até 1000 usuários simultâneos, confirmado em testes de carga. | Desempenho | Alta | RNF07 |
| RNF10 | O sistema deve suportar até 10 mil consultas por hora (relatórios, acessos a conteúdos) sem degradação de desempenho, confirmado em testes de carga. | Desempenho | Média | US05, US06, US07 |
| RNF11 | O sistema deve estar disponível pelo menos 99% do tempo, permitindo apenas 7,2 horas de indisponibilidade por mês para manutenções programadas. | Desempenho | Alta | Nenhum |
| RNF12 | O sistema deve garantir operação contínua mesmo com falhas ocasionais, retomando a operação sem perda de dados de alunos, professores ou conteúdos. | Confiabilidade | Alta | US05, US09 |
| RNF13 | O sistema deve realizar backups automáticos diários de todos os dados (relatórios, Planos de Ação, notas), com perda máxima de 24 horas em caso de falha catastrófica. | Confiabilidade | Alta | US05, US06 |
| RNF14 | O sistema deve fornecer documentação completa e atualizada para administradores, professores e alunos, garantindo a operação correta de todos os perfis de usuário. | Manutenibilidade | Baixa | Nenhum |
| RNF15 | O sistema deve registrar logs de operações críticas (login, criação de plano, envio de conteúdo, acesso a dados sensíveis), mantendo os logs disponíveis por pelo menos 6 meses. | Manutenibilidade | Baixa | RNF01 |
| RNF16 | O sistema deve funcionar corretamente nos navegadores Chrome (versão 90+), Edge (versão 90+) e Firefox (versão 88+), confirmado por testes de compatibilidade. | Portabilidade | Média | Nenhum |
| RNF17 | O sistema deve permitir que o processo de instalação e configuração inicial seja concluído em até 10 minutos, incluindo a criação do primeiro usuário administrador. | Portabilidade | Baixa | Nenhum |
| RNF18 | O sistema deve permitir integração com sistemas legados através de API REST, garantindo troca de dados correta e segura com autenticação via tokens. | Interoperabilidade | Média | Nenhum |
| RNF19 | O sistema deve permitir a exportação de relatórios e painéis em formatos PDF e Excel, gerando arquivos completos e corretos com todos os dados visualizados. | Interoperabilidade | Baixa | US07, US08, US14 |
| RNF20 | O sistema deve ser escalável para suportar crescimento de até 500% no número de usuários, turmas e conteúdos sem degradação de desempenho, confirmado em testes de escalabilidade. | Adequação | Média | Nenhum |
| RNF21 | O sistema deve permitir a customização de cores, logos e layout da interface (branding da escola) sem impacto negativo nas funcionalidades do sistema. | Adequação | Baixa | US04, RN06 |
| RNF22 | O sistema deve utilizar apenas bibliotecas e componentes de software compatíveis com normas de compliance e licenciamento, confirmado por auditoria de código. | Adequação | Baixa | Nenhum |

### 5. Modelo de Casos de Uso

O Modelo de Casos de Uso visa capturar e descrever as funcionalidades que um sistema deve prover para os atores que interagem com o mesmo. Os atores identificados no contexto deste projeto estão descritos na tabela a seguir.

**Tabela 1 – Atores do Sistema**  

| Ator | Descrição |
| :--- | :--- |
| **Usuário Não Autenticado** | Pessoa que ainda não possui conta ou não está logada no sistema, podendo realizar cadastro ou login. |
| **Professor** | Usuário principal do sistema, responsável por cadastrar turmas, registrar notas, criar Planos de Ação personalizados e acompanhar o desempenho dos alunos. |
| **Aluno** | Usuário que acessa a plataforma para visualizar seu desempenho, acessar materiais de estudo, interagir com o fórum e receber Planos de Ação personalizados. |
| **Coordenador** | Usuário com acesso a relatórios consolidados de múltiplas turmas e visão geral do desempenho institucional. |
| **Administrador** | Usuário responsável pela configuração inicial do sistema, gestão de usuários e manutenção técnica. |

A seguir, são apresentados os diagramas de Casos de Uso e descrições associadas, organizados por subsistema.

#### 5.1 Diagrama de Casos de Uso

A Figura 1 apresenta o diagrama de Casos de Uso do subsistema *Plano de Ação*.

![Figura 1 – Diagrama de Casos de Uso do Subsistema Plano de Ação.](EducAlin_Docs_Fig2.jpg)

[Diagrama de Casos de Uso (PDF)](https://drive.google.com/file/d/1NeBFM0KQ1kzlxru9ZKEwABRgF6SqJNvM/view?usp=drive_link)

#### 5.2 Descrições dos Casos de Uso

A seguir, são apresentadas as descrições dos Casos de Uso segundo o padrão UML de descrição completa.

---

##### CU001 – Criar Plano de Ação Personalizado

**Subsistema:** Acompanhamento Individualizado  
**Versão:** 2.0  
**Última Atualização:** 19/01/2026  
**Prioridade:** Alta

---

###### Descrição

Este Caso de Uso descreve o processo pelo qual um professor cria um Plano de Ação personalizado para um aluno específico, com base nas dificuldades identificadas pelo sistema, visando melhorar o desempenho acadêmico do estudante.

---

###### Atores

| Tipo | Ator | Descrição |
| :---: | :--- | :--- |
| Principal | Professor | Usuário autenticado com perfil de professor que executa o Caso de Uso |
| Secundário | Sistema de Análise | Módulo interno responsável por identificar dificuldades e sugerir conteúdos |
| Secundário | Aluno | Receptor do Plano de Ação (notificado ao final do processo) |

---

###### Pré-condições

| ID | Descrição |
| :---: | :--- |
| PRE-01 | Professor está autenticado no sistema com sessão válida |
| PRE-02 | Existe pelo menos uma turma cadastrada pelo professor |
| PRE-03 | A turma selecionada possui pelo menos um aluno cadastrado |
| PRE-04 | Existem dados de avaliação suficientes para análise (mínimo de 2 avaliações registradas) |

---

###### Pós-condições

| ID | Descrição |
| :---: | :--- |
| POS-01 | Plano de Ação foi salvo no sistema com status "Rascunho" ou "Enviado" |
| POS-02 | Se status = "Enviado": aluno recebeu notificação com link para o Plano de Ação |
| POS-03 | Registro de auditoria foi criado contendo: professor, aluno, data/hora, status, conteúdos incluídos |
| POS-04 | Plano de Ação está disponível para edição futura pelo professor |

---

###### Fluxo Principal

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1 | Professor | Acessa o menu "Minhas Turmas" no painel principal |
| 2 | Sistema | Exibe lista de turmas cadastradas pelo professor, ordenadas por data de criação |
| 3 | Professor | Seleciona uma turma da lista |
| 4 | Sistema | Exibe lista de alunos da turma com indicadores visuais de desempenho (verde/amarelo/vermelho) |
| 5 | Professor | Seleciona um aluno da lista |
| 6 | Sistema | Exibe painel individual do aluno contendo: gráfico de evolução temporal, pontos fortes (tópicos ≥70%), pontos de atenção (tópicos <60%), histórico de Planos de Ação anteriores |
| 7 | Professor | Clica no botão "Criar Plano de Ação" |
| 8 | Sistema | Exibe formulário de criação com: sugestões automáticas de conteúdos baseadas nas dificuldades, campo para seleção de foco/objetivo, área para upload de materiais (máximo 50MB por arquivo), campo para observações do professor |
| 9 | Professor | Configura o Plano de Ação: seleciona/desseleciona sugestões do sistema, define foco do plano, opcionalmente anexa materiais próprios, adiciona observações |
| 10 | Professor | Clica em "Salvar como Rascunho" ou "Enviar para Aluno" |
| 11 | Sistema | Valida os dados do Plano de Ação (verifica se há pelo menos 1 conteúdo) |
| 12 | Sistema | Salva o Plano de Ação com status correspondente à ação escolhida |
| 13 | Sistema | Exibe mensagem de confirmação: "Plano de Ação [salvo como rascunho/enviado] com sucesso!" |
| 14 | Sistema | Se opção "Enviar" foi selecionada: dispara notificação por e-mail e push para o aluno |

---

###### Fluxos Alternativos

**FA01 – Nenhuma turma cadastrada** *(extensão do passo 2)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 2a | Sistema | Detecta que não há turmas cadastradas para o professor |
| 2b | Sistema | Exibe mensagem: "Você ainda não possui turmas cadastradas" |
| 2c | Sistema | Exibe botão "Criar Nova Turma" em destaque |
| 2d | Professor | Clica em "Criar Nova Turma" |
| 2e | Sistema | Redireciona para CU002 – Gerenciar Turmas |

**FA02 – Nenhum aluno na turma** *(extensão do passo 4)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 4a | Sistema | Detecta que a turma selecionada não possui alunos cadastrados |
| 4b | Sistema | Exibe mensagem: "Esta turma não possui alunos cadastrados" |
| 4c | Sistema | Exibe opção "Adicionar Alunos" |
| 4d | Professor | Clica em "Adicionar Alunos" |
| 4e | Sistema | Exibe formulário de cadastro de alunos na turma |

**FA03 – Dados insuficientes para análise** *(extensão do passo 6)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 6a | Sistema | Detecta dados insuficientes (menos de 2 avaliações registradas) |
| 6b | Sistema | Exibe painel parcial com aviso: "Dados insuficientes para análise completa. Registre mais avaliações para obter sugestões personalizadas." |
| 6c | Sistema | Desabilita seção "Sugestões Automáticas" no formulário de criação |
| 6d | Professor | Pode continuar criando Plano de Ação manualmente (prossegue para passo 7) |

**FA04 – Editar Plano de Ação existente** *(extensão do passo 6)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 6e | Professor | Visualiza lista de Planos de Ação anteriores e clica em "Editar" em um plano com status "Rascunho" |
| 6f | Sistema | Carrega dados do Plano de Ação existente no formulário de edição |
| 6g | - | Fluxo continua a partir do passo 9 |

---

###### Fluxos de Exceção

**FE01 – Arquivo com formato não suportado** *(exceção do passo 9)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 9a | Professor | Tenta anexar arquivo com extensão não suportada |
| 9b | Sistema | Bloqueia o upload e não adiciona o arquivo |
| 9c | Sistema | Exibe mensagem de erro: "Formato de arquivo não suportado. Formatos aceitos: PDF, DOC, DOCX, MP4, MP3, PNG, JPG" (conforme RN04) |
| 9d | Professor | Pode tentar novamente com outro arquivo ou prosseguir sem anexo |

**FE02 – Tamanho de arquivo excedido** *(exceção do passo 9)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 9e | Professor | Tenta anexar arquivo com tamanho superior a 50MB |
| 9f | Sistema | Bloqueia o upload |
| 9g | Sistema | Exibe mensagem de erro: "Arquivo excede o tamanho máximo permitido (50MB). Reduza o tamanho do arquivo ou divida em partes menores." |

**FE03 – Plano de Ação sem conteúdo** *(exceção do passo 11)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 11a | Sistema | Detecta que nenhum conteúdo foi adicionado ao Plano de Ação |
| 11b | Sistema | Mantém botão "Enviar para Aluno" desabilitado |
| 11c | Sistema | Exibe mensagem informativa: "Adicione pelo menos 1 conteúdo ou arquivo para enviar o Plano de Ação" |
| 11d | Professor | Adiciona conteúdo e tenta novamente |

**FE04 – Falha de conexão ao salvar** *(exceção do passo 12)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 12a | Sistema | Detecta falha de conexão durante o processo de salvamento |
| 12b | Sistema | Salva dados localmente no navegador (cache temporário) |
| 12c | Sistema | Exibe mensagem: "Conexão instável. Seus dados foram salvos localmente e serão sincronizados automaticamente quando a conexão for restabelecida." |
| 12d | Sistema | Quando conexão é restabelecida, sincroniza dados com o servidor |

---

###### Requisitos Especiais

| ID | Descrição |
| :---: | :--- |
| RE01 | O tempo de carregamento do painel individual do aluno deve ser inferior a 2 segundos (conforme RNF09) |
| RE02 | Arquivos anexados devem ser verificados por antivírus antes do armazenamento permanente |
| RE03 | Interface deve seguir padrões de acessibilidade WCAG 2.1 nível AA |
| RE04 | Dados do formulário devem ser salvos automaticamente a cada 30 segundos para evitar perda de informações |

---

###### Regras de Negócio Aplicáveis

| ID | Descrição |
| :---: | :--- |
| RN03 | Relatórios de desempenho acessíveis apenas para usuários com perfil de professor ou coordenador |
| RN04 | Sistema deve suportar upload de arquivos nos formatos: PDF, DOC, DOCX, MP4, MP3, PNG, JPG (máximo 50MB) |
| RN06 | Professor deve possuir acesso a tela de personalização para cada turma |

---

###### User Stories Relacionadas

| ID | Descrição |
| :---: | :--- |
| US12 | Sugerir materiais de reforço personalizados para um aluno |
| US05 | Registrar notas de provas e trabalhos |
| US08 | Gerar gráfico de desempenho individual |
| US09 | Fazer upload de materiais de estudo |

---

##### CU002 – Gerenciar Turmas

**Subsistema:** Gestão Acadêmica  
**Versão:** 1.0  
**Última Atualização:** 19/01/2026  
**Prioridade:** Alta

---

###### Descrição

Este Caso de Uso descreve o processo pelo qual um professor cria, edita e exclui turmas no sistema, bem como adiciona ou remove alunos das turmas.

---

###### Atores

| Tipo | Ator | Descrição |
| :---: | :--- | :--- |
| Principal | Professor | Usuário autenticado com perfil de professor que gerencia suas turmas |
| Secundário | Aluno | Usuário que será vinculado às turmas |

---

###### Pré-condições

| ID | Descrição |
| :---: | :--- |
| PRE-01 | Professor está autenticado no sistema com sessão válida |

---

###### Pós-condições

| ID | Descrição |
| :---: | :--- |
| POS-01 | Turma foi criada/editada/excluída conforme ação realizada |
| POS-02 | Alunos foram vinculados/desvinculados da turma conforme ações realizadas |
| POS-03 | Registro de auditoria foi criado com as alterações realizadas |

---

###### Fluxo Principal (Criar Turma)

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1 | Professor | Acessa o menu "Gerenciar Turmas" no painel principal |
| 2 | Sistema | Exibe lista de turmas existentes e botão "Nova Turma" |
| 3 | Professor | Clica em "Nova Turma" |
| 4 | Sistema | Exibe formulário de criação com campos: Nome da Turma, Disciplina, Ano/Série, Período, Descrição (opcional) |
| 5 | Professor | Preenche os dados obrigatórios e clica em "Criar Turma" |
| 6 | Sistema | Valida os dados e cria a turma |
| 7 | Sistema | Exibe mensagem: "Turma criada com sucesso!" e opção "Adicionar Alunos" |
| 8 | Professor | Opcionalmente, clica em "Adicionar Alunos" para vincular alunos à turma |
| 9 | Sistema | Exibe lista de alunos cadastrados no sistema para seleção |
| 10 | Professor | Seleciona os alunos desejados e confirma |
| 11 | Sistema | Vincula os alunos à turma e exibe confirmação |

---

###### Fluxos Alternativos

**FA01 – Editar Turma**  

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 3a | Professor | Clica em "Editar" em uma turma existente |
| 3b | Sistema | Carrega dados da turma no formulário de edição |
| 3c | Professor | Altera os campos desejados e clica em "Salvar Alterações" |
| 3d | Sistema | Valida e salva as alterações, exibindo confirmação |

**FA02 – Excluir Turma**  

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 3e | Professor | Clica em "Excluir" em uma turma existente |
| 3f | Sistema | Exibe modal de confirmação: "Deseja realmente excluir esta turma? Esta ação não poderá ser desfeita." |
| 3g | Professor | Confirma a exclusão |
| 3h | Sistema | Exclui a turma (os dados de alunos são mantidos, apenas o vínculo é removido) |

---

###### Fluxos de Exceção

**FE01 – Nome de turma duplicado**  

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 6a | Sistema | Detecta que já existe uma turma com o mesmo nome para o professor |
| 6b | Sistema | Exibe mensagem: "Já existe uma turma com este nome. Escolha outro nome." |

---

###### User Stories Relacionadas

| ID | Descrição |
| :---: | :--- |
| US04 | Criar e organizar turmas |

---

##### CU003 – Registrar Notas

**Subsistema:** Gestão Acadêmica  
**Versão:** 1.0  
**Última Atualização:** 19/01/2026  
**Prioridade:** Alta

---

###### Descrição

Este Caso de Uso descreve o processo pelo qual um professor registra as notas de provas, trabalhos e outras avaliações para os alunos de suas turmas.

---

###### Atores

| Tipo | Ator | Descrição |
| :---: | :--- | :--- |
| Principal | Professor | Usuário autenticado que registra as notas |

---

###### Pré-condições

| ID | Descrição |
| :---: | :--- |
| PRE-01 | Professor está autenticado no sistema |
| PRE-02 | Existe pelo menos uma turma cadastrada com alunos vinculados |

---

###### Pós-condições

| ID | Descrição |
| :---: | :--- |
| POS-01 | Notas foram registradas no sistema para os alunos selecionados |
| POS-02 | Sistema de análise atualizou os indicadores de desempenho |
| POS-03 | Alunos receberam notificação sobre nova nota registrada (se configurado) |

---

###### Fluxo Principal

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1 | Professor | Acessa o menu "Registrar Notas" no painel principal |
| 2 | Sistema | Exibe lista de turmas do professor |
| 3 | Professor | Seleciona uma turma |
| 4 | Sistema | Exibe lista de alunos da turma e opções de avaliação |
| 5 | Professor | Clica em "Nova Avaliação" |
| 6 | Sistema | Exibe formulário com campos: Tipo (Prova/Trabalho/Participação), Título, Data, Valor Máximo, Tópicos Associados |
| 7 | Professor | Preenche os dados da avaliação e clica em "Continuar" |
| 8 | Sistema | Exibe grade para lançamento de notas com lista de alunos |
| 9 | Professor | Insere a nota de cada aluno (ou marca como "Faltou"/"Pendente") |
| 10 | Professor | Clica em "Salvar Notas" |
| 11 | Sistema | Valida as notas (verificando se estão dentro do valor máximo) |
| 12 | Sistema | Salva as notas e atualiza os indicadores de desempenho |
| 13 | Sistema | Exibe confirmação: "Notas registradas com sucesso!" |

---

###### Fluxos Alternativos

**FA01 – Importar notas de planilha**  

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 5a | Professor | Clica em "Importar Notas" |
| 5b | Sistema | Exibe opção de upload de arquivo Excel/CSV |
| 5c | Professor | Faz upload do arquivo com as notas |
| 5d | Sistema | Processa o arquivo e exibe prévia das notas para confirmação |
| 5e | Professor | Confirma a importação |
| 5f | Sistema | Salva as notas e continua no passo 12 |

---

###### Fluxos de Exceção

**FE01 – Nota acima do valor máximo**  

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 11a | Sistema | Detecta nota com valor acima do máximo definido |
| 11b | Sistema | Destaca o campo em vermelho e exibe: "Nota acima do valor máximo permitido ([valor])" |
| 11c | Professor | Corrige o valor e tenta salvar novamente |

---

###### User Stories Relacionadas

| ID | Descrição |
| :---: | :--- |
| US05 | Registrar notas de provas e trabalhos |
| US06 | Associar notas a assuntos específicos |

---

##### CU004 – Gerar Relatório de Desempenho

**Subsistema:** Análise e Relatórios  
**Versão:** 1.0  
**Última Atualização:** 19/01/2026  
**Prioridade:** Alta

---

###### Descrição

Este Caso de Uso descreve o processo pelo qual um professor ou coordenador gera relatórios de desempenho de turmas ou alunos individuais.

---

###### Atores

| Tipo | Ator | Descrição |
| :---: | :--- | :--- |
| Principal | Professor | Gera relatórios de suas próprias turmas |
| Principal | Coordenador | Gera relatórios consolidados de múltiplas turmas |

---

###### Pré-condições

| ID | Descrição |
| :---: | :--- |
| PRE-01 | Usuário está autenticado com perfil de professor ou coordenador |
| PRE-02 | Existem dados de avaliação registrados para análise |

---

###### Pós-condições

| ID | Descrição |
| :---: | :--- |
| POS-01 | Relatório foi gerado e exibido na tela |
| POS-02 | Opcionalmente, relatório foi exportado em PDF ou Excel |

---

###### Fluxo Principal

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1 | Usuário | Acessa o menu "Relatórios" no painel principal |
| 2 | Sistema | Exibe opções de relatório: Por Turma, Por Aluno, Comparativo, Consolidado (apenas coordenador) |
| 3 | Usuário | Seleciona o tipo de relatório desejado |
| 4 | Sistema | Exibe filtros disponíveis: Período, Turma(s), Disciplina, Tópicos |
| 5 | Usuário | Configura os filtros desejados e clica em "Gerar Relatório" |
| 6 | Sistema | Processa os dados e gera o relatório |
| 7 | Sistema | Exibe relatório com gráficos, tabelas e indicadores |
| 8 | Usuário | Opcionalmente, clica em "Exportar" para salvar em PDF ou Excel |
| 9 | Sistema | Gera o arquivo no formato selecionado e inicia o download |

---

###### User Stories Relacionadas

| ID | Descrição |
| :---: | :--- |
| US07 | Gerar relatório de desempenho da turma |
| US08 | Gerar gráfico de desempenho individual |
| US14 | Visualizar desempenho nas diversas matérias (aluno) |
| US18 | Visualizar relatórios consolidados (coordenador) |
| US19 | Gerar relatórios comparativos entre turmas |

---

##### CU005 – Enviar Mensagem Privada

**Subsistema:** Comunicação  
**Versão:** 1.0  
**Última Atualização:** 19/01/2026  
**Prioridade:** Alta

---

###### Descrição

Este Caso de Uso descreve o processo de envio de mensagens privadas entre professores e alunos para comunicação individualizada sobre desempenho acadêmico.

---

###### Atores

| Tipo | Ator | Descrição |
| :---: | :--- | :--- |
| Principal | Professor | Envia mensagens para seus alunos |
| Principal | Aluno | Envia mensagens para seus professores |

---

###### Pré-condições

| ID | Descrição |
| :---: | :--- |
| PRE-01 | Usuário está autenticado no sistema |
| PRE-02 | Existe vínculo entre professor e aluno (aluno está em turma do professor) |

---

###### Pós-condições

| ID | Descrição |
| :---: | :--- |
| POS-01 | Mensagem foi enviada e armazenada com criptografia |
| POS-02 | Destinatário recebeu notificação de nova mensagem |

---

###### Fluxo Principal

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1 | Usuário | Acessa o menu "Mensagens" no painel principal |
| 2 | Sistema | Exibe lista de conversas existentes e botão "Nova Mensagem" |
| 3 | Usuário | Clica em uma conversa existente ou em "Nova Mensagem" |
| 4 | Sistema | Se nova mensagem: exibe lista de destinatários disponíveis |
| 5 | Usuário | Seleciona o destinatário (se nova mensagem) |
| 6 | Sistema | Exibe interface de chat com histórico de mensagens |
| 7 | Usuário | Digita a mensagem no campo de texto |
| 8 | Usuário | Opcionalmente, anexa arquivo (conforme RN04) |
| 9 | Usuário | Clica em "Enviar" |
| 10 | Sistema | Criptografa e armazena a mensagem (conforme RN05) |
| 11 | Sistema | Notifica o destinatário sobre a nova mensagem |

---

###### Requisitos Especiais

| ID | Descrição |
| :---: | :--- |
| RE01 | Todas as mensagens devem ser criptografadas end-to-end (conforme RN05 e RNF03) |
| RE02 | Mensagens devem ser armazenadas por período mínimo definido pela instituição |

---

###### User Stories Relacionadas

| ID | Descrição |
| :---: | :--- |
| US10 | Enviar mensagens privadas para um aluno (professor) |
| US17 | Mandar mensagens para o professor (aluno) |

---

##### CU006 – Gerenciar Fórum de Dúvidas

**Subsistema:** Comunicação  
**Versão:** 1.0  
**Última Atualização:** 19/01/2026  
**Prioridade:** Média

---

###### Descrição

Este Caso de Uso descreve a interação de professores e alunos com o fórum de dúvidas da turma, incluindo criação de tópicos, respostas e moderação.

---

###### Atores

| Tipo | Ator | Descrição |
| :---: | :--- | :--- |
| Principal | Aluno | Posta dúvidas e responde a colegas |
| Principal | Professor | Responde dúvidas e modera o fórum |

---

###### Pré-condições

| ID | Descrição |
| :---: | :--- |
| PRE-01 | Usuário está autenticado no sistema |
| PRE-02 | Usuário está vinculado à turma do fórum |

---

###### Pós-condições

| ID | Descrição |
| :---: | :--- |
| POS-01 | Tópico/resposta foi publicado no fórum |
| POS-02 | Participantes da turma foram notificados (conforme configurações) |

---

###### Fluxo Principal (Postar Dúvida)

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1 | Aluno | Acessa o fórum da turma pelo menu "Turmas" → turma desejada → "Fórum" |
| 2 | Sistema | Exibe lista de tópicos existentes e botão "Nova Dúvida" |
| 3 | Aluno | Clica em "Nova Dúvida" |
| 4 | Sistema | Exibe formulário com campos: Título, Tópico/Matéria Relacionada, Descrição da Dúvida, Anexos (opcional) |
| 5 | Aluno | Preenche os campos e clica em "Publicar" |
| 6 | Sistema | Valida o conteúdo e publica a dúvida |
| 7 | Sistema | Notifica professor e colegas da turma |

---

###### Fluxos Alternativos

**FA01 – Responder a uma dúvida**  

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 3a | Usuário | Clica em um tópico existente |
| 3b | Sistema | Exibe o tópico com todas as respostas |
| 3c | Usuário | Digita resposta no campo de texto e clica em "Responder" |
| 3d | Sistema | Publica a resposta e notifica o autor do tópico |

**FA02 – Marcar resposta como solução (Professor)**  

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 3e | Professor | Clica em "Marcar como Solução" em uma resposta |
| 3f | Sistema | Destaca a resposta como solução oficial e encerra o tópico |

---

###### User Stories Relacionadas

| ID | Descrição |
| :---: | :--- |
| US11 | Postar dúvidas sobre um tópico no fórum |

---

##### CU007 – Visualizar Desempenho Individual (Aluno)

**Subsistema:** Acompanhamento do Aluno  
**Versão:** 1.0  
**Última Atualização:** 19/01/2026  
**Prioridade:** Média

---

###### Descrição

Este Caso de Uso descreve como o aluno visualiza seu próprio desempenho acadêmico, incluindo notas, pontos fortes, pontos de atenção e evolução ao longo do tempo.

---

###### Atores

| Tipo | Ator | Descrição |
| :---: | :--- | :--- |
| Principal | Aluno | Visualiza seu próprio desempenho |

---

###### Pré-condições

| ID | Descrição |
| :---: | :--- |
| PRE-01 | Aluno está autenticado no sistema |
| PRE-02 | Aluno está vinculado a pelo menos uma turma |
| PRE-03 | Existem notas registradas para o aluno |

---

###### Pós-condições

| ID | Descrição |
| :---: | :--- |
| POS-01 | Aluno visualizou seus dados de desempenho |

---

###### Fluxo Principal

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1 | Aluno | Acessa o menu "Meu Desempenho" no painel principal |
| 2 | Sistema | Exibe visão geral com: média geral, gráfico de evolução, cards por disciplina |
| 3 | Aluno | Opcionalmente, seleciona uma disciplina para detalhamento |
| 4 | Sistema | Exibe detalhes da disciplina: todas as notas, tópicos com bom desempenho (≥70%), tópicos que precisam de atenção (<60%), materiais recomendados |
| 5 | Aluno | Opcionalmente, clica em "Ver Planos de Ação" |
| 6 | Sistema | Exibe lista de Planos de Ação enviados pelos professores |
| 7 | Aluno | Seleciona um Plano de Ação para visualizar detalhes e acessar materiais |

---

###### User Stories Relacionadas

| ID | Descrição |
| :---: | :--- |
| US14 | Ver desempenho nas diversas matérias por meio de relatório geral |
| US15 | Visualizar pontos fracos em cada matéria |
| US16 | Visualizar e interagir com materiais enviados pelo professor |

---

##### CU008 – Cadastrar Usuário

**Subsistema:** Autenticação e Controle de Acesso  
**Versão:** 1.0  
**Última Atualização:** 19/01/2026  
**Prioridade:** Alta

---

###### Descrição

Este Caso de Uso descreve o processo pelo qual um novo usuário (Professor, Aluno ou Coordenador) realiza seu cadastro no sistema EducAlin, fornecendo suas informações pessoais e credenciais de acesso.

---

###### Atores

| Tipo | Ator | Descrição |
| :---: | :--- | :--- |
| Principal | Usuário Não Autenticado | Pessoa que deseja se cadastrar no sistema |
| Secundário | Sistema de Validação | Módulo interno responsável por validar CPF/RG e verificar duplicidades |
| Secundário | Serviço de E-mail | Sistema externo responsável pelo envio de e-mail de confirmação |

---

###### Pré-condições

| ID | Descrição |
| :---: | :--- |
| PRE-01 | Usuário possui acesso à internet e navegador compatível (Chrome 90+, Edge 90+, Firefox 88+) |
| PRE-02 | Usuário não possui cadastro prévio no sistema com o mesmo CPF/RG ou e-mail |
| PRE-03 | Sistema de e-mail está operacional para envio de confirmação |

---

###### Pós-condições

| ID | Descrição |
| :---: | :--- |
| POS-01 | Novo usuário foi criado no sistema com status "Pendente de Confirmação" |
| POS-02 | E-mail de confirmação foi enviado para o endereço informado |
| POS-03 | Registro de auditoria foi criado com dados do cadastro (data/hora, IP, dados informados) |
| POS-04 | Após confirmação do e-mail, status alterado para "Ativo" |

---

###### Fluxo Principal

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1 | Usuário | Acessa a página inicial do sistema EducAlin |
| 2 | Sistema | Exibe página de boas-vindas com opções "Entrar" e "Cadastrar-se" |
| 3 | Usuário | Clica em "Cadastrar-se" |
| 4 | Sistema | Exibe formulário de cadastro com campos: Tipo de Perfil (Professor/Aluno/Coordenador), Nome Completo, CPF ou RG, E-mail, Telefone (opcional), Data de Nascimento, Senha, Confirmação de Senha |
| 5 | Usuário | Seleciona o tipo de perfil desejado |
| 6 | Sistema | Adapta o formulário conforme o perfil selecionado (campos adicionais específicos) |
| 7 | Usuário | Preenche todos os campos obrigatórios |
| 8 | Sistema | Valida o formato do CPF/RG em tempo real (conforme RN01) |
| 9 | Sistema | Valida a força da senha (mínimo 8 caracteres, 1 maiúscula, 1 número, 1 especial) |
| 10 | Sistema | Exibe indicador visual de força da senha |
| 11 | Usuário | Marca checkbox "Li e aceito os Termos de Uso e Política de Privacidade" |
| 12 | Usuário | Clica em "Criar Conta" |
| 13 | Sistema | Valida todos os dados de entrada (conforme RNF02) |
| 14 | Sistema | Verifica se CPF/RG e e-mail não estão cadastrados |
| 15 | Sistema | Cria o registro do usuário com status "Pendente de Confirmação" |
| 16 | Sistema | Envia e-mail de confirmação com link de ativação (válido por 24 horas) |
| 17 | Sistema | Exibe mensagem: "Cadastro realizado! Verifique seu e-mail para ativar sua conta." |
| 18 | Usuário | Acessa o e-mail e clica no link de confirmação |
| 19 | Sistema | Valida o token de confirmação |
| 20 | Sistema | Altera status do usuário para "Ativo" |
| 21 | Sistema | Exibe mensagem: "Conta ativada com sucesso! Você já pode fazer login." |

---

###### Fluxos Alternativos

**FA01 – Cadastro de Professor com Código da Escola** *(extensão do passo 6)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 6a | Sistema | Para perfil "Professor", exibe campo adicional "Código da Instituição" |
| 6b | Usuário | Informa o código fornecido pela escola |
| 6c | Sistema | Valida o código e vincula automaticamente o professor à instituição |

**FA02 – Cadastro de Aluno com Código de Turma** *(extensão do passo 6)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 6d | Sistema | Para perfil "Aluno", exibe campo opcional "Código da Turma" |
| 6e | Usuário | Informa o código da turma (se disponível) |
| 6f | Sistema | Valida o código e vincula automaticamente o aluno à turma |
| 6g | Sistema | Notifica o professor responsável sobre novo aluno |

**FA03 – Cadastro via Convite** *(alternativa ao passo 3)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 3a | Usuário | Acessa link de convite recebido por e-mail |
| 3b | Sistema | Pré-preenche tipo de perfil e código da turma/instituição |
| 3c | Sistema | Exibe formulário simplificado (continua no passo 7) |

**FA04 – Reenviar E-mail de Confirmação** *(extensão do passo 17)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 17a | Usuário | Clica em "Reenviar e-mail de confirmação" |
| 17b | Sistema | Verifica se já não foi reenviado nos últimos 5 minutos |
| 17c | Sistema | Gera novo token e envia novo e-mail |
| 17d | Sistema | Exibe mensagem: "E-mail reenviado com sucesso!" |

---

###### Fluxos de Exceção

**FE01 – CPF/RG já cadastrado** *(exceção do passo 14)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 14a | Sistema | Detecta que o CPF/RG já está cadastrado no sistema |
| 14b | Sistema | Exibe mensagem: "Este CPF/RG já está cadastrado. Caso tenha esquecido sua senha, utilize a opção 'Recuperar Senha'." |
| 14c | Sistema | Exibe link para recuperação de senha |

**FE02 – E-mail já cadastrado** *(exceção do passo 14)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 14d | Sistema | Detecta que o e-mail já está cadastrado |
| 14e | Sistema | Exibe mensagem: "Este e-mail já está cadastrado. Utilize outro e-mail ou recupere sua senha." |

**FE03 – CPF/RG inválido** *(exceção do passo 8)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 8a | Sistema | Detecta formato inválido ou dígitos verificadores incorretos |
| 8b | Sistema | Destaca campo em vermelho e exibe: "CPF/RG inválido. Verifique os números informados." |

**FE04 – Senhas não coincidem** *(exceção do passo 13)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 13a | Sistema | Detecta que senha e confirmação são diferentes |
| 13b | Sistema | Exibe mensagem: "As senhas informadas não coincidem." |

**FE05 – Senha fraca** *(exceção do passo 9)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 9a | Sistema | Detecta que a senha não atende aos requisitos mínimos |
| 9b | Sistema | Exibe indicador "Senha Fraca" em vermelho |
| 9c | Sistema | Exibe requisitos não atendidos: "A senha deve conter: mínimo 8 caracteres, 1 letra maiúscula, 1 número, 1 caractere especial" |

**FE06 – Link de confirmação expirado** *(exceção do passo 19)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 19a | Sistema | Detecta que o token de confirmação expirou (>24 horas) |
| 19b | Sistema | Exibe mensagem: "Este link expirou. Solicite um novo e-mail de confirmação." |
| 19c | Sistema | Exibe botão "Reenviar e-mail" |

---

###### Requisitos Especiais

| ID | Descrição |
| :---: | :--- |
| RE01 | Senhas devem ser armazenadas utilizando hash bcrypt com salt |
| RE02 | O formulário deve implementar CAPTCHA após 3 tentativas de cadastro do mesmo IP |
| RE03 | Dados sensíveis devem ser transmitidos via HTTPS (TLS 1.3+) |
| RE04 | O sistema deve estar em conformidade com LGPD (RNF04), solicitando consentimento explícito |

---

###### Regras de Negócio Aplicáveis

| ID | Descrição |
| :---: | :--- |
| RN01 | O sistema deve validar o CPF ou RG do usuário no momento do cadastro, verificando formato e dígitos verificadores |
| RN02 | O sistema deve restringir o acesso a uma única sessão ativa por usuário |

---

###### User Stories Relacionadas

| ID | Descrição |
| :---: | :--- |
| US01 | Cadastrar no sistema informando dados pessoais e credenciais |

---

##### CU009 – Realizar Login

**Subsistema:** Autenticação e Controle de Acesso  
**Versão:** 1.0  
**Última Atualização:** 19/01/2026  
**Prioridade:** Alta

---

###### Descrição

Este Caso de Uso descreve o processo de autenticação de um usuário cadastrado no sistema EducAlin, permitindo acesso às funcionalidades de acordo com seu perfil (Professor, Aluno ou Coordenador).

---

###### Atores

| Tipo | Ator | Descrição |
| :---: | :--- | :--- |
| Principal | Usuário Cadastrado | Pessoa com conta ativa no sistema que deseja acessar a plataforma |
| Secundário | Sistema de Autenticação | Módulo interno responsável por validar credenciais e gerenciar sessões |

---

###### Pré-condições

| ID | Descrição |
| :---: | :--- |
| PRE-01 | Usuário possui conta cadastrada no sistema com status "Ativo" |
| PRE-02 | Usuário possui acesso à internet e navegador compatível |
| PRE-03 | Sistema está operacional e disponível |

---

###### Pós-condições

| ID | Descrição |
| :---: | :--- |
| POS-01 | Sessão autenticada foi criada para o usuário |
| POS-02 | Token JWT foi gerado e armazenado no navegador |
| POS-03 | Sessões anteriores do usuário foram encerradas (conforme RN02) |
| POS-04 | Registro de auditoria foi criado (data/hora, IP, dispositivo, sucesso/falha) |
| POS-05 | Usuário foi redirecionado ao painel principal correspondente ao seu perfil |

---

###### Fluxo Principal

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1 | Usuário | Acessa a página inicial do sistema EducAlin |
| 2 | Sistema | Exibe página de boas-vindas com opções "Entrar" e "Cadastrar-se" |
| 3 | Usuário | Clica em "Entrar" |
| 4 | Sistema | Exibe formulário de login com campos: E-mail, Senha, checkbox "Manter conectado" |
| 5 | Usuário | Informa e-mail cadastrado |
| 6 | Usuário | Informa senha |
| 7 | Usuário | Opcionalmente, marca "Manter conectado" |
| 8 | Usuário | Clica em "Entrar" |
| 9 | Sistema | Valida formato do e-mail |
| 10 | Sistema | Busca usuário pelo e-mail informado |
| 11 | Sistema | Verifica se a conta está ativa |
| 12 | Sistema | Compara hash da senha informada com hash armazenado |
| 13 | Sistema | Verifica se há sessão ativa em outro dispositivo |
| 14 | Sistema | Se houver, encerra sessão anterior (conforme RN02) |
| 15 | Sistema | Gera token JWT com dados do usuário e permissões |
| 16 | Sistema | Cria registro de sessão no banco de dados |
| 17 | Sistema | Armazena token no navegador (localStorage ou cookie seguro) |
| 18 | Sistema | Registra log de acesso bem-sucedido (conforme RNF15) |
| 19 | Sistema | Redireciona para o painel principal do perfil correspondente |
| 20 | Sistema | Exibe mensagem de boas-vindas: "Olá, [Nome]! Bem-vindo ao EducAlin." |

---

###### Fluxos Alternativos

**FA01 – Login com "Manter conectado"** *(extensão do passo 15)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 15a | Sistema | Gera token JWT com validade estendida (7 dias ao invés de 24 horas) |
| 15b | Sistema | Armazena refresh token para renovação automática |

**FA02 – Redirecionamento após login** *(extensão do passo 19)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 19a | Sistema | Verifica se há URL de destino salva (usuário tentou acessar página protegida) |
| 19b | Sistema | Redireciona para URL original ao invés do painel principal |

**FA03 – Primeiro acesso após cadastro** *(extensão do passo 19)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 19c | Sistema | Detecta que é o primeiro login do usuário |
| 19d | Sistema | Exibe tutorial de boas-vindas/onboarding |
| 19e | Usuário | Pode pular ou concluir o tutorial |

---

###### Fluxos de Exceção

**FE01 – Usuário não encontrado** *(exceção do passo 10)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 10a | Sistema | Não encontra usuário com o e-mail informado |
| 10b | Sistema | Exibe mensagem genérica: "E-mail ou senha incorretos" |
| 10c | Sistema | Incrementa contador de tentativas falhas |

**FE02 – Senha incorreta** *(exceção do passo 12)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 12a | Sistema | Hash da senha não corresponde ao armazenado |
| 12b | Sistema | Exibe mensagem genérica: "E-mail ou senha incorretos" |
| 12c | Sistema | Incrementa contador de tentativas falhas |
| 12d | Sistema | Registra log de tentativa de acesso falha (conforme RNF01) |

**FE03 – Conta bloqueada por tentativas excessivas** *(exceção do passo 10)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 10d | Sistema | Detecta que a conta está temporariamente bloqueada (5+ tentativas falhas) |
| 10e | Sistema | Exibe mensagem: "Conta temporariamente bloqueada por tentativas excessivas. Tente novamente em [X] minutos ou recupere sua senha." |
| 10f | Sistema | Exibe link para recuperação de senha |

**FE04 – Conta não ativada** *(exceção do passo 11)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 11a | Sistema | Detecta que a conta está com status "Pendente de Confirmação" |
| 11b | Sistema | Exibe mensagem: "Sua conta ainda não foi ativada. Verifique seu e-mail ou solicite um novo link de ativação." |
| 11c | Sistema | Exibe botão "Reenviar e-mail de ativação" |

**FE05 – Conta desativada/suspensa** *(exceção do passo 11)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 11d | Sistema | Detecta que a conta está com status "Desativada" ou "Suspensa" |
| 11e | Sistema | Exibe mensagem: "Sua conta está suspensa. Entre em contato com o administrador." |

---

###### Requisitos Especiais

| ID | Descrição |
| :---: | :--- |
| RE01 | Tempo de resposta do login deve ser inferior a 2 segundos (conforme RNF09) |
| RE02 | Token JWT deve ter validade máxima de 24 horas (ou 7 dias com "Manter conectado") |
| RE03 | Implementar rate limiting: máximo 5 tentativas falhas em 15 minutos |
| RE04 | Bloqueio temporário de 30 minutos após 5 tentativas falhas |

---

###### Regras de Negócio Aplicáveis

| ID | Descrição |
| :---: | :--- |
| RN02 | O sistema deve restringir o acesso a uma única sessão ativa por usuário |

---

###### User Stories Relacionadas

| ID | Descrição |
| :---: | :--- |
| US02 | Fazer login com e-mail e senha para acessar área personalizada |

---

##### CU010 – Recuperar Senha

**Subsistema:** Autenticação e Controle de Acesso  
**Versão:** 1.0  
**Última Atualização:** 19/01/2026  
**Prioridade:** Média

---

###### Descrição

Este Caso de Uso descreve o processo pelo qual um usuário que esqueceu sua senha pode recuperar o acesso à sua conta através de um link enviado por e-mail.

---

###### Atores

| Tipo | Ator | Descrição |
| :---: | :--- | :--- |
| Principal | Usuário Cadastrado | Pessoa com conta no sistema que não consegue acessar por esquecimento de senha |
| Secundário | Serviço de E-mail | Sistema externo responsável pelo envio de e-mail de recuperação |

---

###### Pré-condições

| ID | Descrição |
| :---: | :--- |
| PRE-01 | Usuário possui conta cadastrada no sistema (qualquer status exceto "Excluída") |
| PRE-02 | Usuário tem acesso ao e-mail cadastrado |
| PRE-03 | Sistema de e-mail está operacional |

---

###### Pós-condições

| ID | Descrição |
| :---: | :--- |
| POS-01 | Senha do usuário foi alterada para a nova senha informada |
| POS-02 | Todas as sessões ativas do usuário foram encerradas |
| POS-03 | Token de recuperação foi invalidado |
| POS-04 | Registro de auditoria foi criado com a alteração de senha |
| POS-05 | E-mail de confirmação de alteração foi enviado ao usuário |

---

###### Fluxo Principal

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1 | Usuário | Acessa a página de login |
| 2 | Usuário | Clica em "Esqueci minha senha" |
| 3 | Sistema | Exibe formulário de recuperação com campo "E-mail" |
| 4 | Usuário | Informa o e-mail cadastrado |
| 5 | Usuário | Clica em "Enviar link de recuperação" |
| 6 | Sistema | Valida o formato do e-mail |
| 7 | Sistema | Busca usuário pelo e-mail (sem revelar se existe ou não) |
| 8 | Sistema | Se usuário existe: gera token de recuperação (válido por 1 hora) |
| 9 | Sistema | Se usuário existe: envia e-mail com link de recuperação |
| 10 | Sistema | Exibe mensagem genérica: "Se o e-mail estiver cadastrado, você receberá instruções para recuperar sua senha." |
| 11 | Usuário | Acessa o e-mail e clica no link de recuperação |
| 12 | Sistema | Valida o token de recuperação |
| 13 | Sistema | Exibe formulário de nova senha com campos: Nova Senha, Confirmar Nova Senha |
| 14 | Usuário | Informa a nova senha |
| 15 | Usuário | Confirma a nova senha |
| 16 | Usuário | Clica em "Redefinir Senha" |
| 17 | Sistema | Valida a força da nova senha |
| 18 | Sistema | Verifica se a nova senha é diferente das últimas 3 senhas |
| 19 | Sistema | Atualiza a senha no banco de dados (hash bcrypt) |
| 20 | Sistema | Invalida o token de recuperação |
| 21 | Sistema | Encerra todas as sessões ativas do usuário |
| 22 | Sistema | Envia e-mail de confirmação de alteração de senha |
| 23 | Sistema | Exibe mensagem: "Senha alterada com sucesso! Faça login com sua nova senha." |
| 24 | Sistema | Redireciona para a página de login |

---

###### Fluxos Alternativos

**FA01 – Usuário lembra a senha durante o processo** *(extensão do passo 3)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 3a | Usuário | Clica em "Voltar para login" |
| 3b | Sistema | Redireciona para página de login |

**FA02 – Solicitar novo link** *(extensão do passo 10)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 10a | Usuário | Não recebeu o e-mail e retorna à página de recuperação |
| 10b | Usuário | Solicita novo envio |
| 10c | Sistema | Verifica se já não houve solicitação nos últimos 5 minutos |
| 10d | Sistema | Invalida token anterior e gera novo |
| 10e | Sistema | Envia novo e-mail |

---

###### Fluxos de Exceção

**FE01 – Token expirado** *(exceção do passo 12)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 12a | Sistema | Detecta que o token expirou (>1 hora) |
| 12b | Sistema | Exibe mensagem: "Este link expirou. Solicite um novo link de recuperação de senha." |
| 12c | Sistema | Exibe botão "Solicitar novo link" |

**FE02 – Token já utilizado** *(exceção do passo 12)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 12d | Sistema | Detecta que o token já foi utilizado |
| 12e | Sistema | Exibe mensagem: "Este link já foi utilizado. Se precisar, solicite um novo." |

**FE03 – Senha igual a uma das anteriores** *(exceção do passo 18)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 18a | Sistema | Detecta que a nova senha é igual a uma das últimas 3 |
| 18b | Sistema | Exibe mensagem: "A nova senha não pode ser igual às últimas 3 senhas utilizadas." |

**FE04 – Senhas não coincidem** *(exceção do passo 17)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 17a | Sistema | Detecta que senha e confirmação não coincidem |
| 17b | Sistema | Exibe mensagem: "As senhas informadas não coincidem." |

---

###### Requisitos Especiais

| ID | Descrição |
| :---: | :--- |
| RE01 | Token de recuperação deve ter validade máxima de 1 hora |
| RE02 | Token deve ser de uso único (invalidado após uso) |
| RE03 | Sistema não deve revelar se o e-mail está cadastrado (prevenção de enumeração) |
| RE04 | Histórico das últimas 3 senhas deve ser mantido para comparação |

---

###### User Stories Relacionadas

| ID | Descrição |
| :---: | :--- |
| US03 | Recuperar senha via e-mail para restabelecer acesso |

---

##### CU011 – Gerenciar Materiais de Estudo

**Subsistema:** Gestão de Conteúdo  
**Versão:** 1.0  
**Última Atualização:** 19/01/2026  
**Prioridade:** Média

---

###### Descrição

Este Caso de Uso descreve o processo pelo qual um professor faz upload, organiza, edita e remove materiais de estudo (PDFs, vídeos, áudios, documentos) disponibilizando-os para os alunos de suas turmas.

---

###### Atores

| Tipo | Ator | Descrição |
| :---: | :--- | :--- |
| Principal | Professor | Usuário autenticado com perfil de professor que gerencia os materiais |
| Secundário | Sistema de Armazenamento | Módulo interno responsável pelo armazenamento e gerenciamento de arquivos |
| Secundário | Aluno | Usuário que consome os materiais disponibilizados |

---

###### Pré-condições

| ID | Descrição |
| :---: | :--- |
| PRE-01 | Professor está autenticado no sistema com sessão válida |
| PRE-02 | Professor possui pelo menos uma turma cadastrada |
| PRE-03 | Sistema de armazenamento está operacional |

---

###### Pós-condições

| ID | Descrição |
| :---: | :--- |
| POS-01 | Material foi salvo no sistema de armazenamento |
| POS-02 | Material foi vinculado à(s) turma(s) selecionada(s) |
| POS-03 | Metadados foram registrados (título, descrição, tópico, data, professor) |
| POS-04 | Alunos das turmas vinculadas podem visualizar o material |
| POS-05 | Registro de auditoria foi criado |

---

###### Fluxo Principal (Upload de Material)

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1 | Professor | Acessa o menu "Meus Materiais" no painel principal |
| 2 | Sistema | Exibe biblioteca de materiais do professor organizada por: pastas, turmas, tipos de arquivo |
| 3 | Professor | Clica em "Adicionar Material" |
| 4 | Sistema | Exibe formulário com: área de upload (drag-and-drop), campos de metadados |
| 5 | Professor | Arrasta arquivo(s) para a área de upload ou clica para selecionar |
| 6 | Sistema | Valida o formato do arquivo (conforme RN04: PDF, DOC, DOCX, MP4, MP3, PNG, JPG) |
| 7 | Sistema | Valida o tamanho do arquivo (máximo 50MB conforme RN04) |
| 8 | Sistema | Exibe barra de progresso do upload |
| 9 | Sistema | Ao concluir upload, exibe prévia do arquivo |
| 10 | Professor | Preenche metadados: Título, Descrição (opcional), Tópico/Assunto, Tags |
| 11 | Professor | Seleciona turma(s) de destino (pode selecionar múltiplas) |
| 12 | Professor | Define visibilidade: "Imediata" ou "Agendada" (com data/hora) |
| 13 | Professor | Opcionalmente, organiza em pasta existente ou cria nova |
| 14 | Professor | Clica em "Publicar Material" |
| 15 | Sistema | Salva o material e metadados no banco de dados |
| 16 | Sistema | Vincula material às turmas selecionadas |
| 17 | Sistema | Se visibilidade imediata: notifica alunos sobre novo material |
| 18 | Sistema | Exibe mensagem: "Material publicado com sucesso!" |

---

###### Fluxos Alternativos

**FA01 – Upload de múltiplos arquivos** *(extensão do passo 5)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 5a | Professor | Seleciona múltiplos arquivos (até 10 por vez) |
| 5b | Sistema | Valida cada arquivo individualmente |
| 5c | Sistema | Exibe lista de arquivos com status individual |
| 5d | Professor | Pode remover arquivos da lista antes do upload |
| 5e | Sistema | Faz upload em paralelo com barras de progresso individuais |

**FA02 – Criar material a partir de link externo** *(alternativa ao passo 5)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 5f | Professor | Clica em "Adicionar Link Externo" |
| 5g | Sistema | Exibe campo para URL (YouTube, Google Drive, etc.) |
| 5h | Professor | Cola a URL do recurso |
| 5i | Sistema | Valida a URL e extrai metadados automaticamente (título, thumbnail) |
| 5j | Professor | Continua com preenchimento de metadados (passo 10) |

**FA03 – Editar material existente** *(alternativa ao passo 3)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 3a | Professor | Clica em "Editar" em um material existente |
| 3b | Sistema | Carrega metadados do material no formulário de edição |
| 3c | Professor | Altera campos desejados (não pode substituir arquivo, apenas metadados) |
| 3d | Professor | Clica em "Salvar Alterações" |
| 3e | Sistema | Atualiza metadados e exibe confirmação |

**FA04 – Excluir material** *(alternativa ao passo 3)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 3f | Professor | Clica em "Excluir" em um material |
| 3g | Sistema | Exibe modal: "Deseja excluir este material? Ele não estará mais disponível para os alunos." |
| 3h | Professor | Confirma exclusão |
| 3i | Sistema | Remove vínculos com turmas e move arquivo para "Lixeira" (recuperável por 30 dias) |
| 3j | Sistema | Exibe confirmação de exclusão |

---

###### Fluxos de Exceção

**FE01 – Formato de arquivo não suportado** *(exceção do passo 6)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 6a | Sistema | Detecta formato não suportado |
| 6b | Sistema | Exibe mensagem: "Formato de arquivo não suportado. Formatos aceitos: PDF, DOC, DOCX, MP4, MP3, PNG, JPG" |
| 6c | Sistema | Remove arquivo da lista de upload |

**FE02 – Arquivo excede tamanho máximo** *(exceção do passo 7)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 7a | Sistema | Detecta arquivo maior que 50MB |
| 7b | Sistema | Exibe mensagem: "Arquivo excede o tamanho máximo de 50MB. Reduza o tamanho ou divida em partes." |
| 7c | Sistema | Remove arquivo da lista de upload |

**FE03 – Falha durante upload** *(exceção do passo 8)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 8a | Sistema | Detecta falha de conexão ou erro durante upload |
| 8b | Sistema | Pausa o upload e exibe: "Falha no upload. Tentando reconectar..." |
| 8c | Sistema | Tenta retomar automaticamente por 3 vezes |
| 8d | Sistema | Se persistir: "Upload falhou. Verifique sua conexão e tente novamente." |

---

###### Requisitos Especiais

| ID | Descrição |
| :---: | :--- |
| RE01 | Verificação antivírus obrigatória antes do armazenamento |
| RE02 | Geração de thumbnail automática para vídeos e imagens |
| RE03 | Streaming de vídeo com adaptive bitrate para diferentes conexões |
| RE04 | Compressão automática de imagens >5MB |

---

###### Regras de Negócio Aplicáveis

| ID | Descrição |
| :---: | :--- |
| RN04 | O sistema deve suportar upload e download de arquivos nos formatos: PDF, DOC, DOCX, MP4, MP3, PNG, JPG, com tamanho máximo de 50MB por arquivo |
| RN06 | O professor cadastrado deve possuir acesso a uma tela de personalização para cada turma |

---

###### User Stories Relacionadas

| ID | Descrição |
| :---: | :--- |
| US09 | Fazer upload de materiais de estudo para os alunos |
| US16 | Visualizar e interagir com materiais enviados pelo professor |

---

##### CU012 – Definir Metas de Aprendizado

**Subsistema:** Acompanhamento Individualizado  
**Versão:** 1.0  
**Última Atualização:** 19/01/2026  
**Prioridade:** Baixa

---

###### Descrição

Este Caso de Uso descreve o processo pelo qual um professor define metas de aprendizado personalizadas para seus alunos, estabelecendo objetivos mensuráveis e prazos para acompanhamento do progresso individual.

---

###### Atores

| Tipo | Ator | Descrição |
| :---: | :--- | :--- |
| Principal | Professor | Usuário autenticado que define e acompanha as metas |
| Secundário | Aluno | Usuário que visualiza suas metas e registra progresso |
| Secundário | Sistema de Análise | Módulo que sugere metas baseadas no desempenho |

---

###### Pré-condições

| ID | Descrição |
| :---: | :--- |
| PRE-01 | Professor está autenticado no sistema |
| PRE-02 | Professor possui pelo menos uma turma com alunos cadastrados |
| PRE-03 | Existem dados de desempenho para basear sugestões (opcional) |

---

###### Pós-condições

| ID | Descrição |
| :---: | :--- |
| POS-01 | Meta foi criada e vinculada ao(s) aluno(s) selecionado(s) |
| POS-02 | Aluno(s) recebeu(ram) notificação sobre nova meta |
| POS-03 | Meta está disponível no painel do aluno |
| POS-04 | Sistema iniciou monitoramento automático de progresso |
| POS-05 | Registro de auditoria foi criado |

---

###### Fluxo Principal

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1 | Professor | Acessa o menu "Metas de Aprendizado" ou acessa via painel do aluno |
| 2 | Sistema | Exibe painel de gestão de metas com: metas ativas, metas concluídas, metas vencidas |
| 3 | Professor | Clica em "Nova Meta" |
| 4 | Sistema | Exibe formulário de criação de meta com campos e sugestões automáticas |
| 5 | Sistema | Baseado no desempenho, sugere metas como: "Melhorar nota em [Tópico] de X para Y" |
| 6 | Professor | Seleciona aluno(s) destinatário(s): individual, grupo ou turma inteira |
| 7 | Professor | Define o tipo de meta: Nota Mínima, Conclusão de Atividades, Frequência, Participação, Personalizada |
| 8 | Professor | Preenche os parâmetros da meta: descrição, valor alvo (ex: nota 7.0), tópico/disciplina relacionada, prazo (data limite) |
| 9 | Professor | Define recompensa/reconhecimento (opcional): badge digital, destaque no mural |
| 10 | Professor | Adiciona mensagem motivacional (opcional) |
| 11 | Professor | Clica em "Criar Meta" |
| 12 | Sistema | Valida os dados da meta |
| 13 | Sistema | Cria a meta e vincula aos alunos selecionados |
| 14 | Sistema | Envia notificação aos alunos sobre nova meta |
| 15 | Sistema | Exibe confirmação: "Meta criada com sucesso! [X] aluno(s) notificado(s)." |

---

###### Fluxos Alternativos

**FA01 – Criar meta a partir do painel do aluno** *(alternativa ao passo 1)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 1a | Professor | Está visualizando o painel individual de um aluno |
| 1b | Professor | Clica em "Definir Meta" na seção de metas |
| 1c | Sistema | Pré-seleciona o aluno e sugere metas baseadas em suas dificuldades |
| 1d | Sistema | Continua no passo 7 |

**FA02 – Usar template de meta** *(extensão do passo 4)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 4a | Professor | Clica em "Usar Template" |
| 4b | Sistema | Exibe biblioteca de templates: metas padrão, metas do professor |
| 4c | Professor | Seleciona um template |
| 4d | Sistema | Preenche campos automaticamente, permitindo ajustes |

**FA03 – Meta para turma inteira** *(extensão do passo 6)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 6a | Professor | Seleciona "Toda a Turma" |
| 6b | Sistema | Aplica a mesma meta para todos os alunos da turma |
| 6c | Sistema | Permite exceções (excluir alunos específicos) |

**FA04 – Editar meta existente** *(alternativa ao passo 3)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 3a | Professor | Clica em "Editar" em uma meta ativa |
| 3b | Sistema | Carrega dados da meta no formulário |
| 3c | Professor | Altera campos desejados (prazo, valor alvo, etc.) |
| 3d | Professor | Clica em "Salvar Alterações" |
| 3e | Sistema | Notifica alunos sobre alteração na meta |

**FA05 – Encerrar meta antecipadamente** *(alternativa ao passo 3)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 3f | Professor | Clica em "Encerrar" em uma meta ativa |
| 3g | Sistema | Solicita motivo: "Concluída", "Cancelada", "Não aplicável" |
| 3h | Professor | Seleciona motivo e confirma |
| 3i | Sistema | Altera status da meta e notifica aluno |

---

###### Fluxos de Exceção

**FE01 – Prazo inválido** *(exceção do passo 12)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 12a | Sistema | Detecta prazo no passado ou muito curto (<24h) |
| 12b | Sistema | Exibe mensagem: "O prazo deve ser de pelo menos 24 horas a partir de agora." |

**FE02 – Valor alvo inválido** *(exceção do passo 12)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 12c | Sistema | Detecta valor alvo fora dos limites (ex: nota >10) |
| 12d | Sistema | Exibe mensagem: "O valor alvo deve estar entre [min] e [max]." |

**FE03 – Meta duplicada** *(exceção do passo 12)*

| Passo | Ator/Sistema | Ação |
| :---: | :---: | :--- |
| 12e | Sistema | Detecta meta muito similar já ativa para o mesmo aluno |
| 12f | Sistema | Exibe aviso: "Já existe uma meta similar ativa para este aluno. Deseja continuar?" |
| 12g | Professor | Confirma ou cancela |

---

###### Requisitos Especiais

| ID | Descrição |
| :---: | :--- |
| RE01 | Sistema deve calcular progresso automaticamente baseado em notas registradas |
| RE02 | Notificações de lembrete devem ser enviadas quando faltarem 7 dias, 3 dias e 1 dia para o prazo |
| RE03 | Metas concluídas devem gerar registro para relatório de evolução |
| RE04 | Interface gamificada com elementos visuais de progresso (barras, badges) |

---

###### Regras de Negócio Aplicáveis

| ID | Descrição |
| :---: | :--- |
| RN03 | O sistema deve gerar relatórios de desempenho acessíveis apenas para usuários com perfil de professor ou coordenador (progresso das metas incluído) |

---

###### User Stories Relacionadas

| ID | Descrição |
| :---: | :--- |
| US13 | Definir metas de aprendizado para os alunos |

---

### 6. Protótipo do Sistema

O protótipo interativo do sistema EducAlin foi desenvolvido no Figma e pode ser acessado através do link abaixo:

[Protótipo EducAlin - Figma](https://www.figma.com/proto/xyRMLE6weB3g2CjnDTjJcq/EducAlin---Prot%C3%B3tipo?page-id=18%3A580&node-id=64-144&p=f&viewport=1412%2C204%2C0.56&t=t7RRVwBnc8pTwMlK-1&scaling=min-zoom&content-scaling=fixed&starting-point-node-id=64%3A144)

O protótipo contempla as principais telas do sistema para os perfis de Professor e Aluno, permitindo a validação dos fluxos de navegação e da interface proposta.

---

### 7. Glossário

| Termo | Definição |
| :--- | :--- |
| **Caso de Uso** | Descrição de uma sequência de ações que o sistema executa para produzir um resultado de valor para um ator. |
| **Painel Principal** | Tela inicial do sistema após o login, também conhecido como dashboard, que apresenta uma visão geral das funcionalidades e informações relevantes para o usuário. |
| **Plano de Ação** | Conjunto personalizado de materiais de estudo, exercícios e orientações criado pelo professor para auxiliar um aluno específico a superar suas dificuldades. |
| **Pós-condição** | Estado do sistema após a execução bem-sucedida de um Caso de Uso. |
| **Pré-condição** | Condição que deve ser verdadeira antes da execução de um Caso de Uso. |
| **User Story** | Descrição informal de uma funcionalidade do sistema escrita sob a perspectiva do usuário final, seguindo o formato "Como [tipo de usuário], eu quero [objetivo], para [benefício]". |
| **UML** | Unified Modeling Language - linguagem de modelagem padronizada utilizada para especificação, visualização e documentação de sistemas de software. |
| **Token JWT** | JSON Web Token - padrão de token de acesso utilizado para autenticação e autorização em aplicações web. |
| **Hash bcrypt** | Algoritmo de hash criptográfico utilizado para armazenamento seguro de senhas. |
| **TLS** | Transport Layer Security - protocolo de segurança para comunicações criptografadas na internet. |

---

### 8. Matriz de Rastreabilidade

A tabela a seguir apresenta a rastreabilidade completa entre User Stories, Casos de Uso, Regras de Negócio e Requisitos Não Funcionais.

| User Story | Caso de Uso | Regras de Negócio | RNFs Aplicáveis |
| :---: | :--- | :---: | :---: |
| US01 | CU008 – Cadastrar Usuário | RN01, RN02 | RNF01, RNF02, RNF04 |
| US02 | CU009 – Realizar Login | RN02 | RNF01, RNF09, RNF15 |
| US03 | CU010 – Recuperar Senha | RN02 | RNF02, RNF03 |
| US04 | CU002 – Gerenciar Turmas | RN06 | RNF05, RNF06 |
| US05 | CU003 – Registrar Notas | RN03 | RNF05, RNF09 |
| US06 | CU003 – Registrar Notas | RN03 | RNF05 |
| US07 | CU004 – Gerar Relatório de Desempenho | RN03 | RNF09, RNF10, RNF19 |
| US08 | CU004 – Gerar Relatório de Desempenho | RN03 | RNF09, RNF19 |
| US09 | CU011 – Gerenciar Materiais de Estudo | RN04 | RNF11, RNF12 |
| US10 | CU005 – Enviar Mensagem Privada | RN05 | RNF03 |
| US11 | CU006 – Gerenciar Fórum de Dúvidas | RN04, RN05 | RNF03 |
| US12 | CU001 – Criar Plano de Ação Personalizado | RN03, RN04, RN06 | RNF05, RNF09 |
| US13 | CU012 – Definir Metas de Aprendizado | RN03 | RNF05, RNF06 |
| US14 | CU007 – Visualizar Desempenho Individual | RN03 | RNF05, RNF09 |
| US15 | CU007 – Visualizar Desempenho Individual | RN03 | RNF05 |
| US16 | CU007, CU011 | RN04 | RNF11 |
| US17 | CU005 – Enviar Mensagem Privada | RN05 | RNF03 |
| US18 | CU004 – Gerar Relatório de Desempenho | RN03 | RNF09, RNF19 |
| US19 | CU004 – Gerar Relatório de Desempenho | RN03 | RNF10, RNF19 |
