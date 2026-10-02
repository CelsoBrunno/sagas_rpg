// ==========================================
// Sistema de Campanha GURPS - JavaScript
// ==========================================

// Configuração global
const API_BASE = window.location.origin;

// ==========================================
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

// ==========================================
// Gerenciamento de Vantagens
// ==========================================

// Função removida: adicionarVantagem
// Agora as vantagens são adicionadas apenas através do catálogo pré-cadastrado
// via função selecionarVDCatalogo()

// Catálogo de Vantagens e Desvantagens
let catalogoVD = [];
let catalogoVDFiltrado = [];
let catalogoPericias = [];
let catalogoPericiasFiltrado = [];
let catalogoItens = [];
let catalogoItensFiltrado = [];
let catalogoCategoriasFiltro = null;
let catalogoTipoFiltro = null;
let modalPericiaPersonagemId = null;
let modalItemPersonagemId = null;
let personagemDinheiro = 0;

async function carregarCatalogoVD() {
    const container = document.getElementById('lista-catalogo-vd');
    if (!container) return;
    
    // Mostra mensagem de carregamento
    container.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">⏳ Carregando catálogo...</p>';
    
    try {
        const response = await fetch(`${API_BASE}/api/vantagens-desvantagens/catalogo`);
        
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        
        catalogoVD = await response.json();
        
        if (!Array.isArray(catalogoVD)) {
            throw new Error('Resposta da API não é um array');
        }
        
        catalogoVDFiltrado = catalogoVD;
        renderizarCatalogoVD();
    } catch (error) {
        console.error('Erro ao carregar catálogo:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #dc3545;">
                <p>❌ Erro ao carregar catálogo.</p>
                <p style="font-size: 0.9em; margin-top: 0.5rem;">${error.message}</p>
                <button onclick="carregarCatalogoVD()" class="btn-primary" style="margin-top: 1rem;">Tentar Novamente</button>
            </div>
        `;
    }
}

function renderizarCatalogoVD() {
    const container = document.getElementById('lista-catalogo-vd');
    if (!container) return;
    
    if (!catalogoVDFiltrado || catalogoVDFiltrado.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #666;">
                <p>📋 Nenhum item encontrado no catálogo.</p>
                <p style="font-size: 0.9em; margin-top: 0.5rem;">O catálogo pode estar vazio. Verifique se há vantagens/desvantagens cadastradas.</p>
            </div>
        `;
        return;
    }
    
    let html = '<table class="table-gurps" style="width: 100%;">';
    html += '<thead><tr><th>Nome</th><th>Tipo</th><th>Custo</th><th>Descrição</th><th>Ação</th></tr></thead><tbody>';
    
    catalogoVDFiltrado.forEach(item => {
        const tipoClass = item.tipo === 'Vantagem' ? 'text-success' : 'text-danger';
        const tipoColor = item.tipo === 'Vantagem' ? '#28a745' : '#dc3545';
        const custoDisplay = item.custo_texto || `${item.custo_base} pontos`;
        const descricao = item.descricao || '-';
        const descricaoTruncada = descricao.length > 100 ? descricao.substring(0, 100) + '...' : descricao;
        
        html += `
            <tr>
                <td><strong>${item.nome || 'Sem nome'}</strong></td>
                <td><span style="color: ${tipoColor}; font-weight: 600;">${item.tipo || 'N/A'}</span></td>
                <td>${custoDisplay}</td>
                <td style="font-size: 0.9em; color: #666;" title="${descricao}">${descricaoTruncada}</td>
                <td>
                    <button onclick="selecionarVDCatalogo(${item.id})" class="btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.9em;">
                        Selecionar
                    </button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    html += `<p style="text-align: center; margin-top: 1rem; color: #666; font-size: 0.9em;">Total: ${catalogoVDFiltrado.length} item(ns)</p>`;
    container.innerHTML = html;
}

function filtrarCatalogoVD() {
    const busca = document.getElementById('busca-vd').value.toLowerCase();
    const tipoFiltro = document.getElementById('filtro-tipo-vd')?.value || '';
    
    catalogoVDFiltrado = catalogoVD.filter(item => {
        const matchNome = item.nome.toLowerCase().includes(busca);
        const matchTipo = !tipoFiltro || item.tipo === tipoFiltro;
        return matchNome && matchTipo;
    });
    
    renderizarCatalogoVD();
}

function filtrarTipoVD(tipo) {
    document.getElementById('filtro-tipo-vd')?.remove();
    const filtro = document.createElement('input');
    filtro.type = 'hidden';
    filtro.id = 'filtro-tipo-vd';
    filtro.value = tipo;
    document.getElementById('modal-catalogo-vd').appendChild(filtro);
    
    catalogoVDFiltrado = tipo ? catalogoVD.filter(item => item.tipo === tipo) : catalogoVD;
    
    const busca = document.getElementById('busca-vd').value.toLowerCase();
    if (busca) {
        catalogoVDFiltrado = catalogoVDFiltrado.filter(item => 
            item.nome.toLowerCase().includes(busca)
        );
    }
    
    renderizarCatalogoVD();
}

// Armazena o ID do personagem atual para adicionar vantagens
let personagemIdAtual = null;

async function selecionarVDCatalogo(itemId) {
    const item = catalogoVD.find(vd => vd.id === itemId);
    if (!item) return;
    
    if (!personagemIdAtual) {
        // Tenta pegar do window.personagemId se disponível
        personagemIdAtual = window.personagemId;
    }
    
    if (!personagemIdAtual) {
        alert('Erro: ID do personagem não encontrado.');
        return;
    }
    
    // Pergunta o custo em pontos (pode ser diferente do custo base)
    let custo = item.custo_base;
    if (item.custo_texto && (item.custo_texto.toLowerCase().includes('variável') || item.custo_texto.toLowerCase().includes('variável'))) {
        const custoInput = prompt(`Digite o custo em pontos para "${item.nome}":`, item.custo_base);
        if (custoInput === null) {
            // Usuário cancelou
            return;
        }
        custo = parseInt(custoInput || item.custo_base);
        if (isNaN(custo)) {
            alert('Custo inválido. Operação cancelada.');
            return;
        }
    }
    
    // Pergunta se deseja adicionar notas
    const notas = prompt(`Adicionar notas para "${item.nome}"? (opcional):`, '') || '';
    
    try {
        const response = await fetch(`${API_BASE}/api/personagem/${personagemIdAtual}/vantagens`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nome_item: item.nome,
                custo_em_pontos: custo,
                notas: notas
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            fecharCatalogoVD();
            // Recarrega a página para mostrar a nova vantagem
            location.reload();
        } else {
            alert(data.message || 'Erro ao adicionar vantagem/desvantagem.');
        }
    } catch (error) {
        console.error('Erro ao adicionar vantagem:', error);
        alert('Erro ao adicionar vantagem. Verifique a conexão.');
    }
}

function abrirCatalogoVD(personagemId) {
    const modal = document.getElementById('modal-catalogo-vd');
    if (modal) {
        // Armazena o ID do personagem
        personagemIdAtual = personagemId || window.personagemId;
        
        modal.style.display = 'block';
        
        // Sempre tenta carregar o catálogo quando o modal abre
        // Isso garante que os dados estejam atualizados
        carregarCatalogoVD();
    }
}

function fecharCatalogoVD() {
    const modal = document.getElementById('modal-catalogo-vd');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function deletarVantagem(vantagemId) {
    if (!confirm('Remover desvantagem? Será necessário pagar 1.5x o valor em pontos.')) {
        return;
    }
    const pontos = parseInt(prompt('Informe quantos pontos você vai pagar (mínimo 1.5x do valor absoluto da desvantagem):', '0') || '0', 10);
    
    try {
        const response = await fetch(`${API_BASE}/api/vantagens/${vantagemId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pontos_pagados: pontos })
        });
        
        const data = await response.json();
        
        if (data.success) {
            location.reload();
        } else {
            alert(data.message || 'Erro ao remover vantagem');
        }
    } catch (error) {
        console.error('Erro ao deletar vantagem:', error);
        alert('Erro ao remover vantagem. Verifique a conexão.');
    }
}

