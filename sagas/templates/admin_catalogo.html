{% extends "base.html" %}

{% block title %}Catálogo da campanha{% endblock %}

{% block content %}
<div class="container">
    <h1>Catálogo de {{ campanha.nome_campanha }}</h1>

    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1.5rem 0;">
        {% for chave, item in abas %}
        <a href="{{ url_for('admin.admin_catalogo', aba=chave, adicionados=1 if adicionados else None, q=busca or None) }}"
           class="{% if chave == aba %}btn-primary{% else %}btn-secondary{% endif %}"
           style="padding: 0.5rem 0.75rem;">{{ item.rotulo }}</a>
        {% endfor %}
    </div>

    <div style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;">
        {% if adicionados %}
        <a href="{{ url_for('admin.admin_catalogo', aba=aba, q=busca or None) }}" class="btn-secondary" style="min-width: 12rem; text-align: center;">Para adicionar</a>
        {% else %}
        <a href="{{ url_for('admin.admin_catalogo', aba=aba, adicionados=1, q=busca or None) }}" class="btn-secondary" style="min-width: 12rem; text-align: center;">Ver adicionados</a>
        {% endif %}
        <form method="get" action="{{ url_for('admin.admin_catalogo') }}">
            <input type="hidden" name="aba" value="{{ aba }}">
            {% if adicionados %}<input type="hidden" name="adicionados" value="1">{% endif %}
            <input type="search" name="q" value="{{ busca }}" placeholder="Buscar por nome" style="padding: 0.5rem; min-width: 16rem;">
            <button type="submit" class="btn-secondary">Buscar</button>
        </form>
    </div>

    {% set categoria_curta = {
        'Armas Corpo-a-Corpo': 'Corpo-a-Corpo',
        'Armas à Distância': 'Distância',
        'Ferramentas e Kits': 'Ferramentas',
        'Montarias e Veículos': 'Montarias',
        'Acessórios Mágicos': 'Acess. Mág.',
        'Focos Mágicos': 'Focos',
        'Consumíveis': 'Consumível',
        'Acessórios': 'Acessório',
        'Armaduras': 'Armadura',
        'Escudos': 'Escudo',
        'Exploração': 'Exploração',
        'Vestuário': 'Vestuário',
    } %}
    {% set tipo_item_curto = {
        'equipamento': 'equip.',
        'consumivel': 'cons.',
        'outro': 'outro',
    } %}
    {% set tipo_dano_curto = {
        'corte/perfurante': 'c/p',
        'perfurante': 'perf.',
        'contusão': 'cont.',
        'corte': 'corte',
        'queimadura': 'queim.',
    } %}
    {% set colunas_largas = spec.tela|length >= 8 %}
    {% if aba == 'itens' %}
        {% set colunas_centro = ('dano_bal_mod', 'dano_bal_tipo', 'dano_gdp_mod', 'dano_gdp_tipo', 'rd_mod', 'rd_tipo') %}
    {% elif aba == 'pericias' %}
        {% set colunas_centro = ('atributo_base', 'dificuldade', 'custo_texto') %}
    {% elif aba == 'vantagens' %}
        {% set colunas_centro = ('custo_base',) %}
    {% elif aba == 'magias' %}
        {% set colunas_centro = ('dificuldade',) %}
    {% else %}
        {% set colunas_centro = () %}
    {% endif %}
    <div class="table-responsive catalogo-tabela" style="margin-top: 1rem;">
        <table class="table-gurps table-catalogo-compacta{% if not colunas_largas %} table-catalogo-estreita{% endif %}"
               style="table-layout: fixed;{% if colunas_largas %} width: 100%; min-width: {{ (spec.tela|length * 5) + 6 }}rem;{% else %} width: auto; max-width: 100%;{% endif %}">
            <colgroup>
                <col style="width: 2.5rem;">
                {% for campo in spec.tela %}
                {% if campo.nome == 'nome' %}
                <col style="width: {% if colunas_largas %}11rem{% else %}14rem{% endif %};">
                {% elif campo.nome == 'categoria' %}
                <col style="width: 7rem;">
                {% elif campo.nome == 'atributo_base' %}
                <col style="width: {% if adicionados %}5.5rem{% else %}3rem{% endif %};">
                {% elif campo.nome == 'dificuldade' %}
                <col style="width: {% if adicionados %}5rem{% else %}3rem{% endif %};">
                {% elif campo.nome == 'tipo' %}
                <col style="width: {% if adicionados %}8rem{% else %}5rem{% endif %};">
                {% elif campo.nome == 'tipo_item' %}
                <col style="width: {% if adicionados %}5.5rem{% else %}4.25rem{% endif %};">
                {% elif campo.nome in ('dano_bal_tipo', 'dano_gdp_tipo', 'rd_tipo', 'escola', 'classe') %}
                <col style="width: 4.25rem;">
                {% elif campo.nome in ('preco', 'peso', 'dano_bal_mod', 'dano_gdp_mod', 'rd_mod', 'custo_base', 'custo_texto', 'custo') %}
                <col style="width: 3.25rem;">
                {% elif campo.tipo == 'longo' %}
                <col style="width: 3rem;">
                {% else %}
                <col style="width: 5rem;">
                {% endif %}
                {% endfor %}
                {% if adicionados %}
                <col style="width: 4.5rem;">
                {% endif %}
            </colgroup>
            <thead>
                <tr>
                    <th></th>
                    {% for campo in spec.tela %}
                    <th class="{% if campo.nome in colunas_centro %}celula-centro{% endif %}" data-completo="{{ campo.rotulo }}">{{ campo.rotulo }}</th>
                    {% endfor %}
                    {% if adicionados %}<th></th>{% endif %}
                </tr>
            </thead>
            <tbody>
                {% set custos_nivel = {'F': '1', 'M': '3', 'D': '7', 'MD': '15'} %}
                {% for item in itens %}
                {% set valores = item.efetivo if adicionados else item %}
                {% set formulario = 'ajuste-' ~ item.id %}
                <tr>
                    <td>
                        {% if adicionados %}
                        <form id="{{ formulario }}" method="post" action="{{ url_for('admin.admin_catalogo_ajuste', aba=aba, item_id=item.id) }}">
                            <input type="hidden" name="q" value="{{ busca }}">
                        </form>
                        <form method="post" action="{{ url_for('admin.admin_catalogo_remover', aba=aba, item_id=item.id) }}">
                            <input type="hidden" name="q" value="{{ busca }}">
                            <button type="submit" class="btn-primary" style="padding: 0.15rem 0.4rem;">-</button>
                        </form>
                        {% else %}
                        <form method="post" action="{{ url_for('admin.admin_catalogo_adicionar', aba=aba, item_id=item.id) }}">
                            <input type="hidden" name="q" value="{{ busca }}">
                            <button type="submit" class="btn-primary" style="padding: 0.15rem 0.4rem;">+</button>
                        </form>
                        {% endif %}
                    </td>
                    {% for campo in spec.tela %}
                    {% set valor_cheio = valores[campo.nome] if valores[campo.nome] is not none else '' %}
                    {% if campo.nome == 'categoria' %}
                        {% set valor_tela = categoria_curta.get(valor_cheio, valor_cheio) %}
                    {% elif campo.nome == 'tipo_item' %}
                        {% set valor_tela = tipo_item_curto.get(valor_cheio, valor_cheio) %}
                    {% elif campo.nome in ('dano_bal_tipo', 'dano_gdp_tipo', 'rd_tipo') %}
                        {% set valor_tela = tipo_dano_curto.get(valor_cheio, valor_cheio) %}
                    {% else %}
                        {% set valor_tela = valor_cheio %}
                    {% endif %}
                    <td class="{% if campo.nome == 'nome' %}celula-nome {% endif %}{% if campo.nome in colunas_centro %}celula-centro {% elif campo.tipo == 'numero' or campo.nome in ('preco', 'peso') %}celula-num {% endif %}celula-hover"
                        {% if valor_cheio and campo.tipo != 'longo' %}data-completo="{{ valor_cheio|e }}"{% endif %}
                        >
                        {% if aba == 'pericias' and campo.nome == 'custo_texto' %}
                        {% set custo = custos_nivel.get(valores.dificuldade, '') %}
                        <span class="custo-nivel">{{ custo or '—' }}</span>
                        {% if adicionados %}
                        <input type="hidden" name="custo_texto" form="{{ formulario }}" value="{{ custo }}">
                        {% endif %}
                        {% elif adicionados and campo.tipo == 'longo' %}
                        <button type="button" class="btn-secondary js-texto" style="padding: 0.15rem 0.35rem;" aria-label="{{ campo.rotulo }}"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: block;" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg></button>
                        <textarea name="{{ campo.nome }}" class="texto-fonte" form="{{ formulario }}" hidden>{{ valor_cheio }}</textarea>
                        {% elif adicionados and campo.opcoes %}
                        <select name="{{ campo.nome }}" form="{{ formulario }}" class="campo-lista{% if campo.nome in colunas_centro %} campo-lista-curto{% endif %}">
                            {% for opcao in campo.opcoes %}
                            <option value="{{ opcao }}" {% if valor_cheio == opcao %}selected{% endif %}>{% if campo.nome == 'tipo_item' %}{{ tipo_item_curto.get(opcao, opcao) }}{% else %}{{ opcao }}{% endif %}</option>
                            {% endfor %}
                        </select>
                        {% elif adicionados %}
                        <input name="{{ campo.nome }}" form="{{ formulario }}" value="{{ valor_cheio }}" style="width: 100%;">
                        {% elif campo.tipo == 'longo' %}
                        <button type="button" class="btn-secondary js-texto btn-ver-texto" {% if not valor_cheio %}disabled{% endif %}>Ver</button>
                        <div class="texto-fonte" hidden>{{ valor_cheio }}</div>
                        {% elif valor_tela %}
                        {{ valor_tela }}
                        {% else %}
                        —
                        {% endif %}
                    </td>
                    {% endfor %}
                    {% if adicionados %}
                    <td style="white-space: nowrap;">
                        <button type="submit" class="btn-primary" form="{{ formulario }}" style="padding: 0.15rem 0.35rem;" title="Salvar" aria-label="Salvar"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: block;" aria-hidden="true"><path d="M5 3h11l5 5v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"/><path d="M7 3v5h8V3"/><rect x="7" y="13" width="10" height="8"/></svg></button>
                        <form method="post" action="{{ url_for('admin.admin_catalogo_restaurar', aba=aba, item_id=item.id) }}" style="display: inline;">
                            <input type="hidden" name="q" value="{{ busca }}">
                            <button type="submit" class="btn-secondary" style="padding: 0.15rem 0.35rem;" title="Restaurar padrão" aria-label="Restaurar padrão"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="display: block;" aria-hidden="true"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 3v6h6"/></svg></button>
                        </form>
                    </td>
                    {% endif %}
                </tr>
                {% else %}
                <tr>
                    <td colspan="{{ spec.tela|length + (2 if adicionados else 1) }}">Nada nesta lista.</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <h2 style="margin-top: 2rem;">Acrescentar só nesta campanha</h2>
    <form method="post" action="{{ url_for('admin.admin_catalogo_novo', aba=aba) }}" style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: end;">
        {% for campo in spec.campos %}
        <label>
            {{ campo.rotulo }}
            {% if campo.opcoes %}
            <select name="{{ campo.nome }}" style="display: block; padding: 0.4rem;">
                {% for opcao in campo.opcoes %}
                <option value="{{ opcao }}">{{ opcao }}</option>
                {% endfor %}
            </select>
            {% elif campo.tipo == 'numero' %}
            <input name="{{ campo.nome }}" inputmode="decimal" style="display: block; padding: 0.4rem;">
            {% else %}
            <input name="{{ campo.nome }}" style="display: block; padding: 0.4rem;">
            {% endif %}
        </label>
        {% endfor %}
        <button type="submit" class="btn-primary">Acrescentar</button>
    </form>
