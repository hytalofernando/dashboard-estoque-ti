import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import openpyxl
from datetime import datetime, timedelta
import os
from pathlib import Path

# Configuração da página
st.set_page_config(
    page_title="💻 Dashboard Estoque TI",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modo escuro sempre ativo
DARK_MODE = True

def get_css_theme():
    """Retorna CSS para modo escuro"""
    return """
    <style>
        /* Configuração global do modo escuro */
        .stApp {
            background-color: #0e1117 !important;
        }
        
        /* Header principal */
        .main-header {
            font-size: 3rem;
            color: #ffffff !important;
            text-align: center;
            margin-bottom: 2rem;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }
        
        /* Sidebar - usando seletores mais específicos */
        section[data-testid="stSidebar"] {
            background-color: #262730 !important;
        }
        
        section[data-testid="stSidebar"] .css-1lcbmhc {
            background-color: #262730 !important;
        }
        
        /* Texto da sidebar */
        section[data-testid="stSidebar"] .css-1v0mbdj,
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: #ffffff !important;
        }
        
        /* Selectbox da sidebar */
        section[data-testid="stSidebar"] .stSelectbox > div > div {
            background-color: #262730 !important;
            color: #ffffff !important;
        }
        
        /* Toggle da sidebar */
        section[data-testid="stSidebar"] .stToggle > div > div {
            background-color: #404040 !important;
        }
        
        section[data-testid="stSidebar"] .stToggle > div > div[data-checked="true"] {
            background-color: #00d4ff !important;
        }
        
        /* Cards de métricas */
        .metric-card {
            background-color: #262730 !important;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #00d4ff;
            color: #ffffff !important;
        }
        
        /* Mensagens */
        .success-message {
            background-color: #1e4d2b !important;
            color: #4ade80 !important;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #22c55e;
        }
        
        .warning-message {
            background-color: #4d3c00 !important;
            color: #fbbf24 !important;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #f59e0b;
        }
        
        .error-message {
            background-color: #4d1a1a !important;
            color: #f87171 !important;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #ef4444;
        }
        
        /* Formulários */
        .stForm {
            background-color: #262730 !important;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #404040;
        }
        
        /* Campos de entrada */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #262730 !important;
            color: #ffffff !important;
            border: 1px solid #404040 !important;
        }
        
        /* Selectbox */
        .stSelectbox > div > div {
            background-color: #262730 !important;
            color: #ffffff !important;
        }
        
        /* Dataframe */
        .stDataFrame {
            background-color: #262730 !important;
            color: #ffffff !important;
        }
        
        /* Métricas */
        .stMetric {
            background-color: #262730 !important;
            color: #ffffff !important;
        }
        
        /* Botões */
        .stButton > button {
            background-color: #00d4ff !important;
            color: #000000 !important;
            border: none !important;
            border-radius: 0.5rem !important;
            padding: 0.5rem 1rem !important;
            font-weight: bold !important;
        }
        
        .stButton > button:hover {
            background-color: #0099cc !important;
            color: #ffffff !important;
        }
        
        /* Toggle */
        .stToggle > div > div {
            background-color: #404040 !important;
        }
        
        .stToggle > div > div[data-checked="true"] {
            background-color: #00d4ff !important;
        }
        
        /* Texto geral - CORRIGIDO para melhor legibilidade */
        .css-1v0mbdj, .css-1v0mbdj p, .css-1v0mbdj div {
            color: #ffffff !important;
        }
        
        /* Títulos - CORRIGIDO para melhor legibilidade */
        h1, h2, h3, h4, h5, h6 {
            color: #ffffff !important;
        }
        
        /* Texto específico do Streamlit */
        .stMarkdown, .stMarkdown p {
            color: #ffffff !important;
        }
        
        /* Labels e textos de formulários */
        .stTextInput label, .stNumberInput label, .stSelectbox label, .stTextArea label {
            color: #ffffff !important;
        }
        
        /* Texto das métricas */
        .stMetric > div > div > div {
            color: #ffffff !important;
        }
        
        /* Texto dos dataframes */
        .stDataFrame > div > div > div {
            color: #ffffff !important;
        }
        
        /* Links */
        a {
            color: #00d4ff !important;
        }
        
        /* Separadores */
        hr {
            border-color: #404040 !important;
        }
        
        /* Tooltips */
        .tooltip {
            background-color: #262730 !important;
            color: #ffffff !important;
            border: 1px solid #404040 !important;
        }
        
        /* Scrollbar customizada */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #262730;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #404040;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #00d4ff;
        }
        
        /* Melhorias específicas para legibilidade */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #ffffff !important;
            font-weight: bold !important;
        }
        
        .stMarkdown p {
            color: #ffffff !important;
            line-height: 1.6 !important;
        }
        
        /* Texto das colunas */
        .stColumn > div {
            color: #ffffff !important;
        }
        
        /* Texto dos containers */
        .stContainer > div {
            color: #ffffff !important;
        }
        
        /* Forçar cor branca em todos os elementos de texto */
        * {
            color: #ffffff !important;
        }
        
        /* Exceções para elementos que devem manter cores específicas */
        .stButton > button {
            color: #000000 !important;
        }
        
        .success-message {
            color: #4ade80 !important;
        }
        
        .warning-message {
            color: #fbbf24 !important;
        }
        
        .error-message {
            color: #f87171 !important;
        }
        
        a {
            color: #00d4ff !important;
        }
        
        /* Texto dos gráficos Plotly */
        .js-plotly-plot .plotly .main-svg {
            color: #ffffff !important;
        }
        
        /* Override para elementos específicos do Streamlit */
        .stMarkdown, .stMarkdown *, .stText, .stText * {
            color: #ffffff !important;
        }
    </style>
    """

# Aplicar CSS do modo escuro
st.markdown(get_css_theme(), unsafe_allow_html=True)

class EstoqueTI:
    def __init__(self):
        self.excel_file = "estoque_ti.xlsx"
        self.load_data()
    
    def load_data(self):
        """Carrega dados do Excel ou cria arquivo se não existir"""
        if os.path.exists(self.excel_file):
            try:
                self.df_estoque = pd.read_excel(self.excel_file, sheet_name='Estoque')
                self.df_movimentacoes = pd.read_excel(self.excel_file, sheet_name='Movimentacoes')
            except:
                self.create_initial_data()
        else:
            self.create_initial_data()
    
    def create_initial_data(self):
        """Cria estrutura inicial do Excel com dados de exemplo"""
        # Dados de exemplo para estoque
        self.df_estoque = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'equipamento': ['Notebook Dell Latitude', 'Monitor LG 24"', 'Impressora HP LaserJet', 'Switch Cisco 24P', 'Servidor Dell PowerEdge'],
            'categoria': ['Notebook', 'Monitor', 'Impressora', 'Rede', 'Servidor'],
            'marca': ['Dell', 'LG', 'HP', 'Cisco', 'Dell'],
            'modelo': ['Latitude 5520', '24ML600', 'LaserJet Pro', 'Catalyst 2960', 'PowerEdge R740'],
            'quantidade': [15, 25, 8, 12, 3],
            'valor_unitario': [3500.00, 800.00, 1200.00, 2500.00, 15000.00],
            'data_chegada': ['2024-01-15', '2024-02-10', '2024-01-20', '2024-03-05', '2024-02-28'],
            'fornecedor': ['Dell Brasil', 'LG Electronics', 'HP Brasil', 'Cisco Systems', 'Dell Brasil'],
            'status': ['Disponível', 'Disponível', 'Disponível', 'Disponível', 'Disponível']
        })
        
        # Dados de exemplo para movimentações
        self.df_movimentacoes = pd.DataFrame({
            'id': [1, 2, 3],
            'equipamento_id': [1, 2, 3],
            'tipo_movimentacao': ['Entrada', 'Saída', 'Entrada'],
            'quantidade': [15, 5, 8],
            'data_movimentacao': ['2024-01-15', '2024-02-15', '2024-01-20'],
            'destino_origem': ['Fornecedor: Dell Brasil', 'Loja: Shopping Center', 'Fornecedor: HP Brasil'],
            'observacoes': ['Compra inicial', 'Transferência para loja', 'Compra inicial']
        })
        
        self.save_data()
    
    def save_data(self):
        """Salva dados no Excel"""
        with pd.ExcelWriter(self.excel_file, engine='openpyxl') as writer:
            self.df_estoque.to_excel(writer, sheet_name='Estoque', index=False)
            self.df_movimentacoes.to_excel(writer, sheet_name='Movimentacoes', index=False)
    
    def adicionar_equipamento(self, equipamento, categoria, marca, modelo, quantidade, valor_unitario, fornecedor):
        """Adiciona novo equipamento ao estoque"""
        novo_id = self.df_estoque['id'].max() + 1 if not self.df_estoque.empty else 1
        
        novo_equipamento = {
            'id': novo_id,
            'equipamento': equipamento,
            'categoria': categoria,
            'marca': marca,
            'modelo': modelo,
            'quantidade': quantidade,
            'valor_unitario': valor_unitario,
            'data_chegada': datetime.now().strftime('%Y-%m-%d'),
            'fornecedor': fornecedor,
            'status': 'Disponível'
        }
        
        self.df_estoque = pd.concat([self.df_estoque, pd.DataFrame([novo_equipamento])], ignore_index=True)
        
        # Registrar movimentação de entrada
        self.registrar_movimentacao(novo_id, 'Entrada', quantidade, f'Fornecedor: {fornecedor}', 'Adição inicial ao estoque')
        
        self.save_data()
        return True
    
    def remover_equipamento(self, equipamento_id, quantidade, destino, observacoes):
        """Remove equipamento do estoque"""
        if equipamento_id in self.df_estoque['id'].values:
            idx = self.df_estoque[self.df_estoque['id'] == equipamento_id].index[0]
            estoque_atual = self.df_estoque.loc[idx, 'quantidade']
            
            if estoque_atual >= quantidade:
                self.df_estoque.loc[idx, 'quantidade'] = estoque_atual - quantidade
                
                # Atualizar status se quantidade chegar a zero
                if self.df_estoque.loc[idx, 'quantidade'] == 0:
                    self.df_estoque.loc[idx, 'status'] = 'Indisponível'
                
                # Registrar movimentação de saída
                self.registrar_movimentacao(equipamento_id, 'Saída', quantidade, destino, observacoes)
                
                self.save_data()
                return True
            else:
                return False
        return False
    
    def registrar_movimentacao(self, equipamento_id, tipo, quantidade, destino_origem, observacoes):
        """Registra movimentação no histórico"""
        novo_id = self.df_movimentacoes['id'].max() + 1 if not self.df_movimentacoes.empty else 1
        
        nova_movimentacao = {
            'id': novo_id,
            'equipamento_id': equipamento_id,
            'tipo_movimentacao': tipo,
            'quantidade': quantidade,
            'data_movimentacao': datetime.now().strftime('%Y-%m-%d'),
            'destino_origem': destino_origem,
            'observacoes': observacoes
        }
        
        self.df_movimentacoes = pd.concat([self.df_movimentacoes, pd.DataFrame([nova_movimentacao])], ignore_index=True)

