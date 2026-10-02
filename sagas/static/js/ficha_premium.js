// ==========================================
// Ficha Premium - JavaScript para Edição
// ==========================================

const personagemId = window.personagemId;

// Salvar atributos
function salvarAtributo(atributo, valor) {
    if (!personagemId) return;
    
    const atributosAtuais = {
        ST: parseInt(document.querySelector('[data-attr="ST"] input')?.value || 10),
        DX: parseInt(document.querySelector('[data-attr="DX"] input')?.value || 10),
        IQ: parseInt(document.querySelector('[data-attr="IQ"] input')?.value || 10),
        HT: parseInt(document.querySelector('[data-attr="HT"] input')?.value || 10)
    };
    
    atributosAtuais[atributo] = parseInt(valor) || 10;
    
    fetch(`/api/personagem/${personagemId}/atributos`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(atributosAtuais)
    })
    .then(r => r.json())
    .then(data => {
        if (data.success && data.atributos_derivados) {
            // Atualiza valores derivados na tela
            atualizarDerivados(data.atributos_derivados);
        }
    })
    .catch(e => console.error('Erro ao salvar:', e));
}

// Atualiza atributos derivados na interface
function atualizarDerivados(derivados) {
    if (derivados.PV) {
        const pvInput = document.getElementById('pv-atual');
        if (pvInput && !pvInput.value) pvInput.value = derivados.PV;
        const pvTotal = document.getElementById('pv-total');
        if (pvTotal) pvTotal.textContent = derivados.PV;
    }
    if (derivados.PF) {
        const pfInput = document.getElementById('pf-atual');
        if (pfInput && !pfInput.value) pfInput.value = derivados.PF;
        const pfTotal = document.getElementById('pf-total');
        if (pfTotal) pfTotal.textContent = derivados.PF;
    }
    if (derivados.esquiva) {
        const esquivaEl = document.getElementById('esquiva-valor');
        if (esquivaEl) esquivaEl.textContent = derivados.esquiva;
    }
    if (derivados.deslocamento) {
        const deslocEl = document.getElementById('deslocamento-valor');
        if (deslocEl) deslocEl.textContent = derivados.deslocamento;
    }
    if (derivados.percepcao) {
        const perEl = document.getElementById('percepcao-valor');
        if (perEl) perEl.textContent = derivados.percepcao;
    }
}

// Upload de imagem do personagem
function uploadImagemPersonagem(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('entidade_tipo', 'Personagem');
    formData.append('entidade_id', personagemId);
    formData.append('titulo', 'Imagem Principal');
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erro ao fazer upload: ' + data.message);
        }
    })
    .catch(e => {
        console.error('Erro:', e);
        alert('Erro ao fazer upload da imagem');
    });
}

// Salvar biografia
function salvarBiografia() {
    const texto = document.getElementById('biografia-text').value;
    fetch(`/api/personagem/${personagemId}/biografia`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ biografia: texto })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            mostrarNotificacao('Biografia salva!');
        }
    });
}

// Salvar observações
function salvarObservacoes() {
    const texto = document.getElementById('observacoes-text').value;
    fetch(`/api/personagem/${personagemId}/observacoes`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ observacoes: texto })
    })
    .then(r => r.json())
    .then(data => {
        if (data.success) {
            mostrarNotificacao('Observações salvas!');
        }
    });
}

// Notificação visual
function mostrarNotificacao(mensagem, tipo = 'success') {
    const cores = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    
    const notif = document.createElement('div');
    notif.style.cssText = `position: fixed; top: 20px; right: 20px; background: ${cores[tipo] || cores.success}; color: white; padding: 15px 25px; border-radius: 5px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); z-index: 10000; font-weight: bold; animation: slideIn 0.3s ease-out;`;
    notif.textContent = mensagem;
    
    // Animação CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notif);
    setTimeout(() => {
        notif.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => notif.remove(), 300);
    }, 3000);
}

// Exportar função globalmente
window.mostrarNotificacao = mostrarNotificacao;

// ==========================================
// Sistema de Rolagens Interativas
// ==========================================

/**
 * Rola uma perícia contra seu nível de habilidade
 */
