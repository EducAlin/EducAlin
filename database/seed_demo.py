"""
Script de seed para popular o banco de dados com dados de demonstração.

Cria usuários predefinidos para facilitar testes e demonstrações:
- Professor: professor@educalin.com / senha123
- Aluno: aluno@educalin.com / senha123
- Coordenador: coordenador@educalin.com / senha123

Também cria turmas, avaliações, notas e planos de ação de exemplo.
"""

import sys
import sqlite3
from pathlib import Path

# Adicionar o diretório src ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from educalin.repositories.base import get_connection, init_db
from educalin.repositories.usuario_repository import UsuarioRepository
from educalin.repositories.turma_repository import TurmaRepository
from educalin.repositories.avaliacao_repository import AvaliacaoRepository
from educalin.repositories.plano_acao_repository import PlanoAcaoRepository
from educalin.utils.security import hash_senha
from datetime import date, timedelta


def limpar_dados_demo(conn):
    """Remove dados de demonstração anteriores."""
    print("Limpando dados de demonstração anteriores...")
    
    cursor = conn.cursor()
    
    # Desabilitar foreign keys temporariamente
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # Deletar em ordem reversa de dependências
    # Tabelas com coluna 'id'
    tabelas_com_id = ["notas", "avaliacoes", "planos_acao", "turmas", "usuarios"]
    for tabela in tabelas_com_id:
        try:
            cursor.execute(f"DELETE FROM {tabela} WHERE id >= 1000")
        except sqlite3.OperationalError:
            pass
            
    # Tabelas sem coluna 'id'
    try:
        cursor.execute("DELETE FROM turma_alunos WHERE turma_id >= 1000")
    except sqlite3.OperationalError:
        pass
    
    # Reabilitar foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")
    
    conn.commit()
    print("Dados anteriores removidos")


