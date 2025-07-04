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