import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import streamlit as st

def formatar_moeda(valor):
    """Formata valor para moeda brasileira"""
    return f"R$ {valor:,.2f}"

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

def calcular_metricas_estoque(df_estoque):
    """Calcula métricas principais do estoque"""
    total_equipamentos = df_estoque['quantidade'].sum()
    valor_total = (df_estoque['quantidade'] * df_estoque['valor_unitario']).sum()
    categorias_unicas = df_estoque['categoria'].nunique()
    disponiveis = df_estoque[df_estoque['status'] == 'Disponível']['quantidade'].sum()
    
    return {
        'total_equipamentos': total_equipamentos,
        'valor_total': valor_total,
        'categorias_unicas': categorias_unicas,
        'disponiveis': disponiveis
    }

def criar_grafico_distribuicao_categoria(df_estoque):
    """Cria gráfico de pizza da distribuição por categoria"""
    dados_agrupados = df_estoque.groupby('categoria')['quantidade'].sum().reset_index()
    
    fig = px.pie(
        dados_agrupados,
        values='quantidade',
        names='categoria',
        title='Distribuição por Categoria',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(**get_plotly_theme()['layout'])
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def criar_grafico_quantidade_por_marca(df_estoque):
    """Cria gráfico de barras da quantidade por marca"""
    dados_agrupados = df_estoque.groupby('marca')['quantidade'].sum().reset_index()
    
    fig = px.bar(
        dados_agrupados,
        x='marca',
        y='quantidade',
        title='Quantidade por Marca',
        color='quantidade',
        color_continuous_scale='viridis'
    )
    fig.update_layout(**get_plotly_theme()['layout'])
    return fig

def criar_grafico_temporal_chegadas(df_estoque):
    """Cria gráfico temporal de equipamentos recebidos"""
    df_estoque['data_chegada'] = pd.to_datetime(df_estoque['data_chegada'])
    chegadas_por_mes = df_estoque.groupby(df_estoque['data_chegada'].dt.to_period('M')).size()
    
    fig = px.line(
        x=chegadas_por_mes.index.astype(str),
        y=chegadas_por_mes.values,
        title='Equipamentos Recebidos por Mês',
        labels={'x': 'Mês', 'y': 'Quantidade'}
    )
    fig.update_layout(**get_plotly_theme()['layout'])
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def criar_grafico_valor_por_categoria(df_estoque):
    """Cria gráfico treemap do valor por categoria"""
    valor_por_categoria = df_estoque.groupby('categoria').apply(
        lambda x: (x['quantidade'] * x['valor_unitario']).sum(), include_groups=False
    ).reset_index()
    valor_por_categoria.columns = ['categoria', 'valor_total']
    
    fig = px.treemap(
        valor_por_categoria,
        path=['categoria'],
        values='valor_total',
        title='Valor Total por Categoria',
        color='valor_total',
        color_continuous_scale='Reds'
    )
    fig.update_layout(**get_plotly_theme()['layout'])
    return fig

def criar_grafico_movimentacoes(df_movimentacoes):
    """Cria gráfico de barras das movimentações"""
    dados_agrupados = df_movimentacoes.groupby('tipo_movimentacao').size().reset_index(name='quantidade')
    
    fig = px.bar(
        dados_agrupados,
        x='tipo_movimentacao',
        y='quantidade',
        title='Movimentações por Tipo',
        color='tipo_movimentacao',
        color_discrete_map={'Entrada': 'green', 'Saída': 'red'}
    )
    fig.update_layout(**get_plotly_theme()['layout'])
    return fig

def validar_dados_equipamento(equipamento, marca, modelo, fornecedor):
    """Valida dados obrigatórios do equipamento"""
    if not equipamento or not marca or not modelo or not fornecedor:
        return False, "Todos os campos obrigatórios devem ser preenchidos"
    return True, "Dados válidos"

def validar_remocao_equipamento(df_estoque, equipamento_id, quantidade):
    """Valida se é possível remover a quantidade especificada"""
    if equipamento_id not in df_estoque['id'].values:
        return False, "Equipamento não encontrado"
    
    estoque_atual = df_estoque[df_estoque['id'] == equipamento_id]['quantidade'].iloc[0]
    
    if estoque_atual < quantidade:
        return False, f"Quantidade insuficiente. Disponível: {estoque_atual}"
    
    return True, "Remoção válida"

def aplicar_filtros_movimentacoes(df_movimentacoes, tipo_filtro, data_inicio, data_fim):
    """Aplica filtros no dataframe de movimentações"""
    df_filtrado = df_movimentacoes.copy()
    df_filtrado['data_movimentacao'] = pd.to_datetime(df_filtrado['data_movimentacao'])
    
    if tipo_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado['tipo_movimentacao'] == tipo_filtro]
    
    df_filtrado = df_filtrado[
        (df_filtrado['data_movimentacao'].dt.date >= data_inicio) &
        (df_filtrado['data_movimentacao'].dt.date <= data_fim)
    ]
    
    return df_filtrado

def gerar_relatorio_estoque(df_estoque, df_movimentacoes):
    """Gera relatório completo do estoque"""
    metricas = calcular_metricas_estoque(df_estoque)
    
    relatorio = {
        'metricas': metricas,
        'equipamentos_baixo_estoque': df_estoque[df_estoque['quantidade'] <= 5],
        'equipamentos_indisponiveis': df_estoque[df_estoque['status'] == 'Indisponível'],
        'movimentacoes_recentes': df_movimentacoes.tail(10),
        'categorias_mais_valiosas': df_estoque.groupby('categoria').apply(
            lambda x: (x['quantidade'] * x['valor_unitario']).sum(), include_groups=False
        ).sort_values(ascending=False)
    }
    
    return relatorio 