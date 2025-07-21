# 💻 Dashboard Estoque TI - Versão 2.0 Modernizada

Sistema moderno de gerenciamento de estoque de equipamentos de TI desenvolvido com tecnologias atuais.

## 🚀 **Tecnologias Modernizadas**

- **Streamlit 1.47+** - Interface moderna com novos recursos
- **Plotly 5.21+** - Gráficos com bordas arredondadas e melhor performance
- **Pandas 2.2+** - Análise de dados otimizada
- **Pydantic 2.5+** - Validação robusta de dados
- **Loguru 0.7+** - Sistema de logs estruturado

## ✨ **Novos Recursos da v2.0**

### **Interface Modernizada**
- 🎨 Design responsivo com CSS moderno
- 🌙 Tema escuro otimizado
- 🔧 Navegação intuitiva
- 📱 Interface adaptável
- 🎯 Toast notifications modernas

### **Arquitetura Escalável**
- 📁 Estrutura modular bem organizada
- 🔧 Configurações centralizadas
- 📊 Validação de dados com Pydantic
- 🔍 Logs estruturados com Loguru
- 🧪 Separação clara de responsabilidades

### **Funcionalidades Avançadas**
- 🏷️ Sistema de códigos de produtos automático
- 📈 Gráficos interativos modernos
- 📋 Histórico completo de movimentações
- ⚠️ Alertas inteligentes de baixo estoque
- 🔍 Busca e filtros avançados

## 📁 **Estrutura do Projeto**

```
dashboard/
├── app.py                      # Aplicação principal modernizada
├── requirements.txt            # Dependências atualizadas
├── config/
│   ├── __init__.py
│   └── settings.py            # Configurações centralizadas
├── models/
│   ├── __init__.py
│   └── schemas.py             # Modelos de dados com Pydantic
├── services/
│   ├── __init__.py
│   ├── excel_service.py       # Serviço para operações Excel
│   ├── estoque_service.py     # Lógica principal do estoque
│   └── movimentacao_service.py # Gerenciamento de movimentações
├── utils/
│   ├── __init__.py
│   ├── plotly_utils.py        # Utilitários para gráficos modernos
│   └── ui_utils.py            # Utilitários para interface
├── pages/
│   ├── __init__.py
│   ├── dashboard_page.py      # Página principal
│   ├── adicionar_page.py      # Adicionar equipamentos
│   ├── remover_page.py        # Remover equipamentos
│   ├── historico_page.py      # Histórico de movimentações
│   └── codigos_page.py        # Gerenciamento de códigos
└── logs/                      # Logs estruturados (criado automaticamente)
```

## 🛠️ **Instalação e Execução**

### **Pré-requisitos**
- Python 3.8+
- pip

### **Instalação**
1. Clone ou baixe o projeto
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

### **Execução**
```bash
streamlit run app.py
```

Ou use o arquivo batch (Windows):
```bash
run_dashboard.bat
```

## 📊 **Funcionalidades**

### **1. Dashboard Principal**
- 📈 Métricas em tempo real
- 📊 Gráficos interativos modernos
- 🔔 Alertas de baixo estoque
- 📋 Visão geral do inventário

### **2. Gerenciamento de Equipamentos**
- ➕ Adicionar novos equipamentos
- 📈 Aumentar estoque existente
- ➖ Remover equipamentos
- 🏷️ Códigos automáticos por categoria

### **3. Histórico de Movimentações**
- 📋 Registro completo de entradas/saídas
- 🔍 Filtros avançados por período
- 📊 Análises visuais das movimentações
- 📈 Gráficos temporais

### **4. Sistema de Códigos**
- 🏷️ Geração automática de códigos
- 🔍 Busca inteligente
- 📊 Análise de padrões
- ✅ Validação de unicidade

## 🎨 **Recursos Visuais Modernos**

### **Gráficos Plotly 5.21+**
- 🔵 Bordas arredondadas nos gráficos
- 🎨 Paleta de cores moderna
- 📱 Responsividade aprimorada
- ⚡ Performance otimizada

### **Interface Streamlit 1.47+**
- 🔔 Toast notifications
- 📱 Componentes modernos
- 🎯 Navegação aprimorada
- 📊 Tabelas interativas

## ⚙️ **Configurações**

As configurações estão centralizadas em `config/settings.py`:
- 📁 Arquivo Excel customizável
- 🏷️ Prefixos de códigos por categoria
- 📊 Limites de validação
- 🎨 Cores do tema

## 📝 **Logs e Monitoramento**

Sistema de logs estruturado com Loguru:
- 📁 Logs salvos em `logs/dashboard.log`
- 🔄 Rotação automática semanal
- 📊 Diferentes níveis de log
- 🔍 Fácil debugging

## 🔒 **Validação de Dados**

Validação robusta com Pydantic:
- ✅ Validação de tipos
- 📏 Limites de valores
- 🔤 Formatação automática
- ❌ Mensagens de erro claras

## 📋 **Melhorias v2.0**

### **Performance**
- ⚡ Código otimizado
- 📊 Carregamento mais rápido
- 🔄 Recarregamento inteligente

### **Escalabilidade**
- 📁 Arquitetura modular
- 🔧 Fácil manutenção
- 📈 Preparado para crescimento

### **Usabilidade**
- 🎨 Interface moderna
- 📱 Design responsivo
- 🔔 Feedback visual

## 🐛 **Solução de Problemas**

### **Problemas Comuns**
1. **Erro de importação**: Certifique-se que todas as dependências estão instaladas
2. **Arquivo Excel não encontrado**: O sistema criará automaticamente na primeira execução
3. **Erro de permissão**: Execute como administrador se necessário

### **Logs**
Verifique os logs em `logs/dashboard.log` para diagnóstico detalhado.

## 🤝 **Contribuição**

Para contribuir com o projeto:
1. Mantenha a estrutura modular
2. Use os padrões de validação Pydantic
3. Inclua logs apropriados
4. Teste todas as funcionalidades

## 📄 **Licença**

Este projeto está licenciado sob a MIT License.

---

**Dashboard Estoque TI v2.0** - Sistema moderno e escalável para gerenciamento de estoque de equipamentos de TI.

**Desenvolvido com ❤️ e tecnologias modernas** 