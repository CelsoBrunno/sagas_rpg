# Guia de Instalação - Sistema de Campanha GURPS

## Pré-requisitos

- Python 3.8 ou superior
- MySQL 5.7 ou superior (ou MariaDB 10.3+)
- pip (gerenciador de pacotes Python)

## Passo 1: Instalar Dependências Python

```bash
pip install -r requirements.txt
```

## Passo 2: Configurar o MySQL

1. Inicie o servidor MySQL:
```bash
# Windows
net start MySQL80

# Linux/Mac
sudo systemctl start mysql
```

2. Execute o script de criação do banco de dados:
```bash
mysql -u root -p < database/schema.sql
```

## Passo 3: Configurar Variáveis de Ambiente

Copie o arquivo de exemplo e configure:
```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:
```
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=sua_senha_aqui
MYSQL_DB=sagas_gurps
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=False
```

## Passo 4: Executar o Sistema

```bash
python app.py
```

O sistema estará disponível em: http://localhost:5000

## Testando o Sistema

1. Acesse http://localhost:5000
2. Clique em "Novo Personagem"
3. Preencha os dados do personagem
4. Explore as funcionalidades:
   - Adicionar vantagens e desvantagens
   - Adicionar perícias
   - Rolar dados clicando nos botões
   - Editar atributos em tempo real

## Estrutura do Projeto

```
sagas/
├── app.py                 # Aplicação Flask principal
├── database.py            # Configuração do banco de dados
├── models.py              # Modelos de dados
├── config.py              # Configurações
├── requirements.txt       # Dependências
├── .env                   # Variáveis de ambiente (criar)
├── database/
│   └── schema.sql        # Esquema do banco de dados
├── static/
│   ├── css/
│   │   └── style.css     # Estilos FIAP
│   └── js/
│       └── main.js       # Lógica GURPS
└── templates/
    ├── base.html
    ├── index.html
    ├── novo_personagem.html
    └── personagem.html
```

## Resolução de Problemas

### Erro de conexão com MySQL
- Verifique se o MySQL está rodando
- Confirme as credenciais no arquivo `.env`
- Certifique-se de que o banco `sagas_gurps` foi criado

### Erro ao importar bibliotecas
- Execute: `pip install -r requirements.txt`
- Verifique se está usando Python 3.8+

### Erro ao executar app.py
- Certifique-se de que o arquivo `.env` está na raiz do projeto
- Verifique se todas as dependências estão instaladas

## Próximos Passos

- Configure um servidor de produção (Nginx + Gunicorn)
- Adicione autenticação de usuários
- Implemente o módulo de NPCs
- Implemente o módulo de Locais
- Implemente o módulo de Mapas

## Suporte

Para dúvidas ou problemas, consulte o arquivo README.md

