import os
from flask import Flask
from dotenv import load_dotenv
from ext import db, login_manager, mail
from flask_wtf.csrf import CSRFProtect

load_dotenv()   # reads .env file if present


def create_app():
    app = Flask(__name__)

    # ── Core ──────────────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gamezone-secret-2026')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gamezone.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Mail (Gmail SMTP) ──────────────────────────────────────────────────────
    # To enable email: copy .env.example → .env and fill in your Gmail + App Password
    app.config['MAIL_SERVER']   = 'smtp.gmail.com'
    app.config['MAIL_PORT']     = 587
    app.config['MAIL_USE_TLS']  = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
    app.config['MAIL_DEFAULT_SENDER'] = (
        'GameZone', os.environ.get('MAIL_USERNAME', 'noreply@gamezone.ge')
    )

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    CSRFProtect(app)

    # ── Blueprints ────────────────────────────────────────────────────────────
    from routes import main
    app.register_blueprint(main)

    return app


def seed():
    from models import User, Product

    # Admin
    if not User.query.filter_by(email='admin@gamezone.ge').first():
        u = User(username='admin', email='admin@gamezone.ge', is_admin=True)
        u.set_password('admin123')
        db.session.add(u)
        print('✅  Admin → admin@gamezone.ge / admin123')

    products = [
        # ── Consoles ──────────────────────────────────────────────────────────
        dict(name='PlayStation 5', category='console', platform='PS5',
             price=1899, stock=12,
             description='Sony-ს მე-5 თაობის კონსოლი. Custom 825GB SSD, 4K/120fps, '
                         'DualSense Haptic Feedback. ყველაზე ეპიკური gaming გამოცდილება.',
             image_url='https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=600&q=80'),

        dict(name='PlayStation 5 Slim', category='console', platform='PS5',
             price=1649, stock=15,
             description='PS5-ის კომპაქტური ვერსია. 1TB SSD, ყველა PS5 თამაშთან '
                         'თავსებადი, 30% უფრო პატარა ზომა.',
             image_url='https://images.unsplash.com/photo-1607853202273-797f1c22a38e?w=600&q=80'),

        dict(name='Xbox Series X', category='console', platform='Xbox',
             price=1799, stock=10,
             description='Microsoft-ის ყველაზე ძლიერი კონსოლი. 12 Teraflop GPU, '
                         '1TB NVMe SSD, Quick Resume, Game Pass-თან ინტეგრაცია.',
             image_url='https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=600&q=80'),

        dict(name='Xbox Series S', category='console', platform='Xbox',
             price=999, stock=20,
             description='ყველაზე ხელმისაწვდომი Xbox. 1440p gaming, 512GB SSD. '
                         'Game Pass Ultimate-ისთვის შესანიშნავი არჩევანი.',
             image_url='https://images.unsplash.com/photo-1621259182978-fbf93132d53d?w=600&q=80'),

        dict(name='Nintendo Switch OLED', category='console', platform='Switch',
             price=1199, stock=18,
             description='7" OLED ეკრანი, 64GB storage, გაუმჯობესებული audio. '
                         'ითამაშე სახლში და გზაში. Nintendo-ს ექსკლუზივები.',
             image_url='https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=600&q=80'),

        # ── Console Games ─────────────────────────────────────────────────────
        dict(name="Marvel's Spider-Man 2", category='console_game', platform='PS5',
             price=109, stock=45,
             description='პიტერ პარკერი + მაილს მოროლსი vs ვენომი. '
                         'PS5 ექსკლუზივი. 4K/60fps, DualSense სრული მხარდაჭერა.',
             image_url='https://images.unsplash.com/photo-1534361960057-19f4434a5d59?w=600&q=80'),

        dict(name='God of War Ragnarök', category='console_game', platform='PS5',
             price=99, stock=35,
             description='კრატოსი + ატრეუსი Norse Mythology-ის ეპიკური დასასრულში. '
                         'GOTY 2022. 30-50 საათი კამპანია.',
             image_url='https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&q=80'),

        dict(name='Horizon Forbidden West', category='console_game', platform='PS5',
             price=79, stock=30,
             description='ალოი ახალ სამყაროში. გრაფიკული შედევრი, ღია სამყარო, '
                         'ეპიკური ბრძოლები. PS5 დუალსენსის სრული გამოყენება.',
             image_url='https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600&q=80'),

        dict(name='Forza Horizon 5', category='console_game', platform='Xbox',
             price=89, stock=40,
             description='მექსიკის ღია სამყარო. 500+ მანქანა, 4K/60fps. '
                         'Xbox Game Pass-შიც ხელმისაწვდომი.',
             image_url='https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?w=600&q=80'),

        dict(name='Zelda: Tears of the Kingdom', category='console_game', platform='Switch',
             price=109, stock=30,
             description='Breath of the Wild-ის გაგრძელება. Ultrahand, Fuse, Ascend. '
                         '2023 GOTY. 60+ საათი.',
             image_url='https://images.unsplash.com/photo-1511512578047-dfb367046420?w=600&q=80'),

        dict(name='Mario Kart 8 Deluxe', category='console_game', platform='Switch',
             price=79, stock=50,
             description='48 ტრეკი, 4-player local co-op. Switch-ის ყველაზე გაყიდვადი. '
                         'შესანიშნავი ოჯახისთვის.',
             image_url='https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=600&q=80'),

        # ── PC Games ──────────────────────────────────────────────────────────
        dict(name='Cyberpunk 2077 + Phantom Liberty', category='pc_game', platform='PC',
             price=89, stock=999,
             description='Night City ღია სამყარო RPG + DLC. V-ს ეპიკური ისტორია. '
                         'RTX Ray Tracing, DLSS 3. CD Projekt Red.',
             image_url='https://images.unsplash.com/photo-1542751371-adc38448a05e?w=600&q=80'),

        dict(name='Elden Ring', category='pc_game', platform='Multi',
             price=79, stock=999,
             description='FromSoftware × George R.R. Martin. 2022 GOTY. '
                         'Souls-like masterpiece. The Lands Between ღია სამყარო.',
             image_url='https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=600&q=80'),

        dict(name="Baldur's Gate 3", category='pc_game', platform='Multi',
             price=74, stock=999,
             description='D&D RPG by Larian Studios. 100+ საათი კონტენტი, '
                         'co-op 4 მოთამაშემდე. 2023 ყველა GOTY ჯილდო.',
             image_url='https://images.unsplash.com/photo-1546519638-68e109498ffc?w=600&q=80'),

        dict(name='Red Dead Redemption 2', category='pc_game', platform='Multi',
             price=69, stock=999,
             description='Rockstar-ის Wild West შედევრი. Arthur Morgan-ის ეპიკური '
                         'ისტორია. ყველა დროის ერთ-ერთი საუკეთესო თამაში.',
             image_url='https://images.unsplash.com/photo-1533228705496-072d5ad69dc5?w=600&q=80'),

        dict(name='The Witcher 3: Wild Hunt GOTY', category='pc_game', platform='Multi',
             price=39, stock=999,
             description='Geralt of Rivia-ს ეპიკური თავგადასავალი. GOTY Edition: '
                         'Hearts of Stone + Blood and Wine DLC. 200+ საათი.',
             image_url='https://images.unsplash.com/photo-1511512578047-dfb367046420?w=600&q=80'),

        dict(name='Hogwarts Legacy', category='pc_game', platform='Multi',
             price=79, stock=999,
             description='Harry Potter-ის სამყარო 1800-იანი წლებში. ღია სამყარო RPG, '
                         'Hogwarts, ჯადოსნობა, mythical beasts.',
             image_url='https://images.unsplash.com/photo-1551103782-8ab07afd45c1?w=600&q=80'),

        # ── Controllers ───────────────────────────────────────────────────────
        dict(name='DualSense Wireless Controller', category='controller', platform='PS5',
             price=189, stock=28,
             description='Haptic feedback, adaptive triggers — თითოეული ბრძოლა '
                         'რეალისტური. 12სთ ბატარეა. USB-C.',
             image_url='https://images.unsplash.com/photo-1592840496694-26d035b52b48?w=600&q=80'),

        dict(name='DualSense Edge (Pro Controller)', category='controller', platform='PS5',
             price=369, stock=10,
             description='PS5 Pro Controller. Remappable back buttons, replaceable '
                         'stick caps, customizable trigger travel. eSports-ისთვის.',
             image_url='https://images.unsplash.com/photo-1592840496694-26d035b52b48?w=600&q=80'),

        dict(name='Xbox Elite Controller Series 2', category='controller', platform='Xbox',
             price=379, stock=12,
             description='40+ customization option. Adjustable tension thumbsticks, '
                         'hair trigger locks, rubberized grip, 40h ბატარეა.',
             image_url='https://images.unsplash.com/photo-1612287230202-1ff1d85d1bdf?w=600&q=80'),

        dict(name='Nintendo Switch Pro Controller', category='controller', platform='Switch',
             price=169, stock=22,
             description='Full-size controller Switch-ისთვის. 40სთ ბატარეა, '
                         'HD Rumble, Gyro controls, NFC (amiibo).',
             image_url='https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=600&q=80'),

        # ── Headsets ──────────────────────────────────────────────────────────
        dict(name='HyperX Cloud Alpha Wireless', category='headset', platform='Multi',
             price=299, stock=15,
             description='300 საათი ბატარეა! Dual chamber drivers, '
                         'detachable noise-cancelling mic. PC + PS4/PS5 თავსებადი.',
             image_url='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80'),

        dict(name='SteelSeries Arctis Nova Pro Wireless', category='headset', platform='Multi',
             price=449, stock=8,
             description='Hi-Fi gaming audio. Active Noise Cancellation, '
                         'Infinity Power System, 2 ჩამონაცვლებელი ბატარეა.',
             image_url='https://images.unsplash.com/photo-1583394838336-acd977736f90?w=600&q=80'),

        dict(name='Razer BlackShark V2 Pro', category='headset', platform='Multi',
             price=329, stock=14,
             description='Wireless, 70სთ ბატარეა. THX Spatial Audio, '
                         'HyperClear Supercardioid mic. eSports standard.',
             image_url='https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=80'),

        # ── Keyboards ─────────────────────────────────────────────────────────
        dict(name='Logitech G Pro X TKL Keyboard', category='keyboard', platform='PC',
             price=349, stock=12,
             description='Hot-swappable GX switches. LIGHTSYNC RGB, aircraft-grade '
                         'aluminum frame. Pro gaming standard.',
             image_url='https://images.unsplash.com/photo-1601445638532-1ef87a3778fa?w=600&q=80'),

        dict(name='Razer Huntsman V2 TKL', category='keyboard', platform='PC',
             price=289, stock=16,
             description='Optical switches — fastest actuation. Doubleshot PBT keycaps, '
                         'Razer Chroma RGB, sound dampening foam.',
             image_url='https://images.unsplash.com/photo-1601445638532-1ef87a3778fa?w=600&q=80'),

        # ── Mice ──────────────────────────────────────────────────────────────
        dict(name='Logitech G Pro X Superlight 2', category='mouse', platform='PC',
             price=279, stock=18,
             description='61გ წონა! HERO 2 25K sensor, 95სთ ბატარეა, '
                         'LIGHTSPEED wireless. Pro-ების არჩევანი.',
             image_url='https://images.unsplash.com/photo-1527814050087-3793815479db?w=600&q=80'),

        dict(name='Razer DeathAdder V3 HyperSpeed', category='mouse', platform='PC',
             price=219, stock=20,
             description='Focus Pro 30K sensor, 90სთ ბატარეა, HyperSpeed wireless. '
                         'ერგონომიული, კომფორტული, სწრაფი.',
             image_url='https://images.unsplash.com/photo-1527814050087-3793815479db?w=600&q=80'),

        # ── Monitors ──────────────────────────────────────────────────────────
        dict(name='ASUS ROG Swift 27" 165Hz QHD', category='monitor', platform='PC',
             price=1299, stock=6,
             description='27" IPS, 2560x1440, 165Hz, 1ms GTG. G-Sync Compatible, '
                         'HDR400, ELMB-Sync. RGB lighting.',
             image_url='https://images.unsplash.com/photo-1527443224154-c4a573d9c27c?w=600&q=80'),

        dict(name='LG UltraGear 27" 240Hz', category='monitor', platform='PC',
             price=1499, stock=5,
             description='27" Nano IPS, 1440p, 240Hz, 1ms. NVIDIA G-Sync + '
                         'AMD FreeSync Premium Pro. HDR600.',
             image_url='https://images.unsplash.com/photo-1527443224154-c4a573d9c27c?w=600&q=80'),

        # ── GPUs ──────────────────────────────────────────────────────────────
        dict(name='NVIDIA RTX 4070 Ti Super', category='gpu', platform='PC',
             price=2299, stock=4,
             description='16GB GDDR6X, Ada Lovelace. DLSS 3.5, Frame Generation, '
                         'Ray Tracing. 4K gaming at high settings.',
             image_url='https://images.unsplash.com/photo-1591488320449-011701bb6704?w=600&q=80'),

        dict(name='NVIDIA RTX 4080 Super', category='gpu', platform='PC',
             price=3499, stock=3,
             description='16GB GDDR6X, 208 TOPS AI Performance. DLSS 3.5, '
                         '4K/120fps capable. Creator + Gamer flagship.',
             image_url='https://images.unsplash.com/photo-1591488320449-011701bb6704?w=600&q=80'),

        # ── Chairs ────────────────────────────────────────────────────────────
        dict(name='Secretlab TITAN Evo 2024', category='chair', platform='N/A',
             price=1099, stock=7,
             description='Pebble seat base, 4D L-ADAPT lumbar support, '
                         'magnetic memory foam head pillow. 180° reclining. 5 წლის გარანტია.',
             image_url='https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600&q=80'),

        dict(name='DXRacer Formula Series', category='chair', platform='N/A',
             price=649, stock=10,
             description='Racing-style gaming chair. Steel frame, high-density foam, '
                         '3D adjustable armrests. 150კგ load capacity.',
             image_url='https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=600&q=80'),

        # ── Accessories ───────────────────────────────────────────────────────
        dict(name='Elgato Stream Deck MK.2', category='accessory', platform='PC',
             price=379, stock=11,
             description='15 LCD key სტრიმინგ კონტროლერი. OBS, Twitch, YouTube, '
                         'Spotify კონტროლი. Drag-and-drop setup.',
             image_url='https://images.unsplash.com/photo-1618384887929-16ec33fab9ef?w=600&q=80'),

        dict(name='PS5 DualSense Charging Station', category='accessory', platform='PS5',
             price=129, stock=20,
             description='ერთდროულად 2 DualSense კონტროლერის დამუხტვა. '
                         'LED indicator, USB-C, 3 საათი სრული დამუხტვა.',
             image_url='https://zoommer.ge/_next/image?url=https%3A%2F%2Fs3.zoommer.ge%2Fsite%2F168d70eb-ddd8-48f5-a1fd-a5dd5862a366_Thumb.jpeg&w=640&q=100'),
    ]

    added = 0
    for pd in products:
        if not Product.query.filter_by(name=pd['name']).first():
            db.session.add(Product(**pd))
            added += 1
    if added:
        db.session.commit()
        print(f'✅  {added} products seeded.')


app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed()
    app.run(debug=True, host='0.0.0.0')
