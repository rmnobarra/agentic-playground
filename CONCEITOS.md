# Conceitos Fundamentais de AI Engineering Aplicados

Este documento explica os 17 conceitos de AI Engineering implementados no MVP de Jornada Agêntica de Troca de Produtos.

## Índice de Conceitos

1. **LangChain Framework** - Framework para aplicações com LLMs
2. **ReAct Pattern** - Reasoning + Acting para agents autônomos
3. **Tools** - Interface entre LLMs e sistemas externos
4. **Specialized Agents** - Decomposição em agents especializados
5. **Orchestration Pattern** - Coordenação de múltiplos agents
6. **RAG** - Retrieval Augmented Generation
7. **Prompt Engineering** - Design de prompts eficazes
8. **Temperature & Determinismo** - Controle de aleatoriedade
9. **Error Handling** - Tratamento robusto de erros
10. **Observability** - Logging e auditoria
11. **Separation of Concerns** - Modularização e responsabilidades
12. **Custom Output Parser** - Parser robusto para JSON
13. **Early Stopping** - Prevenção de loops infinitos
14. **Conditional Workflows** - Lógica condicional na jornada
15. **Pydantic Schemas** - Validação de dados estruturados
16. **Mock Services** - Simulação para testes
17. **Facade Pattern** - Interface simplificada

---

## 1. LangChain Framework

### O que é?
LangChain é um framework para desenvolver aplicações alimentadas por LLMs (Large Language Models). Ele fornece abstrações e componentes para:
- Conectar LLMs a fontes de dados externas
- Criar chains (sequências) de operações
- Gerenciar memória e contexto
- Implementar agents autônomos

### Como usamos no projeto?
- **Tools**: Encapsulamos APIs e funções em LangChain Tools
- **Agents**: Criamos agents ReAct que usam as tools
- **Prompts**: Templates estruturados para guiar o comportamento dos agents
- **LLM Integration**: Integração com Groq API para execução dos modelos

**Arquivos principais**: `src/tools/*`, `src/agents/*`

---

## 2. ReAct Pattern (Reasoning + Acting)

### O que é?
ReAct é um padrão onde o LLM alterna entre raciocínio e ação:

```
Thought → Action → Observation → Thought → Action → ...
```

1. **Thought**: O LLM raciocina sobre o que fazer
2. **Action**: Escolhe e executa uma tool
3. **Observation**: Analisa o resultado da tool
4. **Repeat**: Continua até completar a tarefa

### Por que é importante?
- Permite que agents trabalhem de forma autônoma
- Torna o processo de decisão transparente e auditável
- Possibilita que o LLM use tools de forma inteligente

### Exemplo no código:
```python
# src/agents/customer_validator_agent.py
self.agent = create_react_agent(
    llm=self.llm,
    tools=self.tools,
    prompt=self.prompt  # Define o formato ReAct
)
```

**Saída observável**: Quando você executa, vê o agent "pensando" antes de cada ação

---

## 3. Tools (Ferramentas)

### O que são?
Tools são componentes que permitem aos LLMs interagir com sistemas externos. Cada tool tem:
- **Nome**: Identificador único
- **Descrição**: Explica o que faz (o LLM lê isso!)
- **Schema de Input**: Parâmetros esperados
- **Função de Execução**: Código que realmente executa

### Tipos de Tools no Projeto:

#### 3.1 Customer Tools (`customer_tools.py`)
- `consultar_cliente`: Busca dados do cliente
- `validar_dados_cliente`: Valida se dados conferem

#### 3.2 Inventory Tools (`inventory_tools.py`)
- `consultar_produto`: Busca informações de produto
- `verificar_disponibilidade`: Checa estoque
- `reservar_produto`: Cria reserva (modifica estado!)

#### 3.3 Document Tools (`document_tools.py`)
- `analisar_nota_fiscal`: Extrai dados de documentos
- `consultar_regras_elegibilidade`: Acessa base de conhecimento
- `validar_prazo_troca`: Calcula prazos

### Conceito Importante: Tool Selection
O LLM lê as DESCRIÇÕES das tools e decide autonomamente qual usar. Por isso, descrições claras são críticas!

```python
description = """
Útil para validar se os dados fornecidos pelo cliente conferem com o cadastro.
Verifica CPF, nome e email. IMPORTANTE: Use esta tool para garantir a segurança
da operação antes de prosseguir com qualquer troca.
"""
```

---

## 4. Specialized Agents (Agents Especializados)

### Arquitetura de Múltiplos Agents

