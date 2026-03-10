"""
Exemplo de uso do UsuarioRepository.

Este arquivo demonstra como usar o UsuarioRepository para realizar
operações com usuários usando SQL puro.
"""

from educalin.repositories.usuario_repository import UsuarioRepository
from educalin.repositories.base import get_db


def exemplo_basico():
    """Exemplo básico de uso do UsuarioRepository."""
    
    print("=" * 60)
    print("EXEMPLO: Uso básico do UsuarioRepository")
    print("=" * 60)
    
    # Usar o repository com context manager
    with get_db() as conn:
        repo = UsuarioRepository(conn)
        
        # 1. CRIAR usuários
        print("\n1. Criando usuários...")
        
        professor_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'João Silva',
            'email': 'joao.silva@escola.com',
            'senha': 'senha_segura_123',
            'registro_funcional': 'PROF001'
        })
        print(f"   ✓ Professor criado com ID: {professor_id}")
        
        coordenador_id = repo.criar({
            'tipo_usuario': 'coordenador',
            'nome': 'Ana Paula Santos',
            'email': 'ana.paula@escola.com',
            'senha': 'senha_coord_456',
            'codigo_coordenacao': 'COORD001'
        })
        print(f"   ✓ Coordenador criado com ID: {coordenador_id}")
        
        aluno_id = repo.criar({
            'tipo_usuario': 'aluno',
            'nome': 'Maria Oliveira',
            'email': 'maria@estudante.com',
            'senha': 'senha_aluno_789',
            'matricula': '2024001'
        })
        print(f"   ✓ Aluno criado com ID: {aluno_id}")
        
        # 2. BUSCAR por ID
        print("\n2. Buscando usuário por ID...")
        professor = repo.buscar_por_id(professor_id)
        print(f"   ✓ Encontrado: {professor.nome} ({professor.__class__.__name__})")
        print(f"     - Email: {professor.email}")
        print(f"     - Registro: {professor.registro_funcional}")
        
        # 3. BUSCAR por Email
        print("\n3. Buscando usuário por email...")
        aluno = repo.buscar_por_email('maria@estudante.com')
        print(f"   ✓ Encontrado: {aluno.nome} ({aluno.__class__.__name__})")
        print(f"     - Matrícula: {aluno.matricula}")
        
        # 4. AUTENTICAR
        print("\n4. Autenticando usuário...")
        usuario_autenticado = repo.autenticar('joao.silva@escola.com', 'senha_segura_123')
        if usuario_autenticado:
            print(f"   ✓ Login bem-sucedido: {usuario_autenticado.nome}")
        else:
            print("   ✗ Falha na autenticação")
        
        # Teste de autenticação com senha errada
        usuario_falha = repo.autenticar('joao.silva@escola.com', 'senha_errada')
        if usuario_falha:
            print("   ✗ Login não deveria ter funcionado!")
        else:
            print("   ✓ Senha incorreta bloqueada corretamente")
        
        # 5. ATUALIZAR
        print("\n5. Atualizando dados do usuário...")
        sucesso = repo.atualizar(professor_id, {
            'nome': 'João Silva Santos',
            'email': 'joao.santos@escola.com'
        })
        if sucesso:
            professor_atualizado = repo.buscar_por_id(professor_id)
            print(f"   ✓ Usuário atualizado:")
            print(f"     - Nome: {professor_atualizado.nome}")
            print(f"     - Email: {professor_atualizado.email}")
        
        # 6. LISTAR todos
        print("\n6. Listando todos os usuários...")
        todos = repo.listar_todos()
        print(f"   ✓ Total de usuários: {len(todos)}")
        for usuario in todos:
            print(f"     - {usuario.nome} ({usuario.tipo_usuario})")
        
        # 7. LISTAR por tipo
        print("\n7. Listando apenas professores...")
        professores = repo.listar_todos(tipo_usuario='professor')
        print(f"   ✓ Total de professores: {len(professores)}")
        for prof in professores:
            print(f"     - {prof.nome} (Registro: {prof.registro_funcional})")
        
        # 8. VERIFICAR se email existe
        print("\n8. Verificando existência de email...")
        existe = repo.existe_email('joao.santos@escola.com')
        print(f"   ✓ Email 'joao.santos@escola.com' existe: {existe}")
        
        existe_falso = repo.existe_email('nao.existe@escola.com')
        print(f"   ✓ Email 'nao.existe@escola.com' existe: {existe_falso}")
        
        # 9. DELETAR
        print("\n9. Deletando usuário...")
        sucesso = repo.deletar(aluno_id)
        if sucesso:
            print(f"   ✓ Aluno com ID {aluno_id} deletado")
            
        # Verificar se foi deletado
        aluno_deletado = repo.buscar_por_id(aluno_id)
        print(f"   ✓ Verificação: usuário existe? {aluno_deletado is not None}")
    
    print("\n" + "=" * 60)
    print("Exemplo concluído com sucesso!")
    print("=" * 60)