// ==========================================
// Gerenciamento de Perícias
// ==========================================

async function carregarCatalogoPericias() {
    const container = document.getElementById('lista-catalogo-pericias');
    if (!container) return;

    container.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">⏳ Carregando catálogo...</p>';

    try {
        const response = await fetch(`${API_BASE}/api/pericias/catalogo`);
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const itens = await response.json();
        if (!Array.isArray(itens)) {
            throw new Error('Resposta da API não é um array válido.');
        }

        catalogoPericias = itens;
        catalogoPericiasFiltrado = itens;
        renderizarCatalogoPericias();
    } catch (error) {
        console.error('Erro ao carregar catálogo de perícias:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #dc3545;">
                <p>❌ Erro ao carregar o catálogo de perícias.</p>
                <p style="font-size: 0.9em; margin-top: 0.5rem;">${error.message}</p>
                <button onclick="carregarCatalogoPericias()" class="btn-primary" style="margin-top: 1rem;">Tentar Novamente</button>
            </div>
        `;
    }
}

function renderizarCatalogoPericias() {
    const container = document.getElementById('lista-catalogo-pericias');
    if (!container) return;

    if (!catalogoPericiasFiltrado || catalogoPericiasFiltrado.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #666;">
                <p>📋 Nenhuma perícia encontrada no catálogo.</p>
                <p style="font-size: 0.9em; margin-top: 0.5rem;">Ajuste os filtros ou verifique se o catálogo está populado.</p>
            </div>
        `;
        return;
    }

    const dificuldadeLabel = {
        'F': 'Fácil',
        'M': 'Média',
        'D': 'Difícil',
        'VD': 'Muito Difícil'
    };

    let html = '<table class="table-gurps" style="width: 100%;">';
    html += '<thead><tr><th>Perícia</th><th>Atributo</th><th>Dificuldade</th><th>Descrição</th><th>Ação</th></tr></thead><tbody>';

    catalogoPericiasFiltrado.forEach(item => {
        const dificuldade = dificuldadeLabel[item.dificuldade] || item.dificuldade || '-';
        const descricao = item.descricao || '-';
        const descricaoTruncada = descricao.length > 140 ? `${descricao.substring(0, 140)}...` : descricao;

        html += `
            <tr>
                <td><strong>${item.nome}</strong></td>
                <td>${item.atributo_base}</td>
                <td>${dificuldade}</td>
                <td style="font-size: 0.9em; color: #666;" title="${descricao}">${descricaoTruncada}</td>
                <td>
                    <button onclick="selecionarPericiaCatalogo(${item.id})" class="btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.9em;">
                        Adicionar
                    </button>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    html += `<p style="text-align: center; margin-top: 1rem; color: #666; font-size: 0.9em;">Total: ${catalogoPericiasFiltrado.length} perícia(s)</p>`;

    container.innerHTML = html;
}

function filtrarCatalogoPericias() {
    const busca = document.getElementById('busca-pericia')?.value.toLowerCase() || '';
    const tipo = document.getElementById('filtro-tipo-pericia')?.value || '';

    catalogoPericiasFiltrado = catalogoPericias.filter(item => {
        const matchNome = item.nome.toLowerCase().includes(busca);
        const matchTipo = !tipo || item.dificuldade === tipo;
        return matchNome && matchTipo;
    });

    renderizarCatalogoPericias();
}

function filtrarTipoPericia(tipo) {
    document.getElementById('filtro-tipo-pericia')?.remove();
    const filtro = document.createElement('input');
    filtro.type = 'hidden';
    filtro.id = 'filtro-tipo-pericia';
    filtro.value = tipo;
    document.getElementById('modal-catalogo-pericias')?.appendChild(filtro);

    filtrarCatalogoPericias();
}

// ==========================================
// Catálogo de Itens
// ==========================================

async function carregarCatalogoItens() {
    const container = document.getElementById('lista-catalogo-itens');
    if (!container) return;

    container.innerHTML = '<p style="text-align: center; padding: 2rem; color: #666;">⏳ Carregando catálogo...</p>';

    try {
        const response = await fetch(`${API_BASE}/api/itens/catalogo`);
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }

        const itens = await response.json();
        if (!Array.isArray(itens)) {
            throw new Error('Resposta da API não é um array válido.');
        }

        catalogoItens = itens;
        catalogoItensFiltrado = itens;
        renderizarCatalogoItens();
    } catch (error) {
        console.error('Erro ao carregar catálogo de itens:', error);
        container.innerHTML = `
            <div style="text-align:center; padding:2rem; color:#dc3545;">
                <p>❌ Erro ao carregar o catálogo de itens.</p>
                <p style="font-size:0.9em; margin-top:0.5rem;">${error.message}</p>
                <button onclick="carregarCatalogoItens()" class="btn-primary" style="margin-top:1rem;">Tentar Novamente</button>
            </div>
        `;
    }
}

function renderizarCatalogoItens() {
    const container = document.getElementById('lista-catalogo-itens');
    if (!container) return;

    if (!catalogoItensFiltrado || catalogoItensFiltrado.length === 0) {
        container.innerHTML = `
            <div style="text-align:center; padding:2rem; color:#666;">
                <p>📋 Nenhum item encontrado no catálogo.</p>
                <p style="font-size:0.9em; margin-top:0.5rem;">Ajuste os filtros ou verifique se o catálogo está populado.</p>
            </div>
        `;
        return;
    }

    let html = '<div style="overflow-x:auto;"><table class="table-gurps" style="width: 100%; table-layout: auto; font-size:0.85em;">';
    html += '<thead><tr><th style="min-width:120px; padding:0.5rem;">Item</th><th style="width:60px; padding:0.5rem;">Slot</th><th style="min-width:100px; padding:0.5rem;">Categoria</th><th style="width:70px; padding:0.5rem;">Dano (Bal)</th><th style="width:70px; padding:0.5rem;">Dano (GdP)</th><th style="width:70px; padding:0.5rem;">Peso</th><th style="width:100px; padding:0.5rem;">Preço</th><th style="width:80px; padding:0.5rem;">Detalhes</th><th style="width:90px; padding:0.5rem;">Ação</th></tr></thead><tbody>';

    catalogoItensFiltrado.forEach(item => {
        const preco = Number(item.preco || 0).toFixed(2);
        const peso = Number(item.peso || 0).toFixed(2);
        let categoria = item.categoria || '-';
        
        // Limpar prefixos de categoria como na tabela de equipamentos
        if (categoria !== '-') {
            categoria = categoria.replace(/^Armas à /, '');
            categoria = categoria.replace(/^Armas /, '');
        }
        
        // Formatar dano Bal
        const danoBalMod = item.dano_bal_mod != null ? Number(item.dano_bal_mod) : 0;
        const danoBal = danoBalMod !== 0 ? (danoBalMod > 0 ? `+${danoBalMod}` : `${danoBalMod}`) : '-';
        
        // Formatar dano GdP
        const danoGdpMod = item.dano_gdp_mod != null ? Number(item.dano_gdp_mod) : 0;
        const danoGdp = danoGdpMod !== 0 ? (danoGdpMod > 0 ? `+${danoGdpMod}` : `${danoGdpMod}`) : '-';
        
        // Armazenar dados do item para o modal
        const descricao = item.descricao || '';
        const temDetalhes = descricao && descricao !== '-';

        html += `
            <tr style="font-size:0.9em;">
                <td style="font-weight:600; padding:0.5rem;">${item.nome}</td>
                <td style="text-align:center; padding:0.5rem;">-</td>
                <td style="padding:0.5rem;">${categoria}</td>
                <td style="text-align:center; padding:0.5rem;">${danoBal}</td>
                <td style="text-align:center; padding:0.5rem;">${danoGdp}</td>
                <td style="text-align:right; padding:0.5rem;">${peso}</td>
                <td style="text-align:right; padding:0.5rem;">₣ ${preco}</td>
                <td style="text-align:center; padding:0.5rem;">
                    ${temDetalhes ? `
                        <button onclick="abrirModalDetalhesItem(${item.id})" class="btn-secondary" style="padding:0.25rem 0.5rem; font-size:0.75em; cursor:pointer; border:1px solid #ddd; background:#f8f9fa; color:#333; border-radius:4px;" title="Ver detalhes">
                            Detalhes
                        </button>
                    ` : '<span style="color:#999; font-size:0.85em;">-</span>'}
                </td>
                <td style="text-align:center; padding:0.5rem;">
                    <button onclick="selecionarItemCatalogo(${item.id})" class="btn-primary" style="padding:0.25rem 0.5rem; font-size:0.85em;">
                        Comprar
                    </button>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table></div>';
    html += `<p style="text-align:center; margin-top:1rem; color:#666; font-size:0.9em;">Total: ${catalogoItensFiltrado.length} item(ns)</p>`;

    container.innerHTML = html;
}

function filtrarCatalogoItens() {
    const busca = document.getElementById('busca-item')?.value.toLowerCase() || '';
    const categoriaInput = document.getElementById('filtro-categoria-item');
    const categoria = categoriaInput?.value || '';

    catalogoItensFiltrado = catalogoItens.filter(item => {
        const nomeLower = (item.nome || '').toLowerCase();
        const categoriaLower = (item.categoria || '').toLowerCase();
        const descricaoLower = (item.descricao || '').toLowerCase();

        const matchNome = nomeLower.includes(busca) || categoriaLower.includes(busca) || descricaoLower.includes(busca);
        let matchCategoria = true;
        const itemCategoria = item.categoria || '';

        if (Array.isArray(catalogoCategoriasFiltro) && catalogoCategoriasFiltro.length > 0) {
            matchCategoria = catalogoCategoriasFiltro.includes(itemCategoria);
        } else if (categoria) {
            matchCategoria = itemCategoria === categoria;
        }

        const tipoItem = (item.tipo_item || 'outro').toLowerCase();
        const matchTipo = !catalogoTipoFiltro || tipoItem === catalogoTipoFiltro;

        return matchNome && matchCategoria && matchTipo;
    });

    renderizarCatalogoItens();
}

function filtrarCategoriaItem(categoria) {
    document.getElementById('filtro-categoria-item')?.remove();
    const filtro = document.createElement('input');
    filtro.type = 'hidden';
    filtro.id = 'filtro-categoria-item';
    filtro.value = categoria;
    document.getElementById('modal-catalogo-itens')?.appendChild(filtro);
    catalogoCategoriasFiltro = categoria ? [categoria] : null;
    catalogoTipoFiltro = null;
    filtrarCatalogoItens();
}

function filtrarCategoriasItens(listaCategorias) {
    document.getElementById('filtro-categoria-item')?.remove();
    catalogoCategoriasFiltro = Array.isArray(listaCategorias) ? listaCategorias : null;
    catalogoTipoFiltro = null;
    filtrarCatalogoItens();
}

async function abrirCatalogoItens(personagemId) {
    const modal = document.getElementById('modal-catalogo-itens');
    if (!modal) {
        alert('Modal de catálogo de itens não encontrado.');
        return;
    }

    modalItemPersonagemId = personagemId || window.personagemId;
    modal.style.display = 'block';

    catalogoCategoriasFiltro = null;
    catalogoTipoFiltro = null;
    // Sempre recarrega o catálogo para garantir que novos itens apareçam
    await carregarCatalogoItens();
    filtrarCatalogoItens();
}

function fecharCatalogoItens() {
    const modal = document.getElementById('modal-catalogo-itens');
    if (modal) {
        modal.style.display = 'none';
    }
    modalItemPersonagemId = null;
    catalogoCategoriasFiltro = null;
    catalogoTipoFiltro = null;
}

async function abrirCatalogoConsumiveis(personagemId) {
    const modal = document.getElementById('modal-catalogo-itens');
    if (!modal) {
        alert('Modal de catálogo de itens não encontrado.');
        return;
    }
    modalItemPersonagemId = personagemId || window.personagemId;
    modal.style.display = 'block';
    catalogoCategoriasFiltro = null;
    catalogoTipoFiltro = 'consumivel';
    // Sempre recarrega o catálogo para garantir que novos itens apareçam
    await carregarCatalogoItens();
    filtrarCatalogoItens();
}

async function abrirCatalogoEquipamentos(personagemId) {
    const modal = document.getElementById('modal-catalogo-itens');
    if (!modal) {
        alert('Modal de catálogo de itens não encontrado.');
        return;
    }
    modalItemPersonagemId = personagemId || window.personagemId;
    modal.style.display = 'block';
    catalogoCategoriasFiltro = null;
    catalogoTipoFiltro = 'equipamento';
    // Sempre recarrega o catálogo para garantir que novos itens apareçam
    await carregarCatalogoItens();
    filtrarCatalogoItens();
}

function escaparHtml(texto) {
    if (!texto) return '';
    const div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
}

function abrirModalDetalhesItem(itemId) {
    const item = catalogoItens.find(elem => elem.id === itemId);
    if (!item) {
        alert('Item não encontrado no catálogo.');
        return;
    }

    const descricao = item.descricao || '';
    const nomeItem = escaparHtml(item.nome || 'Item sem nome');
    
    // Processar efeitos (dividir descrição por pontos)
    let efeitosLista = [];
    if (descricao && descricao !== '-') {
        const descricaoLimpa = descricao.trim();
        const partes = descricaoLimpa.split(/\.\s+/).filter(p => p.trim().length > 0);
        
        if (partes.length > 1) {
            efeitosLista = partes.map(p => {
                const efeito = p.trim();
                return efeito.endsWith('.') ? efeito : efeito + '.';
            });
        } else if (partes.length === 1) {
            const efeito = partes[0].trim();
            efeitosLista = [efeito.endsWith('.') ? efeito : efeito + '.'];
        } else {
            efeitosLista = [descricaoLimpa.endsWith('.') ? descricaoLimpa : descricaoLimpa + '.'];
        }
    }

    // Criar HTML do modal
    const modal = document.getElementById('modal-detalhes-item');
    if (!modal) {
        alert('Modal de detalhes não encontrado.');
        return;
    }

    const modalContent = document.getElementById('modal-detalhes-item-content');
    if (modalContent) {
        let efeitosHtml = '<p style="color:#999; font-style:italic;">Sem efeitos catalogados.</p>';
        if (efeitosLista.length > 0) {
            efeitosHtml = `<ul style="margin:0; padding-left:1.5rem; line-height:1.8;">${efeitosLista.map(efeito => `<li>${escaparHtml(efeito)}</li>`).join('')}</ul>`;
        }

        const descricaoEscapada = escaparHtml(descricao || 'Sem notas adicionais.');

        modalContent.innerHTML = `
            <h3 style="margin-top:0; margin-bottom:1rem; color:#333;">${nomeItem}</h3>
            <div style="margin-bottom:1.5rem;">
                <h4 style="margin:0 0 0.5rem 0; color:#555; font-size:1em; font-weight:600;">Efeitos:</h4>
                <div style="background:#f8f9fa; padding:1rem; border-radius:6px; border-left:4px solid #0066CC;">
                    ${efeitosHtml}
                </div>
            </div>
            <div>
                <h4 style="margin:0 0 0.5rem 0; color:#555; font-size:1em; font-weight:600;">Notas:</h4>
                <div style="background:#f8f9fa; padding:1rem; border-radius:6px; border-left:4px solid #28a745;">
                    <p style="margin:0; line-height:1.6; white-space:pre-wrap;">${descricaoEscapada}</p>
                </div>
            </div>
        `;
    }

    modal.style.display = 'flex';
}

function fecharModalDetalhesItem() {
    const modal = document.getElementById('modal-detalhes-item');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function abrirModalDetalhesEquipamento(itemId) {
    // Tentar buscar dados dos itens equipados armazenados
    let item = null;
    const itensData = (typeof window !== 'undefined' && window.itensEquipamentosData) || [];
    if (Array.isArray(itensData) && itensData.length > 0) {
        item = itensData.find(i => i.id === itemId);
    }
    
    // Se não encontrou, fazer requisição à API para buscar dados do item
    if (!item && typeof window !== 'undefined' && window.personagemId) {
        try {
            const response = await fetch(`${API_BASE}/api/personagem/${window.personagemId}/inventario`);
            if (response.ok) {
                const data = await response.json();
                const todosItens = [...(data.equipados || []), ...(data.itens || [])];
                item = todosItens.find(i => i.id === itemId);
            }
        } catch (error) {
            console.error('Erro ao buscar dados do item:', error);
        }
    }
    
    if (!item) {
        alert('Item não encontrado. Recarregue a página.');
        return;
    }

    const nomeItem = item.nome_item || 'Item sem nome';
    const efeitosLista = Array.isArray(item.efeitos) ? item.efeitos : [];
    const notas = item.notas || '';

    const modal = document.getElementById('modal-detalhes-equipamento');
    if (!modal) {
        alert('Modal de detalhes não encontrado.');
        return;
    }

    const modalContent = document.getElementById('modal-detalhes-equipamento-content');
    if (modalContent) {
        let efeitosHtml = '<p style="color:#999; font-style:italic;">Sem efeitos catalogados.</p>';
        if (Array.isArray(efeitosLista) && efeitosLista.length > 0) {
            efeitosHtml = `<ul style="margin:0; padding-left:1.5rem; line-height:1.8;">${efeitosLista.map(efeito => `<li>${escaparHtml(efeito)}</li>`).join('')}</ul>`;
        }

        const notasEscapada = escaparHtml(notas || 'Sem notas adicionais.');

        modalContent.innerHTML = `
            <h3 style="margin-top:0; margin-bottom:1rem; color:#333;">${escaparHtml(nomeItem)}</h3>
            <div style="margin-bottom:1.5rem;">
                <h4 style="margin:0 0 0.5rem 0; color:#555; font-size:1em; font-weight:600;">Efeitos:</h4>
                <div style="background:#f8f9fa; padding:1rem; border-radius:6px; border-left:4px solid #0066CC;">
                    ${efeitosHtml}
                </div>
            </div>
            <div>
                <h4 style="margin:0 0 0.5rem 0; color:#555; font-size:1em; font-weight:600;">Notas:</h4>
                <div style="background:#f8f9fa; padding:1rem; border-radius:6px; border-left:4px solid #28a745;">
                    <p style="margin:0; line-height:1.6; white-space:pre-wrap;">${notasEscapada}</p>
                </div>
            </div>
        `;
    }

    modal.style.display = 'flex';
}

function fecharModalDetalhesEquipamento() {
    const modal = document.getElementById('modal-detalhes-equipamento');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function abrirModalDetalhesInventario(itemId) {
    // Tentar buscar dados dos itens do inventário armazenados
    let item = null;
    const itensData = (typeof window !== 'undefined' && window.itensInventarioData) || [];
    if (Array.isArray(itensData) && itensData.length > 0) {
        item = itensData.find(i => i.id === itemId);
    }
    
    // Se não encontrou, fazer requisição à API para buscar dados do item
    if (!item && typeof window !== 'undefined' && window.personagemId) {
        try {
            const response = await fetch(`${API_BASE}/api/personagem/${window.personagemId}/inventario`);
            if (response.ok) {
                const data = await response.json();
                const todosItens = [...(data.equipados || []), ...(data.itens || [])];
                item = todosItens.find(i => i.id === itemId);
            }
        } catch (error) {
            console.error('Erro ao buscar dados do item:', error);
        }
    }
    
    if (!item) {
        alert('Item não encontrado. Recarregue a página.');
        return;
    }

    const nomeItem = item.nome_item || 'Item sem nome';
    const efeitosLista = Array.isArray(item.efeitos) ? item.efeitos : [];
    const notas = item.notas || '';

    const modal = document.getElementById('modal-detalhes-inventario');
    if (!modal) {
        alert('Modal de detalhes não encontrado.');
        return;
    }

    const modalContent = document.getElementById('modal-detalhes-inventario-content');
    if (modalContent) {
        let efeitosHtml = '<p style="color:#999; font-style:italic;">Sem efeitos catalogados.</p>';
        if (Array.isArray(efeitosLista) && efeitosLista.length > 0) {
            efeitosHtml = `<ul style="margin:0; padding-left:1.5rem; line-height:1.8;">${efeitosLista.map(efeito => `<li>${escaparHtml(efeito)}</li>`).join('')}</ul>`;
        }

        const notasEscapada = escaparHtml(notas || 'Sem notas adicionais.');

        modalContent.innerHTML = `
            <h3 style="margin-top:0; margin-bottom:1rem; color:#333;">${escaparHtml(nomeItem)}</h3>
            <div style="margin-bottom:1.5rem;">
                <h4 style="margin:0 0 0.5rem 0; color:#555; font-size:1em; font-weight:600;">Efeitos:</h4>
                <div style="background:#f8f9fa; padding:1rem; border-radius:6px; border-left:4px solid #0066CC;">
                    ${efeitosHtml}
                </div>
            </div>
            <div>
                <h4 style="margin:0 0 0.5rem 0; color:#555; font-size:1em; font-weight:600;">Notas:</h4>
                <div style="background:#f8f9fa; padding:1rem; border-radius:6px; border-left:4px solid #28a745;">
                    <p style="margin:0; line-height:1.6; white-space:pre-wrap;">${notasEscapada}</p>
                </div>
            </div>
        `;
    }

    modal.style.display = 'flex';
}

function fecharModalDetalhesInventario() {
    const modal = document.getElementById('modal-detalhes-inventario');
    if (modal) {
        modal.style.display = 'none';
    }
}

async function selecionarItemCatalogo(itemId) {
    const item = catalogoItens.find(elem => elem.id === itemId);
    if (!item) {
        alert('Item não encontrado no catálogo.');
        return;
    }

    const personagemId = modalItemPersonagemId || window.personagemId;
    if (!personagemId) {
        alert('ID de personagem não encontrado. Reabra o catálogo.');
        return;
    }

    const quantidadeTexto = prompt(`Quantas unidades de "${item.nome}" deseja comprar?`, '1');
    if (quantidadeTexto === null) {
        return;
    }

    const quantidade = parseInt(quantidadeTexto, 10);
    if (!Number.isFinite(quantidade) || quantidade <= 0) {
        alert('Informe uma quantidade válida (inteiro positivo).');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/api/personagem/${personagemId}/inventario/by-catalog`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ catalogo_id: itemId, quantidade })
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            alert(data.message || 'Não foi possível adicionar o item.');
            return;
        }

        location.reload();
    } catch (error) {
        console.error('Erro ao adicionar item do catálogo:', error);
        alert('Erro ao adicionar item. Verifique a conexão.');
    }
}

async function deletarPericia(periciaId) {
    if (!confirm('Tem certeza que deseja remover esta perícia?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/pericias/${periciaId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            location.reload();
        } else {
            alert(data.message || 'Erro ao remover perícia');
        }
    } catch (error) {
        console.error('Erro ao deletar perícia:', error);
        alert('Erro ao remover perícia. Verifique a conexão.');
    }
}

// ==========================================
// Utilitários
// ==========================================

function formatarNumero(numero) {
    return numero.toLocaleString('pt-BR');
}

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

// ==========================================
// Inicialização
// ==========================================

// ==========================================
// Menu Hamburger (Sanduíche)
// ==========================================
function initNavbarToggle() {
    const navbarToggle = document.getElementById('navbar-toggle');
    const navbarNav = document.getElementById('navbar-nav');
    
    if (navbarToggle && navbarNav) {
        navbarToggle.addEventListener('click', function() {
            navbarToggle.classList.toggle('active');
            navbarNav.classList.toggle('active');
        });
        
        // Fechar menu ao clicar em um link
        const navLinks = navbarNav.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navbarToggle.classList.remove('active');
                navbarNav.classList.remove('active');
            });
        });
        
        // Fechar menu ao clicar fora
        document.addEventListener('click', function(event) {
            const isClickInsideNav = navbarNav.contains(event.target);
            const isClickOnToggle = navbarToggle.contains(event.target);
            
            if (!isClickInsideNav && !isClickOnToggle && navbarNav.classList.contains('active')) {
                navbarToggle.classList.remove('active');
                navbarNav.classList.remove('active');
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar menu hamburger
    initNavbarToggle();
    const paginaPersonagem = document.getElementById('personagem-page');
    if (paginaPersonagem) {
        const idAttr = paginaPersonagem.dataset.personagemId;
        if (idAttr) {
            const parsedId = parseInt(idAttr, 10);
            if (Number.isFinite(parsedId)) {
                window.personagemId = parsedId;
            }
        }

        const pontosAttr = paginaPersonagem.dataset.pontosResumo;
        if (pontosAttr) {
            try {
                window.pontosResumo = JSON.parse(pontosAttr);
            } catch (error) {
                console.warn('Não foi possível interpretar pontos_resumo:', error);
            }
        }

        const periciasAttr = paginaPersonagem.dataset.pericias;
        if (periciasAttr) {
            try {
                window.periciasDados = JSON.parse(periciasAttr);
            } catch (error) {
                console.warn('Não foi possível interpretar pericias:', error);
                window.periciasDados = [];
            }
        }

        const dinheiroAttr = paginaPersonagem.dataset.dinheiro;
        if (typeof dinheiroAttr !== 'undefined') {
            const parsedDinheiro = parseFloat(dinheiroAttr);
            if (!Number.isNaN(parsedDinheiro)) {
                personagemDinheiro = parsedDinheiro;
                window.personagemDinheiro = parsedDinheiro;
                atualizarDinheiroDisponivel(parsedDinheiro);
            }
        }
    }

    inicializarControleAtributos();

    document.querySelectorAll('.js-abrir-catalogo-vd').forEach(botao => {
        botao.addEventListener('click', () => {
            const personagemId = parseInt(botao.dataset.personagemId || '0', 10);
            if (Number.isFinite(personagemId) && personagemId > 0) {
                abrirCatalogoVD(personagemId);
            } else {
                console.warn('ID de personagem inválido ao abrir catálogo de V/D.');
            }
        });
    });

    document.querySelectorAll('.js-remover-vantagem').forEach(botao => {
        botao.addEventListener('click', () => {
            const vantagemId = parseInt(botao.dataset.vantagemId || '0', 10);
            if (Number.isFinite(vantagemId) && vantagemId > 0) {
                deletarVantagem(vantagemId);
            } else {
                console.warn('ID de vantagem inválido ao remover.');
            }
        });
    });

    document.querySelectorAll('.js-abrir-catalogo-pericias').forEach(botao => {
        botao.addEventListener('click', () => {
            const personagemId = parseInt(botao.dataset.personagemId || '0', 10);
            if (Number.isFinite(personagemId) && personagemId > 0) {
                abrirCatalogoPericias(personagemId);
            } else {
                console.warn('ID de personagem inválido ao abrir catálogo de perícias.');
            }
        });
    });

    document.querySelectorAll('.js-abrir-catalogo-itens').forEach(botao => {
        botao.addEventListener('click', () => {
            const personagemId = parseInt(botao.dataset.personagemId || '0', 10);
            if (Number.isFinite(personagemId) && personagemId > 0) {
                abrirCatalogoItens(personagemId);
            } else {
                console.warn('ID de personagem inválido ao abrir catálogo de itens.');
            }
        });
    });

    document.querySelectorAll('.js-abrir-catalogo-consumiveis').forEach(botao => {
        botao.addEventListener('click', () => {
            const personagemId = parseInt(botao.dataset.personagemId || '0', 10);
            if (Number.isFinite(personagemId) && personagemId > 0) {
                abrirCatalogoConsumiveis(personagemId);
            } else {
                console.warn('ID de personagem inválido ao abrir catálogo de consumíveis.');
            }
        });
    });

    document.querySelectorAll('.js-abrir-catalogo-equipamentos').forEach(botao => {
        botao.addEventListener('click', () => {
            const personagemId = parseInt(botao.dataset.personagemId || '0', 10);
            if (Number.isFinite(personagemId) && personagemId > 0) {
                abrirCatalogoEquipamentos(personagemId);
            } else {
                console.warn('ID de personagem inválido ao abrir catálogo de equipamentos.');
            }
        });
    });

    document.querySelectorAll('.js-evoluir-pericia').forEach(botao => {
        botao.addEventListener('click', () => {
            const periciaId = parseInt(botao.dataset.periciaId || '0', 10);
            if (Number.isFinite(periciaId) && periciaId > 0) {
                abrirModalEvoluirPericia(periciaId);
            } else {
                console.warn('ID de perícia inválido ao abrir evolução.');
            }
        });
    });
});

// Exporta funções para uso global
window.rolarDados = rolarDados;
window.rolarAtributo = rolarAtributo;
window.rolarPericia = rolarPericia;
window.mostrarAba = mostrarAba;
window.alterarAtributo = alterarAtributo;
window.confirmarMudancasAtributos = confirmarMudancasAtributos;
window.cancelarMudancasAtributos = cancelarMudancasAtributos;
window.deletarVantagem = deletarVantagem;
window.abrirCatalogoVD = abrirCatalogoVD;
window.fecharCatalogoVD = fecharCatalogoVD;
window.selecionarVDCatalogo = selecionarVDCatalogo;
window.filtrarCatalogoVD = filtrarCatalogoVD;
window.filtrarTipoVD = filtrarTipoVD;
window.deletarPericia = deletarPericia;
window.abrirModalEvoluirPericia = abrirModalEvoluirPericia;
window.fecharModalEvoluirPericia = fecharModalEvoluirPericia;
window.confirmarEvolucaoPericia = confirmarEvolucaoPericia;
window.abrirCatalogoPericias = abrirCatalogoPericias;
window.fecharCatalogoPericias = fecharCatalogoPericias;
window.filtrarCatalogoPericias = filtrarCatalogoPericias;
window.filtrarTipoPericia = filtrarTipoPericia;
window.selecionarPericiaCatalogo = selecionarPericiaCatalogo;
window.carregarCatalogoPericias = carregarCatalogoPericias;
window.abrirCatalogoItens = abrirCatalogoItens;
window.fecharCatalogoItens = fecharCatalogoItens;
window.carregarCatalogoItens = carregarCatalogoItens;
window.filtrarCatalogoItens = filtrarCatalogoItens;
window.filtrarCategoriaItem = filtrarCategoriaItem;
window.selecionarItemCatalogo = selecionarItemCatalogo;
window.abrirCatalogoConsumiveis = abrirCatalogoConsumiveis;
window.abrirCatalogoEquipamentos = abrirCatalogoEquipamentos;
