// ==========================================
// Sistema de Campanha GURPS - JavaScript
// ==========================================

// Configuração global
const API_BASE = window.location.origin;

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

    const botaoPontos = document.getElementById('pontos-disponiveis-valor');
    if (botaoPontos) {
        botaoPontos.addEventListener('click', alternarModoUpar);
    }

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
