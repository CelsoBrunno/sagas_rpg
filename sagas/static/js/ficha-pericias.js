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
        'MD': 'Muito Difícil'
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
