"""
Tools do LangChain para operações de estoque
"""

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mocks.api_estoque import APIEstoque


# Schemas
class ConsultarProdutoInput(BaseModel):
    codigo_produto: str = Field(description="Código do produto (ex: PROD-001)")


class VerificarDisponibilidadeInput(BaseModel):
    codigo_produto: str = Field(description="Código do produto")
    quantidade: int = Field(default=1, description="Quantidade desejada")


class ReservarProdutoInput(BaseModel):
    codigo_produto: str = Field(description="Código do produto a reservar")
    quantidade: int = Field(description="Quantidade a reservar")
    protocolo: str = Field(description="Número do protocolo de troca")


# Funções
def _consultar_produto(codigo_produto: str) -> str:
    """Busca informações de um produto"""
    resultado = APIEstoque.consultar_produto(codigo_produto)

    if resultado["status"] == "success":
        produto = resultado["data"]
        return f"""
Produto encontrado:
- Código: {produto['codigo']}
- Nome: {produto['nome']}
- Categoria: {produto['categoria']}
- Preço: R$ {produto['preco']:.2f}
- Quantidade total: {produto['quantidade_disponivel']} unidades
- Quantidade reservada: {produto['quantidade_reservada']} unidades
- Quantidade livre: {produto['quantidade_livre']} unidades
- Localização: {produto['localizacao']}
- Status: {'Ativo' if produto['ativo'] else 'Inativo'}
"""
    else:
        return f"Produto não encontrado. {resultado.get('message', '')}"


def _verificar_disponibilidade(codigo_produto: str, quantidade: int = 1) -> str:
    """Verifica disponibilidade de estoque"""
    resultado = APIEstoque.verificar_disponibilidade(codigo_produto, quantidade)

    if resultado["disponivel"]:
        return f"""
DISPONÍVEL ✓
Produto: {resultado['produto']['nome']}
Quantidade solicitada: {quantidade}
Quantidade livre em estoque: {resultado['quantidade_livre']}
Preço unitário: R$ {resultado['produto']['preco']:.2f}
"""
    else:
        return f"""
INDISPONÍVEL ✗
Motivo: {resultado['motivo']}
Quantidade livre: {resultado.get('quantidade_livre', 0)}
"""


def _reservar_produto(codigo_produto: str, quantidade: int, protocolo: str) -> str:
    """Reserva um produto no estoque"""
    resultado = APIEstoque.reservar_produto(codigo_produto, quantidade, protocolo)

    if resultado["status"] == "success":
        return f"""
RESERVA CRIADA COM SUCESSO ✓
- ID da Reserva: {resultado['reserva_id']}
- Produto: {resultado['codigo_produto']}
- Quantidade: {resultado['quantidade']}
- Protocolo: {protocolo}
- Validade: {resultado['validade']}
- Data: {resultado['timestamp']}
"""
    else:
        return f"""
ERRO AO CRIAR RESERVA ✗
Motivo: {resultado['message']}
"""


# Cria tools
consultar_produto = StructuredTool.from_function(
    func=_consultar_produto,
    name="consultar_produto",
    description="Útil para buscar informações detalhadas de um produto no estoque. Retorna nome, categoria, preço e quantidade disponível.",
    args_schema=ConsultarProdutoInput,
    return_direct=False
)

verificar_disponibilidade = StructuredTool.from_function(
    func=_verificar_disponibilidade,
    name="verificar_disponibilidade",
    description="Útil para verificar se há quantidade suficiente de um produto em estoque. IMPORTANTE: Use antes de tentar reservar.",
    args_schema=VerificarDisponibilidadeInput,
    return_direct=False
)

reservar_produto = StructuredTool.from_function(
    func=_reservar_produto,
    name="reservar_produto",
    description="Útil para reservar um produto no estoque. ATENÇÃO: Esta ação modifica o estoque. Use apenas após validar elegibilidade e disponibilidade.",
    args_schema=ReservarProdutoInput,
    return_direct=False
)


def get_inventory_tools():
    """Retorna lista de tools de estoque"""
    return [consultar_produto, verificar_disponibilidade, reservar_produto]
