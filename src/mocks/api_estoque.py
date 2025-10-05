"""
Mock da API de Estoque
Simula a consulta e reserva de produtos no estoque
"""

from typing import Dict, Optional
from datetime import datetime
import random

# Base de dados mock de estoque
ESTOQUE_DB = {
    "PROD-001": {
        "codigo": "PROD-001",
        "nome": "Smartphone XYZ Pro",
        "categoria": "Eletrônicos",
        "preco": 2499.90,
        "quantidade_disponivel": 15,
        "localizacao": "CD-SP-A12",
        "ativo": True
    },
    "PROD-002": {
        "codigo": "PROD-002",
        "nome": "Notebook ABC 15\"",
        "categoria": "Informática",
        "preco": 3999.00,
        "quantidade_disponivel": 0,  # Sem estoque
        "localizacao": "CD-SP-B05",
        "ativo": True
    },
    "PROD-003": {
        "codigo": "PROD-003",
        "nome": "Fone Bluetooth Premium",
        "categoria": "Áudio",
        "preco": 599.90,
        "quantidade_disponivel": 42,
        "localizacao": "CD-RJ-C08",
        "ativo": True
    },
    "PROD-004": {
        "codigo": "PROD-004",
        "nome": "Smart TV 55\" 4K",
        "categoria": "Eletrônicos",
        "preco": 2899.00,
        "quantidade_disponivel": 8,
        "localizacao": "CD-SP-A15",
        "ativo": True
    },
    "PROD-005": {
        "codigo": "PROD-005",
        "nome": "Tablet 10\" 128GB",
        "categoria": "Eletrônicos",
        "preco": 1499.00,
        "quantidade_disponivel": 23,
        "localizacao": "CD-MG-D03",
        "ativo": True
    }
}

# Controle de reservas (em memória para o mock)
RESERVAS = {}


class APIEstoque:
    """
    Mock da API de consulta e gestão de estoque

    Conceito: Simula operações de consulta e reserva de produtos
    que os agents utilizarão para validar disponibilidade
    """

    @staticmethod
    def consultar_produto(codigo_produto: str) -> Optional[Dict]:
        """
        Consulta informações de um produto no estoque

        Args:
            codigo_produto: Código do produto

        Returns:
            Dicionário com dados do produto ou None se não encontrado
        """
        produto = ESTOQUE_DB.get(codigo_produto)

        if produto:
            # Verifica se há reservas para este produto
            qtd_reservada = sum(
                r["quantidade"]
                for r in RESERVAS.values()
                if r["codigo_produto"] == codigo_produto and r["status"] == "ativa"
            )

            return {
                "status": "success",
                "data": {
                    **produto,
                    "quantidade_reservada": qtd_reservada,
                    "quantidade_livre": produto["quantidade_disponivel"] - qtd_reservada
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "not_found",
                "message": f"Produto {codigo_produto} não encontrado",
                "timestamp": datetime.now().isoformat()
            }

    @staticmethod
    def verificar_disponibilidade(codigo_produto: str, quantidade: int = 1) -> Dict:
        """
        Verifica se há quantidade disponível do produto

        Args:
            codigo_produto: Código do produto
            quantidade: Quantidade desejada

        Returns:
            Resultado da verificação de disponibilidade
        """
        response = APIEstoque.consultar_produto(codigo_produto)

        if response["status"] == "not_found":
            return {
                "disponivel": False,
                "motivo": "Produto não encontrado",
                "timestamp": datetime.now().isoformat()
            }

        produto = response["data"]

        if not produto["ativo"]:
            return {
                "disponivel": False,
                "motivo": "Produto inativo no sistema",
                "timestamp": datetime.now().isoformat()
            }

        if produto["quantidade_livre"] >= quantidade:
            return {
                "disponivel": True,
                "quantidade_livre": produto["quantidade_livre"],
                "produto": {
                    "codigo": produto["codigo"],
                    "nome": produto["nome"],
                    "preco": produto["preco"]
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "disponivel": False,
                "motivo": f"Estoque insuficiente. Disponível: {produto['quantidade_livre']}, Solicitado: {quantidade}",
                "quantidade_livre": produto["quantidade_livre"],
                "timestamp": datetime.now().isoformat()
            }

    @staticmethod
    def reservar_produto(codigo_produto: str, quantidade: int, protocolo: str) -> Dict:
        """
        Reserva um produto no estoque

        Args:
            codigo_produto: Código do produto
            quantidade: Quantidade a reservar
            protocolo: Número do protocolo de troca

        Returns:
            Resultado da reserva
        """
        verificacao = APIEstoque.verificar_disponibilidade(codigo_produto, quantidade)

        if not verificacao["disponivel"]:
            return {
                "status": "error",
                "message": verificacao["motivo"],
                "timestamp": datetime.now().isoformat()
            }

        # Gera ID da reserva
        reserva_id = f"RES-{random.randint(10000, 99999)}"

        # Cria reserva
        RESERVAS[reserva_id] = {
            "id": reserva_id,
            "codigo_produto": codigo_produto,
            "quantidade": quantidade,
            "protocolo": protocolo,
            "status": "ativa",
            "data_reserva": datetime.now().isoformat()
        }

        return {
            "status": "success",
            "reserva_id": reserva_id,
            "codigo_produto": codigo_produto,
            "quantidade": quantidade,
            "validade": "48 horas",
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def cancelar_reserva(reserva_id: str) -> Dict:
        """
        Cancela uma reserva de produto

        Args:
            reserva_id: ID da reserva

        Returns:
            Resultado do cancelamento
        """
        if reserva_id not in RESERVAS:
            return {
                "status": "error",
                "message": "Reserva não encontrada",
                "timestamp": datetime.now().isoformat()
            }

        RESERVAS[reserva_id]["status"] = "cancelada"

        return {
            "status": "success",
            "message": "Reserva cancelada com sucesso",
            "timestamp": datetime.now().isoformat()
        }
