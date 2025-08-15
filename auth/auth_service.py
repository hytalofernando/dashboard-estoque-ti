"""
Serviço de Autenticação - Dashboard Estoque TI
Sistema simples e seguro com Admin e Visualizador
"""

import streamlit as st
import hashlib
from typing import Dict, Optional, List
from dataclasses import dataclass
from loguru import logger

@dataclass
class User:
    """Modelo de usuário"""
    username: str
    profile: str
    display_name: str
    permissions: List[str]

class AuthService:
    """Serviço de autenticação com perfis Admin e Visualizador"""
    
    def __init__(self):
        # ✅ USUÁRIOS PREDEFINIDOS (em produção, usar banco de dados)
        self.users_db = {
            "admin": {
                "password_hash": self._hash_password("admin123"),
                "profile": "administrador",
                "display_name": "Administrador",
                "permissions": [
                    "dashboard", "adicionar", "remover", "historico", 
                    "codigos", "configuracoes", "can_edit"
                ]
            },
            "visualizador": {
                "password_hash": self._hash_password("view123"),
                "profile": "visualizador", 
                "display_name": "Visualizador",
                "permissions": [
                    "dashboard", "historico", "codigos", "configuracoes"
                    # ❌ NÃO tem "adicionar", "remover", "can_edit"
                ]
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash da senha usando SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Autentica usuário e retorna dados se válido"""
        try:
            username = username.lower().strip()
            
            if username not in self.users_db:
                logger.warning(f"Tentativa de login com usuário inexistente: {username}")
                return None
            
            user_data = self.users_db[username]
            password_hash = self._hash_password(password)
            
            if password_hash == user_data["password_hash"]:
                logger.info(f"Login bem-sucedido: {username} ({user_data['profile']})")
                
                return User(
                    username=username,
                    profile=user_data["profile"],
                    display_name=user_data["display_name"],
                    permissions=user_data["permissions"]
                )
            else:
                logger.warning(f"Senha incorreta para usuário: {username}")
                return None
                
        except Exception as e:
            logger.error(f"Erro na autenticação: {str(e)}")
            return None
    
    def is_authenticated(self) -> bool:
        """Verifica se usuário está autenticado"""
        return 'authenticated_user' in st.session_state and st.session_state.authenticated_user is not None
    
    def get_current_user(self) -> Optional[User]:
        """Retorna usuário atual ou None"""
        if self.is_authenticated():
            return st.session_state.authenticated_user
        return None
    
    def has_permission(self, permission: str) -> bool:
        """Verifica se usuário atual tem permissão específica"""
        user = self.get_current_user()
        if not user:
            return False
        return permission in user.permissions
    
    def can_edit(self) -> bool:
        """Verifica se usuário pode editar (adicionar/remover)"""
        return self.has_permission("can_edit")
    
    def logout(self) -> None:
        """Faz logout do usuário"""
        if 'authenticated_user' in st.session_state:
            user = st.session_state.authenticated_user
            logger.info(f"Logout realizado: {user.username if user else 'usuário desconhecido'}")
            del st.session_state.authenticated_user
        
        # Limpar outras informações da sessão relacionadas à autenticação
        keys_to_remove = [k for k in st.session_state.keys() if k.startswith('auth_')]
        for key in keys_to_remove:
            del st.session_state[key]
    
    def get_filtered_pages(self) -> Dict[str, Dict]:
        """Retorna páginas filtradas baseadas nas permissões do usuário"""
        from config.settings import settings
        
        user = self.get_current_user()
        if not user:
            return {}
        
        filtered_pages = {}
        
        for key, page_info in settings.PAGINAS_ATIVAS.items():
            # Se a página está ativa E o usuário tem permissão
            if page_info["ativa"] and key in user.permissions:
                filtered_pages[key] = page_info.copy()
                
                # ✅ ADICIONAR FLAG DE SOMENTE LEITURA PARA VISUALIZADORES
                if not self.can_edit() and key in ["adicionar", "remover"]:
                    filtered_pages[key]["readonly"] = True
                else:
                    filtered_pages[key]["readonly"] = False
        
        return filtered_pages
    
    def get_user_stats(self) -> Dict[str, str]:
        """Estatísticas do usuário para exibição"""
        user = self.get_current_user()
        if not user:
            return {}
        
        return {
            "username": user.username,
            "display_name": user.display_name,
            "profile": user.profile,
            "permissions_count": len(user.permissions),
            "can_edit": "✅" if self.can_edit() else "❌",
            "login_time": st.session_state.get('login_time', 'N/A')
        }

# ✅ INSTÂNCIA GLOBAL DO SERVIÇO
auth_service = AuthService()
