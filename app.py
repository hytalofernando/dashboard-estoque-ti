"""
Dashboard Estoque TI - Sistema Modernizado
Versão: 2.0.0 Moderna com Pydantic 2.x
"""

import streamlit as st
import os

# Configuração de logging
from loguru import logger
logger.add("logs/dashboard.log", rotation="1 week", retention="1 month", level="INFO")

# Imports dos serviços e configurações
from config.settings import settings
from services.estoque_service import EstoqueService
from utils.ui_utils import show_toast, show_error_message

# ✅ SISTEMA DE AUTENTICAÇÃO
from auth.auth_service import auth_service
from pages.login_page import render_login_page

# Configuração da página
st.set_page_config(
    page_title=settings.PAGE_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state="expanded"
)

# Importar novo sistema de CSS
from utils.modern_css import get_modern_css

# CSS customizado moderno
def load_modern_css():
    """Carrega CSS moderno otimizado"""
    return get_modern_css()

def load_legacy_css():
    """CSS legado (mantido para compatibilidade)"""
    css = """
    <style>
    /* ===== VARIÁVEIS CSS ATUALIZADAS E MELHORADAS ===== */
    :root {
        /* Cores de fundo */
        --bg-primary: #0e1117;
        --bg-secondary: #262730;
        --bg-tertiary: #404040;
        --bg-quaternary: #1e2329;
        --bg-card: #1a1d23;
        
        /* Cores de texto - melhor contraste */
        --text-primary: #ffffff;
        --text-secondary: #f0f0f0;  /* Melhorado de #e0e0e0 para melhor contraste */
        --text-tertiary: #c1c7cd;
        --text-muted: #8b949e;
        
        /* Cores funcionais */
        --accent-color: #00d4ff;
        --accent-hover: #00bde6;
        --accent-light: #33ddff;
        --success-color: #4ade80;
        --success-light: #6ee7b7;
        --warning-color: #fbbf24;
        --warning-light: #fcd34d;
        --error-color: #f87171;
        --error-light: #fca5a5;
        --info-color: #60a5fa;
        --info-light: #93c5fd;
        
        /* Cores de status semânticas */
        --status-available: #10b981;
        --status-unavailable: #ef4444;
        --status-maintenance: #f59e0b;
        --status-pending: #6366f1;
        
        /* Propriedades visuais */
        --border-radius: 12px;
        --border-radius-lg: 16px;
        --border-radius-sm: 8px;
        --shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.4);
        --shadow-accent: 0 4px 12px rgba(0, 212, 255, 0.2);
        
        /* Gradientes */
        --gradient-primary: linear-gradient(135deg, var(--accent-color), var(--success-color));
        --gradient-bg: linear-gradient(135deg, var(--bg-primary) 0%, #1a1a2e 100%);
        --gradient-card: linear-gradient(145deg, var(--bg-secondary), var(--bg-quaternary));
    }
    
    /* ===== ESTILO MODERNO GERAL ===== */
    .stApp {
        background: var(--gradient-bg);
    }
    
    /* Header principal com gradiente melhorado */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        letter-spacing: -0.02em;
    }
    
    /* Cards modernos com melhor hierarquia visual */
    .metric-card {
        background: var(--gradient-card);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--bg-tertiary);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: var(--gradient-primary);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-color: var(--accent-color);
    }
    
    .metric-card:hover::before {
        transform: scaleX(1);
    }
    
    /* ===== SIDEBAR MODERNA E APRIMORADA ===== */
    
    /* Container principal do sidebar */
    .css-1d391kg, .stSidebar > div {
        background: var(--gradient-card);
        border-right: 1px solid var(--bg-tertiary);
    }
    
    /* Título do sidebar */
    .css-1d391kg .stMarkdown h1,
    .stSidebar .stMarkdown h1 {
        color: var(--text-primary);
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        padding: 1rem;
        background: var(--gradient-primary);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        border-radius: var(--border-radius);
    }
    
    /* Títulos de seção no sidebar */
    .css-1d391kg .stMarkdown h2,
    .css-1d391kg .stMarkdown h3,
    .stSidebar .stMarkdown h2,
    .stSidebar .stMarkdown h3 {
        color: var(--text-secondary);
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(0, 212, 255, 0.1);
        border-radius: var(--border-radius-sm);
        border-left: 3px solid var(--accent-color);
    }
    
    /* Texto no sidebar */
    .css-1d391kg .stMarkdown p,
    .stSidebar .stMarkdown p {
        color: var(--text-tertiary);
        font-size: 0.9rem;
        line-height: 1.4;
        margin-bottom: 0.5rem;
    }
    
    /* Selectbox no sidebar */
    .css-1d391kg .stSelectbox > div > div > div,
    .stSidebar .stSelectbox > div > div > div {
        background: var(--bg-card);
        border: 2px solid var(--bg-tertiary);
        border-radius: var(--border-radius);
        color: var(--text-secondary);
        transition: all 0.3s ease;
    }
    
    .css-1d391kg .stSelectbox > div > div > div:hover,
    .stSidebar .stSelectbox > div > div > div:hover {
        border-color: var(--accent-color);
        background: var(--bg-secondary);
    }
    
    /* Botões no sidebar */
    .css-1d391kg .stButton > button,
    .stSidebar .stButton > button {
        background: var(--gradient-primary);
        border: none;
        border-radius: var(--border-radius);
        color: var(--text-primary);
        font-weight: 600;
        padding: 0.6rem 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
        box-shadow: var(--shadow);
    }
    
    .css-1d391kg .stButton > button:hover,
    .stSidebar .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-accent);
        filter: brightness(1.1);
    }
    
    /* Expanders no sidebar */
    .css-1d391kg .streamlit-expanderHeader,
    .stSidebar .streamlit-expanderHeader {
        background: var(--bg-card);
        border: 1px solid var(--bg-tertiary);
        border-radius: var(--border-radius);
        color: var(--text-secondary);
        font-weight: 500;
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
    }
    
    .css-1d391kg .streamlit-expanderHeader:hover,
    .stSidebar .streamlit-expanderHeader:hover {
        background: var(--bg-secondary);
        border-color: var(--accent-color);
        color: var(--text-primary);
    }
    
    .css-1d391kg .streamlit-expanderContent,
    .stSidebar .streamlit-expanderContent {
        background: var(--bg-quaternary);
        border: 1px solid var(--bg-tertiary);
        border-top: none;
        border-radius: 0 0 var(--border-radius) var(--border-radius);
        padding: 1rem;
    }
    
    /* Checkboxes no sidebar */
    .css-1d391kg .stCheckbox,
    .stSidebar .stCheckbox {
        margin-bottom: 0.5rem;
    }
    
    .css-1d391kg .stCheckbox > label,
    .stSidebar .stCheckbox > label {
        color: var(--text-tertiary);
        font-size: 0.9rem;
        transition: color 0.3s ease;
    }
    
    .css-1d391kg .stCheckbox > label:hover,
    .stSidebar .stCheckbox > label:hover {
        color: var(--text-secondary);
    }
    
    /* Divisores no sidebar */
    .css-1d391kg hr,
    .stSidebar hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--bg-tertiary), transparent);
        margin: 1.5rem 0;
    }
    
    /* Scrollbar do sidebar */
    .css-1d391kg::-webkit-scrollbar,
    .stSidebar::-webkit-scrollbar {
        width: 6px;
    }
    
    .css-1d391kg::-webkit-scrollbar-track,
    .stSidebar::-webkit-scrollbar-track {
        background: var(--bg-primary);
        border-radius: 3px;
    }
    
    .css-1d391kg::-webkit-scrollbar-thumb,
    .stSidebar::-webkit-scrollbar-thumb {
        background: var(--accent-color);
        border-radius: 3px;
        opacity: 0.7;
    }
    
    .css-1d391kg::-webkit-scrollbar-thumb:hover,
    .stSidebar::-webkit-scrollbar-thumb:hover {
        background: var(--accent-hover);
        opacity: 1;
    }
    
    /* Botões modernos melhorados */
    .stButton > button {
        background: var(--gradient-primary);
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow);
        color: var(--text-primary);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-accent);
        filter: brightness(1.1);
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Formulários modernos melhorados */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background: var(--bg-card);
        border: 2px solid var(--bg-tertiary);
        border-radius: var(--border-radius);
        color: var(--text-secondary);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.15);
        background: var(--bg-secondary);
        color: var(--text-primary);
        transform: translateY(-1px);
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {
        color: var(--text-muted);
        transition: color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus::placeholder,
    .stTextArea > div > div > textarea:focus::placeholder {
        color: var(--text-tertiary);
    }
    
    /* Tabelas modernas */
    .stDataFrame {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--shadow);
    }
    
    /* Alertas modernos */
    .stAlert {
        border-radius: var(--border-radius);
        border: none;
        box-shadow: var(--shadow);
    }
    
    /* Gráficos com bordas modernas */
    .js-plotly-plot {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--shadow);
    }
    
    /* Animações suaves */
    * {
        transition: all 0.2s ease;
    }
    
    /* Scrollbar personalizada melhorada */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--accent-color);
        border-radius: 4px;
        transition: background 0.3s ease;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent-hover);
    }
    
    /* Melhorias adicionais para hierarquia visual */
    
    /* Títulos com melhor hierarquia */
    h1, .stMarkdown h1 {
        color: var(--text-primary);
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    h2, .stMarkdown h2 {
        color: var(--text-secondary);
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    
    h3, .stMarkdown h3 {
        color: var(--text-tertiary);
        font-weight: 500;
    }
    
    /* Parágrafos e texto */
    p, .stMarkdown p {
        color: var(--text-secondary);
        line-height: 1.6;
    }
    
    /* Links com hover melhorado */
    a, .stMarkdown a {
        color: var(--accent-color);
        text-decoration: none;
        transition: color 0.3s ease;
    }
    
    a:hover, .stMarkdown a:hover {
        color: var(--accent-light);
        text-decoration: underline;
    }
    
    /* Divisores mais elegantes */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--bg-tertiary), transparent);
        margin: 2rem 0;
    }
    
    /* Melhorar contraste de elementos de código */
    code {
        background: var(--bg-card);
        color: var(--accent-light);
        padding: 0.2em 0.4em;
        border-radius: var(--border-radius-sm);
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
    }
    
    /* Status indicators com animação */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.25rem 0.75rem;
        border-radius: var(--border-radius);
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .status-available {
        background: rgba(16, 185, 129, 0.1);
        color: var(--status-available);
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    
    .status-unavailable {
        background: rgba(239, 68, 68, 0.1);
        color: var(--status-unavailable);
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    .status-maintenance {
        background: rgba(245, 158, 11, 0.1);
        color: var(--status-maintenance);
        border: 1px solid rgba(245, 158, 11, 0.3);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def initialize_services():
    """Inicializa serviços da aplicação"""
    try:
        if 'estoque_service' not in st.session_state:
            logger.info("Inicializando serviços...")
            st.session_state.estoque_service = EstoqueService()
        return st.session_state.estoque_service
    except Exception as e:
        logger.error(f"Erro ao inicializar serviços: {str(e)}")
        show_error_message(f"Erro ao inicializar aplicação: {str(e)}")
        return None

def render_header():
    """Renderiza header principal"""
    st.markdown(
        '<h1 class="main-header">💻 Novo Atacarejo - Estoque TI</h1>', 
        unsafe_allow_html=True
    )
    
    # Subtitle com informações
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align: center; color: #e0e0e0; margin-bottom: 2rem;">
                <p><strong>Sistema Moderno de Gerenciamento de Estoque</strong></p>
            </div>
            """, 
            unsafe_allow_html=True
        )

