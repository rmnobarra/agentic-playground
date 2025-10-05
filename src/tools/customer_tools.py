"""
Tools do LangChain para operações relacionadas ao cliente

CONCEITO - LangChain Tools:
Tools são componentes que permitem aos agents interagir com sistemas externos.
Cada tool encapsula uma funcionalidade específica e fornece ao agent:
- Nome descritivo
- Descrição do que faz (usado pelo LLM para decidir quando usar)
- Schema de parâmetros esperados
- Função de execução

O LLM analisa a descrição e decide autonomamente quando usar cada tool.
"""

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import sys
import os

# Adiciona o diretório raiz ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mocks.api_cliente import APICliente


# Schemas
class ConsultarClienteInput(BaseModel):
    cpf: str = Field(description="CPF do cliente (com ou sem formatação)")


class ValidarDadosClienteInput(BaseModel):
    cpf: str = Field(description="CPF do cliente")
    nome: str = Field(description="Nome completo do cliente")
    email: str = Field(description="Email do cliente")


# Funções das tools
def _consultar_cliente(cpf: str) -> str:
    """Consulta dados do cliente no sistema"""
    resultado = APICliente.consultar_cliente(cpf)

    if resultado["status"] == "success":
        cliente = resultado["data"]
        return f"""
Cliente encontrado:
- Nome: {cliente['nome']}
- CPF: {cliente['cpf']}
- Email: {cliente['email']}
- Telefone: {cliente['telefone']}
- Endereço: {cliente['endereco']['rua']}, {cliente['endereco']['numero']} - {cliente['endereco']['cidade']}/{cliente['endereco']['estado']}
- Cadastro ativo: {'Sim' if cliente['ativo'] else 'Não'}
- Cliente desde: {cliente['data_cadastro']}
"""
    else:
        return f"Cliente não encontrado. {resultado.get('message', '')}"


def _validar_dados_cliente(cpf: str, nome: str, email: str) -> str:
    """Valida se os dados fornecidos conferem com o cadastro"""
    resultado = APICliente.validar_dados(cpf, nome, email)

    if resultado["valido"]:
        return f"""
VALIDAÇÃO APROVADA ✓
Os dados informados conferem com o cadastro do cliente.
Cliente autenticado: {resultado['dados_cliente']['nome']}
Pode prosseguir com a análise da troca.
"""
    else:
        return f"""
VALIDAÇÃO REPROVADA ✗
Motivo: {resultado['motivo']}
ATENÇÃO: Não prossiga com a troca até que os dados sejam corrigidos.
"""


# Cria as tools usando StructuredTool
consultar_cliente = StructuredTool.from_function(
    func=_consultar_cliente,
    name="consultar_cliente",
    description="Útil para buscar dados completos de um cliente pelo CPF. Retorna nome, email, telefone, endereço e status do cadastro.",
    args_schema=ConsultarClienteInput,
    return_direct=False
)

validar_dados_cliente = StructuredTool.from_function(
    func=_validar_dados_cliente,
    name="validar_dados_cliente",
    description="Útil para validar se os dados fornecidos pelo cliente conferem com o cadastro. Verifica CPF, nome e email. IMPORTANTE: Use esta tool para garantir a segurança da operação.",
    args_schema=ValidarDadosClienteInput,
    return_direct=False
)


# Exporta as tools
def get_customer_tools():
    """Retorna lista de todas as tools relacionadas a cliente"""
    return [consultar_cliente, validar_dados_cliente]
