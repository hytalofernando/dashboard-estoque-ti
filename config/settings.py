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
    
    # Configuração de unicidade de código
    # True = Código deve ser único (mesmo produto em diferentes condições)
    # False = Código + condição deve ser único (produtos diferentes podem ter mesmo código)
    CODIGO_UNICO_OBRIGATORIO: bool = False
    
    # Sistema de cores profissional moderno
    THEME_COLORS: Dict[str, str] = {
        # === CORES PRIMÁRIAS CORPORATIVAS ===
        "primary": "#0066FF",           # Azul corporativo principal
        "primary_hover": "#0052CC",     # Azul hover
        "primary_light": "#4D94FF",     # Azul claro
        "primary_dark": "#003D99",      # Azul escuro
        
        # === CORES FUNCIONAIS PROFISSIONAIS ===
        "success": "#00C851",           # Verde sucesso vibrante
        "success_hover": "#00A142",     # Verde hover
        "success_light": "#4DD678",     # Verde claro
        
        "warning": "#FFB300",           # Laranja profissional
        "warning_hover": "#E69A00",     # Laranja hover  
        "warning_light": "#FFCC4D",     # Laranja claro
        
        "error": "#FF3547",             # Vermelho suave
        "error_hover": "#E6253A",       # Vermelho hover
        "error_light": "#FF6B7A",       # Vermelho claro
        
        "info": "#17A2B8",              # Azul informativo
        "info_hover": "#138496",        # Azul info hover
        "info_light": "#5DBECD",        # Azul info claro
        
        # === CORES DE STATUS SEMÂNTICAS ===
        "status_available": "#00C851",   # Verde disponível
        "status_unavailable": "#FF3547", # Vermelho indisponível
        "status_maintenance": "#FFB300", # Laranja manutenção
        "status_pending": "#6C5CE7",     # Roxo pendente
        "status_low_stock": "#FD79A8",   # Rosa estoque baixo
        
        # === SISTEMA DE NEUTROS MODERNOS ===
        "gray_50": "#F8FAFC",           # Cinza muito claro
        "gray_100": "#F1F5F9",          # Cinza claro
        "gray_200": "#E2E8F0",          # Cinza médio claro
        "gray_300": "#CBD5E1",          # Cinza médio
        "gray_400": "#94A3B8",          # Cinza
        "gray_500": "#64748B",          # Cinza escuro
        "gray_600": "#475569",          # Cinza muito escuro
        "gray_700": "#334155",          # Cinza quase preto
        "gray_800": "#1E293B",          # Cinza preto
        "gray_900": "#0F172A",          # Preto azulado
        
        # === CORES DE FUNDO DARK THEME MELHORADAS ===
        "background": "#0F172A",         # Fundo principal (gray-900)
        "background_secondary": "#1E293B", # Fundo secundário (gray-800)
        "background_tertiary": "#475569",  # Fundo terciário - mais claro para inputs
        "background_card": "#1E293B",      # Fundo de cards
        "background_sidebar": "#0F172A",   # Fundo da sidebar
        "background_input": "#334155",     # Fundo específico para inputs
        "background_input_focus": "#475569", # Fundo de inputs em foco
        
        # === CORES DE TEXTO COM MELHOR CONTRASTE ===
        "text_primary": "#FFFFFF",       # Texto principal - branco puro
        "text_secondary": "#F1F5F9",     # Texto secundário - cinza muito claro
        "text_tertiary": "#CBD5E1",      # Texto terciário - cinza claro (melhor contraste)
        "text_muted": "#94A3B8",         # Texto discreto - mantido
        "text_inverse": "#0F172A",       # Texto em fundos claros
        
        # === CORES DE DESTAQUE ===
        "accent_purple": "#6C5CE7",      # Roxo destaque
        "accent_pink": "#FD79A8",        # Rosa destaque
        "accent_cyan": "#00CEC9",        # Ciano destaque
        "accent_orange": "#FF7675",      # Laranja destaque
        
        # === CORES DE GRÁFICOS ===
        "chart_primary": "#0066FF",      # Azul principal
        "chart_secondary": "#00C851",    # Verde
        "chart_tertiary": "#FFB300",     # Laranja
        "chart_quaternary": "#6C5CE7",   # Roxo
        "chart_quinary": "#FF3547",      # Vermelho
    }
    
    # Paleta de cores para gráficos profissional
    CHART_COLORS: List[str] = [
        "#0066FF",  # Azul corporativo principal
        "#00C851",  # Verde sucesso
        "#FFB300",  # Laranja profissional
        "#6C5CE7",  # Roxo moderno
        "#FF3547",  # Vermelho suave
        "#17A2B8",  # Azul informativo
        "#FD79A8",  # Rosa destaque
        "#00CEC9",  # Ciano destaque
        "#FF7675",  # Laranja destaque
        "#74B9FF",  # Azul claro
        "#A29BFE",  # Roxo claro
        "#6C5CE7"   # Roxo principal
    ]
    
    # Configurações de páginas ativas - SISTEMA COMPLETO
    PAGINAS_ATIVAS: Dict[str, Dict[str, Any]] = {
        "dashboard": {
            "titulo": "📈 Dashboard",
            "ativa": True,
            "descricao": "Visão geral completa do estoque e estatísticas"
        },
        "adicionar": {
            "titulo": "➕ Adicionar Equipamento", 
            "ativa": True,  # ✅ ATIVO
            "descricao": "Adicionar novos equipamentos ao estoque"
        },
        "remover": {
            "titulo": "➖ Remover Equipamento",
            "ativa": True,  # ✅ ATIVO
            "descricao": "Remover equipamentos do estoque"
        },
        "historico": {
            "titulo": "📋 Histórico",
            "ativa": True,  # ✅ ATIVO
            "descricao": "Histórico de movimentações"
        },
        "codigos": {
            "titulo": "🏷️ Códigos",
            "ativa": True,  # ✅ ATIVO
            "descricao": "Gestão de códigos de produtos"
        },
        "configuracoes": {
            "titulo": "⚙️ Configurações",
            "ativa": True,  # ✅ ATIVO
            "descricao": "Configurações da aplicação e páginas"
        }
    }

# Instância global das configurações
settings = Settings() 