Ao invés de um único agent tentando fazer tudo, dividimos em agents especializados:

```
┌─────────────────────────────────────────────────────────┐
│                    JORNADA COMPLETA                     │
└─────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│ 1. CustomerValidator│ ──► Valida identidade do cliente
└─────────────────────┘
           │
           ▼
┌─────────────────────┐
│ 2. DocumentAnalyzer │ ──► Extrai dados de documentos
└─────────────────────┘
           │
           ▼
┌────────────────────────┐
│ 3. EligibilityValidator│ ──► Valida regras de elegibilidade
└────────────────────────┘
           │
           ▼
┌──────────────────────┐
│ 4. ExchangeClassifier│ ──► Classifica tipo de troca
└──────────────────────┘
           │
           ▼
┌──────────────────────┐
│ 5. InventoryValidator│ ──► Valida estoque (condicional)
└──────────────────────┘
           │
           ▼
┌─────────────────────┐
│ 6. DecisionAgent    │ ──► Decisão final
└─────────────────────┘
```

### Vantagens desta Abordagem:

1. **Separation of Concerns**: Cada agent tem uma responsabilidade clara
2. **Prompts Focados**: Instruções específicas para cada tarefa
3. **Debugging Facilitado**: Isola problemas em etapas específicas
4. **Reutilização**: Agents podem ser usados em outras jornadas
5. **Testing**: Testa cada agent independentemente

### Exemplo de Especialização:

```python
# CustomerValidatorAgent
# Foco: Segurança e validação de identidade
# Tools: customer_tools
# Temperatura: 0 (determinístico)

# ExchangeClassifierAgent
# Foco: Classificação inteligente
# Tools: Nenhuma (só raciocínio)
# Temperatura: 0.1 (leve criatividade)
```

---

## 5. Orchestration Pattern (Orquestração)

### O que é?
O Orchestrator coordena a execução de múltiplos agents em uma sequência lógica.

### Responsabilidades do Orchestrator:

1. **Sequenciamento**: Executa agents na ordem correta
2. **Data Flow**: Passa resultados entre agents
3. **Conditional Logic**: Decide se pula ou executa etapas
4. **Error Handling**: Trata erros e interrompe quando necessário
5. **Logging**: Mantém auditoria completa

### Fluxo Condicional:

```python
# Exemplo de lógica condicional
if resultado_classificacao.get("requer_validacao_estoque"):
    # Só executa InventoryValidator se necessário
    resultado_estoque = self.inventory_validator.validate(...)
else:
    # Pula esta etapa
    resultado_estoque = None
```

**Arquivo**: `src/orchestrator.py`

---

## 6. RAG (Retrieval Augmented Generation)

### O que é?
RAG combina recuperação de informações com geração de texto pelo LLM.

### Como implementamos:

#### Caso 1: Regras de Elegibilidade
```python
# Tool lê documento markdown com regras
with open(arquivo_regras, 'r') as f:
    regras = f.read()

# LLM usa essas regras para tomar decisão
return f"REGRAS: {regras}"
```

#### Caso 2: Análise de Nota Fiscal
```python
# Tool extrai dados estruturados de JSON
nota = json.load(arquivo_nota)

# LLM analisa e valida os dados
return f"Nota: {numero}, Data: {data}, Valor: {valor}"
```

### Por que RAG é importante?
- LLMs têm conhecimento limitado (cutoff date)
- RAG permite acesso a dados atualizados e específicos da empresa
- Fundamenta decisões em documentos/políticas reais

---

## 7. Prompt Engineering

### O que é?
Arte e ciência de escrever prompts eficazes para guiar o comportamento do LLM.

### Técnicas Aplicadas:

#### 7.1 Role Assignment
```python
"""
Você é um Agent Especialista em Validação de Clientes
para um sistema de backoffice de varejo.
"""
```
Define persona e contexto profissional.

#### 7.2 Clear Instructions
```python
"""
PROCEDIMENTO OBRIGATÓRIO:
1. Receba os dados do cliente
2. Use a tool "validar_dados_cliente"
3. Se NÃO conferirem, REJEITE
4. Se conferirem, confirme
"""
```
Passos explícitos e ordenados.

#### 7.3 Output Formatting
```python
"""
FORMATO DA RESPOSTA FINAL:
---
STATUS: [APROVADO/REPROVADO]
CLIENTE: [nome]
MOTIVO: [se reprovado]
---
"""
```
Garante saída estruturada e parseável.

