"""
Dashboard Estoque TI 

"""

# ✅ CARREGAR VARIÁVEIS DE AMBIENTE PRIMEIRO - ANTES DE TUDO!
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os

# Configuração de logging
from loguru import logger
logger.add("logs/dashboard.log", rotation="1 week", retention="1 month", level="INFO")

# Imports dos serviços e configurações
from config.settings import settings
from services import EstoqueService, get_service_info
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
            # Obter informações do banco de dados
            service_info = get_service_info()
            db_status = "🐘 PostgreSQL" if service_info['tipo'] in ['PostgreSQL', 'SQLite'] else "📊 Excel"
            persistente = "✅ Persistente" if service_info.get('persistente', False) else "⚠️ Temporário"
            
            st.markdown(f"""
            **Versão:** 3.0.0 + PostgreSQL 🐘  
            **Banco de Dados:** {db_status}  
            **Status:** {persistente}
            
            **Tecnologias:**
            - Streamlit 1.42+
            - Plotly 5.21+ 
            - Pandas 2.2+
            - Pydantic 2.5+
            - SQLAlchemy 2.0+
            - Sistema de Autenticação
            
            **Recursos Modernos:**
            - Interface responsiva
            - Notificações toast
            - Gráficos com bordas arredondadas
            - Validação de dados
            - Logs estruturados
            - Sistema de login seguro
            - {'Dados persistentes 🔒' if service_info.get('persistente') else 'Excel (dados temporários)'}
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