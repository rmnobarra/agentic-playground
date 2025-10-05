"""
Agent especializado em validação de estoque

CONCEITO - Conditional Agent:
Este agent só é acionado em condições específicas (quando requer validação de estoque).
Demonstra como criar workflows condicionais na jornada agêntica.
"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import sys

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.inventory_tools import get_inventory_tools
from agents.output_parser_fix import RobustJSONAgentOutputParser


class InventoryValidatorAgent:
    """
    Agent responsável por validar estoque

    Função na Jornada:
    - Etapa 5: Validação de estoque (condicional)
    - Verifica disponibilidade do produto desejado
    - Reserva o produto se disponível
    - Acionado apenas se tipo_troca = troca_outro_produto
    """

    def __init__(self, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0):
        """Inicializa o agent de validação de estoque"""
        self.llm = ChatGroq(
            model=model_name,
            temperature=temperature,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        self.tools = get_inventory_tools()

        self.output_parser = RobustJSONAgentOutputParser()

        self.prompt = PromptTemplate.from_template("""
Você é um Agent Especialista em Gestão de Estoque para Trocas.

CONTEXTO:
Você é acionado quando o cliente quer trocar por outro produto específico.
Seu trabalho é verificar se o produto desejado está disponível e reservá-lo.

SUA MISSÃO:
1. Verificar se o produto desejado existe no catálogo
2. Verificar se há quantidade disponível em estoque
3. Se disponível, RESERVAR o produto para o protocolo
4. Se indisponível, informar claramente

PROCEDIMENTO OBRIGATÓRIO:
1. Use "consultar_produto" para obter detalhes do produto desejado
2. Use "verificar_disponibilidade" para confirmar estoque livre
3. Se disponível, use "reservar_produto" para criar a reserva
4. Anote o ID da reserva criada

REGRAS IMPORTANTES:
- SEMPRE verifique disponibilidade ANTES de tentar reservar
- Se produto não existir, informe que precisa oferecer alternativa
- Se estoque zerado, informe para oferecer produto similar ou vale
- SEMPRE crie a reserva se houver estoque (não deixe para depois)
- Guarde o ID da reserva na resposta final

TOOLS DISPONÍVEIS:
{tools}

TOOL NAMES: {tool_names}

FORMATO DE RESPOSTA (obrigatório):
Thought: [seu raciocínio]
Action: [nome da tool]
Action Input: [JSON válido, exemplo: {{"codigo_produto": "PROD-001", "quantidade": 1, "protocolo": "TROCA-123"}}]
Observation: [resultado]
... (repita)
Thought: I now know the final answer
Final Answer: [resposta estruturada]

IMPORTANTE: Action Input deve ser JSON válido.

FORMATO DA RESPOSTA FINAL:
---
STATUS: [DISPONIVEL/INDISPONIVEL]
PRODUTO_CODIGO: [código do produto]
PRODUTO_NOME: [nome do produto]
QUANTIDADE_LIVRE: [quantidade disponível]
RESERVA_ID: [ID da reserva criada, se aplicável]
PODE_PROSSEGUIR: [SIM/NAO]
OBSERVACOES: [informações adicionais]
---

DADOS DO PROTOCOLO:
{input}

{agent_scratchpad}
""")

        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
            output_parser=self.output_parser
        )

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=6
        )

    def validate(self, protocolo_data: dict) -> dict:
        """
        Valida estoque do produto desejado

        Args:
            protocolo_data: Dados do protocolo

        Returns:
            Resultado da validação de estoque
        """
        produto_desejado = protocolo_data.get("produto_desejado", {})

        input_text = f"""
Protocolo: {protocolo_data.get('protocolo', 'N/A')}

Produto Desejado pelo Cliente:
- Código: {produto_desejado.get('codigo', 'N/A')}
- Descrição: {produto_desejado.get('descricao', 'N/A')}

Quantidade Necessária: 1 unidade

Por favor, verifique a disponibilidade e, se possível, reserve o produto.
"""

        resultado = self.agent_executor.invoke({"input": input_text})
        output = resultado.get("output", "")

        disponivel = "STATUS: DISPONIVEL" in output or "PODE_PROSSEGUIR: SIM" in output

        # Extrai ID da reserva
        reserva_id = None
        for line in output.split("\n"):
            if "RESERVA_ID:" in line:
                reserva_id = line.split(":", 1)[1].strip()

        return {
            "agent": "InventoryValidator",
            "status": "disponivel" if disponivel else "indisponivel",
            "reserva_id": reserva_id,
            "output": output,
            "raw_result": resultado
        }


def validar_estoque(protocolo_data: dict) -> dict:
    """Função helper para validação de estoque"""
    agent = InventoryValidatorAgent()
    return agent.validate(protocolo_data)