def criar_usuarios_demo(conn):
    """Cria os 3 usuários predefinidos para demonstração."""
    print("\nCriando usuários de demonstração...")
    
    repo = UsuarioRepository(conn)
    
    usuarios = [
        {
            "id": 1000,
            "nome": "Prof. João Silva",
            "email": "professor@educalin.com",
            "senha_hash": hash_senha("senha123"),
            "tipo_usuario": "professor",
            "registro_funcional": "PROF2024001"
        },
        {
            "id": 1001,
            "nome": "Maria Santos",
            "email": "aluno@educalin.com",
            "senha_hash": hash_senha("senha123"),
            "tipo_usuario": "aluno",
            "matricula": "2024001"
        },
        {
            "id": 1002,
            "nome": "Dr. Carlos Coordenador",
            "email": "coordenador@educalin.com",
            "senha_hash": hash_senha("senha123"),
            "tipo_usuario": "coordenador",
            "codigo_coordenacao": "COORD001"
        },
        # Alunos adicionais para popular as turmas
        {
            "id": 1003,
            "nome": "Pedro Oliveira",
            "email": "pedro.oliveira@educalin.com",
            "senha_hash": hash_senha("senha123"),
            "tipo_usuario": "aluno",
            "matricula": "2024002"
        },
        {
            "id": 1004,
            "nome": "Ana Costa",
            "email": "ana.costa@educalin.com",
            "senha_hash": hash_senha("senha123"),
            "tipo_usuario": "aluno",
            "matricula": "2024003"
        },
        {
            "id": 1005,
            "nome": "Lucas Ferreira",
            "email": "lucas.ferreira@educalin.com",
            "senha_hash": hash_senha("senha123"),
            "tipo_usuario": "aluno",
            "matricula": "2024004"
        },
    ]
    
    cursor = conn.cursor()
    for usuario in usuarios:
        cursor.execute("""
            INSERT INTO usuarios (id, tipo_usuario, nome, email, senha_hash, registro_funcional, codigo_coordenacao, matricula)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            usuario["id"],
            usuario["tipo_usuario"],
            usuario["nome"],
            usuario["email"],
            usuario["senha_hash"],
            usuario.get("registro_funcional"),
            usuario.get("codigo_coordenacao"),
            usuario.get("matricula")
        ))
        print(f"  {usuario['nome']} ({usuario['tipo_usuario']}) - {usuario['email']}")
    
    conn.commit()
    print(f"\n{len(usuarios)} usuários criados com sucesso!")
    return usuarios


def criar_turmas_demo(conn, professor_id):
    """Cria turmas de demonstração."""
    print("\nCriando turmas de demonstração...")
    
    repo = TurmaRepository(conn)
    
    turmas = [
        {
            "id": 1000,
            "codigo": "MAT101",
            "disciplina": "Matemática I",
            "semestre": "2026.1",
            "professor_id": professor_id
        },
        {
            "id": 1001,
            "codigo": "POO202",
            "disciplina": "Programação Orientada a Objetos",
            "semestre": "2026.1",
            "professor_id": professor_id
        },
        {
            "id": 1002,
            "codigo": "FIS101",
            "disciplina": "Física I",
            "semestre": "2026.1",
            "professor_id": professor_id
        },
    ]
    
    cursor = conn.cursor()
    for turma in turmas:
        cursor.execute("""
            INSERT INTO turmas (id, codigo, disciplina, semestre, professor_id)
            VALUES (?, ?, ?, ?, ?)
        """, (turma["id"], turma["codigo"], turma["disciplina"], 
              turma["semestre"], turma["professor_id"]))
        print(f"  {turma['codigo']} - {turma['disciplina']}")
    
    conn.commit()
    print(f"\n{len(turmas)} turmas criadas!")
    return turmas


def matricular_alunos(conn, turmas, alunos_ids):
    """Matricula alunos nas turmas."""
    print("\nMatriculando alunos nas turmas...")
    
    cursor = conn.cursor()
    
    # Matricular todos os alunos em todas as turmas
    for turma in turmas:
        for aluno_id in alunos_ids:
            cursor.execute("""
                INSERT INTO turma_alunos (turma_id, aluno_id, data_matricula)
                VALUES (?, ?, ?)
            """, (turma["id"], aluno_id, date.today().isoformat()))
            
        print(f"  {len(alunos_ids)} alunos matriculados em {turma['codigo']}")
    
    conn.commit()
    print("\nMatrículas concluídas!")


def criar_avaliacoes_demo(conn, turmas):
    """Cria avaliações para as turmas."""
    print("\nCriando avaliações...")
    
    cursor = conn.cursor()
    avaliacoes = []
    avaliacao_id = 1000
    
    for turma in turmas:
        # Criar 3 avaliações por turma
        for i, (titulo, dias_atras) in enumerate([
            ("Prova 1", 30),
            ("Trabalho Prático", 15),
            ("Prova 2", 5)
        ], 1):
            data_avaliacao = date.today() - timedelta(days=dias_atras)
            
            cursor.execute("""
                INSERT INTO avaliacoes (id, titulo, data, valor_maximo, peso, turma_id, topico)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (avaliacao_id, titulo, data_avaliacao.isoformat(), 
                  10.0, 0.33, turma["id"], f"Módulo {i}"))
            
            avaliacoes.append({
                "id": avaliacao_id,
                "turma_id": turma["id"],
                "titulo": titulo
            })
            
            print(f"  {turma['codigo']} - {titulo}")
            avaliacao_id += 1
    
    conn.commit()
    print(f"\n{len(avaliacoes)} avaliações criadas!")
    return avaliacoes


