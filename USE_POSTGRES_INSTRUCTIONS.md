# 🔧 Como Ativar PostgreSQL

## ✅ Seu projeto já está preparado para PostgreSQL!

### **Opção 1: Automática (Recomendada)**

O sistema detecta automaticamente se deve usar PostgreSQL ou Excel baseado na presença da variável `DATABASE_URL`.

**Para usar PostgreSQL:**
1. Configure `DATABASE_URL` no `.env`:
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/database
   ```
2. Execute o app normalmente:
   ```bash
   streamlit run app.py
   ```

**Para voltar ao Excel:**
1. Remova ou comente `DATABASE_URL` do `.env`
2. Execute o app

### **Opção 2: Manual (Editar Código)**

Edite o arquivo `app.py` na linha onde importa o `EstoqueService`:

**Para PostgreSQL:**
```python
from services.estoque_service_postgres import EstoqueService
```

**Para Excel:**
```python
from services.estoque_service import EstoqueService
```

---

## 🚀 Deploy no Streamlit Cloud

No Streamlit Cloud, basta configurar `DATABASE_URL` nos **Secrets**:

```toml
DATABASE_URL = "postgresql://..."
```

O sistema usará PostgreSQL automaticamente! ✨

---

## 📊 Verificar qual banco está sendo usado

Execute:
```python
from config.database_config import db_config
print(db_config.info())
```

---

**Pronto! Seu sistema agora suporta ambos!** 🎉

