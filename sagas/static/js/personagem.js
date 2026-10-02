const personagemId = typeof window !== 'undefined' && window.personagemId !== undefined ? window.personagemId : undefined;
const SLOT_LABELS = {
    mao_direita: 'Mão direita',
    mao_esquerda: 'Mão esquerda',
    armadura: 'Armadura',
    vestimenta: 'Vestimenta',
    acessorio: 'Acessório'
};

// Armazenar dados dos itens para acesso nos modais
let itensEquipamentosData = [];
let itensInventarioData = [];

async function adicionarItemInventario(evt, personagemIdParam) {
    evt.preventDefault();
    const payload = {
        nome_item: document.getElementById('inv-nome').value,
        quantidade: parseInt(document.getElementById('inv-quantidade').value || '1', 10),
        peso: parseFloat(document.getElementById('inv-peso').value || '0'),
        preco_unitario: parseFloat(document.getElementById('inv-preco').value || '0'),
        notas: document.getElementById('inv-notas').value || ''
    };
    const res = await fetch(`/api/personagem/${personagemIdParam}/inventario`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (data.success) {
        location.reload();
    } else {
        alert('Erro: ' + (data.message || 'Falha ao adicionar'));
    }
}

async function removerItemInventario(itemId) {
    if (!confirm('Remover este item?')) return;
    const res = await fetch(`/api/inventario/${itemId}`, { method: 'DELETE' });
    const data = await res.json();
    if (data.success) {
        location.reload();
    } else {
        alert('Erro: ' + (data.message || 'Falha ao remover'));
    }
}

async function consumirItem(itemId, buttonEl) {
    if (!itemId || itemId <= 0) {
        console.error('ID do item inválido:', itemId);
        alert('ID do item inválido.');
        if (buttonEl) buttonEl.disabled = false;
        return;
    }
    
    const input = document.getElementById(`usar-${itemId}`);
    if (!input) {
        console.error('Input de quantidade não encontrado para o item:', itemId);
        alert('Input de quantidade não encontrado.');
        if (buttonEl) buttonEl.disabled = false;
        return;
    }
    
    const qtd = parseInt(input.value || '1', 10);
    if (!Number.isFinite(qtd) || qtd <= 0) {
        alert('Quantidade inválida. Por favor, insira um número maior que zero.');
        if (buttonEl) buttonEl.disabled = false;
        return;
    }
    
    try {
        const res = await fetch(`/api/inventario/${itemId}/consumir`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantidade: qtd })
        });
        
        if (!res.ok) {
            throw new Error(`HTTP error! status: ${res.status}`);
        }
        
        const data = await res.json();
        if (data.success) {
            // Atualizar a view do inventário
            await atualizarInventarioView();
        } else {
            alert('Erro: ' + (data.message || 'Falha ao usar item'));
            if (buttonEl) buttonEl.disabled = false;
        }
    } catch (error) {
        console.error('Erro ao consumir item:', error);
        alert('Erro inesperado ao consumir item: ' + error.message);
        if (buttonEl) buttonEl.disabled = false;
    }
}

async function alterarSlotEquipamento(itemId, slot, selectEl, previousValue) {
    const url = slot ? `/api/inventario/${itemId}/equipar` : `/api/inventario/${itemId}/desequipar`;
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(slot ? { slot } : {})
        });
        const data = await res.json();
        if (data.success) {
            if (!slot && selectEl) {
                selectEl.value = '';
                selectEl.dataset.currentSlot = '';
                const container = selectEl.closest('.js-gerenciar-equipamento');
                const botao = container?.querySelector('.js-desequipar-item');
                if (botao) {
                    botao.remove();
                }
            }
            await atualizarInventarioView();
        } else {
            alert('Erro: ' + (data.message || 'Falha ao atualizar equipamento'));
            if (selectEl) {
                selectEl.value = previousValue;
            }
        }
    } catch (error) {
        console.error(error);
        alert('Erro inesperado ao atualizar equipamento.');
        if (selectEl) {
            selectEl.value = previousValue;
        }
    } finally {
        if (selectEl) {
            selectEl.disabled = false;
            selectEl.dataset.currentSlot = selectEl.value || '';
        }
    }
}