def get_plotly_theme():
    """Retorna tema do Plotly para modo escuro"""
    return {
        'layout': {
            'plot_bgcolor': '#0e1117',
            'paper_bgcolor': '#0e1117',
            'font': {'color': '#fafafa'},
            'xaxis': {
                'gridcolor': '#404040',
                'linecolor': '#404040',
                'tickfont': {'color': '#fafafa'}
            },
            'yaxis': {
                'gridcolor': '#404040',
                'linecolor': '#404040',
                'tickfont': {'color': '#fafafa'}
            }
        }
    }

def main():
    # Inicializar sistema de estoque
    estoque = EstoqueTI()
    
    # Sidebar para navegação
    st.sidebar.title("��️ Controles")
    
    st.sidebar.markdown("---")
    
    # Navegação
    pagina = st.sidebar.selectbox(
        "📱 Navegação:",
        ["📈 Dashboard", "➕ Adicionar Equipamento", "➖ Remover Equipamento", "📋 Histórico de Movimentações"]
    )
    
    # Header principal com ícone de notebook
    st.markdown('<h1 class="main-header">💻 Dashboard Estoque TI</h1>', unsafe_allow_html=True)
    
    if pagina == "📈 Dashboard":
        mostrar_dashboard(estoque)
    elif pagina == "➕ Adicionar Equipamento":
        adicionar_equipamento_page(estoque)
    elif pagina == "➖ Remover Equipamento":
        remover_equipamento_page(estoque)
    elif pagina == "📋 Histórico de Movimentações":
        historico_movimentacoes_page(estoque)

