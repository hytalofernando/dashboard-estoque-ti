"""
Página principal do dashboard modernizada
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from services.estoque_service import EstoqueService
from utils.plotly_utils import create_pie_chart, create_bar_chart, create_line_chart, create_treemap
from utils.ui_utils import (
    create_info_cards,
    create_data_table,
    format_dataframe_for_display,
    show_toast
)
from loguru import logger

class DashboardPage:
    """Página principal do dashboard"""
    
    def __init__(self, estoque_service: EstoqueService):
        self.estoque_service = estoque_service
    
    def render(self) -> None:
        """Renderiza a página do dashboard"""
        try:
            # Recarregar dados
            self.estoque_service.recarregar_dados()
            
            # Obter dados originais para gráfico temporal e agrupados para o resto
            df_estoque_original = self.estoque_service.obter_equipamentos()
            df_estoque_agrupado = self.estoque_service.obter_equipamentos_agrupados()
            stats = self.estoque_service.obter_estatisticas()
            
            # Cards de métricas originais
            create_info_cards(stats)
            
            st.markdown("---")
            
            # NOVO: Métricas aprimoradas com separação Novo/Usado
            self._render_metricas_aprimoradas(stats)
            
            # NOVO: Indicadores de performance
            self._render_indicadores_performance(stats)
            
            if df_estoque_original.empty:
                st.warning("Nenhum equipamento cadastrado no estoque.")
                return
            
            # Layout dos gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                self._render_pie_chart_agrupado(df_estoque_agrupado)
                self._render_bar_chart_marca_agrupado(df_estoque_agrupado)
                # NOVO: Gráfico de valor por categoria e condição
                self._render_grafico_valor_condicao(df_estoque_original)
            
            with col2:
                self._render_line_chart(df_estoque_original)  # Mantém dados originais para temporal
                self._render_treemap_value_agrupado(df_estoque_agrupado)
            
            st.markdown("---")
            
            # NOVO: Filtros rápidos antes da tabela
            df_filtrado = self._render_filtros_rapidos_tabela(df_estoque_agrupado)
            
            # Tabela de estoque atual (com dados filtrados)
            self._render_stock_table_agrupado(df_filtrado)
            
            # Equipamentos em baixo estoque (considerando totais)
            self._render_low_stock_alert_agrupado(df_estoque_agrupado)
            
        except Exception as e:
            logger.error(f"Erro ao renderizar dashboard: {str(e)}")
            st.error(f"Erro ao carregar dashboard: {str(e)}")
    
    # ===== MÉTODOS OTIMIZADOS PARA DADOS AGRUPADOS =====
    
    def _render_pie_chart_agrupado(self, df_agrupado: pd.DataFrame) -> None:
        """Renderiza gráfico de pizza por categoria (dados já agrupados)"""
        try:
            if df_agrupado.empty:
                st.info("Sem dados para exibir gráfico de categorias")
                return
                
            # Dados já estão agrupados, apenas agrupar por categoria
            df_categoria = df_agrupado.groupby('categoria')['quantidade'].sum().reset_index()
            
            fig = create_pie_chart(
                df_categoria, 
                'quantidade', 
                'categoria', 
                '📊 Distribuição por Categoria (Total)'
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de pizza: {str(e)}")
            st.error("Erro ao carregar gráfico de categorias")
    
    def _render_bar_chart_marca_agrupado(self, df_agrupado: pd.DataFrame) -> None:
        """Renderiza gráfico de barras por marca (dados já agrupados)"""
        try:
            if df_agrupado.empty:
                st.info("Sem dados para exibir gráfico de marcas")
                return
                
            # Dados já estão agrupados, apenas agrupar por marca
            df_marca = df_agrupado.groupby('marca')['quantidade'].sum().reset_index()
            df_marca = df_marca.sort_values('quantidade', ascending=False)
            
            fig = create_bar_chart(
                df_marca, 
                'marca', 
                'quantidade', 
                '📈 Quantidade Total por Marca'
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de barras: {str(e)}")
            st.error("Erro ao carregar gráfico de marcas")
    
    def _render_treemap_value_agrupado(self, df_agrupado: pd.DataFrame) -> None:
        """Renderiza treemap de valor por categoria (dados já agrupados)"""
        try:
            if df_agrupado.empty:
                st.info("Sem dados para exibir treemap de valores")
                return
                
            # Usar valor_total já calculado e agrupar por categoria
            df_valor = df_agrupado.groupby('categoria')['valor_total'].sum().reset_index()
            
            fig = create_treemap(
                df_valor,
                'categoria',
                'valor_total',
                '💰 Valor Total por Categoria'
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.error(f"Erro ao criar treemap: {str(e)}")
            st.error("Erro ao carregar gráfico de valores")
    
    def _render_stock_table_agrupado(self, df_agrupado: pd.DataFrame) -> None:
        """Renderiza tabela de estoque atual (dados já agrupados)"""
        try:
            if df_agrupado.empty:
                st.warning("Nenhum equipamento cadastrado no estoque.")
                return
            
            # Dados já estão agrupados, apenas ordenar e formatar
            df_display = df_agrupado.copy()
            df_display = df_display.sort_values('quantidade', ascending=True)
            
            # Formatar para exibição
            df_display = format_dataframe_for_display(df_display)
            
            # Selecionar colunas para exibição
            colunas_exibicao = ['codigo_produto', 'equipamento', 'categoria', 'marca', 'modelo', 
                              'quantidade', 'valor_unitario', 'valor_total', 'status']
            
            # Filtrar colunas existentes
            colunas_existentes = [col for col in colunas_exibicao if col in df_display.columns]
            
            create_data_table(df_display[colunas_existentes], "📋 Estoque Atual (Total por Equipamento)")
            
        except Exception as e:
            logger.error(f"Erro ao renderizar tabela: {str(e)}")
            st.error("Erro ao carregar tabela de estoque")
    
    def _render_low_stock_alert_agrupado(self, df_agrupado: pd.DataFrame, limite: int = 5) -> None:
        """Renderiza alerta de baixo estoque (dados já agrupados)"""
        try:
            if df_agrupado.empty:
                return
                
            baixo_estoque = df_agrupado[df_agrupado['quantidade'] <= limite]
            
            if not baixo_estoque.empty:
                st.markdown("### ⚠️ Alertas de Baixo Estoque")
                
                for _, item in baixo_estoque.iterrows():
                    st.warning(
                        f"**{item['equipamento']}** - "
                        f"Código: {item.get('codigo_produto', 'N/A')} - "
                        f"Quantidade Total: {item['quantidade']} unidades"
                    )
                
                # Toast para alertas críticos
                if len(baixo_estoque) > 0:
                    show_toast(f"⚠️ {len(baixo_estoque)} equipamento(s) com baixo estoque!")
            
        except Exception as e:
            logger.error(f"Erro ao verificar baixo estoque: {str(e)}")
    
    def _render_line_chart(self, df: pd.DataFrame) -> None:
        """Renderiza gráfico de linha temporal"""
        try:
            df_temp = df.copy()
            
            # Verificar qual coluna de data existe
            coluna_data = None
            if 'data_cadastro' in df_temp.columns:
                coluna_data = 'data_cadastro'
            elif 'Data Cadastro' in df_temp.columns:
                coluna_data = 'Data Cadastro'
            elif 'data_atualizacao' in df_temp.columns:
                coluna_data = 'data_atualizacao'
            elif 'Data Atualização' in df_temp.columns:
                coluna_data = 'Data Atualização'
            
            if not coluna_data:
                st.info("📅 Gráfico temporal não disponível (coluna de data não encontrada)")
                return
            
            # Converter para datetime
            df_temp[coluna_data] = pd.to_datetime(df_temp[coluna_data])
            
            # Agrupar por mês
            df_temp['mes_ano'] = df_temp[coluna_data].dt.to_period('M')
            cadastros_por_mes = df_temp.groupby('mes_ano').size()
            
            if not cadastros_por_mes.empty and len(cadastros_por_mes) > 1:
                fig = create_line_chart(
                    cadastros_por_mes.index.astype(str).tolist(),
                    cadastros_por_mes.values.tolist(),
                    '📅 Equipamentos Cadastrados por Mês',
                    'Mês',
                    'Quantidade'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("📅 Dados insuficientes para gráfico temporal (necessário dados de múltiplos meses)")
        except Exception as e:
            logger.error(f"Erro ao criar gráfico temporal: {str(e)}")
            st.info("📅 Gráfico temporal temporariamente indisponível")
    
    # ===== NOVOS MÉTODOS - MELHORIAS FASE 1 =====
    
    def _render_metricas_aprimoradas(self, stats: Dict[str, Any]) -> None:
        """Renderiza métricas detalhadas com separação Novo/Usado"""
        st.markdown("### 📊 Análise Detalhada por Condição")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Equipamentos Novos com valor
            total_novos = stats.get('total_novos', 0)
            valor_novos = stats.get('valor_novos', 0)
            
            st.metric(
                "🆕 Equipamentos Novos",
                f"{total_novos:,} unidades",
                delta=f"R$ {valor_novos:,.2f}",
                delta_color="normal",
                help="Total de equipamentos em condição nova e seu valor de mercado"
            )
        
        with col2:
            # Equipamentos Usados com valor
            total_usados = stats.get('total_usados', 0)
            valor_usados = stats.get('valor_usados', 0)
            
            st.metric(
                "🔄 Equipamentos Usados", 
                f"{total_usados:,} unidades",
                delta=f"R$ {valor_usados:,.2f}",
                delta_color="normal",
                help="Total de equipamentos usados/recondicionados e seu valor"
            )
        
        with col3:
            # Proporção de Novos
            percentual_novos = stats.get('percentual_novos', 0)
            
            # Determinar status baseado no percentual
            if percentual_novos > 70:
                status_icon = "🟢"
                status_text = "Excelente"
            elif percentual_novos > 50:
                status_icon = "🟡"
                status_text = "Bom"
            else:
                status_icon = "🟠"
                status_text = "Atenção"
            
            st.metric(
                "📈 Proporção de Novos",
                f"{percentual_novos:.1f}%",
                delta=f"{status_icon} {status_text}",
                help="Percentual de equipamentos novos. Ideal: >70%"
            )
        
        with col4:
            # Valor Médio por Equipamento
            total_equipamentos = stats.get('total_equipamentos', 1)
            valor_total = stats.get('valor_total', 0)
            valor_medio = valor_total / total_equipamentos if total_equipamentos > 0 else 0
            
            st.metric(
                "💰 Valor Médio/Un.",
                f"R$ {valor_medio:,.2f}",
                help="Valor médio por unidade de equipamento"
            )
        
        st.markdown("---")
    
    def _render_indicadores_performance(self, stats: Dict[str, Any]) -> None:
        """Renderiza indicadores de performance do estoque"""
        st.markdown("### ⚡ Indicadores de Performance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Taxa de rotatividade
            rotatividade = stats.get('rotatividade_30d', 0)
            
            # Classificação
            if rotatividade > 50:
                status = "🔴 Alta"
                cor = "inverse"
            elif rotatividade > 25:
                status = "🟡 Média"
                cor = "normal"
            else:
                status = "🟢 Baixa"
                cor = "normal"
            
            st.metric(
                "🔄 Rotatividade (30d)",
                f"{rotatividade:.1f}%",
                delta=status,
                delta_color=cor,
                help="Taxa de rotatividade do estoque nos últimos 30 dias"
            )
        
        with col2:
            # Cobertura de estoque (em dias) - estimativa
            rotatividade_diaria = stats.get('rotatividade_30d', 0) / 30 if stats.get('rotatividade_30d', 0) > 0 else 0.1
            cobertura_dias = int(100 / rotatividade_diaria) if rotatividade_diaria > 0 else 90
            
            if cobertura_dias < 30:
                status_cob = "⚠️ Crítico"
            elif cobertura_dias < 60:
                status_cob = "🟡 Atenção"
            else:
                status_cob = "✅ Saudável"
            
            st.metric(
                "📅 Cobertura Estimada",
                f"~{cobertura_dias} dias",
                delta=status_cob,
                help="Estimativa de dias de cobertura de estoque"
            )
        
        with col3:
            # Índice de diversidade
            categorias_ativas = stats.get('categorias_unicas', 0)
            total_categorias = 7  # Total de categorias disponíveis
            
            indice_diversidade = (categorias_ativas / total_categorias) * 100
            
            st.metric(
                "🎯 Diversidade",
                f"{indice_diversidade:.0f}%",
                delta=f"{categorias_ativas}/{total_categorias} categorias",
                help="Percentual de categorias com estoque ativo"
            )
        
        with col4:
            # Rotatividade semanal
            rotatividade_7d = stats.get('rotatividade_7d', 0)
            
            st.metric(
                "📊 Rotatividade (7d)",
                f"{rotatividade_7d:.1f}%",
                help="Taxa de rotatividade nos últimos 7 dias"
            )
        
        st.markdown("---")
    
    def _render_grafico_valor_condicao(self, df: pd.DataFrame) -> None:
        """Renderiza gráfico de valor por categoria e condição"""
        import plotly.express as px
        
        try:
            if df.empty:
                st.info("📊 Dados insuficientes para análise por condição")
                return
            
            # Verificar se coluna condicao existe
            if 'condicao' not in df.columns:
                logger.warning("Coluna 'condicao' não encontrada. Pulando gráfico.")
                return
            
            # Preparar dados
            df_analise = df.copy()
            
            # Normalizar condição
            df_analise['condicao_normalizada'] = df_analise['condicao'].apply(
                lambda x: self.estoque_service._normalizar_condicao(x)
            )
            
            # Agrupar por categoria e condição
            df_valor = df_analise.groupby(['categoria', 'condicao_normalizada']).agg({
                'quantidade': 'sum',
                'valor_unitario': 'mean'
            }).reset_index()
            
            # Calcular valor total
            df_valor['valor_total'] = df_valor['quantidade'] * df_valor['valor_unitario']
            df_valor['condicao'] = df_valor['condicao_normalizada']
            
            # Criar gráfico de barras agrupadas
            fig = px.bar(
                df_valor,
                x='categoria',
                y='valor_total',
                color='condicao',
                title='💰 Valor Total por Categoria e Condição',
                barmode='group',
                color_discrete_map={
                    'Novo': '#00C851',
                    'Usado': '#FFB300'
                },
                labels={
                    'categoria': 'Categoria',
                    'valor_total': 'Valor Total (R$)',
                    'condicao': 'Condição'
                }
            )
            
            # Aplicar tema
            from utils.plotly_utils import get_plotly_theme
            fig.update_layout(**get_plotly_theme()['layout'])
            
            # Melhorias visuais
            fig.update_traces(
                marker=dict(
                    cornerradius=8,
                    line=dict(width=2, color='rgba(0,0,0,0.3)')
                ),
                hovertemplate='<b>%{x}</b><br>Condição: %{fullData.name}<br>Valor: R$ %{y:,.2f}<extra></extra>'
            )
            
            # Ajustar layout
            fig.update_layout(
                xaxis_tickangle=-45,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                bargap=0.2,
                bargroupgap=0.1
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de valor por condição: {str(e)}")
            st.error("❌ Erro ao carregar gráfico")
    
    def _render_filtros_rapidos_tabela(self, df: pd.DataFrame) -> pd.DataFrame:
        """Renderiza filtros rápidos para tabela"""
        st.markdown("### 🔍 Filtros Rápidos da Tabela")
        
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        
        df_filtrado = df.copy()
        
        with col_f1:
            # Filtro por categoria
            categorias = ["📂 Todas"] + sorted(df['categoria'].unique().tolist())
            cat_sel = st.selectbox(
                "Categoria", 
                categorias, 
                key="quick_filter_categoria",
                help="Filtrar por categoria específica"
            )
            if cat_sel != "📂 Todas":
                df_filtrado = df_filtrado[df_filtrado['categoria'] == cat_sel]
        
        with col_f2:
            # Filtro por condição
            if 'condicao' in df.columns:
                condicoes = ["🔄 Todas", "🆕 Novo", "🔄 Usado"]
                cond_sel = st.selectbox(
                    "Condição", 
                    condicoes, 
                    key="quick_filter_condicao",
                    help="Filtrar por condição do equipamento"
                )
                if "Novo" in cond_sel:
                    # Normalizar condição antes de comparar
                    mask_novo = df_filtrado['condicao'].apply(
                        lambda x: self.estoque_service._normalizar_condicao(x) == 'Novo'
                    )
                    df_filtrado = df_filtrado[mask_novo]
                elif "Usado" in cond_sel:
                    # Normalizar condição antes de comparar
                    mask_usado = df_filtrado['condicao'].apply(
                        lambda x: self.estoque_service._normalizar_condicao(x) == 'Usado'
                    )
                    df_filtrado = df_filtrado[mask_usado]
        
        with col_f3:
            # Ordenação
            ordenacao = [
                "📊 Quantidade ↓", 
                "📊 Quantidade ↑", 
                "💰 Valor Total ↓", 
                "💰 Valor Total ↑",
                "🏷️ Código A-Z"
            ]
            ord_sel = st.selectbox(
                "Ordenar por", 
                ordenacao, 
                key="quick_sort",
                help="Ordenar resultados"
            )
            
            if "Quantidade ↓" in ord_sel:
                df_filtrado = df_filtrado.sort_values('quantidade', ascending=False)
            elif "Quantidade ↑" in ord_sel:
                df_filtrado = df_filtrado.sort_values('quantidade', ascending=True)
            elif "Valor Total ↓" in ord_sel:
                if 'valor_total' in df_filtrado.columns:
                    df_filtrado = df_filtrado.sort_values('valor_total', ascending=False)
            elif "Valor Total ↑" in ord_sel:
                if 'valor_total' in df_filtrado.columns:
                    df_filtrado = df_filtrado.sort_values('valor_total', ascending=True)
            elif "Código" in ord_sel:
                # Garantir que codigo_produto é string antes de ordenar
                df_filtrado = df_filtrado.copy()
                df_filtrado['codigo_produto'] = df_filtrado['codigo_produto'].astype(str)
                df_filtrado = df_filtrado.sort_values('codigo_produto', ascending=True)
        
        with col_f4:
            # Busca textual
            busca = st.text_input(
                "🔎 Buscar", 
                placeholder="Código ou nome...", 
                key="quick_search_text",
                help="Buscar por código ou nome"
            )
            if busca:
                busca_lower = busca.lower()
                # Converter para string antes de usar operações .str
                mask = (
                    df_filtrado['equipamento'].astype(str).str.lower().str.contains(busca_lower, na=False) |
                    df_filtrado['codigo_produto'].astype(str).str.lower().str.contains(busca_lower, na=False) |
                    df_filtrado['marca'].astype(str).str.lower().str.contains(busca_lower, na=False)
                )
                df_filtrado = df_filtrado[mask]
        
        # Contador
        total_original = len(df)
        total_filtrado = len(df_filtrado)
        
        if total_filtrado < total_original:
            st.caption(f"📋 Exibindo **{total_filtrado}** de {total_original} equipamentos (filtrado)")
        else:
            st.caption(f"📋 Exibindo **{total_filtrado}** equipamentos")
        
        st.markdown("---")
        
        return df_filtrado

def render_dashboard_page(estoque_service: EstoqueService) -> None:
    """Função para renderizar a página do dashboard"""
    dashboard = DashboardPage(estoque_service)
    dashboard.render() 