</div>

<div id="popup-texto">
    <div class="popup-caixa">
        <h2 id="popup-titulo">Texto</h2>
        <textarea id="popup-campo" rows="10"></textarea>
        <div class="popup-acoes">
            <button type="button" id="popup-ok" class="btn-primary">Fechar</button>
        </div>
    </div>
</div>

<style>
.catalogo-tabela {
    overflow-x: auto;
}
.table-catalogo-compacta {
    font-size: 0.78rem;
    line-height: 1.25;
    border: 1px solid rgba(255, 255, 255, 0.28);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: none;
}
.table-catalogo-estreita {
    width: auto !important;
    max-width: 100%;
}
.table-catalogo-compacta th,
.table-catalogo-compacta td {
    padding: 0.35rem 0.45rem;
    vertical-align: middle;
    white-space: nowrap;
    border-right: 1px solid rgba(255, 255, 255, 0.12);
}
.table-catalogo-compacta th:last-child,
.table-catalogo-compacta td:last-child {
    border-right: none;
}
.table-catalogo-compacta tbody tr {
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
}
.table-catalogo-compacta tbody tr:last-child {
    border-bottom: none;
}
.table-catalogo-compacta.table-catalogo-estreita th,
.table-catalogo-compacta.table-catalogo-estreita td {
    overflow: visible;
    text-overflow: clip;
}
.table-catalogo-compacta:not(.table-catalogo-estreita) th,
.table-catalogo-compacta:not(.table-catalogo-estreita) td {
    overflow: hidden;
    text-overflow: ellipsis;
}
.table-catalogo-compacta .celula-nome {
    white-space: normal;
    overflow: visible;
    text-overflow: clip;
    word-break: break-word;
}
.table-catalogo-compacta .celula-num {
    text-align: right;
    font-variant-numeric: tabular-nums;
}
.table-catalogo-compacta .celula-centro {
    text-align: center;
    font-variant-numeric: tabular-nums;
}
.table-catalogo-compacta .celula-centro input,
.table-catalogo-compacta .celula-centro select {
    text-align: center;
}
.table-catalogo-compacta select,
.table-catalogo-compacta input {
    font-size: 0.78rem;
    padding: 0.15rem 0.25rem;
}
.table-catalogo-compacta td:has(.campo-lista) {
    overflow: visible;
}
.table-catalogo-compacta select.campo-lista {
    width: 100%;
    min-width: 0;
    box-sizing: border-box;
    padding: 0.25rem 0.15rem;
    appearance: auto;
    -webkit-appearance: menulist;
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.22);
    border-radius: 4px;
    color: inherit;
}
.table-catalogo-compacta select.campo-lista-curto {
    font-size: 0.82rem;
    font-weight: 600;
}
.table-catalogo-compacta .btn-ver-texto {
    font-size: 0.65rem;
    line-height: 1.1;
    padding: 0.1rem 0.28rem;
    letter-spacing: 0;
}
.tip-catalogo {
    position: fixed;
    z-index: 3000;
    max-width: min(28rem, calc(100vw - 1.5rem));
    padding: 0.55rem 0.75rem;
    border-radius: 8px;
    border: 1px solid rgba(185, 173, 151, 0.35);
    background: linear-gradient(160deg, #2a2522 0%, #1a1715 100%);
    color: #e6dfd2;
    font-size: 0.82rem;
    line-height: 1.35;
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.45), 0 0 0 1px rgba(122, 46, 39, 0.25);
    pointer-events: none;
    opacity: 0;
    transform: translateY(4px);
    transition: opacity 0.12s ease, transform 0.12s ease;
    white-space: pre-wrap;
    word-break: break-word;
}
.tip-catalogo.visivel {
    opacity: 1;
    transform: translateY(0);
}
#popup-texto {
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.45);
    align-items: center;
    justify-content: center;
    z-index: 2000;
}
#popup-texto.aberto {
    display: flex;
}
#popup-texto .popup-caixa {
    background: white;
    color: #222;
    max-width: 36rem;
    width: 90%;
    padding: 1rem;
    border-radius: 8px;
}
#popup-texto textarea {
    width: 100%;
}
#popup-texto .popup-acoes {
    margin-top: 0.75rem;
}
</style>

