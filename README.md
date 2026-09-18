# Açaí do João - Delivery em Salvador/BA

![Açaí do João](https://img.shields.io/badge/🍃-Açaí%20do%20João-purple)

Delivery de açaí com pedido via WhatsApp, painel admin completo, carrinho com localStorage e integração com WhatsApp.

## Stack

- **Python 3.10+**
- **Flask** - Framework web
- **Flask-SQLAlchemy** - ORM
- **Bootstrap 5.3** - Frontend CSS
- **SQLite** - Banco de dados (criado automaticamente)
- **Jinja2** - Templates

## Estrutura de Pastas

```
acai-joao-delivery/
├── app.py                  # Aplicação Flask principal
├── models.py               # Modelos SQLAlchemy (Category, Product, StoreConfig)
├── requirements.txt        # Dependências Python
├── .env                    # Variáveis de ambiente
├── .env.example            # Template de variáveis de ambiente
├── .gitignore
├── README.md
├── static/
│   ├── css/
│   │   └── style.css       # Estilos customizados (tema escuro, mobile-first)
│   ├── js/
│   │   ├── cart.js         # Lógica do carrinho (localStorage)
│   │   └── admin.js        # Lógica do painel admin
│   └── img/                  # Imagens dos produtos
├── templates/
│   ├── base.html           # Template base com Bootstrap 5.3
│   ├── public/
│   │   └── index.html      # Página pública do cardápio
│   └── admin/
│       ├── login.html      # Tela de login admin
│       └── dashboard.html  # Dashboard de gestão de produtos
└── instance/
    └── acai_joao.db        # Banco SQLite (criado automaticamente)
```

## Variáveis de Ambiente

Crie um arquivo `.env` na raiz com:

```env
FLASK_SECRET_KEY=uma-chave-secreta-qualquer
DATABASE_URL=sqlite:///instance/acai_joao.db
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change-me
STORE_WHATSAPP=5571999999999
```

- `ADMIN_USERNAME` - Usuário para login no painel admin
- `ADMIN_PASSWORD` - Senha para login no painel admin
- `STORE_WHATSAPP` - Número de WhatsApp no formato internacional (ex: 5571999999999)
- `FLASK_SECRET_KEY` - Chave para sessões Flask
- `DATABASE_URL` - URL do banco de dados SQLite

## Como Rodar

```bash
python -m venv .venv
pip install -r requirements.txt
flask --app app run --debug
```

Acesse: http://localhost:5000

Painel Admin: http://localhost:5000/admin/login
- Usuário padrão: `admin`
- Senha padrão: `change-me`

## Funcionalidades

### Público
- Cardápio mobile-first com categorias
- Carrinho com localStorage (adicionar, aumentar, diminuir, remover)
- Formatação de preços em reais
- Status da loja (aberto/fechado)
- Finalização de pedido com link WhatsApp (`wa.me`)
- Bloqueio de finalização quando loja está fechada

### Admin
- Autenticação por sessão
- Dashboard com lista de produtos
- CRUD completo de produtos (criar, editar, excluir, ativar/desativar)
- Configuração da loja (nome, WhatsApp, taxa de entrega, status)

## Rotas Principais

| Rota | Método | Descrição |
|------|--------|-----------|
| `/` | GET | Página pública do cardápio |
| `/pedido` | POST | Envia pedido e retorna URL WhatsApp |
| `/admin/login` | GET/POST | Login do painel admin |
| `/admin/logout` | GET | Encerra sessão admin |
| `/admin` | GET | Dashboard protegido |
| `/admin/products/create` | POST | Criar produto |
| `/admin/products/<id>/update` | POST | Atualizar produto |
| `/admin/products/<id>/delete` | POST | Excluir produto |
| `/admin/products/<id>/toggle` | POST | Ativar/desativar produto |
| `/admin/store` | POST | Atualizar configurações da loja |

## Limitações Conhecidas

- Upload de imagens não implementado (usa URL)
- Sem validação avançada de CPF/endereço
- Sem sistema de pagamentos

## Créditos

Desenvolvido com ❤️ para o delivery de açaí.
