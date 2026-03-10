# Seed de Dados de Demonstração

Este script popula o banco de dados com dados de teste para facilitar a demonstração do sistema EducAlin.

## O que é criado?

### Usuários Predefinidos

| Perfil | Email | Senha |
|--------|-------|-------|
| **Professor** | professor@educalin.com | senha123 |
| **Aluno** | aluno@educalin.com | senha123 |
| **Coordenador** | coordenador@educalin.com | senha123 |

### Dados Adicionais

- **3 Turmas**: MAT101, POO202, FIS101
- **4 Alunos adicionais** matriculados em todas as turmas
- **9 Avaliações** (3 por turma)
- **36 Notas** registradas
- **3 Planos de Ação** ativos

## Como Usar

### 0. Configurar Variáveis de Ambiente

Antes de executar o sistema, copie o arquivo `.env.example` para `.env`:

```bash
# No Windows (PowerShell)
Copy-Item .env.example .env

# No Linux/Mac
cp .env.example .env
```

O arquivo `.env` já vem configurado para desenvolvimento. **Não é necessário alterá-lo para a demonstração.**

### 1. Executar o Seed

```bash
python database/seed_demo.py
```

### 2. Iniciar o Servidor

```bash
python -m uvicorn src.educalin.api.main:app --reload
```

### 3. Acessar o Sistema

####

 Opção 1: Com Login (Recomendado)
Abra o navegador em: **http://localhost:8000/login**

Use as credenciais acima para fazer login.

#### Opção 2: Acesso Direto ao Dashboard (Para Demonstração)
Para demonstração rápida, você pode acessar diretamente:

**Dashboard do Professor**: http://localhost:8000/dashboard/professor

_(O sistema está configurado para usar o professor de ID 1000 para fins de demonstração)_

## Para a Demonstração do Checkpoint

### Dashboard do Professor

1. **Login**: Use `professor@educalin.com` / `senha123`
2. **Acesse**: http://localhost:8000/dashboard/professor
3. **Demonstre**:
   - Lista de 3 turmas (MAT101, POO202, FIS101)
   - Formulário de registro de nota
   - Botão "Criar Plano de Ação"
   - Botão "Ver Relatório"

### Funcionalidades Implementadas

#### 1. Listar Turmas
- Mostra todas as turmas do professor
- Exibe código, disciplina e número de alunos
- Cards responsivos com hover effects

#### 2. Registrar Nota
- Seleção em cascata: Turma → Avaliação → Aluno
- Validação de campos
- Feedback visual de sucesso/erro

#### 3. Criar Plano de Ação
- Modal interativo
- Seleciona aluno, define objetivo e prazo
- Integrado com API REST

#### 4. Ver Relatório
- Modal com relatório de desempenho
- Dados reais do banco SQLite
- Formato texto

## Recriar Dados

Para limpar e recriar os dados de demonstração, basta executar o seed novamente:

```bash
python database/seed_demo.py
```

O script automaticamente remove os dados anteriores antes de criar novos.

## Estrutura dos Dados

```
Professor (ID: 1000)
├── Turma: MAT101
│   ├── 4 alunos matriculados
│   ├── 3 avaliações
│   └── 12 notas
├── Turma: POO202
│   ├── 4 alunos matriculados
│   ├── 3 avaliações
│   └── 12 notas
└── Turma: FIS101
    ├── 4 alunos matriculados
    ├── 3 avaliações
    └── 12 notas

Planos de Ação: 3 ativos
```

## Critérios de Aceitação Atendidos

- **Interface Responsiva**: Bootstrap 5.3.3
- **4 Funcionalidades**: Todas demonstráveis
- **Dados Reais**: 100% do banco SQLite

## Dicas

- Os dados usam IDs a partir de 1000 para não conflitar com dados reais
- Notas são geradas com variação aleatória baseada no perfil do aluno
- Todas as senhas são `senha123` (apenas para demonstração!)
- O arquivo `.env` contém configurações necessárias (JWT_SECRET_KEY, etc.)
- **Se aparecer erro "JWT_SECRET_KEY", verifique se o arquivo `.env` existe**
