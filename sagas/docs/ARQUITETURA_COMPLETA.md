# 🏛️ Arquitetura Completa do Sistema de Campanha GURPS

## 📋 Índice
1. [Visão Geral da Arquitetura](#visão-geral)
2. [Módulo 1: Fichas de Personagem](#módulo-1-fichas)
3. [Módulo 2: Locais (Hub Central)](#módulo-2-locais)
4. [Módulo 3: NPCs Contextuais](#módulo-3-npcs)
5. [Módulo 4: Mapas](#módulo-4-mapas)
6. [Diagrama de Relações](#diagrama-de-relações)
7. [Estrutura SQL Completa](#estrutura-sql)
8. [API REST Endpoints](#api-endpoints)
9. [Sequência de Implementação](#sequência-de-implementação)
10. [Exemplos Práticos](#exemplos-práticos)

---

## 🎯 Visão Geral da Arquitetura {#visão-geral}

O sistema é baseado em **4 módulos centrais inter-relacionados**:

```
┌─────────────────┐         ┌──────────────────┐
│   FICHAS        │◄────────┤      NPCs         │
│  (Personagem)   │         │   (Contextuais)   │
└─────────────────┘         └─────────┬───────────┘
                                     │
                              local_atual_id
                                     │
                                     ▼
                            ┌──────────────────┐
                            │     LOCAIS       │◄──── Hub Central
                            │   (O "Onde")     │
                            └─────────┬────────┘
                                      │
                            local_associado_id
                                      │
                                      ▼
                            ┌──────────────────┐
                            │     MAPAS        │
                            │  (Visualização)  │
                            └──────────────────┘
```

### Princípios de Design

1. **Local como Hub Central**: O módulo Locais conecta NPCs e Mapas
2. **Fichas Modulares**: Fichas GURPS podem ser associadas a PJs e NPCs
3. **Renderização Contextual**: Informações exibidas dinamicamente por contexto
4. **Separação PJ/NPC**: Mesma estrutura de ficha para ambos os tipos

---

## 📝 Módulo 1: Fichas de Personagem (GURPS) {#módulo-1-fichas}

### 1.1 Status Atual
✅ **IMPLEMENTADO**: Estrutura básica com atributos, vantagens, desvantagens e perícias

### 1.2 Estrutura de Dados Expandida

#### Tabelas SQL Existentes:
```sql
-- ✅ IMPLEMENTADO
personagens (id, nome, jogador_nome, raca, pontos_base, tipo, status)
atributos (id, personagem_id, ST, DX, IQ, HT, custo_total)
vantagens_desvantagens (id, personagem_id, nome_item, custo_em_pontos, notas)
pericias (id, personagem_id, nome_pericia, atributo_base, dificuldade, pontos_investidos, nivel_calculado)
```

#### Nova Tabela: inventario
```sql
CREATE TABLE inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personagem_id INT NOT NULL,
    nome_item VARCHAR(200) NOT NULL,
    quantidade INT DEFAULT 1,
    peso DECIMAL(5,2) DEFAULT 0,
    equipado BOOLEAN DEFAULT FALSE,
    notas TEXT,
    FOREIGN KEY (personagem_id) REFERENCES personagens(id) ON DELETE CASCADE
);
```

### 1.3 Lógica de Cálculos GURPS

#### Atributos Derivados (Auto-calculados)
```python
def calcular_atributos_derivados(ST, DX, IQ, HT):
    return {
        'PV_max': ST,
        'PF_max': HT,
        'Velocidade_Basica': round((DX + HT) / 4, 1),
        'Esquiva': int((DX + HT) / 4) + 3,
        'Peso_Maximo': ST * 15,  # em libras
        'PM': ST * 15  # Peso Morto
    }
```

#### Cálculo de Carga
```python
def calcular_nivel_carga(peso_total, ST):
    PM = ST * 15  # Peso Morto
    
    if peso_total == 0:
        return "Nenhuma"
    elif peso_total <= PM:
        return "Leve (10%)"
    elif peso_total <= PM * 2:
        return "Média (20%)"
    elif peso_total <= PM * 3:
        return "Pesada (30%)"
    else:
        return "Extrema (40%)"
```

### 1.4 Extensões Necessárias

1. **Inventário com Cálculo de Carga**
   - Campo `peso` em inventario
   - Calcular total de peso automaticamente
   - Exibir nível de carga

2. **Calculadora de Combate**
   - Atributos de defesa calculados
   - Modificadores de equipamento

3. **Rolagens Interativas**
   - ✅ Implementado: Botões clicáveis
   - Adicionar: Histórico persistente
   - Adicionar: Rolar múltiplos dados (resistência, etc)

---

## 🗺️ Módulo 2: Locais (Hub Central) {#módulo-2-locais}

### 2.1 Estrutura de Dados

```sql
CREATE TABLE locais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(100),              -- 'Taverna', 'Cidade', 'Masmorra', 'Ruína', 'Região'
    descricao_publica TEXT,        -- O que os jogadores veem
    descricao_mestre TEXT,          -- Notas privadas, segredos, ganchos
    imagem_principal_url VARCHAR(500),
    visivel_para_jogadores BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 2.2 Lógica e Relações

**Local é o HUB**:
- NPCs possuem `local_atual_id` → vinculam a um local
- Mapas possuem `local_associado_id` → vinculam a um local
- Um local pode ter múltiplos NPCs
- Um local pode ter múltiplos mapas

### 2.3 Interfaces Necessárias

#### Página: `/locais` (Índice)
- Grid/listagem de todos os locais
- Filtros: tipo, região, visibilidade
- Busca por nome
- Cards clicáveis

#### Página: `/locais/<id>` (Detalhe)
- Nome, imagem, descrição pública
- Seção "Visão do Mestre" (toggle):
  - Descrição mestre
  - Edição inline
- Seção "NPCs Presentes":
  - Lista dinâmica de NPCs no local
  - Consulta: `SELECT * FROM npcs WHERE local_atual_id = ?`
- Seção "Mapas":
  - Exibe mapas associados
  - Consulta: `SELECT * FROM mapas WHERE local_associado_id = ?`

### 2.4 Rotas Flask Necessárias

```python
@app.route('/locais')
def listar_locais():
    """Lista todos os locais com filtros"""

@app.route('/locais/<int:id>')
def ver_local(id):
    """Exibe detalhes do local + NPCs + Mapas"""

@app.route('/locais/novo', methods=['GET', 'POST'])
def novo_local():
    """Cria novo local"""

@app.route('/locais/<int:id>/editar', methods=['GET', 'POST'])
def editar_local(id):
    """Edita local existente"""

@app.route('/api/locais/<int:id>/npcs')
def api_npcs_do_local(id):
    """API: Retorna NPCs presentes no local"""

@app.route('/api/locais/<int:id>/mapas')
def api_mapas_do_local(id):
    """API: Retorna mapas associados ao local"""
```

---

## 👥 Módulo 3: NPCs Contextuais {#módulo-3-npcs}

### 3.1 Estrutura de Dados

```sql
CREATE TABLE npcs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'Vivo',     -- 'Vivo', 'Morto', 'Desconhecido', 'Ausente'
    descricao_breve VARCHAR(500),          -- Para listas e previews
    descricao_completa TEXT,               -- História, personalidade, segredos
    tipo VARCHAR(100),                     -- 'Guarda', 'Comerciante', 'Nobre', 'Bandido', etc
    importancia VARCHAR(50) DEFAULT 'Comum', -- 'Pequena', 'Comum', 'Importante', 'Crítico'
    
    -- Relação com Locais (Hub)
    local_atual_id INT,
    FOREIGN KEY (local_atual_id) REFERENCES locais(id) ON DELETE SET NULL,
    
    -- Relação com Fichas (Opcional)
    ficha_personagem_id INT NULL,
    FOREIGN KEY (ficha_personagem_id) REFERENCES personagens(id) ON DELETE SET NULL,
    
    -- Metadados
    visivel_para_jogadores BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 3.2 Lógica e Relações

**Relação Fundamental**: `local_atual_id`
- NPC existe em um contexto (local)
- Mover NPC = mudar `local_atual_id`
- A página do local exibe NPCs automaticamente

**Relação Opcional**: `ficha_personagem_id`
- NPC simples (apenas nome + descrição) pode ser promovido
- Link para ficha completa quando necessário
- Toggle: Mostrar/Ocultar ficha do NPC

### 3.3 Interfaces Necessárias

#### Página: `/npcs` (Índice)
- Lista todos os NPCs
- Filtros: status, tipo, importância, local atual
- Busca por nome
- Indicador visual: com/sem ficha GURPS

#### Página: `/npcs/<id>` (Detalhe)
- Nome, descrição, tipo, status
- Link para local atual (se houver)
- Botão "Ver Local Atual" → `/locais/<local_atual_id>`
- Se possui ficha: Link "Ver Ficha GURPS" → `/personagem/<ficha_personagem_id>`

#### Formulário de Edição (CRUD)
- Campo: Nome, descrição, tipo, status
- **Dropdown dinâmico**: Selecionar local atual
  - Carrega lista de locais
  - Valor atual: local_atual_id
- **Checkbox**: "Este NPC possui ficha GURPS"
  - Se marcado: Link para criar/selecionar ficha

### 3.4 Rotas Flask Necessárias

```python
@app.route('/npcs')
def listar_npcs():
    """Lista todos os NPCs"""

@app.route('/npcs/<int:id>')
def ver_npc(id):
    """Exibe detalhes do NPC + link para local"""

@app.route('/npcs/novo', methods=['GET', 'POST'])
def novo_npc():
    """Cria novo NPC"""

@app.route('/npcs/<int:id>/editar', methods=['GET', 'POST'])
def editar_npc(id):
    """Edita NPC existente"""

@app.route('/api/npcs/locais')
def api_lista_locais():
    """API: Retorna lista de locais para dropdown"""

@app.route('/api/npcs/<int:id>/mover', methods=['POST'])
def mover_npc(id):
    """API: Move NPC para outro local"""
```

---

## 🗺️ Módulo 4: Mapas {#módulo-4-mapas}

### 4.1 Estrutura de Dados

```sql
CREATE TABLE mapas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_mapa VARCHAR(255) NOT NULL,
    url_imagem VARCHAR(500) NOT NULL,     -- URL do arquivo de imagem
    tipo_mapa VARCHAR(50),                -- 'Regional', 'Cidade', 'Masmorra', 'Local', 'Batalha'
    descricao TEXT,
    
    -- Relação com Locais (Opcional)
    local_associado_id INT NULL,
    FOREIGN KEY (local_associado_id) REFERENCES locais(id) ON DELETE CASCADE,
    
    -- Metadados
    zoom_min INT DEFAULT 1,
    zoom_max INT DEFAULT 10,
    coord_x INT DEFAULT 0,                -- Para posicionamento futuro
    coord_y INT DEFAULT 0,
    visivel_para_jogadores BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 Lógica e Relações

**Relação com Locais**: `local_associado_id`
- Mapas podem estar associados a um local específico
- Ou podem ser regionais/globais (NULL)
- Um local pode ter múltiplos mapas

**Futuro - Interatividade**:
```sql
CREATE TABLE mapa_pins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mapa_id INT NOT NULL,
    pos_x INT NOT NULL,           -- Coordenadas relativas (0-100)
    pos_y INT NOT NULL,
    tipo VARCHAR(50),              -- 'local', 'npc', 'combate', 'tesouro'
    texto_popup VARCHAR(255),
    link_url VARCHAR(500),         -- Link opcional
    cor VARCHAR(20) DEFAULT '#FF0000',
    FOREIGN KEY (mapa_id) REFERENCES mapas(id) ON DELETE CASCADE
);
```

### 4.3 Interfaces Necessárias

#### Página: `/mapas` (Índice)
- Grid de miniaturas de mapas
- Filtros: tipo, local associado
- Botão "Atlas Regional" (mapas sem local)

#### Página: `/mapas/<id>` (Visualizador)
- Exibe imagem em tamanho grande
- Zoom in/out (básico)
- Botão "Baixar"
- Se associado a local: Link "Ver Local"

#### Página: `/locais/<id>` → Seção Mapas
- Lista mapas associados ao local
- Miniaturas clicáveis
- Expandir para visualização completa

### 4.4 Rotas Flask Necessárias

```python
@app.route('/mapas')
def listar_mapas():
    """Lista todos os mapas"""

@app.route('/mapas/<int:id>')
def ver_mapa(id):
    """Exibe mapa em tamanho grande"""

@app.route('/mapas/novo', methods=['GET', 'POST'])
def novo_mapa():
    """Upload e criação de novo mapa"""

@app.route('/api/mapas/upload', methods=['POST'])
def upload_imagem():
    """API: Upload de arquivo de imagem"""
```

---

## 🔗 Diagrama de Relações {#diagrama-de-relações}

### Diagrama ER Conceitual

```
┌──────────────────────┐
│   PERSONAGENS        │
│  (Fichas GURPS)      │
│──────────────────────│
│ id                   │◄──┐
│ nome                 │   │
│ tipo (PJ/NPC)       │   │
│ [atributos_json]     │   │
│ [pericias_json]      │   │
└──────────────────────┘   │
                           │
                    ficha_personagem_id
                           │
┌──────────────────────┐   │       ┌──────────────────────┐
│        NPCS          │◄──┘       │       LOCAIS          │
│──────────────────────│           │──────────────────────│
│ id                   │           │ id                   │◄──┐
│ nome                 │           │ nome                 │   │
│ local_atual_id ──────┼───────────┤ tipo                 │   │
│ ficha_personagem_id  │           │ descricao_publica    │   │
│ status               │           │ descricao_mestre     │   │
│ [descricao]          │           │ imagem_url           │   │
└──────────────────────┘           └──────────────────────┘   │
                                                  ▲             │
                                                  │             │
                                       local_associado_id       │
                                                  │             │
                           ┌──────────────────────┼─────────────┘
                           │                      │
                  ┌─────────┴──────────┐  local_associado_id
                  │       MAPAS        │
                  │────────────────────│
                  │ id                 │
                  │ nome_mapa          │
                  │ url_imagem         │
                  │ tipo_mapa          │
                  │ local_associado_id │◄──┘
                  └────────────────────┘
```

---

## 🗄️ Estrutura SQL Completa {#estrutura-sql}

### Arquivo: `database/schema_completo.sql`

```sql
-- ==========================================
-- Sistema de Campanha GURPS - Schema Completo
-- ==========================================

USE sagas_gurps;

-- ==========================================
-- Módulo 1: Fichas de Personagem (✅ Existente)
-- ==========================================

-- Tabela de Inventário (NOVA)
CREATE TABLE IF NOT EXISTS inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personagem_id INT NOT NULL,
    nome_item VARCHAR(200) NOT NULL,
    quantidade INT DEFAULT 1,
    peso DECIMAL(5,2) DEFAULT 0,
    equipado BOOLEAN DEFAULT FALSE,
    notas TEXT,
    FOREIGN KEY (personagem_id) REFERENCES personagens(id) ON DELETE CASCADE,
    INDEX idx_inventario_personagem (personagem_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- Módulo 2: Locais (NOVO)
-- ==========================================

CREATE TABLE IF NOT EXISTS locais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(100),
    descricao_publica TEXT,
    descricao_mestre TEXT,
    imagem_principal_url VARCHAR(500),
    visivel_para_jogadores BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_locais_tipo (tipo),
    INDEX idx_locais_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- Módulo 3: NPCs (NOVO)
-- ==========================================

CREATE TABLE IF NOT EXISTS npcs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'Vivo',
    descricao_breve VARCHAR(500),
    descricao_completa TEXT,
    tipo VARCHAR(100),
    importancia VARCHAR(50) DEFAULT 'Comum',
    local_atual_id INT,
    ficha_personagem_id INT NULL,
    visivel_para_jogadores BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (local_atual_id) REFERENCES locais(id) ON DELETE SET NULL,
    FOREIGN KEY (ficha_personagem_id) REFERENCES personagens(id) ON DELETE SET NULL,
    INDEX idx_npcs_local (local_atual_id),
    INDEX idx_npcs_nome (nome),
    INDEX idx_npcs_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- Módulo 4: Mapas (NOVO)
-- ==========================================

CREATE TABLE IF NOT EXISTS mapas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_mapa VARCHAR(255) NOT NULL,
    url_imagem VARCHAR(500) NOT NULL,
    tipo_mapa VARCHAR(50),
    descricao TEXT,
    local_associado_id INT NULL,
    zoom_min INT DEFAULT 1,
    zoom_max INT DEFAULT 10,
    coord_x INT DEFAULT 0,
    coord_y INT DEFAULT 0,
    visivel_para_jogadores BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (local_associado_id) REFERENCES locais(id) ON DELETE CASCADE,
    INDEX idx_mapas_local (local_associado_id),
    INDEX idx_mapas_tipo (tipo_mapa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- Tabela Futura: Mapa Pins (Interatividade)
-- ==========================================

CREATE TABLE IF NOT EXISTS mapa_pins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mapa_id INT NOT NULL,
    pos_x INT NOT NULL,
    pos_y INT NOT NULL,
    tipo VARCHAR(50),
    texto_popup VARCHAR(255),
    link_url VARCHAR(500),
    cor VARCHAR(20) DEFAULT '#FF0000',
    FOREIGN KEY (mapa_id) REFERENCES mapas(id) ON DELETE CASCADE,
    INDEX idx_pins_mapa (mapa_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 🔌 API REST Endpoints {#api-endpoints}

### Estrutura Completa de Rotas

```python
# ==========================================
# ROTAS GLOBAIS
# ==========================================
GET  /                          # Dashboard (próximas sessões, últimas ações)
GET  /health                    # Status do sistema

# ==========================================
# MÓDULO 1: FICHAS (✅ Existente)
# ==========================================
GET    /personagens
GET    /personagem/<id>
POST   /personagem/novo
PUT    /api/personagem/<id>/atributos
POST   /api/personagem/<id>/vantagens
DELETE /api/vantagens/<id>
POST   /api/personagem/<id>/pericias
DELETE /api/pericias/<id>
POST   /api/personagem/<id>/inventario
DELETE /api/inventario/<id>
POST   /api/rolar/<alvo>

# ==========================================
# MÓDULO 2: LOCAIS (🆕 Novo)
# ==========================================
GET    /locais                          # Lista todos
GET    /locais/<id>                     # Detalhe + NPCs + Mapas
POST   /locais/novo
PUT    /locais/<id>/editar
DELETE /locais/<id>
GET    /api/locais/<id>/npcs            # NPCs presentes
GET    /api/locais/<id>/mapas           # Mapas associados

# ==========================================
# MÓDULO 3: NPCs (🆕 Novo)
# ==========================================
GET    /npcs
GET    /npcs/<id>
POST   /npcs/novo
PUT    /npcs/<id>/editar
DELETE /npcs/<id>
POST   /api/npcs/<id>/mover             # Move para outro local
GET    /api/npcs/locais                 # Lista locais (dropdown)
GET    /api/npcs/personagens            # Lista personagens disponíveis

# ==========================================
# MÓDULO 4: MAPAS (🆕 Novo)
# ==========================================
GET    /mapas
GET    /mapas/<id>
POST   /mapas/novo
PUT    /mapas/<id>/editar
DELETE /mapas/<id>
POST   /api/mapas/upload                 # Upload de imagem
GET    /api/atlas                       # Mapa regional/global
```

---

## 🚀 Sequência de Implementação {#sequência-de-implementação}

### Fase 1: Estrutura Base (1-2 dias)
- [x] ✅ Módulo 1: Fichas de Personagem
- [ ] Criar tabelas: `locais`, `npcs`, `mapas`
- [ ] Atualizar schema.sql
- [ ] Criar models: `Local.py`, `NPC.py`, `Mapa.py`

### Fase 2: Módulo Locais (2-3 dias)
- [ ] Implementar CRUD de Locais
- [ ] Página `/locais` (índice com grid)
- [ ] Página `/locais/<id>` (detalhe)
- [ ] Toggle "Visão do Mestre"
- [ ] Upload de imagem

### Fase 3: Módulo NPCs (2-3 dias)
- [ ] Implementar CRUD de NPCs
- [ ] Dropdown de locais no formulário
- [ ] Página `/npcs` (índice)
- [ ] Página `/npcs/<id>` (detalhe)
- [ ] Link para ficha GURPS (quando existir)

### Fase 4: Integração Locais + NPCs (1-2 dias)
- [ ] Consulta dinâmica na página do local
- [ ] Exibir "NPCs Presentes" automaticamente
- [ ] Botão "Mover NPC" (mudar local_atual_id)
- [ ] Atualização em tempo real

### Fase 5: Módulo Mapas (2-3 dias)
- [ ] Implementar CRUD de Mapas
- [ ] Sistema de upload de imagens
- [ ] Visualizador de mapas
- [ ] Zoom básico
- [ ] Exibir mapas na página do local

### Fase 6: Melhorias e Extras (Ongoing)
- [ ] Sistema de busca global
- [ ] Tags/categorias em locais
- [ ] Timeline de eventos
- [ ] Export PDF de fichas
- [ ] Mapa pins interativos (futuro)

---

## 💡 Exemplos Práticos {#exemplos-práticos}

### Exemplo 1: Criando um Local

```python
# POST /locais/novo
{
  "nome": "Taverna do Javali Caolho",
  "tipo": "Taverna",
  "descricao_publica": "Uma taverna acolhedora, famosa por seu javali assado.",
  "descricao_mestre": "O taverna é um ponto de encontro para contrabandistas. O dono, Roberto 'Javali' Silva, é informante da guarda.",
  "imagem_principal_url": "/static/images/taverna_javali.jpg",
  "visivel_para_jogadores": true
}
```

### Exemplo 2: Criando um NPC Ligado a um Local

```python
# POST /npcs/novo
{
  "nome": "Guarda Barba-Ruiva",
  "tipo": "Guarda",
  "status": "Vivo",
  "descricao_breve": "Guarda experiente da cidade, conhecido pela barba ruiva.",
  "descricao_completa": "Joaquim Barba-Ruiva é um veterano da guarda com 20 anos de serviço...",
  "local_atual_id": 1,  # Taverna do Javali
  "ficha_personagem_id": 101,  # Link para ficha GURPS
  "importancia": "Importante"
}
```

### Exemplo 3: Renderização Contextual

Na página `/locais/1`:

```python
# Backend (app.py)
@app.route('/locais/<int:id>')
def ver_local(id):
    local = Local.buscar_por_id(id)
    npcs = NPC.listar_por_local(id)  # SELECT * FROM npcs WHERE local_atual_id = id
    mapas = Mapa.listar_por_local(id)  # SELECT * FROM mapas WHERE local_associado_id = id
    return render_template('local.html', local=local, npcs=npcs, mapas=mapas)
```

```html
<!-- Frontend (local.html) -->
<div class="local-detalhes">
  <h1>{{ local.nome }}</h1>
  <p>{{ local.descricao_publica }}</p>
  
  <div class="secao-npcs">
    <h2>NPCs Presentes</h2>
    {% for npc in npcs %}
      <div class="npc-card">
        <h3>{{ npc.nome }}</h3>
        <p>{{ npc.descricao_breve }}</p>
        {% if npc.ficha_personagem_id %}
          <a href="/personagem/{{ npc.ficha_personagem_id }}">Ver Ficha GURPS</a>
        {% endif %}
      </div>
    {% endfor %}
  </div>
  
  <div class="secao-mapas">
    <h2>Mapas Associados</h2>
    {% for mapa in mapas %}
      <div class="mapa-card">
        <h3>{{ mapa.nome_mapa }}</h3>
        <img src="{{ mapa.url_imagem }}" alt="{{ mapa.nome_mapa }}">
      </div>
    {% endfor %}
  </div>
</div>
```

---

## 📊 Métricas e Objetivos

### Objetivos de Quantidade
- **Locais**: 50-100 locais por campanha média
- **NPCs**: 100-200 NPCs por campanha média
- **Mapas**: 10-30 mapas por campanha
- **Fichas**: 5-10 jogadores + 20-50 NPCs importantes

### Performance Esperada
- Consulta de local + NPCs + Mapas: < 100ms
- Upload de imagem: < 2s
- Renderização de página: < 500ms

---

## 📝 Checklist de Implementação

### Backend
- [ ] Criar models: Local, NPC, Mapa
- [ ] Implementar todas as rotas
- [ ] Upload de arquivos
- [ ] API endpoints

### Frontend
- [ ] Templates HTML para todos os módulos
- [ ] JavaScript para interatividade
- [ ] Sistema de abas/toggles
- [ ] Formulários CRUD

### Testes
- [ ] Testar todas as rotas
- [ ] Testar relacionamentos
- [ ] Testar renderização contextual
- [ ] Testar upload de imagens

---

**Próximo Passo**: Implementar Fase 2 (Módulo Locais)

