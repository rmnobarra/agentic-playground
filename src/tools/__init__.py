"""
Módulo de Tools do LangChain

CONCEITO - Tool Organization:
Organizamos as tools em módulos temáticos (customer, inventory, document)
para facilitar manutenção e reutilização em diferentes agents.
"""

from .customer_tools import get_customer_tools
from .inventory_tools import get_inventory_tools
from .document_tools import get_document_tools

def get_all_tools():
    """
    Retorna todas as tools disponíveis

    CONCEITO: Função helper que agrega todas as tools.
    Útil para agents que precisam de acesso completo ao sistema.
    """
    return (
        get_customer_tools() +
        get_inventory_tools() +
        get_document_tools()
    )

__all__ = [
    'get_customer_tools',
    'get_inventory_tools',
    'get_document_tools',
    'get_all_tools'
]
