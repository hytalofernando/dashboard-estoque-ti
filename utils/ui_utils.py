"""
Utilitários para interface do usuário Streamlit
"""

import streamlit as st
import pandas as pd
from typing import Any, List, Dict, Optional
from loguru import logger
from config.settings import settings

def show_toast(message: str, icon: Optional[str] = None) -> None:
    """Exibe toast moderno (Streamlit 1.42+)"""
    try:
        if icon:
            st.toast(message, icon=icon)
        else:
            st.toast(message)
    except AttributeError:
        # Fallback para versões mais antigas do Streamlit
        if icon:
            st.success(f"{icon} {message}")
        else:
            st.info(message)



def create_metric_card(label: str, value: str, delta: Optional[str] = None, help_text: Optional[str] = None) -> None:
    """Cria card de métrica moderno"""
    st.metric(
        label=label,
        value=value,
        delta=delta,
        help=help_text
    )

def show_success_message(message: str) -> None:
    """Exibe mensagem de sucesso com toast"""
    st.success(message)
    show_toast(message, "✅")

def show_error_message(message: str) -> None:
    """Exibe mensagem de erro com toast"""
    st.error(message)
    show_toast(message, "❌")

def show_warning_message(message: str) -> None:
    """Exibe mensagem de aviso com toast"""
    st.warning(message)
    show_toast(message, "⚠️")

def show_info_message(message: str) -> None:
    """Exibe mensagem informativa com toast"""
    st.info(message)
    show_toast(message, "ℹ️")

def create_status_indicator(status: str) -> str:
    """Cria indicador visual de status"""
    status_map = {
        "Disponível": "🟢",
        "Indisponível": "🔴", 
        "Manutenção": "🟡"
    }
    return f"{status_map.get(status, '⚪')} {status}"

def format_currency(value: float) -> str:
    """Formata valor monetário"""
    return f"R$ {value:,.2f}"



def create_info_cards(stats: Dict[str, Any]) -> None:
    """Cria cards informativos com métricas"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_metric_card(
            "Total de Equipamentos", 
            f"{stats.get('total_equipamentos', 0):,}",
            help_text="Quantidade total de equipamentos no estoque"
        )
    
    with col2:
        create_metric_card(
            "Valor Total do Estoque", 
            format_currency(stats.get('valor_total', 0)),
            help_text="Valor total de todos os equipamentos"
        )
    
    with col3:
        create_metric_card(
            "Categorias", 
            str(stats.get('categorias_unicas', 0)),
            help_text="Número de categorias diferentes"
        )
    
    with col4:
        create_metric_card(
            "Equipamentos Disponíveis", 
            f"{stats.get('disponiveis', 0):,}",
            help_text="Equipamentos disponíveis para uso"
        )



def create_filter_sidebar(df, title: str = "🔍 Filtros") -> Dict[str, Any]:
    """Cria sidebar de filtros"""
    st.sidebar.markdown(f"## {title}")
    
    filters = {}
    
    # Filtro por categoria
    if 'categoria' in df.columns:
        categorias = ["Todas"] + sorted(df['categoria'].unique().tolist())
        filters['categoria'] = st.sidebar.selectbox("Categoria", categorias)
    
    # Filtro por marca
    if 'marca' in df.columns:
        marcas = ["Todas"] + sorted(df['marca'].unique().tolist())
        filters['marca'] = st.sidebar.selectbox("Marca", marcas)
    
    # Filtro por status
    if 'status' in df.columns:
        status_list = ["Todos"] + sorted(df['status'].unique().tolist())
        filters['status'] = st.sidebar.selectbox("Status", status_list)
    
    # Busca por código/nome
    filters['busca'] = st.sidebar.text_input("🔍 Buscar por código ou nome")
    
    return filters

def create_data_table(df, title: str = "📊 Dados", use_container_width: bool = True) -> None:
    """Cria tabela de dados moderna"""
    st.markdown(f"### {title}")
    
    if df.empty:
        st.info("Nenhum dado disponível")
        return
    
    # Configurações da tabela moderna (Streamlit 1.42+)
    try:
        st.dataframe(
            df,
            use_container_width=use_container_width,
            hide_index=True,
            column_config={
                # Configurações específicas por coluna se necessário
            }
        )
    except:
        # Fallback para versões antigas
        st.dataframe(df, use_container_width=use_container_width)

def create_form_section(title: str, description: Optional[str] = None):
    """Cria seção de formulário com título e descrição"""
    st.markdown(f"## {title}")
    if description:
        st.markdown(f"*{description}*")
    st.markdown("---")

def create_action_buttons(primary_label: str, secondary_label: Optional[str] = None, 
                         primary_type: str = "primary", disabled: bool = False) -> Dict[str, bool]:
    """Cria botões de ação"""
    col1, col2 = st.columns(2)
    
    buttons = {}
    
    with col1:
        buttons['primary'] = st.button(
            primary_label, 
            type=primary_type,
            disabled=disabled,
            use_container_width=True
        )
    
    with col2:
        if secondary_label:
            buttons['secondary'] = st.button(
                secondary_label,
                disabled=disabled,
                use_container_width=True
            )
    
    return buttons





def show_confirmation_dialog(message: str, key: str) -> bool:
    """Exibe diálogo de confirmação"""
    return st.checkbox(f"✅ {message}", key=key)





def format_dataframe_for_display(df):
    """Formata DataFrame para exibição"""
    if df.empty:
        return df
    
    df_display = df.copy()
    
    # Formatar colunas monetárias
    money_columns = ['valor_unitario', 'valor_total']
    for col in money_columns:
        if col in df_display.columns:
            df_display[col] = df_display[col].apply(lambda x: format_currency(x) if pd.notna(x) else "")
    
    # Formatar status - normalizar para strings simples
    if 'status' in df_display.columns:
        df_display['status'] = df_display['status'].apply(normalizar_status_equipamento)
    
    return df_display 

def normalizar_status_equipamento(status: str) -> str:
    """Normaliza status de equipamentos para manter consistência visual"""
    if not status or pd.isna(status):
        return "Disponível"  # Default
    
    status_str = str(status).strip()
    
    # Converter enums para strings simples
    if "DISPONIVEL" in status_str.upper() or "Disponível" in status_str:
        return "Disponível"
    elif "INDISPONIVEL" in status_str.upper() or "Indisponível" in status_str:
        return "Indisponível"
    elif "MANUTENCAO" in status_str.upper() or "Manutenção" in status_str:
        return "Manutenção"
    else:
        # Fallback: assumir disponível se não conseguir determinar
        return "Disponível"

def render_status_badge(status: str) -> None:
    """Renderiza badge de status com cores semânticas (bolinhas coloridas)"""
    status_normalizado = normalizar_status_equipamento(status)
    
    if status_normalizado == "Disponível":
        st.success(f"🟢 {status_normalizado}")  # Bolinha verde
    elif status_normalizado == "Indisponível":
        st.error(f"🔴 {status_normalizado}")    # Bolinha vermelha
    elif status_normalizado == "Manutenção":
        st.warning(f"🟡 {status_normalizado}")  # Bolinha amarela
    else:
        st.info(f"⚪ {status_normalizado}")      # Bolinha branca (fallback) 