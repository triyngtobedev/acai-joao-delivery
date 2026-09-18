import os
import json
import urllib.parse
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv
from models import db, Category, Product, StoreConfig, Order, OrderItem

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'change-me')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_dir, exist_ok=True)
db_url = os.getenv('DATABASE_URL')
if not db_url:
    db_url = 'sqlite:///' + os.path.join(instance_dir, 'acai_joao.db').replace(os.sep, '/')
app.config['SQLALCHEMY_DATABASE_URI'] = db_url

db.init_app(app)

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'change-me')
ORDER_STATUS_LABELS = {
    'received': 'Recebido',
    'preparing': 'Preparando',
    'out_for_delivery': 'Saiu para entrega',
    'done': 'Finalizado',
    'canceled': 'Cancelado',
}


def seed_data():
    if Category.query.count() == 0:
        cats = [
            Category(name='Acais', sort_order=1),
            Category(name='Complementos', sort_order=2),
            Category(name='Bebidas', sort_order=3),
        ]
        db.session.add_all(cats)
        db.session.flush()
        acai_cat = Category.query.filter_by(name='Acais').first()
        comp_cat = Category.query.filter_by(name='Complementos').first()
        beb_cat = Category.query.filter_by(name='Bebidas').first()
        products = [
            Product(name='Acaí 300ml', description='Açaí tradicional no copinho', price=12.90, category_id=acai_cat.id, image_url='/static/img/acai-300ml.jpg', is_active=True),
            Product(name='Acaí 500ml', description='Açaí médio, perfeito para matar a fome', price=18.90, category_id=acai_cat.id, image_url='/static/img/acai-500ml.jpg', is_active=True),
            Product(name='Acaí 700ml', description='Açaí grande, o mais pedido', price=24.90, category_id=acai_cat.id, image_url='/static/img/acai-700ml.jpg', is_active=True),
            Product(name='Granola', description='Granola crocante para incrementar seu açaí', price=5.00, category_id=comp_cat.id, image_url='/static/img/granola.jpg', is_active=True),
            Product(name='Leite em pó', description='Leite em pó para o açaí ficar mais cremoso', price=3.50, category_id=comp_cat.id, image_url='/static/img/leite-poezinho.jpg', is_active=True),
            Product(name='Banana', description='Banana natural para acompanhamento', price=2.00, category_id=comp_cat.id, image_url='/static/img/banana.jpg', is_active=True),
            Product(name='Água mineral', description='Água mineral gelada', price=3.00, category_id=beb_cat.id, image_url='/static/img/agua-mineral.jpg', is_active=True),
        ]
        db.session.add_all(products)
        store = StoreConfig(store_name='Açaí do João', whatsapp_number=os.getenv('STORE_WHATSAPP', '5571999999999'), delivery_fee=5.00, is_open=True)
        db.session.add(store)
        db.session.commit()


with app.app_context():
    db.create_all()
    seed_data()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def parse_order_items(raw_items):
    parsed_items = []
    for raw_item in raw_items:
        product_id = raw_item.get('product_id', raw_item.get('id'))
        product = None
        if product_id:
            try:
                product = db.session.get(Product, int(product_id))
            except (TypeError, ValueError):
                product = None

        quantity = raw_item.get('quantidade', raw_item.get('qty', 1))
        try:
            quantity = max(1, int(quantity))
        except (TypeError, ValueError):
            quantity = 1

        if product:
            product_name = product.name
            unit_price = float(product.price)
        else:
            product_name = raw_item.get('nome', raw_item.get('name', '')).strip()
            raw_subtotal = raw_item.get('subtotal', raw_item.get('preco', raw_item.get('price', 0)))
            try:
                raw_subtotal = float(raw_subtotal)
            except (TypeError, ValueError):
                raw_subtotal = 0.0
            unit_price = raw_subtotal / quantity if quantity else raw_subtotal

        if not product_name:
            continue

        subtotal = round(unit_price * quantity, 2)
        parsed_items.append({
            'product_id': product.id if product else None,
            'product_name': product_name,
            'quantity': quantity,
            'unit_price': round(unit_price, 2),
            'subtotal': subtotal,
        })

    return parsed_items


@app.route('/')
def index():
    store = StoreConfig.query.first()
    categories = Category.query.order_by(Category.sort_order.asc()).all()
    products = Product.query.filter_by(is_active=True).all()
    return render_template('public/index.html', store=store, categories=categories, products=products)


