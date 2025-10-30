# 🚀 DEPLOY NO STREAMLIT CLOUD - PASSO A PASSO

## ✅ PRÉ-REQUISITOS (JÁ FEITOS!)

- ✅ Migração para banco de dados concluída
- ✅ Sistema testado e funcionando
- ✅ Código no GitHub
- ✅ `.env` configurado (não vai pro GitHub)

---

## 📋 **PASSO A PASSO COMPLETO**

### **PASSO 1: Verificar Arquivos no GitHub** ✅

Execute para ver o status:

```bash
git status
```

Se houver alterações pendentes:

```bash
git add .
git commit -m "🚀 Pronto para deploy com SQLite/PostgreSQL"
git push origin main
```

---

### **PASSO 2: Acessar Streamlit Cloud** 🌐

1. Acesse: **https://share.streamlit.io/**
2. Faça login com sua conta GitHub
3. Clique em **"New app"** ou **"Deploy an app"**

---

### **PASSO 3: Configurar o Deploy** ⚙️

Preencha os campos:

| Campo | Valor |
|-------|-------|
| **Repository** | `hytalofernando/dashboard-estoque-ti` |
| **Branch** | `main` |
| **Main file path** | `app.py` |
| **App URL** | `dashboard-estoque-ti` (ou nome que preferir) |

Clique em **"Advanced settings..."** (opcional - pode deixar padrão)

Clique em **"Deploy!"**

⏳ **Aguarde 2-5 minutos** (vai instalar as dependências)

---

### **PASSO 4: Configurar PostgreSQL no Streamlit Cloud** 🐘

#### **Opção A: PostgreSQL Gratuito do Streamlit (RECOMENDADO)**

1. No painel do seu app, clique em **⋮** (três pontos)
2. Vá em **Settings** → **Data sources**
3. Clique em **"Connect to data source"**
4. Selecione **"PostgreSQL"**
5. O Streamlit vai criar um banco PostgreSQL **GRATUITO** para você!
6. **Copie a URL** que aparece (algo como `postgresql://user:pass@host:5432/database`)

#### **Opção B: Usar SQLite (Já Funciona!)**

Se quiser começar com SQLite (mais rápido), pule para o Passo 5 e use:

```toml
DATABASE_URL = "sqlite:///estoque_ti.db"
```

**Nota:** SQLite funciona no Streamlit Cloud, mas o banco é resetado em restarts. PostgreSQL é melhor para produção.

---

### **PASSO 5: Configurar Secrets** 🔐

No painel do Streamlit Cloud:

1. Vá em **Settings** → **Secrets**
2. Cole o conteúdo abaixo e **ALTERE AS SENHAS**:

```toml
# === BANCO DE DADOS ===
# Para PostgreSQL (fornecido pelo Streamlit):
DATABASE_URL = "postgresql://user:password@host:5432/database"

# OU para SQLite (funciona, mas dados não persistem):
# DATABASE_URL = "sqlite:///estoque_ti.db"

# === AUTENTICAÇÃO ===
ADMIN_PASSWORD = "SuaSenhaAdmin@2024!Forte#"
VIEWER_PASSWORD = "SuaSenhaVisualizador#2024Forte!"

# === SEGURANÇA ===
SECRET_KEY = "sua-chave-de-32-caracteres-aleatorios-aqui"
JWT_SECRET = "outra-chave-de-32-caracteres-aleatorios"

# === CONFIGURAÇÕES GERAIS ===
ENVIRONMENT = "production"
DEBUG = "false"
LOG_LEVEL = "INFO"

# === RATE LIMITING ===
MAX_REQUESTS_PER_MINUTE = "30"
MAX_LOGIN_ATTEMPTS = "5"

# === CACHE ===
CACHE_TTL_SECONDS = "300"
ENABLE_CACHE = "true"
```

3. Clique em **"Save"**

---

### **PASSO 6: Migrar Dados para o PostgreSQL do Cloud** 📦

#### **Opção 1: Usar SQLite Localmente e Migrar Depois**

1. Configure `DATABASE_URL` nos secrets do Streamlit como SQLite
2. O banco será recriado vazio no cloud
3. Você pode adicionar dados pela interface

