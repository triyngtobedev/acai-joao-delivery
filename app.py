import os
import json
import urllib.parse
from functools import wraps
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from dotenv import load_dotenv
from models import db, Category, Product, StoreConfig

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'change-me')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
os.makedirs(instance_dir, exist_ok=True)

db_url = os.getenv('DATABASE_URL')
if db_url and db_url.startswith('sqlite:///') and not db_url.startswith('sqlite:////'):
    relative_path = db_url[10:]
    abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    db_url = 'sqlite:///' + abs_path.replace(os.sep, '/')
elif not db_url:
    db_url = 'sqlite:///' + os.path.join(instance_dir, 'acai_joao.db').replace(os.sep, '/')

app.config['SQLALCHEMY_DATABASE_URI'] = db_url

db.init_app(app)

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'change-me')


def seed_data():
    if Category.query.count() == 0:
        cats = [
            Category(name='Açaís', sort_order=1),
            Category(name='Complementos', sort_order=2),
            Category(name='Bebidas', sort_order=3),
        ]
        db.session.add_all(cats)
        db.session.flush()
        acai_cat = Category.query.filter_by(name='Açaís').first()
        comp_cat = Category.query.filter_by(name='Complementos').first()
        beb_cat = Category.query.filter_by(name='Bebidas').first()
        products = [
            Product(name='Açaí 300ml', description='Açaí tradicional no copinho', price=12.90, category_id=acai_cat.id, image_url='/static/img/acai-300ml.jpg', is_active=True),
            Product(name='Açaí 500ml', description='Açaí médio, perfeito para matar a fome', price=18.90, category_id=acai_cat.id, image_url='/static/img/acai-500ml.jpg', is_active=True),
            Product(name='Açaí 700ml', description='Açaí grande, o mais pedido', price=24.90, category_id=acai_cat.id, image_url='/static/img/acai-700ml.jpg', is_active=True),
            Product(name='Granola', description='Granola crocante para incrementar seu açaí', price=5.00, category_id=comp_cat.id, image_url='/static/img/granola.jpg', is_active=True),
            Product(name='Leite em pó', description='Leite em pó para o açaí ficar mais cremoso', price=3.50, category_id=comp_cat.id, image_url='/static/img/leite-poezinho.jpg', is_active=True),
            Product(name='Banana', description='Banana natural para acompanhamento', price=2.00, category_id=comp_cat.id, image_url='/static/img/banana.jpg', is_active=True),
            Product(name='Água mineral', description='Água mineral gelada', price=3.00, category_id=beb_cat.id, image_url='/static/img/agua-mineral.jpg', is_active=True),
        ]
        db.session.add_all(products)
        store = StoreConfig(
            store_name='Açaí do João',
            whatsapp_number=os.getenv('STORE_WHATSAPP', '5571999999999'),
            delivery_fee=5.00,
            is_open=True
        )
        db.session.add(store)
        db.session.commit()


with app.app_context():
    db.create_all()
    seed_data()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login_page'))
        return f(*args, **kwargs)
    return decorated_function


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
        itens = eval(data.get('itens', '[]'))

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

    mensagem = f"*📋 Novo Pedido - {store.store_name}*\n\n"
    mensagem += f"👤 *Cliente:* {nome}\n"
    mensagem += f"📍 *Endereço:* {endereco}\n\n"
    mensagem += f"*🛒 Itens:*\n"
    for item in itens:
        nome_item = item.get('nome', item.get('name', ''))
        qtd = item.get('quantidade', item.get('qty', 1))
        subtotal = item.get('subtotal', item.get('preco', 0))
        mensagem += f"  • {nome_item} x{qtd} - R$ {subtotal:.2f}\n"
    mensagem += f"\n*💵 Taxa de entrega:* R$ {delivery_fee:.2f}\n"
    total = sum(item.get('subtotal', item.get('preco', 0)) for item in itens) + delivery_fee
    mensagem += f"*💰 Total: R$ {total:.2f}*\n"
    if observacoes:
        mensagem += f"\n*📝 Observações:* {observacoes}\n"

    params = urllib.parse.urlencode({'text': mensagem})
    wa_me_url = f"https://wa.me/{whatsapp_number}?{params}"

    return jsonify({'success': True, 'wa_me_url': wa_me_url, 'total': total})


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login_page():
    if request.method == 'POST':
        if session.get('admin_logged_in'):
            return redirect(url_for('admin_dashboard'))
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Usuário ou senha inválidos', 'error')
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login_page'))


@app.route('/admin')
@login_required
def admin_dashboard():
    store = StoreConfig.query.first()
    categories = Category.query.order_by(Category.sort_order.asc()).all()
    products = Product.query.all()
    return render_template('admin/dashboard.html', store=store, categories=categories, products=products)


@app.route('/admin/products/create', methods=['POST'])
@login_required
def create_product():
    data = request.get_json() if request.is_json else request.form
    category_id = data.get('category_id')
    name = data.get('name')
    description = data.get('description', '')
    price = data.get('price')
    image_url = data.get('image_url', '')
    is_active = str(data.get('is_active', 'true')) == 'true'

    if not name or not price or not category_id:
        return jsonify({'error': 'Nome, preço e categoria são obrigatórios'}), 400
    try:
        price = float(price)
    except ValueError:
        return jsonify({'error': 'Preço inválido'}), 400

    product = Product(
        category_id=category_id, name=name, description=description,
        price=price, image_url=image_url, is_active=is_active
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'success': True, 'product': {'id': product.id, 'name': product.name}})


@app.route('/admin/products/<int:id>/update', methods=['POST'])
@login_required
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.get_json() if request.is_json else request.form
    product.category_id = data.get('category_id', product.category_id)
    product.name = data.get('name', product.name)
    product.description = data.get('description', product.description)
    try:
        product.price = float(data.get('price', product.price))
    except ValueError:
        return jsonify({'error': 'Preço inválido'}), 400
    product.image_url = data.get('image_url', product.image_url)
    product.is_active = str(data.get('is_active', str(product.is_active))) == 'true'
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/products/<int:id>/delete', methods=['POST'])
@login_required
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/admin/products/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_product(id):
    product = Product.query.get_or_404(id)
    product.is_active = not product.is_active
    db.session.commit()
    return jsonify({'success': True, 'is_active': product.is_active})


@app.route('/admin/store', methods=['POST'])
@login_required
def update_store():
    store = StoreConfig.query.first()
    if not store:
        return jsonify({'error': 'Loja não encontrada'}), 404
    data = request.get_json() if request.is_json else request.form
    store.is_open = data.get('is_open', str(store.is_open)) == 'true'
    store.delivery_fee = float(data.get('delivery_fee', store.delivery_fee))
    store.whatsapp_number = data.get('whatsapp_number', store.whatsapp_number)
    store.store_name = data.get('store_name', store.store_name)
    db.session.commit()
    return jsonify({'success': True, 'store': {'is_open': store.is_open, 'delivery_fee': store.delivery_fee, 'whatsapp_number': store.whatsapp_number}})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
