"""
Página de Login Moderna - Dashboard Estoque TI
Interface elegante com validação e feedback visual
"""

import streamlit as st
from datetime import datetime
from auth.auth_service import auth_service
from utils.ui_utils import show_success_message, show_error_message, show_toast

class LoginPage:
    """Página de login com interface moderna"""
    
    def __init__(self):
        self.setup_page_config()
    
    def setup_page_config(self):
        """Configuração específica da página de login"""
        # CSS personalizado para login
        login_css = """
        <style>
        /* ===== ESTILO ESPECÍFICO PARA LOGIN ===== */
        .login-container {
            background: linear-gradient(135deg, #0e1117 0%, #1a1a2e 50%, #16213e 100%);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0, 212, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-top: 2rem;
        }
        
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        .login-title {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #00d4ff, #4ade80);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        
        .login-subtitle {
            color: #e0e0e0;
            font-size: 1.1rem;
            margin-bottom: 1rem;
        }
        
        .login-form {
            max-width: 400px;
            margin: 0 auto;
        }
        
        .user-info-card {
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
        }
        
        .demo-credentials {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
        }
        </style>
        """
        st.markdown(login_css, unsafe_allow_html=True)
    
    def render(self) -> None:
        """Renderiza a página de login"""
        
        # Container principal
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Header
        self._render_header()
        
        # Verificar se já está logado
        if auth_service.is_authenticated():
            self._render_already_logged_in()
        else:
            # Formulário de login
            self._render_login_form()
            
            # Informações de segurança
            self._render_security_info()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_header(self) -> None:
        """Renderiza cabeçalho da página"""
        st.markdown(
            '''
            <div class="login-header">
                <h1 class="login-title">🔐 Dashboard Estoque TI</h1>
                <p class="login-subtitle">Sistema Seguro de Gerenciamento de Estoque</p>
                <p style="color: #888; font-size: 0.9rem;">Faça login para acessar o sistema</p>
            </div>
            ''', 
            unsafe_allow_html=True
        )
    
    def _render_already_logged_in(self) -> None:
        """Renderiza tela quando usuário já está logado"""
        user = auth_service.get_current_user()
        
        st.markdown('<div class="user-info-card">', unsafe_allow_html=True)
        st.success(f"✅ **Você já está conectado como:** {user.display_name}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("🚪 Logout", use_container_width=True):
                auth_service.logout()
                show_toast("👋 Logout realizado!", "🚪")
                st.rerun()
        
        with col2:
            if st.button("📊 Ir para Dashboard", use_container_width=True, type="primary"):
                st.switch_page("app.py")  # Voltar para app principal
        
        with col3:
            st.metric("Perfil", user.profile.title())
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Informações do usuário
        with st.expander("ℹ️ Informações da Sessão"):
            st.markdown(f"""
            **👤 Usuário:** {user.username}
            **🎯 Perfil:** {user.profile.title()}
            **📋 Permissões:** {len(user.permissions)} recursos
            **🕐 Login:** {st.session_state.get('login_time', 'N/A')}
            **🔒 Tentativas:** {auth_service.get_login_attempts(user.username)}
            """)
    
    def _render_login_form(self) -> None:
        """Renderiza formulário de login"""
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 👤 Credenciais de Acesso")
            
            # Campos de login
            username = st.text_input(
                "👤 Usuário:",
                placeholder="Digite seu usuário",
                help="Entre em contato com o administrador para obter credenciais"
            )
            
            password = st.text_input(
                "🔐 Senha:",
                type="password",
                placeholder="Digite sua senha",
                help="Use a senha fornecida pelo administrador"
            )
            
            # Checkbox "Lembrar-me" (decorativo por enquanto)
            remember_me = st.checkbox("🔄 Lembrar-me neste dispositivo")
            
            # Botão de login
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                login_clicked = st.form_submit_button(
                    "🔐 Fazer Login",
                    use_container_width=True,
                    type="primary"
                )
            
            # Processar login
            if login_clicked:
                self._process_login(username, password, remember_me)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _render_security_info(self) -> None:
        """Renderiza informações de segurança"""
        st.markdown('<div class="demo-credentials">', unsafe_allow_html=True)
        
        st.markdown("### 🔒 **Sistema de Segurança Ativo**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🛡️ PROTEÇÕES ATIVAS**
            - 🔐 **Senhas criptografadas** (bcrypt)
            - 🚦 **Rate limiting** (5 tentativas/15min)
            - 🧹 **Sanitização** de inputs
            - 📊 **Logs de auditoria** completos
            """)
        
        with col2:
            st.markdown("""
            **👥 PERFIS DISPONÍVEIS**  
            - 👑 **Administrador** - Acesso completo
            - 👀 **Visualizador** - Somente leitura
            - 🔒 **Credenciais** fornecidas pelo admin
            - 📋 **Permissões** granulares por perfil
            """)
        
        st.warning("⚠️ **Atenção:** Credenciais são fornecidas pelo administrador do sistema. Entre em contato se não possui acesso.")
        
        # Informações de contato (opcional)
        with st.expander("📞 Solicitar Acesso"):
            st.markdown("""
            **Para obter credenciais de acesso:**
            
            1. 📧 **Email:** hytalo.souza@novoatacarejo.com
            2. 📱 **Telefone:** --
            3. 💬 **Teams/Slack:** #suporte-ti
            4. 🎫 **Ticket:** Sistema de chamados interno
            
            **Informações necessárias:**
            - Nome completo
            - Cargo/Função
            - Tipo de acesso necessário (Visualizador)
            - Justificativa de uso
            """)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def _process_login(self, username: str, password: str, remember_me: bool) -> None:
        """Processa tentativa de login"""
        
        # Validações básicas
        if not username or not password:
            show_error_message("❌ Por favor, preencha usuário e senha")
            return
        
        # Loading visual
        with st.spinner('🔄 Verificando credenciais...'):
            user = auth_service.authenticate(username, password)
        
        if user:
            # ✅ LOGIN BEM-SUCEDIDO
            st.session_state.authenticated_user = user
            st.session_state.login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if remember_me:
                st.session_state.auth_remember_me = True
            
            show_success_message(
                f"🎉 **Login realizado com sucesso!**\n\n"
                f"**Bem-vindo:** {user.display_name}\n"
                f"**Perfil:** {user.profile.title()}\n"
                f"**Permissões:** {len(user.permissions)} recursos disponíveis"
            )
            
            show_toast(f"👋 Bem-vindo, {user.display_name}!", "🎉")
            
            # Aguardar um momento e redirecionar
            import time
            time.sleep(1)
            st.rerun()
            
        else:
            # ❌ LOGIN FALHOU
            show_error_message(
                "❌ **Credenciais inválidas!**\n\n"
                "Verifique se o usuário e senha estão corretos.\n"
                "Entre em contato com o administrador se não possui acesso."
            )
            
            show_toast("❌ Login falhou!", "🚫")

def render_login_page() -> None:
    """Função para renderizar a página de login"""
    login_page = LoginPage()
    login_page.render()
