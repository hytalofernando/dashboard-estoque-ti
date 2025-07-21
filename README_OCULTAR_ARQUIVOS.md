# 🙈 Como Ocultar Páginas do Menu de Desenvolvimento

## 🎯 Problema
Você está vendo todas as páginas individuais do projeto no menu de desenvolvimento:
- `adicionar page`
- `codigos page` 
- `configuracoes page`
- `dashboard page`
- `historico page`
- `remover page`

**Você quer manter apenas o `app` principal visível, pois é o único que mostra gráficos.**

---

## 💡 SOLUÇÕES

### 🔧 **Método 1: VS Code (Mais Comum)**

Já criei o arquivo `.vscode/settings.json` que:
- ✅ **Oculta** todas as pastas internas (`pages/`, `services/`, `utils/`, etc.)
- ✅ **Mantém visível** apenas `app.py` e arquivos essenciais
- ✅ **Agrupa arquivos** relacionados sob o `app.py`

**Para ativar:**
1. Reinicie o VS Code
2. O menu agora mostrará apenas:
   ```
   📁 dashboard/
   ├── 📄 app.py ⭐ (arquivo principal)
   ├── 📄 README.md
   ├── 📄 requirements.txt
   └── 📄 run_dashboard.bat
   ```

### 🎨 **Método 2: File Nesting (Agrupamento)**

O VS Code agrupará automaticamente os arquivos assim:
```
📄 app.py
  ├── 📁 pages/
  ├── 📁 services/
  ├── 📁 models/
  ├── 📁 utils/
  ├── 📁 config/
  └── 📄 *.md
```

**Como usar:**
- Clique na **seta** ao lado de `app.py` para expandir/ocultar

### ⚙️ **Método 3: Configuração Manual**

Se não funcionar automaticamente:

1. **VS Code**: `Ctrl+,` → Procure "files exclude"
2. **Adicione estas regras:**
   ```
   pages/**
   services/**
   models/**
   utils/**
   config/**
   ```

### 🚀 **Método 4: Workspace Settings**

Crie `.code-workspace`:
```json
{
  "folders": [
    {
      "name": "Dashboard Principal",
      "path": "."
    }
  ],
  "settings": {
    "files.exclude": {
      "pages/**": true,
      "services/**": true,
      "models/**": true,
      "utils/**": true,
      "config/**": true
    }
  }
}
```

---

## 🎯 **RESULTADO FINAL**

Após aplicar qualquer método, seu menu ficará assim:

```
📁 dashboard/
├── 📄 app.py             ⭐ (ÚNICO ARQUIVO VISÍVEL)
├── 📄 README.md          
├── 📄 requirements.txt   
├── 📄 run_dashboard.bat  
└── 📄 estoque_ti.xlsx    
```

**Apenas o `app.py` será destacado como arquivo principal!**

---

## 🔧 **Para Reverter (Se Precisar)**

Se quiser ver todos os arquivos novamente:

1. **Temporário**: `Ctrl+Shift+P` → "Toggle Excluded Files"
2. **Permanente**: Apague o arquivo `.vscode/settings.json`

---

## ✅ **EXECUTAR O PROJETO**

Agora você pode focar apenas no arquivo principal:
```bash
streamlit run app.py
```

**O app.py contém TUDO que você precisa ver - gráficos, dashboard, funcionalidades!** 📊✨

---

**🎯 Menu limpo = Foco no que importa!** 🚀 