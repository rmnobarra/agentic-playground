"""
Exemplo de Execução da Jornada Agêntica de Troca

Este script demonstra como executar a jornada completa de troca de produtos
usando o sistema de agents construído.

CONCEITO - End-to-End Flow:
Este exemplo mostra a jornada completa, do protocolo de entrada até a decisão final.
"""

import sys
import os
import json
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from orchestrator import ExchangeJourneyOrchestrator


def exemplo_1_troca_aprovada():
    """
    Exemplo 1: Cenário de Troca APROVADA

    - Cliente válido
    - Documentos corretos
    - Dentro do prazo
    - Produto defeituoso
    - Estoque disponível
    """
    print("\n" + "="*100)
    print("EXEMPLO 1: TROCA DE PRODUTO DEFEITUOSO - CENÁRIO APROVADO")
    print("="*100)

    protocolo = {
        "protocolo": "TROCA-2024-98765",
        "data_abertura": "2025-10-01T10:30:00",
        "tipo_solicitacao": "troca_produto",
        "cliente": {
            "cpf": "123.456.789-00",
            "nome": "João Silva Santos",
            "email": "joao.silva@email.com",
            "telefone": "(11) 98765-4321"
        },
        "produto_original": {
            "codigo": "PROD-001",
            "descricao": "Smartphone XYZ Pro",
            "numero_nota_fiscal": "NF-2024-456789",
            "data_compra": "2025-09-20",
            "valor_pago": 2499.90
        },
        "motivo_troca": "produto_defeituoso",
        "descricao_problema": "Aparelho apresenta tela preta após 2 semanas de uso. Não liga mesmo após carregamento completo.",
        "tipo_troca_desejado": "troca_outro_produto",
        "produto_desejado": {
            "codigo": "PROD-003",
            "descricao": "Fone Bluetooth Premium"
        },
        "documentos_anexados": [
            {
                "tipo": "foto_produto",
                "descricao": "Foto do smartphone mostrando tela preta",
                "arquivo": "foto_produto_defeito.jpg"
            },
            {
                "tipo": "nota_fiscal",
                "descricao": "Nota fiscal da compra original",
                "arquivo": "nota_fiscal.pdf"
            }
        ],
        "status": "aguardando_analise",
        "prioridade": "media"
    }

    # Executa a jornada
    orchestrator = ExchangeJourneyOrchestrator()
    resultado = orchestrator.execute_journey(protocolo)

    # Salva relatório
    orchestrator.save_journey_report(resultado, "exemplo_1_aprovado.json")

    return resultado


def exemplo_2_troca_fora_prazo():
    """
    Exemplo 2: Cenário de Troca REJEITADA por prazo

    - Cliente válido
    - Documentos corretos
    - FORA do prazo (compra há 120 dias)
    - Tentativa de troca voluntária
    """
    print("\n" + "="*100)
    print("EXEMPLO 2: TROCA FORA DO PRAZO - CENÁRIO REJEITADO")
    print("="*100)

    protocolo = {
        "protocolo": "TROCA-2024-11111",
        "data_abertura": "2024-10-01T14:00:00",
        "tipo_solicitacao": "troca_produto",
        "cliente": {
            "cpf": "123.456.789-00",
            "nome": "João Silva Santos",
            "email": "joao.silva@email.com",
            "telefone": "(11) 98765-4321"
        },
        "produto_original": {
            "codigo": "PROD-003",
            "descricao": "Fone Bluetooth Premium",
            "numero_nota_fiscal": "NF-2024-111111",
            "data_compra": "2024-06-01",  # Há 4 meses (120 dias) - FORA DO PRAZO
            "valor_pago": 599.90
        },
        "motivo_troca": "troca_outro_produto",
        "descricao_problema": "Quero trocar por outro modelo que gostei mais",
        "tipo_troca_desejado": "troca_outro_produto",
        "produto_desejado": {
            "codigo": "PROD-004",
            "descricao": "Smart TV 55\" 4K"
        },
        "documentos_anexados": [
            {
                "tipo": "foto_produto",
                "descricao": "Foto do fone lacrado",
                "arquivo": "foto_fone.jpg"
            },
            {
                "tipo": "nota_fiscal",
                "descricao": "Nota fiscal",
                "arquivo": "nota_fiscal.pdf"
            }
        ],
        "status": "aguardando_analise",
        "prioridade": "baixa"
    }

    orchestrator = ExchangeJourneyOrchestrator()
    resultado = orchestrator.execute_journey(protocolo)

    orchestrator.save_journey_report(resultado, "exemplo_2_fora_prazo.json")

    return resultado


