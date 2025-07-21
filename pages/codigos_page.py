"""
Página modernizada para gerenciar códigos de produtos
"""

import streamlit as st
import pandas as pd
from typing import Optional
from loguru import logger

from services.estoque_service import EstoqueService
from utils.plotly_utils import create_pie_chart, create_bar_chart
from utils.ui_utils import (
    create_form_section, create_data_table, format_dataframe_for_display,
    show_toast, create_info_cards
)

class CodigosPage:
    """Página para visualização e busca de códigos de produtos"""
    
    def __init__(self, estoque_service: EstoqueService):
        self.estoque_service = estoque_service
    
    def render(self) -> None:
        """Renderiza a página de códigos"""
        create_form_section(
            "🏷️ Códigos de Produtos",
            "Visualize, busque e analise todos os códigos de produtos do sistema"
        )
        
        # Obter dados
        df_estoque = self.estoque_service.obter_equipamentos()
        
        if df_estoque.empty:
            st.warning("📭 Nenhum produto cadastrado ainda.")
            return
        
        # Renderizar estatísticas
        self._render_statistics(df_estoque)
        
        # Renderizar filtros e busca
        filtros = self._render_filters(df_estoque)
        
        # Aplicar filtros
        df_filtrado = self._aplicar_filtros(df_estoque, filtros)
        
        # Gráficos de análise
        self._render_charts(df_filtrado)
        
        # Tabela de códigos
        self._render_codes_table(df_filtrado)
        
        # Análise de padrões de códigos
        self._render_code_patterns(df_estoque)
    
    def _render_statistics(self, df: pd.DataFrame) -> None:
        """Renderiza estatísticas dos códigos"""
        try:
            total_produtos = len(df)
            categorias_unicas = df['categoria'].nunique()
            marcas_unicas = df['marca'].nunique()
            valor_total = (df['quantidade'] * df['valor_unitario']).sum()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "🏷️ Total de Produtos",
                    f"{total_produtos:,}",
                    help="Número total de produtos com códigos únicos"
                )
            
            with col2:
                st.metric(
                    "📂 Categorias",
                    str(categorias_unicas),
                    help="Número de categorias diferentes"
                )
            
            with col3:
                st.metric(
                    "🏢 Marcas",
                    str(marcas_unicas),
                    help="Número de marcas diferentes"
                )
            
            with col4:
                st.metric(
                    "💰 Valor Total",
                    f"R$ {valor_total:,.2f}",
                    help="Valor total de todos os produtos"
                )
                
        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {str(e)}")
    
    def _render_filters(self, df: pd.DataFrame) -> dict:
        """Renderiza filtros na sidebar"""
        st.sidebar.markdown("## 🔍 Filtros e Busca")
        
        filtros = {}
        
        # Filtro por categoria
        categorias = ["Todas"] + sorted(df['categoria'].unique().tolist())
        filtros['categoria'] = st.sidebar.selectbox("📂 Categoria", categorias)
        
        # Filtro por marca
        marcas = ["Todas"] + sorted(df['marca'].unique().tolist())
        filtros['marca'] = st.sidebar.selectbox("🏢 Marca", marcas)
        
        # Filtro por status
        if 'status' in df.columns:
            status_list = ["Todos"] + sorted(df['status'].unique().tolist())
            filtros['status'] = st.sidebar.selectbox("📊 Status", status_list)
        
        # Busca por código ou nome
        filtros['busca'] = st.sidebar.text_input(
            "🔍 Buscar",
            placeholder="Digite código ou nome do produto",
            help="Busca em códigos de produto e nomes de equipamentos"
        )
        
        # Filtro por faixa de valor
        st.sidebar.markdown("### 💰 Faixa de Valor")
        
        if not df.empty:
            valor_min = float(df['valor_unitario'].min())
            valor_max = float(df['valor_unitario'].max())
            
            if valor_min < valor_max:
                filtros['valor_range'] = st.sidebar.slider(
                    "Valor Unitário (R$)",
                    min_value=valor_min,
                    max_value=valor_max,
                    value=(valor_min, valor_max),
                    format="R$ %.2f"
                )
        
        # Filtro por quantidade
        st.sidebar.markdown("### 📊 Faixa de Quantidade")
        
        if not df.empty:
            qtd_min = int(df['quantidade'].min())
            qtd_max = int(df['quantidade'].max())
            
            if qtd_min < qtd_max:
                filtros['quantidade_range'] = st.sidebar.slider(
                    "Quantidade em Estoque",
                    min_value=qtd_min,
                    max_value=qtd_max,
                    value=(qtd_min, qtd_max)
                )
        
        return filtros
    
    def _aplicar_filtros(self, df: pd.DataFrame, filtros: dict) -> pd.DataFrame:
        """Aplica filtros aos dados"""
        df_filtrado = df.copy()
        
        # Filtro por categoria
        if filtros.get('categoria') and filtros['categoria'] != "Todas":
            df_filtrado = df_filtrado[df_filtrado['categoria'] == filtros['categoria']]
        
        # Filtro por marca
        if filtros.get('marca') and filtros['marca'] != "Todas":
            df_filtrado = df_filtrado[df_filtrado['marca'] == filtros['marca']]
        
        # Filtro por status
        if filtros.get('status') and filtros['status'] != "Todos":
            df_filtrado = df_filtrado[df_filtrado['status'] == filtros['status']]
        
        # Busca por código ou nome
        if filtros.get('busca'):
            busca = filtros['busca'].lower()
            mask = (
                df_filtrado['codigo_produto'].str.lower().str.contains(busca, na=False) |
                df_filtrado['equipamento'].str.lower().str.contains(busca, na=False) |
                df_filtrado['marca'].str.lower().str.contains(busca, na=False) |
                df_filtrado['modelo'].str.lower().str.contains(busca, na=False)
            )
            df_filtrado = df_filtrado[mask]
        
        # Filtro por valor
        if filtros.get('valor_range'):
            valor_min, valor_max = filtros['valor_range']
            df_filtrado = df_filtrado[
                (df_filtrado['valor_unitario'] >= valor_min) &
                (df_filtrado['valor_unitario'] <= valor_max)
            ]
        
        # Filtro por quantidade
        if filtros.get('quantidade_range'):
            qtd_min, qtd_max = filtros['quantidade_range']
            df_filtrado = df_filtrado[
                (df_filtrado['quantidade'] >= qtd_min) &
                (df_filtrado['quantidade'] <= qtd_max)
            ]
        
        return df_filtrado
    
    def _render_charts(self, df: pd.DataFrame) -> None:
        """Renderiza gráficos de análise"""
        if df.empty:
            st.info("📊 Nenhum produto encontrado com os filtros aplicados.")
            return
        
        st.markdown("---")
        st.markdown("### 📊 Análises dos Códigos")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico por categoria
            df_categoria = df.groupby('categoria').size().reset_index(name='quantidade')
            fig_categoria = create_pie_chart(
                df_categoria,
                'quantidade',
                'categoria',
                '📂 Distribuição por Categoria'
            )
            st.plotly_chart(fig_categoria, use_container_width=True)
        
        with col2:
            # Gráfico por marca
            df_marca = df.groupby('marca').size().reset_index(name='quantidade')
            df_marca = df_marca.sort_values('quantidade', ascending=False).head(10)
            
            fig_marca = create_bar_chart(
                df_marca,
                'marca',
                'quantidade',
                '🏢 Top 10 Marcas por Quantidade de Produtos'
            )
            st.plotly_chart(fig_marca, use_container_width=True)
    
    def _render_codes_table(self, df: pd.DataFrame) -> None:
        """Renderiza tabela de códigos"""
        if df.empty:
            return
        
        st.markdown("---")
        
        try:
            # Preparar dados para exibição
            df_display = df.copy()
            df_display['valor_total'] = df_display['quantidade'] * df_display['valor_unitario']
            
            # Ordenar por código
            if 'codigo_produto' in df_display.columns:
                df_display = df_display.sort_values('codigo_produto')
            
            # Formatar para exibição
            df_display = format_dataframe_for_display(df_display)
            
            # Selecionar colunas para exibição
            colunas_exibicao = [
                'codigo_produto', 'equipamento', 'categoria', 'marca', 'modelo',
                'quantidade', 'valor_unitario', 'valor_total', 'fornecedor', 'status'
            ]
            
            # Filtrar colunas existentes
            colunas_existentes = [col for col in colunas_exibicao if col in df_display.columns]
            
            # Renomear colunas para exibição
            rename_columns = {
                'codigo_produto': 'Código',
                'equipamento': 'Equipamento',
                'categoria': 'Categoria',
                'marca': 'Marca',
                'modelo': 'Modelo',
                'quantidade': 'Qtd',
                'valor_unitario': 'Valor Unit.',
                'valor_total': 'Valor Total',
                'fornecedor': 'Fornecedor',
                'status': 'Status'
            }
            
            df_final = df_display[colunas_existentes].rename(columns=rename_columns)
            
            create_data_table(df_final, f"🏷️ Códigos de Produtos ({len(df_final)} produtos)")
            
            # Botão para download (se disponível)
            if hasattr(st, 'download_button'):
                try:
                    csv = df_final.to_csv(index=False)
                    st.download_button(
                        label="📥 Baixar Tabela (CSV)",
                        data=csv,
                        file_name=f"codigos_produtos_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                except Exception as e:
                    logger.error(f"Erro ao gerar download: {str(e)}")
            
        except Exception as e:
            logger.error(f"Erro ao renderizar tabela de códigos: {str(e)}")
            st.error("Erro ao carregar tabela de códigos")
    
    def _render_code_patterns(self, df: pd.DataFrame) -> None:
        """Renderiza análise de padrões de códigos"""
        try:
            st.markdown("---")
            st.markdown("### 🔍 Análise de Padrões de Códigos")
            
            if 'codigo_produto' not in df.columns:
                st.info("Códigos de produto não disponíveis para análise")
                return
            
            # Análise de prefixos
            prefixos = df['codigo_produto'].str.split('-').str[0].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏷️ Prefixos Mais Utilizados")
                for i, (prefixo, count) in enumerate(prefixos.head(5).items()):
                    percentage = (count / len(df)) * 100
                    st.metric(
                        f"{i+1}º {prefixo}",
                        f"{count} códigos",
                        delta=f"{percentage:.1f}%"
                    )
            
            with col2:
                st.markdown("#### 📊 Estatísticas dos Códigos")
                
                # Comprimento médio dos códigos
                comprimento_medio = df['codigo_produto'].str.len().mean()
                st.metric(
                    "Comprimento Médio",
                    f"{comprimento_medio:.1f} caracteres"
                )
                
                # Códigos únicos
                codigos_unicos = df['codigo_produto'].nunique()
                total_produtos = len(df)
                st.metric(
                    "Códigos Únicos",
                    f"{codigos_unicos}/{total_produtos}",
                    delta=f"{(codigos_unicos/total_produtos)*100:.1f}%"
                )
                
                # Padrões mais comuns
                if not df.empty:
                    padrao_mais_comum = df['codigo_produto'].str.extract(r'([A-Z]+-[A-Z]+)').iloc[:, 0].mode()
                    if not padrao_mais_comum.empty:
                        st.metric(
                            "Padrão Mais Comum",
                            padrao_mais_comum.iloc[0]
                        )
            
            # Códigos duplicados (se houver)
            codigos_duplicados = df[df['codigo_produto'].duplicated(keep=False)]
            if not codigos_duplicados.empty:
                st.warning(f"⚠️ Encontrados {len(codigos_duplicados)} códigos duplicados!")
                with st.expander("Ver códigos duplicados"):
                    st.dataframe(codigos_duplicados[['codigo_produto', 'equipamento']])
            else:
                st.success("✅ Todos os códigos são únicos!")
            
            # Sugestões de melhoria
            with st.expander("💡 Sugestões de Melhoria"):
                st.markdown("""
                **Boas práticas para códigos de produto:**
                
                1. **Consistência**: Use sempre o mesmo padrão (ex: XXX-MARCA-###)
                2. **Legibilidade**: Evite caracteres ambíguos (0 vs O, 1 vs I)
                3. **Escalabilidade**: Reserve espaço suficiente para crescimento
                4. **Categoria**: Use prefixos que identifiquem a categoria
                5. **Sequencial**: Mantenha numeração sequencial por categoria
                
                **Padrão recomendado atual:** `CAT-MARCA-NNN`
                - CAT: Categoria (2-3 letras)
                - MARCA: Marca (3-5 letras)
                - NNN: Número sequencial (3 dígitos)
                """)
                
        except Exception as e:
            logger.error(f"Erro ao analisar padrões de códigos: {str(e)}")

def render_codigos_page(estoque_service: EstoqueService) -> None:
    """Função para renderizar a página de códigos"""
    page = CodigosPage(estoque_service)
    page.render() 