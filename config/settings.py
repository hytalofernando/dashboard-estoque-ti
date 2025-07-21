"""
Configurações centralizadas do Dashboard Estoque TI
"""

from pydantic_settings import BaseSettings
from typing import List, Dict, Any

class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Configurações do arquivo Excel
    EXCEL_FILE: str = "estoque_ti.xlsx"
    SHEET_ESTOQUE: str = "Estoque"
    SHEET_MOVIMENTACOES: str = "Movimentacoes"
    
    # Configurações da página
    PAGE_TITLE: str = "💻 Dashboard Estoque TI"
    PAGE_ICON: str = "💻"
    LAYOUT: str = "wide"
    
    # Categorias de equipamentos
    CATEGORIAS: List[str] = [
        "Notebook", "Monitor", "Impressora", 
        "Rede", "Servidor", "Periférico", "Outro"
    ]
    
    # Mapeamento de prefixos para códigos
    PREFIXOS_CODIGO: Dict[str, str] = {
        "Notebook": "NB",
        "Monitor": "MON", 
        "Impressora": "IMP",
        "Rede": "SW",
        "Servidor": "SRV",
        "Periférico": "PER",
        "Outro": "OUT"
    }
    
    # Configurações de validação
    MAX_QUANTIDADE: int = 1000
    MIN_VALOR: float = 0.01
    MAX_OBSERVACOES: int = 500
    
    # Configurações visuais
    THEME_COLORS: Dict[str, str] = {
        "primary": "#00d4ff",
        "success": "#4ade80", 
        "warning": "#fbbf24",
        "error": "#f87171",
        "background": "#0e1117"
    }
    
    # Configurações de páginas ativas - MODO DASHBOARD ÚNICO
    PAGINAS_ATIVAS: Dict[str, Dict[str, Any]] = {
        "dashboard": {
            "titulo": "📈 Dashboard",
            "ativa": True,
            "descricao": "Visão geral completa do estoque e estatísticas"
        },
        "adicionar": {
            "titulo": "➕ Adicionar Equipamento", 
            "ativa": False,  # ❌ OCULTO
            "descricao": "Adicionar novos equipamentos ao estoque"
        },
        "remover": {
            "titulo": "➖ Remover Equipamento",
            "ativa": False,  # ❌ OCULTO
            "descricao": "Remover equipamentos do estoque"
        },
        "historico": {
            "titulo": "📋 Histórico",
            "ativa": False,  # ❌ OCULTO
            "descricao": "Histórico de movimentações"
        },
        "codigos": {
            "titulo": "🏷️ Códigos",
            "ativa": False,  # ❌ OCULTO
            "descricao": "Gestão de códigos de produtos"
        },
        "configuracoes": {
            "titulo": "⚙️ Configurações",
            "ativa": False,  # ❌ OCULTO
            "descricao": "Configurações da aplicação e páginas"
        }
    }

# Instância global das configurações
settings = Settings() 