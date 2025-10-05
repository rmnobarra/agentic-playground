"""
Mock da API de Clientes
Simula a consulta de dados do cliente no sistema
"""

from typing import Dict, Optional
from datetime import datetime

# Base de dados mock de clientes
CLIENTES_DB = {
    "12345678900": {
        "cpf": "12345678900",
        "nome": "João Silva Santos",
        "email": "joao.silva@email.com",
        "telefone": "(11) 98765-4321",
        "endereco": {
            "rua": "Rua das Flores",
            "numero": "123",
            "complemento": "Apto 45",
            "bairro": "Centro",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01234-567"
        },
        "data_cadastro": "2023-01-15",
        "ativo": True
    },
    "98765432100": {
        "cpf": "98765432100",
        "nome": "Maria Oliveira Costa",
        "email": "maria.oliveira@email.com",
        "telefone": "(21) 91234-5678",
        "endereco": {
            "rua": "Av. Principal",
            "numero": "456",
            "complemento": "Casa",
            "bairro": "Jardim América",
            "cidade": "Rio de Janeiro",
            "estado": "RJ",
            "cep": "22222-333"
        },
        "data_cadastro": "2022-06-20",
        "ativo": True
    }
}


class APICliente:
    """
    Mock da API de consulta de clientes

    Conceito: Simula uma API REST que seria consumida pelos agents
    para validar dados do cliente
    """

    @staticmethod
    def consultar_cliente(cpf: str) -> Optional[Dict]:
        """
        Consulta dados do cliente pelo CPF

        Args:
            cpf: CPF do cliente (apenas números)

        Returns:
            Dicionário com dados do cliente ou None se não encontrado
        """
        # Remove caracteres não numéricos
        cpf_limpo = ''.join(filter(str.isdigit, cpf))

        cliente = CLIENTES_DB.get(cpf_limpo)

        if cliente:
            return {
                "status": "success",
                "data": cliente,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "not_found",
                "message": f"Cliente com CPF {cpf} não encontrado",
                "timestamp": datetime.now().isoformat()
            }

    @staticmethod
    def validar_dados(cpf: str, nome: str, email: str) -> Dict:
        """
        Valida se os dados fornecidos conferem com o cadastro

        Args:
            cpf: CPF informado
            nome: Nome informado
            email: Email informado

        Returns:
            Resultado da validação
        """
        cliente_response = APICliente.consultar_cliente(cpf)

        if cliente_response["status"] == "not_found":
            return {
                "valido": False,
                "motivo": "Cliente não encontrado no sistema",
                "timestamp": datetime.now().isoformat()
            }

        cliente = cliente_response["data"]

        # Validações
        erros = []

        if cliente["nome"].lower() != nome.lower():
            erros.append(f"Nome não confere. Cadastrado: {cliente['nome']}, Informado: {nome}")

        if cliente["email"].lower() != email.lower():
            erros.append(f"Email não confere. Cadastrado: {cliente['email']}, Informado: {email}")

        if not cliente["ativo"]:
            erros.append("Cliente com cadastro inativo")

        if erros:
            return {
                "valido": False,
                "motivo": "; ".join(erros),
                "timestamp": datetime.now().isoformat()
            }

        return {
            "valido": True,
            "dados_cliente": cliente,
            "timestamp": datetime.now().isoformat()
        }
