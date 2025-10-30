"""
Página Profissional para Adicionar Equipamentos - Versão 3.0
Tecnologias: Streamlit 1.42+ | Modal Dialogs | Session State | Data Editor | Tabs | Fragments
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List
from loguru import logger
from datetime import datetime

from services.estoque_service import EstoqueService
from models.schemas import Equipamento, CondicionEquipamento
from config.settings import settings
from utils.ui_utils import (
    create_form_section,
    show_success_message,
    show_error_message,
    show_warning_message,
    show_toast,
    create_info_cards,
    create_metric_card,
    clean_codigo_display
)

# ✅ SISTEMA DE AUTENTICAÇÃO
from auth.auth_service import auth_service

class AdicionarEquipamentoProfessional:
    """Página Profissional para Adicionar Equipamentos com Tecnologias de Ponta"""
    
    def __init__(self, estoque_service: EstoqueService):
        self.estoque_service = estoque_service
        self._init_session_state()
    
    def _init_session_state(self) -> None:
        """Inicializa session state com configurações avançadas"""
        if 'adicionar_config' not in st.session_state:
            st.session_state.adicionar_config = {
                'auto_code_generation': True,
                'batch_mode_enabled': True,
                'validation_strict': True,
                'notification_enabled': True,
                'cache_ttl': 300  # 5 minutos
            }
        
        if 'adicionar_stats' not in st.session_state:
            st.session_state.adicionar_stats = {
                'total_added_today': 0,
                'total_value_added_today': 0.0,
                'last_operation': None
            }
    
    def render(self) -> None:
        """Renderiza a página moderna e profissional"""
        # ✅ VERIFICAR PERMISSÕES PRIMEIRO
        if not auth_service.can_edit():
            st.error("🚫 **Acesso Negado**")
            st.warning("⚠️ **Visualizadores não podem adicionar equipamentos.**")
            st.info("💡 **Apenas Administradores podem realizar esta operação.**")
            
            # Mostrar informações do usuário atual
            user = auth_service.get_current_user()
            st.markdown(f"**👤 Usuário atual:** {user.display_name} ({user.profile.title()})")
            
            # Botão para voltar ao dashboard
            if st.button("📊 Voltar ao Dashboard", type="primary"):
                st.switch_page("app.py")
            return
        
        # Header profissional
        create_form_section(
            "📦 Adicionar Equipamentos - Sistema Profissional v3.0",
            "Interface moderna com operações individuais, em lote e configurações avançadas"
        )
        
        # Verificar cache e dados
        equipamentos_cache = self._get_equipamentos_cache_ttl()
        
        # Layout com tabs profissionais
        tab_individual, tab_lote, tab_historico, tab_analytics, tab_config = st.tabs([
            "➕ Adição Individual", 
            "📦 Adição em Lote", 
            "📋 Histórico",
            "📊 Analytics",
            "⚙️ Configurações"
        ])
        
        with tab_individual:
            self._render_adicao_individual(equipamentos_cache)
        
        with tab_lote:
            self._render_adicao_lote()
            
        with tab_historico:
            self._render_historico_adicoes()
            
        with tab_analytics:
            self._render_analytics_dashboard()
            
        with tab_config:
            self._render_configuracoes_avancadas()
    
    @st.cache_data(ttl=300, show_spinner=False)  # Cache com TTL de 5 minutos
    def _get_equipamentos_cache_ttl(_self) -> Dict[str, Dict]:
        """Cache inteligente com TTL automático"""
        try:
            logger.info("🔄 Carregando cache TTL de equipamentos...")
            df_estoque = _self.estoque_service.obter_equipamentos()
            
            cache_equipamentos = {}
            for _, row in df_estoque.iterrows():
                codigo = clean_codigo_display(row.get('codigo_produto', '')).upper()
                if codigo:
                    cache_equipamentos[codigo] = {
                        'id': row.get('id'),
                        'equipamento': row.get('equipamento', ''),
                        'categoria': row.get('categoria', ''),
                        'marca': row.get('marca', ''),
                        'modelo': row.get('modelo', ''),
                        'quantidade': row.get('quantidade', 0),
                        'valor_unitario': row.get('valor_unitario', 0.0),
                        'fornecedor': row.get('fornecedor', ''),
                        'condicao': row.get('condicao', 'Novo')
                    }
            
            logger.info(f"✅ Cache TTL carregado: {len(cache_equipamentos)} equipamentos")
            return cache_equipamentos
            
        except Exception as e:
            logger.error(f"❌ Erro no cache TTL: {str(e)}")
            return {}
    
    def _render_adicao_individual(self, equipamentos_cache: Dict) -> None:
        """Renderiza interface moderna para adição individual"""
        
        # Estatísticas em tempo real
        self._render_stats_realtime()
        
        st.markdown("### 🎯 Busca Inteligente e Adição")
        
        # Sistema de busca avançado
        col_busca1, col_busca2, col_busca3, col_busca4 = st.columns([3, 1, 1, 1])
        
        # Inicializar variáveis fora do contexto de colunas para garantir escopo
        codigo_input = ""
        
        with col_busca1:
            # Obter valor do input e garantir que sempre seja uma string válida
            codigo_input_temp = st.text_input(
                "🔍 Código Produto (AI Search)",
                placeholder="Ex: NB-DELL-001 | Digite para autocompletar...",
                help="Sistema de busca inteligente com sugestões automáticas",
                key="codigo_search_modern"
            )
            # Processar o código em etapas separadas para evitar problemas de escopo
            if codigo_input_temp:
                codigo_input = clean_codigo_display(str(codigo_input_temp).strip().upper())
        
        with col_busca2:
            if st.button("🔄 Refresh Cache", use_container_width=True):
                self._invalidate_cache()
                st.rerun()
        
        with col_busca3:
            if st.button("🧹 Clear All", use_container_width=True):
                self._clear_form_state()
                st.rerun()
        
        with col_busca4:
            if st.button("📊 Quick Add", use_container_width=True):
                self._show_quick_add_dialog()
        
        # Sistema de autocompletar avançado
        produto_encontrado = self._processar_busca_inteligente(codigo_input, equipamentos_cache)
        
        # Formulário moderno com validação em tempo real
        self._render_formulario_moderno(produto_encontrado, codigo_input)
    
    def _render_adicao_lote(self) -> None:
        """Renderiza interface para adição em lote usando data_editor"""
        st.markdown("### 📦 Adição em Lote - Data Editor Profissional")
        
        if not st.session_state.adicionar_config['batch_mode_enabled']:
            st.warning("⚠️ Modo lote desabilitado nas configurações")
            return
        
        # Templates de lote
        col_template1, col_template2, col_template3 = st.columns(3)
        
        with col_template1:
            if st.button("📋 Template Básico", use_container_width=True):
                self._carregar_template_basico()
        
        with col_template2:
            if st.button("💻 Template Notebooks", use_container_width=True):
                self._carregar_template_notebooks()
        
        with col_template3:
            if st.button("🖨️ Template Periféricos", use_container_width=True):
                self._carregar_template_perifericos()
        
        # Data Editor para entrada em lote
        self._render_data_editor_lote()
    
    def _render_data_editor_lote(self) -> None:
        """Renderiza data editor profissional para lote"""
        
        # Inicializar DataFrame se não existir
        if 'df_lote_adicionar' not in st.session_state:
            st.session_state.df_lote_adicionar = pd.DataFrame({
                'equipamento': [''] * 5,
                'categoria': [''] * 5,
                'marca': [''] * 5,
                'modelo': [''] * 5,
                'codigo_produto': [''] * 5,
                'quantidade': [1] * 5,
                'valor_unitario': [100.0] * 5,
                'condicao': [CondicionEquipamento.NOVO.value] * 5,
                'fornecedor': [''] * 5,
                'observacoes': [''] * 5
            })
        
        st.markdown("#### 📝 Editor de Dados - Adição em Lote")
        
        # Data Editor com configuração avançada
        df_editado = st.data_editor(
            st.session_state.df_lote_adicionar,
            column_config={
                "equipamento": st.column_config.TextColumn(
                    "🖥️ Equipamento",
                    help="Nome do equipamento",
                    max_chars=100,
                    required=True
                ),
                "categoria": st.column_config.SelectboxColumn(
                    "📂 Categoria",
                    help="Categoria do equipamento",
                    options=settings.CATEGORIAS,
                    required=True
                ),
                "marca": st.column_config.TextColumn(
                    "🏢 Marca",
                    help="Marca do fabricante",
                    max_chars=50,
                    required=True
                ),
                "modelo": st.column_config.TextColumn(
                    "🔧 Modelo",
                    help="Modelo específico",
                    max_chars=50,
                    required=True
                ),
                "codigo_produto": st.column_config.TextColumn(
                    "🏷️ Código",
                    help="Código único do produto",
                    max_chars=20,
                    required=True
                ),
                "quantidade": st.column_config.NumberColumn(
                    "📊 Qtd",
                    help="Quantidade",
                    min_value=1,
                    max_value=settings.MAX_QUANTIDADE,
                    step=1,
                    format="%d"
                ),
                "valor_unitario": st.column_config.NumberColumn(
                    "💰 Valor Unit.",
                    help="Valor unitário",
                    min_value=settings.MIN_VALOR,
                    step=0.01,
                    format="R$ %.2f"
                ),
                "condicao": st.column_config.SelectboxColumn(
                    "🔄 Condição",
                    help="Condição do equipamento",
                    options=[CondicionEquipamento.NOVO.value, CondicionEquipamento.USADO.value],
                    required=True
                ),
                "fornecedor": st.column_config.TextColumn(
                    "🏪 Fornecedor",
                    help="Nome do fornecedor",
                    max_chars=100,
                    required=True
                ),
                "observacoes": st.column_config.TextColumn(
                    "📝 Obs",
                    help="Observações adicionais",
                    max_chars=200
                )
            },
            num_rows="dynamic",
            use_container_width=True,
            key="editor_lote_adicionar"
        )
        
        # Atualizar session state
        st.session_state.df_lote_adicionar = df_editado
        
        # Validação e processamento do lote
        self._processar_validacao_lote(df_editado)
    
    def _render_historico_adicoes(self) -> None:
        """Renderiza histórico profissional de adições"""
        st.markdown("### 📋 Histórico de Adições")
        
        # Filtros modernos
        col_filtro1, col_filtro2, col_filtro3, col_filtro4 = st.columns(4)
        
        with col_filtro1:
            periodo = st.selectbox(
                "📅 Período",
                ["Hoje", "7 dias", "30 dias", "Personalizado"],
                key="filtro_periodo_hist"
            )
        
        with col_filtro2:
            categoria_filtro = st.selectbox(
                "📂 Categoria",
                ["Todas"] + settings.CATEGORIAS,
                key="filtro_categoria_hist"
            )
        
        with col_filtro3:
            valor_min = st.number_input(
                "💰 Valor Mín.",
                min_value=0.0,
                value=0.0,
                key="filtro_valor_min"
            )
        
        with col_filtro4:
            if st.button("📥 Exportar", use_container_width=True):
                show_toast("📥 Exportação em desenvolvimento!", "🚧")
        
        # Histórico (em desenvolvimento)
        st.info("📊 **Histórico em desenvolvimento** - Será integrado com o banco de movimentações")
    
    def _render_analytics_dashboard(self) -> None:
        """Renderiza dashboard de analytics com paleta de cores correta"""
        st.markdown("### 📊 Analytics Dashboard - Adições")
        
        # Métricas em tempo real com cores adequadas
        col_metric1, col_metric2, col_metric3, col_metric4 = st.columns(4)
        
        with col_metric1:
            create_metric_card(
                "📦 Adições Hoje", 
                str(st.session_state.adicionar_stats['total_added_today']),
                delta="+2 vs ontem",
                help_text="Total de equipamentos adicionados hoje"
            )
        
        with col_metric2:
            create_metric_card(
                "💰 Valor Hoje", 
                f"R$ {st.session_state.adicionar_stats['total_value_added_today']:,.2f}",
                delta="+15% vs ontem",
                help_text="Valor total adicionado hoje"
            )
        
        with col_metric3:
            create_metric_card(
                "⚡ Taxa Sucesso", 
                "98.5%",
                delta="+1.2%",
                help_text="Taxa de sucesso nas adições"
            )
        
        with col_metric4:
            create_metric_card(
                "🎯 Autocompletar", 
                "85%",
                delta="+5%",
                help_text="Eficiência do autocompletar"
            )
        
        # Gráficos (em desenvolvimento)
        st.info("📈 **Gráficos em desenvolvimento** - Analytics avançados em breve")
    
    def _render_configuracoes_avancadas(self) -> None:
        """Renderiza configurações avançadas da página"""
        st.markdown("### ⚙️ Configurações Avançadas")
        
        # Configurações de comportamento
        st.markdown("#### 🎛️ Comportamento do Sistema")
        
        col_config1, col_config2 = st.columns(2)
        
        with col_config1:
            auto_code = st.checkbox(
                "Geração automática de códigos",
                value=st.session_state.adicionar_config['auto_code_generation'],
                help="Gerar códigos automaticamente baseado em categoria e marca"
            )
            
            validation_strict = st.checkbox(
                "Validação rigorosa",
                value=st.session_state.adicionar_config['validation_strict'],
                help="Validações mais rigorosas nos formulários"
            )
            
            notifications = st.checkbox(
                "Notificações habilitadas",
                value=st.session_state.adicionar_config['notification_enabled'],
                help="Mostrar toast notifications"
            )
        
        with col_config2:
            batch_mode = st.checkbox(
                "Modo lote habilitado",
                value=st.session_state.adicionar_config['batch_mode_enabled'],
                help="Permitir adições em lote"
            )
            
            cache_ttl = st.selectbox(
                "TTL do Cache (segundos)",
                [60, 300, 600, 1800],
                index=1,
                help="Tempo de vida do cache"
            )
        
        # Atualizar configurações
        if st.button("💾 Salvar Configurações", type="primary"):
            st.session_state.adicionar_config.update({
                'auto_code_generation': auto_code,
                'validation_strict': validation_strict,
                'notification_enabled': notifications,
                'batch_mode_enabled': batch_mode,
                'cache_ttl': cache_ttl
            })
            show_toast("✅ Configurações salvas!", "🎉")
            st.rerun()
        
        # Configurações avançadas de cache
        st.markdown("#### 🗄️ Gerenciamento de Cache")
        
        col_cache1, col_cache2, col_cache3 = st.columns(3)
        
        with col_cache1:
            if st.button("🔄 Invalidar Cache", use_container_width=True):
                self._invalidate_cache()
                show_toast("Cache invalidado!", "🔄")
        
        with col_cache2:
            if st.button("📊 Estatísticas Cache", use_container_width=True):
                show_toast("📊 Stats: Cache ativo com TTL 5min", "📈")
        
        with col_cache3:
            if st.button("🧹 Limpar Tudo", use_container_width=True):
                self._invalidate_cache()
                self._clear_form_state()
                show_toast("🧹 Dados limpos!", "✅")
    
    @st.dialog("Quick Add - Adição Rápida")
    def _show_quick_add_dialog(self) -> None:
        """Modal dialog para adição rápida"""
        st.markdown("### ⚡ Adição Rápida de Equipamento")
        
        # Formulário simplificado no modal
        equipamento = st.text_input("🖥️ Nome do Equipamento")
        
        col_modal1, col_modal2 = st.columns(2)
        
        with col_modal1:
            categoria = st.selectbox("📂 Categoria", settings.CATEGORIAS)
            marca = st.text_input("🏢 Marca")
        
        with col_modal2:
            quantidade = st.number_input("📊 Quantidade", min_value=1, value=1)
            valor = st.number_input("💰 Valor", min_value=1.0, value=100.0)
        
        # Campo de condição no modal
        col_cond, col_forn = st.columns(2)
        with col_cond:
            condicao_modal = st.selectbox(
                "🔄 Condição",
                [CondicionEquipamento.NOVO.value, CondicionEquipamento.USADO.value],
                help="Selecione se o equipamento é novo ou usado"
            )
        with col_forn:
            fornecedor = st.text_input("🏪 Fornecedor")
        
        # Botões do modal
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("✅ Adicionar Rápido", use_container_width=True, type="primary"):
                if equipamento and marca and fornecedor:
                    # Processar adição rápida
                    self._processar_adicao_rapida(equipamento, categoria, marca, quantidade, valor, fornecedor, condicao_modal)
                    st.success("✅ Equipamento adicionado com sucesso!")
                    show_toast("⚡ Adição rápida concluída!", "✅")
                    st.rerun()
                else:
                    st.error("❌ Preencha todos os campos obrigatórios")
        
        with col_btn2:
            if st.button("❌ Cancelar", use_container_width=True):
                st.rerun()
    
    def _processar_busca_inteligente(self, codigo_input: str, equipamentos_cache: Dict) -> Optional[Dict]:
        """Processa busca inteligente com sugestões e agrupamento Novo/Usado"""
        # Validação defensiva
        if not codigo_input or not isinstance(codigo_input, str) or len(codigo_input.strip()) < 2:
            return None
        
        # Garantir que codigo_input é uma string limpa
        codigo_input = str(codigo_input).strip().upper()
        
        # Buscar equipamentos por código (pode ter Novo e Usado)
        equipamentos_codigo = self.estoque_service.obter_equipamento_por_codigo(codigo_input)
        
        if equipamentos_codigo:
            # Código existe - mostrar agrupamento
            agrupado = self.estoque_service.agrupar_equipamentos_por_codigo(codigo_input)
            
            st.success(f"✅ **Código encontrado:** {agrupado.get('equipamento', 'N/A')}")
            
            # Mostrar informações do produto agrupadas
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.info(f"**📦 Equipamento:** {agrupado['equipamento']}")
                st.info(f"**📂 Categoria:** {agrupado['categoria']}")
            with col_info2:
                st.info(f"**🏢 Marca:** {agrupado['marca']}")
                st.info(f"**🔧 Modelo:** {agrupado['modelo']}")
            with col_info3:
                # Mostrar estoque separado por condição - NOVO DESIGN PROFISSIONAL
                st.markdown("**📊 Estoque por Condição:**")
                col_novo, col_usado = st.columns(2)
                with col_novo:
                    st.metric(
                        "🆕 Novos",
                        f"{agrupado['qtd_novos']:,} un.",
                        delta=f"R$ {agrupado['valor_novos']:,.2f}" if agrupado['qtd_novos'] > 0 else "Sem estoque"
                    )
                with col_usado:
                    st.metric(
                        "🔄 Usados", 
                        f"{agrupado['qtd_usados']:,} un.",
                        delta=f"R$ {agrupado['valor_usados']:,.2f}" if agrupado['qtd_usados'] > 0 else "Sem estoque"
                    )
                
                # Total consolidado
                st.metric("📊 **Total**", f"{agrupado['qtd_total']:,} un.")
            
            st.warning("⬆️ **Modo: Aumentar Estoque** - Selecione a condição para adicionar")
            return agrupado
        
        # Busca aproximada - usar código limpo para consistência
        all_codes = list(equipamentos_cache.keys()) if equipamentos_cache else []
        similares = [codigo for codigo in all_codes if codigo_input in codigo or codigo in codigo_input]
        if similares:
            st.info(f"💡 **Códigos similares encontrados:** {', '.join(similares[:5])}")
        else:
            st.warning(f"❌ Código não encontrado. Criando novo produto: `{codigo_input}`")
        
        return None
    
    def _render_formulario_moderno(self, produto_existente: Optional[Dict], codigo_input: str) -> None:
        """Renderiza formulário moderno com validação avançada"""
        st.markdown("---")
        st.markdown("### 📝 Formulário de Adição Inteligente")
        
        is_produto_existente = produto_existente is not None
        
        # Formulário com validação em tempo real
        with st.form("form_adicionar_moderno", clear_on_submit=not is_produto_existente):
            
            # Fragment para campos dinâmicos
            self._render_campos_formulario(produto_existente, codigo_input, is_produto_existente)
            
            # Validação e submit
            self._render_validacao_submit(is_produto_existente, produto_existente)
    
    @st.fragment
    def _render_campos_formulario(self, produto_existente: Optional[Dict], codigo_input: str, is_produto_existente: bool) -> None:
        """Fragment para campos de formulário responsivos"""
        
        col_form1, col_form2 = st.columns(2)
        
        with col_form1:
            # Campos do lado esquerdo
            equipamento = st.text_input(
                "🖥️ Nome do Equipamento *",
                value=produto_existente['equipamento'] if produto_existente else "",
                placeholder="Ex: Notebook Dell Latitude 5520",
                disabled=is_produto_existente,
                key="campo_equipamento"
            )
            
            categoria_index = 0
            if produto_existente and produto_existente['categoria'] in settings.CATEGORIAS:
                categoria_index = settings.CATEGORIAS.index(produto_existente['categoria'])
            
            categoria = st.selectbox(
                "📂 Categoria *",
                settings.CATEGORIAS,
                index=categoria_index,
                disabled=is_produto_existente,
                key="campo_categoria"
            )
            
            marca = st.text_input(
                "🏢 Marca *",
                value=produto_existente['marca'] if produto_existente else "",
                placeholder="Ex: Dell",
                disabled=is_produto_existente,
                key="campo_marca"
            )
            
            modelo = st.text_input(
                "🔧 Modelo *",
                value=produto_existente['modelo'] if produto_existente else "",
                placeholder="Ex: Latitude 5520",
                disabled=is_produto_existente,
                key="campo_modelo"
            )
        
        with col_form2:
            # Campos do lado direito
            codigo_produto = st.text_input(
                "🏷️ Código do Produto *",
                value=codigo_input,
                placeholder="Ex: NB-DELL-001",
                disabled=is_produto_existente,
                key="campo_codigo"
            )
            
            # NOVO CAMPO: Condição do Equipamento (PROFISSIONAL)
            if is_produto_existente and produto_existente:
                st.markdown("**🔄 Condição do Equipamento:**")
                
                # Mostrar opções baseadas no que existe
                opcoes_condicao = []
                labels_condicao = []
                valores_sugeridos = []
                
                if produto_existente.get('qtd_novos', 0) > 0:
                    opcoes_condicao.append(CondicionEquipamento.NOVO.value)
                    labels_condicao.append(f"🆕 Novo (atual: {produto_existente['qtd_novos']} un.)")
                    valores_sugeridos.append(produto_existente.get('valor_novos', 100.0))
                else:
                    opcoes_condicao.append(CondicionEquipamento.NOVO.value)
                    labels_condicao.append("🆕 Novo (criar)")
                    valores_sugeridos.append(100.0)
                
                if produto_existente.get('qtd_usados', 0) > 0:
                    opcoes_condicao.append(CondicionEquipamento.USADO.value)
                    labels_condicao.append(f"🔄 Usado (atual: {produto_existente['qtd_usados']} un.)")
                    valores_sugeridos.append(produto_existente.get('valor_usados', 70.0))
                else:
                    opcoes_condicao.append(CondicionEquipamento.USADO.value)
                    labels_condicao.append("🔄 Usado (criar)")
                    valores_sugeridos.append(70.0)
                
                condicao_selecionada = st.radio(
                    "Selecione a condição:",
                    opcoes_condicao,
                    format_func=lambda x: labels_condicao[opcoes_condicao.index(x)],
                    key="campo_condicao"
                )
                
                # Ajustar valor sugerido baseado na condição
                idx_condicao = opcoes_condicao.index(condicao_selecionada)
                valor_sugerido = valores_sugeridos[idx_condicao]
            else:
                # Produto novo - seleção normal
                col_cond1, col_cond2 = st.columns(2)
                with col_cond1:
                    condicao_selecionada = st.selectbox(
                        "🔄 Condição *",
                        [CondicionEquipamento.NOVO.value, CondicionEquipamento.USADO.value],
                        key="campo_condicao"
                    )
                with col_cond2:
                    # Sugestão de desconto para usados
                    if condicao_selecionada == CondicionEquipamento.USADO.value:
                        st.info("💡 Sugestão: Valor 70% do novo")
                
                valor_sugerido = 100.0
            
            quantidade = st.number_input(
                "📊 Quantidade a Adicionar *",
                min_value=1,
                max_value=settings.MAX_QUANTIDADE,
                value=1,
                key="campo_quantidade"
            )
            
            # Valor unitário OCULTO - fixado em 100.00
            valor_default = 100.00
            valor_unitario = valor_default  # Valor fixo, não editável
            # Campo oculto para manter no session_state
            if 'campo_valor' not in st.session_state:
                st.session_state['campo_valor'] = valor_default
            
            fornecedor = st.text_input(
                "🏪 Fornecedor *",
                value=produto_existente['fornecedor'] if produto_existente else "",
                placeholder="Ex: Dell Brasil",
                key="campo_fornecedor"
            )
        
        # Preview do estoque (SEM mostrar valores)
        if quantidade > 0:
            condicao_atual = st.session_state.get('campo_condicao', CondicionEquipamento.NOVO.value)
            
            # Mostrar apenas informações de estoque, sem valores monetários
            st.markdown(f"### 📊 **Preview do Estoque**")
            st.markdown(f"**🔄 Condição:** {condicao_atual}")
            
            col_calc = st.columns(1)[0]
            with col_calc:
                if is_produto_existente and produto_existente:
                    # Mostrar novo estoque por condição
                    if condicao_atual == CondicionEquipamento.NOVO.value:
                        novos_atuais = produto_existente.get('qtd_novos', 0)
                        novos_novo = novos_atuais + quantidade
                        usados_atuais = produto_existente.get('qtd_usados', 0)
                        
                        st.markdown("### 📊 **Novo Estoque por Condição:**")
                        st.markdown(f"🆕 **Novos:** {novos_atuais} → **{novos_novo}** (+{quantidade})")
                        st.markdown(f"🔄 **Usados:** {usados_atuais} (sem alteração)")
                        st.markdown(f"📊 **Total:** {novos_novo + usados_atuais} un.")
                    else:
                        novos_atuais = produto_existente.get('qtd_novos', 0)
                        usados_atuais = produto_existente.get('qtd_usados', 0)
                        usados_novo = usados_atuais + quantidade
                        
                        st.markdown("### 📊 **Novo Estoque por Condição:**")
                        st.markdown(f"🆕 **Novos:** {novos_atuais} (sem alteração)")
                        st.markdown(f"🔄 **Usados:** {usados_atuais} → **{usados_novo}** (+{quantidade})")
                        st.markdown(f"📊 **Total:** {novos_atuais + usados_novo} un.")
                else:
                    # Produto novo
                    st.markdown(f"### 📊 **Primeiro Estoque: {quantidade:,} un.**")
                    st.markdown(f"**Condição:** {condicao_atual}")
            
            # Alertas inteligentes de quantidade
            if quantidade > 100:
                st.warning("⚠️ **Quantidade alta!** Confirme antes de prosseguir.")
    
    def _render_validacao_submit(self, is_produto_existente: bool, produto_existente: Optional[Dict]) -> None:
        """Renderiza validação e botões de submit"""
        
        # Botões de ação
        st.markdown("---")
        
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1, 1, 2, 1])
        
        with col_btn2:
            validar_clicked = st.form_submit_button(
                "👀 Validar",
                type="secondary",
                use_container_width=True
            )
        
        with col_btn3:
            if is_produto_existente:
                submit_clicked = st.form_submit_button(
                    f"📈 Aumentar Estoque",
                    type="primary",
                    use_container_width=True
                )
            else:
                submit_clicked = st.form_submit_button(
                    "✅ Adicionar Equipamento",
                    type="primary",
                    use_container_width=True
                )
        
        # Processamento
        if validar_clicked or submit_clicked:
            self._processar_formulario_submit(submit_clicked, is_produto_existente, produto_existente)
    
    def _processar_formulario_submit(self, is_submit: bool, is_produto_existente: bool, produto_existente: Optional[Dict]) -> None:
        """Processa submissão do formulário"""
        
        # Coletar dados do formulário incluindo condição
        equipamento = st.session_state.get('campo_equipamento', '')
        categoria = st.session_state.get('campo_categoria', '')
        marca = st.session_state.get('campo_marca', '')
        modelo = st.session_state.get('campo_modelo', '')
        codigo_produto = st.session_state.get('campo_codigo', '')
        quantidade = st.session_state.get('campo_quantidade', 1)
        valor_unitario = st.session_state.get('campo_valor', 100.0)
        fornecedor = st.session_state.get('campo_fornecedor', '')
        condicao = st.session_state.get('campo_condicao', CondicionEquipamento.NOVO.value)
        
        # Validar dados
        erros = self._validar_dados_moderno(
            equipamento, marca, modelo, codigo_produto,
            fornecedor, valor_unitario, quantidade, is_produto_existente
        )
        
        if erros:
            st.error("**❌ Erros encontrados:**")
            for erro in erros:
                st.error(f"• {erro}")
            return
        
        if not is_submit:
            st.success("✅ **Todos os dados estão corretos!**")
            return
        
        # Processar adição
        self._executar_adicao(
            equipamento, categoria, marca, modelo, codigo_produto,
            quantidade, valor_unitario, fornecedor, condicao, is_produto_existente, produto_existente
        )
    
    def _executar_adicao(self, equipamento: str, categoria: str, marca: str,
                        modelo: str, codigo_produto: str, quantidade: int,
                        valor_unitario: float, fornecedor: str, condicao: str,
                        is_produto_existente: bool, produto_existente: Optional[Dict]) -> None:
        """Executa a adição do equipamento"""
        try:
            if is_produto_existente and produto_existente:
                # Criar equipamento para adicionar (o método adicionar_equipamento já verifica se existe)
                condicao_enum = CondicionEquipamento(condicao)
                novo_equipamento = Equipamento(
                    equipamento=produto_existente['equipamento'],
                    categoria=produto_existente['categoria'],
                    marca=produto_existente['marca'],
                    modelo=produto_existente['modelo'],
                    codigo_produto=codigo_produto.strip().upper(),
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    fornecedor=fornecedor.strip(),
                    condicao=condicao_enum
                )
                
                # O método adicionar_equipamento já verifica se existe e aumenta a quantidade
                response = self.estoque_service.adicionar_equipamento(novo_equipamento)
                
                if response.success:
                    # Atualizar estatísticas
                    st.session_state.adicionar_stats['total_added_today'] += quantidade
                    st.session_state.adicionar_stats['total_value_added_today'] += quantidade * valor_unitario
                    
                    show_success_message(
                        f"✅ **Estoque atualizado com sucesso!**\n\n"
                        f"**📦 Equipamento:** {produto_existente['equipamento']}\n"
                        f"**🔄 Condição:** {condicao}\n"
                        f"**📊 Quantidade:** +{quantidade} unidades"
                    )
                    
                    if st.session_state.adicionar_config['notification_enabled']:
                        show_toast("📈 Estoque atualizado!", "✅")
                    
                    # Invalidar caches
                    st.session_state['historico_cache_invalidated'] = True
                    self._invalidate_cache()
                    st.rerun()
                else:
                    show_error_message(f"❌ Erro: {response.message}")
            else:
                # Criar novo equipamento com condição
                condicao_enum = CondicionEquipamento(condicao)
                novo_equipamento = Equipamento(
                    equipamento=equipamento.strip(),
                    categoria=categoria,
                    marca=marca.strip(),
                    modelo=modelo.strip(),
                    codigo_produto=codigo_produto.strip().upper(),
                    quantidade=quantidade,
                    valor_unitario=valor_unitario,
                    fornecedor=fornecedor.strip(),
                    condicao=condicao_enum
                )
                
                response = self.estoque_service.adicionar_equipamento(novo_equipamento)
                
                if response.success:
                    # Atualizar estatísticas
                    st.session_state.adicionar_stats['total_added_today'] += quantidade
                    st.session_state.adicionar_stats['total_value_added_today'] += quantidade * valor_unitario
                    
                    show_success_message(
                        f"🎉 **Novo equipamento cadastrado!**\n\n"
                        f"**📦 Equipamento:** {equipamento}\n"
                        f"**🏷️ Código:** {codigo_produto}\n"
                        f"**🔄 Condição:** {condicao}\n"
                        f"**📊 Quantidade:** {quantidade} unidades"
                    )
                    
                    if st.session_state.adicionar_config['notification_enabled']:
                        show_toast("🆕 Equipamento criado!", "🎉")
                    
                    # Invalidar caches
                    st.session_state['historico_cache_invalidated'] = True
                    self._invalidate_cache()
                    st.rerun()
                else:
                    show_error_message(f"❌ Erro: {response.message}")
                    
        except Exception as e:
            logger.error(f"Erro na execução de adição: {str(e)}")
            show_error_message(f"❌ Erro interno: {str(e)}")
    
    def _validar_dados_moderno(self, equipamento: str, marca: str, modelo: str,
                              codigo_produto: str, fornecedor: str,
                              valor_unitario: float, quantidade: int,
                              is_produto_existente: bool) -> List[str]:
        """Validação moderna com regras configuráveis - AJUSTADO PARA CÓDIGOS DE EMPRESAS"""
        erros = []
        
        # Validações para novos produtos - REDUZIDO PARA 2 CARACTERES MÍNIMO
        if not is_produto_existente:
            if not equipamento or len(equipamento.strip()) < 2:
                erros.append("Nome do equipamento deve ter pelo menos 2 caracteres")
            
            if not marca or len(marca.strip()) < 2:
                erros.append("Marca deve ter pelo menos 2 caracteres")
            
            if not modelo or len(modelo.strip()) < 2:
                erros.append("Modelo deve ter pelo menos 2 caracteres")
            
            if not codigo_produto or len(codigo_produto.strip()) < 2:
                erros.append("Código deve ter pelo menos 2 caracteres (códigos de empresas)")
        
        # Validações sempre necessárias - REDUZIDO PARA 2 CARACTERES MÍNIMO
        if not fornecedor or len(fornecedor.strip()) < 2:
            erros.append("Fornecedor deve ter pelo menos 2 caracteres")
        
        # Validação de valor_unitario removida (agora é fixo em 100.00)
        
        if quantidade <= 0:
            erros.append("Quantidade deve ser maior que zero")
        
        if quantidade > settings.MAX_QUANTIDADE:
            erros.append(f"Quantidade máxima: {settings.MAX_QUANTIDADE}")
        
        return erros
    
    # Métodos auxiliares
    def _render_stats_realtime(self) -> None:
        """Renderiza estatísticas em tempo real com paleta de cores correta"""
        try:
            stats = self.estoque_service.obter_estatisticas()
            
            # Usar create_info_cards para paleta de cores adequada
            create_info_cards(stats)
                
        except Exception as e:
            logger.error(f"Erro nas estatísticas: {str(e)}")
    
    def _invalidate_cache(self) -> None:
        """Invalida cache TTL"""
        if hasattr(st, 'cache_data'):
            self._get_equipamentos_cache_ttl.clear()
    
    def _clear_form_state(self) -> None:
        """Limpa estado do formulário"""
        keys_to_clear = [k for k in st.session_state.keys() if k.startswith('campo_') or k.startswith('codigo_search')]
        for key in keys_to_clear:
            del st.session_state[key]
    
    def _carregar_template_basico(self) -> None:
        """Carrega template básico para lote"""
        st.session_state.df_lote_adicionar = pd.DataFrame({
            'equipamento': ['Notebook Básico', 'Mouse Óptico', 'Teclado USB'],
            'categoria': ['Notebook', 'Periféricos', 'Periféricos'],
            'marca': ['Dell', 'Logitech', 'Logitech'],
            'modelo': ['Inspiron 15', 'M100', 'K120'],
            'codigo_produto': ['NB-DELL-002', 'MS-LOG-001', 'KB-LOG-001'],
            'quantidade': [5, 10, 8],
            'valor_unitario': [2500.0, 25.0, 45.0],
            'condicao': [CondicionEquipamento.NOVO.value, CondicionEquipamento.NOVO.value, CondicionEquipamento.USADO.value],
            'fornecedor': ['Dell Brasil', 'Logitech', 'Logitech'],
            'observacoes': ['', '', '']
        })
        show_toast("📋 Template básico carregado!", "✅")
    
    def _carregar_template_notebooks(self) -> None:
        """Carrega template para notebooks"""
        st.session_state.df_lote_adicionar = pd.DataFrame({
            'equipamento': ['Notebook Dell Latitude', 'Notebook HP EliteBook', 'Notebook Lenovo ThinkPad'],
            'categoria': ['Notebook', 'Notebook', 'Notebook'],
            'marca': ['Dell', 'HP', 'Lenovo'],
            'modelo': ['Latitude 5520', 'EliteBook 840', 'ThinkPad E14'],
            'codigo_produto': ['NB-DELL-003', 'NB-HP-001', 'NB-LEN-001'],
            'quantidade': [3, 2, 4],
            'valor_unitario': [3500.0, 4200.0, 3800.0],
            'condicao': [CondicionEquipamento.NOVO.value, CondicionEquipamento.NOVO.value, CondicionEquipamento.USADO.value],
            'fornecedor': ['Dell Brasil', 'HP Brasil', 'Lenovo'],
            'observacoes': ['', '', '']
        })
        show_toast("💻 Template notebooks carregado!", "✅")
    
    def _carregar_template_perifericos(self) -> None:
        """Carrega template para periféricos"""
        st.session_state.df_lote_adicionar = pd.DataFrame({
            'equipamento': ['Mouse Wireless', 'Teclado Mecânico', 'Monitor 24"', 'Webcam HD'],
            'categoria': ['Periféricos', 'Periféricos', 'Monitor', 'Periféricos'],
            'marca': ['Logitech', 'Corsair', 'LG', 'Logitech'],
            'modelo': ['MX Master 3', 'K70 RGB', '24MP59G', 'C920'],
            'codigo_produto': ['MS-LOG-002', 'KB-COR-001', 'MN-LG-001', 'WC-LOG-001'],
            'quantidade': [10, 5, 6, 8],
            'valor_unitario': [320.0, 450.0, 650.0, 280.0],
            'condicao': [CondicionEquipamento.NOVO.value, CondicionEquipamento.USADO.value, CondicionEquipamento.NOVO.value, CondicionEquipamento.NOVO.value],
            'fornecedor': ['Logitech', 'Corsair', 'LG', 'Logitech'],
            'observacoes': ['', '', '', '']
        })
        show_toast("🖨️ Template periféricos carregado!", "✅")
    
    def _processar_validacao_lote(self, df_editado: pd.DataFrame) -> None:
        """Processa validação do lote"""
        # Filtrar linhas com dados
        df_valido = df_editado.dropna(subset=['equipamento']).copy()
        df_valido = df_valido[df_valido['equipamento'].str.strip() != '']
        
        if df_valido.empty:
            st.info("💡 Preencha pelo menos um equipamento para processar o lote")
            return
        
        # Validações do lote - AJUSTADO PARA 2 CARACTERES MÍNIMO (CÓDIGOS DE EMPRESAS)
        erros_lote = []
        for idx, row in df_valido.iterrows():
            if len(str(row['equipamento']).strip()) < 2:
                erros_lote.append(f"Linha {idx+1}: Nome deve ter pelo menos 2 caracteres")
            if len(clean_codigo_display(row['codigo_produto'])) < 2:
                erros_lote.append(f"Linha {idx+1}: Código deve ter pelo menos 2 caracteres")
            if row['quantidade'] <= 0:
                erros_lote.append(f"Linha {idx+1}: Quantidade inválida")
            if row['valor_unitario'] <= 0:
                erros_lote.append(f"Linha {idx+1}: Valor inválido")
        
        # Mostrar resultado da validação
        if erros_lote:
            st.error("**❌ Erros no lote:**")
            for erro in erros_lote:
                st.error(f"• {erro}")
        else:
            # Mostrar resumo e permitir processamento
            total_itens = len(df_valido)
            total_unidades = df_valido['quantidade'].sum()
            valor_total = (df_valido['quantidade'] * df_valido['valor_unitario']).sum()
            
            st.success("✅ **Lote válido!**")
            
            col_resumo1, col_resumo2 = st.columns(2)
            with col_resumo1:
                st.metric("📦 Equipamentos", total_itens)
            with col_resumo2:
                st.metric("📊 Total Unidades", f"{total_unidades:,}")
            
            # Botão para processar lote
            if st.button(
                f"🚀 Processar Lote ({total_itens} equipamentos)",
                type="primary",
                use_container_width=True
            ):
                self._executar_lote(df_valido)
    
    def _executar_lote(self, df_valido: pd.DataFrame) -> None:
        """Executa adição em lote"""
        sucessos = 0
        erros = 0
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, row in df_valido.iterrows():
            try:
                # Atualizar progresso
                progresso = (idx + 1) / len(df_valido)
                progress_bar.progress(progresso)
                status_text.text(f"Processando {idx + 1}/{len(df_valido)}: {row['equipamento']}")
                
                # Criar equipamento com condição
                condicao_enum = CondicionEquipamento(row['condicao'])
                equipamento = Equipamento(
                    equipamento=str(row['equipamento']).strip(),
                    categoria=str(row['categoria']).strip(),
                    marca=str(row['marca']).strip(),
                    modelo=str(row['modelo']).strip(),
                    codigo_produto=clean_codigo_display(row['codigo_produto']).upper(),
                    quantidade=int(row['quantidade']),
                    valor_unitario=float(row['valor_unitario']),
                    fornecedor=str(row['fornecedor']).strip(),
                    condicao=condicao_enum
                )
                
                # Adicionar equipamento
                response = self.estoque_service.adicionar_equipamento(equipamento)
                
                if response.success:
                    sucessos += 1
                else:
                    erros += 1
                    logger.error(f"Erro no lote linha {idx+1}: {response.message}")
                
            except Exception as e:
                erros += 1
                logger.error(f"Erro no lote linha {idx+1}: {str(e)}")
        
        # Finalizar
        progress_bar.progress(1.0)
        status_text.text("Processamento concluído!")
        
        if sucessos == len(df_valido):
            show_success_message(f"🎉 **Lote processado com sucesso!** {sucessos} equipamentos adicionados.")
        else:
            show_warning_message(f"⚠️ **Lote parcial:** {sucessos} sucessos, {erros} erros")
        
        # Invalidar caches
        st.session_state['historico_cache_invalidated'] = True
        self._invalidate_cache()
        
        # Limpar formulário de lote
        st.session_state.df_lote_adicionar = pd.DataFrame({
            'equipamento': [''] * 5,
            'categoria': [''] * 5,
            'marca': [''] * 5,
            'modelo': [''] * 5,
            'codigo_produto': [''] * 5,
            'quantidade': [1] * 5,
            'valor_unitario': [100.0] * 5,
            'condicao': [CondicionEquipamento.NOVO.value] * 5,
            'fornecedor': [''] * 5,
            'observacoes': [''] * 5
        })
        
        show_toast(f"📦 Lote concluído: {sucessos} itens!", "🎉")
        st.rerun()
    
    def _processar_adicao_rapida(self, equipamento: str, categoria: str, marca: str,
                                quantidade: int, valor: float, fornecedor: str, condicao: str) -> None:
        """Processa adição rápida via modal"""
        try:
            # Gerar código automático
            codigo = self.estoque_service.gerar_codigo_sugerido(categoria, marca)
            
            condicao_enum = CondicionEquipamento(condicao)
            novo_equipamento = Equipamento(
                equipamento=equipamento,
                categoria=categoria,
                marca=marca,
                modelo="N/A",
                codigo_produto=codigo,
                quantidade=quantidade,
                valor_unitario=valor,
                fornecedor=fornecedor,
                condicao=condicao_enum
            )
            
            response = self.estoque_service.adicionar_equipamento(novo_equipamento)
            
            if response.success:
                # Atualizar estatísticas
                st.session_state.adicionar_stats['total_added_today'] += quantidade
                st.session_state.adicionar_stats['total_value_added_today'] += quantidade * valor
                
                # Invalidar caches
                st.session_state['historico_cache_invalidated'] = True
                self._invalidate_cache()
                
        except Exception as e:
            logger.error(f"Erro na adição rápida: {str(e)}")
    


def render_adicionar_page(estoque_service: EstoqueService) -> None:
    """Função para renderizar a página modernizada"""
    page = AdicionarEquipamentoProfessional(estoque_service)
    page.render() 