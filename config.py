import os

SECRET_KEY='teste'

API_TOKEN = "fertecnica"

SQLALCHEMY_DATABASE_URI = \
    "{SGBD}://{usuario}:{senha}@{servidor}/{database}".format(
        SGBD = 'mysql+mysqlconnector',
        usuario = 'testeapp',
        senha = 'teste123',
        servidor = 'localhost',
        database = 'api_inspecao'
    )

CONFIG_EMAIL = 'feitosa1985@gmail.com'
CONFIG_SENHA = 'pvmt wexb tgsx ffnt'

EMAIL_ADMIN = 'feitosa1985@gmail.com'
NOME_ADMIN = 'Gestor'