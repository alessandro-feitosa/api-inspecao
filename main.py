from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_httpauth import HTTPTokenAuth
from config import SECRET_KEY, CONFIG_EMAIL, CONFIG_SENHA
from flask_mail import Mail

app = Flask(__name__)
app.config.from_pyfile('config.py')
# Configurar o Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Seu servidor SMTP
app.config['MAIL_PORT'] = 587  # Porta do servidor SMTP
app.config['MAIL_USE_TLS'] = True  # Usar TLS
app.config['MAIL_USERNAME'] = CONFIG_EMAIL  # Seu endereço de email
app.config['MAIL_PASSWORD'] = CONFIG_SENHA  # Sua senha de email
app.config['MAIL_DEFAULT_SENDER'] = 'naoresponder@fertecnica.com.br'  # Seu remetente padrão

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
mail = Mail(app)
token_auth = HTTPTokenAuth(scheme='Bearer')

tokens = {
    SECRET_KEY: 'fertecnica'
}

@token_auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]


##@token_auth.unauthorized_handler
##def unauthorized():
##    return jsonify({'mensagem': 'Token inválido'}), 401

from views.view_empresa import *
from views.view_maquina import *
from views.view_usuario import *
from views.view_inspecao import *

if __name__ == '__main__':
    app.run(debug=True, host='192.168.15.144', port=5000)
    ##app.run(debug=True, host='192.168.27.228', port=5000)
    ##app.run(debug=True, host='0.0.0.0', port=443, ssl_context=('F:\certificado\certificate.crt', 'F:\certificado\server.key'))