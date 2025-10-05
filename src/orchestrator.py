"""
Orquestrador da Jornada Agêntica de Troca de Produtos

CONCEITO - Orchestration Pattern:
O orquestrador coordena a execução sequencial dos agents,
gerencia o fluxo de dados entre eles e implementa a lógica
de negócio da jornada completa.

CONCEITO - Sequential Agent Chain:
Diferente de um único agent tentando fazer tudo, este padrão
usa múltiplos agents especializados em sequência, onde cada
um contribui com sua expertise específica.

Este é um dos padrões mais importantes em AI Engineering:
Decomposição de problemas complexos em etapas especializadas.
"""

import json
from datetime import datetime
from typing import Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents import (
    CustomerValidatorAgent,
    DocumentAnalyzerAgent,
    EligibilityValidatorAgent,
    ExchangeClassifierAgent,
    InventoryValidatorAgent,
    DecisionAgent
)


class ExchangeJourneyOrchestrator:
    """
    Orquestrador da jornada completa de troca

    Responsabilidades:
    1. Coordenar execução dos 6 agents na ordem correta
    2. Passar dados entre agents
    3. Implementar lógica condicional (ex: validação de estoque só se necessário)
    4. Consolidar resultados finais
    5. Gerar relatório completo da jornada
    """

    def __init__(self):
        """
        Inicializa o orquestrador

        CONCEITO - Lazy Initialization:
        Os agents são criados sob demanda para economizar recursos
        """
        self.customer_validator = None
        self.document_analyzer = None
        self.eligibility_validator = None
        self.exchange_classifier = None
        self.inventory_validator = None
        self.decision_agent = None

        self.journey_log = []  # Log de todas as etapas

    def _log_step(self, step_name: str, status: str, details: Any):
        """
        Registra uma etapa da jornada

        CONCEITO - Observability:
        Logging detalhado permite auditoria e debugging da jornada
        """
        self.journey_log.append({
            "timestamp": datetime.now().isoformat(),
            "step": step_name,
            "status": status,
            "details": details
        })

    def execute_journey(self, protocolo_data: dict) -> dict:
        """
        Executa a jornada completa de troca

        CONCEITO - Orchestration Flow:
        Este método implementa o diagrama de fluxo da jornada:
        Nova Solicitação → Validação Cliente → Análise Docs →
        Validação Elegibilidade → Classificação → [Estoque] → Decisão

        Args:
            protocolo_data: Dados do protocolo de troca

        Returns:
            Resultado completo da jornada com decisão final
        """
        print("\n" + "="*80)
        print("🚀 INICIANDO JORNADA AGÊNTICA DE TROCA DE PRODUTOS")
        print("="*80)
        print(f"\nProtocolo: {protocolo_data.get('protocolo', 'N/A')}")
        print(f"Cliente: {protocolo_data.get('cliente', {}).get('nome', 'N/A')}")
        print(f"Produto: {protocolo_data.get('produto_original', {}).get('descricao', 'N/A')}")
        print("\n" + "-"*80 + "\n")

        resultados = {
            "protocolo": protocolo_data.get("protocolo"),
            "data_inicio": datetime.now().isoformat(),
            "protocolo_data": protocolo_data
        }

        # =================================================================
        # ETAPA 1: Validação de Cliente
        # =================================================================
        print("📋 ETAPA 1/6: Validação dos Dados do Cliente")
        print("-"*80)

        try:
            if not self.customer_validator:
                self.customer_validator = CustomerValidatorAgent()

            resultado_cliente = self.customer_validator.validate(protocolo_data)
            resultados["validacao_cliente"] = resultado_cliente

            self._log_step("validacao_cliente", resultado_cliente["status"], resultado_cliente)

            print(f"\n✓ Status: {resultado_cliente['status'].upper()}")

            # Se reprovado, interrompe a jornada
            if resultado_cliente["status"] == "reprovado":
                print("\n❌ JORNADA INTERROMPIDA: Cliente não validado")
                resultados["decisao_final"] = "rejeitado"
                resultados["motivo_interrupcao"] = "Validação de cliente reprovada"
                return self._finalize_journey(resultados)

        except Exception as e:
            print(f"\n❌ ERRO na validação de cliente: {str(e)}")
            resultados["erro"] = str(e)
            resultados["decisao_final"] = "erro"
            return self._finalize_journey(resultados)

        print("\n" + "-"*80 + "\n")

        # =================================================================
        # ETAPA 2: Análise de Documentos
        # =================================================================
        print("📄 ETAPA 2/6: Análise dos Documentos Anexados")
        print("-"*80)

        try:
            if not self.document_analyzer:
                self.document_analyzer = DocumentAnalyzerAgent()

            resultado_documentos = self.document_analyzer.analyze(protocolo_data)
            resultados["analise_documentos"] = resultado_documentos

            self._log_step("analise_documentos", resultado_documentos["status"], resultado_documentos)

            print(f"\n✓ Status: {resultado_documentos['status'].upper()}")
            print(f"✓ Data da Compra: {resultado_documentos.get('data_compra', 'N/A')}")
            print(f"✓ Categoria: {resultado_documentos.get('categoria', 'N/A')}")

            if resultado_documentos["status"] == "reprovado":
                print("\n❌ JORNADA INTERROMPIDA: Documentos inválidos")
                resultados["decisao_final"] = "rejeitado"
                resultados["motivo_interrupcao"] = "Análise de documentos reprovada"
                return self._finalize_journey(resultados)

        except Exception as e:
            print(f"\n❌ ERRO na análise de documentos: {str(e)}")
            resultados["erro"] = str(e)
            resultados["decisao_final"] = "erro"
            return self._finalize_journey(resultados)

        print("\n" + "-"*80 + "\n")

        # =================================================================
        # ETAPA 3: Validação de Elegibilidade
        # =================================================================
        print("✅ ETAPA 3/6: Validação de Elegibilidade da Troca")
        print("-"*80)

        try:
            if not self.eligibility_validator:
                self.eligibility_validator = EligibilityValidatorAgent()

            resultado_elegibilidade = self.eligibility_validator.validate(
                protocolo_data,
                resultado_documentos
            )
            resultados["validacao_elegibilidade"] = resultado_elegibilidade

            self._log_step("validacao_elegibilidade", resultado_elegibilidade["status"], resultado_elegibilidade)

            print(f"\n✓ Status: {resultado_elegibilidade['status'].upper()}")

            if resultado_elegibilidade["status"] == "reprovado":
                print("\n❌ JORNADA INTERROMPIDA: Troca não elegível")
                resultados["decisao_final"] = "rejeitado"
                resultados["motivo_interrupcao"] = "Validação de elegibilidade reprovada"
                return self._finalize_journey(resultados)

        except Exception as e:
            print(f"\n❌ ERRO na validação de elegibilidade: {str(e)}")
            resultados["erro"] = str(e)
            resultados["decisao_final"] = "erro"
            return self._finalize_journey(resultados)

        print("\n" + "-"*80 + "\n")

        # =================================================================
        # ETAPA 4: Classificação do Tipo de Troca
        # =================================================================
        print("🏷️  ETAPA 4/6: Caracterização do Tipo de Troca")
        print("-"*80)

        try:
            if not self.exchange_classifier:
                self.exchange_classifier = ExchangeClassifierAgent()

            resultado_classificacao = self.exchange_classifier.classify(protocolo_data)
            resultados["classificacao_troca"] = resultado_classificacao

            self._log_step("classificacao_troca", "concluido", resultado_classificacao)

            print(f"\n✓ Tipo Classificado: {resultado_classificacao.get('tipo_troca_classificado', 'N/A')}")
            print(f"✓ Requer Validação de Estoque: {'Sim' if resultado_classificacao.get('requer_validacao_estoque') else 'Não'}")

        except Exception as e:
            print(f"\n❌ ERRO na classificação: {str(e)}")
            resultados["erro"] = str(e)
            resultados["decisao_final"] = "erro"
            return self._finalize_journey(resultados)

        print("\n" + "-"*80 + "\n")

        # =================================================================
        # ETAPA 5: Validação de Estoque (CONDICIONAL)
        # =================================================================
        # CONCEITO - Conditional Workflow:
        # Esta etapa só executa se o tipo de troca requer validação de estoque

        if resultado_classificacao.get("requer_validacao_estoque"):
            print("📦 ETAPA 5/6: Validação de Estoque")
            print("-"*80)

            try:
                if not self.inventory_validator:
                    self.inventory_validator = InventoryValidatorAgent()

                resultado_estoque = self.inventory_validator.validate(protocolo_data)
                resultados["validacao_estoque"] = resultado_estoque

                self._log_step("validacao_estoque", resultado_estoque["status"], resultado_estoque)

                print(f"\n✓ Status: {resultado_estoque['status'].upper()}")
                if resultado_estoque.get("reserva_id"):
                    print(f"✓ Reserva Criada: {resultado_estoque['reserva_id']}")

                if resultado_estoque["status"] == "indisponivel":
                    print("\n⚠️  Produto indisponível em estoque")
                    # Não interrompe, mas marca para decisão final

            except Exception as e:
                print(f"\n❌ ERRO na validação de estoque: {str(e)}")
                resultados["erro"] = str(e)
                resultados["decisao_final"] = "erro"
                return self._finalize_journey(resultados)

            print("\n" + "-"*80 + "\n")
        else:
            print("📦 ETAPA 5/6: Validação de Estoque - NÃO APLICÁVEL")
            print("-"*80)
            print("\n✓ Esta troca não requer validação de estoque")
            resultados["validacao_estoque"] = None
            self._log_step("validacao_estoque", "nao_aplicavel", "Tipo de troca não requer validação de estoque")
            print("\n" + "-"*80 + "\n")

        # =================================================================
        # ETAPA 6: Decisão Final
        # =================================================================
        print("⚖️  ETAPA 6/6: Decisão Final")
        print("-"*80)

        try:
            if not self.decision_agent:
                self.decision_agent = DecisionAgent()

            resultado_decisao = self.decision_agent.decide(resultados)
            resultados["decisao"] = resultado_decisao
            resultados["decisao_final"] = resultado_decisao["decisao_final"]

            self._log_step("decisao_final", resultado_decisao["decisao_final"], resultado_decisao)

            print(f"\n{'✅' if resultado_decisao['decisao_final'] == 'aprovado' else '❌'} Decisão: {resultado_decisao['decisao_final'].upper()}")

        except Exception as e:
            print(f"\n❌ ERRO na decisão final: {str(e)}")
            resultados["erro"] = str(e)
            resultados["decisao_final"] = "erro"
            return self._finalize_journey(resultados)

        print("\n" + "="*80)

        return self._finalize_journey(resultados)

    def _finalize_journey(self, resultados: dict) -> dict:
        """
        Finaliza a jornada e gera relatório

        CONCEITO - Journey Completion:
        Consolida todos os resultados e gera um relatório completo
        """
        resultados["data_fim"] = datetime.now().isoformat()
        resultados["journey_log"] = self.journey_log

        # Calcula duração (simplificado)
        # Em produção, calcularia tempo real de execução

        print("\n🏁 JORNADA CONCLUÍDA")
        print("="*80)
        print(f"\nDecisão Final: {resultados.get('decisao_final', 'N/A').upper()}")
        print(f"Total de Etapas Executadas: {len(self.journey_log)}")
        print("\n" + "="*80 + "\n")

        return resultados

    def save_journey_report(self, resultados: dict, output_path: str = None):
        """
        Salva relatório completo da jornada em JSON

        CONCEITO - Audit Trail:
        Mantém registro completo para auditoria e análise
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"journey_report_{resultados.get('protocolo', 'unknown')}_{timestamp}.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)

        print(f"📊 Relatório salvo em: {output_path}")
        return output_path


# Função helper para uso simplificado
def executar_jornada_troca(protocolo_data: dict) -> dict:
    """
    Função helper para executar jornada completa

    CONCEITO - Facade Pattern:
    Simplifica o uso do orquestrador para casos comuns
    """
    orchestrator = ExchangeJourneyOrchestrator()
    return orchestrator.execute_journey(protocolo_data)
