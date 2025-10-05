"""
Tools do LangChain para análise de documentos
"""

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
import json
import os
from datetime import datetime


# Schemas
class AnalisarNotaFiscalInput(BaseModel):
    arquivo_nota: str = Field(description="Nome/caminho do arquivo da nota fiscal")


class ConsultarRegrasInput(BaseModel):
    categoria_produto: str = Field(description="Categoria do produto (Eletrônicos, Áudio, Informática)")
    tipo_troca: str = Field(description="Tipo de troca (produto_defeituoso, troca_outro_produto, vale_compra)")


class ValidarPrazoInput(BaseModel):
    data_compra: str = Field(description="Data da compra no formato YYYY-MM-DD")
    categoria: str = Field(description="Categoria do produto")
    tipo_troca: str = Field(description="Tipo de troca")


# Funções
def _analisar_nota_fiscal(arquivo_nota: str) -> str:
    """Extrai informações de nota fiscal"""
    try:
        if "exemplo" in arquivo_nota.lower() or not os.path.exists(arquivo_nota):
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            arquivo_nota = os.path.join(base_path, "data", "synthetic_docs", "nota_fiscal_exemplo.json")

        with open(arquivo_nota, 'r', encoding='utf-8') as f:
            nota = json.load(f)

        produtos_str = "\n".join([
            f"  - {p['descricao']} (Cód: {p['codigo']}) - Qtd: {p['quantidade']} - R$ {p['valor_total']:.2f}"
            for p in nota['produtos']
        ])

        return f"""
NOTA FISCAL ANALISADA:
Número: {nota['numero_nota']}
Data de Emissão: {nota['data_emissao']}
CLIENTE: {nota['destinatario']['nome']} - CPF: {nota['destinatario']['cpf']}
PRODUTOS:
{produtos_str}
TOTAL: R$ {nota['totais']['valor_total']:.2f}
"""
    except Exception as e:
        return f"Erro ao analisar nota fiscal: {str(e)}"


def _consultar_regras_elegibilidade(categoria_produto: str, tipo_troca: str) -> str:
    """Consulta regras de elegibilidade"""
    try:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        arquivo_regras = os.path.join(base_path, "data", "synthetic_docs", "regras_elegibilidade.md")

        with open(arquivo_regras, 'r', encoding='utf-8') as f:
            regras = f.read()

        return f"""
REGRAS DE ELEGIBILIDADE
Categoria: {categoria_produto}
Tipo: {tipo_troca}

{regras}
"""
    except Exception as e:
        return f"Erro ao consultar regras: {str(e)}"


def _validar_prazo_troca(data_compra: str, categoria: str, tipo_troca: str) -> str:
    """Valida prazo de troca"""
    try:
        data_compra_dt = datetime.strptime(data_compra, "%Y-%m-%d")
        hoje = datetime.now()
        dias_passados = (hoje - data_compra_dt).days

        prazos = {
            "eletrônicos": {"produto_defeituoso": 90, "troca_outro_produto": 30, "vale_compra": 30},
            "áudio": {"produto_defeituoso": 90, "troca_outro_produto": 15, "vale_compra": 15},
            "informática": {"produto_defeituoso": 90, "troca_outro_produto": 30, "vale_compra": 30}
        }

        categoria_lower = categoria.lower().replace("ô", "o").replace("á", "a")
        prazo_limite = prazos.get(categoria_lower, {}).get(tipo_troca, 30)
        dentro_prazo = dias_passados <= prazo_limite

        if dentro_prazo:
            return f"""
PRAZO VÁLIDO ✓
Data da compra: {data_compra}
Dias decorridos: {dias_passados}
Prazo limite: {prazo_limite} dias
Dias restantes: {prazo_limite - dias_passados}
"""
        else:
            return f"""
PRAZO EXPIRADO ✗
Data da compra: {data_compra}
Dias decorridos: {dias_passados}
Prazo limite: {prazo_limite} dias
Dias excedidos: {dias_passados - prazo_limite}
ATENÇÃO: Troca não pode ser aprovada.
"""
    except Exception as e:
        return f"Erro ao validar prazo: {str(e)}"


# Cria tools
analisar_nota_fiscal = StructuredTool.from_function(
    func=_analisar_nota_fiscal,
    name="analisar_nota_fiscal",
    description="Útil para extrair informações de nota fiscal. Retorna número, data, cliente, produtos e valores.",
    args_schema=AnalisarNotaFiscalInput,
    return_direct=False
)

consultar_regras_elegibilidade = StructuredTool.from_function(
    func=_consultar_regras_elegibilidade,
    name="consultar_regras_elegibilidade",
    description="Útil para consultar regras de elegibilidade de troca. Retorna prazos e condições. IMPORTANTE: Consulte SEMPRE antes de validar troca.",
    args_schema=ConsultarRegrasInput,
    return_direct=False
)

validar_prazo_troca = StructuredTool.from_function(
    func=_validar_prazo_troca,
    name="validar_prazo_troca",
    description="Útil para validar se troca está dentro do prazo. Calcula diferença entre data da compra e hoje.",
    args_schema=ValidarPrazoInput,
    return_direct=False
)


def get_document_tools():
    """Retorna lista de tools de documentos"""
    return [analisar_nota_fiscal, consultar_regras_elegibilidade, validar_prazo_troca]
