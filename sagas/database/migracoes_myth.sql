-- ==========================================
-- Migrações para bancos que já existiam antes da campanha Myth
-- Rode uma vez, na ordem. Não apaga dados.
-- (Banco novo criado pelo schema.sql já tem tudo isto.)
-- ==========================================

-- 1. Tema visual por campanha
ALTER TABLE campanhas ADD COLUMN tema VARCHAR(30) NOT NULL DEFAULT 'padrao' AFTER status;
UPDATE campanhas SET tema = 'myth' WHERE nome_campanha = 'Myth';

-- 2. Raças e classes por campanha (nome único dentro da campanha)
ALTER TABLE racas
    ADD COLUMN id_campanha INT,
    DROP INDEX nome,
    ADD UNIQUE KEY uq_racas_nome_campanha (nome, id_campanha),
    ADD CONSTRAINT fk_racas_campanha FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE;

ALTER TABLE classes
    ADD COLUMN id_campanha INT,
    DROP INDEX nome,
    ADD UNIQUE KEY uq_classes_nome_campanha (nome, id_campanha),
    ADD CONSTRAINT fk_classes_campanha FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE;

-- 3. Locais, NPCs e mapas por campanha
ALTER TABLE locais
    ADD COLUMN id_campanha INT,
    ADD INDEX idx_local_campanha (id_campanha),
    ADD CONSTRAINT fk_locais_campanha FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE;

ALTER TABLE npcs
    ADD COLUMN id_campanha INT,
    ADD INDEX idx_npc_campanha (id_campanha),
    ADD CONSTRAINT fk_npcs_campanha FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE;

ALTER TABLE mapas
    ADD COLUMN id_campanha INT,
    ADD INDEX idx_mapa_campanha (id_campanha),
    ADD CONSTRAINT fk_mapas_campanha FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE;

-- 4. Bestiário
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

-- 5. Fotos extras do bestiário
CREATE TABLE IF NOT EXISTS bestiario_imagens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_bestiario INT NOT NULL,
    imagem_url VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_bestiario) REFERENCES bestiario(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Campanha Myth renomeada para Os Senhores Caídos
UPDATE campanhas SET nome_campanha = 'Os Senhores Caídos', descricao = 'Ano 17 da Grande Guerra contra o Escuro.'
WHERE nome_campanha = 'Myth';
UPDATE mapas SET nome_mapa = 'Mapa-múndi dos Senhores Caídos' WHERE nome_mapa = 'Mapa-múndi de Myth';

-- 7. Grimório: magias do personagem
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

-- 8. Catálogo de magias (depois rode: python scripts/populate/magias_catalogo.py)
ALTER TABLE personagem_magias
    MODIFY custo VARCHAR(150), MODIFY tempo VARCHAR(60), MODIFY duracao VARCHAR(80);

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

-- 6. Acesso temporário a uma ficha, sem trocar o dono
CREATE TABLE IF NOT EXISTS acessos_temporarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_personagem INT NOT NULL,
    id_usuario INT NOT NULL,
    expira_em DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_acesso_personagem_usuario (id_personagem, id_usuario),
    CONSTRAINT fk_acesso_temp_personagem FOREIGN KEY (id_personagem)
        REFERENCES personagens(id) ON DELETE CASCADE,
    CONSTRAINT fk_acesso_temp_usuario FOREIGN KEY (id_usuario)
        REFERENCES usuarios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
