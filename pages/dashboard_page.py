"""
Página principal do dashboard modernizada
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any

from services.estoque_service import EstoqueService
from utils.plotly_utils import create_pie_chart, create_bar_chart, create_line_chart, create_treemap
from utils.ui_utils import (
    create_form_section, create_info_cards, create_data_table,
    format_dataframe_for_display, normalizar_status_equipamento, render_status_badge,
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
            
            # Cards de métricas
            create_info_cards(stats)
            
            st.markdown("---")
            
            if df_estoque_original.empty:
                st.warning("Nenhum equipamento cadastrado no estoque.")
                return
            
            # Layout dos gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                self._render_pie_chart_agrupado(df_estoque_agrupado)
                self._render_bar_chart_marca_agrupado(df_estoque_agrupado)
            
            with col2:
                self._render_line_chart(df_estoque_original)  # Mantém dados originais para temporal
                self._render_treemap_value_agrupado(df_estoque_agrupado)
            
            st.markdown("---")
            
            # Tabela de estoque atual (agrupada)
            self._render_stock_table_agrupado(df_estoque_agrupado)
            
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
    
    # ===== MÉTODOS LEGADOS (PARA COMPATIBILIDADE) =====
    
    def _render_pie_chart(self, df: pd.DataFrame) -> None:
        """Renderiza gráfico de pizza por categoria (agrupando por código do produto)"""
        try:
            # Agrupar por código do produto primeiro para evitar duplicação, depois por categoria
            df_agrupado = df.groupby(['codigo_produto', 'categoria'])['quantidade'].sum().reset_index()
            # Agora agrupar por categoria para o gráfico
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
    
    def _render_bar_chart_marca(self, df: pd.DataFrame) -> None:
        """Renderiza gráfico de barras por marca (agrupando por código do produto)"""
        try:
            # Agrupar por código do produto primeiro para evitar duplicação, depois por marca
            df_agrupado = df.groupby(['codigo_produto', 'marca'])['quantidade'].sum().reset_index()
            # Agora agrupar por marca para o gráfico
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
    
    def _render_line_chart(self, df: pd.DataFrame) -> None:
        """Renderiza gráfico de linha temporal"""
        try:
            df_temp = df.copy()
            df_temp['data_chegada'] = pd.to_datetime(df_temp['data_chegada'])
            
            # Agrupar por mês
            df_temp['mes_ano'] = df_temp['data_chegada'].dt.to_period('M')
            chegadas_por_mes = df_temp.groupby('mes_ano').size()
            
            if not chegadas_por_mes.empty:
                fig = create_line_chart(
                    chegadas_por_mes.index.astype(str).tolist(),
                    chegadas_por_mes.values.tolist(),
                    '📅 Equipamentos Recebidos por Mês',
                    'Mês',
                    'Quantidade'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Dados temporais insuficientes para gráfico")
        except Exception as e:
            logger.error(f"Erro ao criar gráfico temporal: {str(e)}")
            st.error("Erro ao carregar gráfico temporal")
    
    def _render_treemap_value(self, df: pd.DataFrame) -> None:
        """Renderiza treemap de valor por categoria (agrupando por código do produto)"""
        try:
            # Agrupar por código do produto primeiro para evitar duplicação
            df_agrupado = df.groupby(['codigo_produto', 'categoria']).agg({
                'quantidade': 'sum',
                'valor_unitario': 'mean'  # Usar média do valor unitário para o mesmo produto
            }).reset_index()
            
            # Calcular valor total para cada código de produto
            df_agrupado['valor_total_produto'] = df_agrupado['quantidade'] * df_agrupado['valor_unitario']
            
            # Agora agrupar por categoria
            df_valor = df_agrupado.groupby('categoria')['valor_total_produto'].sum().reset_index()
            df_valor.columns = ['categoria', 'valor_total']
            
            fig = create_treemap(
                df_valor,
                'categoria',
                'valor_total',
                '💰 Valor Total por Categoria (Agrupado)'
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.error(f"Erro ao criar treemap: {str(e)}")
            st.error("Erro ao carregar gráfico de valores")
    
    def _render_stock_table(self, df: pd.DataFrame) -> None:
        """Renderiza tabela de estoque atual (agrupada por código do produto)"""
        try:
            # Agrupar por código do produto para mostrar totais
            df_agrupado = df.groupby(['codigo_produto', 'equipamento', 'categoria', 'marca', 'modelo']).agg({
                'quantidade': 'sum',
                'valor_unitario': 'mean',  # Usar média do valor unitário
                'status': 'first',  # Pegar o primeiro status
                'fornecedor': 'first'  # Pegar o primeiro fornecedor
            }).reset_index()
            
            # Calcular valor total para cada produto agrupado
            df_agrupado['valor_total'] = df_agrupado['quantidade'] * df_agrupado['valor_unitario']
            
            # Ordenar por quantidade (menor primeiro para destacar baixo estoque)
            df_agrupado = df_agrupado.sort_values('quantidade', ascending=True)
            
            # Formatar para exibição
            df_display = format_dataframe_for_display(df_agrupado)
            
            # Selecionar colunas para exibição
            colunas_exibicao = ['codigo_produto', 'equipamento', 'categoria', 'marca', 'modelo', 
                              'quantidade', 'valor_unitario', 'valor_total', 'status']
            
            # Filtrar colunas existentes
            colunas_existentes = [col for col in colunas_exibicao if col in df_display.columns]
            
            create_data_table(df_display[colunas_existentes], "📋 Estoque Atual (Total por Equipamento)")
            
        except Exception as e:
            logger.error(f"Erro ao renderizar tabela: {str(e)}")
            st.error("Erro ao carregar tabela de estoque")
    
    def _render_low_stock_alert(self, df: pd.DataFrame, limite: int = 5) -> None:
        """Renderiza alerta de baixo estoque (considerando totais agrupados)"""
        try:
            # Agrupar por código do produto para verificar estoque total
            df_agrupado = df.groupby(['codigo_produto', 'equipamento']).agg({
                'quantidade': 'sum'
            }).reset_index()
            
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

def render_dashboard_page(estoque_service: EstoqueService) -> None:
    """Função para renderizar a página do dashboard"""
    dashboard = DashboardPage(estoque_service)
    dashboard.render() 