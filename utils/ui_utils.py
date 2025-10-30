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
    """Cria card de métrica moderno com alto contraste"""
    # Sempre usar st.metric para evitar problemas de renderização HTML
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

def format_currency(value: float) -> str:
    """Formata valor monetário"""
    return f"R$ {value:,.2f}"



def create_info_cards(stats: Dict[str, Any]) -> None:
    """Cria cards informativos com métricas - SEM valor total"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        create_metric_card(
            "Total de Equipamentos", 
            f"{stats.get('total_equipamentos', 0):,}",
            help_text="Quantidade total de equipamentos no estoque"
        )
    
    with col2:
        create_metric_card(
            "Categorias", 
            str(stats.get('categorias_unicas', 0)),
            help_text="Número de categorias diferentes"
        )
    
    with col3:
        create_metric_card(
            "Equipamentos Disponíveis", 
            f"{stats.get('disponiveis', 0):,}",
            help_text="Equipamentos disponíveis para uso"
        )



def create_data_table(df, title: str = "📊 Dados", use_container_width: bool = True) -> None:
    """Cria tabela de dados moderna com alto contraste"""
    # Título simples sem HTML
    st.subheader(title)
    
    if df.empty:
        st.info("Nenhum dado disponível")
        return
    
    # Configurações da tabela moderna (Streamlit 1.42+) com melhor contraste
    try:
        st.dataframe(
            df,
            use_container_width=use_container_width,
            hide_index=True,
            column_config={
                # Configurações específicas por coluna para melhor visibilidade
                **{col: st.column_config.TextColumn(
                    col,
                    help=f"Dados da coluna {col}"
                ) for col in df.columns if df[col].dtype == 'object'},
                **{col: st.column_config.NumberColumn(
                    col,
                    help=f"Valores numéricos da coluna {col}",
                    format="%.0f" if col in ['quantidade', 'id'] else "%.2f"
                ) for col in df.columns if pd.api.types.is_numeric_dtype(df[col])}
            }
        )
    except Exception as e:
        # Fallback para versões antigas
        st.dataframe(df, use_container_width=use_container_width)
        
    # Informações adicionais sem HTML
    st.caption(f"📊 Total de registros: **{len(df)}**")

def create_form_section(title: str, description: Optional[str] = None):
    """Cria seção de formulário com título e descrição"""
    st.markdown(f"## {title}")
    if description:
        st.markdown(f"*{description}*")
    st.markdown("---")

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

def clean_codigo_display(codigo) -> str:
    """Limpa código removendo casas decimais desnecessárias (.00, .0)"""
    if codigo is None:
        return ""

    # Converter para string
    codigo_str = str(codigo).strip()

    # Remover .00 ou .0 se for número inteiro
    if '.00' in codigo_str:
        # Verificar se é um número inteiro com .00
        try:
            num = float(codigo_str)
            if num == int(num):
                return str(int(num))
        except ValueError:
            pass
    elif codigo_str.endswith('.0') and '.' in codigo_str:
        # Verificar se termina com .0 e é número inteiro
        try:
            num = float(codigo_str)
            if num == int(num):
                return str(int(num))
        except ValueError:
            pass

    return codigo_str