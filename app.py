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

# Configuração da página
st.set_page_config(
    page_title=settings.PAGE_TITLE,
    page_icon=settings.PAGE_ICON,
    layout=settings.LAYOUT,
    initial_sidebar_state="expanded"
)

# CSS customizado moderno
def load_modern_css():
    """Carrega CSS moderno otimizado"""
    css = """
    <style>
    /* ===== VARIÁVEIS CSS ATUALIZADAS ===== */
    :root {
        --bg-primary: #0e1117;
        --bg-secondary: #262730;
        --bg-tertiary: #404040;
        --text-primary: #ffffff;
        --text-secondary: #e0e0e0;
        --accent-color: #00d4ff;
        --success-color: #4ade80;
        --warning-color: #fbbf24;
        --error-color: #f87171;
        --border-radius: 12px;
        --shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }
    
    /* ===== ESTILO MODERNO GERAL ===== */
    .stApp {
        background: linear-gradient(135deg, var(--bg-primary) 0%, #1a1a2e 100%);
    }
    
    /* Header principal com gradiente */
    .main-header {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent-color), var(--success-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    /* Cards modernos */
    .metric-card {
        background: var(--bg-secondary);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--bg-tertiary);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 212, 255, 0.2);
    }
    
    /* Sidebar moderna */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--bg-secondary) 0%, var(--bg-primary) 100%);
    }
    
    /* Botões modernos */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-color), #0099cc);
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 16px rgba(0, 212, 255, 0.3);
    }
    
    /* Formulários modernos */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {
        background: var(--bg-secondary);
        border: 2px solid var(--bg-tertiary);
        border-radius: var(--border-radius);
        color: var(--text-primary);
        transition: border-color 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--accent-color);
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
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
    
    /* Scrollbar personalizada */
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
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #0099cc;
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
        '<h1 class="main-header">💻 Dashboard Estoque TI</h1>', 
        unsafe_allow_html=True
    )
    
    # Subtitle com informações
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align: center; color: #e0e0e0; margin-bottom: 2rem;">
                <p><strong>Sistema Moderno de Gerenciamento de Estoque</strong></p>
                <p>Tecnologia: Streamlit 1.42+ | Plotly 5.21+ | Pandas 2.2+</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

def main():
    """Função principal da aplicação"""
    try:
        # Carregar CSS moderno
        load_modern_css()
        
        # Renderizar header
        render_header()
        
        # Inicializar serviços
        estoque_service = initialize_services()
        if not estoque_service:
            st.stop()
        
        # Configurar sidebar
        st.sidebar.title("🔧 Controles")
        st.sidebar.markdown("---")
        
        # Obter páginas ativas das configurações
        paginas_ativas = [
            info["titulo"] for key, info in settings.PAGINAS_ATIVAS.items() 
            if info["ativa"]
        ]
        
        # Navegação dinâmica baseada em configurações
        selected_page = st.sidebar.selectbox(
            "📱 Navegação:",
            paginas_ativas
        )
        
        # Adicionar controle de páginas para administradores
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
            **Versão:** 2.0.0 Moderna  
            **Tecnologias:**
            - Streamlit 1.42+
            - Plotly 5.21+ 
            - Pandas 2.2+
            - Pydantic 2.5+
            
            **Recursos Modernos:**
            - Interface responsiva
            - Notificações toast
            - Gráficos com bordas arredondadas
            - Validação de dados
            - Logs estruturados
            """)
            
            # Estatísticas das páginas
            total_paginas = len(settings.PAGINAS_ATIVAS)
            paginas_ativas_count = len([p for p in settings.PAGINAS_ATIVAS.values() if p["ativa"]])
            st.markdown(f"**📊 Páginas:** {paginas_ativas_count}/{total_paginas} ativas")
        
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
                <p><strong>Dashboard Estoque TI v2.0</strong> | Desenvolvido com ❤️ e tecnologias modernas</p>
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