def mostrar_dashboard(estoque):
    """Página principal do dashboard com análises visuais"""
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_equipamentos = estoque.df_estoque['quantidade'].sum()
        st.metric("Total de Equipamentos", f"{total_equipamentos:,}")
    
    with col2:
        valor_total = (estoque.df_estoque['quantidade'] * estoque.df_estoque['valor_unitario']).sum()
        st.metric("Valor Total do Estoque", f"R$ {valor_total:,.2f}")
    
    with col3:
        categorias_unicas = estoque.df_estoque['categoria'].nunique()
        st.metric("Categorias de Equipamentos", categorias_unicas)
    
    with col4:
        disponiveis = estoque.df_estoque[estoque.df_estoque['status'] == 'Disponível']['quantidade'].sum()
        st.metric("Equipamentos Disponíveis", disponiveis)
    
    st.markdown("---")
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de pizza por categoria
        fig_pizza = px.pie(
            estoque.df_estoque.groupby('categoria')['quantidade'].sum().reset_index(),
            values='quantidade',
            names='categoria',
            title='Distribuição por Categoria',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pizza.update_layout(**get_plotly_theme()['layout'])
        fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pizza, use_container_width=True)
        
        # Gráfico de barras por marca
        fig_barras = px.bar(
            estoque.df_estoque.groupby('marca')['quantidade'].sum().reset_index(),
            x='marca',
            y='quantidade',
            title='Quantidade por Marca',
            color='quantidade',
            color_continuous_scale='viridis'
        )
        fig_barras.update_layout(**get_plotly_theme()['layout'])
        st.plotly_chart(fig_barras, use_container_width=True)
    
    with col2:
        # Gráfico de linha temporal
        estoque.df_estoque['data_chegada'] = pd.to_datetime(estoque.df_estoque['data_chegada'])
        chegadas_por_mes = estoque.df_estoque.groupby(estoque.df_estoque['data_chegada'].dt.to_period('M')).size()
        
        fig_temporal = px.line(
            x=chegadas_por_mes.index.astype(str),
            y=chegadas_por_mes.values,
            title='Equipamentos Recebidos por Mês',
            labels={'x': 'Mês', 'y': 'Quantidade'}
        )
        fig_temporal.update_layout(**get_plotly_theme()['layout'])
        fig_temporal.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_temporal, use_container_width=True)
        
        # Gráfico de valor por categoria
        valor_por_categoria = estoque.df_estoque.groupby('categoria').apply(
            lambda x: (x['quantidade'] * x['valor_unitario']).sum(), include_groups=False
        ).reset_index()
        valor_por_categoria.columns = ['categoria', 'valor_total']
        
        fig_valor = px.treemap(
            valor_por_categoria,
            path=['categoria'],
            values='valor_total',
            title='Valor Total por Categoria',
            color='valor_total',
            color_continuous_scale='Reds'
        )
        fig_valor.update_layout(**get_plotly_theme()['layout'])
        st.plotly_chart(fig_valor, use_container_width=True)
    
    # Tabela de estoque atual
    st.markdown("### 📋 Estoque Atual")
    df_display = estoque.df_estoque.copy()
    df_display['valor_total'] = df_display['quantidade'] * df_display['valor_unitario']
    df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
    df_display['valor_unitario'] = df_display['valor_unitario'].apply(lambda x: f"R$ {x:,.2f}")
    
    st.dataframe(
        df_display[['equipamento', 'categoria', 'marca', 'modelo', 'quantidade', 'valor_unitario', 'valor_total', 'status']],
        use_container_width=True
    )

