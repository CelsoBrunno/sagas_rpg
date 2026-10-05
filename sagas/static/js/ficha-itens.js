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
