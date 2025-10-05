"""
Agent especializado em validação de elegibilidade

CONCEITO - Business Rules Engine:
Este agent atua como um motor de regras de negócio inteligente,
consultando políticas da empresa e aplicando-as ao caso específico.
"""

from langchain.agents import AgentExecutor, create_react_agent
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import sys

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.document_tools import get_document_tools
from agents.output_parser_fix import RobustJSONAgentOutputParser


class EligibilityValidatorAgent:
    """
    Agent responsável por validar elegibilidade da troca

    Função na Jornada:
    - Etapa 3: Validação de elegibilidade de troca
    - Consulta regras de elegibilidade da categoria
    - Valida prazo de troca
    - Verifica condições do produto
    - Valida motivo da troca
    """

    def __init__(self, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0):
        """Inicializa o agent de validação de elegibilidade"""
        self.llm = ChatGroq(
            model=model_name,
            temperature=temperature,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        self.tools = get_document_tools()

        self.prompt = PromptTemplate.from_template("""
Você é um Agent Especialista em Validação de Elegibilidade de Trocas.

CONTEXTO:
Você é o terceiro agent na jornada. Seu trabalho é CRÍTICO pois você determina
se a troca solicitada está de acordo com as políticas da empresa. Você previne
trocas indevidas que causariam prejuízo.

SUA MISSÃO:
Validar se a troca solicitada atende TODOS os critérios de elegibilidade:
1. Prazo correto para categoria e tipo de troca
2. Condições do produto adequadas
3. Motivo da troca válido
4. Documentação completa

PROCEDIMENTO OBRIGATÓRIO:
1. Use "consultar_regras_elegibilidade" UMA VEZ para buscar regras
2. Use "validar_prazo_troca" UMA VEZ para verificar prazo
3. Analise os resultados no seu raciocínio (Thought)
4. Vá direto para Final Answer com a decisão

CRITÉRIOS CRÍTICOS (todos obrigatórios):
- Prazo de troca respeitado
- Categoria do produto identificada corretamente
- Tipo de troca permitido para a categoria
- Motivo válido segundo as regras
- Documentação completa (nota fiscal válida)

REGRAS IMPORTANTES:
- Use cada tool APENAS UMA VEZ
- NÃO tente revalidar se o resultado for negativo
- Se validar_prazo_troca retornar EXPIRADO, aceite o resultado e REJEITE a troca
- Após receber Observations, vá direto para "Thought: I now know the final answer"
- NÃO fique em loop tentando usar as mesmas tools repetidamente
- Seja RIGOROSO: prefira rejeitar do que aprovar indevidamente

TOOLS DISPONÍVEIS:
{tools}

TOOL NAMES: {tool_names}

FORMATO DE RESPOSTA (obrigatório):
Thought: [preciso consultar regras]
Action: consultar_regras_elegibilidade
Action Input: {{"categoria_produto": "Eletrônicos", "tipo_troca": "produto_defeituoso"}}
Observation: [resultado das regras]
Thought: [agora preciso validar prazo]
Action: validar_prazo_troca
Action Input: {{"data_compra": "2025-09-20", "categoria": "Eletrônicos", "tipo_troca": "produto_defeituoso"}}
Observation: [resultado do prazo]
Thought: [analiso os resultados - se prazo EXPIRADO, devo reprovar]
Thought: I now know the final answer
Final Answer: [resposta estruturada]

IMPORTANTE:
- Action Input deve ser JSON válido
- Use cada tool APENAS UMA VEZ
- Após receber as 2 Observations, vá para Final Answer
- NÃO tente usar as tools novamente

FORMATO DA RESPOSTA FINAL:
---
STATUS: [APROVADO/REPROVADO]
CATEGORIA: [categoria validada]
TIPO_TROCA: [tipo de troca]
PRAZO_VALIDO: [SIM/NAO]
MOTIVO_VALIDO: [SIM/NAO]
CRITERIOS_ATENDIDOS: [lista dos critérios que passaram]
CRITERIOS_NAO_ATENDIDOS: [lista dos critérios que falharam, se houver]
JUSTIFICATIVA: [explicação da decisão]
PODE_PROSSEGUIR: [SIM/NAO]
---

DADOS PARA VALIDAÇÃO:
{input}

{agent_scratchpad}
""")

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
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,  # 2 tools + Final Answer
            early_stopping_method="force"  # Para evitar loops
        )

    def validate(self, protocolo_data: dict, dados_documento: dict) -> dict:
        """
        Valida elegibilidade da troca

        Args:
            protocolo_data: Dados do protocolo
            dados_documento: Dados extraídos da análise de documentos

        Returns:
            Resultado da validação de elegibilidade
        """
        produto_original = protocolo_data.get("produto_original", {})

        input_text = f"""
Protocolo: {protocolo_data.get('protocolo', 'N/A')}

Dados do Produto:
- Código: {produto_original.get('codigo', 'N/A')}
- Descrição: {produto_original.get('descricao', 'N/A')}
- Data da Compra: {dados_documento.get('data_compra', produto_original.get('data_compra', 'N/A'))}
- Categoria: {dados_documento.get('categoria', 'N/A')}

Tipo de Troca Solicitado: {protocolo_data.get('tipo_troca_desejado', 'N/A')}

Motivo da Troca: {protocolo_data.get('motivo_troca', 'N/A')}
Descrição do Problema: {protocolo_data.get('descricao_problema', 'N/A')}

Por favor, valide se esta troca atende todos os critérios de elegibilidade.
Seja rigoroso e verifique TODOS os requisitos.
"""

        resultado = self.agent_executor.invoke({"input": input_text})
        output = resultado.get("output", "")

        aprovado = "STATUS: APROVADO" in output or "PODE_PROSSEGUIR: SIM" in output

        return {
            "agent": "EligibilityValidator",
            "status": "aprovado" if aprovado else "reprovado",
            "output": output,
            "raw_result": resultado
        }


def validar_elegibilidade(protocolo_data: dict, dados_documento: dict) -> dict:
    """Função helper para validação de elegibilidade"""
    agent = EligibilityValidatorAgent()
    return agent.validate(protocolo_data, dados_documento)