#### 7.4 Constraints e Rules
```python
"""
REGRAS IMPORTANTES:
- NUNCA prossiga sem validar
- Se houver QUALQUER inconsistência, rejeite
- Seja claro nos motivos
"""
```
Define limites e comportamentos críticos.

#### 7.5 Few-Shot Learning (implícito nos formatos)
Mostramos exemplos do formato esperado para guiar o LLM.

---

## 8. Temperature e Determinismo

### O que é Temperature?
Parâmetro que controla aleatoriedade do LLM:
- **0.0**: Sempre escolhe a opção mais provável (determinístico)
- **1.0+**: Mais criativo e variado

### Nossa Estratégia:

```python
# Validações críticas (segurança, elegibilidade)
temperature=0  # Máximo determinismo

# Classificação (permite interpretação)
temperature=0.1  # Leve flexibilidade
```

### Por que isso importa?
Em sistemas de produção, consistência é crucial. Temperature=0 garante que o mesmo input gere o mesmo output.

---

## 9. Error Handling e Graceful Degradation

### Estratégias Implementadas:

#### 9.1 Early Stopping
```python
if resultado_cliente["status"] == "reprovado":
    # Interrompe jornada imediatamente
    return self._finalize_journey(resultados)
```

#### 9.2 Try-Catch com Fallback
```python
try:
    resultado = self.agent_executor.invoke(...)
except Exception as e:
    # Registra erro e finaliza gracefully
    resultados["erro"] = str(e)
    return self._finalize_journey(resultados)
```

#### 9.3 Max Iterations
```python
AgentExecutor(
    max_iterations=5  # Previne loops infinitos
)
```

#### 9.4 Parsing Error Handling
```python
handle_parsing_errors=True  # LangChain trata erros de formato
```

---

## 10. Observability e Auditoria

### Logging Estruturado:

```python
self.journey_log.append({
    "timestamp": datetime.now().isoformat(),
    "step": step_name,
    "status": status,
    "details": details
})
```

### Verbose Mode:
```python
AgentExecutor(verbose=True)
```
Mostra o raciocínio do agent em tempo real.

### Journey Reports:
Cada execução gera um JSON completo com:
- Todas as etapas executadas
- Resultados intermediários
- Decisão final
- Timestamps

**Benefícios**:
- Auditoria completa
- Debugging facilitado
- Análise de performance
- Compliance

---

## 11. Separation of Concerns na Arquitetura

### Camadas do Sistema:

```
┌─────────────────────────────────────┐
│     Orchestrator (Lógica de Negócio)│
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│     Agents (Decisões Inteligentes)  │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│     Tools (Interface com Sistema)   │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│     Mocks/APIs (Dados e Operações)  │
└─────────────────────────────────────┘
```

Cada camada tem responsabilidade clara e pode evoluir independentemente.

---

## 12. Custom Output Parser

### O que é?
Um parser customizado que lida com JSON mal formatado retornado pelo LLM.

### Problema que resolve:
LLMs às vezes geram JSON com problemas:
- Double-encoding: `{"cpf": "{\"cpf\":\"123\"}"}`
- Aspas extras ou faltantes
- Formatação inconsistente

### Solução implementada:

```python
# src/agents/output_parser_fix.py
class RobustJSONAgentOutputParser(AgentOutputParser):
    def _parse_json_robust(self, json_str: str) -> dict:
        # Estratégia 1: Parse direto
        try:
            return json.loads(json_str)
        except:
            pass

        # Estratégia 2: Remove aspas externas
        # Estratégia 3: Regex para extrair
        # Estratégia 4: Constrói dict manualmente
```

### Como usamos:

```python
self.output_parser = RobustJSONAgentOutputParser()
self.agent = create_react_agent(
    llm=self.llm,
    tools=self.tools,
    prompt=self.prompt,
    output_parser=self.output_parser  # Adiciona parser custom
)
```

**Arquivos**: Todos os agents em `src/agents/*_agent.py`

---

## 13. Early Stopping e Prevenção de Loops

### O que é?
Mecanismo para evitar que agents entrem em loops infinitos.

### Implementação:

```python
self.agent_executor = AgentExecutor(
    agent=self.agent,
    tools=self.tools,
    max_iterations=3,  # Limita número de ações
    early_stopping_method="force"  # Para ao atingir limite
)
```

### Estratégias aplicadas:
1. **max_iterations**: Limite de ações por agent
2. **Prompts claros**: "Use cada tool APENAS UMA VEZ"
3. **Early stopping**: Força parada quando necessário

### Por que é importante?
- Evita custos excessivos de API
- Previne timeouts
- Garante resposta em tempo razoável

