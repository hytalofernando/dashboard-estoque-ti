# 🚀 Guia de Deploy - Dashboard Estoque TI

## 📋 Índice
1. [Preparação do Projeto](#-preparação-do-projeto)
2. [Deploy no Streamlit Community Cloud](#-deploy-no-streamlit-community-cloud)
3. [Configuração de Secrets](#-configuração-de-secrets)
4. [Primeiro Acesso](#-primeiro-acesso)
5. [Problemas Comuns](#-problemas-comuns)

---

## 🎯 Preparação do Projeto

### Passo 1: Verificar Arquivos

Certifique-se de que estes arquivos existem e estão corretos:

- ✅ `requirements.txt` - Dependências Python
- ✅ `.gitignore` - Arquivos ignorados pelo Git
- ✅ `.env.example` - Exemplo de variáveis de ambiente
- ✅ `.streamlit/config.toml` - Configurações do Streamlit
- ✅ `app.py` - Aplicação principal

### Passo 2: Criar Repositório no GitHub

Se ainda não tem um repositório:

```bash
# Inicializar Git (se ainda não foi feito)
git init

# Adicionar arquivos
git add .

# Fazer commit
git commit -m "Initial commit - Dashboard Estoque TI v3.0"

# Criar repositório no GitHub e conectar
git remote add origin https://github.com/SEU-USUARIO/dashboard-estoque-ti.git

# Enviar código
git branch -M main
git push -u origin main
```

**⚠️ IMPORTANTE:** O arquivo `.env` NÃO será enviado para o GitHub (está no `.gitignore`). Isso é correto e seguro!

---

## 🌐 Deploy no Streamlit Community Cloud

### Passo 1: Acessar Streamlit Cloud

1. Acesse: https://share.streamlit.io/
2. Faça login com sua conta GitHub
3. Clique em **"New app"** ou **"Deploy an app"**

### Passo 2: Configurar Deploy

Preencha os campos:

| Campo | Valor |
|-------|-------|
| **Repository** | `seu-usuario/dashboard-estoque-ti` |
| **Branch** | `main` |
| **Main file path** | `app.py` |
| **App URL** | `dashboard-estoque-ti` (ou nome desejado) |

### Passo 3: Aguardar Build

- ⏳ O Streamlit Cloud vai instalar as dependências do `requirements.txt`
- ⏳ Pode levar 2-5 minutos
- ✅ Quando concluído, você verá uma tela de erro (normal! Ainda faltam os secrets)

---

## 🔐 Configuração de Secrets

### Passo 1: Acessar Configurações

No painel do Streamlit Cloud:

1. Clique no menu **⋮** (três pontos) do seu app
2. Selecione **"Settings"**
3. Clique na aba **"Secrets"**

### Passo 2: Adicionar Secrets

Cole o conteúdo abaixo e **ALTERE AS SENHAS**:

```toml
# === AUTENTICAÇÃO ===
ADMIN_PASSWORD = "SuaSenhaForteAdmin@2024!"
VIEWER_PASSWORD = "SuaSenhaVisualizador#2024"

# === SEGURANÇA ===
SECRET_KEY = "sua-chave-secreta-com-no-minimo-32-caracteres-aleatórios"
JWT_SECRET = "sua-chave-jwt-com-no-minimo-32-caracteres-aleatórios"

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

**💡 Dica:** Para gerar chaves seguras, você pode usar:

**Python:**
```python
import secrets
print(secrets.token_urlsafe(32))
```

**PowerShell (Windows):**
```powershell
[Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Minimum 0 -Maximum 256 }))
```

### Passo 3: Salvar e Reiniciar

1. Clique em **"Save"**
2. O app vai reiniciar automaticamente
3. ✅ Aguarde 1-2 minutos

---

## 🎉 Primeiro Acesso

### URL do Seu App

Sua aplicação estará disponível em:

```
https://SEU-USUARIO-dashboard-estoque-ti.streamlit.app
```

ou

```
https://dashboard-estoque-ti.streamlit.app
```

### Login

Use as credenciais que você configurou nos Secrets:

**👑 Administrador:**
- Usuário: `admin`
- Senha: (a que você definiu em `ADMIN_PASSWORD`)

**👀 Visualizador:**
- Usuário: `visualizador`
- Senha: (a que você definiu em `VIEWER_PASSWORD`)

---

## ⚠️ Problemas Comuns

### 1. App não inicia / Erro de importação

**Problema:** Dependências não instaladas

**Solução:**
- Verifique se o `requirements.txt` está correto
- No Streamlit Cloud, clique em **"Manage app"** → **"Reboot app"**

### 2. Erro de autenticação

**Problema:** Secrets não configurados

**Solução:**
- Verifique se os secrets foram salvos corretamente
- Certifique-se de que não há espaços extras nas senhas
- Reinicie o app

### 3. Arquivo Excel não persiste

**⚠️ IMPORTANTE:** O Streamlit Cloud reinicia periodicamente e **perde arquivos locais**

**Soluções:**

**Opção A: Usar apenas para testes**
- Aceite que os dados serão perdidos
- Adicione dados de exemplo no código

**Opção B: Migrar para banco de dados (RECOMENDADO para produção)**

Para produção robusta, recomendo migrar de Excel para PostgreSQL:

1. **Adicione ao `requirements.txt`:**
```txt
psycopg2-binary>=2.9.9
```

2. **Configure PostgreSQL no Streamlit:**
   - Streamlit oferece PostgreSQL gratuito
   - Acesse: Settings → Database → Add PostgreSQL

3. **Atualize o código:**
   - Adapte `excel_service.py` para usar SQLAlchemy
   - Já temos a dependência instalada!

---

## 🔄 Atualizações Futuras

Para atualizar seu app:

```bash
# Faça as alterações no código

# Commit e push
git add .
git commit -m "Descrição das alterações"
git push origin main
```

O Streamlit Cloud **detecta automaticamente** e faz redeploy! 🚀

---

## 📊 Monitoramento

### Logs

No painel do Streamlit Cloud:
1. Clique no menu **⋮** do seu app
2. Selecione **"Logs"**
3. Veja logs em tempo real

### Métricas

O Streamlit Cloud fornece:
- 📈 Número de visualizações
- 👥 Usuários ativos
- ⏱️ Tempo de resposta
- 🔄 Status de saúde do app

---

## 🎯 Próximos Passos (Opcional)

### 1. Domínio Customizado

Você pode adicionar um domínio próprio:
- Exemplo: `estoque.suaempresa.com`
- Requer plano pago do Streamlit

### 2. Migração para Banco de Dados

Para um sistema robusto:
1. Configure PostgreSQL no Streamlit Cloud
2. Migre dados do Excel para o banco
3. Atualize services para usar SQLAlchemy

### 3. Backup Automático

Configure backup dos dados:
- Exportação automática para Google Drive/Dropbox
- Webhook para notificações
- Logs externos (Papertrail, Loggly)

---

## 💡 Dicas de Produção

### Segurança

- ✅ **SEMPRE** use senhas fortes (mínimo 12 caracteres)
- ✅ Ative 2FA no GitHub
- ✅ Não compartilhe os secrets
- ✅ Monitore os logs regularmente

### Performance

- ✅ Use cache (`@st.cache_data`) para operações pesadas
- ✅ Otimize carregamento de dados
- ✅ Limite histórico de movimentações

### Manutenção

- ✅ Atualize dependências regularmente
- ✅ Faça backup dos dados importantes
- ✅ Teste antes de fazer push
- ✅ Use branches para desenvolvimento

---

## 📞 Suporte

### Documentação Oficial

- Streamlit Docs: https://docs.streamlit.io/
- Deploy Guide: https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app

### Comunidade

- Streamlit Forum: https://discuss.streamlit.io/
- GitHub Issues: (seu repositório)

---

## ✅ Checklist Final

Antes de fazer deploy, verifique:

- [ ] Código commitado e pushed para GitHub
- [ ] `.gitignore` configurado corretamente
- [ ] `requirements.txt` atualizado
- [ ] `.env` NÃO está no repositório
- [ ] App criado no Streamlit Cloud
- [ ] Secrets configurados
- [ ] Senhas alteradas (não usar padrões)
- [ ] App funcionando corretamente
- [ ] Login testado (admin e visualizador)
- [ ] Todas funcionalidades testadas

---

**🎉 Parabéns! Seu Dashboard Estoque TI está online!**

Deploy realizado com ❤️ usando Streamlit Community Cloud

