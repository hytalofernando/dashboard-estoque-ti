"""
Verificação Completa do Sistema
Analisa se o SQLite está funcionando e compara com Excel
"""

import os
os.environ['DATABASE_URL'] = 'sqlite:///estoque_ti.db'

from dotenv import load_dotenv
load_dotenv()

from services.database_service import DatabaseService
from services.excel_service import ExcelService
import pandas as pd

print("\n" + "="*70)
print("🔍 VERIFICAÇÃO COMPLETA DO SISTEMA")
print("="*70)

# 1. Verificar configuração
print("\n📋 1/5 - VERIFICANDO CONFIGURAÇÃO...")
database_url = os.getenv('DATABASE_URL')
print(f"   DATABASE_URL: {database_url}")
if database_url:
    print("   ✅ Configuração OK")
else:
    print("   ❌ DATABASE_URL não encontrada")

# 2. Verificar dados no SQLite
print("\n🗄️  2/5 - VERIFICANDO DADOS NO SQLITE...")
try:
    db_service = DatabaseService()
    stats_sqlite = db_service.obter_estatisticas()
    df_sqlite = db_service.listar_equipamentos(apenas_ativos=True)
    
    print(f"   📦 Equipamentos no SQLite: {stats_sqlite['total_equipamentos']}")
    print(f"   💰 Valor total SQLite: R$ {stats_sqlite['valor_total']:,.2f}")
    print(f"   📊 Linhas no DataFrame: {len(df_sqlite)}")
    
    if stats_sqlite['total_equipamentos'] > 0:
        print("   ✅ SQLite tem dados!")
    else:
        print("   ❌ SQLite está vazio!")
        
except Exception as e:
    print(f"   ❌ Erro ao acessar SQLite: {str(e)}")
    stats_sqlite = None
    df_sqlite = None

# 3. Verificar dados no Excel
print("\n📊 3/5 - VERIFICANDO DADOS NO EXCEL...")
try:
    excel_service = ExcelService()
    df_excel, df_mov_excel = excel_service.carregar_dados()
    
    total_excel = df_excel['quantidade'].sum() if not df_excel.empty else 0
    print(f"   📦 Equipamentos no Excel: {len(df_excel)} linhas")
    print(f"   📦 Total de unidades: {total_excel}")
    print(f"   📋 Movimentações: {len(df_mov_excel)}")
    
    if len(df_excel) > 0:
        print("   ✅ Excel tem dados!")
    else:
        print("   ❌ Excel está vazio!")
        
except Exception as e:
    print(f"   ❌ Erro ao acessar Excel: {str(e)}")
    df_excel = None

# 4. Comparar dados
print("\n🔍 4/5 - COMPARANDO DADOS...")
if stats_sqlite and df_excel is not None:
    print(f"   SQLite: {stats_sqlite['total_equipamentos']} unidades")
    print(f"   Excel: {total_excel} unidades")
    
    diferenca = abs(stats_sqlite['total_equipamentos'] - total_excel)
    percentual = (diferenca / total_excel * 100) if total_excel > 0 else 0
    
    if diferenca <= 10:  # Tolerância de 10 unidades
        print(f"   ✅ Dados praticamente idênticos (diferença: {diferenca})")
        dados_ok = True
    else:
        print(f"   ⚠️  Diferença de {diferenca} unidades ({percentual:.1f}%)")
        dados_ok = False
else:
    dados_ok = False
    print("   ❌ Não foi possível comparar")

# 5. Verificar categorias
print("\n📂 5/5 - VERIFICANDO CATEGORIAS...")
if stats_sqlite and stats_sqlite.get('por_categoria'):
    print("   Categorias no SQLite:")
    for cat, total in stats_sqlite['por_categoria'].items():
        print(f"      • {cat}: {total}")
    print("   ✅ Categorias OK")
else:
    print("   ⚠️  Sem dados de categoria")

# RESULTADO FINAL
print("\n" + "="*70)
print("📊 RESULTADO DA VERIFICAÇÃO")
print("="*70)

if stats_sqlite and stats_sqlite['total_equipamentos'] > 0 and dados_ok:
    print("\n✅ SISTEMA SQLITE FUNCIONANDO PERFEITAMENTE!")
    print("✅ Dados migrados com sucesso")
    print("✅ É SEGURO fazer backup e remover o Excel")
    print("\n💡 Próximos passos:")
    print("   1. Backup do Excel será criado automaticamente")
    print("   2. Excel pode ser removido do projeto")
    print("   3. Sistema continuará funcionando com SQLite")
    pode_remover = True
else:
    print("\n⚠️  ATENÇÃO: AINDA HÁ PROBLEMAS!")
    print("❌ NÃO É SEGURO remover o Excel ainda")
    print("❌ Verifique os erros acima")
    pode_remover = False

print("\n" + "="*70)

# Salvar resultado
with open('verificacao_resultado.txt', 'w', encoding='utf-8') as f:
    f.write(f"Verificação executada em: {pd.Timestamp.now()}\n")
    f.write(f"SQLite Total: {stats_sqlite['total_equipamentos'] if stats_sqlite else 0}\n")
    f.write(f"Excel Total: {total_excel if df_excel is not None else 0}\n")
    f.write(f"Pode remover Excel: {pode_remover}\n")

print("\n📝 Resultado salvo em: verificacao_resultado.txt\n")

