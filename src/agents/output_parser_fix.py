"""
Output Parser customizado para corrigir problemas de JSON parsing

CONCEITO - Custom Output Parser:
Quando o parser padrão do LangChain falha, podemos criar um customizado
que trata casos específicos do nosso modelo LLM.
"""

import json
import re
from typing import Union
from langchain.agents import AgentOutputParser
from langchain.schema import AgentAction, AgentFinish


class RobustJSONAgentOutputParser(AgentOutputParser):
    """
    Parser robusto que corrige problemas comuns de JSON mal formatado

    CONCEITO - Defensive Parsing:
    Alguns modelos LLM geram JSON com pequenos problemas de formatação.
    Este parser tenta múltiplas estratégias para extrair o JSON correto.
    """

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        """Parse do output do LLM"""

        # Procura por Final Answer
        if "Final Answer:" in text:
            return AgentFinish(
                return_values={"output": text.split("Final Answer:")[-1].strip()},
                log=text,
            )

        # Extrai Action e Action Input
        action_match = re.search(r"Action:\s*(.+?)(?:\n|$)", text, re.IGNORECASE)
        action_input_match = re.search(
            r"Action Input:\s*(.+?)(?:\n|Observation:|$)",
            text,
            re.IGNORECASE | re.DOTALL
        )

        if not action_match:
            raise ValueError(f"Could not parse LLM output: `{text}`")

        action = action_match.group(1).strip()
        action_input_raw = action_input_match.group(1).strip() if action_input_match else "{}"

        # Tenta fazer parse do JSON
        action_input = self._parse_json_robust(action_input_raw)

        return AgentAction(tool=action, tool_input=action_input, log=text)

    def _parse_json_robust(self, json_str: str) -> dict:
        """
        Tenta múltiplas estratégias para fazer parse de JSON

        CONCEITO - Fallback Strategies:
        Se uma estratégia falha, tenta a próxima até conseguir
        """
        # Remove espaços extras
        json_str = json_str.strip()

        # Estratégia 1: Parse direto
        try:
            return json.loads(json_str)
        except:
            pass

        # Estratégia 2: Se já é um dict em string, extrai
        if json_str.startswith("'") or json_str.startswith('"'):
            try:
                # Remove aspas externas
                json_str = json_str.strip("'\"")
                return json.loads(json_str)
            except:
                pass

        # Estratégia 3: Regex para extrair JSON de dentro de string
        json_match = re.search(r'\{.*\}', json_str, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass

        # Estratégia 4: Construir dict manualmente de key-value pairs
        try:
            # Procura por padrões como key: "value" ou "key": "value"
            pairs = re.findall(r'["\']?(\w+)["\']?\s*:\s*["\']([^"\']+)["\']', json_str)
            if pairs:
                return {k: v for k, v in pairs}
        except:
            pass

        # Se tudo falhar, retorna dict vazio (AgentExecutor vai tratar o erro)
        return {}

    @property
    def _type(self) -> str:
        return "robust-json-agent"
