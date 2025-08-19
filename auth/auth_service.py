"""
Serviço de Autenticação - Dashboard Estoque TI
Sistema seguro com Admin e Visualizador - Versão Aprimorada com bcrypt
"""

import streamlit as st
import os
from typing import Dict, Optional, List
from dataclasses import dataclass
from loguru import logger
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from utils.security_utils import PasswordManager, RateLimiter

@dataclass
class User:
    """Modelo de usuário aprimorado"""
    username: str
    profile: str
    display_name: str
    permissions: List[str]
    last_login: Optional[datetime] = None
    login_attempts: int = 0

class AuthService:
    """Serviço de autenticação seguro com perfis Admin e Visualizador"""
    
    def __init__(self):
        # Inicializar componentes de segurança
        self.rate_limiter = RateLimiter(max_requests=5, window_minutes=15)  # 5 tentativas por 15 min
        self.password_manager = PasswordManager()
        
        # ✅ SENHAS SEGURAS COM VARIÁVEIS DE AMBIENTE
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123_CHANGE_ME')
        viewer_password = os.getenv('VIEWER_PASSWORD', 'view123_CHANGE_ME')
        
        # ⚠️ AVISO DE SEGURANÇA
        if admin_password == 'admin123_CHANGE_ME' or viewer_password == 'view123_CHANGE_ME':
            logger.warning("🔒 ATENÇÃO: Usando senhas padrão! Configure as variáveis de ambiente.")
        
        # ✅ USUÁRIOS COM HASHES SEGUROS
        self.users_db = {
            "admin": {
                "password_hash": self._get_or_create_password_hash("admin", admin_password),
                "profile": "administrador",
                "display_name": "Administrador",
                "permissions": [
                    "dashboard", "adicionar", "remover", "historico", 
                    "codigos", "configuracoes", "can_edit"
                ],
                "login_attempts": 0,
                "last_login": None,
                "created_at": datetime.now()
            },
            "visualizador": {
                "password_hash": self._get_or_create_password_hash("visualizador", viewer_password),
                "profile": "visualizador", 
                "display_name": "Visualizador",
                "permissions": [
                    "dashboard", "historico", "codigos", "configuracoes"
                    # ❌ NÃO tem "adicionar", "remover", "can_edit"
                ],
                "login_attempts": 0,
                "last_login": None,
                "created_at": datetime.now()
            }
        }
        
        logger.info("🔐 AuthService inicializado com segurança aprimorada")
    
    def _get_or_create_password_hash(self, username: str, password: str) -> str:
        """
        Obtém ou cria hash da senha de forma segura
        
        Args:
            username: Nome do usuário
            password: Senha em texto plano
            
        Returns:
            Hash seguro da senha
        """
        # Verifica se já existe hash no session_state (cache)
        cache_key = f"password_hash_{username}"
        
        if cache_key in st.session_state:
            return st.session_state[cache_key]
        
        # Gera novo hash
        password_hash = self.password_manager.hash_password(password)
        
        # Salva no cache da sessão
        st.session_state[cache_key] = password_hash
        
        logger.info(f"🔐 Hash de senha gerado para usuário: {username}")
        return password_hash
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        Autentica usuário com validações de segurança
        
        Args:
            username: Nome do usuário
            password: Senha
            
        Returns:
            Objeto User se autenticado, None caso contrário
        """
        try:
            # Sanitizar entrada
            username = username.lower().strip() if username else ""
            
            # ✅ VERIFICAR RATE LIMITING
            client_ip = self._get_client_identifier()
            if not self.rate_limiter.is_allowed(f"login_{client_ip}"):
                logger.warning(f"🚨 Rate limit excedido para IP: {client_ip}")
                return None
            
            # Verificar se usuário existe
            if username not in self.users_db:
                logger.warning(f"🚨 Tentativa de login com usuário inexistente: {username}")
                self._log_failed_attempt(username, "user_not_found")
                return None
            
            user_data = self.users_db[username]
            
            # ✅ VERIFICAR TENTATIVAS DE LOGIN
            if user_data.get("login_attempts", 0) >= 5:
                logger.warning(f"🚨 Usuário bloqueado por muitas tentativas: {username}")
                return None
            
            # ✅ VERIFICAR SENHA COM BCRYPT
            if self.password_manager.verify_password(password, user_data["password_hash"]):
                # ✅ LOGIN BEM-SUCEDIDO
                logger.info(f"✅ Login bem-sucedido: {username} ({user_data['profile']})")
                
                # Resetar tentativas e atualizar último login
                self.users_db[username]["login_attempts"] = 0
                self.users_db[username]["last_login"] = datetime.now()
                
                # Criar objeto User
                user = User(
                    username=username,
                    profile=user_data["profile"],
                    display_name=user_data["display_name"],
                    permissions=user_data["permissions"],
                    last_login=user_data["last_login"]
                )
                
                # Log de auditoria
                self._log_successful_login(user)
                
                return user
            else:
                # ❌ SENHA INCORRETA
                logger.warning(f"🚨 Senha incorreta para usuário: {username}")
                self._log_failed_attempt(username, "wrong_password")
                
                # Incrementar tentativas
                self.users_db[username]["login_attempts"] += 1
                
                return None
                
        except Exception as e:
            logger.error(f"❌ Erro na autenticação: {str(e)}")
            return None
    
    def _get_client_identifier(self) -> str:
        """
        Obtém identificador único do cliente para rate limiting
        
        Returns:
            Identificador do cliente
        """
        # Em produção, usar IP real do cliente
        # Por enquanto, usar session_id do Streamlit
        try:
            # Tentar obter session_id
            if hasattr(st, 'session_state') and hasattr(st.session_state, 'session_id'):
                return f"session_{st.session_state.session_id}"
            else:
                # Fallback para identificador baseado em timestamp
                if 'client_identifier' not in st.session_state:
                    st.session_state.client_identifier = f"client_{datetime.now().timestamp()}"
                return st.session_state.client_identifier
        except:
            return "unknown_client"
    
    def _log_failed_attempt(self, username: str, reason: str) -> None:
        """
        Registra tentativa de login falhada
        
        Args:
            username: Nome do usuário
            reason: Motivo da falha
        """
        logger.warning(f"🚨 Login falhado - Usuário: {username}, Motivo: {reason}, IP: {self._get_client_identifier()}")
    
    def _log_successful_login(self, user: User) -> None:
        """
        Registra login bem-sucedido para auditoria
        
        Args:
            user: Objeto do usuário
        """
        logger.info(f"✅ Auditoria - Login: {user.username} ({user.profile}), IP: {self._get_client_identifier()}, Timestamp: {datetime.now()}")
    
    def is_authenticated(self) -> bool:
        """Verifica se usuário está autenticado"""
        return 'authenticated_user' in st.session_state and st.session_state.authenticated_user is not None
    
    def get_current_user(self) -> Optional[User]:
        """Retorna usuário atual ou None"""
        if self.is_authenticated():
            return st.session_state.authenticated_user
        return None
    
    def has_permission(self, permission: str) -> bool:
        """
        Verifica se usuário atual tem permissão específica
        
        Args:
            permission: Permissão a verificar
            
        Returns:
            True se tem permissão
        """
        user = self.get_current_user()
        if not user:
            return False
        return permission in user.permissions
    
    def can_edit(self) -> bool:
        """Verifica se usuário pode editar (adicionar/remover)"""
        return self.has_permission("can_edit")
    
    def logout(self) -> None:
        """Realiza logout do usuário"""
        user = self.get_current_user()
        if user:
            logger.info(f"🚪 Logout: {user.username}")
        
        # Limpar dados da sessão
        keys_to_clear = [
            'authenticated_user', 
            'login_timestamp',
            'session_token'
        ]
        
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]
    
    def get_login_attempts(self, username: str) -> int:
        """
        Retorna número de tentativas de login falhadas
        
        Args:
            username: Nome do usuário
            
        Returns:
            Número de tentativas
        """
        if username in self.users_db:
            return self.users_db[username].get("login_attempts", 0)
        return 0
    
    def reset_login_attempts(self, username: str) -> bool:
        """
        Reseta tentativas de login (função administrativa)
        
        Args:
            username: Nome do usuário
            
        Returns:
            True se resetado com sucesso
        """
        if username in self.users_db:
            self.users_db[username]["login_attempts"] = 0
            logger.info(f"🔄 Tentativas de login resetadas para: {username}")
            return True
        return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """
        Retorna informações do usuário (sem dados sensíveis)
        
        Args:
            username: Nome do usuário
            
        Returns:
            Dicionário com informações do usuário
        """
        if username in self.users_db:
            user_data = self.users_db[username].copy()
            # Remove dados sensíveis
            user_data.pop("password_hash", None)
            return user_data
        return None
    
    def get_filtered_pages(self) -> Dict:
        """
        Retorna páginas filtradas baseadas nas permissões do usuário atual
        
        Returns:
            Dicionário com páginas que o usuário pode acessar
        """
        from config.settings import settings
        
        user = self.get_current_user()
        if not user:
            # Se não estiver autenticado, retorna apenas dashboard
            return {
                "dashboard": settings.PAGINAS_ATIVAS["dashboard"]
            }
        
        # Filtrar páginas baseado nas permissões do usuário
        paginas_filtradas = {}
        
        for page_key, page_info in settings.PAGINAS_ATIVAS.items():
            # Verificar se a página está ativa nas configurações
            if not page_info.get("ativa", False):
                continue
                
            # Verificar permissões específicas
            if page_key == "dashboard" and self.has_permission("dashboard"):
                paginas_filtradas[page_key] = page_info
            elif page_key == "adicionar" and self.has_permission("adicionar"):
                paginas_filtradas[page_key] = page_info
            elif page_key == "remover" and self.has_permission("remover"):
                paginas_filtradas[page_key] = page_info
            elif page_key == "historico" and self.has_permission("historico"):
                paginas_filtradas[page_key] = page_info
            elif page_key == "codigos" and self.has_permission("codigos"):
                paginas_filtradas[page_key] = page_info
            elif page_key == "configuracoes" and self.has_permission("configuracoes"):
                paginas_filtradas[page_key] = page_info
        
        return paginas_filtradas

# Instância global do serviço de autenticação
auth_service = AuthService()