def adicionar_equipamento_page(estoque):
    """Página para adicionar novos equipamentos"""
    st.markdown("## ➕ Adicionar Novo Equipamento")
    
    with st.form("adicionar_equipamento"):
        col1, col2 = st.columns(2)
        
        with col1:
            equipamento = st.text_input("Nome do Equipamento", placeholder="Ex: Notebook Dell Latitude")
            categoria = st.selectbox("Categoria", ["Notebook", "Monitor", "Impressora", "Rede", "Servidor", "Periférico", "Outro"])
            marca = st.text_input("Marca", placeholder="Ex: Dell")
            modelo = st.text_input("Modelo", placeholder="Ex: Latitude 5520")
        
        with col2:
            quantidade = st.number_input("Quantidade", min_value=1, value=1)
            valor_unitario = st.number_input("Valor Unitário (R$)", min_value=0.0, value=0.0, step=0.01)
            fornecedor = st.text_input("Fornecedor", placeholder="Ex: Dell Brasil")
        
        submitted = st.form_submit_button("Adicionar ao Estoque")
        
        if submitted:
            if equipamento and marca and modelo and fornecedor:
                success = estoque.adicionar_equipamento(
                    equipamento, categoria, marca, modelo, quantidade, valor_unitario, fornecedor
                )
                if success:
                    st.success("✅ Equipamento adicionado com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao adicionar equipamento")
            else:
                st.warning("⚠️ Preencha todos os campos obrigatórios")

