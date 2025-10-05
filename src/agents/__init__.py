"""
Módulo de Agents Especializados

CONCEITO - Agent Architecture:
Cada agent tem uma responsabilidade específica na jornada.
Esta arquitetura modular permite:
- Fácil manutenção e debugging
- Reutilização de agents em outras jornadas
- Testes isolados de cada etapa
- Evolução independente de cada agent
"""

from .customer_validator_agent import CustomerValidatorAgent, validar_cliente
from .document_analyzer_agent import DocumentAnalyzerAgent, analisar_documentos
from .eligibility_validator_agent import EligibilityValidatorAgent, validar_elegibilidade
from .exchange_classifier_agent import ExchangeClassifierAgent, classificar_troca
from .inventory_validator_agent import InventoryValidatorAgent, validar_estoque
from .decision_agent import DecisionAgent, tomar_decisao

__all__ = [
    'CustomerValidatorAgent',
    'DocumentAnalyzerAgent',
    'EligibilityValidatorAgent',
    'ExchangeClassifierAgent',
    'InventoryValidatorAgent',
    'DecisionAgent',
    'validar_cliente',
    'analisar_documentos',
    'validar_elegibilidade',
    'classificar_troca',
    'validar_estoque',
    'tomar_decisao'
]
