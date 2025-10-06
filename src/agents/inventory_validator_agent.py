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
1. Use "consultar_produto" APENAS UMA VEZ para obter detalhes do produto desejado
2. Após receber o resultado, analise:
   - Se produto NÃO EXISTE: vá direto para Final Answer com STATUS: INDISPONIVEL
   - Se produto EXISTE: use "verificar_disponibilidade" e depois "reservar_produto"
3. NÃO repita ações já executadas
4. Após completar (sucesso ou falha), vá para "Thought: I now know the final answer"

REGRAS IMPORTANTES:
- Use cada tool APENAS UMA VEZ
- Se produto não existir na primeira consulta, NÃO tente novamente
- Após receber "Produto não encontrado", vá DIRETO para Final Answer
- NUNCA use "N/A" como Action - isso não é uma tool válida
- Se não pode completar a tarefa, finalize mesmo assim com STATUS: INDISPONIVEL

TOOLS DISPONÍVEIS:
{tools}

TOOL NAMES: {tool_names}

FORMATO DE RESPOSTA (obrigatório):
Thought: [seu raciocínio]
Action: [nome da tool]
Action Input: [JSON válido, exemplo: {{"codigo_produto": "PROD-001"}}]
Observation: [resultado será preenchido]
Thought: [análise do resultado]
Thought: I now know the final answer
Final Answer: [resposta estruturada]

EXEMPLO - PRODUTO NÃO ENCONTRADO:
Thought: Preciso verificar se o produto existe
Action: consultar_produto
Action Input: {{"codigo_produto": "PROD-999"}}
Observation: Produto não encontrado
Thought: O produto PROD-999 não existe no catálogo, portanto está indisponível
Thought: I now know the final answer
Final Answer:
---
STATUS: INDISPONIVEL
PRODUTO_CODIGO: PROD-999
MOTIVO: Produto não encontrado no catálogo
PODE_PROSSEGUIR: NAO
OBSERVACOES: Produto inexistente. Sugerir alternativas ou vale compra.
---

EXEMPLO - PRODUTO DISPONÍVEL:
Thought: Preciso verificar se o produto existe
Action: consultar_produto
Action Input: {{"codigo_produto": "PROD-003"}}
Observation: Produto encontrado: Fone Bluetooth Premium, Preço: 299.90, Categoria: audio
Thought: Produto existe, agora verifico disponibilidade
Action: verificar_disponibilidade
Action Input: {{"codigo_produto": "PROD-003", "quantidade": 1}}
Observation: Disponível - 10 unidades livres
Thought: Produto disponível, vou reservar
Action: reservar_produto
Action Input: {{"codigo_produto": "PROD-003", "quantidade": 1, "protocolo": "TROCA-123"}}
Observation: Reserva criada - ID: RES-12345
Thought: I now know the final answer
Final Answer:
---
STATUS: DISPONIVEL
PRODUTO_CODIGO: PROD-003
PRODUTO_NOME: Fone Bluetooth Premium
QUANTIDADE_LIVRE: 10
RESERVA_ID: RES-12345
PODE_PROSSEGUIR: SIM
OBSERVACOES: Produto reservado com sucesso
---

FORMATO DA RESPOSTA FINAL:
---
STATUS: [DISPONIVEL/INDISPONIVEL]
PRODUTO_CODIGO: [código do produto]
PRODUTO_NOME: [nome do produto ou "N/A"]
QUANTIDADE_LIVRE: [quantidade disponível ou 0]
RESERVA_ID: [ID da reserva criada, ou "N/A"]
PODE_PROSSEGUIR: [SIM/NAO]
MOTIVO: [se indisponível, explique o motivo]
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
            max_iterations=4,  # Reduzido: 1 consulta + (2 verificação/reserva ou 1 finalização) + 1 final
            early_stopping_method="force"  # Para forçadamente ao atingir max_iterations
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

        # Verifica status - prioriza marcadores explícitos
        disponivel = False
        indisponivel = False

        if "STATUS: DISPONIVEL" in output or "PODE_PROSSEGUIR: SIM" in output:
            disponivel = True

        if "STATUS: INDISPONIVEL" in output or "PODE_PROSSEGUIR: NAO" in output or "não encontrado" in output.lower():
            indisponivel = True

        # Se ambos ou nenhum, usa lógica de reserva
        if not disponivel and not indisponivel:
            if "RESERVA_ID:" in output and "RES-" in output:
                disponivel = True
            else:
                indisponivel = True

        # Extrai ID da reserva
        reserva_id = None
        for line in output.split("\n"):
            if "RESERVA_ID:" in line:
                parts = line.split(":", 1)
                if len(parts) > 1:
                    reserva_id = parts[1].strip()
                    if reserva_id in ["N/A", "n/a", ""]:
                        reserva_id = None

        return {
            "agent": "InventoryValidator",
            "status": "disponivel" if disponivel and not indisponivel else "indisponivel",
            "reserva_id": reserva_id,
            "output": output,
            "raw_result": resultado
        }


def validar_estoque(protocolo_data: dict) -> dict:
    """Função helper para validação de estoque"""
    agent = InventoryValidatorAgent()
    return agent.validate(protocolo_data)
