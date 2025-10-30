"""
Página de configurações da aplicação
"""

import streamlit as st
from typing import Dict, Any
from loguru import logger

from config.settings import settings
from utils.ui_utils import (
    create_form_section,
    show_success_message,
    show_info_message,
    show_error_message
)
from services.estoque_service import EstoqueService

class ConfiguracoesPage:
    """Página de configurações da aplicação"""
    
    def __init__(self):
        self.estoque_service = EstoqueService()
    
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
            
            # Seção de gerenciamento de códigos duplicados
            self._render_codigo_duplicado_config()
            
            # Seção de informações do sistema
            self._render_system_info()
            
        except Exception as e:
            logger.error(f"Erro ao renderizar página de configurações: {str(e)}")
            st.error("Erro ao carregar configurações.")
    
    def _render_codigo_duplicado_config(self) -> None:
        """Renderiza seção para gerenciar códigos duplicados"""
        create_form_section(
            "🏷️ Gerenciamento de Códigos de Produto",
            "Configure a política de códigos únicos e gerencie códigos duplicados"
        )
        
        # Configuração atual
        col_config, col_status = st.columns(2)
        
        with col_config:
            st.subheader("⚙️ Configuração Atual")
            if settings.CODIGO_UNICO_OBRIGATORIO:
                st.success("✅ **Códigos únicos obrigatórios**")
                st.info("Cada produto deve ter um código único, independente da condição (Novo/Usado)")
            else:
                st.warning("⚠️ **Códigos podem ser compartilhados**")
                st.info("Produtos diferentes podem ter o mesmo código se tiverem condições diferentes")
        
        with col_status:
            st.subheader("📊 Status dos Códigos")
            try:
                codigos_duplicados = self.estoque_service.listar_codigos_duplicados()
                if codigos_duplicados:
                    st.error(f"❌ **{len(codigos_duplicados)} códigos duplicados encontrados**")
                    with st.expander("Ver códigos duplicados"):
                        for codigo in codigos_duplicados:
                            st.write(f"• {codigo}")
                else:
                    st.success("✅ **Nenhum código duplicado encontrado**")
            except Exception as e:
                st.error(f"Erro ao verificar códigos: {str(e)}")
        
        # Ferramentas de gerenciamento
        st.subheader("🛠️ Ferramentas de Gerenciamento")
        
        col_tool1, col_tool2, col_tool3 = st.columns(3)
        
        with col_tool1:
            if st.button("🔍 Verificar Duplicados", use_container_width=True):
                self._verificar_codigos_duplicados()
        
        with col_tool2:
            if st.button("📋 Listar Equipamentos", use_container_width=True):
                self._listar_todos_equipamentos()
        
        with col_tool3:
            if st.button("🧹 Limpar Dados Teste", use_container_width=True):
                self._confirmar_limpeza_dados()
    
    def _verificar_codigos_duplicados(self) -> None:
        """Verifica e exibe códigos duplicados detalhadamente"""
        try:
            df_estoque = self.estoque_service.obter_equipamentos()
            if df_estoque.empty:
                show_info_message("📭 Nenhum equipamento cadastrado.")
                return
            
            codigos_duplicados = self.estoque_service.listar_codigos_duplicados()
            
            if not codigos_duplicados:
                show_success_message("✅ Nenhum código duplicado encontrado!")
                return
            
            st.subheader("🚨 Códigos Duplicados Detectados")
            
            for codigo in codigos_duplicados:
                with st.expander(f"Código: {codigo}"):
                    produtos_mesmo_codigo = df_estoque[df_estoque['codigo_produto'] == codigo]
                    
                    for _, produto in produtos_mesmo_codigo.iterrows():
                        col_info, col_acao = st.columns([3, 1])
                        
                        with col_info:
                            st.write(f"**ID:** {produto['id']}")
                            st.write(f"**Produto:** {produto['equipamento']}")
                            st.write(f"**Marca:** {produto['marca']} - **Modelo:** {produto['modelo']}")
                            st.write(f"**Condição:** {produto['condicao']} - **Quantidade:** {produto['quantidade']}")
                        
                        with col_acao:
                            if st.button(f"🗑️ Remover", key=f"remove_{produto['id']}"):
                                self._remover_equipamento(produto['id'])
                        
                        st.divider()
            
        except Exception as e:
            show_error_message(f"Erro ao verificar códigos: {str(e)}")
    
    def _listar_todos_equipamentos(self) -> None:
        """Lista todos os equipamentos cadastrados"""
        try:
            df_estoque = self.estoque_service.obter_equipamentos()
            if df_estoque.empty:
                show_info_message("📭 Nenhum equipamento cadastrado.")
                return
            
            st.subheader("📦 Todos os Equipamentos")
            st.dataframe(
                df_estoque[['id', 'codigo_produto', 'equipamento', 'marca', 'modelo', 'condicao', 'quantidade']],
                use_container_width=True
            )
            
        except Exception as e:
            show_error_message(f"Erro ao listar equipamentos: {str(e)}")
    
    def _confirmar_limpeza_dados(self) -> None:
        """Confirma limpeza de dados de teste"""
        st.subheader("⚠️ Limpar Dados de Teste")
        st.warning("Esta ação removerá TODOS os equipamentos cadastrados. Use apenas para limpar dados de teste antes de usar em produção.")
        
        if st.checkbox("Confirmo que quero remover TODOS os equipamentos"):
            if st.button("🗑️ CONFIRMAR LIMPEZA TOTAL", type="primary"):
                self._executar_limpeza_total()
    
    def _remover_equipamento(self, equipamento_id: int) -> None:
        """Remove um equipamento específico"""
        try:
            response = self.estoque_service.remover_equipamento_por_id(equipamento_id)
            if response.success:
                show_success_message(response.message)
                st.rerun()
            else:
                show_error_message(response.message)
        except Exception as e:
            show_error_message(f"Erro ao remover equipamento: {str(e)}")
    
    def _executar_limpeza_total(self) -> None:
        """Executa limpeza total dos dados"""
        try:
            # Criar DataFrames vazios
            df_estoque_vazio = self.estoque_service.excel_service._criar_dados_iniciais()[0]
            df_movimentacoes_vazio = self.estoque_service.excel_service._criar_dados_iniciais()[1]
            
            # Salvar dados vazios
            self.estoque_service.excel_service.salvar_dados(df_estoque_vazio, df_movimentacoes_vazio)
            
            # Recarregar dados no serviço
            self.estoque_service.recarregar_dados()
            
            show_success_message("✅ Todos os dados foram removidos com sucesso! Sistema pronto para uso em produção.")
            st.rerun()
            
        except Exception as e:
            show_error_message(f"Erro ao limpar dados: {str(e)}")
    
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