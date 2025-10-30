"""Verificar dados no SQLite"""
import os
os.environ['DATABASE_URL'] = 'sqlite:///estoque_ti.db'

from models.database_models import db_connection
from services.database_service import DatabaseService

db = DatabaseService()
stats = db.obter_estatisticas()

print("\n" + "="*60)
print("🗄️ DADOS NO SQLITE (estoque_ti.db)")
print("="*60)
print(f"\n📦 Total de equipamentos: {stats['total_equipamentos']}")
print(f"💰 Valor total: R$ {stats['valor_total']:,.2f}")

if stats['por_categoria']:
    print("\n📂 Por Categoria:")
    for cat, total in stats['por_categoria'].items():
        print(f"   • {cat}: {total}")

if stats['por_condicao']:
    print("\n🏷️ Por Condição:")
    for cond, total in stats['por_condicao'].items():
        print(f"   • {cond}: {total}")

print("\n" + "="*60 + "\n")

