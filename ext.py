from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()

login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'გთხოვთ გაიაროთ ავტორიზაცია.'
login_manager.login_message_category = 'warning'
