# Exemplos de Uso dos Modelos - EducAlin

Este arquivo contém exemplos práticos de como usar os modelos criados.

## Setup Inicial

```python
import sqlite3
from datetime import datetime, date, timedelta
from educalin.repositories.models import (
    # Schemas
    create_all_tables,
    
    # Modelos de Usuário
    ProfessorModel,
    AlunoModel,
    CoordenadorModel,
    
    # Modelos de Turma
    TurmaModel,
    
    # Modelos de Material (Polimorfismo)
    MaterialPDFModel,
    MaterialVideoModel,
    MaterialLinkModel,
    
    # Modelos de Avaliação e Nota
    AvaliacaoModel,
    NotaModel,
    
    # Modelos de Meta
    MetaModel,
    
    # Modelos de Plano de Ação
    PlanoAcaoModel,
)

# Criar conexão com banco de dados
conn = sqlite3.connect('database/educalin.db')
conn.row_factory = sqlite3.Row

# Ativar Foreign Keys no SQLite
conn.execute("PRAGMA foreign_keys = ON")

# Criar todas as tabelas
create_all_tables(conn)
```

## 1. Criando Usuários (STI - Single Table Inheritance)

```python
# Criar Professor
professor_id = ProfessorModel.criar(
    conn=conn,
    nome="Dr. João Silva",
    email="joao.silva@educalin.com",
    senha="senha_segura",
    registro_funcional="PROF123"
)
print(f"Professor criado com ID: {professor_id}")

# Criar Aluno
aluno_id = AlunoModel.criar(
    conn=conn,
    nome="Maria Santos",
    email="maria.santos@estudante.com",
    senha="senha_aluno",
    matricula="2024001"
)
print(f"Aluno criado com ID: {aluno_id}")

# Criar Coordenador
coordenador_id = CoordenadorModel.criar(
    conn=conn,
    nome="Ana Paula",
    email="ana.paula@educalin.com",
    senha="senha_coord",
    codigo_coordenacao="COORD456"
)
print(f"Coordenador criado com ID: {coordenador_id}")

# Buscar usuário (retorna a subclasse correta automaticamente)
professor = ProfessorModel.buscar_por_id(conn, professor_id)
print(f"Professor: {professor.nome} - {professor.registro_funcional}")
```

## 2. Criando Turmas e Relacionamentos N:N

```python
# Criar turma
turma_id = TurmaModel.criar(
    conn=conn,
    codigo="POO2024-1",
    disciplina="Programação Orientada a Objetos",
    semestre="2024.1",
    professor_id=professor_id
)
print(f"Turma criada com ID: {turma_id}")

# Adicionar alunos à turma (Many-to-Many)
turma = TurmaModel.buscar_por_id(conn, turma_id)
turma.adicionar_aluno(conn, aluno_id)
print(f"Aluno {aluno_id} adicionado à turma")

# Listar alunos da turma
alunos_ids = turma.listar_alunos(conn)
print(f"Alunos na turma: {alunos_ids}")
```

## 3. Criando Materiais (STI com Polimorfismo)

```python
# Criar Material PDF
pdf_id = MaterialPDFModel.criar(
    conn=conn,
    titulo="Introdução à POO",
    descricao="Material sobre conceitos básicos de POO",
    autor_id=professor_id,
    num_paginas=50
)
print(f"Material PDF criado com ID: {pdf_id}")

# Criar Material de Vídeo
video_id = MaterialVideoModel.criar(
    conn=conn,
    titulo="Aula 1 - Encapsulamento",
    descricao="Vídeo explicativo sobre encapsulamento",
    autor_id=professor_id,
    duracao_segundos=1800,  # 30 minutos
    codec="H.264"
)
print(f"Material Vídeo criado com ID: {video_id}")

# Criar Material Link
link_id = MaterialLinkModel.criar(
    conn=conn,
    titulo="Documentação Python",
    descricao="Link para documentação oficial",
    autor_id=professor_id,
    url="https://docs.python.org/3/",
    tipo_conteudo="documentacao"
)
print(f"Material Link criado com ID: {link_id}")

# Buscar material (retorna a subclasse correta automaticamente)
from educalin.repositories.models import MaterialModel
material = MaterialModel.buscar_por_id(conn, pdf_id)
print(f"Tipo do material: {type(material).__name__}")
print(f"Material: {material.titulo} - {material.num_paginas} páginas")
```

