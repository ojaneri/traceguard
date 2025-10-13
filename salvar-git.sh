#!/bin/bash

# Script para salvar versão no GitHub
# Uso: ./salvar-git.sh VERSAO
# Exemplo: ./salvar-git.sh 0.5

if [ $# -eq 0 ]; then
    echo "Erro: Informe a versão como parâmetro"
    echo "Uso: $0 VERSAO"
    echo "Exemplo: $0 0.5"
    exit 1
fi

VERSAO="$1"

echo "🔄 Salvando versão $VERSAO no GitHub..."

# Verificar se estamos em um repositório git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Erro: Não está em um repositório Git"
    exit 1
fi

# Verificar se há mudanças não commitadas
if [[ -n $(git status --porcelain) ]]; then
    echo "📦 Adicionando arquivos..."
    git add .

    echo "💾 Fazendo commit..."
    git commit -m "Release v$VERSAO"
else
    echo "ℹ️  Nenhum arquivo modificado para commit"
fi

# Verificar se existe remote origin
if ! git remote get-url origin > /dev/null 2>&1; then
    echo "Erro: Remote origin não configurado"
    echo "Configure com: git remote add origin https://github.com/ojaneri/traceguard.git"
    exit 1
fi

echo "⬆️  Enviando para o GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Versão $VERSAO salva com sucesso no GitHub!"
    echo "🌐 URL: https://github.com/ojaneri/traceguard"
else
    echo "❌ Erro ao enviar para o GitHub"
    exit 1
fi