def criar_notas_demo(conn, avaliacoes, alunos_ids):
    """Cria notas para os alunos nas avaliações."""
    print("\nRegistrando notas...")
    
    import random
    
    cursor = conn.cursor()
    nota_id = 1000
    total_notas = 0
    
    # Definir desempenho base para cada aluno
    desempenho = {
        1001: 8.5,  # Maria (aluno principal) - bom desempenho
        1003: 7.0,  # Pedro - desempenho médio
        1004: 6.0,  # Ana - dificuldades
        1005: 9.0,  # Lucas - excelente desempenho
    }
    
    for avaliacao in avaliacoes:
        for aluno_id in alunos_ids:
            # Gerar nota com variação aleatória
            base = desempenho[aluno_id]
            variacao = random.uniform(-1.5, 1.5)
            nota = max(0, min(10, base + variacao))
            
            cursor.execute("""
                INSERT INTO notas (id, aluno_id, avaliacao_id, valor)
                VALUES (?, ?, ?, ?)
            """, (nota_id, aluno_id, avaliacao["id"], round(nota, 2)))
            
            nota_id += 1
            total_notas += 1
    
    conn.commit()
    print(f"{total_notas} notas registradas!")


def criar_planos_acao_demo(conn, alunos_ids):
    """Cria alguns planos de ação de exemplo."""
    print("\nCriando planos de ação...")
    
    cursor = conn.cursor()
    
    planos = [
        {
            "id": 1000,
            "aluno_id": 1001,  # Maria
            "objetivo": "Melhorar desempenho em Física",
            "status": "em_andamento",
            "data_limite": (date.today() + timedelta(days=30)).isoformat(),
            "observacoes": "Focar em exercícios de cinemática"
        },
        {
            "id": 1001,
            "aluno_id": 1004,  # Ana
            "objetivo": "Reforçar base de Matemática",
            "status": "em_andamento",
            "data_limite": (date.today() + timedelta(days=45)).isoformat(),
            "observacoes": "Revisar álgebra básica e funções"
        },
        {
            "id": 1002,
            "aluno_id": 1003,  # Pedro
            "objetivo": "Dominar conceitos de POO",
            "status": "enviado",
            "data_limite": (date.today() + timedelta(days=20)).isoformat(),
            "observacoes": "Praticar herança e polimorfismo"
        },
    ]
    
    for plano in planos:
        cursor.execute("""
            INSERT INTO planos_acao 
            (id, aluno_id, objetivo, status, data_criacao, data_limite, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (plano["id"], plano["aluno_id"], plano["objetivo"], 
              plano["status"], date.today().isoformat(), 
              plano["data_limite"], plano["observacoes"]))
        
        print(f"  Plano para aluno {plano['aluno_id']}: {plano['objetivo']}")
    
    conn.commit()
    print(f"\n{len(planos)} planos de ação criados!")


def main():
    """Executa o seed completo."""
    print("=" * 60)
    print("SEED DE DADOS DE DEMONSTRAÇÃO - EducAlin")
    print("=" * 60)
    
    try:
        # Garantir que o banco existe e as tabelas estão criadas
        init_db()
        
        conn = get_connection()
        
        # Limpar dados anteriores
        limpar_dados_demo(conn)
        
        # Criar usuários
        usuarios = criar_usuarios_demo(conn)
        
        # IDs dos usuários criados
        professor_id = 1000
        alunos_ids = [1001, 1003, 1004, 1005]
        
        # Criar turmas
        turmas = criar_turmas_demo(conn, professor_id)
        
        # Matricular alunos
        matricular_alunos(conn, turmas, alunos_ids)
        
        # Criar avaliações
        avaliacoes = criar_avaliacoes_demo(conn, turmas)
        
        # Registrar notas
        criar_notas_demo(conn, avaliacoes, alunos_ids)
        
        # Criar planos de ação
        criar_planos_acao_demo(conn, alunos_ids)
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("SEED CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("\nCREDENCIAIS PARA LOGIN:\n")
        print("Professor:")
        print("   Email: professor@educalin.com")
        print("   Senha: senha123")
        print("\nAluno:")
        print("   Email: aluno@educalin.com")
        print("   Senha: senha123")
        print("\nCoordenador:")
        print("   Email: coordenador@educalin.com")
        print("   Senha: senha123")
        print("\n" + "=" * 60)
        print("Acesse: http://localhost:8000/login")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\nERRO ao executar seed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
