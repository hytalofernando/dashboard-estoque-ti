# 💻 Dashboard Estoque TI - v2.1 Security Enhanced

Sistema moderno e seguro de gerenciamento de estoque de equipamentos de TI desenvolvido com tecnologias atuais e foco em segurança enterprise.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.42%2B-red.svg)](https://streamlit.io/)
[![Security](https://img.shields.io/badge/Security-Enterprise%20Ready-green.svg)](#-segurança)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🚀 **Tecnologias Modernizadas**

- **Streamlit 1.47+** - Interface moderna com novos recursos
- **Plotly 5.21+** - Gráficos com bordas arredondadas e melhor performance
- **Pandas 2.2+** - Análise de dados otimizada
- **Pydantic 2.5+** - Validação robusta de dados
- **Loguru 0.7+** - Sistema de logs estruturado
- **Bcrypt 4.0+** - Criptografia segura de senhas
- **SQLAlchemy 2.0+** - ORM preparado para migração de banco

## ✨ **Novos Recursos da v2.1**

### **🔒 Segurança Enterprise**
- 🔐 **Autenticação bcrypt** - Senhas criptografadas com salt
- 🚦 **Rate limiting** - Proteção contra força bruta (5 tentativas/15min)
- 🛡️ **Sanitização de inputs** - Prevenção XSS e injection
- 📊 **Logs de auditoria** - Monitoramento completo de acessos
- 🔑 **Controle de permissões** - Admin vs Visualizador
- 🌍 **Variáveis de ambiente** - Configuração segura

### **⚡ Performance Otimizada**
- 🗄️ **Cache inteligente** - TTL automático (5 minutos)
- 📈 **Estatísticas de cache** - Hit rate e métricas
- 🔄 **Invalidação seletiva** - Cache por padrão
- ⚡ **Operações em memória** - DataFrames otimizados

### **🎨 Interface Profissional**
- 🎨 Design system moderno com paleta corporativa
- 🌙 Tema escuro otimizado (#0066FF como primária)
- 🔧 Navegação intuitiva baseada em permissões
- 📱 Interface adaptável e responsiva
- 🎯 Toast notifications modernas

### **🏗️ Arquitetura Robusta**
- 📁 Estrutura modular bem organizada
- 🔧 Configurações centralizadas
- 📊 Validação de dados com Pydantic 2.x
- 🔍 Logs estruturados com Loguru
- 🧪 Separação clara de responsabilidades

### **🚀 Funcionalidades Avançadas**
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
- Git (para clonagem)

### **Instalação**
1. **Clone o repositório:**
```bash
git clone https://github.com/seu-usuario/dashboard-estoque-ti.git
cd dashboard-estoque-ti
```

2. **Crie ambiente virtual:**
```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

3. **Instale dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure variáveis de ambiente:**
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite .env e configure suas senhas seguras
# IMPORTANTE: Altere as senhas padrão!
```

### **Execução**
```bash
streamlit run app.py
```

Ou use o arquivo batch (Windows):
```bash
run_dashboard.bat
```

### **🔐 Primeiro Acesso**
Entre em contato com o administrador do sistema para obter credenciais de acesso. O sistema possui dois perfis:
- 👑 **Administrador** - Acesso completo
- 👀 **Visualizador** - Somente leitura

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

## 🔒 **Segurança**

### **🛡️ Recursos de Segurança Implementados:**
- 🔐 **Autenticação bcrypt** - Senhas criptografadas com salt
- 🚦 **Rate limiting** - Proteção contra ataques de força bruta
- 🧹 **Sanitização de inputs** - Prevenção XSS e injection attacks
- 📊 **Logs de auditoria** - Monitoramento completo de acessos
- 🔑 **Controle granular** - Permissões por perfil de usuário
- 🌍 **Configuração segura** - Variáveis de ambiente para dados sensíveis

### **🔐 Sistema de Autenticação:**
- **Dois perfis** de usuário com permissões diferenciadas
- **Bloqueio automático** após tentativas excessivas
- **Logs de auditoria** para todas as tentativas de acesso
- **Senhas seguras** configuradas via arquivo .env

### **🛡️ Validação de Dados:**
Validação robusta com Pydantic + Sanitização:
- ✅ Validação de tipos e formatos
- 🧹 Sanitização automática de inputs
- 📏 Limites de valores seguros
- 🔤 Formatação e escape automático
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