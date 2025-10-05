"""
Agent especializado em validação de dados do cliente

CONCEITO - Specialized Agents:
Cada agent tem uma responsabilidade específica na jornada.
Isso permite prompts focados, melhor controle e facilita debugging.

CONCEITO - Zero-Shot ReAct Agent:
O ReAct (Reasoning + Acting) é um padrão onde o LLM:
1. PENSA (Reasoning): Analisa a situação e decide o próximo passo
2. AGE (Acting): Executa uma tool
3. OBSERVA: Analisa o resultado
4. REPETE: Até completar a tarefa

Este padrão permite que o agent trabalhe de forma autônoma,
tomando decisões baseadas em contexto.
"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import sys

# Carrega variáveis de ambiente
load_dotenv()

# Adiciona path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.customer_tools import get_customer_tools
from agents.output_parser_fix import RobustJSONAgentOutputParser


class CustomerValidatorAgent:
    """
    Agent responsável por validar dados do cliente

    Função na Jornada:
    - Etapa 1: Análise dos documentos do cliente
    - Valida se os dados informados conferem com o cadastro
    - Garante segurança antes de prosseguir
    """

    def __init__(self, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0):
        """
        Inicializa o agent

        Args:
            model_name: Modelo da Groq a usar (recomendado: llama-3.3-70b-versatile)
            temperature: Temperatura do modelo (0 = mais determinístico)

        CONCEITO - Temperature:
        Temperature controla a criatividade/aleatoriedade do modelo:
        - 0.0: Sempre escolhe a opção mais provável (determinístico)
        - 1.0+: Mais criativo e variado
        Para tarefas críticas como validação, usamos temperatura baixa.
        """
        self.llm = ChatGroq(
            model=model_name,
            temperature=temperature,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        self.tools = get_customer_tools()

        # Define o prompt do agent
        # CONCEITO - Prompt Engineering:
        # O prompt define o comportamento, personalidade e objetivos do agent
        self.prompt = PromptTemplate.from_template("""
Você é um Agent Especialista em Validação de Clientes para um sistema de backoffice de varejo.

CONTEXTO:
Você é o primeiro agent na jornada de troca de produtos. Sua responsabilidade é CRÍTICA
para a segurança da operação, pois você valida a identidade do cliente.

SUA MISSÃO:
Validar se os dados fornecidos pelo cliente no protocolo de troca conferem com o cadastro
no sistema da empresa.

PROCEDIMENTO OBRIGATÓRIO:
1. Use a tool "validar_dados_cliente" UMA ÚNICA VEZ com os dados fornecidos
2. Após receber a Observation, analise o resultado
3. Vá DIRETO para "Thought: I now know the final answer" e depois "Final Answer"
4. NÃO tente usar mais nenhuma tool após receber a validação

REGRAS IMPORTANTES:
- Use a tool validar_dados_cliente APENAS UMA VEZ
- Após receber o resultado, NÃO use mais nenhuma Action
- Vá direto para Final Answer com o resultado da validação
- NÃO tente criar Actions adicionais ou usar "Nenhuma ação"

TOOLS DISPONÍVEIS:
{tools}

TOOL NAMES: {tool_names}

FORMATO DE RESPOSTA (obrigatório):
Thought: Preciso validar os dados do cliente
Action: validar_dados_cliente
Action Input: {{"cpf": "123.456.789-00", "nome": "João Silva Santos", "email": "joao@email.com"}}
Observation: [resultado será preenchido automaticamente]
Thought: Baseado na validação recebida, [analise o resultado]
Thought: I now know the final answer
Final Answer: [resposta estruturada]

IMPORTANTE:
- Use validar_dados_cliente APENAS UMA VEZ
- Após receber a Observation, NÃO crie mais Actions
- Vá direto para Final Answer

FORMATO DA RESPOSTA FINAL:
Sempre retorne no formato:
---
STATUS: [APROVADO/REPROVADO]
CLIENTE: [nome do cliente]
CPF: [cpf]
MOTIVO: [se reprovado, explique o motivo]
PODE_PROSSEGUIR: [SIM/NAO]
---

PROTOCOLO ATUAL:
{input}

{agent_scratchpad}
""")

        # Cria o agent usando o padrão ReAct
        # CONCEITO - Agent Creation:
        # create_react_agent combina: LLM + Tools + Prompt
        # O agent_executor gerencia o loop de execução

        # CONCEITO - Custom Output Parser:
        # Usa parser customizado para lidar melhor com JSON mal formatado
        self.output_parser = RobustJSONAgentOutputParser()

        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
            output_parser=self.output_parser
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,  # Mostra o processo de raciocínio
            handle_parsing_errors=True,  # Trata erros de parsing graciosamente
            max_iterations=3,  # 1 tool + Final Answer
            early_stopping_method="force"  # Para evitar loops
        )

    def validate(self, protocolo_data: dict) -> dict:
        """
        Valida os dados do cliente a partir do protocolo

        Args:
            protocolo_data: Dicionário com dados do protocolo de troca

        Returns:
            Resultado da validação com status e detalhes

        CONCEITO - Structured Input:
        Recebemos dados estruturados (dict) mas passamos como texto
        para o LLM, que é melhor em processar linguagem natural.
        """
        # Extrai dados do cliente do protocolo
        cliente = protocolo_data.get("cliente", {})

        # Formata input para o agent
        input_text = f"""
Protocolo: {protocolo_data.get('protocolo', 'N/A')}

Dados do Cliente a Validar:
- CPF: {cliente.get('cpf', 'N/A')}
- Nome: {cliente.get('nome', 'N/A')}
- Email: {cliente.get('email', 'N/A')}

Por favor, valide se estes dados conferem com o cadastro do cliente no sistema.
"""

        # Executa o agent
        resultado = self.agent_executor.invoke({"input": input_text})

        # Processa a resposta
        output = resultado.get("output", "")

        # Determina se foi aprovado
        aprovado = "STATUS: APROVADO" in output or "PODE_PROSSEGUIR: SIM" in output

        return {
            "agent": "CustomerValidator",
            "status": "aprovado" if aprovado else "reprovado",
            "output": output,
            "raw_result": resultado
        }


# Função helper para uso standalone
def validar_cliente(protocolo_data: dict) -> dict:
    """
    Função helper para validar cliente

    CONCEITO - Facade Pattern:
    Simplifica o uso do agent para casos simples
    """
    agent = CustomerValidatorAgent()
    return agent.validate(protocolo_data)
