# Guia Rápido de Início

## Setup em 3 Passos

### 1. Instalar Dependências

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar pacotes
pip install langchain langchain-groq langchain-community python-dotenv pydantic
```

### 2. Configurar API Key

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env e adicionar sua chave
# GROQ_API_KEY=gsk_...
```

**Obter chave gratuita:** https://console.groq.com/keys

### 3. Executar Exemplo

```bash
cd examples
python run_exchange_journey.py
```

## Verificação Rápida

Teste se está funcionando:

```bash
python3 << 'EOF'
import sys
sys.path.append('src')

from mocks.api_cliente import APICliente

# Testa mock
resultado = APICliente.consultar_cliente("12345678900")
print("✓ Mock funcionando!" if resultado["status"] == "success" else "✗ Erro no mock")
EOF
```

## Primeiro Teste Simples

Crie um arquivo `test_simple.py`:

```python
import sys
import os
sys.path.append('src')
os.environ['GROQ_API_KEY'] = 'sua_chave_aqui'

from agents.customer_validator_agent import CustomerValidatorAgent

# Dados de teste
protocolo = {
    "protocolo": "TEST-001",
    "cliente": {
        "cpf": "123.456.789-00",
        "nome": "João Silva Santos",
        "email": "joao.silva@email.com"
    }
}

# Executa validação
agent = CustomerValidatorAgent()
resultado = agent.validate(protocolo)

print(f"\nStatus: {resultado['status']}")
print(f"\nSaída:\n{resultado['output']}")
```

Execute:
```bash
python test_simple.py
```

## Modelos Disponíveis

```python
# Mais rápido (recomendado para testes)
model_name = "llama3-8b-8192"

# Balanceado
model_name = "mixtral-8x7b-32768"

# Mais preciso (padrão)
model_name = "llama-3.3-70b-versatile"
```

Para mudar o modelo, edite o `__init__` dos agents em `src/agents/`.

## Estrutura Mínima

```
agentic-playground/
├── .env                    # Sua API key aqui
├── src/
│   ├── agents/            # 6 agents especializados
│   ├── tools/             # Tools do LangChain
│   ├── mocks/             # Simulação de APIs
│   └── orchestrator.py    # Orquestrador
└── examples/
    └── run_exchange_journey.py
```

## Testando Componentes

### Testar Mocks de API

```python
from src.mocks.api_cliente import APICliente
from src.mocks.api_estoque import APIEstoque

# Cliente
print(APICliente.consultar_cliente("12345678900"))

# Estoque
print(APIEstoque.consultar_produto("PROD-001"))
```

### Testar Tools

```python
from src.tools.customer_tools import get_customer_tools

tools = get_customer_tools()
print(f"Tools disponíveis: {[t.name for t in tools]}")
```

### Testar Agent Individual

```python
from src.agents.document_analyzer_agent import DocumentAnalyzerAgent

protocolo = {
    "protocolo": "TEST-001",
    "cliente": {"cpf": "123.456.789-00", "nome": "João Silva Santos"},
    "produto_original": {
        "codigo": "PROD-001",
        "descricao": "Smartphone XYZ Pro",
        "numero_nota_fiscal": "NF-2024-456789"
    },
    "documentos_anexados": [
        {"tipo": "nota_fiscal", "arquivo": "nota_fiscal_exemplo.json"}
    ]
}

agent = DocumentAnalyzerAgent()
resultado = agent.analyze(protocolo)
print(resultado)
```

## 🐛 Problemas Comuns

### Erro: "No module named 'langchain'"
```bash
pip install langchain langchain-groq
```

### Erro: "Model decommissioned"
Use modelo atualizado: `llama-3.3-70b-versatile`

### Erro: "field required"
Veja [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

### Erro: "Rate limit"
Aguarde alguns segundos entre requisições

## Próximos Passos

1. **Leia os conceitos:** [CONCEITOS.md](./CONCEITOS.md)
2. **Entenda a arquitetura:** [README.md](./README.md)
3. **Execute exemplos completos:** `cd examples && python run_exchange_journey.py`
4. **Customize:** Adicione produtos, regras e cenários

## Dicas

- Use `verbose=True` nos agents para ver o raciocínio
- Comece com modelos rápidos (`llama3-8b-8192`) para testes
- Analise os logs JSON gerados (`journey_report_*.json`)
- Modifique os prompts em `src/agents/` para ajustar comportamento

## Ajuda

- **Documentação completa:** [README.md](./README.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **Conceitos aplicados:** [CONCEITOS.md](./CONCEITOS.md)

---

**Pronto para começar!**