#### **Opção 2: Migrar Dados do SQLite Local para PostgreSQL do Cloud**

1. **No seu computador**, edite o arquivo `.env`:

```env
# Use a URL do PostgreSQL fornecida pelo Streamlit
DATABASE_URL=postgresql://user:password@host:5432/database
```

2. Execute o script de migração:

```bash
python migrate_auto.py
```

Isso vai enviar todos os dados do seu SQLite local para o PostgreSQL do Streamlit Cloud!

3. Após migrar, o cloud já terá todos os dados!

---

### **PASSO 7: Aguardar Deploy e Testar** ✅

1. O Streamlit vai reiniciar o app automaticamente
2. Aguarde 1-2 minutos
3. Acesse a URL do seu app (ex: `https://dashboard-estoque-ti.streamlit.app`)

---

## 🧪 **VERIFICAR SE ESTÁ FUNCIONANDO**

### ✅ Checklist:

- [ ] App carregou sem erros?
- [ ] Página de login aparece?
- [ ] Consegue fazer login com as credenciais?
- [ ] Dashboard mostra "Banco de Dados: 🐘 PostgreSQL" na sidebar?
- [ ] Dados aparecem corretamente?

Se todos estiverem OK: **🎉 DEPLOY CONCLUÍDO!**

---

## 🔧 **PROBLEMAS COMUNS**

### **1. App não inicia / Erro de importação**

**Solução:**
- Verifique se o `requirements.txt` está no GitHub
- No painel do Streamlit, clique em **"Reboot app"**

### **2. Erro de autenticação / Senha não funciona**

**Solução:**
- Verifique se os secrets foram salvos corretamente
- Certifique-se de que não há espaços extras
- Clique em "Save" novamente e aguarde restart

### **3. Banco de dados vazio**

**Solução:**
- Execute o script de migração local apontando para o PostgreSQL do cloud
- Ou adicione dados pela interface

### **4. Erro "DATABASE_URL not found"**

**Solução:**
- Verifique se `DATABASE_URL` está nos Secrets
- Deve estar exatamente como: `DATABASE_URL = "postgresql://..."`
- Clique em "Save" e aguarde restart

---

## 🎯 **DICA PRO: Gerar Chaves Seguras**

**No PowerShell (Windows):**
```powershell
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

**No Python:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## 📊 **MONITORAMENTO**

### Ver Logs:

1. No painel do app, clique em **⋮**
2. Selecione **"Logs"**
3. Veja logs em tempo real

### Ver Métricas:

- Streamlit Cloud mostra automaticamente:
  - 👥 Visitantes
  - ⏱️ Tempo de resposta
  - 📊 Uso de recursos

---

## 🔄 **ATUALIZAÇÕES FUTURAS**

Para atualizar o app:

```bash
# Faça alterações no código
git add .
git commit -m "Descrição das alterações"
git push origin main
```

O Streamlit Cloud **detecta automaticamente** e faz redeploy! 🚀

---

## 💡 **OPÇÕES AVANÇADAS**

### **Custom Domain (Domínio Próprio)**

- Disponível em planos pagos
- Exemplo: `estoque.suaempresa.com`

### **Escalar para PostgreSQL Robusto**

- Neon.tech (gratuito até 10 GB)
- Supabase (gratuito até 500 MB)
- Railway (gratuito limitado)

---

## 📞 **RECURSOS**

- **Docs do Streamlit:** https://docs.streamlit.io/
- **Deploy Guide:** https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app
- **Community:** https://discuss.streamlit.io/

---

## ✅ **CHECKLIST FINAL**

Antes de considerar completo:

- [ ] App publicado no Streamlit Cloud
- [ ] PostgreSQL configurado e funcionando
- [ ] Secrets configurados (senhas fortes!)
- [ ] Dados migrados (se necessário)
- [ ] Login funcionando
- [ ] Dashboard carregando
- [ ] Todas as páginas acessíveis
- [ ] Sidebar mostrando banco correto
- [ ] URL compartilhada com equipe

---

**🎉 SEU APP ESTÁ NO AR!** 🚀

URL: `https://seu-app.streamlit.app`

**Compartilhe com sua equipe e aproveite!** ✨

