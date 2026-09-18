# Açaí do João - Delivery de Açaí em Salvador/BA

Site de delivery de açaí desenvolvido em Flask com painel administrativo completo, carrinho com localStorage e integração com WhatsApp.

## Stack

- Python 3.12
- Flask
- Flask-SQLAlchemy
- python-dotenv
- gunicorn
- Bootstrap 5.3 (mobile-first)
- Jinja2 templates
- SQLite (dev) / PostgreSQL (produção, via `DATABASE_URL`)
- psycopg2-binary (driver PostgreSQL)

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
APP_ENV=development
FLASK_SECRET_KEY=gere-uma-chave-grande-e-aleatoria
DATABASE_URL=
ADMIN_USERNAME=joao_admin
ADMIN_PASSWORD=troque-por-uma-senha-forte
STORE_WHATSAPP=5571999999999
```

Em produção, defina `APP_ENV=production`. O app não inicia se `FLASK_SECRET_KEY`, `ADMIN_USERNAME` ou `ADMIN_PASSWORD` ainda estiverem com valores fracos/padrão.

Para gerar uma chave segura:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

## Como Rodar

### Local

```bash
python -m venv .venv
pip install -r requirements.txt
flask --app app run --debug
```

Acesse: http://localhost:5000

### Deploy no Render (PostgreSQL)

O repositório inclui um `render.yaml` (Blueprint) que cria automaticamente o **Web Service** e o banco **PostgreSQL** já conectados.

1. No Render, vá em **New > Blueprint** e aponte para este repositório
2. O `render.yaml` já configura: build (`pip install -r requirements.txt`), start (`gunicorn app:app`), health check (`/healthz`), `APP_ENV=production`, `FLASK_SECRET_KEY` gerada automaticamente e `DATABASE_URL` vinculada ao banco PostgreSQL
3. Preencha manualmente as variáveis marcadas como `sync: false` (o Render pedirá na tela):
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
   - `STORE_WHATSAPP`
4. Deploy. As tabelas e os dados iniciais são criados automaticamente no primeiro boot.

O app aceita `DATABASE_URL` nos formatos `postgres://` e `postgresql://` (normalização automática para SQLAlchemy).

### Outras plataformas (Railway / Hostinger / etc.)

1. Clone o repositório
2. Configure as variáveis de ambiente na plataforma
3. Use o comando de instalação: `pip install -r requirements.txt`
4. Use o comando de start: `gunicorn app:app`
5. Configure `APP_ENV=production`
6. Configure `FLASK_SECRET_KEY`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` e `STORE_WHATSAPP`
7. Configure `DATABASE_URL` (ex.: `postgresql://user:senha@host:5432/db`) se a plataforma oferecer banco persistente

O repositório inclui um `Procfile` com:

```Procfile
web: gunicorn app:app
```

### Checklist de Produção

- `APP_ENV=production`
- `FLASK_SECRET_KEY` forte e única
- `ADMIN_USERNAME` diferente de `admin`
- `ADMIN_PASSWORD` forte, diferente de `change-me`
- `STORE_WHATSAPP` com o número real da loja
- Banco persistente configurado (PostgreSQL via `DATABASE_URL`) ou volume persistente para SQLite
- `/healthz` retornando `{"status":"ok"}`

### Credenciais Admin

- Nunca use `admin/change-me` em produção.
- Configure via variáveis de ambiente `ADMIN_USERNAME` e `ADMIN_PASSWORD`.

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
- gunicorn
- python-dotenv
- psycopg2-binary

## Banco de Dados

- SQLite via SQLAlchemy em desenvolvimento; PostgreSQL em produção via `DATABASE_URL`
- Banco SQLite criado automaticamente em `instance/acai_joao.db`
- Dados de exemplo inseridos automaticamente no primeiro acesso
- Configuração da loja criada automaticamente

## Licença

MIT