---

## 14. Conditional Workflows

### Implementação de Lógica Condicional:

```python
# Etapa só executa sob certas condições
if resultado_classificacao.get("requer_validacao_estoque"):
    resultado_estoque = validar_estoque(...)
else:
    resultado_estoque = None  # Pula esta etapa
```

### Casos de Uso:
- Validação de estoque só para troca por outro produto
- Consultas adicionais só se primeira falhar
- Fluxos diferentes por categoria de produto

---

## 15. Pydantic Schemas

### O que é?
Validação de dados estruturados em Python.

### Como usamos:

```python
class ValidarDadosClienteInput(BaseModel):
    cpf: str = Field(description="CPF do cliente")
    nome: str = Field(description="Nome completo")
    email: str = Field(description="Email do cliente")
```

### Benefícios:
- Validação automática de inputs
- Type safety
- Documentação inline
- LangChain usa isso para gerar schemas

---

## 16. Mock Services para Testing

### Por que Mocks?
Permite testar sem dependências externas:
- APIs podem estar indisponíveis
- Dados de teste controlados
- Execução rápida
- Sem custos de API

### Implementação:
```python
# src/mocks/api_cliente.py
CLIENTES_DB = {
    "12345678900": {...}  # Dados sintéticos
}
```

Em produção, trocaríamos pelos clients reais das APIs.

---

## 17. Facade Pattern

### O que é?
Interface simplificada para sistemas complexos.

### Implementação:

```python
# Uso complexo
orchestrator = ExchangeJourneyOrchestrator()
resultado = orchestrator.execute_journey(protocolo)

# Facade simplificado
from orchestrator import executar_jornada_troca
resultado = executar_jornada_troca(protocolo)
```

Facilita adoção e uso do sistema.

---

## Resumo dos Conceitos por Arquivo

| Arquivo | Conceitos Principais |
|---------|---------------------|
| `tools/customer_tools.py` | Tools, Pydantic Schemas, StructuredTool |
| `tools/inventory_tools.py` | Stateful Tools, Side Effects |
| `tools/document_tools.py` | RAG, Knowledge Base, Document Understanding |
| `agents/output_parser_fix.py` | Custom Output Parser, Error Recovery |
| `agents/customer_validator_agent.py` | ReAct Agent, Prompt Engineering, Temperature |
| `agents/eligibility_validator_agent.py` | Business Rules Engine, Early Stopping |
| `agents/decision_agent.py` | Decision Agent, Consolidation |
| `orchestrator.py` | Orchestration, Conditional Workflows, Observability |
| `examples/run_exchange_journey.py` | End-to-End Testing, Multiple Scenarios |

---

## Melhores Práticas Aplicadas

1.  ✅ **Separation of Concerns**: Cada componente tem responsabilidade única
2.  ✅ **Error Handling**: Try-catch e graceful degradation
3.  ✅ **Observability**: Logging completo e verbose mode
4.  ✅ **Type Safety**: Pydantic para validação
5.  ✅ **Documentation**: Docstrings e comentários explicativos
6.  ✅ **Testing**: Múltiplos cenários de teste
7.  ✅ **Security**: Validações rigorosas antes de operações críticas
8.  ✅ **Auditability**: Journey logs completos
9.  ✅ **Modularity**: Componentes reutilizáveis
10. ✅ **Clarity**: Código autodocumentado

---

## Próximos Passos para Evolução

### Conceitos Avançados para Implementar:

1. **LangGraph**: State machines para workflows mais complexos
2. **Vector Stores**: Embeddings para RAG semântico
3. **Memory**: Histórico de conversas entre agents
4. **Streaming**: Respostas em tempo real
5. **Parallel Agents**: Execução simultânea de agents
6. **Human-in-the-Loop**: Aprovação humana em decisões críticas
7. **Fine-tuning**: Modelos customizados para domínio específico
8. **Evaluation**: Métricas de qualidade dos agents
9. **A/B Testing**: Comparar diferentes prompts/estratégias
10. **Production Monitoring**: APM para agents em produção

---

## Recursos para Aprofundamento

- **LangChain Docs**: https://python.langchain.com/
- **ReAct Paper**: https://arxiv.org/abs/2210.03629
- **Prompt Engineering Guide**: https://www.promptingguide.ai/
- **Groq API**: https://console.groq.com/docs
- **LangGraph**: https://langchain-ai.github.io/langgraph/

---

**Este documento é um guia vivo. À medida que o projeto evolui, novos conceitos serão adicionados.**
