"""
Exemplo de uso do MaterialRepository.

Este arquivo demonstra como usar o MaterialRepository para realizar
operações CRUD com materiais de estudo usando SQL puro.
"""

from educalin.repositories.material_repository import MaterialRepository
from educalin.repositories.usuario_repository import UsuarioRepository
from educalin.repositories.base import get_db
from educalin.repositories.schemas import create_usuarios_table, create_materiais_table


def exemplo_basico():
    """Exemplo básico de uso do MaterialRepository."""
    
    print("=" * 70)
    print("EXEMPLO: Uso básico do MaterialRepository")
    print("=" * 70)
    
    with get_db() as conn:
        # Criar as tabelas necessárias
        create_usuarios_table(conn)
        create_materiais_table(conn)
        
        # Instantiate repositories
        usuario_repo = UsuarioRepository(conn)
        material_repo = MaterialRepository(conn)
        
        # 1. CRIAR um professor (autor dos materiais)
        print("\n1. Criando um professor (autor)...")
        professor_id = usuario_repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'Dr. Carlos Mendes',
            'email': 'carlos@escola.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF_CARLOS_001'
        })
        print(f"   ✓ Professor criado com ID: {professor_id}")
        
        # 2. CRIAR materiais de diferentes tipos
        print("\n2. Criando materiais de estudo...")
        
        # Material PDF
        pdf_id = material_repo.criar({
            'tipo_material': 'pdf',
            'titulo': 'Introdução à Programação Orientada a Objetos',
            'descricao': 'Conceitos fundamentais de POO com exemplos práticos',
            'autor_id': professor_id,
            'topico': 'Programação',
            'num_paginas': 150
        })
        print(f"   ✓ Material PDF criado com ID: {pdf_id}")
        
        # Material Vídeo
        video_id = material_repo.criar({
            'tipo_material': 'video',
            'titulo': 'Tutorial: Implementando Padrões de Design',
            'descricao': 'Demonstração prática de padrões de design em Python',
            'autor_id': professor_id,
            'topico': 'Programação',
            'duracao_segundos': 7200,  # 2 horas
            'codec': 'h264'
        })
        print(f"   ✓ Material Vídeo criado com ID: {video_id}")
        
        # Material Link
        link_id = material_repo.criar({
            'tipo_material': 'link',
            'titulo': 'Documentação Oficial Python',
            'descricao': 'Referência completa da linguagem Python',
            'autor_id': professor_id,
            'topico': 'Referências',
            'url': 'https://docs.python.org/3/',
            'tipo_conteudo': 'documentação'
        })
        print(f"   ✓ Material Link criado com ID: {link_id}")
        
        # 3. BUSCAR materiais
        print("\n3. Buscando materiais...")
        
        material = material_repo.buscar_por_id(pdf_id)
        print(f"   ✓ Material encontrado: '{material.titulo}'")
        print(f"      - Tipo: {material.tipo_material}")
        print(f"      - Tópico: {material.topico}")
        print(f"      - Páginas: {material.num_paginas}")
        
        # 4. LISTAR materiais por professor
        print("\n4. Listando materiais do professor...")
        materiais_prof = material_repo.listar_por_professor(professor_id)
        print(f"   ✓ Total de materiais: {len(materiais_prof)}")
        for mat in materiais_prof:
            print(f"      - {mat.titulo} ({mat.tipo_material})")
        
        # 5. BUSCAR por tópico
        print("\n5. Buscando materiais por tópico 'Programação'...")
        materiais_prog = material_repo.buscar_por_topico('Programação')
        print(f"   ✓ Encontrados {len(materiais_prog)} materiais")
        for mat in materiais_prog:
            print(f"      - {mat.titulo}")
        
        # 6. CONTAR materiais
        print("\n6. Contando materiais...")
        total = material_repo.contar()
        total_pdf = material_repo.contar(tipo_material='pdf')
        total_videos = material_repo.contar(tipo_material='video')
        print(f"   ✓ Total de materiais: {total}")
        print(f"   ✓ PDFs: {total_pdf}")
        print(f"   ✓ Vídeos: {total_videos}")
        
        # 7. ATUALIZAR tópico
        print("\n7. Atualizando tópico de um material...")
        sucesso = material_repo.atualizar_topico(link_id, 'Material de Referência')
        if sucesso:
            material_atualizado = material_repo.buscar_por_id(link_id)
            print(f"   ✓ Tópico atualizado para: '{material_atualizado.topico}'")
        
        # 8. LISTAR todos
        print("\n8. Listando todos os materiais...")
        todos = material_repo.listar_todos()
        print(f"   ✓ Total: {len(todos)} materiais")
        
        # 9. DELETAR um material
        print("\n9. Deletando um material...")
        sucesso = material_repo.excluir(video_id)
        if sucesso:
            print(f"   ✓ Material com ID {video_id} foi deletado")
            materiais_restantes = material_repo.listar_por_professor(professor_id)
            print(f"   ✓ Materiais restantes do professor: {len(materiais_restantes)}")
        
        print("\n" + "=" * 70)
        print("✓ Exemplo concluído com sucesso!")
        print("=" * 70)