def exemplo_3_produto_sem_estoque():
    """
    Exemplo 3: Cenário com produto SEM ESTOQUE

    - Cliente válido
    - Documentos corretos
    - Dentro do prazo
    - Produto desejado SEM estoque
    """
    print("\n" + "="*100)
    print("EXEMPLO 3: PRODUTO DESEJADO SEM ESTOQUE")
    print("="*100)

    protocolo = {
        "protocolo": "TROCA-2024-22222",
        "data_abertura": "2024-10-01T16:00:00",
        "tipo_solicitacao": "troca_produto",
        "cliente": {
            "cpf": "987.654.321-00",
            "nome": "Maria Oliveira Costa",
            "email": "maria.oliveira@email.com",
            "telefone": "(21) 91234-5678"
        },
        "produto_original": {
            "codigo": "PROD-003",
            "descricao": "Fone Bluetooth Premium",
            "numero_nota_fiscal": "NF-2024-222222",
            "data_compra": "2024-09-20",  # Recente
            "valor_pago": 599.90
        },
        "motivo_troca": "produto_defeituoso",
        "descricao_problema": "Fone apresenta chiado no lado esquerdo",
        "tipo_troca_desejado": "troca_outro_produto",
        "produto_desejado": {
            "codigo": "PROD-002",  # Este produto está SEM ESTOQUE
            "descricao": "Notebook ABC 15\""
        },
        "documentos_anexados": [
            {
                "tipo": "foto_produto",
                "descricao": "Foto do fone",
                "arquivo": "foto_fone_defeito.jpg"
            },
            {
                "tipo": "nota_fiscal",
                "descricao": "Nota fiscal",
                "arquivo": "nota_fiscal.pdf"
            }
        ],
        "status": "aguardando_analise",
        "prioridade": "alta"
    }

    orchestrator = ExchangeJourneyOrchestrator()
    resultado = orchestrator.execute_journey(protocolo)

    orchestrator.save_journey_report(resultado, "exemplo_3_sem_estoque.json")

    return resultado


def exemplo_4_dados_invalidos():
    """
    Exemplo 4: Cenário com DADOS DO CLIENTE INVÁLIDOS

    - CPF não confere
    - Jornada deve ser interrompida na primeira etapa
    """
    print("\n" + "="*100)
    print("EXEMPLO 4: DADOS DO CLIENTE INVÁLIDOS - INTERROMPIDO NA ETAPA 1")
    print("="*100)

    protocolo = {
        "protocolo": "TROCA-2024-33333",
        "data_abertura": "2024-10-01T18:00:00",
        "tipo_solicitacao": "troca_produto",
        "cliente": {
            "cpf": "123.456.789-00",
            "nome": "Nome Errado",  # Nome não confere com cadastro
            "email": "email.errado@email.com",  # Email não confere
            "telefone": "(11) 98765-4321"
        },
        "produto_original": {
            "codigo": "PROD-001",
            "descricao": "Smartphone XYZ Pro",
            "numero_nota_fiscal": "NF-2024-456789",
            "data_compra": "2024-08-15",
            "valor_pago": 2499.90
        },
        "motivo_troca": "produto_defeituoso",
        "descricao_problema": "Tela quebrada",
        "tipo_troca_desejado": "troca_outro_produto",
        "produto_desejado": {
            "codigo": "PROD-003",
            "descricao": "Fone Bluetooth Premium"
        },
        "documentos_anexados": [],
        "status": "aguardando_analise",
        "prioridade": "media"
    }

    orchestrator = ExchangeJourneyOrchestrator()
    resultado = orchestrator.execute_journey(protocolo)

    orchestrator.save_journey_report(resultado, "exemplo_4_dados_invalidos.json")

    return resultado


def main():
    """
    Função principal que executa todos os exemplos

    CONCEITO - Test Scenarios:
    Cobrimos diferentes cenários para demonstrar como o sistema
    se comporta em situações variadas (happy path, edge cases, error cases)
    """
    print("\n")
    print("╔" + "="*98 + "╗")
    print("║" + " "*98 + "║")
    print("║" + " "*25 + "JORNADA AGÊNTICA - SISTEMA DE TROCAS" + " "*36 + "║")
    print("║" + " "*20 + "Demonstração de Múltiplos Cenários de Uso" + " "*36 + "║")
    print("║" + " "*98 + "║")
    print("╚" + "="*98 + "╝")

    print("\n⚠️  IMPORTANTE: Certifique-se de que a variável GROQ_API_KEY está configurada no arquivo .env\n")

    exemplos = [
        ("Troca Aprovada - Produto Defeituoso", exemplo_1_troca_aprovada),
        ("Troca Rejeitada - Fora do Prazo", exemplo_2_troca_fora_prazo),
        ("Produto Sem Estoque", exemplo_3_produto_sem_estoque),
        ("Dados Inválidos - Interrupção", exemplo_4_dados_invalidos)
    ]

    resultados_geral = []

    for i, (nome, func) in enumerate(exemplos, 1):
        print(f"\n\n{'#'*100}")
        print(f"# EXECUTANDO EXEMPLO {i}/{len(exemplos)}: {nome}")
        print(f"{'#'*100}\n")

        try:
            resultado = func()
            resultados_geral.append({
                "exemplo": nome,
                "status": "executado",
                "decisao_final": resultado.get("decisao_final"),
                "protocolo": resultado.get("protocolo")
            })
        except Exception as e:
            print(f"\n❌ ERRO ao executar exemplo: {str(e)}")
            resultados_geral.append({
                "exemplo": nome,
                "status": "erro",
                "erro": str(e)
            })

        print("\n" + "="*100)
        print("Pressione ENTER para continuar para o próximo exemplo...")
        input()

    # Resumo final
    print("\n\n")
    print("╔" + "="*98 + "╗")
    print("║" + " "*35 + "RESUMO DOS EXEMPLOS" + " "*44 + "║")
    print("╚" + "="*98 + "╝\n")

    for i, res in enumerate(resultados_geral, 1):
        status_icon = "✅" if res.get("decisao_final") == "aprovado" else "❌" if res.get("decisao_final") == "rejeitado" else "⚠️"
        print(f"{i}. {res['exemplo']}")
        print(f"   {status_icon} Decisão: {res.get('decisao_final', res.get('status')).upper()}")
        print(f"   Protocolo: {res.get('protocolo', 'N/A')}\n")

    print("\n📊 Relatórios detalhados salvos em formato JSON")
    print("="*100 + "\n")


if __name__ == "__main__":
    main()
