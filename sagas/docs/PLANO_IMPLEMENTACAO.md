# 📅 Plano de Implementação - Sistema de Campanha GURPS

## 🎯 Objetivo
Expandir o sistema atual de Fichas de Personagem para incluir os módulos de Locais, NPCs e Mapas, criando um "Campaign Manager" completo.

---

## ✅ Status Atual

### Módulos Implementados
- ✅ **Módulo 1: Fichas de Personagem** (Completo)
  - Criar, editar, visualizar personagens
  - Atributos básicos e derivados
  - Vantagens e desvantagens
  - Perícias com NH calculado
  - Sistema de rolagens interativo

---

## 🚀 Próximos Passos

### Sprint 1: Estrutura Base de Dados (2 dias)

#### Dia 1: Criar Tabelas
```bash
# Executar schema expandido
mysql -u root -p sagas_gurps < database/schema_completo.sql
```

Arquivos a criar/modificar:
- [ ] `database/schema_completo.sql` - Adicionar tabelas locais, npcs, mapas
- [ ] `models/locais.py` - Model Local
- [ ] `models/npcs.py` - Model NPC
- [ ] `models/mapas.py` - Model Mapa

#### Dia 2: Criar Models Python
- [ ] `Local.buscar_por_id()`
- [ ] `Local.criar()`, `Local.atualizar()`, `Local.deletar()`
- [ ] `NPC.buscar_por_id()`, `NPC.listar_por_local()`
- [ ] `NPC.criar()`, `NPC.mover_para_local()`
- [ ] `Mapa.buscar_por_id()`, `Mapa.listar_por_local()`

---

### Sprint 2: Módulo Locais (3 dias)

#### Dia 3-4: CRUD Locais
- [ ] `app.py` - Rotas Flask para locais
- [ ] `templates/locais_index.html` - Lista de locais
- [ ] `templates/local_detalhe.html` - Página de detalhe
- [ ] Upload de imagens (pasta `static/uploads/locais/`)

#### Dia 5: Funcionalidades Extras
- [ ] Filtros na lista (por tipo, região)
- [ ] Busca por nome
- [ ] Toggle "Visão do Mestre"
- [ ] Edição inline de descrição mestre

**Entregável**: Usuário consegue criar e visualizar locais.

---

### Sprint 3: Módulo NPCs (3 dias)

#### Dia 6-7: CRUD NPCs
- [ ] `app.py` - Rotas Flask para NPCs
- [ ] `templates/npcs_index.html` - Lista de NPCs
- [ ] `templates/npc_detalhe.html` - Página de detalhe
- [ ] Dropdown de locais no formulário
- [ ] Seleção de ficha de personagem

#### Dia 8: Integração com Locais
- [ ] Exibir NPCs na página do local
- [ ] Botão "Mover NPC" (mudar local_atual_id)
- [ ] Indicador visual de NPC com/sem ficha

**Entregável**: Usuário consegue criar NPCs vinculados a locais.

---

### Sprint 4: Módulo Mapas (2 dias)

#### Dia 9: CRUD Mapas
- [ ] `app.py` - Rotas Flask para mapas
- [ ] `templates/mapas_index.html` - Grid de miniaturas
- [ ] `templates/mapa_visualizador.html` - Visualizador
- [ ] Sistema de upload de imagens
- [ ] Exibir mapas na página do local

#### Dia 10: Polimento
- [ ] Zoom básico (JavaScript)
- [ ] Botão download
- [ ] "Atlas" (mapas sem local)

**Entregável**: Usuário consegue associar mapas a locais.

---

### Sprint 5: Melhorias (1-2 dias)

#### Integração Completa
- [ ] Dashboard inicial (/)
- [ ] Busca global (todos os módulos)
- [ ] Navegação breadcrumb
- [ ] Indicadores de status

#### UX/UI
- [ ] Ícones e badges
- [ ] Animações de transição
- [ ] Tooltips informativos
- [ ] Confirmações de exclusão

**Entregável**: Sistema completo e polido.

---

## 📊 Estimativa Total

- **Tempo total**: 10-12 dias de trabalho
- **Linhas de código**: ~3.000-4.000 linhas
- **Arquivos novos**: ~15-20 arquivos

---

## 🛠️ Ferramentas e Tecnologias

### Backend
- Flask (rotas e lógica)
- MySQL (banco de dados)
- SQLAlchemy ORM (opcional)

### Frontend
- HTML5 + Jinja2
- CSS3 (design FIAP)
- JavaScript (interatividade)

### Upload de Arquivos
- Biblioteca: `werkzeug` (Flask)
- Configuração: `UPLOAD_FOLDER = 'static/uploads/'`
- Validação: Tipo e tamanho de arquivo

---

## 📋 Checklist de Validação

### Funcionalidades Core
- [ ] Posso criar um local
- [ ] Posso criar um NPC vinculado a um local
- [ ] Na página do local, vejo os NPCs automaticamente
- [ ] Posso mover um NPC para outro local
- [ ] Posso associar mapas a um local
- [ ] Na página do local, vejo os mapas associados

### Integração
- [ ] NPCs podem ter fichas GURPS
- [ ] Link funciona: NPC → Ficha
- [ ] Personagens PJ e NPC usam mesma estrutura
- [ ] Dados são consistentes entre módulos

### UX
- [ ] Navegação intuitiva
- [ ] Feedback visual claro
- [ ] Mensagens de erro úteis
- [ ] Performance aceitável (< 1s)

---

## 🐛 Riscos e Mitigações

### Risco 1: Upload de Arquivos
**Problema**: Gerenciar upload de imagens (tamanho, segurança)
**Solução**: Validar tipo/extensão, limitar tamanho, sanitizar nomes

### Risco 2: Performance
**Problema**: Muitas consultas SQL em uma página
**Solução**: Usar JOINs, cache quando possível, índices no banco

### Risco 3: Complexidade de Relações
**Problema**: Local pode ter muitos NPCs/Mapas
**Solução**: Paginação, lazy loading, AJAX para carregar dados

---

## 📈 Métricas de Sucesso

### Quantitativas
- Sistema suporta 100+ locais
- Sistema suporta 200+ NPCs
- Tempo de carregamento < 1s
- Zero erros SQL em produção

### Qualitativas
- Interface intuitiva (sem necessidade de manual)
- Dados consistentes e íntegros
- Experiência fluida para o mestre

---

## 🎯 Foco no Valor

### O que este sistema permite ao Mestre?
1. **Contextualização**: Ver onde cada NPC está agora
2. **Navegação**: Entender o layout do mundo
3. **Rastreamento**: Acompanhar movimentação de NPCs
4. **Preparação**: Planejar sessões com antecedência

### ROI (Retorno sobre Investimento)
- **Tempo economizado**: 1h/sessão → 15min/sessão
- **Qualidade**: Dados organizados → Decisões melhores
- **Imersão**: Mundo consistente → Jogadores engajados

---

**Pronto para começar!** 🚀