@app.route('/pedido', methods=['POST'])
def pedido():
    data = request.get_json() if request.is_json else request.form
    if request.is_json:
        nome = data.get('nome')
        endereco = data.get('endereco')
        observacoes = data.get('observacoes', '')
        itens = data.get('itens', [])
    else:
        nome = data.get('nome')
        endereco = data.get('endereco')
        observacoes = data.get('observacoes', '')
        itens = json.loads(data.get('itens', '[]'))

    nome = (nome or '').strip()
    endereco = (endereco or '').strip()
    observacoes = (observacoes or '').strip()

    if not nome or not endereco:
        return jsonify({'error': 'Nome e endereço são obrigatórios'}), 400
    if not itens:
        return jsonify({'error': 'Carrinho vazio'}), 400

    store = StoreConfig.query.first()
    if not store:
        return jsonify({'error': 'Configuração da loja não encontrada'}), 500
    if not store.is_open:
        return jsonify({'error': 'Loja está fechada no momento'}), 400

    delivery_fee = store.delivery_fee
    whatsapp_number = store.whatsapp_number
    parsed_items = parse_order_items(itens)
    if not parsed_items:
        return jsonify({'error': 'Nenhum item válido no carrinho'}), 400

    subtotal = round(sum(item['subtotal'] for item in parsed_items), 2)
    total = round(subtotal + delivery_fee, 2)

    order = Order(
        customer_name=nome,
        customer_address=endereco,
        notes=observacoes,
        status='received',
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total=total,
    )
    db.session.add(order)
    db.session.flush()

    for item in parsed_items:
        db.session.add(OrderItem(
            order_id=order.id,
            product_id=item['product_id'],
            product_name=item['product_name'],
            quantity=item['quantity'],
            unit_price=item['unit_price'],
            subtotal=item['subtotal'],
        ))

    mensagem = f'*📋 Novo Pedido #{order.id} - Açaí do João*\n\n'
    mensagem += f'*👤 Cliente:* {nome}\n'
    mensagem += f'*📍 Endereço:* {endereco}\n\n'
    mensagem += '*🛒 Itens:*\n'
    for item in parsed_items:
        mensagem += f"  • {item['product_name']} x{item['quantity']} - R$ {item['subtotal']:.2f}\n"
    mensagem += f'\n*💵 Taxa de entrega:* R$ {delivery_fee:.2f}\n'
    mensagem += f'*💰 Total: R$ {total:.2f}*\n'
    if observacoes:
        mensagem += f'\n*📝 Observações:* {observacoes}\n'

    params = urllib.parse.urlencode({'text': mensagem})
    wa_me_url = f'https://wa.me/{whatsapp_number}?{params}'
    order.whatsapp_url = wa_me_url
    db.session.commit()

    return jsonify({
        'success': True,
        'order_id': order.id,
        'wa_me_url': wa_me_url,
        'total': total,
        'message': 'Pedido gerado com sucesso!',
    })


@app.route('/admin/login')
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/login.html')


@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/login.html', error='Usuário ou senha inválidos')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/admin')
@login_required
def admin_dashboard():
    store = StoreConfig.query.first()
    categories = Category.query.order_by(Category.sort_order.asc()).all()
    products = Product.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).limit(20).all()
    open_orders = Order.query.filter(Order.status.in_(['received', 'preparing', 'out_for_delivery'])).count()
    revenue_total = db.session.query(db.func.coalesce(db.func.sum(Order.total), 0)).filter(Order.status != 'canceled').scalar()
    return render_template(
        'admin/dashboard.html',
        store=store,
        categories=categories,
        products=products,
        orders=orders,
        open_orders=open_orders,
        revenue_total=revenue_total,
        order_status_labels=ORDER_STATUS_LABELS,
    )


@app.route('/admin/orders/<int:id>/status', methods=['POST'])
@login_required
def update_order_status(id):
    order = db.get_or_404(Order, id)
    status = request.form.get('status') or (request.get_json(silent=True) or {}).get('status')
    if status not in ORDER_STATUS_LABELS:
        return jsonify({'error': 'Status inválido'}), 400
    order.status = status
    db.session.commit()
    return jsonify({'success': True, 'status': status, 'label': ORDER_STATUS_LABELS[status]})


@app.route('/admin/products/create', methods=['POST'])
@login_required
def create_product():
    category_id = request.form.get('category_id')
    name = request.form.get('name')
    description = request.form.get('description', '')
    price = request.form.get('price')
    image_url = request.form.get('image_url', '')
    is_active = request.form.get('is_active') == 'on'
    if not name or not price or not category_id:
        return jsonify({'error': 'Nome, preço e categoria são obrigatórios'}), 400
    try:
        price = float(price)
    except ValueError:
        return jsonify({'error': 'Preço inválido'}), 400
    product = Product(category_id=category_id, name=name, description=description, price=price, image_url=image_url, is_active=is_active)
    db.session.add(product)
    db.session.commit()
    return jsonify({'success': True, 'product': {'id': product.id, 'name': product.name}})


@app.route('/admin/products/<int:id>/update', methods=['POST'])
@login_required
def update_product(id):
    product = db.get_or_404(Product, id)
    product.category_id = request.form.get('category_id', product.category_id)
    product.name = request.form.get('name', product.name)
    product.description = request.form.get('description', product.description)
    try:
        product.price = float(request.form.get('price', product.price))
    except ValueError:
        return jsonify({'error': 'Preço inválido'}), 400
    product.image_url = request.form.get('image_url', product.image_url)
    product.is_active = request.form.get('is_active') == 'on'
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/products/<int:id>/delete', methods=['POST'])
@login_required
def delete_product(id):
    product = db.get_or_404(Product, id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/products/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_product(id):
    product = db.get_or_404(Product, id)
    product.is_active = not product.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': product.is_active})


if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true', host='0.0.0.0', port=5000)
