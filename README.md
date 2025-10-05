# 🤖 Jornada Agêntica - Sistema de Troca de Produtos

MVP de sistema agêntico para automação de processos de backoffice de varejo, focado em trocas de produtos.

> **🌐 NOVIDADE**: Agora com interface web interativa! Execute `streamlit run app.py` para usar no browser.

## Visão Geral

Este projeto implementa uma **jornada agêntica completa** usando **LangChain + Groq** para automatizar o processo de análise e aprovação de trocas de produtos em um contexto de varejo.

### Problema Resolvido

Empresas de varejo enfrentam desafios em suas operações de backoffice:
- **TMA Alto**: Tempo médio de atendimento de até 2 semanas
- **Custo Elevado**: R$ 130 por protocolo
- **Processos Manuais**: Muitos analistas fazendo tarefas repetitivas
- **Erros Humanos**: Falhas em validações críticas

### Solução

Sistema agêntico que executa automaticamente as 6 etapas do processo de troca:

```
Nova Solicitação → Validação Cliente → Análise Documentos →
Validação Elegibilidade → Classificação Troca → [Estoque] → Decisão Final
```

## Arquitetura

### Componentes Principais

```
agentic-playground/
├── src/
│   ├── agents/              # 6 Agents especializados + Custom Parser
│   │   ├── customer_validator_agent.py
│   │   ├── document_analyzer_agent.py
│   │   ├── eligibility_validator_agent.py
│   │   ├── exchange_classifier_agent.py
│   │   ├── inventory_validator_agent.py
│   │   ├── decision_agent.py
│   │   └── output_parser_fix.py  # Parser robusto para JSON
│   ├── tools/               # LangChain Tools
│   │   ├── customer_tools.py
│   │   ├── inventory_tools.py
│   │   └── document_tools.py
│   ├── mocks/               # Mock de APIs
│   │   ├── api_cliente.py
│   │   └── api_estoque.py
│   ├── data/
│   │   └── synthetic_docs/  # Documentos sintéticos
│   └── orchestrator.py      # Orquestrador da jornada
├── examples/
│   └── run_exchange_journey.py  # 4 cenários de exemplo
├── README.md                # Documentação principal
├── CONCEITOS.md             # Explicação dos conceitos
├── QUICKSTART.md            # Guia rápido de 3 passos
└── requirements.txt         # Dependências Python
```

### Agents Especializados

| Agent | Responsabilidade | Tools Usadas |
|-------|------------------|--------------|
| CustomerValidator | Valida identidade do cliente | consultar_cliente, validar_dados_cliente |
| DocumentAnalyzer | Extrai dados de documentos | analisar_nota_fiscal |
| EligibilityValidator | Valida regras de elegibilidade | consultar_regras_elegibilidade, validar_prazo_troca |
| ExchangeClassifier | Classifica tipo de troca | Nenhuma (raciocínio puro) |
| InventoryValidator | Valida e reserva estoque | consultar_produto, verificar_disponibilidade, reservar_produto |
| DecisionAgent | Decisão final consolidada | Nenhuma (análise de resultados) |

## Setup

### Pré-requisitos

