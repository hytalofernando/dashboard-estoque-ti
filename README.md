# 📊 Dashboard Estoque TI

Um dashboard completo para gerenciamento de estoque de equipamentos de TI, desenvolvido com Streamlit e integração com Excel.

## 🚀 Funcionalidades

### 📈 Dashboard Principal
- **Métricas em Tempo Real**: Total de equipamentos, valor do estoque, categorias e disponibilidade
- **Gráficos Interativos**: 
  - Distribuição por categoria (pizza)
  - Quantidade por marca (barras)
  - Equipamentos recebidos por mês (linha temporal)
  - Valor por categoria (treemap)
- **Tabela de Estoque**: Visualização completa dos equipamentos

### ➕ Adicionar Equipamentos
- Formulário completo para adição de novos equipamentos
- Validação de dados obrigatórios
- Registro automático de movimentação de entrada
- Categorização automática

### ➖ Remover Equipamentos
- Seleção de equipamentos disponíveis
- Controle de quantidade
- Registro de destino e observações
- Atualização automática do status

### 📋 Histórico de Movimentações
- Filtros por tipo de movimentação
- Filtros por período
- Gráfico de movimentações
- Tabela detalhada com informações completas

### 🌙 Modo Escuro
- **Interface Escura**: Design moderno com tema escuro por padrão
- **Cores Otimizadas**: Contraste perfeito para melhor legibilidade
- **Gráficos Adaptados**: Temas do Plotly otimizados para modo escuro
- **Experiência Consistente**: Interface uniforme em todas as páginas

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Interface web interativa
- **Pandas**: Manipulação e análise de dados
- **Plotly**: Gráficos interativos e avançados
- **OpenPyXL**: Integração com arquivos Excel
- **Requests**: Requisições HTTP (para futuras integrações)
- **BeautifulSoup4**: Web scraping (para futuras funcionalidades)

## 📁 Estrutura do Projeto

```
dashboard/
├── app.py              # Aplicação principal
├── utils.py            # Funções utilitárias
├── requirements.txt    # Dependências
├── README.md          # Documentação
├── run_dashboard.bat  # Script de execução (Windows)
└── estoque_ti.xlsx    # Banco de dados (criado automaticamente)
```

## 🗄️ Estrutura do Banco de Dados

### Tabela: Estoque
- `id`: Identificador único
- `equipamento`: Nome do equipamento
- `categoria`: Categoria (Notebook, Monitor, etc.)
- `marca`: Marca do equipamento
- `modelo`: Modelo específico
- `quantidade`: Quantidade em estoque
- `valor_unitario`: Valor unitário
- `data_chegada`: Data de chegada
- `fornecedor`: Fornecedor
- `status`: Status (Disponível/Indisponível)

### Tabela: Movimentacoes
- `id`: Identificador único
- `equipamento_id`: ID do equipamento
- `tipo_movimentacao`: Entrada ou Saída
- `quantidade`: Quantidade movimentada
- `data_movimentacao`: Data da movimentação
- `destino_origem`: Destino (saída) ou Origem (entrada)
- `observacoes`: Observações adicionais

## 🚀 Como Executar

1. **Instalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Executar o dashboard**:
   ```bash
   streamlit run app.py
   ```
   Ou clique duas vezes no arquivo `run_dashboard.bat`

3. **Acessar no navegador**:
   ```
   http://localhost:8501
   ```

## 🌙 Design Modo Escuro

### Características do Tema Escuro
- **Fundo Principal**: #0e1117 (azul muito escuro)
- **Sidebar**: #262730 (cinza escuro)
- **Texto**: #fafafa (branco suave)
- **Destaque**: #00d4ff (azul ciano)
- **Bordas**: #404040 (cinza médio)

### Benefícios do Modo Escuro
- **Redução da Fadiga Visual**: Menos cansaço nos olhos
- **Melhor Contraste**: Texto mais legível
- **Design Moderno**: Interface contemporânea
- **Economia de Energia**: Menor consumo em telas OLED/AMOLED
- **Experiência Profissional**: Aparência mais sofisticada

## 📊 Funcionalidades Avançadas

### Análises Visuais
- **Gráfico de Pizza**: Distribuição por categoria
- **Gráfico de Barras**: Quantidade por marca
- **Gráfico Temporal**: Equipamentos recebidos por mês
- **Treemap**: Valor total por categoria
- **Gráfico de Movimentações**: Entradas vs Saídas

### Controle de Estoque
- **Adição Automática**: Registro de entrada com data e fornecedor
- **Remoção Controlada**: Validação de quantidade disponível
- **Rastreamento**: Histórico completo de movimentações
- **Status Automático**: Atualização baseada na quantidade

### Filtros e Relatórios
- **Filtros Temporais**: Por período específico
- **Filtros por Tipo**: Entradas ou saídas
- **Relatórios**: Métricas em tempo real
- **Exportação**: Dados salvos em Excel

## 🔧 Configurações

### Personalização de Categorias
As categorias podem ser facilmente modificadas no código:
```python
categoria = st.selectbox("Categoria", [
    "Notebook", "Monitor", "Impressora", "Rede", 
    "Servidor", "Periférico", "Outro"
])
```

### Estilo Visual
O dashboard utiliza CSS customizado para melhor apresentação:
- **Tema Escuro Fixo**: Interface consistente e moderna
- **Cards de Métricas**: Design elegante com bordas coloridas
- **Mensagens**: Sucesso, aviso e erro com cores distintas
- **Layout Responsivo**: Adaptação para diferentes tamanhos de tela
- **Scrollbar Customizada**: Estilo escuro para navegadores WebKit

## 📈 Escalabilidade

### Arquitetura Modular
- **Separação de Responsabilidades**: Lógica de negócio separada da interface
- **Funções Utilitárias**: Código reutilizável em `utils.py`
- **Classe EstoqueTI**: Encapsulamento da lógica de estoque
- **Design System**: Base sólida para futuras expansões

### Manutenibilidade
- **Código Documentado**: Funções com docstrings completas
- **Validações**: Verificações de dados em todas as operações
- **Tratamento de Erros**: Mensagens informativas para o usuário
- **CSS Modular**: Estilos organizados por funcionalidade
- **Estrutura Clara**: Organização lógica dos arquivos

### Escalabilidade
- **Banco de Dados Flexível**: Estrutura Excel que pode ser facilmente migrada para SQL
- **Funções Modulares**: Fácil adição de novas funcionalidades
- **Configurações Centralizadas**: Fácil personalização de categorias e estilos
- **Design Consistente**: Base sólida para adição de novos recursos

## 🔮 Próximas Funcionalidades

- [ ] **Alertas de Estoque Baixo**: Notificações automáticas
- [ ] **Relatórios em PDF**: Exportação de relatórios
- [ ] **Integração com APIs**: Conexão com sistemas externos
- [ ] **Backup Automático**: Salvamento em nuvem
- [ ] **Múltiplos Usuários**: Sistema de login
- [ ] **Dashboard Mobile**: Interface responsiva
- [ ] **Temas Personalizados**: Opções adicionais de cores
- [ ] **Modo Automático**: Detecção automática do tema do sistema

## 🤝 Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Implemente as mudanças
4. Teste as funcionalidades
5. Envie um pull request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Suporte

Para dúvidas ou sugestões, abra uma issue no repositório ou entre em contato através do email.

---

**Desenvolvido com ❤️ para otimizar o gerenciamento de estoque de TI** 