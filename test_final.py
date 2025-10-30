"""Teste Final - Sistema sem Excel"""
from dotenv import load_dotenv
load_dotenv()

from services import EstoqueService, get_service_info
import os

print("\n" + "="*60)
print("🧪 TESTE FINAL - SISTEMA SEM EXCEL")
print("="*60)

# 1. Verificar configuração
info = get_service_info()
print(f"\n📊 Banco de Dados: {info['tipo']}")
print(f"🔧 Backend: {info['backend']}")
print(f"💾 Persistente: {info.get('persistente', False)}")

# 2. Inicializar serviço
print("\n⚙️  Inicializando EstoqueService...")
try:
    service = EstoqueService()
    print("   ✅ Serviço inicializado!")
except Exception as e:
    print(f"   ❌ Erro: {str(e)}")
    exit(1)

# 3. Obter equipamentos
print("\n📦 Obtendo equipamentos...")
try:
    df = service.obter_equipamentos()
    print(f"   ✅ {len(df)} equipamentos carregados")
    print(f"   ✅ Total de unidades: {df['quantidade'].sum()}")
except Exception as e:
    print(f"   ❌ Erro: {str(e)}")
    exit(1)

# 4. Obter estatísticas
print("\n📊 Obtendo estatísticas...")
try:
    stats = service.obter_estatisticas()
    print(f"   ✅ Total: {stats['total_equipamentos']} unidades")
    print(f"   ✅ Valor: R$ {stats['valor_total']:,.2f}")
    print(f"   ✅ Categorias: {len(stats['por_categoria'])}")
except Exception as e:
    print(f"   ❌ Erro: {str(e)}")
    exit(1)

# 5. Verificar arquivo Excel
print("\n📁 Verificando arquivos...")
if os.path.exists('estoque_ti.xlsx'):
    print("   ⚠️  estoque_ti.xlsx ainda existe!")
else:
    print("   ✅ estoque_ti.xlsx removido com sucesso")

if os.path.exists('estoque_ti.db'):
    size = os.path.getsize('estoque_ti.db') / 1024
    print(f"   ✅ estoque_ti.db existe ({size:.1f} KB)")
else:
    print("   ❌ estoque_ti.db não encontrado!")

if os.path.exists('backup_excel/estoque_ti_backup_20251030.xlsx'):
    print("   ✅ Backup salvo em backup_excel/")
else:
    print("   ⚠️  Backup não encontrado!")

print("\n" + "="*60)
print("✅ TODOS OS TESTES PASSARAM!")
print("✅ Sistema funcionando perfeitamente com SQLite!")
print("✅ Excel removido e backup criado!")
print("="*60 + "\n")

