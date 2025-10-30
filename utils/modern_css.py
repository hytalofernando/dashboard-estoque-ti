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
    
    /* Sidebar com fundo preto e melhor contraste */
    .css-1d391kg {{
        background: #000000 !important;
        border-right: 1px solid var(--gray-700);
    }}
    
    /* Seletores adicionais para garantir sidebar preto */
    .stSidebar {{
        background: #000000 !important;
    }}
    
    .stSidebar > div {{
        background: #000000 !important;
    }}
    
    [data-testid="stSidebar"] {{
        background: #000000 !important;
    }}
    
    [data-testid="stSidebar"] > div {{
        background: #000000 !important;
    }}
    
    /* Container principal do sidebar */
    .css-1d391kg, .css-17lntkn, .css-1y0tads {{
        background: #000000 !important;
    }}
    
    /* Textos do sidebar com contraste otimizado para fundo preto */
    .css-1d391kg .stMarkdown {{
        color: #FFFFFF !important;
    }}
    
    .css-1d391kg .stMarkdown h1, .css-1d391kg .stMarkdown h2, .css-1d391kg .stMarkdown h3 {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }}
    
    /* Textos adicionais do sidebar */
    .stSidebar .stMarkdown {{
        color: #FFFFFF !important;
    }}
    
    .stSidebar .stMarkdown h1, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }}
    
    [data-testid="stSidebar"] .stMarkdown {{
        color: #FFFFFF !important;
    }}
    
    [data-testid="stSidebar"] .stMarkdown h1, 
    [data-testid="stSidebar"] .stMarkdown h2, 
    [data-testid="stSidebar"] .stMarkdown h3 {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }}
    
    /* Inputs do sidebar com fundo escuro para contraste com preto */
    .css-1d391kg .stSelectbox > div > div > div {{
        background: #1a1a1a !important;
        border: 2px solid #404040 !important;
        color: #FFFFFF !important;
    }}
    
    .css-1d391kg .stTextInput > div > div > input {{
        background: #1a1a1a !important;
        border: 2px solid #404040 !important;
        color: #FFFFFF !important;
    }}
    
    /* Inputs adicionais do sidebar */
    .stSidebar .stSelectbox > div > div > div {{
        background: #1a1a1a !important;
        border: 2px solid #404040 !important;
        color: #FFFFFF !important;
    }}
    
    .stSidebar .stTextInput > div > div > input {{
        background: #1a1a1a !important;
        border: 2px solid #404040 !important;
        color: #FFFFFF !important;
    }}
    
    [data-testid="stSidebar"] .stSelectbox > div > div > div {{
        background: #1a1a1a !important;
        border: 2px solid #404040 !important;
        color: #FFFFFF !important;
    }}
    
    [data-testid="stSidebar"] .stTextInput > div > div > input {{
        background: #1a1a1a !important;
        border: 2px solid #404040 !important;
        color: #FFFFFF !important;
    }}
    
    /* Botões do sidebar */
    .css-1d391kg .stButton > button {{
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }}
    
    .stSidebar .stButton > button {{
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }}
    
    [data-testid="stSidebar"] .stButton > button {{
        background: var(--gradient-primary) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }}
    
    /* Checkboxes e labels do sidebar */
    .css-1d391kg .stCheckbox > label {{
        color: #FFFFFF !important;
    }}
    
    .stSidebar .stCheckbox > label {{
        color: #FFFFFF !important;
    }}
    
    [data-testid="stSidebar"] .stCheckbox > label {{
        color: #FFFFFF !important;
    }}
    
    /* Expanders do sidebar com fundo escuro */
    .css-1d391kg .stExpander > div > div {{
        background: #1a1a1a !important;
        border: 1px solid #404040 !important;
    }}
    
    .css-1d391kg .stExpander summary {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
        background: #1a1a1a !important;
    }}
    
    .stSidebar .stExpander > div > div {{
        background: #1a1a1a !important;
        border: 1px solid #404040 !important;
    }}
    
    .stSidebar .stExpander summary {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
        background: #1a1a1a !important;
    }}
    
    [data-testid="stSidebar"] .stExpander > div > div {{
        background: #1a1a1a !important;
        border: 1px solid #404040 !important;
    }}
    
    [data-testid="stSidebar"] .stExpander summary {{
        color: #FFFFFF !important;
        font-weight: 600 !important;
        background: #1a1a1a !important;
    }}
    
    /* Métricas com melhor contraste */
    [data-testid="metric-container"] {{
        background: var(--bg-card) !important;
        border-radius: var(--border-radius) !important;
        padding: var(--space-4) !important;
        box-shadow: var(--shadow) !important;
        border: 1px solid var(--gray-600) !important;
        transition: all var(--transition-normal) !important;
    }}
    
    [data-testid="metric-container"]:hover {{
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
        border-color: var(--primary) !important;
    }}
    
    [data-testid="metric-container"] [data-testid="metric-label"] {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: var(--text-sm) !important;
    }}
    
    [data-testid="metric-container"] [data-testid="metric-value"] {{
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: var(--text-2xl) !important;
    }}
    
    [data-testid="metric-container"] [data-testid="metric-delta"] {{
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }}

    /* === MELHORIAS DE CONTRASTE PARA VALORES DAS MÉTRICAS === */

    /* Valores das métricas com melhor contraste - especificamente para '0' */
    [data-testid="metric-container"] [data-testid="metric-value"],
    .metric-value {{
        color: #FFFFFF !important;
        font-weight: 800 !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5) !important;
        font-size: var(--text-3xl) !important;
        line-height: 1.1 !important;
    }}

    /* Específico para valores que aparecem como '0' - forçando branco puro */
    div[class*="st-emotion-cache"] {{
        color: #FFFFFF !important;
        font-weight: 700 !important;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.7) !important;
    }}

    /* Container das métricas com fundo mais escuro para melhor contraste */
    [data-testid="metric-container"] {{
        background: linear-gradient(135deg, #1E293B 0%, #334155 100%) !important;
        border: 2px solid #475569 !important;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.4) !important;
    }}

    /* Hover das métricas com destaque ainda melhor */
    [data-testid="metric-container"]:hover {{
        background: linear-gradient(135deg, #334155 0%, #475569 100%) !important;
        border-color: #0066FF !important;
        box-shadow: 0 12px 35px rgba(0, 102, 255, 0.3) !important;
        transform: translateY(-3px) !important;
    }}

    /* Labels das métricas com contraste otimizado */
    [data-testid="metric-container"] [data-testid="metric-label"] {{
        color: #E2E8F0 !important;
        font-weight: 600 !important;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3) !important;
    }}

    /* Delta das métricas com cores mais vibrantes */
    [data-testid="metric-container"] [data-testid="metric-delta"] {{
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.4) !important;
    }}

    [data-testid="metric-container"] [data-testid="metric-delta"][class*="positive"] {{
        color: #4DD678 !important;
        font-weight: 700 !important;
    }}

    [data-testid="metric-container"] [data-testid="metric-delta"][class*="negative"] {{
        color: #FF6B7A !important;
        font-weight: 700 !important;
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
    
    /* Inputs com melhor contraste */
    .stTextInput > div > div > input {{
        background: {colors.get('background_input', colors['background_tertiary'])} !important;
        border: 2px solid var(--gray-500) !important;
        border-radius: var(--border-radius) !important;
        color: var(--text-primary) !important;
        padding: var(--space-3) !important;
        font-size: var(--text-base) !important;
        transition: all var(--transition-normal) !important;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: var(--primary) !important;
        background: {colors.get('background_input_focus', colors['background_tertiary'])} !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.2) !important;
        color: white !important;
    }}
    
    .stTextInput > div > div > input::placeholder {{
        color: var(--text-muted) !important;
        opacity: 0.8 !important;
    }}
    
    .stSelectbox > div > div > div {{
        background: {colors.get('background_input', colors['background_tertiary'])} !important;
        border: 2px solid var(--gray-500) !important;
        border-radius: var(--border-radius) !important;
        color: var(--text-primary) !important;
        font-size: var(--text-base) !important;
    }}
    
    .stSelectbox > div > div > div:hover {{
        border-color: var(--primary) !important;
        background: {colors.get('background_input_focus', colors['background_tertiary'])} !important;
    }}
    
    .stNumberInput > div > div > input {{
        background: {colors.get('background_input', colors['background_tertiary'])} !important;
        border: 2px solid var(--gray-500) !important;
        border-radius: var(--border-radius) !important;
        color: var(--text-primary) !important;
        padding: var(--space-3) !important;
        font-size: var(--text-base) !important;
        transition: all var(--transition-normal) !important;
    }}
    
    .stNumberInput > div > div > input:focus {{
        border-color: var(--primary) !important;
        background: {colors.get('background_input_focus', colors['background_tertiary'])} !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.2) !important;
        color: white !important;
    }}
    
    .stTextArea > div > div > textarea {{
        background: {colors.get('background_input', colors['background_tertiary'])} !important;
        border: 2px solid var(--gray-500) !important;
        border-radius: var(--border-radius) !important;
        color: var(--text-primary) !important;
        padding: var(--space-3) !important;
        font-size: var(--text-base) !important;
        transition: all var(--transition-normal) !important;
    }}
    
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--primary) !important;
        background: {colors.get('background_input_focus', colors['background_tertiary'])} !important;
        box-shadow: 0 0 0 3px rgba(0, 102, 255, 0.2) !important;
        color: white !important;
    }}
    
    /* === TABELAS E DATAFRAMES OTIMIZADAS === */
    
    /* Streamlit Dataframes */
    .stDataFrame > div {{
        background: var(--bg-card) !important;
        border-radius: var(--border-radius) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-md) !important;
        border: 2px solid var(--gray-600) !important;
    }}
    
    .stDataFrame table {{
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }}
    
    .stDataFrame thead th {{
        background: var(--primary) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: var(--space-4) !important;
        border-bottom: 2px solid var(--primary-dark) !important;
        font-size: var(--text-sm) !important;
        text-align: left !important;
        letter-spacing: 0.5px !important;
    }}
    
    .stDataFrame tbody td {{
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        padding: var(--space-3) !important;
        border-bottom: 1px solid var(--gray-600) !important;
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
    }}
    
    .stDataFrame tbody tr:nth-child(even) td {{
        background: var(--bg-secondary) !important;
    }}
    
    .stDataFrame tbody tr:hover td {{
        background: var(--bg-tertiary) !important;
        color: white !important;
        transform: scale(1.001) !important;
        transition: all var(--transition-fast) !important;
    }}
    
    .stDataFrame .col_heading {{
        background: var(--primary) !important;
        color: white !important;
        font-weight: 700 !important;
    }}
    
    .stDataFrame .row_heading {{
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }}
    
    .stDataFrame .data {{
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }}
    
    /* Tabelas padrão HTML/CSS */
    .dataframe {{
        background: var(--bg-card) !important;
        border-radius: var(--border-radius) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-md) !important;
        border: 2px solid var(--gray-600) !important;
    }}
    
    .dataframe th {{
        background: var(--primary) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: var(--space-4) !important;
        border-bottom: 2px solid var(--primary-dark) !important;
        font-size: var(--text-sm) !important;
        text-align: left !important;
    }}
    
    .dataframe td {{
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        padding: var(--space-3) !important;
        border-bottom: 1px solid var(--gray-600) !important;
        font-size: var(--text-sm) !important;
        font-weight: 500 !important;
    }}
    
    .dataframe tr:nth-child(even) td {{
        background: var(--bg-secondary) !important;
    }}
    
    .dataframe tr:hover td {{
        background: var(--bg-tertiary) !important;
        color: white !important;
    }}
    
    /* Casos específicos de tabelas */
    table {{
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border-collapse: collapse !important;
    }}
    
    th {{
        background: var(--primary) !important;
        color: white !important;
        font-weight: 700 !important;
        padding: var(--space-3) !important;
        border: 1px solid var(--gray-600) !important;
    }}
    
    td {{
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
        padding: var(--space-3) !important;
        border: 1px solid var(--gray-700) !important;
    }}
    
    /* Labels e textos de formulário */
    .stTextInput > label {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: var(--text-sm) !important;
        margin-bottom: var(--space-1) !important;
    }}
    
    .stSelectbox > label {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: var(--text-sm) !important;
        margin-bottom: var(--space-1) !important;
    }}
    
    .stNumberInput > label {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: var(--text-sm) !important;
        margin-bottom: var(--space-1) !important;
    }}
    
    .stTextArea > label {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: var(--text-sm) !important;
        margin-bottom: var(--space-1) !important;
    }}
    
    /* Markdown e textos gerais */
    .stMarkdown {{
        color: var(--text-secondary) !important;
    }}
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
        color: var(--text-primary) !important;
    }}
    
    .stMarkdown p {{
        color: var(--text-secondary) !important;
        line-height: 1.6 !important;
    }}
    
    .stMarkdown strong {{
        color: var(--text-primary) !important;
    }}
    
    .stCaption {{
        color: var(--text-tertiary) !important;
        font-size: var(--text-xs) !important;
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
    
    /* === ALERTAS E MENSAGENS OTIMIZADAS === */
    .stAlert {{
        border-radius: var(--border-radius) !important;
        border: none !important;
        padding: var(--space-4) !important;
        font-weight: 500 !important;
        font-size: var(--text-sm) !important;
        box-shadow: var(--shadow) !important;
    }}
    
    .stSuccess {{
        background: rgba(0, 200, 81, 0.15) !important;
        color: var(--success-light) !important;
        border-left: 4px solid var(--success) !important;
        border: 1px solid rgba(0, 200, 81, 0.3) !important;
    }}
    
    .stWarning {{
        background: rgba(255, 179, 0, 0.15) !important;
        color: var(--warning-light) !important;
        border-left: 4px solid var(--warning) !important;
        border: 1px solid rgba(255, 179, 0, 0.3) !important;
    }}
    
    .stError {{
        background: rgba(255, 53, 71, 0.15) !important;
        color: var(--error-light) !important;
        border-left: 4px solid var(--error) !important;
        border: 1px solid rgba(255, 53, 71, 0.3) !important;
    }}
    
    .stInfo {{
        background: rgba(23, 162, 184, 0.15) !important;
        color: var(--info-light) !important;
        border-left: 4px solid var(--info) !important;
        border: 1px solid rgba(23, 162, 184, 0.3) !important;
    }}
    
    /* Mensagens específicas do Streamlit */
    .stAlert > div {{
        color: inherit !important;
        font-size: var(--text-sm) !important;
    }}
    
    /* Status badges personalizados */
    .status-badge {{
        display: inline-flex !important;
        align-items: center !important;
        padding: var(--space-1) var(--space-3) !important;
        border-radius: var(--border-radius-sm) !important;
        font-size: var(--text-xs) !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }}
    
    .status-disponivel {{
        background: rgba(0, 200, 81, 0.2) !important;
        color: var(--success-light) !important;
        border: 1px solid var(--success) !important;
    }}
    
    .status-indisponivel {{
        background: rgba(255, 53, 71, 0.2) !important;
        color: var(--error-light) !important;
        border: 1px solid var(--error) !important;
    }}
    
    .status-manutencao {{
        background: rgba(255, 179, 0, 0.2) !important;
        color: var(--warning-light) !important;
        border: 1px solid var(--warning) !important;
    }}
    
    /* === CONTAINERS E COLUNAS STREAMLIT === */
    
    .stContainer {{
        color: var(--text-primary) !important;
    }}
    
    .stColumn {{
        color: var(--text-primary) !important;
    }}
    
    .stExpander {{
        background: var(--bg-secondary) !important;
        border-radius: var(--border-radius) !important;
        border: 1px solid var(--gray-600) !important;
    }}
    
    .stExpander > div > div > div {{
        color: var(--text-primary) !important;
    }}
    
    .stExpander summary {{
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        padding: var(--space-3) !important;
        border-radius: var(--border-radius-sm) !important;
    }}
    
    .stExpander summary:hover {{
        background: var(--bg-tertiary) !important;
        color: white !important;
    }}
    
    /* Containers de métricas personalizados */
    .metric-container {{
        background: var(--bg-card) !important;
        border-radius: var(--border-radius) !important;
        padding: var(--space-4) !important;
        box-shadow: var(--shadow) !important;
        border: 1px solid var(--gray-600) !important;
        margin: var(--space-2) 0 !important;
    }}
    
    .metric-label {{
        color: var(--text-secondary) !important;
        font-size: var(--text-sm) !important;
        font-weight: 600 !important;
        margin-bottom: var(--space-1) !important;
    }}
    
    .metric-value {{
        color: var(--text-primary) !important;
        font-size: var(--text-2xl) !important;
        font-weight: 700 !important;
        line-height: 1.2 !important;
    }}
    
    .metric-delta {{
        color: var(--text-tertiary) !important;
        font-size: var(--text-xs) !important;
        font-weight: 500 !important;
        margin-top: var(--space-1) !important;
    }}
    
    /* Progress bars */
    .stProgress > div > div > div {{
        background: var(--primary) !important;
    }}
    
    .stProgress > div > div {{
        background: var(--bg-tertiary) !important;
    }}
    
    /* === CLASSES UTILITÁRIAS MELHORADAS === */
    .text-center {{ text-align: center; }}
    .text-right {{ text-align: right; }}
    .font-bold {{ font-weight: 700; }}
    .font-semibold {{ font-weight: 600; }}
    .font-medium {{ font-weight: 500; }}
    
    .text-primary {{ color: var(--text-primary) !important; }}
    .text-secondary {{ color: var(--text-secondary) !important; }}
    .text-tertiary {{ color: var(--text-tertiary) !important; }}
    .text-muted {{ color: var(--text-muted) !important; }}
    .text-white {{ color: white !important; }}
    
    .bg-primary {{ background-color: var(--primary) !important; }}
    .bg-secondary {{ background-color: var(--bg-secondary) !important; }}
    .bg-card {{ background-color: var(--bg-card) !important; }}
    .bg-success {{ background-color: var(--success) !important; }}
    .bg-warning {{ background-color: var(--warning) !important; }}
    .bg-error {{ background-color: var(--error) !important; }}
    
    .border-primary {{ border-color: var(--primary) !important; }}
    .border-success {{ border-color: var(--success) !important; }}
    .border-warning {{ border-color: var(--warning) !important; }}
    .border-error {{ border-color: var(--error) !important; }}
    
    .rounded {{ border-radius: var(--border-radius) !important; }}
    .rounded-sm {{ border-radius: var(--border-radius-sm) !important; }}
    .rounded-lg {{ border-radius: var(--border-radius-lg) !important; }}
    
    .shadow {{ box-shadow: var(--shadow) !important; }}
    .shadow-md {{ box-shadow: var(--shadow-md) !important; }}
    .shadow-lg {{ box-shadow: var(--shadow-lg) !important; }}
    
    .transition {{ transition: all var(--transition-normal) !important; }}
    .transition-fast {{ transition: all var(--transition-fast) !important; }}
    
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
