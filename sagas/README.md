# 🎲 Sistema de Gerenciamento de Campanha GURPS

Sistema completo para gerenciamento de campanhas **GURPS 4ª Edição** desenvolvido com Flask, MySQL e Python.

## 🚀 Início Rápido

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar Banco de Dados
```bash
mysql -u root -p < database/schema.sql
```

### 3. Configurar Variáveis de Ambiente
```bash
cp .env.example .env
# Edite o .env com suas credenciais do MySQL
```

### 4. Executar o Sistema
```bash
python app.py
```

Acesse: http://localhost:5000

## 📋 Funcionalidades

### ✅ Módulo de Personagens (GURPS)
- Gerenciamento completo de PJs e NPCs
- Cálculo automático de atributos derivados (PV, PF, Esquiva, Velocidade)
- Sistema de vantagens e desvantagens
- Perícias com cálculo automático de NH
- Sistema de rolagens interativas (3d6)

### ✅ Sistema de Campanhas
- Criação e gerenciamento de campanhas
- Sistema de aprovação de fichas (mestre/jogador)
- Controle de pontos iniciais por campanha

### ✅ Módulo de Locais
- Catálogo de locais da campanha
- Descrições públicas e privadas (mestre)
- Relacionamento com NPCs e mapas

### ✅ Módulo de NPCs
- Gerenciamento de personagens não jogadores
- Vinculação a locais (contextual)
- Link opcional para fichas GURPS completas

### ✅ Módulo de Mapas
- Upload e visualização de mapas
- Associação com locais
- Suporte a múltiplos mapas por local

### ✅ Autenticação
- Sistema de login/registro
- Controle de permissões (Admin/Usuário)
- Sessões seguras

## 📁 Estrutura do Projeto

```
sagas/
├── app.py                 # Aplicação Flask principal
├── config.py              # Configurações
├── database.py            # Pool de conexões MySQL
├── requirements.txt       # Dependências Python
├── .env.example           # Exemplo de variáveis de ambiente
├── .gitignore            # Arquivos ignorados pelo Git
│
├── models/                # Models do sistema
│   ├── __init__.py
│   ├── personagem.py      # Personagens, Atributos, Perícias, Vantagens
│   ├── campanha.py        # Campanhas
│   ├── usuario.py         # Usuários e autenticação
│   ├── local.py           # Locais
│   ├── npc.py             # NPCs
│   ├── mapa.py            # Mapas
│   └── imagem.py          # Sistema de imagens
│
├── database/
│   └── schema.sql         # Schema completo do banco de dados
│
├── static/
│   ├── css/
│   │   └── style.css      # Estilos (design FIAP)
│   ├── js/
│   │   └── main.js        # Lógica JavaScript GURPS
│   └── uploads/           # Arquivos enviados
│
├── templates/             # Templates HTML (Jinja2)
│   ├── base.html
│   ├── index.html
│   ├── personagem.html
│   └── ...
│
├── docs/                  # Documentação
│   ├── installation.md
│   ├── architecture.md
│   └── ...
│
└── GURPS 4E - Módulo Básico - *.pdf  # Referência oficial
```

## 🛠️ Tecnologias

- **Backend**: Flask 3.0 (Python)
- **Banco de Dados**: MySQL 5.7+ (com pool de conexões)
- **Frontend**: HTML5, CSS3, JavaScript ES6+
- **Autenticação**: Sessões Flask

## 🎲 Regras GURPS Implementadas

### Cálculo de Atributos
- **PV (Pontos de Vida)**: ST
- **PF (Pontos de Fadiga)**: HT
- **Velocidade Básica**: (DX + HT) / 4
- **Esquiva**: Velocidade Básica + 3 + Percepção Extra (cada ponto = +1 Esquiva)
- **Peso Morto**: ST × 15 libras

### Cálculo de Custos
- Atributos ≤ 10: custo negativo ou zero
- Atributos > 10: +20 pontos por ponto acima de 10

### Perícias
- Nível = Atributo Base + Modificador de Dificuldade + Bônus de Pontos
- Dificuldades: F (0), M (0), D (-1), VD (-2)

### Rolagens
- Sistema 3d6 vs. Nível
- Detecção de crítico (3-4) e falha crítica (18)

## 📚 Documentação

Documentação detalhada disponível em `docs/`:
- `docs/installation.md` - Guia completo de instalação
- `docs/architecture.md` - Arquitetura do sistema
- `docs/TODO.md` - Próximas implementações

## 🔒 Segurança

- Proteção contra SQL Injection (prepared statements)
- Variáveis de ambiente para credenciais sensíveis
- Pool de conexões seguro
- Validação de uploads de arquivos

## 🚧 Próximas Funcionalidades

- Inventário com cálculo de carga
- Sistema de combate
- Timeline de eventos da campanha
- Exportação de fichas em PDF
- Pins interativos em mapas

## 📝 Licença

Sistema desenvolvido para uso em campanhas de RPG. GURPS é marca registrada da Steve Jackson Games.

## 👨‍💻 Contribuindo

Para contribuir, consulte a documentação em `docs/` e siga os padrões de código estabelecidos.

---

**Desenvolvido para facilitar o gerenciamento de campanhas GURPS!** 🎲
