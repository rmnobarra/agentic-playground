"""
Agent especializado em classificação do tipo de troca

CONCEITO - Classification Agent:
Este agent demonstra um padrão de classificação inteligente,
onde o LLM analisa contexto e categoriza a solicitação.
"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import sys

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.output_parser_fix import RobustJSONAgentOutputParser


class ExchangeClassifierAgent:
    """
    Agent responsável por caracterizar o tipo de troca

    Função na Jornada:
    - Etapa 4: Caracteriza tipo de troca
    - Analisa o motivo e classifica em:
      * produto_defeituoso
      * troca_outro_produto
      * vale_compra
    """

    def __init__(self, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0.1):
        """
        Inicializa o agent classificador

        CONCEITO - Temperature for Classification:
        Usamos temperatura ligeiramente maior (0.1) para permitir
        alguma flexibilidade na interpretação, mas ainda determinístico.
        """
        self.llm = ChatGroq(
            model=model_name,
            temperature=temperature,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        # Este agent não precisa de tools, apenas raciocínio
        self.tools = []

        self.output_parser = RobustJSONAgentOutputParser()

        self.prompt = PromptTemplate.from_template("""
Você é um Agent Especialista em Classificação de Tipos de Troca.

CONTEXTO:
Você é o quarto agent na jornada. Seu trabalho é analisar o motivo da troca
e classificá-la corretamente em uma das categorias permitidas.

SUA MISSÃO:
Classificar a troca em UMA das seguintes categorias:
1. PRODUTO_DEFEITUOSO: Produto com defeito de fabricação
2. TROCA_OUTRO_PRODUTO: Cliente quer trocar por outro produto diferente
3. VALE_COMPRA: Cliente prefere receber crédito/vale compra

CRITÉRIOS DE CLASSIFICAÇÃO:

PRODUTO_DEFEITUOSO:
- Produto não funciona
- Defeito de fabricação
- Produto quebrado/danificado (não por culpa do cliente)
- Produto não liga, tela com defeito, etc.

TROCA_OUTRO_PRODUTO:
- Cliente quer um produto diferente
- Arrependimento da compra
- Produto não atendeu expectativas
- Cliente especificou qual produto quer

VALE_COMPRA:
- Cliente não quer produto específico
- Prefere crédito para compra futura
- Explicitamente pediu vale/crédito

PROCEDIMENTO:
1. Leia o motivo da troca fornecido pelo cliente
2. Leia a descrição do problema
3. Analise qual categoria se encaixa melhor
4. Se o cliente especificou um produto desejado, é TROCA_OUTRO_PRODUTO
5. Se não especificou produto, analise se é defeito ou preferência por vale

REGRAS IMPORTANTES:
- Se houver menção a defeito/problema técnico = PRODUTO_DEFEITUOSO
- Se cliente mencionar produto específico que quer = TROCA_OUTRO_PRODUTO
- Se cliente não mencionar produto específico e não há defeito = VALE_COMPRA
- Em caso de dúvida entre defeituoso e outro produto, priorize a descrição do problema

TOOLS DISPONÍVEIS:
{tools}

TOOL NAMES: {tool_names}

FORMATO DE RESPOSTA (obrigatório):
Thought: [analise o motivo e a descrição]
Thought: [determine qual categoria se encaixa]
Thought: I now know the final answer
Final Answer: [resposta estruturada]

FORMATO DA RESPOSTA FINAL:
---
TIPO_TROCA_CLASSIFICADO: [PRODUTO_DEFEITUOSO/TROCA_OUTRO_PRODUTO/VALE_COMPRA]
CONFIANCA: [ALTA/MEDIA/BAIXA]
JUSTIFICATIVA: [explique por que classificou desta forma]
REQUER_ESTOQUE: [SIM/NAO - SIM se for troca por outro produto]
---

DADOS DA SOLICITAÇÃO:
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
            max_iterations=3  # Classificação é simples, poucas iterações
        )

    def classify(self, protocolo_data: dict) -> dict:
        """
        Classifica o tipo de troca

        Args:
            protocolo_data: Dados do protocolo

        Returns:
            Tipo de troca classificado
        """
        input_text = f"""
Protocolo: {protocolo_data.get('protocolo', 'N/A')}

Tipo de Troca Solicitado pelo Cliente: {protocolo_data.get('tipo_troca_desejado', 'N/A')}

Motivo da Troca: {protocolo_data.get('motivo_troca', 'N/A')}

Descrição do Problema: {protocolo_data.get('descricao_problema', 'N/A')}

Produto Desejado: {protocolo_data.get('produto_desejado', {}).get('descricao', 'Não especificado')}

Por favor, classifique esta troca na categoria apropriada.
"""

        resultado = self.agent_executor.invoke({"input": input_text})
        output = resultado.get("output", "")

        # Extrai tipo classificado
        tipo_troca = None
        requer_estoque = False

        for line in output.split("\n"):
            if "TIPO_TROCA_CLASSIFICADO:" in line:
                tipo_troca = line.split(":", 1)[1].strip()
            if "REQUER_ESTOQUE: SIM" in line:
                requer_estoque = True

        return {
            "agent": "ExchangeClassifier",
            "tipo_troca_classificado": tipo_troca,
            "requer_validacao_estoque": requer_estoque,
            "output": output,
            "raw_result": resultado
        }


def classificar_troca(protocolo_data: dict) -> dict:
    """Função helper para classificação de troca"""
    agent = ExchangeClassifierAgent()
    return agent.classify(protocolo_data)
