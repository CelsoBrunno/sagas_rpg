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
