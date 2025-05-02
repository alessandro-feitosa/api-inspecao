from main import db, bcrypt
import os

class Empresas(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    cnpj = db.Column(db.String(14), unique=True, nullable=False)
    razao_social = db.Column(db.String(100), nullable=False)
    nome_fantasia = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    sincronizado = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)
    aprovado = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Empresa: {self.razao_social}(CNPJ: {self.cnpj})>'

class Usuarios(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    empresaId = db.Column(db.String(100), nullable=False)
    nome = db.Column(db.String(255), nullable=False)
    email= db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), nullable=False)
    login = db.Column(db.String(50), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128), nullable=False)
    senha_salt = db.Column(db.String(29), nullable=False)
    perfil = db.Column(db.String(50), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    sincronizado = db.Column(db.Boolean, default=False)

    def set_password(self, senha):
        ## Gera um salt aleatorio
        self.senha_salt = bcrypt.generate_password_hash(os.urandom(16)).decode('utf-8')
        self.senha_hash = bcrypt.generate_password_hash((senha + self.senha_salt).encode('utf-8')).decode('utf-8')
    
    def check_password(self, senha):
        return bcrypt.check_password_hash(self.senha_hash, (senha + self.senha_salt).encode('utf-8'))
    
    def __repr__(self):
        return f'<Usuario: {self.nome}, Login: {self.login}'

class Maquinas(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    numero_serie = db.Column(db.String(50), nullable=False)
    empresaId = db.Column(db.String(100), nullable=False)
    sincronizado = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Maquina: {self.modelo} - {self.numero_serie}>'

class Inspecao(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    maquinaId = db.Column(db.String(100), nullable=False)
    usuarioId = db.Column(db.String(100), nullable=False)
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
    observacao = db.Column(db.String(255), nullable=False)
    sincronizado = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Inspecao: Dia {self.dataInspecao} | Maquina {self.maquinaId} | Usuario {self.usuarioId}>'

class Defeitos(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    inspecaoId = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    desvioAnomalia = db.Column(db.String(255), nullable=False)
    causaAnomalia = db.Column(db.String(255), nullable=False)
    acaoCorretiva = db.Column(db.String(255), nullable=False)
    responsavel = db.Column(db.String(255), nullable=False)
    sincronizado = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Defeito: {self.status} Desvio: {self.desvioAnomalia} Causa: {self.causaAnomalia} Acao Corretiva: {self.acaoCorretiva} Responsavel: {self.responsavel}'
