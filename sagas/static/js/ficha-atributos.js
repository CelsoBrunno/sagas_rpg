// ==========================================
// Gerenciamento de Atributos
// ==========================================

// Controle de atributos com confirmação
const ATRIBUTOS_BASICOS = ['ST', 'DX', 'IQ', 'HT'];
let atributosOriginais = null;
let atributosPendentes = null;
let processamentoAtributos = false;
let timeoutMensagemAtributos = null;
let mensagemAtributosTravada = false;
let mensagemErroDetalheTravada = false;
let periciaPlanoEvolucao = null;
window.personagemId = window.personagemId || null;
window.pontosResumo = window.pontosResumo || {};
window.periciasDados = window.periciasDados || [];
window.personagemDinheiro = window.personagemDinheiro || 0;

function obterValorAtributoDoDOM(atributo) {
    const elemento = document.getElementById(`stat-${atributo}`);
    return elemento ? parseInt(elemento.textContent, 10) || 10 : 10;
}

function atualizarExibicaoAtributo(atributo, valor) {
    const elemento = document.getElementById(`stat-${atributo}`);
    if (elemento) {
        elemento.textContent = valor;
    }
}

function existemAlteracoesPendentes() {
    if (!atributosOriginais || !atributosPendentes) return false;
    return ATRIBUTOS_BASICOS.some(attr => atributosPendentes[attr] !== atributosOriginais[attr]);
}

function mostrarMensagemAtributos(mensagem, tipo = 'info', forcar = false) {
    const alerta = document.getElementById('atributos-alerta');
    if (!alerta) return;

    if (!forcar && mensagemAtributosTravada) {
        return;
    }

    if (timeoutMensagemAtributos) {
        clearTimeout(timeoutMensagemAtributos);
        timeoutMensagemAtributos = null;
    }

    if (!mensagem) {
        alerta.style.display = 'none';
        alerta.textContent = '';
        mensagemAtributosTravada = false;
        return;
    }

    const cores = {
        info: '#0d6efd',
        success: '#28a745',
        error: '#dc3545'
    };

    alerta.style.display = 'block';
    alerta.style.color = cores[tipo] || cores.info;
    alerta.textContent = mensagem;

    if (tipo === 'success' || tipo === 'error') {
        mensagemAtributosTravada = true;
        timeoutMensagemAtributos = setTimeout(() => {
            alerta.style.display = 'none';
            alerta.textContent = '';
            mensagemAtributosTravada = false;
        }, 4000);
    } else {
        mensagemAtributosTravada = false;
    }
}

function atualizarEstadoBotoesAtributos() {
    const btnConfirmar = document.getElementById('btn-confirmar-atributos');
    const btnCancelar = document.getElementById('btn-cancelar-atributos');
    const possuiPendencias = existemAlteracoesPendentes();

    if (btnConfirmar) {
        btnConfirmar.disabled = processamentoAtributos || !possuiPendencias;
    }
    if (btnCancelar) {
        btnCancelar.disabled = processamentoAtributos || !possuiPendencias;
    }

    if (processamentoAtributos) {
        mostrarMensagemAtributos('Aplicando alterações nos atributos...', 'info', true);
    } else if (possuiPendencias) {
        mostrarMensagemAtributos('Você possui alterações pendentes. Clique em "Confirmar Mudanças" para aplicar.', 'info', true);
    } else {
        if (!mensagemAtributosTravada) {
            mostrarMensagemAtributos('', 'info', true);
        }
    }
}

function alternarModoUpar() {
    const pagina = document.getElementById('personagem-page');
    const botao = document.getElementById('pontos-disponiveis-valor');
    if (!pagina || !botao || processamentoAtributos) {
        return;
    }

    const ativo = pagina.classList.toggle('modo-upar');
    botao.setAttribute('aria-pressed', ativo ? 'true' : 'false');
    if (!ativo && existemAlteracoesPendentes()) {
        cancelarMudancasAtributos();
    }
}

function inicializarControleAtributos() {
    const elementoST = document.getElementById('stat-ST');
    if (!elementoST) {
        return;
    }

    atributosOriginais = {};
    ATRIBUTOS_BASICOS.forEach(attr => {
        atributosOriginais[attr] = obterValorAtributoDoDOM(attr);
    });
    atributosPendentes = { ...atributosOriginais };
    definirErroAtributos(null);
    atualizarEstadoBotoesAtributos();
}

