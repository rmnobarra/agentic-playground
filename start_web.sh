#!/bin/bash

# Script para iniciar a interface web do sistema agêntico

echo "🚀 Iniciando Jornada Agêntica - Interface Web"
echo "================================================"
echo ""

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "⚠️  Ambiente virtual não encontrado!"
    echo "Execute primeiro:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

# Ativa o ambiente virtual
source venv/bin/activate

# Verifica se o .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "Copie .env.example para .env e configure GROQ_API_KEY"
    echo ""
    echo "Execute:"
    echo "  cp .env.example .env"
    echo "  # Edite .env e adicione sua chave"
    exit 1
fi

# Verifica se a chave está configurada
if ! grep -q "GROQ_API_KEY=gsk_" .env; then
    echo "⚠️  GROQ_API_KEY não configurada no .env"
    echo ""
    echo "Obtenha sua chave gratuita em:"
    echo "  https://console.groq.com/keys"
    echo ""
    echo "Depois adicione no arquivo .env:"
    echo "  GROQ_API_KEY=sua_chave_aqui"
    exit 1
fi

echo "✅ Ambiente configurado!"
echo ""
echo "📚 Abrindo interface web..."
echo "   URL: http://localhost:8501"
echo ""
echo "💡 Dica: Pressione Ctrl+C para parar o servidor"
echo ""

# Inicia o Streamlit
streamlit run app.py
