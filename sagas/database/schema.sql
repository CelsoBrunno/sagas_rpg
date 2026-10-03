-- ==========================================
-- Sistema de Campanha GURPS - Esquema MySQL Completo
-- Design inspirado na FIAP
-- Versão: 2.0 Completa (Dezembro 2024)
-- ==========================================
-- 
-- Este schema inclui TODAS as funcionalidades do sistema:
-- 
-- ✅ Estrutura completa de tabelas
-- ✅ Sistema de Raças e Classes
-- ✅ Campo pontos_disponiveis para usuários
-- ✅ Campos RD (Redução de Dano) em inventário e itens
-- ✅ Scripts de criação de usuários iniciais
-- ✅ Índices e Foreign Keys otimizados
-- 
-- Este é o arquivo ÚNICO necessário para criar o banco de dados.
-- Todos os outros arquivos SQL foram consolidados aqui.
-- ==========================================

-- Cria o banco de dados (se não existir)
-- Para PythonAnywhere, use: sagasrpg$default
-- Para local, use: sagas_gurps
CREATE DATABASE IF NOT EXISTS sagas_gurps CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- No PythonAnywhere, o banco já existe como 'sagasrpg$default'
-- Ajuste o USE abaixo conforme seu ambiente:
-- use sagasrpg$default;
use sagas_gurps;  -- Local

-- ==========================================
-- REMOÇÃO DE TABELAS (Ordem respeitando Foreign Keys)
-- ==========================================

DROP TABLE IF EXISTS mapa_pins;
DROP TABLE IF EXISTS sessoes_pontos_pc;
DROP TABLE IF EXISTS sessoes_log;
DROP TABLE IF EXISTS rolagens_log;
DROP TABLE IF EXISTS pericias_catalogo;
DROP TABLE IF EXISTS vantagens_desvantagens_catalogo;
DROP TABLE IF EXISTS imagens;
DROP TABLE IF EXISTS mapas;
DROP TABLE IF EXISTS bestiario_imagens;
DROP TABLE IF EXISTS bestiario;
DROP TABLE IF EXISTS npcs;
DROP TABLE IF EXISTS locais;
DROP TABLE IF EXISTS equipamentos_personagem;
DROP TABLE IF EXISTS inventario;
DROP TABLE IF EXISTS pericias;
DROP TABLE IF EXISTS vantagens_desvantagens;
DROP TABLE IF EXISTS atributos;
DROP TABLE IF EXISTS personagens;
DROP TABLE IF EXISTS classes;
DROP TABLE IF EXISTS racas;
DROP TABLE IF EXISTS campanhas;
DROP TABLE IF EXISTS usuarios;

-- ==========================================
-- TABELAS BASE
-- ==========================================

-- Tabela de Usuários
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'usuario') NOT NULL DEFAULT 'usuario',
    pontos_disponiveis INT DEFAULT 0 COMMENT 'Pontos disponíveis concedidos pelo admin para criação de fichas',
    nome_completo VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    INDEX idx_usuarios_pontos_disponiveis (pontos_disponiveis)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Campanhas