async function atualizarInventarioView() {
    try {
        if (!personagemId) return;
        const res = await fetch(`/api/personagem/${personagemId}/inventario`);
        const data = await res.json();
        if (!data || !data.itens) return;
        const infoContainer = document.getElementById('inventario-resumo');
        if (infoContainer) {
            infoContainer.innerHTML = `<strong>Peso total:</strong> ${Number(data.peso_total).toFixed(2)} | <strong>Nível de carga:</strong> ${data.nivel_carga}`;
        }
        const equipResumo = document.getElementById('equipamentos-resumo');
        if (equipResumo) {
            equipResumo.innerHTML = `<strong>Peso total:</strong> ${Number(data.peso_total).toFixed(2)} | <strong>Nível de carga:</strong> ${data.nivel_carga}`;
        }
        const dinheiroValor = Number(data.dinheiro ?? window.personagemDinheiro ?? 0).toFixed(2);
        const dinheiroInventario = document.getElementById('dinheiro-disponivel-valor');
        if (dinheiroInventario) {
            dinheiroInventario.textContent = dinheiroValor;
        }
        const dinheiroEquip = document.querySelector('#equipamentos-dinheiro strong');
        if (dinheiroEquip) {
            dinheiroEquip.textContent = dinheiroValor;
        }
        const tbody = document.getElementById('inventario-lista');
        const tabelaWrapper = document.getElementById('inventario-tabela-wrapper');
        const emptyState = document.getElementById('inventario-empty-state');
        const equipamentosTbody = document.getElementById('equipamentos-lista');
        const isAdmin = tbody?.dataset?.isAdmin === '1';
        if (tbody) {
            tbody.dataset.podeEquipar = data.pode_equipar ? '1' : '0';
        }
        const podeEquipar = tbody?.dataset?.podeEquipar === '1';
        if (tbody) tbody.innerHTML = '';
        if (equipamentosTbody) equipamentosTbody.innerHTML = '';
        if (equipamentosTbody) {
            equipamentosTbody.dataset.podeEquipar = data.pode_equipar ? '1' : '0';
        }

        const equipados = Array.isArray(data.equipados) ? data.equipados.filter(item => item && item.nome_item) : [];
        let naoEquipados = Array.isArray(data.itens) ? data.itens.filter(item => item && item.nome_item) : [];

        const idsEquipados = new Set(equipados.map(item => item.id));

        const todosEquipamentos = [...equipados];
        naoEquipados = naoEquipados.filter(item => {
            if (idsEquipados.has(item.id)) {
                return false;
            }
            const tipoItem = (item.tipo_item || '').toLowerCase();
            const categoriaLower = (item.categoria || '').toLowerCase();
            const heuristicaEquip = categoriaLower.includes('armadura') || categoriaLower.includes('vestiment') || categoriaLower.includes('acess') || categoriaLower.includes('arma') || categoriaLower.includes('escudo') || categoriaLower.includes('foco') || categoriaLower.includes('ferramenta') || categoriaLower.includes('explor');
            if (tipoItem === 'equipamento' || heuristicaEquip) {
                if (!Array.isArray(item.slots_disponiveis) || item.slots_disponiveis.length === 0) {
                    if (categoriaLower.includes('armadura')) {
                        item.slots_disponiveis = ['armadura'];
                    } else if (categoriaLower.includes('vestiment')) {
                        item.slots_disponiveis = ['vestimenta'];
                    } else if (categoriaLower.includes('escudo')) {
                        item.slots_disponiveis = ['mao_direita', 'mao_esquerda'];
                    } else if (categoriaLower.includes('arma') || categoriaLower.includes('foco')) {
                        item.slots_disponiveis = ['mao_direita', 'mao_esquerda'];
                    } else if (categoriaLower.includes('acess')) {
                        item.slots_disponiveis = ['acessorio'];
                    } else {
                        item.slots_disponiveis = [];
                    }
                }
                todosEquipamentos.push(item);
                return false;
            }
            return true;
        });
        
        // Armazenar dados para acesso nos modais (após processamento completo)
        itensEquipamentosData = todosEquipamentos;
        itensInventarioData = naoEquipados;
        
        // Tornar acessível globalmente para main.js
        if (typeof window !== 'undefined') {
            window.itensEquipamentosData = itensEquipamentosData;
            window.itensInventarioData = itensInventarioData;
        }

        if (equipamentosTbody) {
            if (todosEquipamentos.length === 0) {
                const row = document.createElement('tr');
                row.innerHTML = '<td colspan="9" style="text-align:center; color: var(--cor-texto-claro); padding:0.5rem;">Nenhum item equipado.</td>';
                equipamentosTbody.appendChild(row);
            } else {
                todosEquipamentos.forEach(item => {
                    const slotsDisponiveis = Array.isArray(item.slots_disponiveis) ? item.slots_disponiveis : [];
                    const danoBalFinal = item.dano_bal_final || '-';
                    const danoGdpFinal = item.dano_gdp_final || '-';
                    let gerenciarHtml = '<span style="color: var(--cor-texto-claro); font-size:0.85rem;">Sem permissão</span>';
                    if (podeEquipar) {
                        const selectHtml = slotsDisponiveis.length > 0
                            ? `
                                <select class="form-control form-control-sm js-slot-equipamento" data-item-id="${item.id}" data-current-slot="${item.slot || ''}" style="font-size:0.85em; width:120px; margin:0 auto; display:block; text-align:center; text-align-last:center; padding:0.25rem 0.5rem;">
                                    <option value="" ${!item.slot ? 'selected' : ''}>-</option>
                                    ${slotsDisponiveis.map(slotCodigo => `<option value="${slotCodigo}" ${item.slot === slotCodigo ? 'selected' : ''}>${SLOT_LABELS[slotCodigo] || slotCodigo}</option>`).join('')}
                                </select>
                              `
                            : '';
                        const botaoDesequipar = item.slot
                            ? `<button type="button" class="btn-secondary btn-small js-desequipar-item" data-item-id="${item.id}" style="font-size:0.8em;">Desequipar</button>`
                            : '';
                        gerenciarHtml = `
                            <div class="js-gerenciar-equipamento" style="display:flex; flex-direction:column; gap:0.35rem; align-items:center;">
                                ${selectHtml}
                                ${botaoDesequipar}
                            </div>
                        `;
                    }
                    
                    const temDetalhes = (Array.isArray(item.efeitos) && item.efeitos.length > 0) || item.notas;
                    
                    const detalhesHtml = temDetalhes 
                        ? `<button onclick="abrirModalDetalhesEquipamento(${item.id})" class="btn-secondary js-detalhes-equipamento" data-item-id="${item.id}" style="padding:0.25rem 0.5rem; font-size:0.75em; cursor:pointer; border:1px solid #ddd; background:#f8f9fa; color:#333; border-radius:4px;" title="Ver detalhes">Detalhes</button>`
                        : '<span style="color:#999; font-size:0.85em;">-</span>';
                    
                    const row = document.createElement('tr');
                    row.style.fontSize = '0.9em';
                    row.innerHTML = `
                        <td style="font-weight:600; padding:0.5rem;">${item.nome_item}</td>
                        <td style="text-align:center; padding:0.5rem;">${SLOT_LABELS[item.slot] || item.slot || '-'}</td>
                        <td style="padding:0.5rem;">${item.categoria || '-'}</td>
                        <td style="text-align:center; padding:0.5rem;">${danoBalFinal}</td>
                        <td style="text-align:center; padding:0.5rem;">${danoGdpFinal}</td>
                        <td style="text-align:right; padding:0.5rem;">${(item.peso || 0).toFixed(2)}</td>
                        <td style="text-align:right; padding:0.5rem;">₣ ${(item.preco_unitario || 0).toFixed(2)}</td>
                        <td style="text-align:center; padding:0.5rem;">${detalhesHtml}</td>
                        <td style="text-align:center; padding:0.5rem;">${gerenciarHtml}</td>
                    `;
                    equipamentosTbody.appendChild(row);
                });
            }
        }

        const itensListados = naoEquipados;

        if (itensListados.length === 0) {
            if (tabelaWrapper) tabelaWrapper.classList.add('is-hidden');
            if (emptyState) emptyState.classList.remove('is-hidden');
        } else {
            if (tabelaWrapper) tabelaWrapper.classList.remove('is-hidden');
            if (emptyState) emptyState.classList.add('is-hidden');

            itensListados.forEach(item => {
                const temDetalhes = (Array.isArray(item.efeitos) && item.efeitos.length > 0) || item.notas;
                
                const detalhesHtml = temDetalhes 
                    ? `<button onclick="abrirModalDetalhesInventario(${item.id})" class="btn-secondary js-detalhes-inventario" data-item-id="${item.id}" style="padding:0.25rem 0.5rem; font-size:0.75em; cursor:pointer; border:1px solid #ddd; background:#f8f9fa; color:#333; border-radius:4px;" title="Ver detalhes">Detalhes</button>`
                    : '<span style="color:#999; font-size:0.85em;">-</span>';

                const tr = document.createElement('tr');
                tr.style.fontSize = '0.9em';
                tr.innerHTML = `
                    <td style="font-weight:600; padding:0.5rem;">${item.nome_item}</td>
                    <td style="padding:0.5rem;">${item.categoria || '-'}</td>
                    <td style="text-align:center; padding:0.5rem;">${item.quantidade}</td>
                    <td style="text-align:right; padding:0.5rem;">${(item.peso || 0).toFixed(2)}</td>
                    <td style="text-align:right; padding:0.5rem;">${(((item.peso || 0) * (item.quantidade || 0))).toFixed(2)}</td>
                    <td style="text-align:right; padding:0.5rem;">₣ ${(item.preco_unitario || 0).toFixed(2)}</td>
                    <td style="text-align:right; padding:0.5rem;">₣ ${(((item.preco_unitario || 0) * (item.quantidade || 0))).toFixed(2)}</td>
                    <td style="padding:0.5rem;">
                        <div style="display:flex; gap: .5rem; align-items:center;">
                            <input type="number" min="1" max="${item.quantidade}" value="1" class="form-control" style="max-width: 70px; font-size:0.85em;" id="usar-${item.id}">
                            <button class="btn-secondary btn-small js-consumir-item" data-item-id="${item.id}" style="font-size:0.8em; padding:0.25rem 0.5rem;">Usar</button>
                        </div>
                    </td>
                    <td style="text-align:center; padding:0.5rem;">${detalhesHtml}</td>
                    ${isAdmin ? `<td style="padding:0.5rem;"><button class="btn-danger btn-small js-remover-item" data-item-id="${item.id}" style="font-size:0.85em;">Remover</button></td>` : ''}
                `;
                tbody.appendChild(tr);
            });
        }

        const resumoLista = document.getElementById('inventario-efeitos-resumo-lista');
        if (resumoLista) {
            const linhas = (data.efeitos?.resumo_textual) || ['Nenhum efeito adicional ativo.'];
            resumoLista.innerHTML = linhas.map((linha) => `<li>${linha}</li>`).join('');
        }
        const resumoEquipLista = document.getElementById('equipamentos-efeitos-resumo-lista');
        if (resumoEquipLista) {
            const linhasEquip = (data.efeitos?.resumo_textual) || ['Nenhum efeito adicional ativo.'];
            resumoEquipLista.innerHTML = linhasEquip.map((linha) => `<li>${linha}</li>`).join('');
        }

        const danosAtivos = Array.isArray(data.efeitos?.danos) ? data.efeitos.danos : [];
        const danosHtml = danosAtivos.length > 0
            ? danosAtivos.map((dano) => {
                const partes = [];
                if (dano.dano_bal) {
                    partes.push(`Bal ${dano.dano_bal}`);
                }
                if (dano.dano_gdp) {
                    partes.push(`GdP ${dano.dano_gdp}`);
                }
                const texto = partes.length > 0 ? `${dano.nome}: ${partes.join(' | ')}` : `${dano.nome}: -`;
                return `<li>${texto}</li>`;
            }).join('')
            : '<li>Nenhuma arma equipada com modificadores de dano.</li>';

        const danosEquipLista = document.getElementById('equipamentos-danos-resumo-lista');
        if (danosEquipLista) {
            danosEquipLista.innerHTML = danosHtml;
        }
        const danosInventarioLista = document.getElementById('inventario-danos-resumo-lista');
        if (danosInventarioLista) {
            danosInventarioLista.innerHTML = danosHtml;
        }

        const valorTotalEl = document.getElementById('valor-total-inventario');
        if (valorTotalEl) {
            valorTotalEl.textContent = Number(data.valor_total || 0).toFixed(2);
        }
    } catch (e) {
        console.error(e);
    }
}

