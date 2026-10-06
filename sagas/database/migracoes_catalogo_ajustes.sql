-- Ajuste de catálogo que vale só para a campanha que marcou o registro.
-- Rode uma vez. Não apaga dados.

ALTER TABLE campanha_pericia ADD COLUMN ajustes TEXT NULL;
ALTER TABLE campanha_vantagem ADD COLUMN ajustes TEXT NULL;
ALTER TABLE campanha_magia ADD COLUMN ajustes TEXT NULL;
ALTER TABLE campanha_item ADD COLUMN ajustes TEXT NULL;
ALTER TABLE campanha_criatura ADD COLUMN ajustes TEXT NULL;

INSERT IGNORE INTO campanha_pericia (id_campanha, id_pericia)
SELECT id_campanha, id FROM pericias_catalogo
WHERE origem = 'campanha' AND id_campanha IS NOT NULL;

INSERT IGNORE INTO campanha_vantagem (id_campanha, id_vantagem)
SELECT id_campanha, id FROM vantagens_desvantagens_catalogo
WHERE origem = 'campanha' AND id_campanha IS NOT NULL;

INSERT IGNORE INTO campanha_magia (id_campanha, id_magia)
SELECT id_campanha, id FROM magias_catalogo
WHERE origem = 'campanha' AND id_campanha IS NOT NULL;

INSERT IGNORE INTO campanha_item (id_campanha, id_item)
SELECT id_campanha, id FROM itens_catalogo
WHERE origem = 'campanha' AND id_campanha IS NOT NULL;

INSERT IGNORE INTO campanha_criatura (id_campanha, id_acervo)
SELECT id_campanha, id FROM acervo_criaturas
WHERE origem = 'campanha' AND id_campanha IS NOT NULL;
