"""
Sistema de CSS Moderno e Profissional para Dashboard Estoque TI
Design System baseado em variáveis CSS e componentes reutilizáveis
"""

from config.settings import settings

def get_modern_css() -> str:
    """
    Retorna CSS moderno e profissional baseado no design system
    
    Returns:
        String com CSS completo
    """
    
    colors = settings.THEME_COLORS
    
    css = f"""
    <style>
    /* ===== DESIGN SYSTEM PROFISSIONAL ===== */
    :root {{
        /* === CORES PRIMÁRIAS === */
        --primary: {colors['primary']};
        --primary-hover: {colors['primary_hover']};
        --primary-light: {colors['primary_light']};
        --primary-dark: {colors['primary_dark']};
        
        /* === CORES FUNCIONAIS === */
        --success: {colors['success']};
        --success-hover: {colors['success_hover']};
        --success-light: {colors['success_light']};
        
        --warning: {colors['warning']};
        --warning-hover: {colors['warning_hover']};
        --warning-light: {colors['warning_light']};
        
        --error: {colors['error']};
        --error-hover: {colors['error_hover']};
        --error-light: {colors['error_light']};
        
        --info: {colors['info']};
        --info-hover: {colors['info_hover']};
        --info-light: {colors['info_light']};
        
        /* === SISTEMA DE NEUTROS === */
        --gray-50: {colors['gray_50']};
        --gray-100: {colors['gray_100']};
        --gray-200: {colors['gray_200']};
        --gray-300: {colors['gray_300']};
        --gray-400: {colors['gray_400']};
        --gray-500: {colors['gray_500']};
        --gray-600: {colors['gray_600']};
        --gray-700: {colors['gray_700']};
        --gray-800: {colors['gray_800']};
        --gray-900: {colors['gray_900']};
        
        /* === CORES DE FUNDO === */
        --bg-primary: {colors['background']};
        --bg-secondary: {colors['background_secondary']};
        --bg-tertiary: {colors['background_tertiary']};
        --bg-card: {colors['background_card']};
        --bg-sidebar: {colors['background_sidebar']};
        
        /* === CORES DE TEXTO === */
        --text-primary: {colors['text_primary']};
        --text-secondary: {colors['text_secondary']};
        --text-tertiary: {colors['text_tertiary']};
        --text-muted: {colors['text_muted']};
        --text-inverse: {colors['text_inverse']};
        
        /* === CORES DE STATUS === */
        --status-available: {colors['status_available']};
        --status-unavailable: {colors['status_unavailable']};
        --status-maintenance: {colors['status_maintenance']};
        --status-pending: {colors['status_pending']};
        --status-low-stock: {colors['status_low_stock']};
        
        /* === CORES DE DESTAQUE === */
        --accent-purple: {colors['accent_purple']};
        --accent-pink: {colors['accent_pink']};
        --accent-cyan: {colors['accent_cyan']};
        --accent-orange: {colors['accent_orange']};
        
        /* === TIPOGRAFIA === */
        --font-primary: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        --font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
        
        --text-xs: 0.75rem;      /* 12px */
        --text-sm: 0.875rem;     /* 14px */
        --text-base: 1rem;       /* 16px */
        --text-lg: 1.125rem;     /* 18px */
        --text-xl: 1.25rem;      /* 20px */
        --text-2xl: 1.5rem;      /* 24px */
        --text-3xl: 1.875rem;    /* 30px */
        --text-4xl: 2.25rem;     /* 36px */
        
        /* === ESPAÇAMENTO === */
        --space-1: 0.25rem;      /* 4px */
        --space-2: 0.5rem;       /* 8px */
        --space-3: 0.75rem;      /* 12px */
        --space-4: 1rem;         /* 16px */
        --space-5: 1.25rem;      /* 20px */
        --space-6: 1.5rem;       /* 24px */
        --space-8: 2rem;         /* 32px */
        --space-10: 2.5rem;      /* 40px */
        --space-12: 3rem;        /* 48px */
        --space-16: 4rem;        /* 64px */
        
        /* === PROPRIEDADES VISUAIS === */
        --border-radius: 0.75rem;    /* 12px */
        --border-radius-sm: 0.5rem;  /* 8px */
        --border-radius-lg: 1rem;    /* 16px */
        --border-radius-xl: 1.5rem;  /* 24px */
        
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        
        /* === GRADIENTES === */
        --gradient-primary: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
        --gradient-success: linear-gradient(135deg, var(--success) 0%, var(--success-light) 100%);
        --gradient-warning: linear-gradient(135deg, var(--warning) 0%, var(--warning-light) 100%);
        --gradient-error: linear-gradient(135deg, var(--error) 0%, var(--error-light) 100%);
        --gradient-bg: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 100%);
        
        /* === TRANSIÇÕES === */
        --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-normal: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    
    /* ===== RESET E BASE ===== */
    * {{
        box-sizing: border-box;
    }}
    
    /* ===== LAYOUT PRINCIPAL ===== */
    .stApp {{
        background: var(--gradient-bg);
        font-family: var(--font-primary);
        color: var(--text-primary);
        line-height: 1.6;
    }}
    
    /* ===== TIPOGRAFIA ===== */
    .main-header {{
        font-size: var(--text-4xl);
        font-weight: 800;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: var(--space-8);
        letter-spacing: -0.025em;
        line-height: 1.2;
    }}
    
    .section-header {{
        font-size: var(--text-2xl);
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: var(--space-4);
        display: flex;
        align-items: center;
        gap: var(--space-2);
    }}
    
    .section-subheader {{
        font-size: var(--text-lg);
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: var(--space-3);
    }}
    
    /* ===== CARDS E CONTAINERS ===== */
    .metric-card {{
        background: var(--bg-card);
        border-radius: var(--border-radius);
        padding: var(--space-6);
        box-shadow: var(--shadow-md);
        border: 1px solid var(--gray-700);
        transition: all var(--transition-normal);
        position: relative;
        overflow: hidden;
    }}
    
    .metric-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--gradient-primary);
        transform: scaleX(0);
        transform-origin: left;
        transition: transform var(--transition-normal);
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary);
    }}
    
    .metric-card:hover::before {{
        transform: scaleX(1);
    }}
    
    .info-card {{
        background: var(--bg-secondary);
        border-radius: var(--border-radius);
        padding: var(--space-4);
        border-left: 4px solid var(--info);
        margin: var(--space-4) 0;
    }}
    
    .success-card {{
        background: rgba(0, 200, 81, 0.1);
        border-radius: var(--border-radius);
        padding: var(--space-4);
        border-left: 4px solid var(--success);
        color: var(--success-light);
    }}
    
    .warning-card {{
        background: rgba(255, 179, 0, 0.1);
        border-radius: var(--border-radius);
        padding: var(--space-4);
        border-left: 4px solid var(--warning);
        color: var(--warning-light);
    }}
    
    .error-card {{
        background: rgba(255, 53, 71, 0.1);
        border-radius: var(--border-radius);
        padding: var(--space-4);
        border-left: 4px solid var(--error);
        color: var(--error-light);
    }}
    
    /* ===== COMPONENTES STREAMLIT ===== */
    
    /* Sidebar */
    .css-1d391kg {{
        background: var(--bg-sidebar) !important;
        border-right: 1px solid var(--gray-700);
    }}
    
    /* Métricas */
    [data-testid="metric-container"] {{
        background: var(--bg-card);
        border-radius: var(--border-radius);
        padding: var(--space-4);
        box-shadow: var(--shadow);
        border: 1px solid var(--gray-700);
        transition: all var(--transition-normal);
    }}
    
    [data-testid="metric-container"]:hover {{
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
        border-color: var(--primary);
    }}
    
    /* Botões */
    .stButton > button {{
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius) !important;
        padding: var(--space-3) var(--space-6) !important;
        font-weight: 600 !important;
        font-size: var(--text-sm) !important;
        transition: all var(--transition-normal) !important;
        box-shadow: var(--shadow) !important;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
        filter: brightness(1.1) !important;
    }}
    
    .stButton > button:active {{
        transform: translateY(0) !important;
    }}
    
    /* Botão secundário */
    .stButton.secondary > button {{
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--gray-600) !important;
    }}
    
    .stButton.secondary > button:hover {{
        background: var(--gray-600) !important;
        border-color: var(--gray-500) !important;
    }}
    
    /* Inputs */
    .stTextInput > div > div > input {{
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--gray-600) !important;
        border-radius: var(--border-radius) !important;
        color: var(--text-primary) !important;
        padding: var(--space-3) !important;
        transition: all var(--transition-normal) !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.1) !important;
    }}
    
    .stSelectbox > div > div > select {{
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--gray-600) !important;
        border-radius: var(--border-radius) !important;
        color: var(--text-primary) !important;
    }}
    
    /* Tabelas */
    .dataframe {{
        background: var(--bg-card) !important;
        border-radius: var(--border-radius) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow) !important;
    }}
    
    .dataframe th {{
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        padding: var(--space-3) !important;
        border-bottom: 1px solid var(--gray-600) !important;
    }}
    
    .dataframe td {{
        background: var(--bg-card) !important;
        color: var(--text-secondary) !important;
        padding: var(--space-3) !important;
        border-bottom: 1px solid var(--gray-700) !important;
    }}
    
    .dataframe tr:hover td {{
        background: var(--bg-tertiary) !important;
    }}
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        gap: var(--space-2);
        background: var(--bg-secondary);
        border-radius: var(--border-radius);
        padding: var(--space-1);
    }}
    
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        border-radius: var(--border-radius-sm) !important;
        color: var(--text-tertiary) !important;
        font-weight: 500 !important;
        transition: all var(--transition-normal) !important;
        padding: var(--space-2) var(--space-4) !important;
    }}
    
    .stTabs [data-baseweb="tab"]:hover {{
        background: var(--bg-tertiary) !important;
        color: var(--text-secondary) !important;
    }}
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        background: var(--primary) !important;
        color: white !important;
    }}
    
    /* Alertas */
    .stAlert {{
        border-radius: var(--border-radius) !important;
        border: none !important;
        padding: var(--space-4) !important;
    }}
    
    .stSuccess {{
        background: rgba(0, 200, 81, 0.1) !important;
        color: var(--success-light) !important;
        border-left: 4px solid var(--success) !important;
    }}
    
    .stWarning {{
        background: rgba(255, 179, 0, 0.1) !important;
        color: var(--warning-light) !important;
        border-left: 4px solid var(--warning) !important;
    }}
    
    .stError {{
        background: rgba(255, 53, 71, 0.1) !important;
        color: var(--error-light) !important;
        border-left: 4px solid var(--error) !important;
    }}
    
    .stInfo {{
        background: rgba(23, 162, 184, 0.1) !important;
        color: var(--info-light) !important;
        border-left: 4px solid var(--info) !important;
    }}
    
    /* ===== CLASSES UTILITÁRIAS ===== */
    .text-center {{ text-align: center; }}
    .text-right {{ text-align: right; }}
    .font-bold {{ font-weight: 700; }}
    .font-semibold {{ font-weight: 600; }}
    .font-medium {{ font-weight: 500; }}
    
    .text-primary {{ color: var(--text-primary); }}
    .text-secondary {{ color: var(--text-secondary); }}
    .text-muted {{ color: var(--text-muted); }}
    
    .bg-primary {{ background-color: var(--primary); }}
    .bg-success {{ background-color: var(--success); }}
    .bg-warning {{ background-color: var(--warning); }}
    .bg-error {{ background-color: var(--error); }}
    
    .border-primary {{ border-color: var(--primary); }}
    .border-success {{ border-color: var(--success); }}
    .border-warning {{ border-color: var(--warning); }}
    .border-error {{ border-color: var(--error); }}
    
    .rounded {{ border-radius: var(--border-radius); }}
    .rounded-sm {{ border-radius: var(--border-radius-sm); }}
    .rounded-lg {{ border-radius: var(--border-radius-lg); }}
    
    .shadow {{ box-shadow: var(--shadow); }}
    .shadow-md {{ box-shadow: var(--shadow-md); }}
    .shadow-lg {{ box-shadow: var(--shadow-lg); }}
    
    .transition {{ transition: all var(--transition-normal); }}
    .transition-fast {{ transition: all var(--transition-fast); }}
    
    /* ===== RESPONSIVIDADE ===== */
    @media (max-width: 768px) {{
        .main-header {{
            font-size: var(--text-3xl);
        }}
        
        .metric-card {{
            padding: var(--space-4);
        }}
        
        .section-header {{
            font-size: var(--text-xl);
        }}
    }}
    
    /* ===== ANIMAÇÕES ===== */
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    
    @keyframes slideIn {{
        from {{ opacity: 0; transform: translateX(-20px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}
    
    .animate-fade-in {{ animation: fadeIn 0.5s ease-out; }}
    .animate-slide-in {{ animation: slideIn 0.3s ease-out; }}
    .animate-pulse {{ animation: pulse 2s infinite; }}
    
    /* ===== ACESSIBILIDADE ===== */
    .focus-visible:focus {{
        outline: 2px solid var(--primary) !important;
        outline-offset: 2px !important;
    }}
    
    .sr-only {{
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        padding: 0 !important;
        margin: -1px !important;
        overflow: hidden !important;
        clip: rect(0, 0, 0, 0) !important;
        white-space: nowrap !important;
        border: 0 !important;
    }}
    
    /* ===== DARK MODE OTIMIZADO ===== */
    @media (prefers-color-scheme: dark) {{
        .stApp {{
            color-scheme: dark;
        }}
    }}
    
    </style>
    """
    
    return css
