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
    
    # Configurações visuais expandidas
    THEME_COLORS: Dict[str, str] = {
        # Cores principais
        "primary": "#00d4ff",
        "primary_hover": "#00bde6",
        "primary_light": "#33ddff",
        
        # Cores funcionais
        "success": "#4ade80",
        "success_light": "#6ee7b7",
        "warning": "#fbbf24",
        "warning_light": "#fcd34d",
        "error": "#f87171",
        "error_light": "#fca5a5",
        "info": "#60a5fa",
        "info_light": "#93c5fd",
        
        # Cores de status semânticas
        "status_available": "#10b981",
        "status_unavailable": "#ef4444", 
        "status_maintenance": "#f59e0b",
        "status_pending": "#6366f1",
        
        # Cores de fundo
        "background": "#0e1117",
        "background_secondary": "#262730",
        "background_tertiary": "#404040",
        "background_card": "#1a1d23",
        
        # Cores de texto
        "text_primary": "#ffffff",
        "text_secondary": "#f0f0f0",
        "text_tertiary": "#c1c7cd",
        "text_muted": "#8b949e"
    }
    
    # Paleta de cores para gráficos (harmonizada com o tema)
    CHART_COLORS: List[str] = [
        "#00d4ff",  # Azul ciano principal
        "#4ade80",  # Verde sucesso
        "#fbbf24",  # Amarelo aviso
        "#f87171",  # Vermelho erro
        "#60a5fa",  # Azul informativo
        "#a78bfa",  # Roxo
        "#fb7185",  # Rosa
        "#34d399",  # Verde claro
        "#fcd34d",  # Amarelo claro
        "#f472b6"   # Rosa claro
    ]
    
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