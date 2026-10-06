-- ==========================================
-- Acervo do manual e seleção por campanha
-- Rode uma vez, depois de migracoes_myth.sql. Não apaga dados.
-- Campanhas que já existem recebem o catálogo atual marcado,
-- para a mesa não abrir vazia. Campanha nova começa sem marcas.
-- ==========================================

ALTER TABLE pericias_catalogo
    ADD COLUMN origem ENUM('manual', 'campanha') NOT NULL DEFAULT 'manual' AFTER descricao,
    ADD COLUMN id_campanha INT NULL AFTER origem,
    ADD COLUMN pagina INT NULL AFTER id_campanha,
    ADD INDEX idx_pericia_campanha (id_campanha),
    ADD CONSTRAINT fk_pericia_catalogo_campanha FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE;

ALTER TABLE vantagens_desvantagens_catalogo
    ADD COLUMN origem ENUM('manual', 'campanha') NOT NULL DEFAULT 'manual' AFTER categoria,
    ADD COLUMN id_campanha INT NULL AFTER origem,
    ADD COLUMN pagina INT NULL AFTER id_campanha,
    ADD INDEX idx_vantagem_campanha (id_campanha),
    ADD CONSTRAINT fk_vantagem_catalogo_campanha FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE;

ALTER TABLE magias_catalogo
    ADD COLUMN origem ENUM('manual', 'campanha') NOT NULL DEFAULT 'manual' AFTER descricao,
    ADD COLUMN id_campanha INT NULL AFTER origem,
    ADD INDEX idx_magia_campanha (id_campanha),
    ADD CONSTRAINT fk_magia_catalogo_campanha FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE;

ALTER TABLE itens_catalogo
    ADD COLUMN origem ENUM('manual', 'campanha') NOT NULL DEFAULT 'manual' AFTER rd_tipo,
    ADD COLUMN id_campanha INT NULL AFTER origem,
    ADD COLUMN pagina INT NULL AFTER id_campanha,
    ADD INDEX idx_item_campanha (id_campanha),
    ADD CONSTRAINT fk_item_catalogo_campanha FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE;

CREATE TABLE IF NOT EXISTS acervo_criaturas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    categoria ENUM('animal', 'monstro') NOT NULL DEFAULT 'monstro',
    st INT NULL,
    dx INT NULL,
    iq INT NULL,
    ht INT NULL,
    vontade INT NULL,
    percepcao INT NULL,
    velocidade DECIMAL(4,2) NULL,
    esquiva INT NULL,
    deslocamento INT NULL,
    tamanho VARCHAR(40),
    peso VARCHAR(40),
    caracteristicas TEXT,
    pericias TEXT,
    custo INT NULL,
    pagina INT NULL,
    origem ENUM('manual', 'campanha') NOT NULL DEFAULT 'manual',
    id_campanha INT NULL,
    UNIQUE KEY uniq_acervo_criatura_nome (nome),
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS campanha_pericia (
    id_campanha INT NOT NULL,
    id_pericia INT NOT NULL,
    PRIMARY KEY (id_campanha, id_pericia),
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_pericia) REFERENCES pericias_catalogo(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS campanha_vantagem (
    id_campanha INT NOT NULL,
    id_vantagem INT NOT NULL,
    PRIMARY KEY (id_campanha, id_vantagem),
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_vantagem) REFERENCES vantagens_desvantagens_catalogo(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS campanha_magia (
    id_campanha INT NOT NULL,
    id_magia INT NOT NULL,
    PRIMARY KEY (id_campanha, id_magia),
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_magia) REFERENCES magias_catalogo(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS campanha_item (
    id_campanha INT NOT NULL,
    id_item INT NOT NULL,
    PRIMARY KEY (id_campanha, id_item),
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_item) REFERENCES itens_catalogo(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS campanha_criatura (
    id_campanha INT NOT NULL,
    id_acervo INT NOT NULL,
    PRIMARY KEY (id_campanha, id_acervo),
    FOREIGN KEY (id_campanha) REFERENCES campanhas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_acervo) REFERENCES acervo_criaturas(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT IGNORE INTO campanha_pericia (id_campanha, id_pericia)
SELECT c.id, p.id FROM campanhas c JOIN pericias_catalogo p ON p.origem = 'manual';

INSERT IGNORE INTO campanha_vantagem (id_campanha, id_vantagem)
SELECT c.id, v.id FROM campanhas c JOIN vantagens_desvantagens_catalogo v ON v.origem = 'manual';

INSERT IGNORE INTO campanha_magia (id_campanha, id_magia)
SELECT c.id, m.id FROM campanhas c JOIN magias_catalogo m ON m.origem = 'manual';

INSERT IGNORE INTO campanha_item (id_campanha, id_item)
SELECT c.id, i.id FROM campanhas c JOIN itens_catalogo i ON i.origem = 'manual';