function alterarAtributo(atributo, delta) {
    if (!atributosPendentes || !ATRIBUTOS_BASICOS.includes(atributo)) {
        return;
    }

    if (mensagemErroDetalheTravada) {
        definirErroAtributos(null);
    }

    const valorAtual = atributosPendentes[atributo];
    const novoValor = Math.max(1, valorAtual + delta);

    if (novoValor === valorAtual) {
        return;
    }

    atributosPendentes[atributo] = novoValor;
    atualizarExibicaoAtributo(atributo, novoValor);
    atualizarEstadoBotoesAtributos();
}

async function confirmarMudancasAtributos() {
    if (!atributosPendentes || !existemAlteracoesPendentes()) {
        return;
    }

    if (!window.personagemId) {
        definirErroAtributos('Erro: personagem não identificado.');
        mostrarMensagemAtributos('Você possui alterações pendentes. Clique em "Confirmar Mudanças" para aplicar.', 'info', true);
        return;
    }

    processamentoAtributos = true;
    atualizarEstadoBotoesAtributos();

    try {
        const response = await fetch(`${API_BASE}/api/personagem/${window.personagemId}/atributos`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(atributosPendentes)
        });

        let data = {};
        try {
            data = await response.json();
        } catch (jsonError) {
            data = {};
        }

        if (!response.ok || !data.success) {
            const mensagem = data && data.message ? data.message : 'Erro ao atualizar atributos.';
            definirErroAtributos(mensagem);
            mostrarMensagemAtributos('Você possui alterações pendentes. Clique em "Confirmar Mudanças" para aplicar.', 'info', true);
            return;
        }

        // Atualiza estado local com valores confirmados
        if (data.atributos) {
            atributosOriginais = {
                ST: parseInt(data.atributos.ST, 10),
                DX: parseInt(data.atributos.DX, 10),
                IQ: parseInt(data.atributos.IQ, 10),
                HT: parseInt(data.atributos.HT, 10)
            };
        } else {
            atributosOriginais = { ...atributosPendentes };
        }

        atributosPendentes = { ...atributosOriginais };
        ATRIBUTOS_BASICOS.forEach(attr => atualizarExibicaoAtributo(attr, atributosOriginais[attr]));

        if (data.atributos_derivados) {
            atualizarAtributosDerivados(data.atributos_derivados);
        }

        if (data.pontos_resumo) {
            atualizarResumoPontos(data.pontos_resumo);
        }

        definirErroAtributos(null);
        mostrarMensagemAtributos('Atributos atualizados com sucesso!', 'success', true);
    } catch (error) {
        console.error('Erro ao atualizar atributos:', error);
        definirErroAtributos('Erro ao atualizar atributos. Verifique a conexão.');
        mostrarMensagemAtributos('Você possui alterações pendentes. Clique em "Confirmar Mudanças" para aplicar.', 'info', true);
    } finally {
        processamentoAtributos = false;
        atualizarEstadoBotoesAtributos();
    }
}

function cancelarMudancasAtributos() {
    if (!atributosOriginais || !atributosPendentes) {
        return;
    }

    atributosPendentes = { ...atributosOriginais };
    ATRIBUTOS_BASICOS.forEach(attr => atualizarExibicaoAtributo(attr, atributosOriginais[attr]));
    definirErroAtributos(null);
    mostrarMensagemAtributos('Alterações canceladas.', 'info', true);
    atualizarEstadoBotoesAtributos();
}

function atualizarAtributosDerivados(derivados) {
    if (derivados.PV) document.getElementById('derivado-PV').textContent = derivados.PV;
    if (derivados.PF) document.getElementById('derivado-PF').textContent = derivados.PF;
    if (derivados.percepcao) {
        const perEl = document.getElementById('derivado-Per');
        if (perEl) perEl.textContent = derivados.percepcao;
    }
    if (derivados.vontade) {
        const vtEl = document.getElementById('derivado-VT');
        if (vtEl) vtEl.textContent = derivados.vontade;
    }
    if (derivados.esquiva) document.getElementById('derivado-Esquiva').textContent = derivados.esquiva;
    if (derivados.velocidade_basica) document.getElementById('derivado-Velocidade').textContent = derivados.velocidade_basica;
    if (derivados.PM) document.getElementById('derivado-PM').textContent = derivados.PM;
}

