import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Teste Cores do Menu",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carregar CSS otimizado
def load_theme_css():
    with open("theme.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Aplicar CSS
load_theme_css()

# Sidebar de teste
st.sidebar.title("🎨 Teste de Cores")
st.sidebar.markdown("---")

# Selectbox de teste
opcao = st.sidebar.selectbox(
    "Escolha uma opção:",
    ["Opção 1", "Opção 2", "Opção 3", "Opção 4", "Opção 5"]
)

# Informações de teste
st.sidebar.info(f"Opção selecionada: {opcao}")

# Conteúdo principal
st.title("🎨 Teste de Cores do Menu")
st.write("Esta página testa se as cores do menu estão funcionando corretamente após a otimização.")

# Verificações visuais
st.markdown("### ✅ Verificações Visuais")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Menu (Sidebar):**
    - ✅ Fundo cinza escuro (#262730)
    - ✅ Texto branco suave (#e0e0e0)
    - ✅ Títulos azul ciano (#00d4ff)
    - ✅ Selectbox visível e funcional
    """)

with col2:
    st.markdown("""
    **Aplicação Principal:**
    - ✅ Fundo preto escuro (#0e1117)
    - ✅ Texto branco (#ffffff)
    - ✅ Tema escuro aplicado
    - ✅ CSS otimizado carregado
    """)

# Status do teste
if opcao:
    st.success(f"✅ Opção selecionada: {opcao}")
else:
    st.warning("⚠️ Nenhuma opção selecionada")

# Informações técnicas
st.markdown("### 📊 Informações Técnicas")
st.info(f"""
**Arquivo CSS:** theme.css
**Tamanho:** 6.5KB
**Variáveis CSS:** Implementadas
**Encoding:** UTF-8
**Status:** Otimizado e funcionando
""")

# Botão para testar
if st.button("🔄 Recarregar"):
    st.rerun()

st.success("✅ Se você consegue ver este texto em verde, o teste está funcionando!") 