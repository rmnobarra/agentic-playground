"""
Interface Web para Jornada Agêntica de Troca de Produtos

Execute com: streamlit run app.py
"""

import streamlit as st
import sys
import os
from pathlib import Path
import json
from datetime import datetime, timedelta

# Adiciona src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from orchestrator import ExchangeJourneyOrchestrator

# Configuração da página
st.set_page_config(
    page_title="Jornada Agêntica - Troca de Produtos",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .step-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2ca02c;
        margin-top: 1rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .status-aprovado {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
    }
    .status-reprovado {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
    }
    .status-processando {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🤖 Jornada Agêntica - Sistema de Trocas</p>', unsafe_allow_html=True)
st.markdown("**Sistema inteligente para automação de processos de troca de produtos**")
st.divider()

# Sidebar - Informações
with st.sidebar:
    st.header("📚 Sobre o Sistema")
    st.markdown("""
    Este sistema utiliza **6 Agents especializados** para automatizar o processo de troca:

    1. 🔍 **Customer Validator** - Valida identidade
    2. 📄 **Document Analyzer** - Analisa documentos
    3. ✅ **Eligibility Validator** - Valida elegibilidade
    4. 🏷️ **Exchange Classifier** - Classifica tipo
    5. 📦 **Inventory Validator** - Verifica estoque
    6. ⚖️ **Decision Agent** - Decisão final

    ---
    **Stack**: LangChain + Groq + ReAct Pattern
    """)

    st.divider()

    # Verificação da API Key
    if os.getenv("GROQ_API_KEY"):
        st.success("✅ API Key configurada")
    else:
        st.error("⚠️ Configure GROQ_API_KEY no .env")

# Tabs principais
tab1, tab2, tab3 = st.tabs(["📝 Nova Solicitação", "🎯 Cenários Pré-definidos", "📊 Sobre"])

with tab1:
    st.subheader("Criar Nova Solicitação de Troca")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 👤 Dados do Cliente")
        cliente_cpf = st.text_input("CPF", "123.456.789-00", help="CPF do cliente")
        cliente_nome = st.text_input("Nome Completo", "João Silva Santos")
        cliente_email = st.text_input("Email", "joao.silva@email.com")

        st.markdown("#### 📦 Produto Original")
        produto_codigo = st.text_input("Código do Produto", "PROD-001")
        produto_desc = st.text_input("Descrição", "Smartphone XYZ Pro")

        # Data de compra (últimos 30 dias por padrão)
        data_default = datetime.now() - timedelta(days=15)
        data_compra = st.date_input("Data da Compra", data_default)

    with col2:
        st.markdown("#### 🔄 Dados da Troca")
        motivo = st.selectbox(
            "Motivo da Troca",
            ["produto_defeituoso", "arrependimento", "produto_errado"],
            help="Motivo da solicitação"
        )

        descricao_problema = st.text_area(
            "Descrição do Problema",
            "Aparelho apresenta tela preta após 2 semanas de uso. Não liga mesmo após carregamento completo.",
            height=100
        )

        tipo_troca = st.selectbox(
            "Tipo de Troca Desejado",
            ["troca_outro_produto", "vale_compra", "devolucao"],
            help="O que o cliente deseja"
        )

        st.markdown("#### 🎁 Produto Desejado (se aplicável)")
        produto_desejado_cod = st.text_input("Código", "PROD-003")
        produto_desejado_desc = st.text_input("Descrição do Produto", "Fone Bluetooth Premium")

    st.divider()

    if st.button("🚀 Executar Jornada Agêntica", type="primary", use_container_width=True):
        try:
            # Monta protocolo
            protocolo = {
                "protocolo": f"WEB-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "data_abertura": datetime.now().isoformat(),
                "tipo_solicitacao": "troca_produto",
                "cliente": {
                    "cpf": cliente_cpf,
                    "nome": cliente_nome,
                    "email": cliente_email
                },
                "produto_original": {
                    "codigo": produto_codigo,
                    "descricao": produto_desc,
                    "numero_nota_fiscal": "NF-2024-456789",
                    "data_compra": data_compra.strftime("%Y-%m-%d"),
                    "valor_pago": 2499.90
                },
                "motivo_troca": motivo,
                "descricao_problema": descricao_problema,
                "tipo_troca_desejado": tipo_troca,
                "produto_desejado": {
                    "codigo": produto_desejado_cod,
                    "descricao": produto_desejado_desc
                },
                "documentos_anexados": [
                    {"tipo": "nota_fiscal", "arquivo": "nota_fiscal_exemplo.json"}
                ],
                "status": "aguardando_analise"
            }

            # Executa jornada
            with st.spinner("🤖 Agents processando a solicitação..."):
                orchestrator = ExchangeJourneyOrchestrator()
                resultado = orchestrator.execute_journey(protocolo)

            # Exibe resultados
            st.success("✅ Jornada executada com sucesso!")

            # Decisão Final
            decisao = resultado.get("decisao_final", {})

            # Verifica se decisao é dict ou string
            if isinstance(decisao, dict):
                decisao_status = decisao.get("decisao_final", "desconhecido")
            else:
                # Se for string, usa diretamente
                decisao_status = str(decisao) if decisao else "desconhecido"

            if decisao_status == "aprovado":
                st.markdown(f'<div class="status-box status-aprovado"><h3>✅ TROCA APROVADA</h3></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-box status-reprovado"><h3>❌ TROCA REPROVADA</h3></div>', unsafe_allow_html=True)

            st.divider()

            # Detalhes de cada etapa
            st.subheader("📋 Detalhes da Jornada")

            etapas = [
                ("1️⃣ Validação de Cliente", "validacao_cliente"),
                ("2️⃣ Análise de Documentos", "analise_documentos"),
                ("3️⃣ Validação de Elegibilidade", "validacao_elegibilidade"),
                ("4️⃣ Classificação de Troca", "classificacao_troca"),
                ("5️⃣ Validação de Estoque", "validacao_estoque"),
                ("6️⃣ Decisão Final", "decisao")  # Mudou para "decisao" que é o dict
            ]

            for titulo, chave in etapas:
                with st.expander(titulo, expanded=False):
                    etapa_resultado = resultado.get(chave, {})

                    # Tratamento especial para tipos diferentes
                    if etapa_resultado:
                        # Se for um dict válido
                        if isinstance(etapa_resultado, dict):
                            status = etapa_resultado.get("status", etapa_resultado.get("decisao_final", "N/A"))
                            agent = etapa_resultado.get("agent", "N/A")

                            col_a, col_b = st.columns([1, 3])
                            with col_a:
                                st.metric("Status", str(status).upper())
                                st.caption(f"Agent: {agent}")

                            with col_b:
                                output = etapa_resultado.get("output", "Sem detalhes")
                                st.text_area("Saída do Agent", output, height=200, key=f"output_{chave}")
                        else:
                            # Se for string ou outro tipo
                            st.info(f"Resultado: {etapa_resultado}")
                    else:
                        st.info("Etapa não executada (condicional)")

            st.divider()

            # JSON completo
            with st.expander("🔍 Ver JSON Completo"):
                st.json(resultado)

        except Exception as e:
            st.error(f"❌ Erro ao executar jornada: {str(e)}")
            st.exception(e)

with tab2:
    st.subheader("🎯 Cenários Pré-configurados")
    st.markdown("Execute cenários de teste pré-definidos para ver diferentes resultados:")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Cenário 1: Troca Aprovada", use_container_width=True):
            st.session_state.cenario = 1

        if st.button("⏰ Cenário 2: Fora do Prazo", use_container_width=True):
            st.session_state.cenario = 2

    with col2:
        if st.button("📦 Cenário 3: Sem Estoque", use_container_width=True):
            st.session_state.cenario = 3

        if st.button("❌ Cenário 4: Dados Inválidos", use_container_width=True):
            st.session_state.cenario = 4

    # Executa cenário selecionado
    if 'cenario' in st.session_state:
        cenario_num = st.session_state.cenario

        # Define protocolos
        protocolos = {
            1: {
                "protocolo": "TESTE-APROVADO-001",
                "data_abertura": "2025-10-01T10:30:00",
                "tipo_solicitacao": "troca_produto",
                "cliente": {
                    "cpf": "123.456.789-00",
                    "nome": "João Silva Santos",
                    "email": "joao.silva@email.com"
                },
                "produto_original": {
                    "codigo": "PROD-001",
                    "descricao": "Smartphone XYZ Pro",
                    "numero_nota_fiscal": "NF-2024-456789",
                    "data_compra": "2025-09-20",
                    "valor_pago": 2499.90
                },
                "motivo_troca": "produto_defeituoso",
                "descricao_problema": "Tela preta, não liga",
                "tipo_troca_desejado": "troca_outro_produto",
                "produto_desejado": {
                    "codigo": "PROD-003",
                    "descricao": "Fone Bluetooth Premium"
                },
                "documentos_anexados": [
                    {"tipo": "nota_fiscal", "arquivo": "nota_fiscal_exemplo.json"}
                ],
                "status": "aguardando_analise"
            },
            2: {
                "protocolo": "TESTE-FORA-PRAZO-002",
                "data_abertura": "2025-10-01T11:00:00",
                "tipo_solicitacao": "troca_produto",
                "cliente": {
                    "cpf": "123.456.789-00",
                    "nome": "João Silva Santos",
                    "email": "joao.silva@email.com"
                },
                "produto_original": {
                    "codigo": "PROD-002",
                    "descricao": "Notebook Ultra Slim",
                    "numero_nota_fiscal": "NF-2024-111222",
                    "data_compra": "2024-06-01",  # Muito antigo
                    "valor_pago": 3999.90
                },
                "motivo_troca": "arrependimento",
                "descricao_problema": "Cliente não gostou do produto",
                "tipo_troca_desejado": "vale_compra",
                "documentos_anexados": [
                    {"tipo": "nota_fiscal", "arquivo": "nota_fiscal_exemplo.json"}
                ],
                "status": "aguardando_analise"
            },
            3: {
                "protocolo": "TESTE-SEM-ESTOQUE-003",
                "data_abertura": "2025-10-01T12:00:00",
                "tipo_solicitacao": "troca_produto",
                "cliente": {
                    "cpf": "123.456.789-00",
                    "nome": "João Silva Santos",
                    "email": "joao.silva@email.com"
                },
                "produto_original": {
                    "codigo": "PROD-001",
                    "descricao": "Smartphone XYZ Pro",
                    "numero_nota_fiscal": "NF-2024-456789",
                    "data_compra": "2025-09-20",
                    "valor_pago": 2499.90
                },
                "motivo_troca": "produto_defeituoso",
                "descricao_problema": "Tela quebrada",
                "tipo_troca_desejado": "troca_outro_produto",
                "produto_desejado": {
                    "codigo": "PROD-999",  # Produto inexistente
                    "descricao": "Produto Indisponível"
                },
                "documentos_anexados": [
                    {"tipo": "nota_fiscal", "arquivo": "nota_fiscal_exemplo.json"}
                ],
                "status": "aguardando_analise"
            },
            4: {
                "protocolo": "TESTE-DADOS-INVALIDOS-004",
                "data_abertura": "2025-10-01T13:00:00",
                "tipo_solicitacao": "troca_produto",
                "cliente": {
                    "cpf": "999.999.999-99",  # CPF inválido
                    "nome": "Cliente Inexistente",
                    "email": "inexistente@email.com"
                },
                "produto_original": {
                    "codigo": "PROD-001",
                    "descricao": "Smartphone XYZ Pro",
                    "numero_nota_fiscal": "NF-2024-456789",
                    "data_compra": "2025-09-20",
                    "valor_pago": 2499.90
                },
                "motivo_troca": "produto_defeituoso",
                "descricao_problema": "Produto com defeito",
                "tipo_troca_desejado": "troca_outro_produto",
                "produto_desejado": {
                    "codigo": "PROD-003",
                    "descricao": "Fone Bluetooth Premium"
                },
                "documentos_anexados": [
                    {"tipo": "nota_fiscal", "arquivo": "nota_fiscal_exemplo.json"}
                ],
                "status": "aguardando_analise"
            }
        }

        protocolo = protocolos[cenario_num]

        st.info(f"🎯 Executando Cenário {cenario_num}...")

        try:
            with st.spinner("🤖 Agents processando..."):
                orchestrator = ExchangeJourneyOrchestrator()
                resultado = orchestrator.execute_journey(protocolo)

            st.success("✅ Jornada concluída!")

            # Mostra resultado
            decisao = resultado.get("decisao_final", {})

            # Verifica se decisao é dict ou string
            if isinstance(decisao, dict):
                decisao_status = decisao.get("decisao_final", "desconhecido")
            else:
                # Se for string, usa diretamente
                decisao_status = str(decisao) if decisao else "desconhecido"

            if decisao_status == "aprovado":
                st.markdown(f'<div class="status-box status-aprovado"><h3>✅ TROCA APROVADA</h3></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="status-box status-reprovado"><h3>❌ TROCA REPROVADA</h3></div>', unsafe_allow_html=True)

            with st.expander("Ver Detalhes Completos"):
                st.json(resultado)

        except Exception as e:
            st.error(f"❌ Erro ao executar cenário: {str(e)}")
            st.exception(e)

        # Limpa seleção
        if 'cenario' in st.session_state:
            del st.session_state.cenario

with tab3:
    st.subheader("📊 Sobre o Sistema")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Agents", "6", help="Agents especializados")
        st.metric("Tools", "10", help="LangChain Tools")

    with col2:
        st.metric("Conceitos", "17", help="Conceitos de AI Engineering")
        st.metric("Tempo Médio", "15-25s", help="Por jornada completa")

    with col3:
        st.metric("Modelo", "llama-3.3-70b", help="Groq API")
        st.metric("Pattern", "ReAct", help="Reasoning + Acting")

    st.divider()

    st.markdown("""
    ### 🎓 Conceitos Aplicados

    Este sistema demonstra 17 conceitos de AI Engineering:

    - **ReAct Pattern**: Agents que raciocinam antes de agir
    - **Custom Output Parser**: Parser robusto para JSON
    - **Early Stopping**: Prevenção de loops infinitos
    - **Specialized Agents**: Decomposição por responsabilidade
    - **Orchestration**: Coordenação de múltiplos agents
    - **RAG**: Retrieval Augmented Generation
    - **Conditional Workflows**: Lógica condicional
    - E mais 10 conceitos...

    📚 **Documentação completa**: Ver `CONCEITOS.md`

    ---

    ### 🚀 Como Usar

    1. **Nova Solicitação**: Preencha os dados e execute
    2. **Cenários Pré-definidos**: Teste casos específicos
    3. **Analise os Logs**: Veja o raciocínio dos agents

    ---

    ### 🛠️ Stack Tecnológica

    - **LangChain**: Framework de agents
    - **Groq**: API de LLM (gratuita)
    - **Streamlit**: Interface web
    - **Pydantic**: Validação de schemas
    - **Python 3.9+**: Linguagem base

    ---

    **Desenvolvido como MVP educacional para workshop de AI Agents** 🎓
    """)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p><strong>Jornada Agêntica v1.0</strong> | LangChain + Groq + ReAct Pattern</p>
    <p>📖 Documentação: README.md | CONCEITOS.md | QUICKSTART.md</p>
</div>
""", unsafe_allow_html=True)