<script>
(function () {
    var popup = document.getElementById('popup-texto');
    var campo = document.getElementById('popup-campo');
    var titulo = document.getElementById('popup-titulo');
    var origem = null;
    var custosNivel = {F: '1', M: '3', D: '7', MD: '15'};
    document.querySelectorAll('select[name="dificuldade"]').forEach(function (selecao) {
        selecao.addEventListener('change', function () {
            var linha = selecao.closest('tr');
            var numero = custosNivel[selecao.value] || '—';
            var visivel = linha.querySelector('.custo-nivel');
            var oculto = linha.querySelector('input[name="custo_texto"]');
            if (visivel) visivel.textContent = numero;
            if (oculto) oculto.value = numero === '—' ? '' : numero;
        });
    });
    function fechar() {
        if (origem && origem.tagName === 'TEXTAREA') {
            origem.value = campo.value;
        }
        popup.classList.remove('aberto');
        origem = null;
    }
    document.querySelectorAll('.js-texto').forEach(function (botao) {
        botao.addEventListener('click', function () {
            origem = botao.parentElement.querySelector('.texto-fonte');
            titulo.textContent = botao.textContent === 'Ver' ? 'Texto' : (botao.getAttribute('aria-label') || 'Texto');
            campo.value = origem ? (origem.value !== undefined ? origem.value : origem.textContent) : '';
            campo.readOnly = !origem || origem.tagName !== 'TEXTAREA';
            popup.classList.add('aberto');
        });
    });
    document.getElementById('popup-ok').addEventListener('click', fechar);
    popup.addEventListener('click', function (evento) {
        if (evento.target === popup) {
            fechar();
        }
    });

    var tip = document.createElement('div');
    tip.className = 'tip-catalogo';
    tip.setAttribute('role', 'tooltip');
    document.body.appendChild(tip);
    var tipTimer = null;
    var tipAlvo = null;

    function textoDica(el) {
        if (!el) return '';
        if (el.classList.contains('js-texto')) {
            var fonte = el.parentElement && el.parentElement.querySelector('.texto-fonte');
            var texto = fonte ? (fonte.value !== undefined ? fonte.value : fonte.textContent) : '';
            return (texto || '').trim();
        }
        if (el.matches('input, select, textarea')) {
            return (el.value || '').trim();
        }
        var completo = el.getAttribute('data-completo');
        if (completo) return completo.trim();
        return (el.textContent || '').replace(/\s+/g, ' ').trim();
    }

    function precisaDica(el) {
        var completo = textoDica(el);
        if (!completo || completo === '—') return false;
        if (el.classList.contains('js-texto') || el.matches('input, select, textarea')) return true;
        var visivel = (el.textContent || '').replace(/\s+/g, ' ').trim();
        if (completo !== visivel) return true;
        return el.scrollWidth > el.clientWidth + 1;
    }

    function esconderTip() {
        clearTimeout(tipTimer);
        tipTimer = null;
        tipAlvo = null;
        tip.classList.remove('visivel');
    }

    function posicionarTip(el) {
        var ret = el.getBoundingClientRect();
        tip.style.left = '0px';
        tip.style.top = '0px';
        tip.classList.add('visivel');
        var tw = tip.offsetWidth;
        var th = tip.offsetHeight;
        var left = ret.left + (ret.width / 2) - (tw / 2);
        var top = ret.top - th - 8;
        if (top < 8) top = ret.bottom + 8;
        left = Math.max(8, Math.min(left, window.innerWidth - tw - 8));
        tip.style.left = left + 'px';
        tip.style.top = top + 'px';
    }

    function mostrarTip(el) {
        var texto = textoDica(el);
        if (!texto) return;
        tip.textContent = texto;
        tipAlvo = el;
        clearTimeout(tipTimer);
        tipTimer = setTimeout(function () {
            if (tipAlvo === el) posicionarTip(el);
        }, 60);
    }

    function alvoHover(evento) {
        var el = evento.target.closest('th[data-completo], td.celula-hover, .js-texto, .table-catalogo-compacta input, .table-catalogo-compacta select');
        if (!el || !el.closest('.table-catalogo-compacta')) return null;
        if (el.matches('td.celula-hover') && el.querySelector('button, input, select, textarea, form')) {
            var interno = el.querySelector('.js-texto, input, select, textarea');
            return interno || null;
        }
        return el;
    }

    var tabela = document.querySelector('.table-catalogo-compacta');
    if (tabela) {
        tabela.addEventListener('mouseover', function (evento) {
            var el = alvoHover(evento);
            if (!el || !precisaDica(el)) {
                if (!evento.target.closest('.tip-catalogo')) esconderTip();
                return;
            }
            if (tipAlvo !== el) mostrarTip(el);
        });
        tabela.addEventListener('mouseout', function (evento) {
            var proximo = evento.relatedTarget;
            if (proximo && tabela.contains(proximo)) {
                var el = alvoHover({ target: proximo });
                if (el && precisaDica(el)) return;
            }
            esconderTip();
        });
        tabela.addEventListener('scroll', esconderTip, true);
        window.addEventListener('scroll', esconderTip, true);
    }
})();
</script>
{% endblock %}
