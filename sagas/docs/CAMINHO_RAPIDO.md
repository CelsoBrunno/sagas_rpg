# 🎲 Sistema de Campanha GURPS - Guia Rápido

## ⚡ Início Rápido

### 1. Instalação

```bash
# Instalar dependências
pip install -r requirements.txt

# Criar banco de dados
mysql -u root -p < database/schema.sql

# Copiar configuração
cp env_example.txt .env
# Editar .env com suas credenciais
```

### 2. Executar

```bash
python app.py
# ou
python run.py
```

### 3. Acessar

Abra no navegador: http://localhost:5000

## 📋 Comandos Úteis

### Popular dados de exemplo
```bash
python populate_example_data.py
```

### Criar banco do zero
```bash
mysql -u root -p
# Depois, dentro do MySQL:
source database/schema.sql
exit
```

### Verificar saúde do sistema
```bash
curl http://localhost:5000/health
```

## 🎯 Funcionalidades Principais

### Fichas de Personagem GURPS
- ✅ Atributos básicos (ST, DX, IQ, HT)
- ✅ Atributos derivados (PV, PF, Esquiva, etc)
- ✅ Vantagens e Desvantagens
- ✅ Perícias com cálculo automático de NH
- ✅ Sistema de abas organizado

### Sistema de Rolagens
- ✅ Botões clicáveis para rolar dados
- ✅ Rolagens de atributos (ST, DX, IQ, HT)
- ✅ Rolagens de perícias (com NH calculado)
- ✅ Exibição de resultados (sucesso/falha/crítico)
- ✅ Histórico de rolagens

### Design Moderno
- ✅ Paleta de cores inspirada na FIAP
- ✅ Interface responsiva
- ✅ Animações suaves
- ✅ Cards e botões modernos

## 📁 Estrutura

```
sagas/
├── app.py                    # Aplicação Flask
├── models.py                 # Modelos de dados
├── database.py              # Conexão MySQL
├── config.py                # Configurações
├── requirements.txt          # Dependências
├── run.py                   # Script de execução
├── populate_example_data.py # Dados de exemplo
├── database/
│   └── schema.sql          # Esquema MySQL
├── static/
│   ├── css/style.css       # Estilos FIAP
│   └── js/main.js          # Lógica GURPS
└── templates/
    ├── base.html
    ├── index.html
    ├── novo_personagem.html
    └── personagem.html
```

## 🔧 Configuração

### Variáveis de Ambiente (.env)

```env
SECRET_KEY=sua-chave-secreta
DEBUG=False
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha_aqui
MYSQL_DB=sagas_gurps
```

## 🎮 Como Usar

1. **Criar um Personagem**
   - Clique em "Novo Personagem"
   - Preencha nome, atributos e dados
   - Sistema calcula pontos automaticamente

2. **Adicionar Vantagens**
   - Vá para aba "Vantagens & Desvantagens"
   - Preencha nome e custo em pontos
   - Clique em "Adicionar"

3. **Adicionar Perícias**
   - Vá para aba "Perícias"
   - Escolha atributo base e dificuldade
   - Sistema calcula NH automaticamente

4. **Rolar Dados**
   - Clique em "Rolar" ao lado de qualquer atributo/perícia
   - Resultado aparece na área de rolagens
   - Sistema indica sucesso/falha/crítico

## 📖 Documentação Completa

- **README.md** - Visão geral do projeto
- **INSTALL.md** - Guia de instalação detalhado
- **CAMINHO_RAPIDO.md** - Este arquivo

## 💡 Dicas

- Use `python populate_example_data.py` para criar personagens de exemplo
- Aperte F12 no navegador para ver logs de JavaScript
- Todos os campos calculam em tempo real
- O sistema é responsivo - funciona em mobile

## 🐛 Problemas Comuns

**Erro: Cannot connect to MySQL**
```bash
# Verifique se MySQL está rodando
mysql -u root -p

# Verifique credenciais no .env
cat .env
```

**Erro: Module not found**
```bash
pip install -r requirements.txt
```

**Personagens não aparecem**
```bash
# Verifique se o banco foi criado
mysql -u root -p sagas_gurps

# Veja se há dados
SELECT * FROM personagens;
```

## 🚀 Próximos Passos

- [ ] Adicionar autenticação de usuários
- [ ] Implementar módulo de NPCs
- [ ] Implementar módulo de Locais
- [ ] Implementar módulo de Mapas
- [ ] Adicionar exportação de ficha (PDF)
- [ ] Adicionar sistema de anotações

## 📧 Suporte

Para dúvidas, consulte a documentação completa ou abra uma issue.

---

**Desenvolvido com Flask, MySQL e design inspirado na FIAP** 🎓

