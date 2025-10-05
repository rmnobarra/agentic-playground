"""
Agent decisor final

CONCEITO - Decision Agent:
O agent decisor consolida todos os resultados das etapas anteriores
e toma a decisão final: aprovar ou rejeitar a troca.

Este padrão é crucial pois centraliza a lógica de decisão e garante
que todas as validações foram consideradas.
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


class DecisionAgent:
    """
    Agent decisor final da jornada de troca

    Função na Jornada:
    - Etapa 6: Decisor
    - Consolida resultados de todas as etapas anteriores
    - Toma decisão final: APROVAR ou REJEITAR
    - Gera justificativa clara da decisão
    """

    def __init__(self, model_name: str = "llama-3.3-70b-versatile", temperature: float = 0):
        """Inicializa o agent decisor"""
        self.llm = ChatGroq(
            model=model_name,
            temperature=temperature,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

        # Agent decisor não precisa de tools, apenas raciocínio
        self.tools = []

        self.output_parser = RobustJSONAgentOutputParser()

        self.prompt = PromptTemplate.from_template("""
Você é o Agent Decisor Final para o sistema de trocas de produtos.

CONTEXTO:
Você é o último agent na jornada. Você recebe os resultados de todos os agents
anteriores e toma a DECISÃO FINAL sobre aprovar ou rejeitar a troca.

SUA RESPONSABILIDADE:
Esta é a decisão mais importante. Você deve:
1. Analisar TODOS os resultados das etapas anteriores
2. Verificar se TODAS as validações passaram
3. Tomar decisão final baseada em evidências
4. Gerar justificativa clara e detalhada

CRITÉRIOS PARA APROVAÇÃO:
A troca só pode ser APROVADA se TODAS as condições forem verdadeiras:
✓ Validação de Cliente: APROVADO
✓ Análise de Documentos: APROVADO
✓ Validação de Elegibilidade: APROVADO
✓ Tipo de Troca: Classificado corretamente
✓ Estoque (se aplicável): DISPONÍVEL ou não se aplica

Se QUALQUER critério falhar = REJEITAR

PROCEDIMENTO:
1. Revise cada etapa anterior
2. Identifique se houve alguma reprovação
3. Se todas aprovadas, verifique se há observações importantes
4. Tome a decisão final
5. Gere justificativa detalhada

REGRAS IMPORTANTES:
- Seja CONSERVADOR: em caso de dúvida, REJEITE
- NUNCA aprove se houver qualquer reprovação anterior
- Sempre explique CLARAMENTE o motivo da decisão
- Se aprovar, liste o que será feito (troca, vale, etc)
- Se rejeitar, explique o que o cliente precisa fazer

TOOLS DISPONÍVEIS:
{tools}

TOOL NAMES: {tool_names}

FORMATO DE RESPOSTA (obrigatório):
Thought: [analise todos os resultados anteriores]
Thought: [verifique cada critério]
Thought: [tome a decisão]
Thought: I now know the final answer
Final Answer: [decisão estruturada]

FORMATO DA RESPOSTA FINAL:
---
DECISÃO FINAL: [APROVADO/REJEITADO]

RESUMO DA ANÁLISE:
- Validação Cliente: [resultado]
- Análise Documentos: [resultado]
- Elegibilidade: [resultado]
- Tipo Troca: [resultado]
- Estoque: [resultado ou N/A]

JUSTIFICATIVA:
[Explicação detalhada da decisão]

PRÓXIMOS PASSOS:
[O que acontece agora - para aprovação ou rejeição]

DADOS DA RESERVA (se aplicável):
[ID da reserva, produto, etc]

VALOR DA OPERAÇÃO:
[Informações sobre valores, créditos, etc]

MENSAGEM PARA O CLIENTE:
[Mensagem clara e amigável explicando a decisão]
---

RESULTADOS DAS ETAPAS ANTERIORES:
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
            max_iterations=4
        )

    def decide(self, resultados_anteriores: dict) -> dict:
        """
        Toma decisão final baseada em todos os resultados

        Args:
            resultados_anteriores: Dicionário com resultados de todas as etapas

        Returns:
            Decisão final com justificativa
        """
        # Formata resultados para o prompt
        input_text = f"""
Protocolo: {resultados_anteriores.get('protocolo', 'N/A')}

=== RESULTADOS DAS ETAPAS ===

1. VALIDAÇÃO DE CLIENTE:
Status: {resultados_anteriores.get('validacao_cliente', {}).get('status', 'N/A')}
Detalhes: {resultados_anteriores.get('validacao_cliente', {}).get('output', 'N/A')[:300]}

2. ANÁLISE DE DOCUMENTOS:
Status: {resultados_anteriores.get('analise_documentos', {}).get('status', 'N/A')}
Data Compra: {resultados_anteriores.get('analise_documentos', {}).get('data_compra', 'N/A')}
Categoria: {resultados_anteriores.get('analise_documentos', {}).get('categoria', 'N/A')}

3. VALIDAÇÃO DE ELEGIBILIDADE:
Status: {resultados_anteriores.get('validacao_elegibilidade', {}).get('status', 'N/A')}
Detalhes: {resultados_anteriores.get('validacao_elegibilidade', {}).get('output', 'N/A')[:300]}

4. CLASSIFICAÇÃO DE TROCA:
Tipo: {resultados_anteriores.get('classificacao_troca', {}).get('tipo_troca_classificado', 'N/A')}
Requer Estoque: {resultados_anteriores.get('classificacao_troca', {}).get('requer_validacao_estoque', 'N/A')}

5. VALIDAÇÃO DE ESTOQUE:
Status: {resultados_anteriores.get('validacao_estoque', {}).get('status', 'N/A') if resultados_anteriores.get('validacao_estoque') else 'N/A - Não aplicável'}
Reserva ID: {resultados_anteriores.get('validacao_estoque', {}).get('reserva_id', 'N/A') if resultados_anteriores.get('validacao_estoque') else 'N/A'}

=== FIM DOS RESULTADOS ===

Com base em TODOS os resultados acima, tome a decisão final sobre aprovar ou rejeitar esta troca.
Seja rigoroso e justifique sua decisão claramente.
"""

        resultado = self.agent_executor.invoke({"input": input_text})
        output = resultado.get("output", "")

        # Determina se foi aprovado
        aprovado = "DECISÃO FINAL: APROVADO" in output

        return {
            "agent": "DecisionAgent",
            "decisao_final": "aprovado" if aprovado else "rejeitado",
            "output": output,
            "raw_result": resultado
        }


def tomar_decisao(resultados_anteriores: dict) -> dict:
    """Função helper para decisão final"""
    agent = DecisionAgent()
    return agent.decide(resultados_anteriores)
