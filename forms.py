from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, TextAreaField,
                     FloatField, IntegerField, SelectField)
from wtforms.validators import (DataRequired, Email, EqualTo, Length,
                                NumberRange, Optional, ValidationError)
from models import User


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterForm(FlaskForm):
    username = StringField('მომხმარებლის სახელი', validators=[
        DataRequired(message='სავალდებულო ველი'),
        Length(min=3, max=64, message='3–64 სიმბოლო')
    ])
    email = StringField('ელ-ფოსტა', validators=[
        DataRequired(message='სავალდებულო ველი'),
        Email(message='შეიყვანეთ სწორი ელ-ფოსტა')
    ])
    password = PasswordField('პაროლი', validators=[
        DataRequired(message='სავალდებულო ველი'),
        Length(min=6, message='მინიმუმ 6 სიმბოლო')
    ])
    confirm_password = PasswordField('გაიმეორეთ პაროლი', validators=[
        DataRequired(message='სავალდებულო ველი'),
        EqualTo('password', message='პაროლები არ ემთხვევა')
    ])
    submit = SubmitField('რეგისტრაცია')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('ეს სახელი უკვე დაკავებულია.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('ეს ელ-ფოსტა უკვე რეგისტრირებულია.')


class LoginForm(FlaskForm):
    email = StringField('ელ-ფოსტა', validators=[
        DataRequired(message='სავალდებულო ველი'),
        Email(message='შეიყვანეთ სწორი ელ-ფოსტა')
    ])
    password = PasswordField('პაროლი', validators=[
        DataRequired(message='სავალდებულო ველი')
    ])
    submit = SubmitField('შესვლა')


# ── Profile settings ──────────────────────────────────────────────────────────

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('მიმდინარე პაროლი', validators=[
        DataRequired(message='სავალდებულო ველი')
    ])
    new_password = PasswordField('ახალი პაროლი', validators=[
        DataRequired(message='სავალდებულო ველი'),
        Length(min=6, message='მინიმუმ 6 სიმბოლო')
    ])
    confirm_password = PasswordField('გაიმეორეთ ახალი პაროლი', validators=[
        DataRequired(message='სავალდებულო ველი'),
        EqualTo('new_password', message='პაროლები არ ემთხვევა')
    ])
    submit = SubmitField('პაროლის შეცვლა')


class ChangeEmailForm(FlaskForm):
    new_email = StringField('ახალი ელ-ფოსტა', validators=[
        DataRequired(message='სავალდებულო ველი'),
        Email(message='შეიყვანეთ სწორი ელ-ფოსტა')
    ])
    current_password = PasswordField('პაროლი (დასადასტურებლად)', validators=[
        DataRequired(message='სავალდებულო ველი')
    ])
    submit = SubmitField('ელ-ფოსტის შეცვლა')

    def validate_new_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('ეს ელ-ფოსტა უკვე გამოყენებულია.')


# ── Product ───────────────────────────────────────────────────────────────────

CATEGORIES = [
    ('',             'აირჩიეთ კატეგორია'),
    ('console',      'კონსოლი'),
    ('pc_game',      'PC თამაში'),
    ('console_game', 'კონსოლის თამაში'),
    ('controller',   'კონტროლერი'),
    ('headset',      'ჰედსეტი'),
    ('keyboard',     'კლავიატურა'),
    ('mouse',        'მაუსი'),
    ('monitor',      'მონიტორი'),
    ('gpu',          'ვიდეო ბარათი'),
    ('chair',        'სავარძელი'),
    ('accessory',    'აქსესუარი'),
]

PLATFORMS = [
    ('',      'პლატფორმა'),
    ('PC',    'PC'),
    ('PS5',   'PlayStation 5'),
    ('PS4',   'PlayStation 4'),
    ('Xbox',  'Xbox Series X/S'),
    ('Switch','Nintendo Switch'),
    ('Multi', 'მულტიპლატფორმა'),
    ('N/A',   'არ ეხება'),
]


class ProductForm(FlaskForm):
    name = StringField('სახელი', validators=[
        DataRequired(message='სავალდებულო ველი'),
        Length(min=2, max=120)
    ])
    description = TextAreaField('აღწერა', validators=[
        DataRequired(message='სავალდებულო ველი'),
        Length(min=10)
    ])
    price = FloatField('ფასი (₾)', validators=[
        DataRequired(message='სავალდებულო ველი'),
        NumberRange(min=0.01)
    ])
    category = SelectField('კატეგორია', choices=CATEGORIES, validators=[
        DataRequired(message='სავალდებულო ველი')
    ])
    platform  = SelectField('პლატფორმა', choices=PLATFORMS, validators=[Optional()])
    stock     = IntegerField('მარაგი', validators=[DataRequired(), NumberRange(min=0)])
    image_url = StringField('სურათის URL', validators=[Optional()])
    submit    = SubmitField('შენახვა')
