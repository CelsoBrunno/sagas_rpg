// Sistema de Abas
// ==========================================

function mostrarAba(abaNome, evt) {
    // Oculta todas as abas
    const abas = document.querySelectorAll('.tab-content');
    abas.forEach(aba => aba.classList.remove('active'));
    
    // Remove active de todos os botões
    const botoes = document.querySelectorAll('.tab-button');
    botoes.forEach(botao => botao.classList.remove('active'));
    
    // Mostra a aba selecionada
    document.getElementById(`tab-${abaNome}`).classList.add('active');
    
    // Ativa o botão selecionado
    const alvo = evt?.currentTarget || evt?.target || window.event?.target || null;
    if (alvo) {
        alvo.classList.add('active');
    }
}

// ==========================================
// Sistema de Rolagens de Dados
// ==========================================

/**
 * Executa uma rolagem de dados 3d6 contra um alvo
 * @param {number} alvo - O valor alvo (NH, atributo, etc)
 * @param {number} bonus - Bonus adicional
 * @param {string} nome - Nome da rolagem (para exibição)
 */
async function rolarDados(alvo, bonus = 0, nome = 'Rolagem') {
    try {
        const response = await fetch(`${API_BASE}/api/rolar/${alvo}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ bonus, personagem_id: window.personagemId || null })
        });
        
        const resultado = await response.json();
        
        exibirRolagem(nome, resultado);
        
        return resultado;
    } catch (error) {
        console.error('Erro ao rolar dados:', error);
        alert('Erro ao rolar dados. Verifique a conexão.');
    }
}

/**
 * Exibe o resultado de uma rolagem na área de resultados
 */
function exibirRolagem(nome, resultado) {
    // Mostra a área de rolagem se estiver oculta
    const areaRolagem = document.getElementById('area-rolagem');
    if (areaRolagem) {
        areaRolagem.style.display = 'block';
    }
    
    // Cria o elemento de resultado
    const resultadosDiv = document.getElementById('resultados-rolagem');
    const resultadoElement = document.createElement('div');
    
    // Determina a classe CSS baseado no resultado
    let classeResultado = resultado.sucesso ? 'rolagem-sucesso' : 'rolagem-falha';
    let textoResultado = resultado.sucesso ? '✓ Sucesso!' : '✗ Falha!';
    
    if (resultado.resultado === 'crítico') {
        classeResultado = 'rolagem-sucesso';
        textoResultado = '🎯 Crítico!';
    } else if (resultado.resultado === 'falha_crítica') {
        classeResultado = 'rolagem-falha';
        textoResultado = '💀 Falha Crítica!';
    }
    
    resultadoElement.className = `rolagem-resultado ${classeResultado}`;
    resultadoElement.innerHTML = `
        <strong>${nome}</strong> (Alvo: ${resultado.alvo})<br>
        Dados: <span class="rolagem-dados">[${resultado.resultados.join(', ')}]</span> 
        = <strong>${resultado.total}</strong>
        ${resultado.bonus !== 0 ? ` +${resultado.bonus}` : ''}<br>
        ${textoResultado}
    `;
    
    // Adiciona no topo
    resultadosDiv.insertBefore(resultadoElement, resultadosDiv.firstChild);
    
    // Limita a 10 resultados
    const resultados = resultadosDiv.querySelectorAll('.rolagem-resultado');
    if (resultados.length > 10) {
        resultados[resultados.length - 1].remove();
    }
}

// ==========================================
// Funções de Rolagem Específicas
// ==========================================

function rolarAtributo(nomeAtributo, valor) {
    rolarDados(valor, 0, nomeAtributo);
}

function rolarPericia(nomePericia, NH) {
    rolarDados(NH, 0, nomePericia);
}