async function rolarPericia(nome, nh) {
    if (!personagemId) {
        mostrarNotificacao('Erro: Personagem não identificado', 'error');
        return;
    }
    
    try {
        const bonus = prompt(`Rolagem de ${nome}\nNH: ${nh}\n\nDigite bônus adicional (ou 0):`, '0');
        const bonusNum = parseInt(bonus) || 0;
        
        const response = await fetch(`/api/rolar/${nh}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                bonus: bonusNum,
                personagem_id: personagemId
            })
        });
        
        const resultado = await response.json();
        exibirResultadoRolagem(nome, nh, resultado, bonusNum);
        
    } catch (error) {
        console.error('Erro ao rolar perícia:', error);
        mostrarNotificacao('Erro ao rolar dados', 'error');
    }
}

/**
 * Rola um teste de atributo
 */
async function rolarAtributo(nome, valor) {
    if (!personagemId) {
        mostrarNotificacao('Erro: Personagem não identificado', 'error');
        return;
    }
    
    try {
        const bonus = prompt(`Teste de ${nome}\nValor: ${valor}\n\nDigite bônus adicional (ou 0):`, '0');
        const bonusNum = parseInt(bonus) || 0;
        
        const response = await fetch(`/api/rolar/${valor}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                bonus: bonusNum,
                personagem_id: personagemId
            })
        });
        
        const resultado = await response.json();
        exibirResultadoRolagem(nome, valor, resultado, bonusNum);
        
    } catch (error) {
        console.error('Erro ao rolar atributo:', error);
        mostrarNotificacao('Erro ao rolar dados', 'error');
    }
}

/**
 * Exibe resultado da rolagem em modal customizado
 */
function exibirResultadoRolagem(nome, alvo, resultado, bonus) {
    const modal = document.createElement('div');
    modal.className = 'modal-rolagem';
    modal.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: linear-gradient(135deg, #f5e6d3 0%, #e8d5b8 100%);
        border: 3px solid #8b6914;
        border-radius: 10px;
        padding: 30px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        z-index: 10000;
        min-width: 300px;
        text-align: center;
    `;
    
    const corResultado = resultado.sucesso ? '#28a745' : '#dc3545';
    const icone = resultado.resultado === 'crítico' ? '✨' : 
                  resultado.resultado === 'falha_crítica' ? '💥' : 
                  resultado.sucesso ? '✓' : '✗';
    
    modal.innerHTML = `
        <h3 style="margin-top: 0; color: #8b6914; font-family: 'Cinzel', serif;">${icone} ${nome}</h3>
        <div style="font-size: 48px; font-weight: bold; color: ${corResultado}; margin: 20px 0;">
            ${resultado.total}
        </div>
        <div style="color: #6b4e2e; margin-bottom: 10px;">
            <strong>Alvo:</strong> ${alvo}
            ${bonus !== 0 ? `<br><strong>Bônus:</strong> ${bonus > 0 ? '+' : ''}${bonus}` : ''}
        </div>
        <div style="color: #6b4e2e; margin-bottom: 10px;">
            <strong>Dados:</strong> ${resultado.resultados.join(' + ')} = ${resultado.total - bonus}
            ${bonus !== 0 ? ` + ${bonus}` : ''}
        </div>
        <div style="font-size: 18px; font-weight: bold; color: ${corResultado}; margin: 15px 0; padding: 10px; background: rgba(139,105,20,0.1); border-radius: 5px;">
            ${resultado.resultado === 'crítico' ? '✨ Sucesso Crítico!' : 
              resultado.resultado === 'falha_crítica' ? '💥 Falha Crítica!' : 
              resultado.sucesso ? '✓ Sucesso!' : '✗ Falha'}
        </div>
        <button onclick="this.parentElement.remove()" style="
            background: linear-gradient(135deg, #8b6914 0%, #6b4e2e 100%);
            color: white;
            border: none;
            padding: 10px 30px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
            margin-top: 10px;
        ">Fechar</button>
    `;
    
    document.body.appendChild(modal);
    
    // Fecha ao clicar fora (opcional)
    setTimeout(() => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) modal.remove();
        });
    }, 100);
}

// Exportar funções globalmente
window.rolarPericia = rolarPericia;
window.rolarAtributo = rolarAtributo;

// Debounce para salvar
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Salvar PV atual
function salvarPVAtual() {
    const valor = parseInt(document.getElementById('pv-atual').value) || 0;
    // Pode salvar em localStorage ou enviar para servidor
    localStorage.setItem(`pv_${personagemId}`, valor);
}

// Salvar PF atual
function salvarPFAtual() {
    const valor = parseInt(document.getElementById('pf-atual').value) || 0;
    localStorage.setItem(`pf_${personagemId}`, valor);
}

// Carregar valores salvos ao carregar página
document.addEventListener('DOMContentLoaded', function() {
    if (personagemId) {
        const pvSalvo = localStorage.getItem(`pv_${personagemId}`);
        const pfSalvo = localStorage.getItem(`pf_${personagemId}`);
        
        const pvInput = document.getElementById('pv-atual');
        const pfInput = document.getElementById('pf-atual');
        
        if (pvSalvo && pvInput && !pvInput.value) pvInput.value = pvSalvo;
        if (pfSalvo && pfInput && !pfInput.value) pfInput.value = pfSalvo;
    }
});

// Exportar funções
window.salvarAtributo = salvarAtributo;
window.uploadImagemPersonagem = uploadImagemPersonagem;
window.salvarBiografia = salvarBiografia;
window.salvarObservacoes = salvarObservacoes;
window.salvarPVAtual = salvarPVAtual;
window.salvarPFAtual = salvarPFAtual;

