"""
Página Profissional para Remover Equipamentos - Versão 2.0
Tecnologias: Streamlit 1.42+ | Session State | Filtros Avançados | Operações em Lote
"""

import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List
from loguru import logger
from datetime import datetime

from services.estoque_service import EstoqueService
from models.schemas import CondicionEquipamento
from utils.ui_utils import (
    create_form_section,
    show_success_message,
    show_error_message,
    show_warning_message,
    show_toast,
    format_dataframe_for_display,
    clean_codigo_display
)
from config.settings import settings

# ✅ SISTEMA DE AUTENTICAÇÃO
from auth.auth_service import auth_service

def normalizar_condicao_equipamento(condicao_raw) -> str:
    """Normaliza condição do equipamento para formato válido do enum"""
    if not condicao_raw:
        return CondicionEquipamento.NOVO.value

    # Se já for um valor válido, retornar como está
    if condicao_raw in [CondicionEquipamento.NOVO.value, CondicionEquipamento.USADO.value]:
        return condicao_raw

    # Se for string com formato "CondicionEquipamento.XYZ", extrair o valor
    condicao_str = str(condicao_raw)
    if 'CondicionEquipamento.' in condicao_str:
        if 'NOVO' in condicao_str:
            return CondicionEquipamento.NOVO.value
        elif 'USADO' in condicao_str:
            return CondicionEquipamento.USADO.value

    # Se for apenas "NOVO" ou "USADO" maiúsculo
    if condicao_str.upper() == 'NOVO':
        return CondicionEquipamento.NOVO.value
    elif condicao_str.upper() == 'USADO':
        return CondicionEquipamento.USADO.value

    # Valor padrão
    return CondicionEquipamento.NOVO.value

