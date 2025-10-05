"""
Agent especializado em análise de documentos

CONCEITO - Document Intelligence:
Este agent combina análise de documentos (nota fiscal) com validação
de regras de negócio, demonstrando como agents podem trabalhar com
informações não estruturadas.
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


class DocumentAnalyzerAgent:
    """
    Agent responsável por analisar documentos anexados

    Função na Jornada:
    - Etapa 2: Análise dos documentos anexados
    - Extrai informações da nota fiscal
    - Valida se os dados da nota conferem com o protocolo
    - Verifica integridade dos documentos
    """

    def __init__(self, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0):
        """Inicializa o agent de análise de documentos"""
        self.llm = ChatGroq(
            model=model_name,
            temperature=temperature,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        self.tools = get_document_tools()

        # Prompt especializado em análise de documentos
        self.prompt = PromptTemplate.from_template("""
Você é um Agent Especialista em Análise de Documentos para backoffice de varejo.

CONTEXTO:
Você é o segundo agent na jornada de troca. Seu trabalho é analisar os documentos
anexados pelo cliente (nota fiscal e fotos do produto) e extrair informações críticas
para as próximas etapas.

SUA MISSÃO:
1. Analisar a nota fiscal fornecida
2. Extrair dados importantes: produto, data de compra, valor, dados do cliente
3. Validar se os dados da nota conferem com os dados do protocolo
4. Identificar categoria do produto para próximas validações

PROCEDIMENTO OBRIGATÓRIO:
1. Use a tool "analisar_nota_fiscal" UMA ÚNICA VEZ para extrair dados
2. Após receber a Observation, analise os dados
3. Compare com o protocolo internamente (use apenas raciocínio, NÃO use tools)
4. Vá direto para Final Answer com os resultados

REGRAS IMPORTANTES:
- Use a tool analisar_nota_fiscal APENAS UMA VEZ
- Após receber os dados da nota, NÃO use mais nenhuma tool
- Faça a comparação e validação no seu raciocínio (Thought)
- Vá direto para "Thought: I now know the final answer" e depois "Final Answer"
- Se houver divergência entre nota fiscal e protocolo, REJEITE no Final Answer
- Se a nota fiscal estiver ilegível ou com dados faltando, REJEITE no Final Answer

TOOLS DISPONÍVEIS:
{tools}

TOOL NAMES: {tool_names}

FORMATO DE RESPOSTA (OBRIGATÓRIO - SIGA EXATAMENTE):
Thought: [seu raciocínio]
Action: [nome exato da tool]
Action Input: {{"arquivo_nota": "nota_fiscal_exemplo.json"}}
Observation: [será preenchido automaticamente]

IMPORTANTE:
- SEMPRE inclua "Action Input:" na mesma mensagem que "Action:"
- Action Input DEVE ser JSON válido com chaves duplas
- NÃO pule a linha Action Input
- Exemplo completo:
  Thought: Preciso analisar a nota fiscal
  Action: analisar_nota_fiscal
  Action Input: {{"arquivo_nota": "nota_fiscal_exemplo.json"}}

Após ver a Observation, NÃO USE MAIS TOOLS. Continue assim:
Thought: Analisando os dados da nota fiscal recebidos...
Thought: Comparando com dados do protocolo...
Thought: [identifique divergências se houver]
Thought: I now know the final answer
Final Answer: [resposta estruturada]

CRÍTICO: Após usar analisar_nota_fiscal e receber a Observation, você DEVE ir para Final Answer.
NÃO tente usar mais nenhuma Action. Toda a comparação deve ser feita no Thought.

FORMATO DA RESPOSTA FINAL:
---
STATUS: [APROVADO/REPROVADO]
NUMERO_NOTA: [número da nota fiscal]
DATA_COMPRA: [data no formato YYYY-MM-DD]
PRODUTO_CODIGO: [código do produto]
PRODUTO_NOME: [nome do produto]
CATEGORIA: [categoria do produto]
VALOR_PAGO: [valor total pago]
DIVERGENCIAS: [liste divergências encontradas, se houver]
PODE_PROSSEGUIR: [SIM/NAO]
---

PROTOCOLO E DOCUMENTOS:
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
            max_iterations=3,  # Apenas 1 tool + Final Answer
            early_stopping_method="force"  # Para ir direto para Final Answer após usar a tool
        )

    def analyze(self, protocolo_data: dict) -> dict:
        """
        Analisa documentos do protocolo de troca

        Args:
            protocolo_data: Dados do protocolo incluindo referências aos documentos

        Returns:
            Resultado da análise com dados extraídos
        """
        cliente = protocolo_data.get("cliente", {})
        produto_original = protocolo_data.get("produto_original", {})
        documentos = protocolo_data.get("documentos_anexados", [])

        # Identifica arquivo da nota fiscal
        nota_fiscal = "nota_fiscal_exemplo.json"  # Default
        for doc in documentos:
            if doc.get("tipo") == "nota_fiscal":
                nota_fiscal = doc.get("arquivo", nota_fiscal)

        input_text = f"""
Protocolo: {protocolo_data.get('protocolo', 'N/A')}

Dados do Protocolo:
- Cliente CPF: {cliente.get('cpf', 'N/A')}
- Cliente Nome: {cliente.get('nome', 'N/A')}
- Produto Código: {produto_original.get('codigo', 'N/A')}
- Produto Descrição: {produto_original.get('descricao', 'N/A')}
- Nota Fiscal Informada: {produto_original.get('numero_nota_fiscal', 'N/A')}

Documento Anexado:
- Arquivo da Nota Fiscal: {nota_fiscal}

Por favor, analise a nota fiscal e valide se os dados conferem com o protocolo.
Extraia todas as informações necessárias para as próximas etapas.
"""

        resultado = self.agent_executor.invoke({"input": input_text})
        output = resultado.get("output", "")

        aprovado = "STATUS: APROVADO" in output or "PODE_PROSSEGUIR: SIM" in output

        # Extrai dados estruturados do output (parsing simples)
        # Em produção, usaríamos output parsers do LangChain
        data_compra = None
        categoria = None
        for line in output.split("\n"):
            if "DATA_COMPRA:" in line:
                data_compra = line.split(":", 1)[1].strip()
            if "CATEGORIA:" in line:
                categoria = line.split(":", 1)[1].strip()

        return {
            "agent": "DocumentAnalyzer",
            "status": "aprovado" if aprovado else "reprovado",
            "output": output,
            "data_compra": data_compra,
            "categoria": categoria,
            "raw_result": resultado
        }


def analisar_documentos(protocolo_data: dict) -> dict:
    """Função helper para análise de documentos"""
    agent = DocumentAnalyzerAgent()
    return agent.analyze(protocolo_data)
