from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class CrearCuenta(FlaskForm):
    #The serial number will stay aside, until further notice
    #serial_number = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=2, max=5)])
    username = StringField('Nombre de usuario', validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField('Correo electrónico', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class IniciarSesion(FlaskForm):
    email = StringField('Correo electrónico',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Login')