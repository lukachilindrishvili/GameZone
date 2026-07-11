from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from ext import db, login_manager

# likes association table
likes = db.Table('likes',
    db.Column('user_id',    db.Integer, db.ForeignKey('user.id'),    primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'), primary_key=True),
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin      = db.Column(db.Boolean, default=False)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)

    liked      = db.relationship('Product', secondary=likes,
                                 backref=db.backref('likers', lazy='dynamic'),
                                 lazy='dynamic')
    cart_items = db.relationship('CartItem', backref='user', lazy=True,
                                 cascade='all, delete-orphan')
    orders     = db.relationship('Order', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_liked(self, product):
        return self.liked.filter_by(id=product.id).first() is not None

    def __repr__(self):
        return f'<User {self.username}>'


class Product(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text,        nullable=False)
    price       = db.Column(db.Float,       nullable=False)
    category    = db.Column(db.String(50),  nullable=False)
    platform    = db.Column(db.String(50),  nullable=True)
    stock       = db.Column(db.Integer,     default=0)
    image_url   = db.Column(db.String(400), nullable=True)
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)

    @property
    def like_count(self):
        return self.likers.count()

    def __repr__(self):
        return f'<Product {self.name}>'


class CartItem(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),    nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity   = db.Column(db.Integer, default=1, nullable=False)
    product    = db.relationship('Product')


class Order(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status     = db.Column(db.String(20), default='pending')
    items      = db.relationship('OrderItem', backref='order', lazy=True,
                                 cascade='all, delete-orphan')

    @property
    def total(self):
        return sum(i.quantity * i.price_at_purchase for i in self.items)


class OrderItem(db.Model):
    id                = db.Column(db.Integer, primary_key=True)
    order_id          = db.Column(db.Integer, db.ForeignKey('order.id'),   nullable=False)
    product_id        = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity          = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float,   nullable=False)
    product           = db.relationship('Product')
