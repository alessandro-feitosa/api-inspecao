from main import db, bcrypt
import os

class Empresa(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    cnpj = db.Column(db.String(14), nullable=False)
    razaosocial = db.Column(db.String(100), nullable=False)
    nomefantasia = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    login = db.Column(db.String(80), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    senha_salt = db.Column(db.String(29), nullable=False)
    sincronizado = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)
    aprovado = db.Column(db.Boolean, default=False)

    def set_password(self, senha):
        ## Gera um salt aleatorio
        self.senha_salt = bcrypt.generate_password_hash(os.urandom(16)).decode('utf-8')
        self.senha_hash = bcrypt.generate_password_hash((senha + self.senha_salt).encode('utf-8')).decode('utf-8')
    
    def check_password(self, senha):
        return bcrypt.check_password_hash(self.senha_hash, (senha + self.senha_salt).encode('utf-8'))

    def __repr__(self):
        return f'<Empresa: {self.razaosocial}(CNPJ: {self.cnpj}) | Login: {self.login}>'

class Maquina(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    numero_serie = db.Column(db.String(50), nullable=False)
    empresaId = db.Column(db.String(100), nullable=False)
    sincronizado = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Maquina: {self.modelo} - {self.numero_serie}>'

class Operador(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(11), nullable=False)
    empresaId = db.Column(db.String(100), nullable=False)
    sincronizado = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Operador: {self.nome} (CPF: {self.cpf})'

from main import db

class Inspecao(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    maquinaId = db.Column(db.String(100), nullable=False)
    operadorId = db.Column(db.String(100), nullable=False)
    dataInspecao = db.Column(db.Date, nullable=False)
    horasDeOperacao = db.Column(db.Integer, nullable=False)
    horasEmCarga = db.Column(db.Integer, nullable=False)
    temperaturaOleo = db.Column(db.Integer, nullable=False)
    pressaoOleo = db.Column(db.Float, nullable=False)
    pressaoFiltroAr = db.Column(db.Float, nullable=False)
    temperaturaSaidaAr = db.Column(db.Integer, nullable=False)
    temperaturaEntradaAgua = db.Column(db.Integer, nullable=False)
    temperaturaSaidaAgua = db.Column(db.Integer, nullable=False)
    pressaoSeparadorArOleo = db.Column(db.Float, nullable=False)
    pressaoSaidaCompressor = db.Column(db.Float, nullable=False)
    temperaturaPontoOrvalho = db.Column(db.Integer, nullable=False)
    dreno = db.Column(db.Boolean)
    limpeza = db.Column(db.Boolean)
    status = db.Column(db.String(255), nullable=False)
    desvioAnomalia = db.Column(db.String(255), nullable=False)
    causaAnomalia = db.Column(db.String(255), nullable=False)
    acaoCorretiva = db.Column(db.String(255), nullable=False)
    responsavel = db.Column(db.String(255), nullable=False)
    sincronizado = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Inspecao: Dia {self.dataInspecao} | Maquina {self.maquinaId} | Operador {self.operadorId}>'