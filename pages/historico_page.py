"""
Página modernizada para histórico de movimentações com cache inteligente
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from loguru import logger

from services.estoque_service import EstoqueService
from utils.plotly_utils import create_bar_chart, create_line_chart
from utils.ui_utils import (
    create_form_section, create_data_table, format_dataframe_for_display,
    create_filter_sidebar, create_info_cards, show_success_message, show_toast
)

class HistoricoMovimentacoesPageProfessional:
    """Página profissional e responsiva para histórico de movimentações"""
    
    def __init__(self, estoque_service: EstoqueService):
        self.estoque_service = estoque_service
        # Invalidar cache se necessário
        if st.session_state.get('historico_cache_invalidated', True):
            self._invalidate_cache()
    
    def render(self) -> None:
        """Renderiza a página do histórico com cache inteligente"""
        create_form_section(
            "📋 Histórico de Movimentações em Tempo Real",
            "Visualize e analise todas as movimentações do estoque com dados sempre atualizados"
        )
        
        # Cache inteligente de movimentações
        df_movimentacoes = self._get_movimentacoes_cache()
        
        if df_movimentacoes.empty:
            self._render_empty_state()
            return
        
        # Renderizar controles superiores
        self._render_controles_superiores()
        
        # Renderizar filtros dinâmicos
        filtros = self._render_filtros_dinamicos(df_movimentacoes)
        
        # Aplicar filtros
        df_filtrado = self._aplicar_filtros_avancados(df_movimentacoes, filtros)
        
        # Tabs organizadas
        self._render_tabs_organizadas(df_filtrado, df_movimentacoes)
    
    @st.cache_data(ttl=15, show_spinner=False)  # Cache reduzido para 15 segundos para mais responsividade
    def _get_movimentacoes_cache(_self) -> pd.DataFrame:
        """Cache inteligente de movimentações com validação aprimorada"""
        try:
            # Recarregar dados do Excel sempre
            _self.estoque_service.recarregar_dados()
            df_movimentacoes = _self.estoque_service.movimentacao_service.obter_movimentacoes()
            
            if not df_movimentacoes.empty:
                # Validação e correção de dados mais robusta
                colunas_necessarias = ['codigo_produto', 'observacoes', 'tipo_movimentacao', 'quantidade']
                for coluna in colunas_necessarias:
                    if coluna not in df_movimentacoes.columns:
                        if coluna == 'codigo_produto':
                            df_movimentacoes[coluna] = 'N/A'
                        elif coluna == 'observacoes':
                            df_movimentacoes[coluna] = ''
                        else:
                            logger.warning(f"Coluna obrigatória '{coluna}' não encontrada")
                
                # Preencher valores NaN/None de forma mais cuidadosa
                df_movimentacoes['codigo_produto'] = df_movimentacoes['codigo_produto'].fillna('N/A')
                df_movimentacoes['observacoes'] = df_movimentacoes['observacoes'].fillna('')
                
                # Validar e corrigir tipos de movimentação
                df_movimentacoes['tipo_movimentacao'] = df_movimentacoes['tipo_movimentacao'].fillna('Entrada')
                
                # Converter datas com tratamento de erro
                try:
                    df_movimentacoes['data_movimentacao'] = pd.to_datetime(df_movimentacoes['data_movimentacao'])
                except Exception as e:
                    logger.error(f"Erro ao converter datas: {str(e)}")
                    # Usar data atual como fallback
                    df_movimentacoes['data_movimentacao'] = pd.to_datetime('today')
                
                # Ordenar por data (mais recente primeiro)
                df_movimentacoes = df_movimentacoes.sort_values('data_movimentacao', ascending=False)
                
                logger.info(f"📊 Cache de histórico atualizado: {len(df_movimentacoes)} movimentações validadas")
            else:
                logger.info("📊 Nenhuma movimentação encontrada")
            
            # Marcar cache como válido
            st.session_state['historico_cache_invalidated'] = False
            
            return df_movimentacoes
            
        except Exception as e:
            logger.error(f"Erro crítico ao carregar cache de movimentações: {str(e)}")
            return pd.DataFrame()
    
    def _invalidate_cache(self) -> None:
        """Invalida cache inteligentemente"""
        if hasattr(st, 'cache_data'):
            try:
                # Limpar cache específico desta função
                self._get_movimentacoes_cache.clear()
                logger.info("🔄 Cache de histórico invalidado")
            except:
                # Fallback: limpar todo o cache
                st.cache_data.clear()
    
    def _render_empty_state(self) -> None:
        """Renderiza estado vazio"""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("📭 **Nenhuma movimentação registrada ainda**")
            st.markdown("**Primeiras movimentações aparecerão aqui após:**")
            st.markdown("• ➕ Adicionar equipamentos")
            st.markdown("• ➖ Remover equipamentos")
            st.markdown("• 📦 Operações de estoque")
    
    def _render_controles_superiores(self) -> None:
        """Renderiza controles superiores"""
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.markdown("### 🔄 **Dados sempre atualizados automaticamente**")
        
        with col2:
            if st.button("🔄 Recarregar Agora", use_container_width=True):
                self._force_reload()
        
        with col3:
            if st.button("📥 Exportar CSV", use_container_width=True):
                self._export_data()
        
        with col4:
            if st.button("🧹 Limpar Filtros", use_container_width=True):
                self._clear_filters()
        
        # Informações de debug (somente se houver dados)
        df_debug = self._get_movimentacoes_cache()
        if not df_debug.empty:
            st.caption(f"🔍 **Debug:** {len(df_debug)} movimentações carregadas | Última atualização: {datetime.now().strftime('%H:%M:%S')}")
            
            # Mostrar tipos únicos encontrados para debug
            tipos_unicos = df_debug['tipo_movimentacao'].unique().tolist()
            st.caption(f"📊 **Tipos encontrados:** {', '.join(tipos_unicos)}")
    
    def _force_reload(self) -> None:
        """Força recarregamento dos dados"""
        st.session_state['historico_cache_invalidated'] = True
        self._invalidate_cache()
        show_toast("🔄 Dados recarregados!", "✅")
        st.rerun()
    
    def _export_data(self) -> None:
        """Exporta dados"""
        try:
            df = self._get_movimentacoes_cache()
            if not df.empty:
                csv = df.to_csv(index=False)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"historico_movimentacoes_{timestamp}.csv"
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )
                show_success_message("✅ Arquivo CSV preparado para download!")
        except Exception as e:
            st.error(f"❌ Erro ao exportar: {str(e)}")
    
    def _clear_filters(self) -> None:
        """Limpa todos os filtros"""
        filter_keys = [
            'hist_tipo_filter', 'hist_periodo_filter', 'hist_data_inicio', 
            'hist_data_fim', 'hist_busca_equipamento', 'hist_busca_codigo'
        ]
        for key in filter_keys:
            if key in st.session_state:
                del st.session_state[key]
        show_toast("🧹 Filtros limpos!", "✅")
        st.rerun()
    
    def _render_filtros_dinamicos(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Renderiza filtros dinâmicos na sidebar"""
        st.sidebar.markdown("## 🔍 **Filtros Inteligentes**")
        
        filtros = {}
        
        # Filtro por tipo com contadores
        tipos_count = df['tipo_movimentacao'].value_counts()
        tipos_options = ["🔄 Todos"] + [f"{tipo} ({count})" for tipo, count in tipos_count.items()]
        
        tipo_selecionado = st.sidebar.selectbox(
            "📊 Tipo de Movimentação", 
            tipos_options,
            key="hist_tipo_filter"
        )
        
        if tipo_selecionado != "🔄 Todos":
            filtros['tipo'] = tipo_selecionado.split(' (')[0]
        
        # Filtros de período otimizados
        st.sidebar.markdown("### 📅 **Período**")
        
        periodo_opcoes = {
            "📅 Hoje": 0,
            "📅 Últimos 3 dias": 3,
            "📅 Última semana": 7,
            "📅 Últimos 30 dias": 30,
            "📅 Últimos 90 dias": 90,
            "📅 Último ano": 365,
            "🎯 Personalizado": -1
        }
        
        periodo_selecionado = st.sidebar.selectbox(
            "🕐 Período",
            list(periodo_opcoes.keys()),
            index=3,  # Default: últimos 30 dias
            key="hist_periodo_filter"
        )
        
        if periodo_selecionado == "🎯 Personalizado":
            col1, col2 = st.sidebar.columns(2)
            with col1:
                filtros['data_inicio'] = st.date_input(
                    "De:",
                    value=datetime.now() - timedelta(days=30),
                    key="hist_data_inicio"
                )
            with col2:
                filtros['data_fim'] = st.date_input(
                    "Até:",
                    value=datetime.now(),
                    key="hist_data_fim"
                )
        else:
            dias = periodo_opcoes[periodo_selecionado]
            if dias >= 0:
                filtros['data_inicio'] = datetime.now() - timedelta(days=dias)
                filtros['data_fim'] = datetime.now()
        
        # Busca inteligente
        st.sidebar.markdown("### 🔍 **Busca Inteligente**")
        
        filtros['busca_equipamento'] = st.sidebar.text_input(
            "🔍 Nome do Equipamento",
            placeholder="Ex: Notebook, Monitor...",
            key="hist_busca_equipamento"
        )
        
        filtros['busca_codigo'] = st.sidebar.text_input(
            "🏷️ Código do Produto",
            placeholder="Ex: NB-DELL-001...",
            key="hist_busca_codigo"
        )
        
        # Estatísticas na sidebar - melhoradas e mais precisas
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 **Estatísticas Rápidas**")
        
        # Normalizar todos os tipos antes de contar
        df_stats = df.copy()
        df_stats['tipo_normalizado'] = df_stats['tipo_movimentacao'].apply(
            lambda x: self._normalizar_tipo_movimentacao(x)
        )
        
        total = len(df_stats)
        entradas = len(df_stats[df_stats['tipo_normalizado'] == 'Entrada'])
        saidas = len(df_stats[df_stats['tipo_normalizado'] == 'Saída'])
        
        # Calcular quantidades também
        qtd_entradas = df_stats[df_stats['tipo_normalizado'] == 'Entrada']['quantidade'].sum() if entradas > 0 else 0
        qtd_saidas = df_stats[df_stats['tipo_normalizado'] == 'Saída']['quantidade'].sum() if saidas > 0 else 0
        
        st.sidebar.metric("📊 Total", f"{total:,}")
        st.sidebar.metric("📈 Entradas", f"{entradas:,}", delta=f"+{qtd_entradas:,} itens")
        st.sidebar.metric("📉 Saídas", f"{saidas:,}", delta=f"-{qtd_saidas:,} itens")
        
        return filtros
    
    def _aplicar_filtros_avancados(self, df: pd.DataFrame, filtros: Dict[str, Any]) -> pd.DataFrame:
        """Aplica filtros avançados com performance otimizada"""
        df_filtrado = df.copy()
        
        try:
            # 🔧 NORMALIZAR TIPOS DE MOVIMENTAÇÃO para manter semântica visual
            if 'tipo_movimentacao' in df_filtrado.columns:
                df_filtrado['tipo_movimentacao'] = df_filtrado['tipo_movimentacao'].apply(
                    lambda x: self._normalizar_tipo_movimentacao(x)
                )
            
            # Filtro por tipo
            if filtros.get('tipo'):
                tipo_normalizado = self._normalizar_tipo_movimentacao(filtros['tipo'])
                mask_tipo = df_filtrado['tipo_movimentacao'] == tipo_normalizado
                df_filtrado = df_filtrado[mask_tipo]
            
            # Filtro por período
            if filtros.get('data_inicio'):
                data_inicio = pd.to_datetime(filtros['data_inicio'])
                df_filtrado = df_filtrado[df_filtrado['data_movimentacao'] >= data_inicio]
            
            if filtros.get('data_fim'):
                data_fim = pd.to_datetime(filtros['data_fim']) + timedelta(days=1)  # Incluir o dia todo
                df_filtrado = df_filtrado[df_filtrado['data_movimentacao'] < data_fim]
            
            # Busca por equipamento
            if filtros.get('busca_equipamento'):
                busca = filtros['busca_equipamento'].lower()
                
                # Buscar nas observações (que contém info do equipamento)
                mask_obs = df_filtrado['observacoes'].str.lower().str.contains(busca, na=False)
                mask_destino = df_filtrado['destino_origem'].str.lower().str.contains(busca, na=False)
                
                df_filtrado = df_filtrado[mask_obs | mask_destino]
            
            # Busca por código
            if filtros.get('busca_codigo'):
                codigo = filtros['busca_codigo'].upper()
                mask_codigo = df_filtrado['codigo_produto'].str.upper().str.contains(codigo, na=False)
                df_filtrado = df_filtrado[mask_codigo]
            
        except Exception as e:
            logger.error(f"Erro ao aplicar filtros: {str(e)}")
            st.warning("⚠️ Erro ao aplicar filtros. Mostrando todos os dados.")
            return df
        
        return df_filtrado
    
    def _normalizar_tipo_movimentacao(self, tipo: str) -> str:
        """Normaliza tipos de movimentação com validação rigorosa"""
        if not tipo or pd.isna(tipo):
            logger.warning("Tipo de movimentação vazio encontrado - usando 'Entrada' como padrão")
            return "Entrada"
        
        tipo_str = str(tipo).strip()
        
        # Conversão mais rigorosa com logging para debug
        if tipo_str in ["Entrada", "ENTRADA"] or "Entrada" in tipo_str:
            return "Entrada"
        elif tipo_str in ["Saída", "SAÍDA", "SAIDA"] or "Saída" in tipo_str or "Saida" in tipo_str:
            return "Saída"
        else:
            # Log para tipos não reconhecidos antes do fallback
            logger.warning(f"Tipo de movimentação não reconhecido: '{tipo_str}' - usando 'Entrada' como fallback")
            return "Entrada"
    
    def _render_tabs_organizadas(self, df_filtrado: pd.DataFrame, df_completo: pd.DataFrame) -> None:
        """Renderiza tabs organizadas"""
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 **Visão Geral**", 
            "📋 **Detalhes**", 
            "📈 **Análises**", 
            "🕐 **Recentes**"
        ])
        
        with tab1:
            self._render_visao_geral(df_filtrado)
        
        with tab2:
            self._render_tabela_detalhada(df_filtrado)
        
        with tab3:
            self._render_analises_avancadas(df_filtrado)
        
        with tab4:
            self._render_movimentacoes_recentes(df_completo)
    
    def _render_visao_geral(self, df: pd.DataFrame) -> None:
        """Renderiza visão geral"""
        if df.empty:
            st.info("📊 Nenhuma movimentação encontrada com os filtros aplicados.")
            return
        
        # 🔧 NORMALIZAR TIPOS antes de calcular estatísticas
        df_normalizado = df.copy()
        df_normalizado['tipo_movimentacao'] = df_normalizado['tipo_movimentacao'].apply(
            lambda x: self._normalizar_tipo_movimentacao(x)
        )
        
        # Métricas principais com tipos normalizados
        col1, col2, col3, col4 = st.columns(4)
        
        # ✅ USAR TIPOS NORMALIZADOS para estatísticas corretas
        entradas = df_normalizado[df_normalizado['tipo_movimentacao'] == 'Entrada']
        saidas = df_normalizado[df_normalizado['tipo_movimentacao'] == 'Saída']
        
        total_movimentacoes = len(df_normalizado)
        total_entradas = len(entradas)
        total_saidas = len(saidas)
        quantidade_entrada = entradas['quantidade'].sum() if not entradas.empty else 0
        quantidade_saida = saidas['quantidade'].sum() if not saidas.empty else 0
        
        with col1:
            st.metric(
                "📊 Total Movimentações",
                f"{total_movimentacoes:,}",
                help="Número total de movimentações no período"
            )
        
        with col2:
            st.metric(
                "📈 Entradas",
                f"{total_entradas:,}",
                delta=f"+{quantidade_entrada:,} itens",
                help="Movimentações de entrada"
            )
        
        with col3:
            st.metric(
                "📉 Saídas",
                f"{total_saidas:,}",
                delta=f"-{quantidade_saida:,} itens",
                delta_color="inverse",
                help="Movimentações de saída"
            )
        
        with col4:
            saldo = quantidade_entrada - quantidade_saida
            st.metric(
                "⚖️ Saldo Líquido",
                f"{saldo:+,} itens",
                delta=f"{'Positivo' if saldo >= 0 else 'Negativo'}",
                delta_color="normal" if saldo >= 0 else "inverse"
            )
        
        # Gráficos resumo com dados normalizados
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribuição por tipo com tipos normalizados
            df_tipo = df_normalizado['tipo_movimentacao'].value_counts().reset_index()
            df_tipo.columns = ['Tipo', 'Quantidade']
            
            if not df_tipo.empty:
                fig_tipo = create_bar_chart(
                    df_tipo,
                    'Tipo',
                    'Quantidade',
                    '📊 Distribuição por Tipo'
                )
                st.plotly_chart(fig_tipo, use_container_width=True)
        
        with col2:
            # Timeline de movimentações
            try:
                df_timeline = df_normalizado.copy()
                df_timeline['data'] = df_timeline['data_movimentacao'].dt.date
                timeline_data = df_timeline.groupby('data').size()
                
                if len(timeline_data) > 1:
                    fig_timeline = create_line_chart(
                        timeline_data.index.astype(str).tolist(),
                        timeline_data.values.tolist(),
                        '📈 Timeline de Movimentações',
                        'Data',
                        'Quantidade'
                    )
                    st.plotly_chart(fig_timeline, use_container_width=True)
                else:
                    st.info("📈 Dados insuficientes para timeline")
            except Exception as e:
                logger.error(f"Erro no gráfico timeline: {str(e)}")
                st.info("📈 Erro ao carregar timeline")
    
    def _render_tabela_detalhada(self, df: pd.DataFrame) -> None:
        """Renderiza tabela detalhada com integração de equipamentos"""
        if df.empty:
            st.info("📋 Nenhuma movimentação para exibir.")
            return
        
        try:
            # Enriquecer dados com informações de equipamentos de forma mais robusta
            df_estoque = self.estoque_service.obter_equipamentos()
            
            if not df_estoque.empty and 'equipamento_id' in df.columns:
                # Verificar se colunas necessárias existem no estoque
                colunas_merge = ['id', 'equipamento', 'categoria', 'marca']
                colunas_disponveis = [col for col in colunas_merge if col in df_estoque.columns]
                
                if len(colunas_disponveis) >= 2:  # Pelo menos ID e uma outra coluna
                    # Merge inteligente com validação
                    df_enriquecido = df.merge(
                        df_estoque[colunas_disponveis],
                        left_on='equipamento_id',
                        right_on='id',
                        how='left',
                        suffixes=('', '_equip')
                    )
                    logger.info(f"Merge realizado com {len(colunas_disponveis)} colunas do estoque")
                else:
                    logger.warning("Colunas insuficientes no estoque para merge - usando dados básicos")
                    df_enriquecido = df.copy()
                    # Adicionar colunas vazias para manter compatibilidade
                    for col in ['equipamento', 'categoria', 'marca']:
                        if col not in df_enriquecido.columns:
                            df_enriquecido[col] = 'N/A'
            else:
                logger.warning("Estoque vazio ou coluna equipamento_id ausente - usando dados básicos")
                df_enriquecido = df.copy()
                # Adicionar colunas vazias para manter compatibilidade
                for col in ['equipamento', 'categoria', 'marca']:
                    if col not in df_enriquecido.columns:
                        df_enriquecido[col] = 'N/A'
            
            # Preparar para exibição
            df_display = df_enriquecido.copy()
            df_display['Data'] = df_display['data_movimentacao'].dt.strftime('%d/%m/%Y %H:%M')
            df_display['Tipo'] = df_display['tipo_movimentacao']
            df_display['Equipamento'] = df_display['equipamento'].fillna('N/A')
            df_display['Categoria'] = df_display['categoria'].fillna('N/A')
            df_display['Marca'] = df_display['marca'].fillna('N/A')
            df_display['Código'] = df_display['codigo_produto']
            df_display['Qtd'] = df_display['quantidade']
            df_display['Destino/Origem'] = df_display['destino_origem']
            df_display['Observações'] = df_display['observacoes']
            
            # Selecionar colunas finais
            colunas_finais = [
                'Data', 'Tipo', 'Equipamento', 'Categoria', 'Marca',
                'Código', 'Qtd', 'Destino/Origem', 'Observações'
            ]
            
            df_final = df_display[colunas_finais]
            
            # Exibir com configuração avançada
            st.dataframe(
                df_final,
                use_container_width=True,
                height=500,
                column_config={
                    "Data": st.column_config.DatetimeColumn(
                        "Data",
                        help="Data e hora da movimentação"
                    ),
                    "Tipo": st.column_config.TextColumn(
                        "Tipo",
                        help="Tipo de movimentação"
                    ),
                    "Qtd": st.column_config.NumberColumn(
                        "Qtd",
                        help="Quantidade movimentada"
                    )
                }
            )
            
            # Estatísticas da tabela
            st.caption(f"📋 **{len(df_final)}** movimentações exibidas | Última atualização: {datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            logger.error(f"Erro ao renderizar tabela detalhada: {str(e)}")
            st.error(f"❌ Erro ao carregar tabela: {str(e)}")
    
    def _render_analises_avancadas(self, df: pd.DataFrame) -> None:
        """Renderiza análises avançadas"""
        if df.empty:
            st.info("📈 Nenhum dado para análise.")
            return
        
        st.markdown("### 📊 **Análises Detalhadas**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Análise por período
            st.markdown("#### 📅 **Por Período**")
            df_periodo = df.copy()
            df_periodo['periodo'] = df_periodo['data_movimentacao'].dt.strftime('%Y-%m')
            periodo_stats = df_periodo.groupby(['periodo', 'tipo_movimentacao']).size().unstack(fill_value=0)
            
            if not periodo_stats.empty:
                st.bar_chart(periodo_stats)
            else:
                st.info("Dados insuficientes")
        
        with col2:
            # Top equipamentos
            st.markdown("#### 🏆 **Top Equipamentos**")
            if 'codigo_produto' in df.columns:
                top_equipamentos = df['codigo_produto'].value_counts().head(10)
                if not top_equipamentos.empty:
                    st.bar_chart(top_equipamentos)
                else:
                    st.info("Dados insuficientes")
    
    def _render_movimentacoes_recentes(self, df: pd.DataFrame) -> None:
        """Renderiza movimentações mais recentes"""
        st.markdown("### 🕐 **Últimas Movimentações**")
        
        if df.empty:
            st.info("Nenhuma movimentação recente.")
            return
        
        # Pegar as 10 mais recentes
        df_recentes = df.head(10).copy()
        
        # 🔧 NORMALIZAR TIPOS para manter semântica visual
        df_recentes['tipo_movimentacao'] = df_recentes['tipo_movimentacao'].apply(
            lambda x: self._normalizar_tipo_movimentacao(x)
        )
        
        for idx, mov in df_recentes.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([1, 4, 1])
                
                # 🎨 ÍCONE E COR BASEADOS NO TIPO NORMALIZADO (semântica original)
                tipo_normalizado = mov['tipo_movimentacao']
                if tipo_normalizado == "Entrada":
                    icone = "📈"
                    cor_delta = "normal"
                    sinal = "+"
                    cor_texto = "success"
                else:  # Saída
                    icone = "📉"  
                    cor_delta = "inverse"
                    sinal = "-"
                    cor_texto = "error"
                
                with col1:
                    st.markdown(f"### {icone}")
                
                with col2:
                    data_formatada = pd.to_datetime(mov['data_movimentacao']).strftime('%d/%m/%Y %H:%M')
                    codigo = mov.get('codigo_produto', 'N/A')
                    
                    st.markdown(f"**Código: {codigo}**")
                    st.markdown(f"**{tipo_normalizado}** - {mov['quantidade']} unidades")
                    st.markdown(f"*{data_formatada} - {mov['destino_origem']}*")
                    
                    if mov.get('observacoes'):
                        st.caption(f"📝 {mov['observacoes']}")
                
                with col3:
                    # 🎨 CORES CORRETAS baseadas no tipo (semântica original)
                    if tipo_normalizado == "Entrada":
                        st.success(f"+{mov['quantidade']}")  # Verde para entrada
                    else:
                        st.error(f"-{mov['quantidade']}")    # Vermelho para saída
                
                st.markdown("---")

def render_historico_page(estoque_service: EstoqueService) -> None:
    """Função para renderizar a página do histórico profissional"""
    page = HistoricoMovimentacoesPageProfessional(estoque_service)
    page.render() 