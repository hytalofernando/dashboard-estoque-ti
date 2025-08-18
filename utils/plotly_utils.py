"""
Utilitários para gráficos Plotly com recursos modernos
"""

import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
from config.settings import settings

def get_plotly_theme() -> Dict[str, Any]:
    """Retorna tema moderno do Plotly harmonizado com o design system"""
    return {
        'layout': {
            'plot_bgcolor': settings.THEME_COLORS["background"],
            'paper_bgcolor': settings.THEME_COLORS["background"],
            'font': {
                'color': settings.THEME_COLORS["text_secondary"], 
                'family': 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
                'size': 12
            },
            'colorway': settings.CHART_COLORS,
            'title': {
                'font': {
                    'color': settings.THEME_COLORS["text_primary"],
                    'size': 16,
                    'family': 'Inter, sans-serif'
                },
                'x': 0.5,
                'xanchor': 'center'
            },
            'xaxis': {
                'gridcolor': settings.THEME_COLORS["background_tertiary"],
                'linecolor': settings.THEME_COLORS["background_tertiary"],
                'tickfont': {'color': settings.THEME_COLORS["text_tertiary"]},
                'showgrid': True,
                'gridwidth': 1,
                'zeroline': False,
                'title': {'font': {'color': settings.THEME_COLORS["text_secondary"]}}
            },
            'yaxis': {
                'gridcolor': settings.THEME_COLORS["background_tertiary"],
                'linecolor': settings.THEME_COLORS["background_tertiary"],
                'tickfont': {'color': settings.THEME_COLORS["text_tertiary"]},
                'showgrid': True,
                'gridwidth': 1,
                'zeroline': False,
                'title': {'font': {'color': settings.THEME_COLORS["text_secondary"]}}
            },
            'margin': {'l': 50, 'r': 30, 't': 80, 'b': 50},
            'showlegend': True,
            'legend': {
                'bgcolor': 'rgba(26, 29, 35, 0.8)',
                'bordercolor': settings.THEME_COLORS["background_tertiary"],
                'borderwidth': 1,
                'font': {'color': settings.THEME_COLORS["text_secondary"]},
                'orientation': 'v',
                'x': 1.02,
                'y': 1
            },
            'hovermode': 'closest',
            'hoverlabel': {
                'bgcolor': settings.THEME_COLORS["background_card"],
                'bordercolor': settings.THEME_COLORS["primary"],
                'font': {'color': settings.THEME_COLORS["text_primary"]}
            }
        }
    }

def create_pie_chart(df, values_col: str, names_col: str, title: str, **kwargs) -> go.Figure:
    """Cria gráfico de pizza moderno com paleta harmonizada"""
    fig = px.pie(
        df, 
        values=values_col, 
        names=names_col, 
        title=title,
        color_discrete_sequence=settings.CHART_COLORS
    )
    
    # Aplicar tema
    fig.update_layout(**get_plotly_theme()['layout'])
    
    # Melhorias visuais modernas
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont=dict(
            size=11,
            color=settings.THEME_COLORS["text_primary"]
        ),
        hovertemplate='<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>',
        marker=dict(
            line=dict(
                color=settings.THEME_COLORS["background"], 
                width=3
            )
        ),
        pull=[0.05] * len(df)  # Separação sutil entre fatias
    )
    
    return fig

def create_bar_chart(df, x_col: str, y_col: str, title: str, color_col: Optional[str] = None, **kwargs) -> go.Figure:
    """Cria gráfico de barras moderno com paleta harmonizada"""
    if color_col:
        fig = px.bar(
            df, 
            x=x_col, 
            y=y_col, 
            title=title,
            color=color_col,
            color_discrete_sequence=settings.CHART_COLORS
        )
    else:
        fig = px.bar(
            df, 
            x=x_col, 
            y=y_col, 
            title=title,
            color_discrete_sequence=settings.CHART_COLORS
        )
    
    # Aplicar tema
    fig.update_layout(**get_plotly_theme()['layout'])
    
    # Melhorias visuais modernas
    fig.update_traces(
        marker=dict(
            cornerradius=8,  # Bordas arredondadas
            line=dict(
                color=settings.THEME_COLORS["background"], 
                width=2
            ),
            opacity=0.9
        ),
        hovertemplate='<b>%{x}</b><br>Quantidade: %{y}<extra></extra>',
        texttemplate='%{y}',
        textposition='outside',
        textfont=dict(
            color=settings.THEME_COLORS["text_secondary"],
            size=10
        )
    )
    
    # Melhorar layout
    fig.update_layout(
        xaxis_tickangle=-45 if len(df) > 5 else 0,
        showlegend=False,
        bargap=0.3,  # Espaçamento entre barras
        bargroupgap=0.1
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


 