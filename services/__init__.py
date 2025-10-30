"""
Services Package - Dashboard Estoque TI
Exporta automaticamente o EstoqueService correto (Excel ou PostgreSQL)
"""

from services.service_loader import get_estoque_service, get_service_info

# Carregar o serviço apropriado automaticamente
EstoqueService = get_estoque_service()

# Exportar para que outros módulos possam usar
__all__ = ['EstoqueService', 'get_service_info']
