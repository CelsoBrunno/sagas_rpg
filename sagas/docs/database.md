# 🗄️ Banco de Dados - Sistema de Campanha GURPS

Este diretório contém os arquivos SQL para criação e configuração do banco de dados MySQL.

## 📋 Arquivos

- `schema.sql` - Script completo para criação do banco de dados e todas as tabelas

## 🚀 Como Usar

### Opção 1: Pelo Terminal/Linha de Comando

```bash
# Conecte-se ao MySQL (você precisará da senha do root)
mysql -u root -p < database/schema.sql
```

### Opção 2: Pelo MySQL Workbench

1. Abra o MySQL Workbench
2. Conecte-se ao seu servidor MySQL
3. Vá em File → Open SQL Script
4. Selecione o arquivo `database/schema.sql`
5. Clique em "Execute" ou pressione `Ctrl + Shift + Enter`

### Opção 3: Manualmente (copiar e colar)

1. Abra o arquivo `database/schema.sql` em um editor de texto
2. Abra o MySQL Workbench ou terminal MySQL
3. Copie todo o conteúdo do arquivo
4. Cole no MySQL e execute

## 📊 Estrutura do Banco de Dados

### Tabelas Criadas:

#### Módulo 1: Fichas de Personagem (Já Implementado)
1. **personagens** - Armazena informações básicas dos personagens
2. **atributos** - Atributos básicos (ST, DX, IQ, HT)
3. **vantagens_desvantagens** - Lista de vantagens e desvantagens
4. **pericias** - Perícias e habilidades dos personagens
5. **inventario** - Itens e equipamentos

#### Módulo 2: Locais (O Hub Central)
6. **locais** - Catálogo de locais visitáveis da campanha

#### Módulo 3: NPCs
7. **npcs** - Personagens do mestre, contextuais aos locais

#### Módulo 4: Mapas
8. **mapas** - Recursos visuais dos locais
9. **mapa_pins** - Pins interativos nos mapas (futuro)

### Arquitetura de Relacionamentos:

- **Locais** é o hub central (pivô) que conecta NPCs e Mapas
- **NPCs** → se conecta a **Locais** via `local_atual_id`
- **NPCs** → se conecta a **Personagens** via `ficha_personagem_id` (opcional)
- **Mapas** → se conecta a **Locais** via `local_associado_id`

### Características:

- ✅ **Charset**: utf8mb4 (suporta emojis e caracteres especiais)
- ✅ **Collation**: utf8mb4_unicode_ci (ordenação Unicode)
- ✅ **Engine**: InnoDB (suporte a transações e chaves estrangeiras)
- ✅ **Foreign Keys**: Relacionamentos com CASCADE (exclusão automática)
- ✅ **Índices**: Otimização de consultas
- ✅ **Timestamps**: Created_at e Updated_at automáticos

## 🔍 Verificando a Instalação

Após executar o schema, você pode verificar se tudo foi criado corretamente:

```sql
-- Ver todas as tabelas
SHOW TABLES;

-- Ver estrutura da tabela personagens
DESCRIBE personagens;

-- Ver índices criados
SHOW INDEX FROM personagens;

-- Verificar banco de dados
SELECT DATABASE();
```

## 📝 Exemplo de Dados

Para inserir dados de exemplo no banco, execute:

```bash
python populate_example_data.py
```

## ⚠️ Importante

- **Backup**: Sempre faça backup antes de recriar o banco
- **Dados**: O script `DROP TABLE` remove dados existentes
- **Credenciais**: Configure corretamente no arquivo `config.py` ou variáveis de ambiente

## 🆘 Problemas Comuns

### Erro de permissão:
```bash
# Dar permissão ao usuário
GRANT ALL PRIVILEGES ON sagas_gurps.* TO 'seu_usuario'@'localhost';
FLUSH PRIVILEGES;
```

### Banco já existe:
O script usa `CREATE DATABASE IF NOT EXISTS`, então não há problema.

### Tabela já existe:
O script inclui `DROP TABLE IF EXISTS` no início para recriar as tabelas.

## 📚 Mais Informações

Para mais detalhes sobre o sistema, consulte:
- `README.md` - Visão geral do projeto
- `INSTALL.md` - Guia de instalação completo
- `IDENTIDADE_VISUAL.md` - Design e identidade visual FIAP