def remover_equipamento_page(estoque):
    """Página para remover equipamentos"""
    st.markdown("## ➖ Remover Equipamento")
    
    # Selecionar equipamento
    equipamentos_disponiveis = estoque.df_estoque[estoque.df_estoque['quantidade'] > 0]
    
    if equipamentos_disponiveis.empty:
        st.warning("⚠️ Não há equipamentos disponíveis para remoção")
        return
    
    with st.form("remover_equipamento"):
        equipamento_id = st.selectbox(
            "Selecione o Equipamento",
            options=equipamentos_disponiveis['id'].tolist(),
            format_func=lambda x: f"{equipamentos_disponiveis[equipamentos_disponiveis['id'] == x]['equipamento'].iloc[0]} - Qtd: {equipamentos_disponiveis[equipamentos_disponiveis['id'] == x]['quantidade'].iloc[0]}"
        )
        
        equipamento_selecionado = equipamentos_disponiveis[equipamentos_disponiveis['id'] == equipamento_id].iloc[0]
        quantidade_maxima = equipamento_selecionado['quantidade']
        
        quantidade = st.number_input("Quantidade a Remover", min_value=1, max_value=quantidade_maxima, value=1)
        destino = st.text_input("Destino", placeholder="Ex: Loja Shopping Center")
        observacoes = st.text_area("Observações", placeholder="Ex: Transferência para nova loja")
        
        submitted = st.form_submit_button("Remover do Estoque")
        
        if submitted:
            if destino:
                success = estoque.remover_equipamento(equipamento_id, quantidade, destino, observacoes)
                if success:
                    st.success("✅ Equipamento removido com sucesso!")
                    st.rerun()
                else:
                    st.error("❌ Erro ao remover equipamento")
            else:
                st.warning("⚠️ Preencha o campo de destino")

def historico_movimentacoes_page(estoque):
    """Página com histórico de movimentações"""
    st.markdown("## 📋 Histórico de Movimentações")
    
    # Filtrar movimentações
    col1, col2 = st.columns(2)
    
    with col1:
        tipo_filtro = st.selectbox("Filtrar por Tipo", ["Todos"] + estoque.df_movimentacoes['tipo_movimentacao'].unique().tolist())
    
    with col2:
        data_inicio = st.date_input("Data Início", value=datetime.now() - timedelta(days=30))
        data_fim = st.date_input("Data Fim", value=datetime.now())
    
    # Aplicar filtros
    df_filtrado = estoque.df_movimentacoes.copy()
    df_filtrado['data_movimentacao'] = pd.to_datetime(df_filtrado['data_movimentacao'])
    
    if tipo_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado['tipo_movimentacao'] == tipo_filtro]
    
    df_filtrado = df_filtrado[
        (df_filtrado['data_movimentacao'].dt.date >= data_inicio) &
        (df_filtrado['data_movimentacao'].dt.date <= data_fim)
    ]
    
    # Adicionar informações do equipamento
    df_filtrado = df_filtrado.merge(
        estoque.df_estoque[['id', 'equipamento', 'categoria']],
        left_on='equipamento_id',
        right_on='id',
        suffixes=('', '_equip')
    )
    
    # Gráfico de movimentações
    fig_movimentacoes = px.bar(
        df_filtrado.groupby('tipo_movimentacao').size().reset_index(name='quantidade'),
        x='tipo_movimentacao',
        y='quantidade',
        title='Movimentações por Tipo',
        color='tipo_movimentacao',
        color_discrete_map={'Entrada': 'green', 'Saída': 'red'}
    )
    fig_movimentacoes.update_layout(**get_plotly_theme()['layout'])
    st.plotly_chart(fig_movimentacoes, use_container_width=True)
    
    # Tabela de movimentações
    st.markdown("### 📊 Detalhes das Movimentações")
    df_display = df_filtrado[['data_movimentacao', 'equipamento', 'categoria', 'tipo_movimentacao', 'quantidade', 'destino_origem', 'observacoes']].sort_values('data_movimentacao', ascending=False)
    
    st.dataframe(df_display, use_container_width=True)

if __name__ == "__main__":
    main() 