class RemoverEquipamentoPageProfessional:
    """Página Profissional para Remover Equipamentos com Tecnologias Modernas"""
    
    def __init__(self, estoque_service: EstoqueService):
        self.estoque_service = estoque_service
    
    def render(self) -> None:
        """Renderiza a página moderna de remover equipamentos"""
        # ✅ VERIFICAR PERMISSÕES PRIMEIRO
        if not auth_service.can_edit():
            st.error("🚫 **Acesso Negado**")
            st.warning("⚠️ **Visualizadores não podem remover equipamentos.**")
            st.info("💡 **Apenas Administradores podem realizar esta operação.**")
            
            # Mostrar informações do usuário atual
            user = auth_service.get_current_user()
            st.markdown(f"**👤 Usuário atual:** {user.display_name} ({user.profile.title()})")
            
            # Botão para voltar ao dashboard
            if st.button("📊 Voltar ao Dashboard", type="primary"):
                st.switch_page("app.py")
            return
        
        create_form_section(
            "🗑️ Remover Equipamentos - Sistema Profissional",
            "Remova equipamentos com busca inteligente, filtros avançados e operações em lote"
        )
        
        # Cache e dados
        equipamentos_cache = self._get_equipamentos_cache()
        df_disponivel = self._get_equipamentos_disponiveis()
        
        if df_disponivel.empty:
            st.error("❌ **Nenhum equipamento disponível para remoção**")
            st.info("💡 Adicione equipamentos primeiro na página 'Adicionar Equipamentos'")
            return
        
        # Layout com tabs para organizar funcionalidades
        tab_busca, tab_lote, tab_historico, tab_config = st.tabs([
            "🔍 Busca & Remoção", 
            "📦 Operações em Lote", 
            "📋 Histórico",
            "⚙️ Configurações"
        ])
        
        with tab_busca:
            self._render_busca_inteligente(equipamentos_cache, df_disponivel)
        
        with tab_lote:
            self._render_operacoes_lote(df_disponivel)
            
        with tab_historico:
            self._render_historico_remocoes()
            
        with tab_config:
            self._render_configuracoes_avancadas()
    
    def _get_equipamentos_cache(self) -> Dict[str, Dict]:
        """Cache otimizado com session_state para busca inteligente - VERSÃO MELHORADA"""
        cache_key = 'equipamentos_cache_remover'
        
        # ✅ FORÇAR RELOAD SE CACHE INVALIDADO OU MUITO ANTIGO
        cache_invalido = (
            cache_key not in st.session_state or 
            st.session_state.get('cache_remover_invalidated', True) or
            st.session_state.get('cache_invalidated', True) or
            st.session_state.get('historico_cache_invalidated', True)
        )
        
        if cache_invalido:
            try:
                logger.info("🔄 Carregando cache de equipamentos para remoção...")
                
                # ✅ SEMPRE BUSCAR DADOS FRESCOS DO BANCO COM RECARREGAMENTO
                self.estoque_service.recarregar_dados()  # ✅ FORÇAR RECARREGAMENTO DO EXCEL
                df_estoque = self.estoque_service.obter_equipamentos()
                df_disponivel = df_estoque[df_estoque['quantidade'] > 0]
                
                cache_equipamentos = {}
                
                for _, row in df_disponivel.iterrows():
                    codigo = clean_codigo_display(row.get('codigo_produto', '')).upper()
                    if codigo:
                        cache_equipamentos[codigo] = {
                            'codigo_produto': codigo,
                            'equipamento': row.get('equipamento', ''),
                            'categoria': row.get('categoria', ''),
                            'marca': row.get('marca', ''),
                            'modelo': row.get('modelo', ''),
                            'quantidade': row.get('quantidade', 0),
                            'valor_unitario': row.get('valor_unitario', 0.0),
                            'condicao': row.get('condicao', 'Novo'),
                            'observacoes': row.get('observacoes', ''),
                            'data_cadastro': row.get('data_cadastro', '')
                        }
                
                # ✅ ATUALIZAR CACHE E RESETAR FLAGS
                st.session_state[cache_key] = cache_equipamentos
                st.session_state['cache_remover_invalidated'] = False
                st.session_state['cache_invalidated'] = False
                st.session_state['historico_cache_invalidated'] = False
                
                # ✅ DEBUG DETALHADO NA SIDEBAR
                st.sidebar.success(f"✅ Cache Remoção: {len(cache_equipamentos)} equipamentos")
                st.sidebar.caption(f"🔄 Última atualização: {datetime.now().strftime('%H:%M:%S')}")
                
                # ✅ DEBUG EXTRA: Mostrar alguns equipamentos no cache
                if len(cache_equipamentos) > 0:
                    exemplo_equipamentos = list(cache_equipamentos.items())[:3]
                    with st.sidebar.expander("🔍 Debug Cache", expanded=False):
                        for codigo, info in exemplo_equipamentos:
                            st.text(f"{codigo}: {info['quantidade']} un.")
                
                logger.info(f"✅ Cache carregado para remoção: {len(cache_equipamentos)} equipamentos")
                
            except Exception as e:
                logger.error(f"❌ Erro ao carregar cache: {str(e)}")
                st.session_state[cache_key] = {}
                st.sidebar.error(f"❌ Erro no cache: {str(e)}")
        else:
            # ✅ USAR CACHE EXISTENTE MAS MOSTRAR INFO
            cache_equipamentos = st.session_state.get(cache_key, {})
            st.sidebar.info(f"📋 Cache Remoção: {len(cache_equipamentos)} equipamentos (cached)")
        
        return st.session_state.get(cache_key, {})
    
    def _get_equipamentos_disponiveis(self) -> pd.DataFrame:
        """Obtém equipamentos disponíveis com filtros aplicados"""
        try:
            # ✅ SEMPRE RECARREGAR DADOS DO EXCEL PARA GARANTIR CONSISTÊNCIA
            self.estoque_service.recarregar_dados()
            df_estoque = self.estoque_service.obter_equipamentos()
            df_disponivel = df_estoque[df_estoque['quantidade'] > 0].copy()
            
            if df_disponivel.empty:
                return df_disponivel
            
            # Aplicar filtros da sidebar
            df_filtrado = self._aplicar_filtros_sidebar(df_disponivel)
            
            return df_filtrado
            
        except Exception as e:
            logger.error(f"Erro ao obter equipamentos disponíveis: {str(e)}")
            return pd.DataFrame()
    
    def _aplicar_filtros_sidebar(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica filtros avançados na sidebar"""
        st.sidebar.markdown("### 🔧 Filtros Avançados")
        
        # Filtro por categoria
        categorias = ['Todas'] + list(df['categoria'].unique())
        categoria_selecionada = st.sidebar.selectbox(
            "📂 Categoria", 
            categorias,
            key="filtro_categoria_remover"
        )
        
        # Filtro por marca
        marcas = ['Todas'] + list(df['marca'].unique())
        marca_selecionada = st.sidebar.selectbox(
            "🏢 Marca", 
            marcas,
            key="filtro_marca_remover"
        )
        
        # Filtro por faixa de valor
        if not df.empty:
            valor_min = float(df['valor_unitario'].min())
            valor_max = float(df['valor_unitario'].max())
            
            faixa_valor = st.sidebar.slider(
                "💰 Faixa de Valor (R$)",
                min_value=valor_min,
                max_value=valor_max,
                value=(valor_min, valor_max),
                key="filtro_valor_remover"
            )
        
        # Filtro por quantidade disponível
        if not df.empty:
            qtd_min = int(df['quantidade'].min())
            qtd_max = int(df['quantidade'].max())
            
            faixa_quantidade = st.sidebar.slider(
                "📊 Quantidade Disponível",
                min_value=qtd_min,
                max_value=qtd_max,
                value=(qtd_min, qtd_max),
                key="filtro_quantidade_remover"
            )
        
        # Aplicar filtros
        df_filtrado = df.copy()
        
        if categoria_selecionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_selecionada]
        
        if marca_selecionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['marca'] == marca_selecionada]
        
        if not df.empty:
            df_filtrado = df_filtrado[
                (df_filtrado['valor_unitario'] >= faixa_valor[0]) &
                (df_filtrado['valor_unitario'] <= faixa_valor[1])
            ]
            
            df_filtrado = df_filtrado[
                (df_filtrado['quantidade'] >= faixa_quantidade[0]) &
                (df_filtrado['quantidade'] <= faixa_quantidade[1])
            ]
        
        # Mostrar estatísticas dos filtros
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Resultado dos Filtros")
        st.sidebar.metric("📦 Equipamentos", len(df_filtrado))
        if not df_filtrado.empty:
            valor_total_filtrado = (df_filtrado['quantidade'] * df_filtrado['valor_unitario']).sum()
            st.sidebar.metric("💰 Valor Total", f"R$ {valor_total_filtrado:,.2f}")
        
        return df_filtrado
    
    def _render_busca_inteligente(self, equipamentos_cache: Dict, df_disponivel: pd.DataFrame) -> None:
        """Renderiza sistema de busca inteligente e remoção individual - CORRIGIDO"""
        
        # Estatísticas principais
        self._render_estatisticas_principais(df_disponivel)
        
        st.markdown("### 🎯 Busca Inteligente de Equipamentos")
        
        # Sistema de busca com opções separadas
        col_tipo1, col_tipo2 = st.columns(2)
        
        with col_tipo1:
            tipo_busca = st.radio(
                "📌 Tipo de Busca:",
                ["🏷️ Por Código", "📦 Por Nome/Marca"],
                horizontal=True,
                key="tipo_busca_remover"
            )
        
        with col_tipo2:
            st.caption("💡 **Dica:** Busca por código é mais precisa e rápida!")
        
        # Campos de busca baseados no tipo selecionado
        col_busca1, col_busca2, col_busca3 = st.columns([2, 1, 1])
        
        with col_busca1:
            if "Código" in tipo_busca:
                # Busca específica por código
                codigo_busca = st.text_input(
                    "🏷️ Digite o Código do Produto",
                    placeholder="Ex: NB-DELL-001, 21588, MON-LG-001",
                    help="Busca apenas no campo CÓDIGO (mais precisa)",
                    key="busca_codigo_field"
                ).strip()
            else:
                # Busca por nome/marca
                codigo_busca = st.text_input(
                    "📦 Digite Nome do Equipamento ou Marca",
                    placeholder="Ex: Notebook, Dell, Monitor",
                    help="Busca em Nome, Marca e Categoria",
                    key="busca_nome_field"
                ).strip()
        
        with col_busca2:
            if st.button("🔄 Recarregar", use_container_width=True):
                st.session_state['cache_remover_invalidated'] = True
                st.rerun()
        
        with col_busca3:
            if st.button("🧹 Limpar", use_container_width=True):
                if 'busca_codigo_field' in st.session_state:
                    st.session_state['busca_codigo_field'] = ""
                if 'busca_nome_field' in st.session_state:
                    st.session_state['busca_nome_field'] = ""
                st.rerun()
        
        # BUSCA INTELIGENTE COM TIPO ESPECÍFICO
        equipamentos_encontrados = []
        tipo_busca_selecionado = st.session_state.get('tipo_busca_remover', '🏷️ Por Código')
        
        if codigo_busca and len(codigo_busca.strip()) >= 2:  # Mínimo 2 caracteres
            codigo_busca_upper = codigo_busca.strip().upper()

            # Busca baseada no tipo selecionado
            for _, row in df_disponivel.iterrows():
                # Converter campos para string
                codigo = str(row.get('codigo_produto', '')).upper()
                nome = str(row.get('equipamento', '')).upper()
                marca = str(row.get('marca', '')).upper()
                modelo = str(row.get('modelo', '')).upper()
                categoria = str(row.get('categoria', '')).upper()

                # Lógica de busca baseada no tipo
                encontrado = False
                
                if "Código" in tipo_busca_selecionado:
                    # Busca APENAS por código (mais precisa)
                    if codigo_busca_upper in codigo:
                        encontrado = True
                else:
                    # Busca por nome, marca, categoria (não código)
                    if (codigo_busca_upper in nome or
                        codigo_busca_upper in marca or
                        codigo_busca_upper in modelo or
                        codigo_busca_upper in categoria):
                        encontrado = True
                
                if encontrado:
                    equipamentos_encontrados.append(row)
            
            # Mostrar resultados da busca
            if equipamentos_encontrados:
                st.success(f"✅ **{len(equipamentos_encontrados)} equipamento(s) encontrado(s) para '{codigo_busca}'**")
                
                # Mostrar equipamentos encontrados com melhor organização
                for i, equipamento in enumerate(equipamentos_encontrados):
                    # Destacar o termo buscado no título
                    # Acessar com .get() para evitar KeyError
                    titulo_equipamento = f"📦 {equipamento.get('equipamento', 'N/A')} - {equipamento.get('codigo_produto', 'N/A')}"
                    subtitulo = f"({equipamento.get('quantidade', 0)} unidades disponíveis | R$ {equipamento.get('valor_unitario', 0):,.2f} cada)"
                    
                    with st.expander(
                        f"{titulo_equipamento} {subtitulo}",
                        expanded=i == 0  # Expandir apenas o primeiro
                    ):
                        self._render_formulario_remocao_individual(equipamento)
            else:
                st.warning(f"❌ Nenhum equipamento encontrado para: `{codigo_busca}`")
                
                # Sugestões inteligentes melhoradas
                if len(codigo_busca) >= 3:
                    sugestoes = []
                    for _, row in df_disponivel.head(5).iterrows():
                        codigo = clean_codigo_display(row.get('codigo_produto', ''))
                        nome = str(row.get('equipamento', ''))
                        sugestoes.append(f"`{codigo}` - {nome}")
                    
                    if sugestoes:
                        st.info(f"💡 **Sugestões (digite estes códigos):**")
                        for sugestao in sugestoes:
                            st.markdown(f"• {sugestao}")
        
        # Mostrar alguns equipamentos como exemplo quando não há busca
        elif not codigo_busca:
            if "Código" in tipo_busca_selecionado:
                st.info("💡 **Digite pelo menos 2 caracteres do CÓDIGO para buscar** (ex: 21588, NB-DELL)")
                
                # Mostrar exemplos de códigos disponíveis
                if not df_disponivel.empty:
                    exemplos = []
                    for _, row in df_disponivel.head(5).iterrows():
                        codigo = str(row.get('codigo_produto', ''))
                        nome = str(row.get('equipamento', ''))
                        exemplos.append(f"`{codigo}` - {nome}")
                    
                    if exemplos:
                        st.markdown("**📋 Exemplos de códigos disponíveis:**")
                        for exemplo in exemplos:
                            st.markdown(f"• {exemplo}")
            else:
                st.info("💡 **Digite pelo menos 2 caracteres do NOME ou MARCA para buscar** (ex: Notebook, Dell)")
                
                # Mostrar exemplos de equipamentos
                if not df_disponivel.empty:
                    exemplos = []
                    for _, row in df_disponivel.head(5).iterrows():
                        nome = str(row.get('equipamento', ''))
                        marca = str(row.get('marca', ''))
                        exemplos.append(f"**{nome}** ({marca})")
                    
                    if exemplos:
                        st.markdown("**📋 Exemplos de equipamentos disponíveis:**")
                        for exemplo in exemplos:
                            st.markdown(f"• {exemplo}")
        
        # Tabela de equipamentos disponíveis
        st.markdown("---")
        self._render_tabela_equipamentos_disponiveis(df_disponivel)
    
    def _render_estatisticas_principais(self, df_disponivel: pd.DataFrame) -> None:
        """Renderiza estatísticas principais"""
        if df_disponivel.empty:
            return
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📦 Equipamentos", len(df_disponivel))
        
        with col2:
            quantidade_total = df_disponivel['quantidade'].sum()
            st.metric("📊 Unidades Total", f"{quantidade_total:,}")
        
        with col3:
            valor_total = (df_disponivel['quantidade'] * df_disponivel['valor_unitario']).sum()
            st.metric("💰 Valor Total", f"R$ {valor_total:,.2f}")
        
        with col4:
            # Equipamentos com estoque baixo (menos de 5 unidades)
            estoque_baixo = len(df_disponivel[df_disponivel['quantidade'] < 5])
            st.metric("⚠️ Estoque Baixo", estoque_baixo)
            if estoque_baixo > 0:
                st.caption("📉 Menos de 5 unidades")
    
    def _render_formulario_remocao_individual(self, equipamento: pd.Series) -> None:
        """Renderiza formulário para remoção individual - TOTALMENTE SEM 'id'"""
        
        # Extrair dados do equipamento (pandas Series)
        try:
            codigo_produto = str(equipamento.get('codigo_produto', equipamento.name if hasattr(equipamento, 'name') else 'N/A'))
            nome_equipamento = str(equipamento.get('equipamento', equipamento.get('Nome', 'N/A')))
            categoria = str(equipamento.get('categoria', equipamento.get('Categoria', 'N/A')))
            marca = str(equipamento.get('marca', equipamento.get('Marca', 'N/A')))
            modelo = str(equipamento.get('modelo', equipamento.get('Modelo', 'N/A')))
            quantidade_disp = int(equipamento.get('quantidade', equipamento.get('Quantidade', 0)))
            valor_unit = float(equipamento.get('valor_unitario', equipamento.get('Valor Unitário', 0)))
            condicao_raw = equipamento.get('condicao', equipamento.get('Condição', 'Novo'))
        except Exception as e:
            st.error(f"❌ Erro ao processar equipamento: {str(e)}")
            return
        
        # Informações do equipamento
        col_info1, col_info2, col_info3, col_info4 = st.columns(4)
        
        with col_info1:
            st.markdown(f"**🖥️ Equipamento:** {nome_equipamento}")
            st.markdown(f"**📂 Categoria:** {categoria}")
        
        with col_info2:
            st.markdown(f"**🏢 Marca:** {marca}")
            st.markdown(f"**🔧 Modelo:** {modelo}")
        
        with col_info3:
            st.markdown(f"**📊 Disponível:** {quantidade_disp} unidades")
            st.markdown(f"**💰 Valor Unit:** R$ {valor_unit:,.2f}")
            
        with col_info4:
            condicao_atual = normalizar_condicao_equipamento(condicao_raw)
            icon_condicao = "🆕" if condicao_atual == "Novo" else "🔄" if condicao_atual == "Usado" else "❓"
            st.markdown(f"**{icon_condicao} Condição:** {condicao_atual}")
            st.markdown(f"**🔢 Código:** {codigo_produto}")
            
        # Verificar se existem outras condições para o mesmo código
        if codigo_produto and codigo_produto != 'N/A':
            agrupado = self.estoque_service.agrupar_equipamentos_por_codigo(str(codigo_produto))
            if agrupado and (agrupado.get('qtd_novos', 0) > 0 and agrupado.get('qtd_usados', 0) > 0):
                st.info(f"📦 **Estoque total por código {codigo_produto}:** "
                       f"🆕 Novos: {agrupado['qtd_novos']} un. | "
                       f"🔄 Usados: {agrupado['qtd_usados']} un. | "
                       f"📊 Total: {agrupado['qtd_total']} un.")
        
        # Preview da operação
        st.markdown("---")
        # Criar key única usando código + condição + timestamp para evitar conflitos
        import time
        codigo_key = str(codigo_produto).replace('-', '_').replace('.', '_')
        timestamp_key = str(int(time.time() * 1000) % 10000)  # Últimos 4 dígitos
        quantidade_key = f"qtd_remover_{codigo_key}_{timestamp_key}"
        
        # Formulário de remoção COM KEYS ÚNICAS
        form_key = f"remover_{codigo_key}_{timestamp_key}"
        with st.form(form_key, clear_on_submit=True):
            col_form1, col_form2 = st.columns(2)
            
            with col_form1:
                # ✅ SELEÇÃO DA CONDIÇÃO (COMO NA PÁGINA ADICIONAR)
                condicao_atual = normalizar_condicao_equipamento(condicao_raw)
                
                # Verificar se existem outras condições para o mesmo código
                agrupado = self.estoque_service.agrupar_equipamentos_por_codigo(str(codigo_produto)) if codigo_produto and codigo_produto != 'N/A' else {}
                
                if agrupado and agrupado.get('qtd_novos', 0) > 0 and agrupado.get('qtd_usados', 0) > 0:
                    # Múltiplas condições disponíveis - permitir escolha
                    st.info(f"💡 **Código {codigo_produto}:** 🆕 {agrupado['qtd_novos']} Novos | 🔄 {agrupado['qtd_usados']} Usados")
                    
                    condicao_selecionada = st.selectbox(
                        "🔄 Selecione a Condição para Remoção",
                        options=[CondicionEquipamento.NOVO.value, CondicionEquipamento.USADO.value],
                        index=0 if condicao_atual == CondicionEquipamento.NOVO.value else 1,
                        help="💡 Escolha se deseja remover um equipamento NOVO ou USADO",
                        key=f"condicao_{timestamp_key}"
                    )
                    
                    # Mostrar estoque disponível para a condição selecionada
                    if condicao_selecionada == CondicionEquipamento.NOVO.value:
                        qtd_disponivel = agrupado.get('qtd_novos', 0)
                        st.success(f"✅ **{qtd_disponivel} unidades Novas** disponíveis para remoção")
                    else:
                        qtd_disponivel = agrupado.get('qtd_usados', 0)
                        st.success(f"✅ **{qtd_disponivel} unidades Usadas** disponíveis para remoção")
                else:
                    # Apenas uma condição disponível - confirmar apenas
                    condicao_selecionada = condicao_atual
                    st.info(f"📦 **Condição:** {condicao_atual} (única disponível)")
                    qtd_disponivel = quantidade_disp
                
                # Determinar quantidade máxima
                if agrupado and agrupado.get('qtd_novos', 0) > 0 and agrupado.get('qtd_usados', 0) > 0:
                    max_quantidade = qtd_disponivel
                    help_text = f"💡 {qtd_disponivel} unidades {condicao_selecionada} disponíveis"
                else:
                    max_quantidade = quantidade_disp
                    help_text = f"💡 {quantidade_disp} unidades disponíveis"
                
                # Botões de atalho rápido para quantidade
                st.markdown("**⚡ Atalhos Rápidos:**")
                col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                
                with col_btn1:
                    if st.form_submit_button("1 un.", use_container_width=True):
                        st.session_state[quantidade_key] = 1
                with col_btn2:
                    if st.form_submit_button("5 un.", use_container_width=True) and max_quantidade >= 5:
                        st.session_state[quantidade_key] = min(5, max_quantidade)
                with col_btn3:
                    if st.form_submit_button("10 un.", use_container_width=True) and max_quantidade >= 10:
                        st.session_state[quantidade_key] = min(10, max_quantidade)
                with col_btn4:
                    if st.form_submit_button(f"Tudo ({max_quantidade})", use_container_width=True):
                        st.session_state[quantidade_key] = max_quantidade
                
                st.markdown("---")
                
                # Campo de quantidade
                quantidade = st.number_input(
                    "📊 Quantidade a Remover",
                    min_value=1,
                    max_value=max_quantidade,
                    value=min(st.session_state.get(quantidade_key, 1), max_quantidade),
                    step=1,
                    help=help_text,
                    key=quantidade_key
                )
                
                destino = st.text_input(
                    "📍 Destino",
                    placeholder="Ex: Filial SP, Cliente XYZ",
                    help="Para onde está sendo enviado",
                    key=f"destino_{timestamp_key}"
                )
            
            with col_form2:
                codigo_saida = st.text_input(
                    "🏷️ Código de Saída",
                    placeholder="Ex: SAIDA-001-2024",
                    help="Código para rastreamento",
                    key=f"codigo_saida_{timestamp_key}"
                )
                
                observacoes = st.text_area(
                    "📝 Observações",
                    placeholder="Motivo da remoção, destino específico, etc.",
                    help="Informações adicionais",
                    key=f"obs_{timestamp_key}"
                )
            
            # Cálculos e alertas (só quando quantidade > 0)
            if quantidade > 0:
                valor_total = quantidade * valor_unit
                nova_quantidade = quantidade_disp - quantidade
                percentual = (quantidade / quantidade_disp) * 100
                
                # ✅ PREVIEW DOS CÁLCULOS EM TEMPO REAL
                st.markdown("---")
                st.markdown("### 📊 **Preview da Operação:**")
                
                col_calc1, col_calc2, col_calc3 = st.columns(3)
                with col_calc1:
                    st.markdown(f"**📦 Remover:** {quantidade} unidades")
                    st.markdown(f"**💰 Valor:** R$ {valor_total:,.2f}")
                with col_calc2:
                    st.markdown(f"**📊 Atual:** {quantidade_disp} unidades")
                    st.markdown(f"**🔄 Operação:** -{quantidade}")
                with col_calc3:
                    st.markdown(f"**📈 Resultado:** {nova_quantidade} unidades")
                    st.markdown(f"**📊 Percentual:** {percentual:.1f}%")
                
                # Alertas inteligentes (só avisos, não erros)
                if percentual > 80:
                    st.warning(f"🚨 **ATENÇÃO CRÍTICA**: Removendo {percentual:.1f}% do estoque!")
                elif percentual > 50:
                    st.info(f"⚠️ **ATENÇÃO**: Removendo {percentual:.1f}% do estoque")
                elif nova_quantidade < 5:
                    st.info("📉 **AVISO**: Restará menos de 5 unidades no estoque")
            
            # Sistema de confirmação em duas etapas
            st.markdown("---")
            
            # Verificar se é remoção grande (>50% do estoque OU >10 unidades)
            is_remocao_grande = percentual > 50 or quantidade > 10
            
            if is_remocao_grande and quantidade > 0:
                # CONFIRMAÇÃO EM DUAS ETAPAS
                st.warning("⚠️ **Remoção Significativa Detectada**")
                confirmacao_checkbox = st.checkbox(
                    f"✅ Confirmo que desejo remover {quantidade} unidades ({percentual:.1f}% do estoque)",
                    key=f"confirm_{timestamp_key}"
                )
                
                if confirmacao_checkbox:
                    col_btn = st.columns([1, 2, 1])[1]
                    with col_btn:
                        submitted = st.form_submit_button(
                            f"🗑️ CONFIRMAR Remoção de {quantidade} unidade(s)",
                            use_container_width=True,
                            type="primary"
                        )
                else:
                    col_btn = st.columns([1, 2, 1])[1]
                    with col_btn:
                        submitted = st.form_submit_button(
                            f"⚠️ Marque a confirmação acima",
                            use_container_width=True,
                            type="secondary",
                            disabled=True
                        )
            else:
                # Remoção normal
                col_btn = st.columns([1, 2, 1])[1]
                with col_btn:
                    submitted = st.form_submit_button(
                        f"🗑️ Confirmar Remoção de {quantidade} unidade(s)",
                        use_container_width=True,
                        type="primary"
                    )
            
            # VALIDAÇÃO APÓS SUBMIT
            if submitted:
                erros = []
                
                # Validar apenas quando realmente necessário
                if not destino or len(destino.strip()) < 3:
                    erros.append("Destino deve ter pelo menos 3 caracteres")
                
                if quantidade <= 0:
                    erros.append("Quantidade deve ser maior que zero")
                
                # Validação será feita após buscar o equipamento correto da condição selecionada
                
                # Validar se a condição é válida
                if condicao_selecionada not in [CondicionEquipamento.NOVO.value, CondicionEquipamento.USADO.value]:
                    erros.append(f"Condição inválida: {condicao_selecionada}")
                
                # Buscar equipamento específico da condição selecionada
                if codigo_produto:
                    equipamento_condicao = self.estoque_service.obter_equipamento_por_codigo_e_condicao(
                        str(codigo_produto), CondicionEquipamento(condicao_selecionada)
                    )
                    if equipamento_condicao is None:
                        erros.append(f"Não há equipamentos {condicao_selecionada} disponíveis para o código {codigo_produto}")
                    elif equipamento_condicao.get('Quantidade', 0) < quantidade:
                        # Note: banco retorna 'Quantidade' com maiúscula
                        erros.append(f"Quantidade insuficiente. Disponível {condicao_selecionada}: {equipamento_condicao.get('Quantidade', 0)} unidades")
                
                # Mostrar erros APENAS se houver e após tentar submeter
                if erros:
                    st.error("**❌ Corrija os erros abaixo:**")
                    for erro in erros:
                        st.error(f"• {erro}")
                else:
                    # ✅ PROCESSAR REMOÇÃO COM CONFIRMAÇÃO VISUAL
                    st.success(f"✅ **Processando remoção de {quantidade} unidade(s) {condicao_selecionada}...**")
                    
                    # Processar remoção apenas se não houver erros
                    self._processar_remocao_individual(
                        equipamento, quantidade, destino, observacoes, codigo_saida, condicao_selecionada
                    )
    
    def _render_operacoes_lote(self, df_disponivel: pd.DataFrame) -> None:
        """Renderiza operações em lote"""
        st.markdown("### 📦 Operações em Lote - Remover Múltiplos Equipamentos")
        
        if df_disponivel.empty:
            st.warning("❌ Nenhum equipamento disponível para operações em lote")
            return
        
        # Seleção múltipla com data editor
        st.markdown("#### 🎯 Selecione os Equipamentos para Remoção")
        
        # Preparar DataFrame para seleção
        df_selecao = df_disponivel.copy()
        df_selecao['SELECIONAR'] = False
        df_selecao['QTD_REMOVER'] = 1
        df_selecao['DESTINO'] = ""
        df_selecao['OBSERVACOES'] = ""
        
        # Reordenar colunas
        colunas_ordem = ['SELECIONAR', 'codigo_produto', 'equipamento', 'categoria', 
                        'marca', 'quantidade', 'QTD_REMOVER', 'DESTINO', 'OBSERVACOES', 
                        'valor_unitario']
        colunas_existentes = [col for col in colunas_ordem if col in df_selecao.columns]
        df_selecao = df_selecao[colunas_existentes]
        
        # Editor de dados interativo
        df_editado = st.data_editor(
            df_selecao,
            column_config={
                "SELECIONAR": st.column_config.CheckboxColumn(
                    "Selecionar",
                    help="Marque para incluir na remoção em lote",
                    default=False,
                ),
                "QTD_REMOVER": st.column_config.NumberColumn(
                    "Qtd a Remover",
                    help="Quantidade a remover",
                    min_value=1,
                    max_value=None,
                    step=1,
                    format="%d",
                ),
                "DESTINO": st.column_config.TextColumn(
                    "Destino",
                    help="Para onde está sendo enviado",
                    max_chars=100,
                ),
                "OBSERVACOES": st.column_config.TextColumn(
                    "Observações",
                    help="Informações adicionais",
                    max_chars=200,
                ),
                "codigo_produto": "Código",
                "equipamento": "Equipamento",
                "categoria": "Categoria",
                "marca": "Marca",
                "quantidade": "Disponível",
                "valor_unitario": st.column_config.NumberColumn(
                    "Valor Unit.",
                    format="R$ %.2f"
                )
            },
            hide_index=True,
            use_container_width=True,
            key="editor_lote_remover"
        )
        
        # Processar seleções
        selecionados = df_editado[df_editado['SELECIONAR'] == True]
        
        if not selecionados.empty:
            st.markdown("#### 📋 Resumo da Operação em Lote")
            
            # Validações
            erros_lote = []
            for idx, row in selecionados.iterrows():
                if row['QTD_REMOVER'] > row['quantidade']:
                    erros_lote.append(f"• {row['equipamento']}: Quantidade ({row['QTD_REMOVER']}) > Disponível ({row['quantidade']})")
                if not row['DESTINO'] or len(str(row['DESTINO']).strip()) < 3:
                    erros_lote.append(f"• {row['equipamento']}: Destino obrigatório (mín. 3 caracteres)")
            
            if erros_lote:
                st.error("**❌ Erros encontrados:**")
                for erro in erros_lote:
                    st.error(erro)
            else:
                # Mostrar resumo
                total_itens = len(selecionados)
                total_unidades = selecionados['QTD_REMOVER'].sum()
                valor_total = (selecionados['QTD_REMOVER'] * selecionados['valor_unitario']).sum()
                
                col_resumo1, col_resumo2, col_resumo3 = st.columns(3)
                
                with col_resumo1:
                    st.metric("📦 Equipamentos", total_itens)
                with col_resumo2:
                    st.metric("📊 Total Unidades", f"{total_unidades:,}")
                with col_resumo3:
                    st.metric("💰 Valor Total", f"R$ {valor_total:,.2f}")
                
                # Botão de confirmação
                st.markdown("---")
                col_confirmar = st.columns([1, 2, 1])[1]
                with col_confirmar:
                    if st.button(
                        f"🗑️ Confirmar Remoção em Lote ({total_itens} itens)",
                        use_container_width=True,
                        type="primary"
                    ):
                        self._processar_remocao_lote(selecionados)
        else:
            st.info("💡 Marque os equipamentos que deseja remover usando a checkbox 'Selecionar'")
    
    def _render_historico_remocoes(self) -> None:
        """Renderiza histórico de remoções"""
        st.markdown("### 📋 Histórico de Remoções")
        
        # Filtros de período
        col_periodo1, col_periodo2, col_periodo3 = st.columns(3)
        
        with col_periodo1:
            periodo = st.selectbox(
                "📅 Período",
                ["Hoje", "Última Semana", "Último Mês", "Personalizado"],
                key="periodo_historico"
            )
        
        with col_periodo2:
            if periodo == "Personalizado":
                data_inicio = st.date_input("Data Início", key="data_inicio_hist")
        
        with col_periodo3:
            if periodo == "Personalizado":
                data_fim = st.date_input("Data Fim", key="data_fim_hist")
        
        # Simular dados de histórico (substituir por dados reais do banco)
        st.info("📊 Funcionalidade em desenvolvimento - Será integrada com o banco de dados de movimentações")
        
        # Botão de exportar
        if st.button("📥 Exportar Histórico"):
            # Implementar exportação
            st.success("✅ Histórico exportado com sucesso!")
    
    def _render_configuracoes_avancadas(self) -> None:
        """Renderiza configurações avançadas"""
        st.markdown("### ⚙️ Configurações Avançadas")
        
        # Configurações de validação
        st.markdown("#### 🔒 Validações e Segurança")
        
        col_config1, col_config2 = st.columns(2)
        
        with col_config1:
            confirmacao_critica = st.checkbox(
                "Confirmação para remoções críticas (>50% estoque)",
                value=True,
                help="Exigir confirmação extra para remoções que deixem estoque muito baixo"
            )
            
            alerta_estoque_baixo = st.number_input(
                "Alerta de estoque baixo (unidades)",
                min_value=1,
                max_value=50,
                value=5,
                help="Alertar quando estoque ficar abaixo deste valor"
            )
        
        with col_config2:
            limite_lote = st.number_input(
                "Limite de itens por lote",
                min_value=1,
                max_value=100,
                value=20,
                help="Máximo de equipamentos por operação em lote"
            )
            
            auto_export = st.checkbox(
                "Auto-exportar relatórios",
                help="Exportar automaticamente relatórios de remoção"
            )
        
        # Códigos QR (funcionalidade futura)
        st.markdown("#### 📱 Funcionalidades Futuras")
        st.info("🚀 **Em Desenvolvimento:**\n- Códigos QR/Barcode para busca rápida\n- Integração com sistema de rastreamento\n- Aprovação para remoções de alto valor\n- Notificações em tempo real")
    
    def _render_tabela_equipamentos_disponiveis(self, df_disponivel: pd.DataFrame) -> None:
        """Renderiza tabela moderna de equipamentos disponíveis"""
        st.markdown("### 📋 Equipamentos Disponíveis")
        
        if df_disponivel.empty:
            st.warning("❌ Nenhum equipamento encontrado com os filtros aplicados")
            return
        
        # Preparar dados para exibição
        df_display = df_disponivel.copy()
        df_display['valor_total'] = df_display['quantidade'] * df_display['valor_unitario']
        
        # Selecionar colunas para exibição
        colunas_exibicao = ['codigo_produto', 'equipamento', 'categoria', 'marca', 
                          'quantidade', 'condicao', 'valor_unitario', 'valor_total']
        colunas_existentes = [col for col in colunas_exibicao if col in df_display.columns]
        
        # Formatar DataFrame
        df_formatado = format_dataframe_for_display(df_display[colunas_existentes])
        
        # ✅ ADICIONAR INDICADORES VISUAIS SEM ESTILIZAÇÃO PROBLEMÁTICA
        # Adicionar coluna de alertas de estoque
        def criar_alerta_estoque(quantidade):
            if quantidade < 5:
                return "🔴 CRÍTICO"
            elif quantidade < 10:
                return "🟡 BAIXO"
            else:
                return "🟢 OK"
        
        df_formatado.insert(0, '⚠️ Status', df_formatado['quantidade'].apply(criar_alerta_estoque))
        
        # Renderizar tabela simples sem estilização CSS problemática
        st.dataframe(
            df_formatado,
            use_container_width=True,
            hide_index=True,
            column_config={
                "⚠️ Status": st.column_config.TextColumn(
                    "⚠️ Status",
                    help="Indicador visual do nível de estoque",
                    width="small"
                ),
                "quantidade": st.column_config.NumberColumn(
                    "Quantidade",
                    help="Quantidade disponível em estoque",
                    format="%d un."
                ),
                "valor_unitario": st.column_config.NumberColumn(
                    "Valor Unit.",
                    help="Valor unitário do equipamento",
                    format="R$ %.2f"
                ),
                "valor_total": st.column_config.NumberColumn(
                    "Valor Total",
                    help="Valor total (quantidade × valor unitário)",
                    format="R$ %.2f"
                )
            }
        )
        
        # Legenda atualizada e mais clara
        st.markdown("""
        **📊 Legenda de Status:**
        - 🔴 **CRÍTICO** (< 5 unidades) - Estoque muito baixo
        - 🟡 **BAIXO** (5-9 unidades) - Estoque baixo  
        - 🟢 **OK** (≥ 10 unidades) - Estoque adequado
        """)
    
    def _processar_remocao_individual(self, equipamento: pd.Series, quantidade: int,
                                    destino: str, observacoes: str, codigo_saida: str, condicao: str) -> None:
        """Processa remoção individual de equipamento - SEM usar 'id'"""
        try:
            # Extrair dados do equipamento com fallbacks
            codigo_produto = str(equipamento.get('codigo_produto', equipamento.name if hasattr(equipamento, 'name') else 'N/A'))
            nome_equipamento = str(equipamento.get('equipamento', equipamento.get('Nome', 'N/A')))
            quantidade_disp = int(equipamento.get('quantidade', equipamento.get('Quantidade', 0)))
            valor_unit = float(equipamento.get('valor_unitario', equipamento.get('Valor Unitário', 0)))
            
            # Mostrar preview resumido
            st.markdown("### ⏳ **Processando remoção...**")
            valor_total = quantidade * valor_unit
            st.info(f"📦 **{nome_equipamento}** | 📊 {quantidade} un. | 💰 R$ {valor_total:,.2f}")
            
            # Preparar observações completas
            obs_completas = observacoes.strip() if observacoes else ""
            if codigo_saida and codigo_saida.strip():
                if obs_completas:
                    obs_completas += f" | Código: {codigo_saida.strip()}"
                else:
                    obs_completas = f"Código: {codigo_saida.strip()}"
            
            # Converter string para enum com tratamento robusto
            try:
                # Primeiro normalizar a condição
                condicao_normalizada = normalizar_condicao_equipamento(condicao)

                if condicao_normalizada == CondicionEquipamento.NOVO.value:
                    condicao_enum = CondicionEquipamento.NOVO
                elif condicao_normalizada == CondicionEquipamento.USADO.value:
                    condicao_enum = CondicionEquipamento.USADO
                else:
                    # Fallback para NOVO se não conseguir determinar
                    st.warning(f"⚠️ Condição '{condicao}' não reconhecida, usando NOVO como padrão")
                    condicao_enum = CondicionEquipamento.NOVO

            except Exception as e:
                st.error(f"❌ Erro na conversão de condição: {condicao} → {str(e)}")
                st.stop()
            
            # Processar remoção - usar APENAS codigo_produto e condicao
            response = self.estoque_service.remover_equipamento(
                codigo_produto, quantidade, destino.strip(), obs_completas, condicao=condicao_enum
            )
            
            if response.success:
                # ✅ SUCESSO - Mostrar detalhes completos
                valor_removido = quantidade * valor_unit
                nova_quantidade = quantidade_disp - quantidade
                
                # Sucesso - Interface limpa e profissional
                st.balloons()  # Animação de celebração
                
                # ✅ MENSAGEM FINAL DE SUCESSO
                show_success_message(
                    f"✅ **Equipamento removido com sucesso!**\n\n"
                    f"**📦 Equipamento:** {nome_equipamento}\n"
                    f"**🏷️ Código:** {codigo_produto}\n"
                    f"**🔄 Condição:** {condicao}\n"
                    f"**📊 Quantidade:** {quantidade} unidades\n"
                    f"**💰 Valor:** R$ {valor_removido:,.2f}\n"
                    f"**📈 Novo estoque:** {nova_quantidade} unidades\n"
                    f"**📍 Destino:** {destino}"
                )
                show_toast("🗑️ Equipamento removido!", "✅")
                
                # Invalidar caches
                st.session_state['historico_cache_invalidated'] = True
                st.session_state['cache_remover_invalidated'] = True
                st.session_state['cache_invalidated'] = True
                
                if hasattr(st, 'cache_data'):
                    st.cache_data.clear()
                
                logger.info(f"✅ Remoção bem-sucedida: {quantidade} un. de {nome_equipamento}")
                
                # Recarregar página
                import time
                time.sleep(1.5)
                st.rerun()
                
            else:
                st.error(f"❌ **Erro na remoção:** {response.message}")
                show_error_message(f"❌ Erro: {response.message}")
                
        except Exception as e:
            logger.error(f"Erro ao processar remoção individual: {str(e)}")
            st.error(f"❌ **Erro interno:** {str(e)}")
            show_error_message(f"❌ Erro interno: {str(e)}")
    
    def _processar_remocao_lote(self, selecionados: pd.DataFrame) -> None:
        """Processa remoção em lote"""
        try:
            sucesso_count = 0
            erro_count = 0
            detalhes_operacao = []
            
            for _, row in selecionados.iterrows():
                try:
                    obs_lote = f"Operação em lote | {row.get('OBSERVACOES', '')}"
                    
                    # Usar codigo_produto em vez de id
                    codigo_lote = row.get('codigo_produto', 'N/A')
                    response = self.estoque_service.remover_equipamento(
                        codigo_lote, 
                        int(row['QTD_REMOVER']), 
                        str(row['DESTINO']).strip(), 
                        obs_lote
                    )
                    
                    if response.success:
                        sucesso_count += 1
                        valor_item = row['QTD_REMOVER'] * row['valor_unitario']
                        detalhes_operacao.append(
                            f"✅ {row['equipamento']}: {row['QTD_REMOVER']} un. → R$ {valor_item:,.2f}"
                        )
                    else:
                        erro_count += 1
                        detalhes_operacao.append(
                            f"❌ {row['equipamento']}: {response.message}"
                        )
                        
                except Exception as e:
                    erro_count += 1
                    detalhes_operacao.append(
                        f"❌ {row['equipamento']}: Erro interno - {str(e)}"
                    )
            
            # Mostrar resultado da operação
            total_operacoes = len(selecionados)
            
            if sucesso_count == total_operacoes:
                show_success_message(
                    f"🎉 **Operação em lote concluída com sucesso!**\n\n"
                    f"**📦 Equipamentos processados:** {total_operacoes}\n"
                    f"**✅ Sucessos:** {sucesso_count}\n"
                    f"**❌ Erros:** {erro_count}"
                )
                show_toast("📦 Lote removido com sucesso!", "🎉")
            else:
                show_warning_message(
                    f"⚠️ **Operação em lote parcialmente concluída**\n\n"
                    f"**📦 Total:** {total_operacoes}\n"
                    f"**✅ Sucessos:** {sucesso_count}\n"
                    f"**❌ Erros:** {erro_count}"
                )
            
            # Mostrar detalhes se solicitado
            with st.expander("📋 Ver Detalhes da Operação"):
                for detalhe in detalhes_operacao:
                    st.markdown(f"• {detalhe}")
            
            # ✅ INVALIDAR CACHE DO HISTÓRICO AUTOMATICAMENTE SE HOUVE SUCESSOS
            if sucesso_count > 0:
                st.session_state['historico_cache_invalidated'] = True
                logger.info(f"🔄 Cache de histórico invalidado após {sucesso_count} remoções em lote")
            
            # Invalidar cache e recarregar
            st.session_state['cache_remover_invalidated'] = True
            if hasattr(st, 'cache_data'):
                st.cache_data.clear()
            st.rerun()
            
        except Exception as e:
            logger.error(f"Erro ao processar remoção em lote: {str(e)}")
            show_error_message(f"❌ Erro interno na operação em lote: {str(e)}")

def render_remover_page(estoque_service: EstoqueService) -> None:
    """Função para renderizar a página profissional de remover equipamentos"""
    page = RemoverEquipamentoPageProfessional(estoque_service)
    page.render() 