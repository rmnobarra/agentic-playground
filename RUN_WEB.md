# 🌐 Interface Web - Guia de Uso

## 🚀 Demo Online

**Acesse agora sem instalar nada:**

👉 **https://agentic-playground.streamlit.app/**

A interface está disponível publicamente na Streamlit Cloud!

---

## 💻 Como Executar Localmente

### 1. Instalar Streamlit (se ainda não instalou)

```bash
pip install -r requirements.txt
```

### 2. Executar a Interface Web

```bash
streamlit run app.py
```

O browser abrirá automaticamente em: **http://localhost:8501**

## Funcionalidades

### 📝 Nova Solicitação
- Preencha os dados do cliente, produto e troca
- Execute a jornada agêntica em tempo real
- Visualize o resultado de cada agent
- Veja a decisão final (APROVADO/REPROVADO)

### 🎯 Cenários Pré-definidos
Execute cenários de teste prontos:

1. **✅ Troca Aprovada**: Todos os requisitos OK
2. **⏰ Fora do Prazo**: Data de compra muito antiga
3. **📦 Sem Estoque**: Produto desejado indisponível
4. **❌ Dados Inválidos**: Cliente não encontrado

### 📊 Sobre
- Métricas do sistema
- Conceitos aplicados
- Stack tecnológica
- Documentação

## Interface

```
┌─────────────────────────────────────────────┐
│  🤖 Jornada Agêntica - Sistema de Trocas    │
├─────────────────────────────────────────────┤
│                                             │
│  [Nova Solicitação] [Cenários] [Sobre]      │
│                                             │
│  👤 Dados do Cliente                        │
│  ├─ CPF: [____________]                     │
│  ├─ Nome: [____________]                    │
│  └─ Email: [____________]                   │
│                                             │
│  📦 Produto Original                        │
│  ├─ Código: [____________]                  │
│  ├─ Descrição: [____________]               │
│  └─ Data Compra: [____/____/____]           │
│                                             │
│  🔄 Dados da Troca                          │
│  ├─ Motivo: [▼ produto_defeituoso]          │
│  ├─ Descrição: [____________]               │
│  └─ Tipo: [▼ troca_outro_produto]           │
│                                             │
│  [🚀 Executar Jornada Agêntica]             │
│                                             │
│  Resultado:                                 │
│  ┌─────────────────────────────────────┐    │
│  │ ✅ TROCA APROVADA                   │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  📋 Detalhes da Jornada:                    │
│  ▸ 1️⃣ Validação de Cliente                  │
│  ▸ 2️⃣ Análise de Documentos                 │
│  ▸ 3️⃣ Validação de Elegibilidade            │
│  ▸ 4️⃣ Classificação de Troca                │
│  ▸ 5️⃣ Validação de Estoque                  │
│  ▸ 6️⃣ Decisão Final                         │
│                                             │
└─────────────────────────────────────────────┘
```

## Visualização em Tempo Real

A interface mostra:

- ✅ **Status**: Aprovado/Reprovado com cores
- 🤖 **Raciocínio dos Agents**: Expandir cada etapa
- 📊 **Métricas**: Tempo, status, agent usado
- 🔍 **JSON Completo**: Dados brutos da jornada

## Customização

### Mudar a Porta

```bash
streamlit run app.py --server.port 8080
```

### Modo Dark/Light

Clique no menu (⋮) → Settings → Theme

### Desabilitar Telemetria

```bash
streamlit run app.py --browser.gatherUsageStats false
```

## Troubleshooting

### Erro: "GROQ_API_KEY not found"

Configure o arquivo `.env`:
```bash
echo "GROQ_API_KEY=sua_chave_aqui" >> .env
```

### Porta já em uso

```bash
# Use outra porta
streamlit run app.py --server.port 8502
```

### Interface não abre

```bash
# Abra manualmente
# O endereço aparece no terminal após executar
# Exemplo: http://localhost:8501
```

## Comandos Úteis

```bash
# Limpar cache do Streamlit
streamlit cache clear

# Ver versão
streamlit --version

# Ajuda
streamlit --help
```

## Próximos Passos

Após usar a interface:

1. ✅ Teste os 4 cenários pré-definidos
2. ✅ Crie suas próprias solicitações
3. ✅ Analise os logs detalhados de cada agent
4. ✅ Experimente diferentes combinações

## Deploy (Opcional)

Para disponibilizar publicamente:

### Streamlit Cloud (Gratuito)

1. Faça commit do projeto no GitHub
2. Acesse: https://streamlit.io/cloud
3. Conecte seu repositório
4. Configure `GROQ_API_KEY` nos secrets
5. Deploy automático!

### Docker

```bash
# Criar imagem
docker build -t jornada-agentica .

# Executar
docker run -p 8501:8501 jornada-agentica
```

---

**Documentação**: README.md | CONCEITOS.md | QUICKSTART.md
