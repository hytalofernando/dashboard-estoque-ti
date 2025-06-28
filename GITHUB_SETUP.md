# 🚀 Configuração do Repositório GitHub

## Passos para criar o repositório no GitHub:

### 1. Acesse o GitHub
- Vá para: https://github.com
- Faça login na sua conta

### 2. Crie um novo repositório
- Clique no botão "+" no canto superior direito
- Selecione "New repository"

### 3. Configure o repositório
- **Repository name**: `dashboard-estoque-ti`
- **Description**: `Dashboard completo para gerenciamento de estoque de TI com Streamlit`
- **Visibility**: Escolha entre Public ou Private
- **NÃO** marque "Add a README file" (já temos um)
- **NÃO** marque "Add .gitignore" (já temos um)
- **NÃO** marque "Choose a license" (pode adicionar depois)

### 4. Clique em "Create repository"

### 5. Após criar o repositório, execute os comandos abaixo:

```bash
# Adicionar o repositório remoto (substitua SEU_USUARIO pelo seu username do GitHub)
git remote add origin https://github.com/SEU_USUARIO/dashboard-estoque-ti.git

# Enviar o código para o GitHub
git branch -M main
git push -u origin main
```

### 6. Exemplo completo:
```bash
# Se seu username for "hital", por exemplo:
git remote add origin https://github.com/hital/dashboard-estoque-ti.git
git branch -M main
git push -u origin main
```

## 📋 Arquivos incluídos no repositório:

- ✅ `app.py` - Aplicação principal do dashboard
- ✅ `utils.py` - Funções utilitárias
- ✅ `requirements.txt` - Dependências do projeto
- ✅ `README.md` - Documentação completa
- ✅ `run_dashboard.bat` - Script de execução (Windows)
- ✅ `.gitignore` - Arquivos ignorados pelo Git

## 🚫 Arquivos NÃO incluídos (por segurança):

- ❌ `estoque_ti.xlsx` - Banco de dados (será criado automaticamente)
- ❌ `.venv/` - Ambiente virtual
- ❌ `__pycache__/` - Cache do Python

## 🔗 Após o push, seu repositório estará disponível em:
`https://github.com/SEU_USUARIO/dashboard-estoque-ti`

## 📝 Próximos passos sugeridos:

1. **Adicionar uma licença** (MIT, Apache, etc.)
2. **Configurar GitHub Pages** para demo online
3. **Adicionar badges** (status, versão, etc.)
4. **Criar releases** para versões estáveis
5. **Configurar GitHub Actions** para CI/CD

## 🆘 Se precisar de ajuda:

- Verifique se o Git está configurado: `git config --list`
- Configure seu usuário se necessário:
  ```bash
  git config --global user.name "Seu Nome"
  git config --global user.email "seu.email@exemplo.com"
  ``` 