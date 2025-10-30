"""
Arquivo de Configuração Rápida - Dashboard Estoque TI

👉 EDITE ESTE ARQUIVO para alternar entre Excel e PostgreSQL
"""

# ========================================
# ESCOLHA SEU BANCO DE DADOS AQUI:
# ========================================

# Opção 1: Usar Excel (padrão anterior)
USE_DATABASE = "EXCEL"

# Opção 2: Usar PostgreSQL (recomendado para produção)
# USE_DATABASE = "POSTGRES"

# ========================================
# NÃO EDITE ABAIXO DESTA LINHA
# ========================================

import os

# Exportar configuração para variável de ambiente
os.environ["DATABASE_TYPE"] = USE_DATABASE

print(f"🔧 Configuração: Usando {USE_DATABASE}")

