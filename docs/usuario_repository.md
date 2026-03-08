# UsuarioRepository - Documentação

## Visão Geral

O `UsuarioRepository` implementa o padrão Repository para abstrair operações de banco de dados com usuários, utilizando **SQL puro (SQLite3)** sem SQLAlchemy.

## Características

- ✅ **SQL Puro**: Usa apenas sqlite3, sem ORM
- ✅ **Single Table Inheritance (STI)**: Suporta Professor, Coordenador e Aluno na mesma tabela
- ✅ **Validações**: Email, senhas e campos obrigatórios
- ✅ **Segurança**: Passwords hasheadas com bcrypt
- ✅ **Polimorfismo**: Retorna a subclasse correta (ProfessorModel, CoordenadorModel, AlunoModel)
- ✅ **Context Manager**: Gerenciamento automático de conexões
- ✅ **Testado**: 43 testes unitários cobrindo todos os métodos

## Instalação

```python
from educalin.repositories import UsuarioRepository
from educalin.repositories.base import get_db
```

## Métodos Disponíveis

### 1. `criar(usuario_data: Dict[str, Any]) -> int`

Cria um novo usuário no banco de dados.

**Parâmetros:**
- `usuario_data`: Dicionário com os dados do usuário:
  - `tipo_usuario` (obrigatório): `'professor'`, `'coordenador'` ou `'aluno'`
  - `nome` (obrigatório): Nome completo
  - `email` (obrigatório): E-mail válido e único
  - `senha` (obrigatório): Senha em texto plano (será hasheada)
  - `registro_funcional`: (obrigatório para professores)
  - `codigo_coordenacao`: (obrigatório para coordenadores)
  - `matricula`: (obrigatória para alunos)

**Retorna:** ID do usuário criado

**Exemplo:**
```python
with get_db() as conn:
    repo = UsuarioRepository(conn)
    
    # Criar professor
    professor_id = repo.criar({
        'tipo_usuario': 'professor',
        'nome': 'João Silva',
        'email': 'joao@escola.com',
        'senha': 'senha_segura_123',
        'registro_funcional': 'PROF001'
    })
    
    # Criar aluno
    aluno_id = repo.criar({
        'tipo_usuario': 'aluno',
        'nome': 'Maria Santos',
        'email': 'maria@estudante.com',
        'senha': 'senha789',
        'matricula': '2024001'
    })
```

**Validações:**
- Email válido e único
- Campos obrigatórios preenchidos
- Campo específico do tipo (registro_funcional, codigo_coordenacao, matricula)

---

### 2. `buscar_por_id(id: int) -> Optional[UsuarioModel]`

Busca um usuário por ID.

**Parâmetros:**
- `id`: ID do usuário

**Retorna:** `UsuarioModel` (ou subclasse) se encontrado, `None` caso contrário

**Exemplo:**
```python
usuario = repo.buscar_por_id(1)
if usuario:
    print(f"Nome: {usuario.nome}")
    print(f"Tipo: {usuario.__class__.__name__}")  # ProfessorModel, AlunoModel, etc.
```

---

### 3. `buscar_por_email(email: str) -> Optional[UsuarioModel]`

Busca um usuário por e-mail (case-insensitive).

**Parâmetros:**
- `email`: E-mail do usuário

**Retorna:** `UsuarioModel` (ou subclasse) se encontrado, `None` caso contrário

**Exemplo:**
```python
# Busca é case-insensitive
usuario = repo.buscar_por_email('JOAO@ESCOLA.COM')
if usuario:
    print(f"Email normalizado: {usuario.email}")  # joao@escola.com
```

---

### 4. `atualizar(id: int, dados: Dict[str, Any]) -> bool`

Atualiza dados de um usuário existente.

**Parâmetros:**
- `id`: ID do usuário
- `dados`: Dicionário com campos a atualizar:
  - `nome`: Novo nome
  - `email`: Novo e-mail
  - `senha`: Nova senha (será hasheada)
  - `registro_funcional`, `codigo_coordenacao`, `matricula`: Campos específicos

**Retorna:** `True` se atualizou, `False` se usuário não existe

**Exemplo:**
```python
# Atualizar nome e email
sucesso = repo.atualizar(1, {
    'nome': 'João Silva Santos',
    'email': 'joao.novo@escola.com'
})

# Atualizar senha
sucesso = repo.atualizar(1, {
    'senha': 'nova_senha_segura'
})
```

**Validações:**
- Email válido e único (se fornecido)
- Nome não vazio (se fornecido)
- Senha hasheada automaticamente

---

### 5. `autenticar(email: str, senha: str) -> Optional[UsuarioModel]`

Autentica um usuário por e-mail e senha.

**Parâmetros:**
- `email`: E-mail do usuário
- `senha`: Senha em texto plano

**Retorna:** `UsuarioModel` (ou subclasse) se credenciais válidas, `None` caso contrário

**Exemplo:**
```python
usuario = repo.autenticar('joao@escola.com', 'senha_segura_123')
if usuario:
    print(f"Login bem-sucedido: {usuario.nome}")
    print(f"Tipo: {usuario.tipo_usuario}")
else:
    print("E-mail ou senha inválidos")
```

---

### 6. `listar_todos(tipo_usuario: Optional[str] = None) -> list[UsuarioModel]`

Lista todos os usuários, opcionalmente filtrados por tipo.