CREATE TABLE IF NOT EXISTS campanhas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_campanha VARCHAR(150) NOT NULL,
    id_mestre INT NOT NULL,
    pontos_iniciais INT DEFAULT 100,
    descricao TEXT,
    status ENUM('Ativa', 'Pausada', 'Finalizada') DEFAULT 'Ativa',
    tema VARCHAR(30) NOT NULL DEFAULT 'padrao',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_mestre) REFERENCES usuarios(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- MÓDULO 9: Sistema de Raças e Classes
-- (Criado antes de personagens para permitir Foreign Keys)
-- ==========================================

-- Tabela de Raças
CREATE TABLE IF NOT EXISTS racas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    -- Bônus em Atributos
    bonus_st INT DEFAULT 0,
    bonus_dx INT DEFAULT 0,
    bonus_iq INT DEFAULT 0,
    bonus_ht INT DEFAULT 0,
    -- Bônus em Atributos Derivados
    bonus_pv_extra INT DEFAULT 0,
    bonus_pf_extra INT DEFAULT 0,
    bonus_percepcao_extra INT DEFAULT 0,
    bonus_vontade_extra INT DEFAULT 0,
    -- Custo em pontos (pode ser negativo para raças que dão desvantagens)
    custo_em_pontos INT DEFAULT 0,
    -- Vantagens/Desvantagens automáticas (JSON ou texto)
    vantagens_automaticas TEXT,
    -- Perícias automáticas (JSON ou texto)
    pericias_automaticas TEXT,
    -- Observações
    observacoes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    id_campanha INT,
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE,
    UNIQUE KEY uq_racas_nome_campanha (nome, id_campanha),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Classes
CREATE TABLE IF NOT EXISTS classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    descricao TEXT,
    -- Bônus em Atributos
    bonus_st INT DEFAULT 0,
    bonus_dx INT DEFAULT 0,
    bonus_iq INT DEFAULT 0,
    bonus_ht INT DEFAULT 0,
    -- Bônus em Atributos Derivados
    bonus_pv_extra INT DEFAULT 0,
    bonus_pf_extra INT DEFAULT 0,
    bonus_percepcao_extra INT DEFAULT 0,
    bonus_vontade_extra INT DEFAULT 0,
    -- Custo em pontos (pode ser negativo)
    custo_em_pontos INT DEFAULT 0,
    -- Vantagens/Desvantagens automáticas (JSON ou texto)
    vantagens_automaticas TEXT,
    -- Perícias automáticas (JSON ou texto)
    pericias_automaticas TEXT,
    -- Observações
    observacoes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    id_campanha INT,
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE,
    UNIQUE KEY uq_classes_nome_campanha (nome, id_campanha),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- MÓDULO 1: FICHAS DE PERSONAGEM
-- ==========================================

-- Tabela de Personagens
CREATE TABLE IF NOT EXISTS personagens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    jogador_nome VARCHAR(100),
    id_campanha INT,
    id_usuario_jogador INT,
    raca VARCHAR(50),  -- Mantido para compatibilidade (deprecated)
    raca_id INT,  -- FK para racas (novo sistema)
    classe_id INT,  -- FK para classes
    categoria VARCHAR(50) DEFAULT 'Humano',  -- 'Humano', 'Animal', 'Criatura', 'Outro'
    pontos_base INT DEFAULT 0,
    pontos_ganhos INT DEFAULT 0,
    pontos_desvantagens_max INT DEFAULT 0,
    pontos_gastos INT DEFAULT 0,
    dinheiro DECIMAL(12,2) DEFAULT 0,
    is_pc BOOLEAN DEFAULT TRUE,
    biografia TEXT,
    status ENUM('Ativo', 'Inativo', 'Morto') DEFAULT 'Ativo',
    status_criacao ENUM('Pendente', 'Em_Andamento', 'Aprovado', 'Rejeitado') DEFAULT 'Pendente',
    tipo ENUM('PJ', 'NPC') DEFAULT 'PJ',
    observacoes_mestre TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario_jogador) REFERENCES usuarios(id) ON DELETE SET NULL,
    FOREIGN KEY (raca_id) REFERENCES racas(id) ON DELETE SET NULL,
    FOREIGN KEY (classe_id) REFERENCES classes(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Atributos
CREATE TABLE IF NOT EXISTS atributos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personagem_id INT NOT NULL,
    ST INT NOT NULL DEFAULT 10,
    DX INT NOT NULL DEFAULT 10,
    IQ INT NOT NULL DEFAULT 10,
    HT INT NOT NULL DEFAULT 10,
    custo_total_atributos INT DEFAULT 0,
    PV_extra INT DEFAULT 0,
    PF_extra INT DEFAULT 0,
    percepcao_extra INT DEFAULT 0,
    vontade_extra INT DEFAULT 0,
    FOREIGN KEY (personagem_id) REFERENCES personagens(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Vantagens e Desvantagens
CREATE TABLE IF NOT EXISTS vantagens_desvantagens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personagem_id INT NOT NULL,
    nome_item VARCHAR(200) NOT NULL,
    custo_em_pontos INT NOT NULL,
    notas TEXT,
    FOREIGN KEY (personagem_id) REFERENCES personagens(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Perícias
CREATE TABLE IF NOT EXISTS pericias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personagem_id INT NOT NULL,
    nome_pericia VARCHAR(200) NOT NULL,
    atributo_base ENUM('ST', 'DX', 'IQ', 'HT') NOT NULL DEFAULT 'DX',
    dificuldade ENUM('F', 'M', 'D', 'VD') NOT NULL DEFAULT 'M',
    pontos_investidos INT DEFAULT 0,
    nivel_habilidade_calculado INT,
    FOREIGN KEY (personagem_id) REFERENCES personagens(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de magias (GURPS 4e Módulo Básico)
CREATE TABLE IF NOT EXISTS magias_catalogo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    escola VARCHAR(60) NOT NULL,
    classe VARCHAR(80),
    dificuldade ENUM('D', 'MD') NOT NULL DEFAULT 'D',
    custo VARCHAR(150),
    tempo VARCHAR(60),
    duracao VARCHAR(80),
    pre_requisitos VARCHAR(255),
    pagina INT,
    descricao TEXT,
    UNIQUE KEY uniq_magia_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Grimório: magias do personagem (só o mestre edita)
CREATE TABLE IF NOT EXISTS personagem_magias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personagem_id INT NOT NULL,
    nome VARCHAR(150) NOT NULL,
    escola VARCHAR(60),
    nh INT,
    custo VARCHAR(150),
    tempo VARCHAR(60),
    duracao VARCHAR(80),
    notas TEXT,
    FOREIGN KEY (personagem_id) REFERENCES personagens(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Inventário
CREATE TABLE IF NOT EXISTS inventario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personagem_id INT NOT NULL,
    nome_item VARCHAR(200) NOT NULL,
    quantidade INT DEFAULT 1,
    peso DECIMAL(5,2) DEFAULT 0,
    preco_unitario DECIMAL(10,2) DEFAULT 0,
    quantidade_em_uso INT DEFAULT 0,
    notas TEXT,
    tipo_item ENUM('equipamento', 'consumivel', 'outro') NOT NULL DEFAULT 'outro',
    dano_bal_mod INT DEFAULT 0,
    dano_bal_tipo VARCHAR(50),
    dano_gdp_mod INT DEFAULT 0,
    dano_gdp_tipo VARCHAR(50),
    rd_mod INT DEFAULT 0,
    rd_tipo VARCHAR(50),
    FOREIGN KEY (personagem_id) REFERENCES personagens(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tabela de Equipamentos (slots equipados)
CREATE TABLE IF NOT EXISTS equipamentos_personagem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personagem_id INT NOT NULL,
    inventario_id INT NOT NULL,
    slot ENUM('mao_direita', 'mao_esquerda', 'armadura', 'vestimenta', 'acessorio') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (personagem_id) REFERENCES personagens(id) ON DELETE CASCADE,
    FOREIGN KEY (inventario_id) REFERENCES inventario(id) ON DELETE CASCADE,
    UNIQUE KEY uniq_inventario_slot (inventario_id),
    INDEX idx_equip_personagem (personagem_id),
    INDEX idx_equip_slot (slot)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- MÓDULO 2: LOCAIS (O Hub Central)
-- ==========================================

CREATE TABLE IF NOT EXISTS locais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    tipo VARCHAR(100),               -- 'Taverna', 'Cidade', 'Masmorra', 'Ruína'
    descricao_publica TEXT,           -- O que os jogadores veem
    descricao_mestre TEXT,            -- Notas secretas do mestre
    imagem_principal_url VARCHAR(500), -- URL da imagem do local
    id_campanha INT,
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- MÓDULO 3: NPCs (Listas Contextuais)
-- ==========================================

CREATE TABLE IF NOT EXISTS npcs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'Vivo',  -- 'Vivo', 'Morto', 'Desconhecido'
    descricao_breve VARCHAR(500),      -- Resumo para listas
    descricao_completa TEXT,           -- História completa
    imagem_url VARCHAR(500),            -- URL da imagem do NPC
    
    -- Relação com Locais (Módulo 2)
    local_atual_id INT,
    FOREIGN KEY (local_atual_id) REFERENCES locais(id) ON DELETE SET NULL,
    
    -- Relação opcional com Fichas de Personagem (Módulo 1)
    ficha_personagem_id INT NULL,
    FOREIGN KEY (ficha_personagem_id) REFERENCES personagens(id) ON DELETE SET NULL,
    id_campanha INT,
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- BESTIÁRIO (criaturas por campanha, liberadas pelo mestre)
-- ==========================================

CREATE TABLE IF NOT EXISTS bestiario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_campanha INT NOT NULL,
    nome VARCHAR(150) NOT NULL,
    categoria VARCHAR(100),
    descricao_publica TEXT,
    descricao_mestre TEXT,
    imagem_url VARCHAR(500),
    ficha_personagem_id INT NULL,
    nivel_revelacao TINYINT NOT NULL DEFAULT 0, -- 0 oculta, 1 avistada (foto), 2 derrotada (ficha)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE,
    FOREIGN KEY (ficha_personagem_id) REFERENCES personagens(id) ON DELETE SET NULL,
    UNIQUE KEY uq_bestiario_nome_campanha (nome, id_campanha)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Fotos extras da criatura (a capa fica em bestiario.imagem_url)
CREATE TABLE IF NOT EXISTS bestiario_imagens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_bestiario INT NOT NULL,
    imagem_url VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_bestiario) REFERENCES bestiario(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- MÓDULO 4: MAPAS
-- ==========================================

CREATE TABLE IF NOT EXISTS mapas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_mapa VARCHAR(255) NOT NULL,
    url_imagem VARCHAR(500) NOT NULL,  -- URL da imagem do mapa
    tipo_mapa VARCHAR(50),            -- 'Regional', 'Cidade', 'Masmorra', 'Local', 'Batalha'
    descricao TEXT,
    
    -- Relação com Locais (Módulo 2)
    local_associado_id INT NULL,      -- Nulo se for mapa regional
    FOREIGN KEY (local_associado_id) REFERENCES locais(id) ON DELETE CASCADE,
    id_campanha INT,
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- MÓDULO 4.1: Pins de Mapa (Futuro - Opcional)
-- ==========================================

CREATE TABLE IF NOT EXISTS mapa_pins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mapa_id INT NOT NULL,
    pos_x INT NOT NULL,               -- Posição X no mapa (0-100%)
    pos_y INT NOT NULL,               -- Posição Y no mapa (0-100%)
    texto_popup TEXT,                  -- Texto exibido no hover
    link_url VARCHAR(500),             -- Link opcional (para locais, NPCs, etc)
    cor VARCHAR(20) DEFAULT '#FF0000', -- Cor do pin
    icone VARCHAR(50),                 -- Ícone a usar
    
    FOREIGN KEY (mapa_id) REFERENCES mapas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- MÓDULO 6: Sistema de Imagens Polimórfico
-- ==========================================

CREATE TABLE IF NOT EXISTS imagens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    path_url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    titulo VARCHAR(255),
    descricao TEXT,
    
    -- Chaves Polimórficas
    entidade_tipo VARCHAR(50) NOT NULL, -- 'Personagem', 'NPC', 'Local', 'Item', 'Mapa'
    entidade_id INT NOT NULL,
    
    -- Metadados
    file_size INT, -- Tamanho em bytes
    mime_type VARCHAR(100), -- image/jpeg, image/png, etc
    width INT,
    height INT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- MÓDULO 7: Sessões e Distribuição de Pontos
-- ==========================================

CREATE TABLE IF NOT EXISTS sessoes_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_sessao DATE NOT NULL,
    descricao TEXT,
    data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sessoes_pontos_pc (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sessao_id INT NOT NULL,
    personagem_id INT NOT NULL,
    pontos_ganhos INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sessao_id) REFERENCES sessoes_log(id) ON DELETE CASCADE,
    FOREIGN KEY (personagem_id) REFERENCES personagens(id) ON DELETE CASCADE,
    UNIQUE KEY uniq_sessao_personagem (sessao_id, personagem_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- MÓDULO 8: Log de Rolagens e Catálogos
-- ==========================================

-- Tabela de Log de Rolagens
CREATE TABLE IF NOT EXISTS rolagens_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    personagem_id INT NULL,
    tipo VARCHAR(50) DEFAULT '3d6',
    alvo INT,
    bonus INT DEFAULT 0,
    resultados VARCHAR(50),
    total INT,
    sucesso BOOLEAN,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (personagem_id) REFERENCES personagens(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de Perícias
CREATE TABLE IF NOT EXISTS pericias_catalogo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    atributo_base ENUM('ST','DX','IQ','HT') NOT NULL,
    dificuldade ENUM('F','M','D','VD') NOT NULL,
    custo_texto VARCHAR(100),
    descricao TEXT,
    UNIQUE KEY uniq_pericia_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de Vantagens e Desvantagens
CREATE TABLE IF NOT EXISTS vantagens_desvantagens_catalogo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    tipo ENUM('Vantagem', 'Desvantagem') NOT NULL,
    custo_base INT NOT NULL,
    custo_texto VARCHAR(100),
    descricao TEXT,
    categoria VARCHAR(100),
    UNIQUE KEY uniq_vd_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Catálogo de Itens
CREATE TABLE IF NOT EXISTS itens_catalogo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    categoria VARCHAR(100),
    preco DECIMAL(10,2) NOT NULL DEFAULT 0,
    peso DECIMAL(6,3) DEFAULT 0,
    descricao TEXT,
    tipo_item ENUM('equipamento', 'consumivel', 'outro') NOT NULL DEFAULT 'outro',
    dano_bal_mod INT DEFAULT 0,
    dano_bal_tipo VARCHAR(50),
    dano_gdp_mod INT DEFAULT 0,
    dano_gdp_tipo VARCHAR(50),
    rd_mod INT DEFAULT 0,
    rd_tipo VARCHAR(50),
    UNIQUE KEY uniq_item_catalogo_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ==========================================
-- ÍNDICES PARA PERFORMANCE
-- ==========================================

-- Índices para Personagens
CREATE INDEX idx_personagem_nome ON personagens(nome);
CREATE INDEX idx_personagem_tipo ON personagens(tipo);
CREATE INDEX idx_personagem_status ON personagens(status);
CREATE INDEX idx_personagem_ispc ON personagens(is_pc);
CREATE INDEX idx_personagem_campanha ON personagens(id_campanha);
CREATE INDEX idx_personagem_usuario ON personagens(id_usuario_jogador);
CREATE INDEX idx_personagem_categoria ON personagens(categoria);

-- Índices para Atributos e Perícias
CREATE INDEX idx_atributos_personagem ON atributos(personagem_id);
CREATE INDEX idx_vantagens_personagem ON vantagens_desvantagens(personagem_id);
CREATE INDEX idx_pericias_personagem ON pericias(personagem_id);
CREATE INDEX idx_inventario_personagem ON inventario(personagem_id);

-- Índices para Sessões
CREATE INDEX idx_sessoes_data ON sessoes_log(data_sessao);
CREATE INDEX idx_sessoes_pontos_personagem ON sessoes_pontos_pc(personagem_id);
CREATE INDEX idx_sessoes_pontos_sessao ON sessoes_pontos_pc(sessao_id);

-- Índices para Locais
CREATE INDEX idx_local_tipo ON locais(tipo);
CREATE INDEX idx_local_nome ON locais(nome);
CREATE INDEX idx_local_campanha ON locais(id_campanha);

-- Índices para NPCs
CREATE INDEX idx_npc_local ON npcs(local_atual_id);
CREATE INDEX idx_npc_status ON npcs(status);
CREATE INDEX idx_npc_ficha ON npcs(ficha_personagem_id);
CREATE INDEX idx_npc_nome ON npcs(nome);
CREATE INDEX idx_npc_campanha ON npcs(id_campanha);

-- Índices para Mapas
CREATE INDEX idx_mapa_local ON mapas(local_associado_id);
CREATE INDEX idx_mapa_tipo ON mapas(tipo_mapa);
CREATE INDEX idx_mapa_campanha ON mapas(id_campanha);

-- Índices para Pins de Mapa
CREATE INDEX idx_mapa_pins_mapa ON mapa_pins(mapa_id);

-- Índices para Imagens
CREATE INDEX idx_imagens_entidade ON imagens(entidade_tipo, entidade_id);

-- Índices para Rolagens
CREATE INDEX idx_rolagens_created ON rolagens_log(created_at);
CREATE INDEX idx_rolagens_personagem ON rolagens_log(personagem_id);

-- Índices para Raças e Classes
-- Nota: nome + id_campanha é único em racas e classes (UNIQUE KEY na tabela)
CREATE INDEX idx_racas_active ON racas(is_active);
CREATE INDEX idx_classes_active ON classes(is_active);
CREATE INDEX idx_personagem_raca ON personagens(raca_id);
CREATE INDEX idx_personagem_classe ON personagens(classe_id);

-- ==========================================
-- DADOS INICIAIS E SCRIPTS ÚTEIS
-- ==========================================

-- ==========================================
-- Script para criar/verificar usuário ADMIN
-- ==========================================
-- Login padrão: admin
-- Senha padrão: admin
-- ==========================================

-- Verificar se o admin já existe
-- SELECT 
--     id,
--     username,
--     email,
--     role,
--     is_active,
--     created_at
-- FROM usuarios
-- WHERE username = 'admin' AND role = 'admin';

-- Criar admin se não existir
INSERT INTO usuarios (username, email, hashed_password, role, nome_completo, is_active, pontos_disponiveis)
SELECT 
    'admin',
    'admin@sagas.local',
    MD5('admin'),
    'admin',
    'Administrador',
    TRUE,
    0
WHERE NOT EXISTS (
    SELECT 1 FROM usuarios WHERE username = 'admin' AND role = 'admin'
);

-- Jogadores da mesa são criados pelo mestre, fora deste arquivo.
-- Não grave senhas no repositório.

-- ==========================================
-- NOTAS SOBRE MIGRATIONS
-- ==========================================
-- 
-- Este schema já inclui todas as funcionalidades:
-- 
-- 1. Campo pontos_disponiveis na tabela usuarios (linha 58)
--    - Permite que o admin conceda pontos aos usuários
--    - Migration original: migration_add_pontos_usuarios.sql
-- 
-- 2. Tabelas racas e classes (linhas 371-424)
--    - Sistema completo de raças e classes com bônus
--    - Foreign keys em personagens (raca_id, classe_id)
--    - Migration original: migration_add_racas_classes.sql
-- 
-- 3. Campos RD (Redução de Dano) nas tabelas inventario e itens_catalogo
--    - rd_mod e rd_tipo já incluídos no schema
-- 
-- Para bancos de dados EXISTENTES que não possuem essas funcionalidades,
-- execute as migrations correspondentes antes de usar este schema completo.
-- 
-- ==========================================
-- FIM DO SCHEMA
-- ==========================================

-- ==========================================
-- COMANDOS ÚTEIS PARA VERIFICAÇÃO
-- ==========================================
-- 
-- Verificar todas as tabelas:
-- SHOW TABLES;
--
-- Ver estrutura de uma tabela:
-- DESCRIBE personagens;
-- DESCRIBE locais;
-- DESCRIBE npcs;
-- DESCRIBE mapas;
-- DESCRIBE usuarios;
-- DESCRIBE racas;
-- DESCRIBE classes;
--
-- Verificar índices:
-- SHOW INDEX FROM personagens;
-- SHOW INDEX FROM usuarios;
--
-- Verificar Foreign Keys:
-- SELECT 
--     TABLE_NAME,
--     COLUMN_NAME,
--     CONSTRAINT_NAME,
--     REFERENCED_TABLE_NAME,
--     REFERENCED_COLUMN_NAME
-- FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
-- WHERE TABLE_SCHEMA = 'sagas_gurps'
--     AND REFERENCED_TABLE_NAME IS NOT NULL;
--
-- Verificar usuários criados:
-- SELECT id, username, email, role, pontos_disponiveis, is_active, created_at
-- FROM usuarios
-- ORDER BY id;
--
-- Verificar raças e classes:
-- SELECT id, nome, is_active FROM racas ORDER BY nome;
-- SELECT id, nome, is_active FROM classes ORDER BY nome;