function atualizarResumoPontos(pontos) {
    if (!pontos) {
        return;
    }

    window.pontosResumo = pontos;
    const elementoDisponiveis = document.getElementById('pontos-disponiveis-valor');
    if (elementoDisponiveis) {
        // Mostra os pontos do usuário (concedidos pelo admin) se disponíveis, senão mostra os pontos da ficha
        const pontosMostrar = (pontos.pontos_disponiveis_usuario !== undefined && pontos.pontos_disponiveis_usuario !== null) 
            ? pontos.pontos_disponiveis_usuario 
            : pontos.pontos_disponiveis;
        
        if (typeof pontosMostrar !== 'undefined') {
            elementoDisponiveis.textContent = pontosMostrar;
            
            // Atualiza cor do fundo baseado no valor
            const corFundo = pontosMostrar >= 0 ? '#28a745' : '#dc3545';
            elementoDisponiveis.style.background = corFundo;
        }
    }
}

function atualizarDinheiroDisponivel(valor) {
    const elemento = document.getElementById('dinheiro-disponivel-valor');
    if (elemento) {
        const numero = Number(valor) || 0;
        elemento.textContent = numero.toFixed(2);
    }
}

function abrirCatalogoPericias(personagemId) {
    modalPericiaPersonagemId = personagemId;
    const modal = document.getElementById('modal-catalogo-pericias');
    if (!modal) {
        alert('Modal de catálogo de perícias não encontrado.');
        return;
    }

    modal.style.display = 'block';

    // Se já carregamos anteriormente, apenas refiltra
    if (catalogoPericias.length > 0) {
        filtrarCatalogoPericias();
        return;
    }

    carregarCatalogoPericias();
}

function fecharCatalogoPericias() {
    const modal = document.getElementById('modal-catalogo-pericias');
    if (modal) {
        modal.style.display = 'none';
    }
    modalPericiaPersonagemId = null;
}