**Parâmetros:**
- `tipo_usuario` (opcional): `'professor'`, `'coordenador'` ou `'aluno'`

**Retorna:** Lista de `UsuarioModel` (com subclasses apropriadas)

**Exemplo:**
```python
# Listar todos
todos = repo.listar_todos()
for usuario in todos:
    print(f"{usuario.nome} - {usuario.tipo_usuario}")

# Listar apenas professores
professores = repo.listar_todos(tipo_usuario='professor')
for prof in professores:
    print(f"{prof.nome} - {prof.registro_funcional}")
```

---

### 7. `deletar(id: int) -> bool`

Remove um usuário do banco de dados.

**Parâmetros:**
- `id`: ID do usuário

**Retorna:** `True` se deletou, `False` se usuário não existe

**Exemplo:**
```python
sucesso = repo.deletar(1)
if sucesso:
    print("Usuário deletado com sucesso")
```

---

### 8. `existe_email(email: str, excluir_id: Optional[int] = None) -> bool`

Verifica se um e-mail já está cadastrado.

**Parâmetros:**
- `email`: E-mail a verificar
- `excluir_id` (opcional): ID de usuário a excluir da verificação (útil para updates)

**Retorna:** `True` se e-mail existe, `False` caso contrário

**Exemplo:**
```python
# Verificar disponibilidade de email
if repo.existe_email('novo@escola.com'):
    print("E-mail já cadastrado")
else:
    print("E-mail disponível")

# Verificar se outro usuário tem o mesmo email (útil para atualizações)
if repo.existe_email('joao@escola.com', excluir_id=1):
    print("Outro usuário já usa este e-mail")
```

---

## Uso com Context Manager

O `UsuarioRepository` pode ser usado como context manager, gerenciando a conexão automaticamente:

```python
# Repository gerencia a própria conexão
with UsuarioRepository() as repo:
    usuario_id = repo.criar({
        'tipo_usuario': 'professor',
        'nome': 'João Silva',
        'email': 'joao@escola.com',
        'senha': 'senha123',
        'registro_funcional': 'PROF001'
    })
    
    usuario = repo.buscar_por_id(usuario_id)
    print(usuario.nome)
# Conexão fechada automaticamente
```

Ou passar uma conexão existente:

```python
with get_db() as conn:
    repo = UsuarioRepository(conn)
    # usar repo...
# Conexão gerenciada pelo get_db()
```

---

## Tratamento de Erros

O repository levanta exceções apropriadas:

```python
try:
    repo.criar({
        'tipo_usuario': 'professor',
        'nome': 'João',
        'email': 'email_invalido',  # sem @
        'senha': 'senha123',
        'registro_funcional': 'PROF001'
    })
except ValueError as e:
    print(f"Erro de validação: {e}")
    # "Formato de e-mail inválido: email_invalido"

try:
    repo.criar({
        'tipo_usuario': 'professor',
        'nome': 'João',
        'email': 'duplicado@escola.com',  # já existe
        'senha': 'senha123',
        'registro_funcional': 'PROF001'
    })
except ValueError as e:
    print(f"Erro: {e}")
    # "E-mail 'duplicado@escola.com' já está cadastrado"
```

**Exceções comuns:**
- `ValueError`: Validação de dados (email inválido, campos obrigatórios faltando)
- `ValueError`: Constraints de unicidade (email, registro, matrícula duplicados)

---

## Polimorfismo (Single Table Inheritance)

O repository retorna automaticamente a subclasse correta:

```python
# Criar diferentes tipos
prof_id = repo.criar({'tipo_usuario': 'professor', ...})
coord_id = repo.criar({'tipo_usuario': 'coordenador', ...})
aluno_id = repo.criar({'tipo_usuario': 'aluno', ...})

# Buscar retorna o tipo correto
professor = repo.buscar_por_id(prof_id)
print(isinstance(professor, ProfessorModel))  # True
print(professor.registro_funcional)  # Acesso ao campo específico

coordenador = repo.buscar_por_id(coord_id)
print(isinstance(coordenador, CoordenadorModel))  # True
print(coordenador.codigo_coordenacao)

aluno = repo.buscar_por_id(aluno_id)
print(isinstance(aluno, AlunoModel))  # True
print(aluno.matricula)
```

---

## Testes

Execute os testes completos:

```bash
pytest tests/repositories/test_usuario_repository.py -v
```

**Cobertura:**
- ✅ 43 testes unitários
- ✅ Todos os métodos testados
- ✅ Validações e casos de erro
- ✅ Context manager
- ✅ Polimorfismo

---

## Exemplo Completo

Veja o arquivo `examples/usuario_repository_example.py` para um exemplo completo de uso.

```bash
python examples/usuario_repository_example.py
```

---

## Estrutura do Banco de Dados

Tabela `usuarios`:
```sql
CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_usuario TEXT NOT NULL CHECK(tipo_usuario IN ('professor', 'coordenador', 'aluno')),
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    registro_funcional TEXT UNIQUE,  -- Professor
    codigo_coordenacao TEXT UNIQUE,  -- Coordenador
    matricula TEXT UNIQUE,           -- Aluno
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

---

## Próximos Passos

Para implementar repositories similares para outras entidades:
1. Criar `TurmaRepository`, `MaterialRepository`, etc.
2. Seguir o mesmo padrão de `UsuarioRepository`
3. Reutilizar validações de `BaseModel`
4. Implementar testes abrangentes
