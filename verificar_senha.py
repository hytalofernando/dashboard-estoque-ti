"""Verificar senhas configuradas"""
import os
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*60)
print("🔐 SENHAS CONFIGURADAS NO SISTEMA")
print("="*60)

admin_pass = os.getenv('ADMIN_PASSWORD', 'NÃO CONFIGURADA')
viewer_pass = os.getenv('VIEWER_PASSWORD', 'NÃO CONFIGURADA')

print("\n👑 ADMINISTRADOR:")
print(f"   Usuário: admin")
print(f"   Senha: {admin_pass}")

print("\n👀 VISUALIZADOR:")
print(f"   Usuário: visualizador")
print(f"   Senha: {viewer_pass}")

print("\n" + "="*60)
print("💡 DICA: Use exatamente essas senhas para fazer login!")
print("="*60 + "\n")



