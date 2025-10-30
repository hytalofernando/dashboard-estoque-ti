# 🐘 Setup PostgreSQL - Dashboard Estoque TI

## 📋 Índice
1. [Por que PostgreSQL?](#-por-que-postgresql)
2. [Instalação Local (Desenvolvimento)](#-instalação-local-desenvolvimento)
3. [Migração dos Dados](#-migração-dos-dados)
4. [Configuração no Streamlit Cloud](#-configuração-no-streamlit-cloud)
5. [Testando a Conexão](#-testando-a-conexão)
6. [Troubleshooting](#-troubleshooting)

---

## 🎯 Por que PostgreSQL?

### ✅ **Vantagens sobre Excel:**

| Excel | PostgreSQL |
|-------|------------|
| ❌ Dados perdidos no restart | ✅ Dados persistentes |
| ❌ Sem controle de concorrência | ✅ Múltiplos acessos simultâneos |
| ❌ Sem transações | ✅ ACID compliant |
| ❌ Performance limitada | ✅ Otimizado para grandes volumes |
| ❌ Sem backup automático | ✅ Backup e recovery |

---

## 💻 Instalação Local (Desenvolvimento)

### **Opção 1: SQLite (Mais Simples para Desenvolvimento)**

SQLite não requer instalação! O sistema já está configurado para usar SQLite automaticamente se o PostgreSQL não estiver disponível.

**No arquivo `.env`:**
```env
# Comentar ou remover DATABASE_URL para usar SQLite
# DATABASE_URL=postgresql://...
```

O sistema criará automaticamente o arquivo `estoque_ti.db` na raiz do projeto.

### **Opção 2: PostgreSQL Local (Recomendado para Produção)**

#### **Windows:**

1. **Baixar PostgreSQL:**
   - Acesse: https://www.postgresql.org/download/windows/
   - Baixe o instalador
   - Execute e siga o wizard

2. **Durante a instalação:**
   - Defina senha para usuário `postgres`
   - Porta padrão: `5432`
   - Anote a senha!

3. **Criar Banco de Dados:**
```bash
# Abrir psql (PostgreSQL Shell)
psql -U postgres

# Criar banco
CREATE DATABASE estoque_ti;

# Criar usuário (opcional)
CREATE USER estoque_admin WITH PASSWORD 'sua_senha_segura';
GRANT ALL PRIVILEGES ON DATABASE estoque_ti TO estoque_admin;

# Sair
\q
```

4. **Configurar `.env`:**
```env
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/estoque_ti
```

#### **Linux/Mac:**

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Mac (com Homebrew)
brew install postgresql@15
brew services start postgresql@15

# Criar banco
sudo -u postgres psql
CREATE DATABASE estoque_ti;
\q
```

**Configurar `.env`:**
```env
DATABASE_URL=postgresql://postgres:SUA_SENHA@localhost:5432/estoque_ti
```

---

## 🔄 Migração dos Dados

### **Passo 1: Fazer Backup do Excel**

```bash
# Copiar arquivo Excel para backup
copy estoque_ti.xlsx estoque_ti_backup_2024.xlsx
```

### **Passo 2: Executar Script de Migração**

O projeto inclui um script automático de migração:

```bash
# Ativar ambiente virtual
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Executar migração
python migrate_excel_to_postgres.py
```

**Opções do migrador:**
1. **Opção 1** - Migrar SEM limpar banco (adiciona/atualiza)
2. **Opção 2** - Migrar E LIMPAR banco antes (**APAGA tudo e recria**)

### **Passo 3: Verificar Migração**

O script mostrará:
- ✅ Número de equipamentos migrados
- ✅ Número de movimentações migradas
- ✅ Estatísticas do banco
- ⚠️ Erros encontrados (se houver)

**Exemplo de saída:**
```
✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!
====================
📊 ESTATÍSTICAS DO BANCO:
   📦 Total de equipamentos: 150
   💰 Valor total do estoque: R$ 125,450.00
   
   📂 Por Categoria:
      • Notebook: 45
      • Monitor: 32
      • Impressora: 23
      ...
```

---

## ☁️ Configuração no Streamlit Cloud

### **Passo 1: Adicionar PostgreSQL no Streamlit Cloud**

1. Acesse seu app no **Streamlit Cloud**
2. Vá em **Settings** → **Data sources**
3. Clique em **Connect to PostgreSQL**
4. Streamlit criará um banco PostgreSQL **GRATUITO** para você!
5. Copie a `DATABASE_URL` fornecida

### **Passo 2: Configurar Secrets**

No painel do Streamlit Cloud:

1. Vá em **Settings** → **Secrets**
2. Adicione:

```toml
# === BANCO DE DADOS ===
DATABASE_URL = "postgresql://user:password@host:5432/database"

# === AUTENTICAÇÃO ===
ADMIN_PASSWORD = "SuaSenhaAdmin@2024!"
VIEWER_PASSWORD = "SuaSenhaVisualizador#2024"

# === SEGURANÇA ===
SECRET_KEY = "sua-chave-de-32-caracteres"
JWT_SECRET = "sua-outra-chave-de-32-caracteres"

# === CONFIGURAÇÕES ===
ENVIRONMENT = "production"
DEBUG = "false"
LOG_LEVEL = "INFO"
MAX_REQUESTS_PER_MINUTE = "30"
MAX_LOGIN_ATTEMPTS = "5"
CACHE_TTL_SECONDS = "300"
ENABLE_CACHE = "true"
```

3. Clique em **Save**

### **Passo 3: Migrar Dados para o Cloud**

**Opção A: Executar migração local apontando para cloud**

1. Configure `.env` local com DATABASE_URL do cloud
2. Execute `python migrate_excel_to_postgres.py`
3. Dados serão enviados para o PostgreSQL do Streamlit Cloud

**Opção B: Migrar via interface web (futuro)**

Estamos desenvolvendo uma interface web para upload dos dados.

---

## 🧪 Testando a Conexão

### **Script de Teste:**

Crie um arquivo `test_database.py`:

```python
from services.database_service import DatabaseService

def test_connection():
    try:
        db = DatabaseService()
        stats = db.obter_estatisticas()
        
        print("✅ Conexão bem-sucedida!")
        print(f"📦 Total de equipamentos: {stats['total_equipamentos']}")
        print(f"💰 Valor total: R$ {stats['valor_total']:,.2f}")
        
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")

if __name__ == "__main__":
    test_connection()
```

Execute:
```bash
python test_database.py
```

---

## 🔧 Troubleshooting

### **Erro: "could not connect to server"**

**Causa:** PostgreSQL não está rodando ou configuração incorreta

**Solução:**
```bash
# Windows - Verificar serviço
services.msc
# Procurar por "postgresql" e iniciar

# Linux
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### **Erro: "password authentication failed"**

**Causa:** Senha incorreta no DATABASE_URL

**Solução:**
- Verifique a senha no `.env`
- Formato correto: `postgresql://USER:SENHA@HOST:5432/DATABASE`
- Caracteres especiais na senha devem ser URL-encoded

### **Erro: "relation does not exist"**

**Causa:** Tabelas não foram criadas

**Solução:**
```python
# Executar para criar tabelas
from models.database_models import Base, db_connection
Base.metadata.create_all(db_connection.get_engine())
```

### **Erro: "too many connections"**

**Causa:** Limite de conexões atingido

**Solução:**
- Reinicie o app no Streamlit Cloud
- No PostgreSQL local, aumente `max_connections` no `postgresql.conf`

### **Dados não aparecem após migração**

**Verificar:**
1. Execute o teste de conexão
2. Verifique os logs: `logs/dashboard.log`
3. Confirme que DATABASE_URL está configurado
4. Verifique se as tabelas foram criadas:
   ```sql
   psql -U postgres -d estoque_ti
   \dt
   SELECT COUNT(*) FROM equipamentos;
   SELECT COUNT(*) FROM movimentacoes;
   ```

---

## 📊 Comandos Úteis PostgreSQL

### **Conectar ao banco:**
```bash
psql -U postgres -d estoque_ti
```

### **Comandos SQL:**
```sql
-- Ver todas as tabelas
\dt

-- Ver estrutura de tabela
\d equipamentos

-- Contar registros
SELECT COUNT(*) FROM equipamentos;
SELECT COUNT(*) FROM movimentacoes;

-- Ver últimos equipamentos
SELECT codigo, nome, quantidade, condicao 
FROM equipamentos 
ORDER BY data_cadastro DESC 
LIMIT 10;

-- Ver últimas movimentações
SELECT tipo, codigo, quantidade, data_movimentacao 
FROM movimentacoes 
ORDER BY data_movimentacao DESC 
LIMIT 10;

-- Estatísticas por categoria
SELECT categoria, COUNT(*), SUM(quantidade) 
FROM equipamentos 
WHERE ativo = true 
GROUP BY categoria;
```

### **Backup e Restore:**
```bash
# Fazer backup
pg_dump -U postgres estoque_ti > backup_estoque_ti.sql

# Restaurar backup
psql -U postgres estoque_ti < backup_estoque_ti.sql
```

---

## 🎯 Checklist de Migração

Antes de fazer deploy com PostgreSQL:

- [ ] PostgreSQL instalado (local) ou configurado (cloud)
- [ ] Banco de dados criado
- [ ] DATABASE_URL configurado no `.env` ou `secrets`
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Backup do Excel feito
- [ ] Script de migração executado com sucesso
- [ ] Teste de conexão bem-sucedido
- [ ] Dados verificados no banco
- [ ] App testado localmente com PostgreSQL
- [ ] Secrets configurados no Streamlit Cloud
- [ ] Deploy realizado e testado

---

## 💡 Dicas de Produção

### **1. Monitoramento**
- Use logs para acompanhar queries
- Configure alertas para erros de conexão
- Monitore uso de conexões

### **2. Performance**
- Cache de queries habilitado (5 minutos)
- Índices já criados nas colunas principais
- Pool de conexões configurado

### **3. Segurança**
- Nunca commite DATABASE_URL
- Use senhas fortes
- SSL habilitado em produção (automático no Streamlit Cloud)

### **4. Backup**
- Streamlit Cloud faz backup automático
- Para local, configure backup diário:
  ```bash
  # Cron job (Linux)
  0 2 * * * pg_dump -U postgres estoque_ti > /backups/estoque_$(date +\%Y\%m\%d).sql
  ```

---

## 📚 Recursos Adicionais

- **PostgreSQL Docs:** https://www.postgresql.org/docs/
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org/
- **Streamlit Databases:** https://docs.streamlit.io/knowledge-base/tutorials/databases

---

**✅ Pronto! Seu sistema agora usa PostgreSQL e os dados estão seguros! 🎉**

