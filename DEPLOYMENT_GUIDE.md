# 🚀 **GUIA DE IMPLANTAÇÃO - Dashboard Estoque TI v2.1**

## 🎯 **Visão Geral**

Este guia detalha como implantar o Dashboard Estoque TI v2.1 com todas as melhorias de segurança e performance implementadas.

---

## 🔧 **PRÉ-REQUISITOS**

### **Sistema:**
- ✅ **Python 3.8+** (Recomendado: 3.11+)
- ✅ **pip** atualizado
- ✅ **Git** (para clonagem)
- ✅ **Navegador moderno** (Chrome, Firefox, Edge)

### **Opcional (Produção):**
- 🐳 **Docker** (para containerização)
- 🌐 **Nginx** (proxy reverso)
- 🔒 **SSL Certificate** (HTTPS)

---

## 📦 **INSTALAÇÃO PASSO A PASSO**

### **1. 📁 Clonagem e Preparação**

```bash
# Clonar repositório
git clone <url-do-repositorio>
cd dashboard-estoque-ti

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### **2. 📋 Instalação de Dependências**

```bash
# Instalar dependências de segurança
pip install --upgrade pip
pip install -r requirements.txt

# Verificar instalação
python -c "import bcrypt; print('✅ Bcrypt instalado')"
python -c "import streamlit; print('✅ Streamlit instalado')"
```

### **3. 🔐 Configuração de Segurança**

```bash
# Copiar arquivo de configuração
cp .env.example .env

# Editar .env com suas configurações
# IMPORTANTE: Altere as senhas padrão!
```

**Exemplo de .env seguro:**
```bash
# === AUTENTICAÇÃO SEGURA ===
ADMIN_PASSWORD=MinhaSenh@Admin2024!Segur@
VIEWER_PASSWORD=Visualiz@dor2024#Forte

# === CHAVES DE SEGURANÇA ===
SECRET_KEY=chave-super-secreta-32-caracteres-aleatoria-aqui
JWT_SECRET=jwt-secret-key-diferente-da-anterior-segura

# === CONFIGURAÇÕES ===
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# === PERFORMANCE ===
CACHE_TTL_SECONDS=300
ENABLE_CACHE=true
MAX_REQUESTS_PER_MINUTE=30
```

### **4. 🧪 Teste de Configuração**

```bash
# Teste rápido
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('✅ Configuração carregada')
print(f'Admin Password: {\"CONFIGURADO\" if os.getenv(\"ADMIN_PASSWORD\") != \"admin123_CHANGE_ME\" else \"❌ USAR SENHA PADRÃO\"}')
"
```

---

## 🚀 **EXECUÇÃO**

### **Desenvolvimento:**
```bash
# Ativar ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Executar aplicação
streamlit run app.py

# Acessar: http://localhost:8501
```

### **Produção (Básica):**
```bash
# Executar com configurações de produção
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

### **Produção (Docker):**

**Dockerfile já incluído:**
```bash
# Construir imagem
docker build -t dashboard-estoque-ti .

# Executar container
docker run -p 8501:8501 \
  -e ADMIN_PASSWORD=sua_senha_aqui \
  -e VIEWER_PASSWORD=senha_viewer_aqui \
  dashboard-estoque-ti
```

**Docker Compose:**
```bash
# Executar stack completa
docker-compose up -d

# Verificar status
docker-compose ps
```

---

## 🔒 **CONFIGURAÇÃO DE SEGURANÇA AVANÇADA**

### **1. 🌐 Nginx (Proxy Reverso)**

**nginx.conf:**
```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    # Redirect para HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name seu-dominio.com;
    
    # SSL Configuration
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000";
    
    # Proxy para Streamlit
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support
    location /_stcore/stream {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### **2. 🔥 Firewall (UFW)**

```bash
# Configurar firewall básico
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 8501  # Bloquear acesso direto ao Streamlit
```

### **3. 📊 Monitoramento**

**Script de monitoramento:**
```bash
#!/bin/bash
# monitor.sh

# Verificar se aplicação está rodando
if ! curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "❌ Aplicação não está respondendo"
    # Reiniciar serviço
    systemctl restart dashboard-estoque
else
    echo "✅ Aplicação funcionando"
fi

# Verificar logs de erro
if grep -q "ERROR" logs/dashboard.log; then
    echo "⚠️ Erros encontrados nos logs"
