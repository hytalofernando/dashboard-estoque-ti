# 🚀 Migração Rápida: Excel → PostgreSQL

## ⏱️ 10 Minutos para Migrar!

### **Passo 1: Instalar Dependências** (2 min)

```bash
pip install -r requirements.txt
```

### **Passo 2: Configurar Banco** (3 min)

**Opção A: SQLite (Mais Rápido - Desenvolvimento)**
```bash
# Nada a fazer! Já funciona automaticamente
# O sistema criará estoque_ti.db automaticamente
```

**Opção B: PostgreSQL (Produção)**
```bash
# Criar banco no PostgreSQL
psql -U postgres
CREATE DATABASE estoque_ti;
\q

# Configurar .env
echo "DATABASE_URL=postgresql://postgres:SENHA@localhost:5432/estoque_ti" > .env
```

### **Passo 3: Migrar Dados** (3 min)

```bash
python migrate_excel_to_postgres.py
```

Escolha opção **1** (migrar sem limpar)

### **Passo 4: Ativar PostgreSQL no App** (2 min)

Edite `app.py` e substitua a importação:

```python
# ANTES (Excel):
from services.estoque_service import EstoqueService

# DEPOIS (PostgreSQL):
from services.estoque_service_postgres import EstoqueService
```

### **Passo 5: Testar!**

```bash
streamlit run app.py
```

---

## ✅ Pronto!

Seus dados agora estão no PostgreSQL e não serão mais perdidos! 🎉

---

## 📊 Para Deploy no Streamlit Cloud:

1. **Settings** → **Data sources** → **Connect to PostgreSQL**
2. Copie a `DATABASE_URL`
3. **Settings** → **Secrets** → Cole:
   ```toml
   DATABASE_URL = "postgresql://..."
   ```
4. O resto dos secrets (senhas, etc) também
5. **Salvar** e aguardar restart

**DONE!** ✨

---

## 🆘 Problemas?

Veja **`POSTGRESQL_SETUP.md`** para guia completo com troubleshooting.

