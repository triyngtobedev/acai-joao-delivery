# Açaí do João - Delivery de Açaí em Salvador/BA

Site de delivery de açaí desenvolvido em Flask com painel administrativo completo, carrinho com localStorage e integração com WhatsApp.

## Stack

- Python 3.12
- Flask
- Flask-SQLAlchemy
- python-dotenv
- Bootstrap 5.3 (mobile-first)
- Jinja2 templates
- SQLite

## Estrutura de Pastas

```
acai-joao-delivery/
├── app.py
├── models.py
├── requirements.txt
├── .env.example
├── README.md
├── instance/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── cart.js
└── templates/
    ├── base.html
    ├── public/
    │   └── index.html
    └── admin/
        ├── login.html
        └── dashboard.html
```

## Variáveis de Ambiente

Crie um arquivo `.env` baseado em `.env.example`:

```env
FLASK_SECRET_KEY=change-me
DATABASE_URL=sqlite:///acai_joao.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me
STORE_WHATSAPP=5571999999999
```

## Como Rodar

### Local

```bash
python -m venv .venv
pip install -r requirements.txt
flask --app app run --debug
```

Acesse: http://localhost:5000

### Remoto (Render / Railway / Hostinger / etc.)

1. Clone o repositório
2. Crie o ambiente virtual e instale dependências
3. Copie `.env.example` para `.env` e configure as variáveis
4. Rode `flask --app app run --debug` ou adapte para o servidor WSGI da plataforma
5. O banco SQLite é criado automaticamente na pasta `instance/`

### Credenciais Admin

- Usuário padrão: `admin`
- Senha padrão: `change-me`
- Configuráveis via variáveis de ambiente `ADMIN_USERNAME` e `ADMIN_PASSWORD`

## Funcionalidades

### Página Pública (`/`)
- Cardápio com categorias e produtos ativos
- Indicador de loja aberta/fechada
- Carrinho com `localStorage`
- Finalização de pedido via WhatsApp (`POST /pedido`)
- Modal com nome, endereço e observações

### Painel Administrativo (`/admin`)
- Login com credenciais configuráveis via `.env`
- Dashboard com configurações da loja (nome, WhatsApp, taxa de entrega, status)
- CRUD completo de produtos (criar, editar, excluir, ativar/desativar)
- Todas as rotas admin protegidas por sessão

### Carrinho
- Adicionar/remover itens
- Aumentar/diminuir quantidade
- Cálculo de subtotal + taxa de entrega
- Total formatado em reais
- Persistência via `localStorage`
- Envia pedido para WhatsApp via `POST /pedido`
- Limpa carrinho após finalizar

## Dependências

`requirements.txt` contém:
- Flask
- Flask-SQLAlchemy
- python-dotenv

## Banco de Dados

- SQLite via SQLAlchemy
- Banco criado automaticamente em `instance/acai_joao.db`
- Dados de exemplo inseridos automaticamente no primeiro acesso
- Configuração da loja criada automaticamente

## Licença

MIT
