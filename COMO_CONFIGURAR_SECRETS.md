# 🔐 COMO CONFIGURAR SECRETS NO STREAMLIT CLOUD

## 📋 PASSO A PASSO VISUAL

### **PASSO 1: Acessar Secrets**

1. Vá para: https://share.streamlit.io/
2. Encontre seu app na lista
3. Clique nos **três pontos (⋮)** ao lado do nome do app
4. Selecione **"Settings"**
5. No menu lateral, clique em **"Secrets"**

---

### **PASSO 2: Formato dos Secrets**

O Streamlit usa formato **TOML**. É assim:

```toml
VARIAVEL = "valor"
```

**⚠️ ATENÇÃO:**
- ✅ Use `=` (igual)
- ✅ Valores entre aspas duplas `"valor"`
- ✅ Uma variável por linha
- ❌ NÃO use `#` antes das variáveis ativas
- ❌ NÃO use `:` (dois pontos)

---

### **PASSO 3: Copiar e Colar Seus Secrets**

**COPIE ESTE CONTEÚDO COMPLETO:**

```toml
# === BANCO DE DADOS ===
DATABASE_URL = "sqlite:///estoque_ti.db"

# === AUTENTICAÇÃO ===
ADMIN_PASSWORD = "admin123"
VIEWER_PASSWORD = "viewer123"

# === SEGURANÇA ===
SECRET_KEY = "minha-chave-secreta-unica-de-32-caracteres-12345"
JWT_SECRET = "outra-chave-diferente-unica-de-32-chars-98765"

# === CONFIGURAÇÕES ===
ENVIRONMENT = "production"
DEBUG = "false"
LOG_LEVEL = "INFO"
MAX_REQUESTS_PER_MINUTE = "30"
MAX_LOGIN_ATTEMPTS = "5"
CACHE_TTL_SECONDS = "300"
ENABLE_CACHE = "true"
```

---

### **PASSO 4: Colar no Streamlit**

1. Na página de Secrets do Streamlit Cloud
2. **APAGUE** tudo que estiver lá (se houver algo)
3. **COLE** o conteúdo completo acima
4. Clique no botão **"Save"** no canto inferior direito

---

### **PASSO 5: Aguardar Reinício**

- O app vai **reiniciar automaticamente**
- Aguarde **1-2 minutos**
- Seu app estará online com as novas configurações!

---

## 🔐 **EXEMPLO VISUAL:**

**O campo de Secrets ficará assim:**

```
┌────────────────────────────────────────────┐
│ Secrets                                    │
├────────────────────────────────────────────┤
│                                            │
│ DATABASE_URL = "sqlite:///estoque_ti.db"  │
│                                            │
│ ADMIN_PASSWORD = "admin123"               │
│ VIEWER_PASSWORD = "viewer123"             │
│                                            │
│ SECRET_KEY = "minha-chave-32-chars"       │
│ JWT_SECRET = "outra-chave-32-chars"       │
│                                            │
│ ENVIRONMENT = "production"                │
│ DEBUG = "false"                           │
│ LOG_LEVEL = "INFO"                        │
│ MAX_REQUESTS_PER_MINUTE = "30"            │
│ MAX_LOGIN_ATTEMPTS = "5"                  │
│ CACHE_TTL_SECONDS = "300"                 │
│ ENABLE_CACHE = "true"                     │
│                                            │
└────────────────────────────────────────────┘
       [Cancel]              [Save]
```

Clique em **[Save]** →

---

## ⚠️ **ERROS COMUNS A EVITAR:**

### ❌ **ERRADO:**
```toml
# Sem aspas
ADMIN_PASSWORD = admin123

# Com dois pontos
ADMIN_PASSWORD: "admin123"

# Sem igual
ADMIN_PASSWORD "admin123"

# Espaços errados
ADMIN_PASSWORD ="admin123"
```

### ✅ **CERTO:**
```toml
ADMIN_PASSWORD = "admin123"
```

---

## 🎯 **MUDAR SENHAS DEPOIS:**

### **Senhas Mais Fortes (Use no Streamlit Cloud):**

```toml
# === AUTENTICAÇÃO ===
ADMIN_PASSWORD = "MinhaSenha@Admin2024#Forte!"
VIEWER_PASSWORD = "MinhaSenha#Visualizador2024!"

# === SEGURANÇA ===
SECRET_KEY = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"
JWT_SECRET = "z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4"
```

---

## 💡 **GERAR SENHAS SEGURAS:**

### **No PowerShell (Windows):**
```powershell
# Gerar chave aleatória de 32 caracteres
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | % {[char]$_})
```

### **No Python:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## 🔄 **ATUALIZAR SECRETS:**

Se precisar mudar uma senha depois:

1. Vá em **Settings** → **Secrets**
2. Encontre a linha: `ADMIN_PASSWORD = "admin123"`
3. Mude para: `ADMIN_PASSWORD = "NovaSenha123!"`
4. Clique em **"Save"**
5. App reinicia automaticamente

---

## ✅ **VERIFICAR SE FUNCIONOU:**

Depois de salvar:

1. Aguarde 1-2 minutos
2. Acesse seu app: `https://seu-app.streamlit.app`
3. Tente fazer login:
   - Usuário: `admin`
   - Senha: (a que você configurou nos secrets)

Se entrar → **✅ FUNCIONOU!**

---

## 📞 **PROBLEMAS?**

### **"Senha incorreta" após configurar:**

1. Verifique se salvou os secrets
2. Aguarde 2 minutos (reinício completo)
3. Limpe cache do navegador (Ctrl+Shift+Del)
4. Tente novamente

### **App não inicia:**

1. Vá em **Logs** (⋮ → Logs)
2. Procure por erros
3. Verifique se formato TOML está correto
4. Tente **Reboot app** (⋮ → Reboot app)

---

## 🎊 **PRONTO!**

Agora você sabe configurar os secrets perfeitamente! 🎉

**Resumo:**
1. Settings → Secrets
2. Copiar o conteúdo com suas senhas
3. Colar no campo
4. Save
5. Aguardar 1-2 minutos
6. Testar login!

---

**Boa sorte com seu deploy! 🚀**



