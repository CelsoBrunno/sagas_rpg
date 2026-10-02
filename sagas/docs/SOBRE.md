# 🎯 Sobre o Sistema de Campanha GURPS

## 📝 Visão Geral

Este é um sistema completo de gerenciamento de campanhas para **GURPS (Generic Universal RolePlaying System)**, desenvolvido com Flask, MySQL e Python. O sistema foi projetado para gerenciar personagens, calcular atributos derivados automaticamente e fornecer uma interface moderna inspirada no design da **FIAP**.

## 🎨 Design Inspirado na FIAP

O design visual foi baseado no site da FIAP (https://www.fiap.com.br/graduacao/), incorporando:

- **Paleta de Cores**: Magenta vibrante (#FF0066) como cor primária e charcoal escuro (#1A1A1A) como fundo base
- **Tipografia**: Montserrat para títulos e Inter para corpo do texto
- **Componentes Modernos**: Cards com sombras, botões com gradientes e animações suaves
- **Interface Responsiva**: Adaptável para desktop, tablet e mobile

## 🎲 Funcionalidades GURPS

### Cálculos Automáticos

O sistema calcula automaticamente todos os atributos derivados conforme as regras do GURPS:

- **Velocidade Básica**: (DX + HT) / 4
- **Esquiva**: Velocidade Básica + 3
- **Pontos de Vida (PV)**: Baseado em ST
- **Pontos de Fadiga (PF)**: Baseado em HT
- **Peso Máximo (PM)**: ST × 15

### Sistema de Rolagens

Rolagens interativas com botões clicáveis para:
- Atributos (ST, DX, IQ, HT)
- Perícias (com NH calculado automaticamente)
- Feedback visual (sucesso, falha, crítico)
- Histórico de rolagens

### Estrutura de Dados

O banco de dados foi modelado para suportar completamente o sistema GURPS:

```
personagens       → Informações básicas
atributos         → ST, DX, IQ, HT
vantagens_desvantagens → Lista de vantagens/desvantagens
pericias          → Perícias com NH calculado
inventario        → Itens e equipamentos
```

## 🏗️ Arquitetura

### Backend
- **Flask**: Framework web Python
- **MySQL**: Banco de dados relacional
- **Pool de Conexões**: Gerenciamento eficiente de conexões
- **API RESTful**: Endpoints para operações CRUD

### Frontend
- **HTML5**: Estrutura semântica
- **CSS3**: Estilos modernos com variáveis CSS
- **JavaScript**: Lógica de interface e comunicação com API
- **Design Responsivo**: Mobile-first approach

### Segurança
- Proteção contra SQL Injection (prepared statements)
- Variáveis de ambiente para credenciais
- Pool de conexões seguro

## 📊 Estrutura de Código

```
app.py              → Rotas e lógica da aplicação
models.py           → Modelos de dados (Personagem, Atributos, etc)
database.py         → Gerenciamento de conexões MySQL
config.py           → Configurações centralizadas
schema.sql          → Estrutura do banco de dados

static/css/style.css → Design inspirado na FIAP
static/js/main.js    → Lógica GURPS (cálculos e rolagens)

templates/          → Templates HTML (Jinja2)
```

## 🔄 Fluxo de Dados

1. **Usuário Interage** → Interface HTML
2. **JavaScript Captura** → Evento (clique, mudança)
3. **API Fetch** → Requisição HTTP para Flask
4. **Flask Processa** → Models.py valida e executa
5. **MySQL Persiste** → Banco de dados atualizado
6. **Resposta JSON** → Retorna para o cliente
7. **JavaScript Atualiza** → DOM atualizado

## 🎮 Experiência do Usuário

### Criar Personagem
1. Navega para "Novo Personagem"
2. Preenche nome, raça, pontos base
3. Define atributos iniciais (ST, DX, IQ, HT)
4. Sistema calcula automaticamente os derivados

### Gerenciar Ficha
- **Aba Principal**: Atributos e valores derivados
- **Aba Vantagens**: Adicionar/remover vantagens e desvantagens
- **Aba Perícias**: Adicionar perícias com cálculo de NH
- **Aba Inventário**: (futuro) Itens e equipamentos

### Rolar Dados
1. Clica em "Rolar" ao lado de atributo/perícia
2. Sistema executa rolagem 3d6
3. Compara com o alvo (atributo ou NH)
4. Exibe resultado: sucesso, falha ou crítico
5. Atualiza histórico visual

## 🚀 Extensibilidade

O sistema foi projetado para crescer:

- **Módulo de NPCs**: Personagens não jogadores
- **Módulo de Locais**: Mapa de locais do mundo
- **Módulo de Mapas**: Visualização cartográfica
- **Sistema de Sessões**: Registro de cronologia
- **Sistema de Combate**: Gerenciamento de batalhas
- **Sistema de Inventário**: Gestão completa de itens

## 🔧 Configuração

### Variáveis de Ambiente

Todas as configurações sensíveis são gerenciadas via `.env`:

```env
SECRET_KEY=chave-secreta-da-aplicacao
DEBUG=False
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=senha
MYSQL_DB=sagas_gurps
```

### Banco de Dados

O esquema MySQL foi projetado com:
- **Integridade Referencial**: Foreign keys com CASCADE
- **Índices**: Performance otimizada para queries
- **Tipos Enumerados**: Validação de dados
- **Timestamps**: Controle de criação e atualização

## 📈 Performance

- **Pool de Conexões**: 5 conexões simultâneas
- **Índices**: Queries otimizadas com índices em campos-chave
- **Cache**: Preparação para cache de resultados frequentes
- **Compressão**: Assets estáticos minificados (futuro)

## 🎓 Tecnologias Utilizadas

- **Python 3.8+**: Linguagem backend
- **Flask 3.0**: Framework web
- **MySQL 5.7+**: Banco de dados
- **HTML5**: Estrutura
- **CSS3**: Estilização com variáveis
- **JavaScript ES6+**: Lógica frontend
- **Jinja2**: Template engine

## 🌟 Diferenciais

1. **Calculadora GURPS Nativa**: Entende todas as regras do sistema
2. **Interface Moderna**: Design inspirado em referências visuais
3. **Rolagens Interativas**: Sistema de dados integrado
4. **Sistema de Abas**: Organização clara de informações
5. **Responsivo**: Funciona em qualquer dispositivo
6. **Extensível**: Arquitetura preparada para novos módulos
7. **Open Source**: Código livre e aberto

## 📝 Licença e Créditos

- **GURPS**: Sistema de propriedade da Steve Jackson Games
- **Design**: Inspirado em https://www.fiap.com.br/graduacao/
- **Desenvolvido**: Para uso em campanhas de RPG
- **Licença**: Uso educativo e de entretenimento

---

**Sistema desenvolvido para facilitar o gerenciamento de campanhas GURPS!** 🎲