// Expondo no escopo global para handlers inline existentes
window.adicionarItemInventario = adicionarItemInventario;
window.removerItemInventario = removerItemInventario;
window.consumirItem = consumirItem;
window.atualizarInventarioView = atualizarInventarioView;
window.alterarSlotEquipamento = alterarSlotEquipamento;

document.addEventListener('DOMContentLoaded', () => {
    const formInventario = document.getElementById('form-inventario');
    if (formInventario) {
        formInventario.addEventListener('submit', (event) => {
            const personagemIdAttr = formInventario.dataset.personagemId || personagemId;
            const personagemIdValue = parseInt(personagemIdAttr || '0', 10);
            adicionarItemInventario(event, personagemIdValue);
        });
    }

    const lista = document.getElementById('inventario-lista');
    if (lista) {
        lista.addEventListener('click', (event) => {
            const consumirBtn = event.target.closest('.js-consumir-item');
            if (consumirBtn) {
                event.preventDefault();
                event.stopPropagation();
                const itemId = parseInt(consumirBtn.dataset.itemId || '0', 10);
                if (Number.isFinite(itemId) && itemId > 0) {
                    consumirBtn.disabled = true;
                    consumirItem(itemId, consumirBtn);
                }
                return false;
            }

            const removerBtn = event.target.closest('.js-remover-item');
            if (removerBtn) {
                event.preventDefault();
                event.stopPropagation();
                const itemId = parseInt(removerBtn.dataset.itemId || '0', 10);
                if (Number.isFinite(itemId) && itemId > 0) {
                    if (confirm('Remover este item?')) {
                        removerItemInventario(itemId);
                    }
                }
                return false;
            }
        });
    }

    const equipamentosLista = document.getElementById('equipamentos-lista');
    if (equipamentosLista) {
        equipamentosLista.addEventListener('change', (event) => {
            const select = event.target.closest('.js-slot-equipamento');
            if (!select) {
                return;
            }
            const pode = equipamentosLista.dataset?.podeEquipar === '1';
            if (!pode) {
                return;
            }
            const itemId = parseInt(select.dataset.itemId || '0', 10);
            if (!Number.isFinite(itemId) || itemId <= 0) {
                return;
            }
            const previousValue = select.dataset.currentSlot || '';
            select.disabled = true;
            alterarSlotEquipamento(itemId, select.value || null, select, previousValue);
        });

        equipamentosLista.addEventListener('click', async (event) => {
            const btn = event.target.closest('.js-desequipar-item');
            if (!btn) {
                return;
            }
            const pode = equipamentosLista.dataset?.podeEquipar === '1';
            if (!pode) {
                return;
            }
            const itemId = parseInt(btn.dataset.itemId || '0', 10);
            if (!Number.isFinite(itemId) || itemId <= 0) {
                return;
            }
            btn.disabled = true;
            const select = btn.closest('td')?.querySelector('.js-slot-equipamento') || null;
            const previousValue = select ? select.dataset.currentSlot || '' : '';
            await alterarSlotEquipamento(itemId, null, select, previousValue);
            btn.disabled = false;
        });
    }

});