fi
```

---

## 📋 **CHECKLIST DE IMPLANTAÇÃO**

### **🔒 Segurança:**
- [ ] Senhas padrão alteradas no .env
- [ ] Arquivo .env com permissões 600 (`chmod 600 .env`)
- [ ] HTTPS configurado (produção)
- [ ] Firewall configurado
- [ ] Headers de segurança configurados
- [ ] Logs de auditoria funcionando

### **⚡ Performance:**
- [ ] Cache habilitado
- [ ] TTL configurado adequadamente
- [ ] Rate limiting testado
- [ ] Backup automático configurado
- [ ] Monitoramento ativo

### **🧪 Testes:**
- [ ] Login com usuário admin
- [ ] Login com usuário visualizador
- [ ] Tentativas de força bruta bloqueadas
- [ ] Inputs maliciosos sanitizados
- [ ] Cache funcionando (verificar hit rate)
- [ ] Logs sendo gerados

---

## 🚨 **SOLUÇÃO DE PROBLEMAS**

### **Problema: "ModuleNotFoundError: bcrypt"**
```bash
# Solução:
pip install bcrypt>=4.0.1

# Se persistir:
pip uninstall bcrypt
pip install --no-cache-dir bcrypt
```

### **Problema: "Arquivo .env não encontrado"**
```bash
# Solução:
cp .env.example .env
# Editar .env com suas configurações
```

### **Problema: "Senhas padrão detectadas"**
```bash
# Verificar logs:
tail -f logs/dashboard.log | grep "ATENÇÃO"

# Editar .env:
nano .env
# Alterar ADMIN_PASSWORD e VIEWER_PASSWORD
```

### **Problema: "Rate limit muito restritivo"**
```bash
# Ajustar no .env:
MAX_REQUESTS_PER_MINUTE=60  # Aumentar limite
```

### **Problema: "Cache não funcionando"**
```bash
# Verificar configuração:
ENABLE_CACHE=true
CACHE_TTL_SECONDS=300

# Verificar logs:
grep "Cache" logs/dashboard.log
```

---

## 📊 **MONITORAMENTO E MANUTENÇÃO**

### **1. 📈 Métricas Importantes**

**Verificar regularmente:**
- Taxa de hit do cache (>70% é bom)
- Tentativas de login falhadas
- Tempo de resposta da aplicação
- Uso de memória e CPU
- Tamanho dos logs

### **2. 🔄 Manutenção Rotineira**

**Diário:**
- Verificar logs de erro
- Monitorar tentativas de acesso suspeitas
- Verificar status da aplicação

**Semanal:**
- Backup dos dados
- Rotação de logs
- Verificar atualizações de segurança
- Análise de performance

**Mensal:**
- Revisar senhas e tokens
- Atualizar dependências
- Teste de recuperação de backup
- Auditoria de segurança

### **3. 📋 Comandos Úteis**

```bash
# Status da aplicação
systemctl status dashboard-estoque

# Logs em tempo real
tail -f logs/dashboard.log

# Verificar conexões ativas
netstat -tlnp | grep :8501

# Uso de recursos
htop
df -h

# Backup rápido
tar -czf backup-$(date +%Y%m%d).tar.gz *.xlsx logs/

# Verificar segurança
grep "Login falhado" logs/dashboard.log | tail -10
```

---

## 🎯 **PRÓXIMOS PASSOS**

### **Após Implantação:**
1. **Configurar backup automático**
2. **Implementar monitoramento avançado**
3. **Configurar alertas de segurança**
4. **Documentar procedimentos operacionais**

### **Melhorias Futuras:**
1. **Migração para PostgreSQL**
2. **Implementação de 2FA**
3. **API REST separada**
4. **Containerização completa**

---

## 📞 **SUPORTE**

### **Logs de Diagnóstico:**
```bash
# Gerar relatório completo
echo "=== DIAGNÓSTICO DASHBOARD ESTOQUE TI ===" > diagnostico.txt
echo "Data: $(date)" >> diagnostico.txt
echo "Versão Python: $(python --version)" >> diagnostico.txt
echo "Dependências:" >> diagnostico.txt
pip list >> diagnostico.txt
echo "Logs recentes:" >> diagnostico.txt
tail -50 logs/dashboard.log >> diagnostico.txt
```

### **Contatos:**
- 📧 **Email:** suporte@empresa.com
- 📱 **Telefone:** (11) 9999-9999
- 💬 **Chat:** Teams/Slack

---

**Versão:** 2.1 Security Enhanced  
**Data:** Agosto 2025  
**Próxima Atualização:** Implementação de banco relacional
