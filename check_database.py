"""Script para verificar qual banco de dados está sendo usado"""
import os
from services import get_service_info

info = get_service_info()

print("\n" + "="*60)
print("🔍 BANCO DE DADOS ATUAL")
print("="*60)
print(f"\n📊 Tipo: {info['tipo']}")
print(f"🔧 Backend: {info['backend']}")
print(f"💾 Persistente: {info.get('persistente', False)}")

if info['tipo'] == 'Excel':
    print(f"📁 Arquivo: {info.get('arquivo', 'estoque_ti.xlsx')}")
    print("\n⚠️  Usando Excel - Dados temporários!")
else:
    print(f"🔗 URL: {info.get('url', 'N/A')}")
    print("\n✅ Usando banco persistente!")

print("\n" + "="*60)

# Verificar arquivos
print("\n📂 Arquivos no diretório:")
if os.path.exists('estoque_ti.xlsx'):
    size = os.path.getsize('estoque_ti.xlsx') / 1024
    print(f"   ✅ estoque_ti.xlsx ({size:.1f} KB)")
else:
    print(f"   ❌ estoque_ti.xlsx não encontrado")

if os.path.exists('estoque_ti.db'):
    size = os.path.getsize('estoque_ti.db') / 1024
    print(f"   ✅ estoque_ti.db ({size:.1f} KB)")
else:
    print(f"   ❌ estoque_ti.db não existe")

# Verificar DATABASE_URL
database_url = os.getenv('DATABASE_URL')
print(f"\n🔑 DATABASE_URL: {'Configurada' if database_url else '❌ Não configurada'}")
if database_url:
    # Ofuscar senha
    display_url = database_url
    if "@" in display_url and ":" in display_url:
        parts = display_url.split("@")
        user_pass = parts[0].split("://")
        if len(user_pass) > 1 and ":" in user_pass[1]:
            user = user_pass[1].split(":")[0]
            display_url = f"{user_pass[0]}://{user}:****@{parts[1]}"
    print(f"   URL: {display_url}")

print("\n" + "="*60 + "\n")

