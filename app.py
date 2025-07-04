import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl
from datetime import datetime, timedelta
import os
from utils import get_plotly_theme

# Configuração da página
st.set_page_config(
    page_title="💻 Dashboard Estoque TI",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar o CSS otimizado
def load_theme_css():
    with open("theme.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
                
                # Verificar se a coluna codigo_produto existe, se não, adicionar
                if 'codigo_produto' not in self.df_estoque.columns:
                    self.migrate_data()
            except:
                self.create_initial_data()
        else:
            self.create_initial_data()
    
    def migrate_data(self):
        """Migra dados existentes para incluir código do produto"""
        # Gerar códigos para produtos existentes
        codigos = []
        for idx, row in self.df_estoque.iterrows():
            categoria = row['categoria']
            marca = row['marca']
            
            # Gerar código baseado na categoria e marca
            if categoria == 'Notebook':
                prefixo = 'NB'
            elif categoria == 'Monitor':
                prefixo = 'MON'
            elif categoria == 'Impressora':
                prefixo = 'IMP'
            elif categoria == 'Rede':
                prefixo = 'SW'
            elif categoria == 'Servidor':
                prefixo = 'SRV'
            elif categoria == 'Periférico':
                prefixo = 'PER'
            else:
                prefixo = 'OUT'
            
            # Criar código único
            codigo = f"{prefixo}-{marca.upper()}-{idx+1:03d}"
            codigos.append(codigo)
        
        # Adicionar coluna de código do produto
        self.df_estoque['codigo_produto'] = codigos
        
        # Salvar dados migrados
        self.save_data()
    
    def create_initial_data(self):
        """Cria estrutura inicial do Excel com dados de exemplo"""
        # Dados de exemplo para estoque
        self.df_estoque = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'equipamento': ['Notebook Dell Latitude', 'Monitor LG 24"', 'Impressora HP LaserJet', 'Switch Cisco 24P', 'Servidor Dell PowerEdge'],
            'categoria': ['Notebook', 'Monitor', 'Impressora', 'Rede', 'Servidor'],
            'marca': ['Dell', 'LG', 'HP', 'Cisco', 'Dell'],
            'modelo': ['Latitude 5520', '24ML600', 'LaserJet Pro', 'Catalyst 2960', 'PowerEdge R740'],
            'codigo_produto': ['NB-DELL-001', 'MON-LG-002', 'IMP-HP-003', 'SW-CISCO-004', 'SRV-DELL-005'],
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
    
    def adicionar_equipamento(self, equipamento, categoria, marca, modelo, codigo_produto, quantidade, valor_unitario, fornecedor):
        """Adiciona novo equipamento ao estoque"""
        novo_id = self.df_estoque['id'].max() + 1 if not self.df_estoque.empty else 1
        
        novo_equipamento = {
            'id': novo_id,
            'equipamento': equipamento,
            'categoria': categoria,
            'marca': marca,
            'modelo': modelo,
            'codigo_produto': codigo_produto,
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



def mostrar_notificacao(tipo, mensagem):
    """Exibe notificação com estilo melhorado para modo escuro"""
    if tipo == "success":
        st.markdown(f"""
        <div class="success-message">
            <strong>✅ {mensagem}</strong>
        </div>
        """, unsafe_allow_html=True)
    elif tipo == "warning":
        st.markdown(f"""
        <div class="warning-message">
            <strong>⚠️ {mensagem}</strong>
        </div>
        """, unsafe_allow_html=True)
    elif tipo == "error":
        st.markdown(f"""
        <div class="error-message">
            <strong>❌ {mensagem}</strong>
        </div>
        """, unsafe_allow_html=True)



def main():
    # Inicializar sistema de estoque
    estoque = EstoqueTI()
    
    # Aplicar tema escuro - VERSÃO SIMPLIFICADA
    load_theme_css()
    
    # Sidebar para navegação
    st.sidebar.title("🔧 Controles")
    
    st.sidebar.markdown("---")
    
    # Navegação
    pagina = st.sidebar.selectbox(
        "📱 Navegação:",
        ["📈 Dashboard", "➕ Adicionar Equipamento", "➖ Remover Equipamento", "📋 Histórico de Movimentações", "🏷️ Código Produto"]
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
    elif pagina == "🏷️ Código Produto":
        codigo_produto_page(estoque)

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
    
    # Verificar se a coluna codigo_produto existe
    colunas_exibicao = ['equipamento', 'categoria', 'marca', 'modelo', 'quantidade', 'valor_unitario', 'valor_total', 'status']
    if 'codigo_produto' in df_display.columns:
        colunas_exibicao.insert(0, 'codigo_produto')
    
    st.dataframe(
        df_display[colunas_exibicao],
        use_container_width=True
    )

def adicionar_equipamento_page(estoque):
    """Página para adicionar novos equipamentos"""
    st.markdown("## ➕ Adicionar Novo Equipamento")
    
    # Inicializar session_state para controlar reset
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    if 'form_message' not in st.session_state:
        st.session_state.form_message = ""
    if 'form_message_type' not in st.session_state:
        st.session_state.form_message_type = ""
    
    # Mostrar mensagem de feedback se existir
    if st.session_state.form_message:
        mostrar_notificacao(st.session_state.form_message_type, st.session_state.form_message)
        # Limpar mensagem após exibir
        st.session_state.form_message = ""
        st.session_state.form_message_type = ""
    
    # Informações sobre a operação
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Total de Equipamentos:** {len(estoque.df_estoque)}")
    with col2:
        st.info(f"**Categorias:** {estoque.df_estoque['categoria'].nunique()}")
    with col3:
        st.info(f"**Marcas:** {estoque.df_estoque['marca'].nunique()}")
    
    st.markdown("---")
    
    with st.form("adicionar_equipamento", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            equipamento = st.text_input("Nome do Equipamento", placeholder="Ex: Notebook Dell Latitude")
            categoria = st.selectbox("Categoria", ["Notebook", "Monitor", "Impressora", "Rede", "Servidor", "Periférico", "Outro"])
            marca = st.text_input("Marca", placeholder="Ex: Dell")
            modelo = st.text_input("Modelo", placeholder="Ex: Latitude 5520")
            codigo_produto = st.text_input("Código do Produto", placeholder="Ex: NB-DELL-001")
        
        with col2:
            quantidade = st.number_input("Quantidade", min_value=1, value=1)
            valor_unitario = st.number_input("Valor Unitário (R$)", min_value=0.0, value=0.0, step=0.01)
            fornecedor = st.text_input("Fornecedor", placeholder="Ex: Dell Brasil")
        
        # Mostrar valor total calculado
        if valor_unitario > 0 and quantidade > 0:
            valor_total = valor_unitario * quantidade
            st.markdown(f"**💰 Valor Total:** R$ {valor_total:,.2f}")
        
        submitted = st.form_submit_button("✅ Adicionar ao Estoque")
        
        if submitted:
            if equipamento and marca and modelo and codigo_produto and fornecedor:
                success = estoque.adicionar_equipamento(
                    equipamento, categoria, marca, modelo, codigo_produto, quantidade, valor_unitario, fornecedor
                )
                if success:
                    st.session_state.form_message = f"✅ Equipamento '{equipamento}' adicionado com sucesso! (Qtd: {quantidade})"
                    st.session_state.form_message_type = "success"
                    st.rerun()
                else:
                    st.session_state.form_message = "❌ Erro ao adicionar equipamento"
                    st.session_state.form_message_type = "error"
                    st.rerun()
            else:
                st.session_state.form_message = "⚠️ Preencha todos os campos obrigatórios"
                st.session_state.form_message_type = "warning"
                st.rerun()

def remover_equipamento_page(estoque):
    """Página para remover equipamentos"""
    st.markdown("## ➖ Remover Equipamento")
    
    # Inicializar session_state para controlar reset
    if 'remove_form_submitted' not in st.session_state:
        st.session_state.remove_form_submitted = False
    if 'remove_form_message' not in st.session_state:
        st.session_state.remove_form_message = ""
    if 'remove_form_message_type' not in st.session_state:
        st.session_state.remove_form_message_type = ""
    
    # Mostrar mensagem de feedback se existir
    if st.session_state.remove_form_message:
        mostrar_notificacao(st.session_state.remove_form_message_type, st.session_state.remove_form_message)
        # Limpar mensagem após exibir
        st.session_state.remove_form_message = ""
        st.session_state.remove_form_message_type = ""
    
    # Selecionar equipamento
    equipamentos_disponiveis = estoque.df_estoque[estoque.df_estoque['quantidade'] > 0]
    
    if equipamentos_disponiveis.empty:
        mostrar_notificacao("warning", "Não há equipamentos disponíveis para remoção")
        return
    
    # Informações sobre a operação
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Equipamentos Disponíveis:** {len(equipamentos_disponiveis)}")
    with col2:
        total_disponivel = equipamentos_disponiveis['quantidade'].sum()
        st.info(f"**Quantidade Total:** {total_disponivel}")
    with col3:
        valor_total_disponivel = (equipamentos_disponiveis['quantidade'] * equipamentos_disponiveis['valor_unitario']).sum()
        st.info(f"**Valor Total:** R$ {valor_total_disponivel:,.2f}")
    
    st.markdown("---")
    
    with st.form("remover_equipamento", clear_on_submit=True):
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
        
        # Mostrar informações do equipamento selecionado
        if equipamento_id:
            st.markdown(f"**📦 Equipamento Selecionado:** {equipamento_selecionado['equipamento']}")
            st.markdown(f"**🏷️ Código:** {equipamento_selecionado.get('codigo_produto', 'N/A')}")
            st.markdown(f"**💰 Valor Unitário:** R$ {equipamento_selecionado['valor_unitario']:,.2f}")
            st.markdown(f"**📊 Quantidade Disponível:** {quantidade_maxima}")
        
        submitted = st.form_submit_button("❌ Remover do Estoque")
        
        if submitted:
            if destino:
                success = estoque.remover_equipamento(equipamento_id, quantidade, destino, observacoes)
                if success:
                    st.session_state.remove_form_message = f"✅ Equipamento removido com sucesso! (Qtd: {quantidade})"
                    st.session_state.remove_form_message_type = "success"
                    st.rerun()
                else:
                    st.session_state.remove_form_message = "❌ Erro ao remover equipamento"
                    st.session_state.remove_form_message_type = "error"
                    st.rerun()
            else:
                st.session_state.remove_form_message = "⚠️ Preencha o campo de destino"
                st.session_state.remove_form_message_type = "warning"
                st.rerun()

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

def codigo_produto_page(estoque):
    """Página para visualização e busca de códigos de produtos"""
    st.markdown("## 🏷️ Código Produto")
    
    # Métricas dos códigos
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_codigos = len(estoque.df_estoque)
        st.metric("Total de Produtos", total_codigos)
    
    with col2:
        categorias_com_codigo = estoque.df_estoque['categoria'].nunique()
        st.metric("Categorias com Código", categorias_com_codigo)
    
    with col3:
        marcas_com_codigo = estoque.df_estoque['marca'].nunique()
        st.metric("Marcas com Código", marcas_com_codigo)
    
    st.markdown("---")
    
    # Filtros de busca
    col1, col2 = st.columns(2)
    
    with col1:
        categoria_filtro = st.selectbox(
            "Filtrar por Categoria",
            ["Todas"] + estoque.df_estoque['categoria'].unique().tolist()
        )
    
    with col2:
        marca_filtro = st.selectbox(
            "Filtrar por Marca",
            ["Todas"] + estoque.df_estoque['marca'].unique().tolist()
        )
    
    # Busca por código
    codigo_busca = st.text_input("🔍 Buscar por Código do Produto", placeholder="Digite o código para buscar...")
    
    # Aplicar filtros
    df_filtrado = estoque.df_estoque.copy()
    
    if categoria_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_filtro]
    
    if marca_filtro != "Todas":
        df_filtrado = df_filtrado[df_filtrado['marca'] == marca_filtro]
    
    if codigo_busca:
        df_filtrado = df_filtrado[
            (df_filtrado['codigo_produto'].str.contains(codigo_busca, case=False, na=False) if 'codigo_produto' in df_filtrado.columns else False) |
            df_filtrado['equipamento'].str.contains(codigo_busca, case=False, na=False)
        ]
    
    # Gráfico de distribuição por categoria
    if not df_filtrado.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            fig_categoria = px.pie(
                df_filtrado.groupby('categoria').size().reset_index(name='quantidade'),
                values='quantidade',
                names='categoria',
                title='Produtos por Categoria',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_categoria.update_layout(**get_plotly_theme()['layout'])
            fig_categoria.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_categoria, use_container_width=True)
        
        with col2:
            fig_marca = px.bar(
                df_filtrado.groupby('marca').size().reset_index(name='quantidade'),
                x='marca',
                y='quantidade',
                title='Produtos por Marca',
                color='quantidade',
                color_continuous_scale='viridis'
            )
            fig_marca.update_layout(**get_plotly_theme()['layout'])
            st.plotly_chart(fig_marca, use_container_width=True)
    
    # Tabela de códigos de produtos
    st.markdown("### 📋 Códigos dos Produtos")
    
    if not df_filtrado.empty:
        # Preparar dados para exibição
        df_display = df_filtrado.copy()
        df_display['valor_total'] = df_display['quantidade'] * df_display['valor_unitario']
        df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
        df_display['valor_unitario'] = df_display['valor_unitario'].apply(lambda x: f"R$ {x:,.2f}")
        
        # Ordenar por código do produto
        if 'codigo_produto' in df_display.columns:
            df_display = df_display.sort_values('codigo_produto')
        
        # Exibir tabela com códigos em destaque
        colunas_exibicao = ['equipamento', 'categoria', 'marca', 'modelo', 'quantidade', 'valor_unitario', 'valor_total', 'status']
        if 'codigo_produto' in df_display.columns:
            colunas_exibicao.insert(0, 'codigo_produto')
        
        st.dataframe(
            df_display[colunas_exibicao],
            use_container_width=True
        )
        
        # Estatísticas dos códigos
        st.markdown("### 📊 Estatísticas dos Códigos")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info(f"**Produtos Encontrados:** {len(df_filtrado)}")
        
        with col2:
            if not df_filtrado.empty:
                valor_total_filtrado = df_filtrado['quantidade'].sum() * df_filtrado['valor_unitario'].sum()
                st.info(f"**Valor Total:** R$ {valor_total_filtrado:,.2f}")
            else:
                st.info("**Valor Total:** R$ 0,00")
        
        with col3:
            if not df_filtrado.empty:
                disponiveis_filtrado = df_filtrado[df_filtrado['status'] == 'Disponível']['quantidade'].sum()
                st.info(f"**Disponíveis:** {disponiveis_filtrado}")
            else:
                st.info("**Disponíveis:** 0")
    
    else:
        st.warning("⚠️ Nenhum produto encontrado com os filtros aplicados.")
        
        if codigo_busca:
            st.info("💡 **Dica:** Verifique se o código foi digitado corretamente ou tente uma busca mais ampla.")
        
        # Mostrar todos os produtos se não houver resultados
        if codigo_busca or categoria_filtro != "Todas" or marca_filtro != "Todas":
            st.markdown("### 📋 Todos os Produtos")
            df_display = estoque.df_estoque.copy()
            df_display['valor_total'] = df_display['quantidade'] * df_display['valor_unitario']
            df_display['valor_total'] = df_display['valor_total'].apply(lambda x: f"R$ {x:,.2f}")
            df_display['valor_unitario'] = df_display['valor_unitario'].apply(lambda x: f"R$ {x:,.2f}")
            
            if 'codigo_produto' in df_display.columns:
                df_display = df_display.sort_values('codigo_produto')
            
            colunas_exibicao = ['equipamento', 'categoria', 'marca', 'modelo', 'quantidade', 'valor_unitario', 'valor_total', 'status']
            if 'codigo_produto' in df_display.columns:
                colunas_exibicao.insert(0, 'codigo_produto')
            
            st.dataframe(
                df_display[colunas_exibicao],
                use_container_width=True
            )

if __name__ == "__main__":
    main() 