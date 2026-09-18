from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    products = db.relationship('Product', backref='category', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Product {self.name}>'


class Order(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(200), nullable=False)
    customer_address = db.Column(db.String(500), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(30), default='received', nullable=False)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    delivery_fee = db.Column(db.Float, nullable=False, default=0.0)
    total = db.Column(db.Float, nullable=False, default=0.0)
    whatsapp_url = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Order #{self.id} {self.customer_name}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(200), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False, default=0.0)
    subtotal = db.Column(db.Float, nullable=False, default=0.0)
    product = db.relationship('Product')

    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'


class StoreConfig(db.Model):
    __tablename__ = 'store_config'
    id = db.Column(db.Integer, primary_key=True)
    store_name = db.Column(db.String(200), nullable=False)
    whatsapp_number = db.Column(db.String(20), nullable=False)
    delivery_fee = db.Column(db.Float, default=5.0)
    is_open = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<StoreConfig {self.store_name}>'
