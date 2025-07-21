"""
Página de configurações da aplicação
"""

import streamlit as st
from typing import Dict, Any
from loguru import logger

from config.settings import settings
from utils.ui_utils import (
    create_form_section, show_success_message, show_info_message,
    create_action_buttons
)

class ConfiguracoesPage:
    """Página de configurações da aplicação"""
    
    def __init__(self):
        pass
    
    def render(self) -> None:
        """Renderiza a página de configurações"""
        try:
            # Header da página
            st.markdown("# ⚙️ Configurações da Aplicação")
            st.markdown("Configure as funcionalidades e páginas da aplicação conforme suas necessidades.")
            st.markdown("---")
            
            # Seção de configuração de páginas
            self._render_page_config()
            
            # Seção de configurações gerais
            self._render_general_config()
            
            # Seção de informações do sistema
            self._render_system_info()
            
        except Exception as e:
            logger.error(f"Erro ao renderizar página de configurações: {str(e)}")
            st.error("Erro ao carregar configurações.")
    
    def _render_page_config(self) -> None:
        """Renderiza configurações de páginas"""
        create_form_section(
            "📱 Gerenciamento de Páginas",
            "Ative ou desative páginas conforme necessário para sua organização"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔧 Configurar Páginas Ativas")
            
            changes_made = False
            original_states = {}
            
            for key, info in settings.PAGINAS_ATIVAS.items():
                original_states[key] = info["ativa"]
                
                new_state = st.checkbox(
                    f"{info['titulo']}",
                    value=info["ativa"],
                    key=f"config_page_{key}",
                    help=info["descricao"]
                )
                
                if new_state != info["ativa"]:
                    settings.PAGINAS_ATIVAS[key]["ativa"] = new_state
                    changes_made = True
            
            if changes_made:
                show_success_message("Configurações de páginas atualizadas!")
                logger.info("Configurações de páginas modificadas pelo usuário")
        
        with col2:
            st.markdown("### 📊 Status das Páginas")
            
            total_paginas = len(settings.PAGINAS_ATIVAS)
            ativas = len([p for p in settings.PAGINAS_ATIVAS.values() if p["ativa"]])
            inativas = total_paginas - ativas
            
            st.metric("Total de Páginas", total_paginas)
            st.metric("Páginas Ativas", ativas, delta=None)
            st.metric("Páginas Inativas", inativas)
            
            # Progresso visual
            progress = ativas / total_paginas if total_paginas > 0 else 0
            st.progress(progress, text=f"Utilização: {progress:.1%}")
            
            # Lista de páginas ativas
            st.markdown("**📋 Páginas Ativas:**")
            for key, info in settings.PAGINAS_ATIVAS.items():
                if info["ativa"]:
                    st.markdown(f"✅ {info['titulo']}")
                else:
                    st.markdown(f"❌ {info['titulo']}")
    
    def _render_general_config(self) -> None:
        """Renderiza configurações gerais"""
        st.markdown("---")
        create_form_section(
            "🔧 Configurações Gerais",
            "Ajustes gerais da aplicação"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📁 Configurações de Arquivo")
            st.text_input("Nome do arquivo Excel", value=settings.EXCEL_FILE, disabled=True)
            st.text_input("Planilha de Estoque", value=settings.SHEET_ESTOQUE, disabled=True)
            st.text_input("Planilha de Movimentações", value=settings.SHEET_MOVIMENTACOES, disabled=True)
            
            st.markdown("### 🎨 Configurações Visuais")
            st.text_input("Título da Página", value=settings.PAGE_TITLE, disabled=True)
            st.text_input("Ícone da Página", value=settings.PAGE_ICON, disabled=True)
        
        with col2:
            st.markdown("### 📊 Limites de Validação")
            st.number_input("Quantidade Máxima", value=settings.MAX_QUANTIDADE, disabled=True)
            st.number_input("Valor Mínimo", value=settings.MIN_VALOR, disabled=True)
            st.number_input("Máx. Caracteres Observações", value=settings.MAX_OBSERVACOES, disabled=True)
            
            st.markdown("### 🏷️ Categorias Disponíveis")
            for categoria in settings.CATEGORIAS:
                st.markdown(f"• {categoria}")
    
    def _render_system_info(self) -> None:
        """Renderiza informações do sistema"""
        st.markdown("---")
        create_form_section(
            "ℹ️ Informações do Sistema",
            "Detalhes técnicos e status da aplicação"
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🚀 Versão")
            st.markdown("**Dashboard Estoque TI**")
            st.markdown("Versão: 2.0.0 Moderna")
            st.markdown("Status: ✅ Ativo")
        
        with col2:
            st.markdown("### 💻 Tecnologias")
            st.markdown("• Streamlit 1.42+")
            st.markdown("• Plotly 5.21+")
            st.markdown("• Pandas 2.2+")
            st.markdown("• Pydantic 2.5+")
            st.markdown("• Loguru 0.7+")
        
        with col3:
            st.markdown("### 🎯 Recursos")
            st.markdown("• Interface responsiva")
            st.markdown("• Notificações toast")
            st.markdown("• Gráficos modernos")
            st.markdown("• Validação de dados")
            st.markdown("• Logs estruturados")
        
        # Ações rápidas
        st.markdown("---")
        st.markdown("### 🔧 Ações Rápidas")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Recarregar Configurações", type="secondary"):
                st.rerun()
        
        with col2:
            if st.button("✅ Ativar Todas as Páginas", type="secondary"):
                for key in settings.PAGINAS_ATIVAS:
                    settings.PAGINAS_ATIVAS[key]["ativa"] = True
                show_success_message("Todas as páginas foram ativadas!")
                st.rerun()
        
        with col3:
            if st.button("❌ Desativar Páginas Opcionais", type="secondary"):
                # Manter apenas Dashboard ativo
                for key in settings.PAGINAS_ATIVAS:
                    if key != "dashboard":
                        settings.PAGINAS_ATIVAS[key]["ativa"] = False
                show_info_message("Páginas opcionais desativadas. Apenas Dashboard ativo.")
                st.rerun()
        
        with col4:
            if st.button("🔄 Resetar Configurações", type="secondary"):
                for key in settings.PAGINAS_ATIVAS:
                    settings.PAGINAS_ATIVAS[key]["ativa"] = True
                show_success_message("Configurações resetadas para padrão!")
                st.rerun()

def render_configuracoes_page() -> None:
    """Função para renderizar a página de configurações"""
    page = ConfiguracoesPage()
    page.render() 