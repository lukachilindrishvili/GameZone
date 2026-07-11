from functools import wraps
from flask import (Blueprint, render_template, redirect, url_for,
                   flash, request, jsonify, abort)
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from ext import db, mail
from models import User, Product, CartItem, Order, OrderItem
from forms import (LoginForm, RegisterForm, ProductForm,
                   ChangePasswordForm, ChangeEmailForm)

main = Blueprint('main', __name__)


# ── Helpers ───────────────────────────────────────────────────────────────────

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def send_email(to, subject, template, **kwargs):
    """Send an HTML email — silently fails if mail not configured."""
    try:
        msg = Message(subject, recipients=[to])
        msg.html = render_template(template, **kwargs)
        mail.send(msg)
    except Exception as e:
        print(f'[Mail] Could not send email: {e}')


@main.app_context_processor
def inject_cart_count():
    if current_user.is_authenticated:
        count = CartItem.query.filter_by(user_id=current_user.id).count()
    else:
        count = 0
    return {'cart_count': count}


# ── Home ──────────────────────────────────────────────────────────────────────

@main.route('/')
def index():
    featured   = Product.query.filter(Product.stock > 0).order_by(
                     Product.created_at.desc()).limit(8).all()
    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]
    return render_template('index.html', featured=featured,
                           categories=categories, total=Product.query.count())


# ── Store ─────────────────────────────────────────────────────────────────────

@main.route('/store')
def store():
    cat      = request.args.get('category', '')
    platform = request.args.get('platform', '')
    search   = request.args.get('search', '').strip()
    sort     = request.args.get('sort', 'newest')

    q = Product.query
    if cat:      q = q.filter_by(category=cat)
    if platform: q = q.filter_by(platform=platform)
    if search:   q = q.filter(Product.name.ilike(f'%{search}%'))
    if   sort == 'price_asc':  q = q.order_by(Product.price.asc())
    elif sort == 'price_desc': q = q.order_by(Product.price.desc())
    else:                      q = q.order_by(Product.created_at.desc())

    products   = q.all()
    categories = [c[0] for c in db.session.query(Product.category).distinct().all()]
    platforms  = [p[0] for p in db.session.query(Product.platform)
                  .filter(Product.platform.isnot(None)).distinct().all()]
    return render_template('store.html', products=products,
                           categories=categories, platforms=platforms,
                           cat=cat, platform=platform, search=search, sort=sort)


# ── Product detail ────────────────────────────────────────────────────────────

@main.route('/product/<int:pid>')
def product(pid):
    p       = Product.query.get_or_404(pid)
    related = Product.query.filter(Product.category == p.category,
                                   Product.id != p.id, Product.stock > 0).limit(4).all()
    liked   = current_user.is_authenticated and current_user.has_liked(p)
    return render_template('product.html', p=p, related=related, liked=liked)


# ── Like toggle (AJAX) ────────────────────────────────────────────────────────

@main.route('/product/<int:pid>/like', methods=['POST'])
@login_required
def toggle_like(pid):
    p = Product.query.get_or_404(pid)
    if current_user.has_liked(p):
        current_user.liked.remove(p)
        liked = False
    else:
        current_user.liked.append(p)
        liked = True
    db.session.commit()
    return jsonify({'liked': liked, 'count': p.like_count})


# ── Liked ─────────────────────────────────────────────────────────────────────

@main.route('/liked')
@login_required
def liked():
    products = current_user.liked.all()
    return render_template('liked.html', products=products)


# ── Cart ──────────────────────────────────────────────────────────────────────

@main.route('/cart')
@login_required
def cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(i.quantity * i.product.price for i in items)
    return render_template('cart.html', items=items, total=total)


@main.route('/cart/add/<int:pid>', methods=['POST'])
@login_required
def cart_add(pid):
    p   = Product.query.get_or_404(pid)
    qty = max(1, int(request.form.get('quantity', 1)))
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=pid).first()
    if item:
        item.quantity = min(item.quantity + qty, p.stock)
    else:
        db.session.add(CartItem(user_id=current_user.id, product_id=pid, quantity=qty))
    db.session.commit()
    flash(f'✅ {p.name} კალათში დაემატა!', 'success')
    return redirect(request.referrer or url_for('main.cart'))


@main.route('/cart/update/<int:pid>', methods=['POST'])
@login_required
def cart_update(pid):
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=pid).first_or_404()
    qty  = int(request.form.get('quantity', 1))
    if qty <= 0:
        db.session.delete(item)
    else:
        item.quantity = min(qty, item.product.stock)
    db.session.commit()
    return redirect(url_for('main.cart'))


@main.route('/cart/remove/<int:pid>', methods=['POST'])
@login_required
def cart_remove(pid):
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=pid).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('main.cart'))


