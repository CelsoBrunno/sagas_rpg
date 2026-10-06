-- Muito Difícil nas perícias passa de VD para MD, a mesma sigla das magias.

ALTER TABLE pericias
    MODIFY dificuldade ENUM('F', 'M', 'D', 'VD', 'MD') NOT NULL DEFAULT 'M';

UPDATE pericias SET dificuldade = 'MD' WHERE dificuldade = 'VD';

ALTER TABLE pericias
    MODIFY dificuldade ENUM('F', 'M', 'D', 'MD') NOT NULL DEFAULT 'M';

ALTER TABLE pericias_catalogo
    MODIFY dificuldade ENUM('F', 'M', 'D', 'VD', 'MD') NOT NULL;

UPDATE pericias_catalogo SET dificuldade = 'MD' WHERE dificuldade = 'VD';

ALTER TABLE pericias_catalogo
    MODIFY dificuldade ENUM('F', 'M', 'D', 'MD') NOT NULL;

UPDATE campanha_pericia
SET ajustes = REPLACE(
    REPLACE(ajustes, '"dificuldade": "VD"', '"dificuldade": "MD"'),
    '"dificuldade":"VD"',
    '"dificuldade":"MD"'
)
WHERE ajustes LIKE '%"VD"%';
