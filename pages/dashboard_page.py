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
            
            # Obter dados
            df_estoque = self.estoque_service.obter_equipamentos()
            stats = self.estoque_service.obter_estatisticas()
            
            # Cards de métricas
            create_info_cards(stats)
            
            st.markdown("---")
            
            if df_estoque.empty:
                st.warning("Nenhum equipamento cadastrado no estoque.")
                return
            
            # Layout dos gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                self._render_pie_chart(df_estoque)
                self._render_bar_chart_marca(df_estoque)
            
            with col2:
                self._render_line_chart(df_estoque)
                self._render_treemap_value(df_estoque)
            
            st.markdown("---")
            
            # Tabela de estoque atual
            self._render_stock_table(df_estoque)
            
            # Equipamentos em baixo estoque
            self._render_low_stock_alert(df_estoque)
            
        except Exception as e:
            logger.error(f"Erro ao renderizar dashboard: {str(e)}")
            st.error(f"Erro ao carregar dashboard: {str(e)}")
    
    def _render_pie_chart(self, df: pd.DataFrame) -> None:
        """Renderiza gráfico de pizza por categoria"""
        try:
            df_categoria = df.groupby('categoria')['quantidade'].sum().reset_index()
            fig = create_pie_chart(
                df_categoria, 
                'quantidade', 
                'categoria', 
                '📊 Distribuição por Categoria'
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            logger.error(f"Erro ao criar gráfico de pizza: {str(e)}")
            st.error("Erro ao carregar gráfico de categorias")
    
    def _render_bar_chart_marca(self, df: pd.DataFrame) -> None:
        """Renderiza gráfico de barras por marca"""
        try:
            df_marca = df.groupby('marca')['quantidade'].sum().reset_index()
            df_marca = df_marca.sort_values('quantidade', ascending=False)
            
            fig = create_bar_chart(
                df_marca, 
                'marca', 
                'quantidade', 
                '📈 Quantidade por Marca'
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
        """Renderiza treemap de valor por categoria"""
        try:
            df_valor = df.groupby('categoria').apply(
                lambda x: (x['quantidade'] * x['valor_unitario']).sum(),
                include_groups=False
            ).reset_index()
            df_valor.columns = ['categoria', 'valor_total']
            
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
    
    def _render_stock_table(self, df: pd.DataFrame) -> None:
        """Renderiza tabela de estoque atual"""
        try:
            # Preparar dados para exibição
            df_display = df.copy()
            df_display['valor_total'] = df_display['quantidade'] * df_display['valor_unitario']
            
            # Ordenar por quantidade (menor primeiro para destacar baixo estoque)
            df_display = df_display.sort_values('quantidade', ascending=True)
            
            # Formatar para exibição
            df_display = format_dataframe_for_display(df_display)
            
            # Selecionar colunas para exibição
            colunas_exibicao = ['codigo_produto', 'equipamento', 'categoria', 'marca', 'modelo', 
                              'quantidade', 'valor_unitario', 'valor_total', 'status']
            
            # Filtrar colunas existentes
            colunas_existentes = [col for col in colunas_exibicao if col in df_display.columns]
            
            create_data_table(df_display[colunas_existentes], "📋 Estoque Atual")
            
        except Exception as e:
            logger.error(f"Erro ao renderizar tabela: {str(e)}")
            st.error("Erro ao carregar tabela de estoque")
    
    def _render_low_stock_alert(self, df: pd.DataFrame, limite: int = 5) -> None:
        """Renderiza alerta de baixo estoque"""
        try:
            baixo_estoque = df[df['quantidade'] <= limite]
            
            if not baixo_estoque.empty:
                st.markdown("### ⚠️ Alertas de Baixo Estoque")
                
                for _, item in baixo_estoque.iterrows():
                    st.warning(
                        f"**{item['equipamento']}** - "
                        f"Código: {item.get('codigo_produto', 'N/A')} - "
                        f"Quantidade: {item['quantidade']} unidades"
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