@main.route('/cart/checkout', methods=['POST'])
@login_required
def checkout():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not items:
        flash('კალათი ცარიელია.', 'warning')
        return redirect(url_for('main.cart'))

    order = Order(user_id=current_user.id)
    db.session.add(order)
    db.session.flush()

    for item in items:
        db.session.add(OrderItem(
            order_id=order.id, product_id=item.product_id,
            quantity=item.quantity, price_at_purchase=item.product.price
        ))
        item.product.stock = max(0, item.product.stock - item.quantity)
        db.session.delete(item)

    db.session.commit()
    flash(f'🎉 შეკვეთა #{order.id} წარმატებით განხორციელდა!', 'success')
    return redirect(url_for('main.profile'))


# ── Profile ───────────────────────────────────────────────────────────────────

@main.route('/profile')
@login_required
def profile():
    pw_form    = ChangePasswordForm(prefix='pw')
    email_form = ChangeEmailForm(prefix='em')
    orders     = Order.query.filter_by(user_id=current_user.id)\
                            .order_by(Order.created_at.desc()).all()
    liked      = current_user.liked.all()
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', pw_form=pw_form, email_form=email_form,
                           orders=orders, liked=liked, cart_items=cart_items)


@main.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    form = ChangePasswordForm(prefix='pw')
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('მიმდინარე პაროლი არასწორია.', 'danger')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            # send notification email
            send_email(
                current_user.email,
                '🔐 GameZone — პაროლი შეიცვალა',
                'email/password_changed.html',
                username=current_user.username
            )
            flash('✅ პაროლი წარმატებით შეიცვალა! შეტყობინება გაიგზავნა ელ-ფოსტაზე.', 'success')
    else:
        for field_errors in form.errors.values():
            for err in field_errors:
                flash(err, 'danger')
    return redirect(url_for('main.profile') + '#settings')


@main.route('/profile/change-email', methods=['POST'])
@login_required
def change_email():
    form = ChangeEmailForm(prefix='em')
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('პაროლი არასწორია.', 'danger')
        else:
            old_email = current_user.email
            current_user.email = form.new_email.data
            db.session.commit()
            # notify old address
            send_email(
                old_email,
                '📧 GameZone — ელ-ფოსტა შეიცვალა',
                'email/email_changed.html',
                username=current_user.username,
                new_email=form.new_email.data
            )
            flash('✅ ელ-ფოსტა წარმატებით შეიცვალა!', 'success')
    else:
        for field_errors in form.errors.values():
            for err in field_errors:
                flash(err, 'danger')
    return redirect(url_for('main.profile') + '#settings')


# ── Auth ──────────────────────────────────────────────────────────────────────

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash(f'🎮 კეთილი იყოს თქვენი დაბრუნება, {user.username}!', 'success')
            return redirect(url_for('main.index'))
        flash('ელ-ფოსტა ან პაროლი არასწორია.', 'danger')
    return render_template('auth/login.html', form=form)


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # send welcome email
        send_email(
            user.email,
            '🎮 კეთილი იყოს თქვენი მობრძანება — GameZone!',
            'email/welcome.html',
            username=user.username
        )
        flash('🎮 რეგისტრაცია წარმატებით დასრულდა! შეამოწმეთ ელ-ფოსტა.', 'success')
        return redirect(url_for('main.login'))
    return render_template('auth/register.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('წარმატებით გამოხვედით.', 'info')
    return redirect(url_for('main.index'))


# ── Admin ─────────────────────────────────────────────────────────────────────

@main.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    stats = {
        'products': Product.query.count(),
        'users':    User.query.count(),
        'orders':   Order.query.count(),
        'stock0':   Product.query.filter_by(stock=0).count(),
        'low':      Product.query.filter(Product.stock < 5, Product.stock > 0).all(),
    }
    recent = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template('admin/dashboard.html', stats=stats, recent=recent)


@main.route('/admin/products')
@login_required
@admin_required
def admin_products():
    products = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('admin/products.html', products=products)


@main.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_add():
    form = ProductForm()
    if form.validate_on_submit():
        db.session.add(Product(
            name=form.name.data, description=form.description.data,
            price=form.price.data, category=form.category.data,
            platform=form.platform.data or None,
            stock=form.stock.data, image_url=form.image_url.data or None
        ))
        db.session.commit()
        flash('✅ პროდუქტი დაემატა!', 'success')
        return redirect(url_for('main.admin_products'))
    return render_template('admin/product_form.html', form=form, title='დამატება', product=None)


@main.route('/admin/products/<int:pid>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_edit(pid):
    p    = Product.query.get_or_404(pid)
    form = ProductForm(obj=p)
    if form.validate_on_submit():
        p.name = form.name.data; p.description = form.description.data
        p.price = form.price.data; p.category = form.category.data
        p.platform = form.platform.data or None
        p.stock = form.stock.data; p.image_url = form.image_url.data or None
        db.session.commit()
        flash('✅ პროდუქტი განახლდა!', 'success')
        return redirect(url_for('main.admin_products'))
    return render_template('admin/product_form.html', form=form, title='რედაქტირება', product=p)


@main.route('/admin/products/<int:pid>/delete', methods=['POST'])
@login_required
@admin_required
def admin_delete(pid):
    p = Product.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    flash('პროდუქტი წაიშალა.', 'info')
    return redirect(url_for('main.admin_products'))


@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403
