"""
Utilitários para gráficos Plotly com recursos modernos
"""

import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
from config.settings import settings

def get_plotly_theme() -> Dict[str, Any]:
    """Retorna tema moderno do Plotly para modo escuro"""
    return {
        'layout': {
            'plot_bgcolor': settings.THEME_COLORS["background"],
            'paper_bgcolor': settings.THEME_COLORS["background"],
            'font': {'color': '#fafafa', 'family': 'Arial, sans-serif'},
            'colorway': ['#00d4ff', '#4ade80', '#fbbf24', '#f87171', '#a78bfa', '#fb7185'],
            'xaxis': {
                'gridcolor': '#404040',
                'linecolor': '#404040',
                'tickfont': {'color': '#fafafa'},
                'showgrid': True,
                'gridwidth': 1
            },
            'yaxis': {
                'gridcolor': '#404040',
                'linecolor': '#404040',
                'tickfont': {'color': '#fafafa'},
                'showgrid': True,
                'gridwidth': 1
            },
            'margin': {'l': 40, 'r': 40, 't': 60, 'b': 40},
            'showlegend': True,
            'legend': {
                'bgcolor': 'rgba(0,0,0,0)',
                'bordercolor': '#404040',
                'borderwidth': 1
            }
        }
    }

def create_pie_chart(df, values_col: str, names_col: str, title: str, **kwargs) -> go.Figure:
    """Cria gráfico de pizza moderno com bordas arredondadas"""
    fig = px.pie(
        df, 
        values=values_col, 
        names=names_col, 
        title=title,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    # Aplicar tema
    fig.update_layout(**get_plotly_theme()['layout'])
    
    # Melhorias visuais modernas
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>',
        marker=dict(
            line=dict(color='#000000', width=2)
        )
    )
    
    return fig

def create_bar_chart(df, x_col: str, y_col: str, title: str, color_col: Optional[str] = None, **kwargs) -> go.Figure:
    """Cria gráfico de barras moderno com bordas arredondadas"""
    if color_col:
        fig = px.bar(
            df, 
            x=x_col, 
            y=y_col, 
            title=title,
            color=color_col,
            color_continuous_scale='viridis'
        )
    else:
        fig = px.bar(
            df, 
            x=x_col, 
            y=y_col, 
            title=title,
            color=y_col,
            color_continuous_scale='viridis'
        )
    
    # Aplicar tema
    fig.update_layout(**get_plotly_theme()['layout'])
    
    # Bordas arredondadas (recurso moderno do Plotly 5.19+)
    fig.update_traces(
        marker=dict(
            cornerradius=8,  # Bordas arredondadas
            line=dict(color='#000000', width=1)
        ),
        hovertemplate='<b>%{x}</b><br>Quantidade: %{y}<extra></extra>'
    )
    
    # Melhorar layout
    fig.update_layout(
        xaxis_tickangle=-45 if len(df) > 5 else 0,
        showlegend=False
    )
    
    return fig

def create_line_chart(x_data: List, y_data: List, title: str, x_label: str = "", y_label: str = "", **kwargs) -> go.Figure:
    """Cria gráfico de linha moderno"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines+markers',
        name='Tendência',
        line=dict(
            color=settings.THEME_COLORS["primary"],
            width=3,
            smoothing=1.0  # Suavização da linha
        ),
        marker=dict(
            color=settings.THEME_COLORS["primary"],
            size=8,
            line=dict(color='white', width=2)
        ),
        hovertemplate='<b>%{x}</b><br>Valor: %{y}<extra></extra>'
    ))
    
    # Aplicar tema
    fig.update_layout(**get_plotly_theme()['layout'])
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        xaxis_tickangle=-45 if len(x_data) > 5 else 0
    )
    
    return fig

def create_treemap(df, path_col: str, values_col: str, title: str, **kwargs) -> go.Figure:
    """Cria treemap moderno com bordas arredondadas"""
    fig = px.treemap(
        df,
        path=[path_col],
        values=values_col,
        title=title,
        color=values_col,
        color_continuous_scale='Reds'
    )
    
    # Aplicar tema
    fig.update_layout(**get_plotly_theme()['layout'])
    
    # Bordas arredondadas para treemap (recurso moderno)
    fig.update_traces(
        marker=dict(cornerradius=5),
        hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<extra></extra>'
    )
    
    return fig


 