- Python 3.9+
- Conta Groq (API Key gratuita em https://console.groq.com)

### Instalação

```bash
# 1. Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 2. Instale dependências
pip install -r requirements.txt

# 3. Configure .env
cp .env.example .env
# Edite .env e adicione sua GROQ_API_KEY
```

Obtenha sua API key gratuita em: https://console.groq.com/keys

**Veja guia detalhado em [QUICKSTART.md](./QUICKSTART.md)**

## Como Usar

### 🌐 Interface Web (Recomendado)

Execute a interface web com **Streamlit**:

```bash
streamlit run app.py
```

Acesse no browser: **http://localhost:8501**

**Funcionalidades:**
- ✅ Interface visual para criar solicitações
- 🎯 4 cenários pré-configurados
- 📊 Visualização em tempo real da jornada
- 🔍 Detalhes expandíveis de cada agent
- 📈 Métricas e status coloridos

**Veja guia completo em [RUN_WEB.md](./RUN_WEB.md)**

### 💻 Exemplo via Código

```python
from src.orchestrator import ExchangeJourneyOrchestrator

# Dados do protocolo de troca
protocolo = {
    "protocolo": "TROCA-2024-98765",
    "cliente": {
        "cpf": "123.456.789-00",
        "nome": "João Silva Santos",
        "email": "joao.silva@email.com"
    },
    "produto_original": {
        "codigo": "PROD-001",
        "descricao": "Smartphone XYZ Pro",
        "data_compra": "2025-09-20"
    },
    "motivo_troca": "produto_defeituoso",
    "descricao_problema": "Tela preta, não liga",
    "tipo_troca_desejado": "troca_outro_produto",
    "produto_desejado": {
        "codigo": "PROD-003",
        "descricao": "Fone Bluetooth Premium"
    }
}

# Executa jornada
orchestrator = ExchangeJourneyOrchestrator()
resultado = orchestrator.execute_journey(protocolo)

# Salva relatório
orchestrator.save_journey_report(resultado)
```

### 📝 Executando via Script Python

```bash
cd examples
python run_exchange_journey.py
```

Este script executa 4 cenários e gera arquivos JSON:
1. Troca Aprovada - Produto defeituoso, todos os requisitos OK
2. Troca Rejeitada - Fora do prazo
3. Sem Estoque - Produto desejado indisponível
4. Dados Inválidos - Falha na validação de cliente

**Melhor usar a interface web para visualização interativa!**

## Conceitos de AI Engineering Aplicados

Este projeto é uma demonstração educacional de padrões e conceitos modernos:

### Técnicas Implementadas

1. **ReAct Pattern** - Agents que raciocinam e agem
2. **LangChain Tools** - Interface com sistemas externos
3. **Specialized Agents** - Decomposição em agents especializados
4. **Orchestration** - Coordenação de múltiplos agents
5. **RAG** (Retrieval Augmented Generation) - Acesso a documentos
6. **Prompt Engineering** - Prompts estruturados e eficazes
7. **Conditional Workflows** - Lógica condicional na jornada
8. **Error Handling** - Tratamento gracioso de erros
9. **Observability** - Logging e auditoria completa
10. **Temperature Control** - Determinismo em decisões críticas
11. **Custom Output Parser** - Parser robusto para JSON mal formatado
12. **Early Stopping** - Prevenção de loops infinitos

**Leia [CONCEITOS.md](./CONCEITOS.md) para explicação detalhada de cada conceito**

## Estrutura Didática

### Para Aprender:

1. **Comece pelos Mocks**: `src/mocks/` - Veja como simulamos APIs
2. **Entenda as Tools**: `src/tools/` - Como agents interagem com sistemas
3. **Estude os Agents**: `src/agents/` - Um por vez, começando pelo CustomerValidator
4. **Analise o Orchestrator**: `src/orchestrator.py` - Como tudo se conecta
5. **Execute os Exemplos**: `examples/` - Veja na prática

### Para Experimentar:

- Modifique os prompts dos agents
- Adicione novas tools
- Crie novos cenários de teste
- Altere regras de elegibilidade
- Adicione produtos no mock de estoque

## Saída do Sistema

Cada execução gera:

1. **Console Output**: Log detalhado de cada etapa
2. **JSON Report**: Arquivo completo com todas as etapas executadas

## Observability

### Verbose Mode

O sistema mostra o raciocínio dos agents em tempo real:

```
> Entering new AgentExecutor chain...
Thought: Preciso validar os dados do cliente usando a tool apropriada
Action: validar_dados_cliente
Action Input: {"cpf": "123.456.789-00", "nome": "João Silva Santos"}
Observation: VALIDAÇÃO APROVADA...
```

### Journey Logs

Cada etapa é registrada com timestamp e detalhes completos para auditoria.

## Segurança e Validações

O sistema implementa múltiplas camadas de validação:

1. **Validação de Identidade** - CPF, nome e email devem conferir
2. **Validação de Documentos** - Nota fiscal legível e válida
3. **Validação de Prazo** - Dentro do período permitido
4. **Validação de Elegibilidade** - Conforme políticas da empresa
5. **Validação de Estoque** - Produto disponível antes de reservar

Qualquer falha interrompe a jornada e rejeita a troca.

## Casos de Uso

### Cenários Suportados

- Troca por produto defeituoso
- Troca por outro produto
- Vale compra
- Validação de prazo por categoria
- Reserva automática de estoque
- Interrupção em caso de dados inválidos

### Categorias de Produtos

- Eletrônicos (90 dias para defeito, 30 para troca)
- Áudio (90 dias para defeito, 15 para troca)
- Informática (90 dias para defeito, 30 para troca)

## Customização

### Adicionar Nova Categoria

1. Edite `src/data/synthetic_docs/regras_elegibilidade.md`
2. Adicione regras específicas
3. Atualize `ValidarPrazoTrocaTool` em `document_tools.py`

### Adicionar Novo Agent

1. Crie arquivo em `src/agents/novo_agent.py`
2. Defina tools necessárias
3. Crie prompt específico
4. Adicione ao orchestrator

### Adicionar Nova Tool

1. Crie função privada (ex: `_minha_tool`) em `src/tools/categoria_tools.py`
2. Crie schema Pydantic para os argumentos
3. Use `StructuredTool.from_function()` para criar a tool
4. Adicione ao getter correspondente (ex: `get_customer_tools()`)

## Métricas e Performance

### Tempo de Execução Típico

- Validação Cliente: ~2-3s
- Análise Documentos: ~3-4s
- Validação Elegibilidade: ~4-5s
- Classificação: ~2-3s
- Validação Estoque: ~3-4s
- Decisão Final: ~2-3s

**Total: ~15-25s** (vs. 2 semanas manual!)

### Custos

Com Groq (free tier):
- ~5000 tokens por jornada
- Praticamente zero custo em uso moderado

## Limitações Atuais (MVP)

- Mocks ao invés de APIs reais
- Análise de imagem não implementada (apenas simulada)
- Sem persistência em banco de dados
- Sem interface de usuário
- Sem autenticação/autorização
- Documentos sintéticos (não lê PDFs reais)

## Próximos Passos

### Features Planejadas

- ✅ **Interface web (Streamlit)** - IMPLEMENTADO!
- Integração com APIs reais
- Análise de imagens (OCR de documentos)
- Banco de dados (PostgreSQL)
- Notificações (email/SMS)
- Dashboard de métricas avançado
- Human-in-the-loop para casos duvidosos
- A/B testing de prompts
- LangGraph para workflows mais complexos
- Deploy em cloud (Streamlit Cloud/Railway)

## Licença

MIT License - Sinta-se livre para usar em projetos educacionais ou comerciais.

## Suporte

- **Interface Web**: [RUN_WEB.md](./RUN_WEB.md) - Como usar a interface Streamlit
- **Início Rápido**: [QUICKSTART.md](./QUICKSTART.md) - Guia de 3 passos
- **Conceitos**: [CONCEITOS.md](./CONCEITOS.md) - Explicação detalhada dos conceitos
- **Exemplos**: `examples/run_exchange_journey.py` - 4 cenários via script
- **Issues**: Abra uma issue no GitHub

## Agradecimentos

- **LangChain**: Framework incrível para AI agents
- **Groq**: API rápida e gratuita
- **Anthropic**: Conceitos de AI engineering

---

**Desenvolvido como MVP educacional para workshop de AI Agents**

**Stack**: Python · LangChain · Groq · Pydantic