## 4. Criando Avaliações e Notas

```python
# Criar avaliação
avaliacao_id = AvaliacaoModel.criar(
    conn=conn,
    titulo="Prova 1 - POO",
    data=date(2024, 4, 15),
    valor_maximo=10.0,
    peso=0.3,  # 30% da nota final
    turma_id=turma_id
)
print(f"Avaliação criada com ID: {avaliacao_id}")

# Registrar nota do aluno (ForeignKey: aluno_id e avaliacao_id)
nota_id = NotaModel.criar(
    conn=conn,
    aluno_id=aluno_id,
    avaliacao_id=avaliacao_id,
    valor=8.5
)
print(f"Nota registrada com ID: {nota_id}")

# Buscar nota específica
nota = NotaModel.buscar_por_aluno_avaliacao(conn, aluno_id, avaliacao_id)
print(f"Nota do aluno: {nota.valor}")

# Calcular percentual
percentual = nota.calcular_percentual(conn)
print(f"Percentual: {percentual:.1f}%")

# Listar todas as notas do aluno
notas_aluno = NotaModel.listar_por_aluno(conn, aluno_id)
print(f"Total de notas do aluno: {len(notas_aluno)}")

# Calcular média da turma na avaliação
avaliacao = AvaliacaoModel.buscar_por_id(conn, avaliacao_id)
media_turma = avaliacao.calcular_media_turma(conn)
print(f"Média da turma: {media_turma:.2f}")
```

## 5. Criando Metas de Aprendizado

```python
# Criar meta para o aluno
meta_id = MetaModel.criar(
    conn=conn,
    aluno_id=aluno_id,
    descricao="Alcançar média 9.0 em POO",
    valor_alvo=9.0,
    prazo=datetime.now() + timedelta(days=90),
    progresso_atual=7.5
)
print(f"Meta criada com ID: {meta_id}")

# Buscar meta
meta = MetaModel.buscar_por_id(conn, meta_id)
print(f"Meta: {meta.descricao}")
print(f"Progresso: {meta.calcular_percentual_progresso():.1f}%")

# Atualizar progresso
meta_atingida = meta.atualizar_progresso(conn, 9.2)
if meta_atingida:
    print("🎉 Meta atingida!")

# Listar metas ativas do aluno
metas_ativas = MetaModel.listar_por_aluno(conn, aluno_id, apenas_ativas=True)
print(f"Metas ativas: {len(metas_ativas)}")

# Verificar se meta está vencida
if meta.esta_vencida():
    print("⚠️ Meta vencida!")
```

## 6. Criando Planos de Ação (Composição com Materiais)

```python
# Criar plano de ação
plano_id = PlanoAcaoModel.criar(
    conn=conn,
    aluno_id=aluno_id,
    objetivo="Revisar conceitos de herança e polimorfismo",
    prazo_dias=30,
    observacoes="Focar em exercícios práticos"
)
print(f"Plano de ação criado com ID: {plano_id}")

# Buscar plano
plano = PlanoAcaoModel.buscar_por_id(conn, plano_id)
print(f"Plano: {plano.objetivo}")
print(f"Status: {plano.status}")

# Adicionar materiais ao plano (Composição Many-to-Many)
plano.adicionar_material(conn, pdf_id)
plano.adicionar_material(conn, video_id)
plano.adicionar_material(conn, link_id)
print("Materiais adicionados ao plano")

# Listar materiais do plano
materiais_ids = plano.listar_materiais(conn)
print(f"Materiais no plano: {materiais_ids}")

# Atualizar status (máquina de estados)
try:
    plano.atualizar_status(conn, 'enviado')  # rascunho -> enviado
    print("Plano enviado ao aluno")
    
    plano.atualizar_status(conn, 'em_andamento')  # enviado -> em_andamento
    print("Aluno iniciou o plano")
    
    plano.atualizar_status(conn, 'concluido')  # em_andamento -> concluido
    print("✅ Plano concluído!")
except ValueError as e:
    print(f"Erro: {e}")

# Verificar se plano está vencido
if plano.esta_vencido():
    print("⚠️ Plano vencido!")

# Remover material do plano
plano.remover_material(conn, link_id)
print(f"Material {link_id} removido do plano")

# Listar planos do aluno por status
planos_concluidos = PlanoAcaoModel.listar_por_aluno(
    conn, 
    aluno_id, 
    status='concluido'
)
print(f"Planos concluídos: {len(planos_concluidos)}")
```