def render_user_info_sidebar():
    """Renderiza informações do usuário na sidebar"""
    if auth_service.is_authenticated():
        user = auth_service.get_current_user()
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Usuário Conectado")
        
        # Informações do usuário
        if user.profile == "administrador":
            profile_icon = "👑"
            profile_color = "🟢"
        else:
            profile_icon = "👀"
            profile_color = "🔵"
        
        st.sidebar.markdown(f"**{profile_icon} {user.display_name}**")
        st.sidebar.markdown(f"{profile_color} {user.profile.title()}")
        
        # Permissões
        can_edit = auth_service.can_edit()
        edit_status = "✅ Pode editar" if can_edit else "👀 Somente leitura"
        st.sidebar.markdown(f"**Permissões:** {edit_status}")
        
        # Botão de logout
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            auth_service.logout()
            show_toast("👋 Logout realizado!", "🚪")
            st.rerun()
        
        st.sidebar.markdown("---")

def main():
    """Função principal da aplicação"""
    try:
        # Carregar CSS moderno profissional
        st.markdown(load_modern_css(), unsafe_allow_html=True)
        
        # ✅ VERIFICAR AUTENTICAÇÃO PRIMEIRO
        if not auth_service.is_authenticated():
            # Renderizar página de login se não estiver autenticado
            render_login_page()
            return
        
        # ✅ USUÁRIO AUTENTICADO - RENDERIZAR DASHBOARD
        # Renderizar header
        render_header()
        
        # Inicializar serviços
        estoque_service = initialize_services()
        if not estoque_service:
            st.stop()
        
        # Configurar sidebar com informações do usuário
        st.sidebar.title("🔧 Controles")
        render_user_info_sidebar()
        
        # ✅ OBTER PÁGINAS FILTRADAS POR PERMISSÕES
        paginas_filtradas = auth_service.get_filtered_pages()
        paginas_ativas = [
            info["titulo"] for key, info in paginas_filtradas.items()
        ]
        
        if not paginas_ativas:
            st.error("❌ Nenhuma página disponível para seu perfil.")
            st.stop()
        
        # Navegação dinâmica baseada em permissões
        selected_page = st.sidebar.selectbox(
            "📱 Navegação:",
            paginas_ativas
        )
        
        # ✅ CONTROLE DE PÁGINAS APENAS PARA ADMINISTRADORES
        if auth_service.has_permission("configuracoes"):
            with st.sidebar.expander("⚙️ Configurar Páginas"):
                st.markdown("**Ativar/Desativar Páginas:**")
                for key, info in settings.PAGINAS_ATIVAS.items():
                    current_state = st.checkbox(
                        info["titulo"], 
                        value=info["ativa"],
                        key=f"page_{key}",
                        help=info["descricao"]
                    )
                    # Atualizar configuração em tempo real
                    settings.PAGINAS_ATIVAS[key]["ativa"] = current_state
        
        st.sidebar.markdown("---")
        
        # Informações da sidebar
        with st.sidebar.expander("ℹ️ Informações do Sistema"):
            st.markdown("""
            **Versão:** 2.0.0 Moderna + Auth 🔐  
            **Tecnologias:**
            - Streamlit 1.42+
            - Plotly 5.21+ 
            - Pandas 2.2+
            - Pydantic 2.5+
            - Sistema de Autenticação
            
            **Recursos Modernos:**
            - Interface responsiva
            - Notificações toast
            - Gráficos com bordas arredondadas
            - Validação de dados
            - Logs estruturados
            - Sistema de login seguro
            """)
            
            # ✅ Estatísticas das páginas baseadas em permissões
            total_paginas = len(settings.PAGINAS_ATIVAS)
            paginas_disponiveis = len(paginas_filtradas)
            st.markdown(f"**📊 Páginas:** {paginas_disponiveis}/{total_paginas} disponíveis")
            
            # ✅ Informações do usuário
            user = auth_service.get_current_user()
            st.markdown(f"**👤 Usuário:** {user.username}")
            st.markdown(f"**🔐 Perfil:** {user.profile.title()}")
        
        # Status da página atual
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**📍 Página Atual:** {selected_page}")
        
        # Renderizar página selecionada com tratamento de erro
        try:
            if "Dashboard" in str(selected_page):
                from pages.dashboard_page import render_dashboard_page
                logger.info("Renderizando Dashboard")
                render_dashboard_page(estoque_service)
            elif "Adicionar" in str(selected_page):
                from pages.adicionar_page import render_adicionar_page
                logger.info("Renderizando Adicionar Equipamento")
                render_adicionar_page(estoque_service)
            elif "Remover" in str(selected_page):
                from pages.remover_page import render_remover_page
                logger.info("Renderizando Remover Equipamento")
                render_remover_page(estoque_service)
            elif "Histórico" in str(selected_page):
                from pages.historico_page import render_historico_page
                logger.info("Renderizando Histórico")
                render_historico_page(estoque_service)
            elif "Códigos" in str(selected_page):
                from pages.codigos_page import render_codigos_page
                logger.info("Renderizando Códigos")
                render_codigos_page(estoque_service)
            elif "Configurações" in str(selected_page):
                from pages.configuracoes_page import render_configuracoes_page
                logger.info("Renderizando Configurações")
                render_configuracoes_page()
            else:
                st.error("Página não encontrada!")
                st.info("Selecione uma página válida no menu lateral.")
                
        except Exception as page_error:
            logger.error(f"Erro ao renderizar página {selected_page}: {str(page_error)}")
            st.error(f"Erro ao carregar a página: {str(page_error)}")
            st.info("Por favor, tente selecionar outra página ou recarregue a aplicação.")
            
            # Mostrar detalhes técnicos em modo debug
            with st.expander("🔧 Detalhes Técnicos (Debug)"):
                st.code(str(page_error))
                st.markdown("**Dica:** Verifique os logs para mais informações.")
        
        # Footer moderno
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; color: #666; margin-top: 2rem;">
                <p><strong>Dashboard Estoque TI v2.0</strong> | Desenvolvedor: Hytalo Fernando</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    except Exception as e:
        logger.error(f"Erro na aplicação principal: {str(e)}")
        st.error("Ocorreu um erro inesperado. Verifique os logs para mais detalhes.")
        show_error_message("Erro crítico na aplicação")

if __name__ == "__main__":
    # Criar diretório de logs se não existir
    os.makedirs("logs", exist_ok=True)
    
    # Executar aplicação
    logger.info("Iniciando Dashboard Estoque TI v2.0")
    main() 