async function selecionarPericiaCatalogo(periciaId) {
    const item = catalogoPericias.find(p => p.id === periciaId);
    if (!item) {
        alert('Perícia não encontrada no catálogo.');
        return;
    }

    if (!modalPericiaPersonagemId) {
        alert('ID do personagem não encontrado. Reabra o catálogo.');
        return;
    }

    const sugestao = item.dificuldade === 'F' ? '1' : '1';
    const pontosTexto = prompt(
        `Quantos pontos investir em "${item.nome}"?\nSugestão: 1, 2, 4, 8... (conforme tabela GURPS)`, 
        sugestao
    );

    if (pontosTexto === null) {
        return; // usuário cancelou
    }

    const pontos = parseInt(pontosTexto, 10);
    if (!Number.isFinite(pontos) || pontos < 0) {
        alert('Informe um número inteiro válido de pontos a investir.');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/personagem/${modalPericiaPersonagemId}/pericias/by-catalog`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ catalogo_id: periciaId, pontos_investidos: pontos })
        });
        const data = await response.json();

        if (!response.ok || !data.success) {
            alert(data.message || 'Erro ao adicionar perícia do catálogo.');
            return;
        }

        location.reload();
    } catch (error) {
        console.error('Erro ao adicionar perícia a partir do catálogo:', error);
        alert('Erro ao adicionar perícia. Verifique a conexão.');
    }
}

function definirErroAtributos(mensagem) {
    const container = document.getElementById('card-controle-atributos');
    const detalhe = document.getElementById('atributos-erro-detalhe');
    if (!container || !detalhe) {
        return;
    }

    if (mensagem) {
        container.classList.add('erro');
        detalhe.textContent = mensagem;
        detalhe.style.display = 'block';
        mensagemErroDetalheTravada = true;
    } else {
        container.classList.remove('erro');
        detalhe.textContent = '';
        detalhe.style.display = 'none';
        mensagemErroDetalheTravada = false;
    }
}

function calcularProximoInvestimento(pontosAtuais) {
    if (pontosAtuais <= 0) {
        return 1;
    }
    if (pontosAtuais === 1) {
        return 2;
    }
    if (pontosAtuais === 2) {
        return 4;
    }
    return pontosAtuais + 4;
}

function abrirModalEvoluirPericia(periciaId) {
    if (!window.periciasDados || !Array.isArray(window.periciasDados)) {
        return;
    }

    const pericia = window.periciasDados.find(p => p.id === periciaId);
    if (!pericia) {
        return;
    }

    const pontosAtuais = parseInt(pericia.pontos_investidos || 0, 10);
    const pontosProximo = calcularProximoInvestimento(pontosAtuais);
    const custoAdicional = pontosProximo - pontosAtuais;
    const novoNH = (parseInt(pericia.nivel_habilidade_calculado || 0, 10) + 1);
    const pontosDisponiveis = window.pontosResumo ? parseInt(window.pontosResumo.pontos_disponiveis || 0, 10) : null;

    periciaPlanoEvolucao = {
        id: pericia.id,
        nome: pericia.nome_pericia,
        atributo_base: pericia.atributo_base,
        dificuldade: pericia.dificuldade,
        pontosAtuais,
        pontosProximo,
        custoAdicional,
        nhAtual: pericia.nivel_habilidade_calculado,
        nhNovo: novoNH
    };

    const modal = document.getElementById('modal-evoluir-pericia');
    const conteudo = document.getElementById('modal-evoluir-conteudo');
    const alerta = document.getElementById('modal-evoluir-alerta');
    if (!modal || !conteudo || !alerta) {
        return;
    }

    const mensagemDisponivel = pontosDisponiveis !== null
        ? `<li>Pontos disponíveis atuais: <strong>${pontosDisponiveis}</strong></li>`
        : '';

    conteudo.innerHTML = `
        <p style="margin-bottom: 1rem;">
            <strong>${pericia.nome_pericia}</strong><br>
            Atributo base: <strong>${pericia.atributo_base}</strong>
            ${pericia.dificuldade ? ` | Dificuldade: <strong>${pericia.dificuldade}</strong>` : ''}
        </p>
        <ul style="padding-left: 1.2rem; color: var(--cor-texto);">
            <li>Pontos: <strong>${pontosAtuais}</strong> + <strong>${custoAdicional}</strong> = <strong>${pontosProximo}</strong></li>
            <li>NH atual: <strong>${pericia.nivel_habilidade_calculado}</strong> -> <strong>${novoNH}</strong></li>
            ${mensagemDisponivel}
        </ul>
        <p style="margin-top: 1rem; font-size: 0.95rem; color: var(--cor-texto-claro);">
            Confirme os gastos de pontos para aplicar esta evolução.
        </p>
    `;

    alerta.style.display = 'none';
    alerta.textContent = '';

    modal.style.display = 'flex';
}

function fecharModalEvoluirPericia() {
    const modal = document.getElementById('modal-evoluir-pericia');
    const alerta = document.getElementById('modal-evoluir-alerta');
    if (modal) {
        modal.style.display = 'none';
    }
    if (alerta) {
        alerta.style.display = 'none';
        alerta.textContent = '';
    }
    periciaPlanoEvolucao = null;
    if (document.getElementById('btn-confirmar-evolucao')) {
        document.getElementById('btn-confirmar-evolucao').disabled = false;
    }
}

async function confirmarEvolucaoPericia() {
    if (!periciaPlanoEvolucao) {
        return;
    }

    const alerta = document.getElementById('modal-evoluir-alerta');
    const botao = document.getElementById('btn-confirmar-evolucao');
    if (botao) {
        botao.disabled = true;
    }

    try {
        const response = await fetch(`${API_BASE}/api/pericias/${periciaPlanoEvolucao.id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pontos_investidos: periciaPlanoEvolucao.pontosProximo })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            if (alerta) {
                alerta.style.display = 'block';
                alerta.textContent = data.message || 'Não foi possível evoluir a perícia.';
            }
            if (botao) {
                botao.disabled = false;
            }
            return;
        }

        if (window.pontosResumo) {
            window.pontosResumo.pontos_gastos = (window.pontosResumo.pontos_gastos || 0) + periciaPlanoEvolucao.custoAdicional;
            window.pontosResumo.pontos_disponiveis = (window.pontosResumo.pontos_disponiveis || 0) - periciaPlanoEvolucao.custoAdicional;
        }

        location.reload();
    } catch (error) {
        console.error('Erro ao evoluir perícia:', error);
        if (alerta) {
            alerta.style.display = 'block';
            alerta.textContent = 'Erro ao evoluir a perícia. Verifique sua conexão.';
        }
        if (botao) {
            botao.disabled = false;
        }
    }
}

// Funções removidas: atualizarPVPFExtra() e atualizarPerVtExtra()
// PV Extra, PF Extra, Percepção Extra e Vontade Extra
// só podem ser alterados através de vantagens do catálogo