def exemplo_context_manager():
    """Exemplo usando context manager."""
    
    print("\n" + "=" * 70)
    print("EXEMPLO: Usando MaterialRepository com context manager")
    print("=" * 70)
    
    with MaterialRepository() as repo:
        print("\n✓ Repository aberto com context manager")
        # O repository irá fechar automaticamente a conexão ao sair do bloco
        pass
    
    print("✓ Repository fechado automaticamente")
    print("=" * 70)


def exemplo_validacoes():
    """Exemplo demonstrando validações."""
    
    print("\n" + "=" * 70)
    print("EXEMPLO: Validações do MaterialRepository")
    print("=" * 70)
    
    with get_db() as conn:
        # Criar  as tabelas necessárias
        create_usuarios_table(conn)
        create_materiais_table(conn)
        
        usuario_repo = UsuarioRepository(conn)
        material_repo = MaterialRepository(conn)
        
        # Criar professor
        prof_id = usuario_repo.criar({
            'tipo_usuario': 'professor',
            'nome': 'Maria Oliveira',
            'email': 'maria@escola.com',
            'senha': 'senha123',
            'registro_funcional': 'PROF002'
        })
        
        # Testar validações
        print("\n1. Tentando criar material com tipo inválido...")
        try:
            material_repo.criar({
                'tipo_material': 'audio',  # tipo inválido
                'titulo': 'Material',
                'descricao': 'Descrição',
                'autor_id': prof_id
            })
        except ValueError as e:
            print(f"   ✓ Validação funcionou: {e}")
        
        print("\n2. Tentando criar PDF sem num_paginas...")
        try:
            material_repo.criar({
                'tipo_material': 'pdf',
                'titulo': 'Material',
                'descricao': 'Descrição',
                'autor_id': prof_id
                # Falta num_paginas
            })
        except ValueError as e:
            print(f"   ✓ Validação funcionou: {e}")
        
        print("\n3. Tentando criar Link com URL inválida...")
        try:
            material_repo.criar({
                'tipo_material': 'link',
                'titulo': 'Material',
                'descricao': 'Descrição',
                'autor_id': prof_id,
                'url': 'exemplo.com',  # Falta protocolo
                'tipo_conteudo': 'artigo'
            })
        except ValueError as e:
            print(f"   ✓ Validação funcionou: {e}")
        
        print("\n4. Tentando buscar material inexistente...")
        material = material_repo.buscar_por_id(999)
        if material is None:
            print("   ✓ Retornou None conforme esperado")
        
        print("\n5. Tentando deletar material inexistente...")
        sucesso = material_repo.excluir(999)
        if not sucesso:
            print("   ✓ Retornou False conforme esperado")
        
        print("\n" + "=" * 70)
        print("✓ Exemplo de validações concluído!")
        print("=" * 70)


if __name__ == '__main__':
    exemplo_basico()
    exemplo_context_manager()
    exemplo_validacoes()
