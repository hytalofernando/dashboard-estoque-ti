"""
Migração Automática: Excel → SQLite
"""

import os
os.environ['DATABASE_URL'] = 'sqlite:///estoque_ti.db'

from services.excel_service import ExcelService
from services.database_service import DatabaseService
from loguru import logger

print("\n" + "="*60)
print("🔄 MIGRANDO DADOS: Excel → SQLite")
print("="*60)

# Carregar dados do Excel
print("\n📂 1/3 - Carregando dados do Excel...")
excel_service = ExcelService()
df_estoque, df_movimentacoes = excel_service.carregar_dados()

print(f"   ✅ {len(df_estoque)} equipamentos encontrados")
print(f"   ✅ {len(df_movimentacoes)} movimentações encontradas")

# Conectar ao SQLite
print("\n🗄️  2/3 - Conectando ao SQLite...")
db_service = DatabaseService()
print("   ✅ Conectado!")

# Migrar equipamentos
print("\n📦 3/3 - Migrando equipamentos...")
sucesso = 0
erro = 0

for idx, row in df_estoque.iterrows():
    try:
        codigo = str(row.get('codigo_produto', '')).strip().upper()
        nome = str(row.get('equipamento', '')).strip()
        categoria = str(row.get('categoria', 'Outro')).strip()
        marca = str(row.get('marca', '')).strip()
        modelo = str(row.get('modelo', '')).strip()
        quantidade = int(row.get('quantidade', 0))
        condicao = str(row.get('condicao', 'Novo')).strip()
        valor_unitario = float(row.get('valor_unitario', 0))
        
        if not codigo or not nome:
            continue
        
        # Verificar se já existe
        existe = db_service.buscar_equipamento(codigo, condicao)
        
        if existe:
            # Atualizar
            if db_service.atualizar_equipamento(codigo, condicao, quantidade):
                sucesso += 1
        else:
            # Adicionar novo
            if db_service.adicionar_equipamento(
                codigo=codigo,
                nome=nome,
                categoria=categoria,
                marca=marca,
                modelo=modelo,
                quantidade=quantidade,
                condicao=condicao,
                valor_unitario=valor_unitario,
                observacoes=""
            ):
                sucesso += 1
                
    except Exception as e:
        erro += 1
        print(f"   ⚠️  Erro na linha {idx+1}: {str(e)}")

print(f"\n   ✅ {sucesso} equipamentos migrados!")
if erro > 0:
    print(f"   ⚠️  {erro} erros")

# Verificar resultado
print("\n📊 Verificando resultado...")
stats = db_service.obter_estatisticas()
print(f"   📦 Total no SQLite: {stats['total_equipamentos']}")
print(f"   💰 Valor total: R$ {stats['valor_total']:,.2f}")

print("\n" + "="*60)
print("✅ MIGRAÇÃO CONCLUÍDA!")
print("="*60)
print("\n💡 Agora reinicie o app:")
print("   streamlit run app.py")
print("\n")