## 7. Consultas Avançadas

```python
# Listar todos os materiais de um professor
from educalin.repositories.models import MaterialModel
materiais_prof = MaterialModel.listar_por_autor(conn, professor_id)
print(f"Materiais do professor: {len(materiais_prof)}")

# Listar avaliações de uma turma
avaliacoes = AvaliacaoModel.listar_por_turma(conn, turma_id)
print(f"Avaliações da turma: {len(avaliacoes)}")

# Listar notas de uma avaliação específica
notas = NotaModel.listar_por_avaliacao(conn, avaliacao_id)
print(f"Notas da avaliação: {len(notas)}")

# Listar turmas de um professor
turmas_prof = TurmaModel.listar_por_professor(conn, professor_id)
print(f"Turmas do professor: {len(turmas_prof)}")

# Listar turmas de um aluno
turmas_aluno = TurmaModel.listar_por_aluno(conn, aluno_id)
print(f"Turmas do aluno: {len(turmas_aluno)}")
```

## 8. Validações e Exceções

```python
try:
    # Tentar criar nota com valor maior que o máximo
    NotaModel.criar(conn, aluno_id, avaliacao_id, 15.0)
except ValueError as e:
    print(f"Erro de validação: {e}")

try:
    # Tentar transição de status inválida
    plano = PlanoAcaoModel.buscar_por_id(conn, plano_id)
    plano.atualizar_status(conn, 'rascunho')  # Inválido se já está concluído
except ValueError as e:
    print(f"Erro de transição: {e}")

try:
    # Tentar enviar plano sem materiais
    plano_vazio = PlanoAcaoModel.criar(conn, aluno_id, "Teste", 10)
    plano_vazio_obj = PlanoAcaoModel.buscar_por_id(conn, plano_vazio)
    plano_vazio_obj.atualizar_status(conn, 'enviado')
except ValueError as e:
    print(f"Erro: {e}")
```

## 9. Limpeza e Remoção

```python
# Deletar nota
nota = NotaModel.buscar_por_id(conn, nota_id)
nota.deletar(conn)
print("Nota deletada")

# Deletar meta
meta = MetaModel.buscar_por_id(conn, meta_id)
meta.deletar(conn)
print("Meta deletada")

# Deletar plano de ação (CASCADE: remove materiais associados)
plano = PlanoAcaoModel.buscar_por_id(conn, plano_id)
plano.deletar(conn)
print("Plano deletado")

# Fechar conexão
conn.close()
```

## Observações Importantes

### Polimorfismo (STI)

- **UsuarioModel**: Usa `tipo_usuario` para diferenciar Professor, Coordenador e Aluno
- **MaterialModel**: Usa `tipo_material` para diferenciar PDF, Video e Link
- As consultas retornam automaticamente a subclasse correta

### Foreign Keys

Sempre referenciam a tabela correta:
- `autor_id` → `usuarios.id` (professor)
- `aluno_id` → `usuarios.id` (aluno)
- `turma_id` → `turmas.id`
- `avaliacao_id` → `avaliacoes.id`

### Relacionamentos Many-to-Many

- **Turma ↔ Alunos**: Via tabela `turma_alunos`
- **Plano ↔ Materiais**: Via tabela `plano_materiais` (composição)

### Validações

Todos os modelos validam:
- Tipos de dados
- Valores dentro de limites esperados
- Foreign Keys existentes
- Transições de estado válidas

### Transações

Para operações críticas, use transações:

```python
try:
    conn.execute("BEGIN")
    # ... operações ...
    conn.commit()
except Exception as e:
    conn.rollback()
    print(f"Erro: {e}")
```
