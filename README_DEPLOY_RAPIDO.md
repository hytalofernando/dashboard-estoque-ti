# 🚀 Deploy Rápido - 5 Minutos!

## ✅ Preparação (no seu computador)

### 1. Subir para o GitHub

```bash
# Se ainda não fez, inicialize o Git
git init
git add .
git commit -m "Preparado para deploy"

# Crie um repositório no GitHub e depois:
git remote add origin https://github.com/SEU-USUARIO/dashboard-estoque-ti.git
git branch -M main
git push -u origin main
```

---

## 🌐 Deploy no Streamlit Cloud

### 2. Criar App

1. Acesse: **https://share.streamlit.io/**
2. Faça login com GitHub
3. Clique em **"New app"**
4. Preencha:
   - Repository: `seu-usuario/dashboard-estoque-ti`
   - Branch: `main`
   - Main file: `app.py`
5. Clique em **"Deploy"**

### 3. Configurar Senhas (IMPORTANTE!)

1. No painel do seu app, clique em **⋮** (três pontos)
2. Vá em **Settings** → **Secrets**
3. Cole e **ALTERE AS SENHAS**:

```toml
# Cole isso e MUDE AS SENHAS!
ADMIN_PASSWORD = "SuaSenhaAdmin@2024!"
VIEWER_PASSWORD = "SuaSenhaVisualizador#2024"

SECRET_KEY = "sua-chave-de-32-caracteres-aleatórios"
JWT_SECRET = "outra-chave-de-32-caracteres-aleatórios"

ENVIRONMENT = "production"
DEBUG = "false"
LOG_LEVEL = "INFO"

MAX_REQUESTS_PER_MINUTE = "30"
MAX_LOGIN_ATTEMPTS = "5"

CACHE_TTL_SECONDS = "300"
ENABLE_CACHE = "true"
```

4. Clique em **"Save"**
5. Aguarde 1-2 minutos para reiniciar

---

## 🎉 Pronto!

Seu app está em:
```
https://SEU-USUARIO-dashboard-estoque-ti.streamlit.app
```

### Login:
- **Administrador:** usuário `admin` + senha que você definiu
- **Visualizador:** usuário `visualizador` + senha que você definiu

---

## ⚠️ Importante Saber

### O arquivo Excel NÃO persiste!

O Streamlit Cloud reinicia periodicamente e **PERDE os dados do Excel**.

**Soluções:**

1. **Para Testes:** Aceite que os dados serão perdidos
2. **Para Produção:** Migre para banco de dados (veja `DEPLOY.md` completo)

---

## 📚 Documentação Completa

Para informações detalhadas, veja **`DEPLOY.md`**

## 🆘 Problemas?

- App não inicia? → Verifique os Secrets
- Erro de login? → Confirme que salvou os Secrets
- Dúvidas? → Leia `DEPLOY.md` completo

**Boa sorte! 🚀**