def exemplo_tratamento_erros():
    """Exemplo de tratamento de erros."""
    
    print("\n" + "=" * 60)
    print("EXEMPLO: Tratamento de erros")
    print("=" * 60)
    
    with get_db() as conn:
        repo = UsuarioRepository(conn)
        
        # Tentar criar usuário com email inválido
        print("\n1. Tentando criar usuário com email inválido...")
        try:
            repo.criar({
                'tipo_usuario': 'professor',
                'nome': 'Teste',
                'email': 'email_invalido',  # sem @
                'senha': 'senha123',
                'registro_funcional': 'PROF999'
            })
        except ValueError as e:
            print(f"   ✓ Erro capturado: {e}")
        
        # Tentar criar professor sem registro funcional
        print("\n2. Tentando criar professor sem registro funcional...")
        try:
            repo.criar({
                'tipo_usuario': 'professor',
                'nome': 'Teste',
                'email': 'teste@escola.com',
                'senha': 'senha123'
                # falta registro_funcional
            })
        except ValueError as e:
            print(f"   ✓ Erro capturado: {e}")
        
        # Tentar criar com email duplicado
        print("\n3. Tentando criar usuário com email duplicado...")
        repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'Primeiro Usuário',
            'email': 'duplicado@escola.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF100'
        })
        print("   ✓ Primeiro usuário criado")
        
        try:
            repo.criar({
                'tipo_usuario': 'aluno',
                'nome': 'Segundo Usuário',
                'email': 'duplicado@escola.com',  # mesmo email
                'senha': 'senha456',
                'matricula': '2024999'
            })
        except ValueError as e:
            print(f"   ✓ Erro capturado: {e}")
    
    print("\n" + "=" * 60)


def exemplo_context_manager():
    """Exemplo usando repository como context manager."""
    
    print("\n" + "=" * 60)
    print("EXEMPLO: Usando UsuarioRepository como context manager")
    print("=" * 60)
    
    # Repository gerencia a própria conexão
    with UsuarioRepository() as repo:
        usuario_id = repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'Context Manager Test',
            'email': 'context@escola.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF200'
        })
        
        usuario = repo.buscar_por_id(usuario_id)
        print(f"\n   ✓ Usuário criado e recuperado: {usuario.nome}")
    
    # Conexão foi fechada automaticamente após o with
    print("   ✓ Conexão fechada automaticamente")
    print("\n" + "=" * 60)


if __name__ == '__main__':
    # Certifique-se de que o banco está inicializado antes de rodar
    from educalin.repositories.base import init_db
    
    print("Inicializando banco de dados...")
    init_db()
    print()
    
    # Executar exemplos
    exemplo_basico()
    exemplo_tratamento_erros()
    exemplo_context_manager()
    
    print("\n✅ Todos os exemplos executados com sucesso!")
