import logging
from main import app, db, token_auth, mail
from flask import flash, request, jsonify, render_template, redirect, url_for
from flask_httpauth import HTTPTokenAuth
from models import Empresas, Usuarios
from flask_mail import Message

# Configurando Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/empresa', methods=['POST'])
@token_auth.login_required
def criar_empresa():
    logging.info('Iniciando a criação de uma nova empresa.')
    try:
        data = request.get_json()
        logging.info(f'Dados recebidos: {data}')
        ## Validar CNPJ na base da Fertecnica

        login = data['login']
        senha = data['senha']

        ## Validar campos de Login e Senha
        if not login or not senha:
            return jsonify({'mensagem':'Login e Senha são obrigatorios'})
        
        ## Validar se já existe algum Usuario com esse login cadastrado
        if Usuarios.query.filter_by(login=login).first():
            return jsonify({'mensagem':'Login ja existe!'})

        nova_empresa = Empresas(
            id = data['id'],
            cnpj = data['cnpj'],
            razao_social = data['razaosocial'],
            nome_fantasia = data['nomefantasia'],
            email = data['email'],
            sincronizado = False,
            ativo = True,
            aprovado = False
        )
        novo_usuario = Usuarios(
            id = data['usuarioId'],
            empresaId = nova_empresa.id,
            nome = data['nome'],
            cpf = data['cpf'],
            email = data['usuarioEmail'],
            login = login,
            perfil = data['perfil'],
            sincronizado = False,
            ativo = True,
        )
        novo_usuario.set_password(senha)
        logging.info(f'Dados da Nova Empresa: {nova_empresa}')
        logging.info(f'Dados do Novo Usuario: {novo_usuario}')
        
        db.session.add(nova_empresa)
        db.session.commit()
        db.session.add(novo_usuario)
        db.session.commit()
        logging.info(f'Empresa criada com sucesso. ID: {nova_empresa.id}')
        logging.info(f'Usuario criado com sucesso. Login: {novo_usuario.login}')
        return jsonify({'mensagem':'Empresa criada com sucesso!'}), 201
    
    except Exception as e:
        logging.error(f'Erro ao criar empresa: {e}')
        db.session.rollback()
        return jsonify({'mensagem':f'Erro ao criar empresa: {e}'}), 500

@app.route('/empresas', methods=['GET'])
@token_auth.login_required
def listar_empresas():
    empresas = Empresas.query.filter_by(sincronizado=False).all()
    resultado = []
    for empresa in empresas:
        resultado.append({
            'id': empresa.id,
            'cnpj': empresa.cnpj,
            'razao_social': empresa.razao_social,
            'nome_fantasia': empresa.nome_fantasia,
            'email': empresa.email,
            'ativo': 'ATIVO' if empresa.ativo else 'INATIVO',
            'aprovado': 'OK' if empresa.aprovado else 'PENDENTE'
        })
    return jsonify(resultado), 200

@app.route('/empresa/<id>', methods=['GET'])
@token_auth.login_required
def consulta_empresa(id):
    empresa = Empresas.query.get(id)
    if empresa:
        return jsonify({
            'id': empresa.id,
            'cnpj': empresa.cnpj,
            'razaosocial': empresa.razao_social,
            'nomefantasia': empresa.nome_fantasia,
            'ativo': 'ATIVO' if empresa.ativo else 'INATIVO'
        }), 200
    return jsonify({'mensagem':'Empresa não encontrada'}), 404

@app.route('/empresa/<id>', methods=['PUT'])
@token_auth.login_required
def atualizar_empresa(id):
    empresa = Empresas.query.get(id)
    if empresa:
        data = request.get_json()
        empresa.cnpj = data.get('cnpj', empresa.cnpj)
        empresa.razao_social = data.get('razaosocial', empresa.razao_social)
        empresa.nome_fantasia = data.get('nomefantasia', empresa.nome_fantasia)
        db.session.commit()
        return jsonify({'mensagem':'Empresa atualizada com sucesso!'}), 200
    
    return jsonify({'mensagem':'Empresa não encontrada'}), 404

@app.route('/empresa/<id>', methods=['DELETE'])
@token_auth.login_required
def deletar_empresa(id):
    empresa = Empresas.query.get(id)
    if empresa:
        empresa.ativo = False
        empresa.sincronizado = False
        db.session.commit()
        return jsonify({'mensagem': 'Empresa deletada com sucesso!'}), 200
    
    return jsonify({'mensagem': 'Empresa não encontrada!'}), 404

@app.route('/empresa/pendentes')
def listar_empresas_pendentes():
    listaEmpresasPendentes = Empresas.query.filter_by(aprovado=False).all()
    return render_template('aprovar_empresa.html', titulo='Aprovar Empresas Pendentes', empresas=listaEmpresasPendentes)

@app.route('/empresa/aprovar/<id>')
def aprovar_empresa(id):
    empresa = Empresas.query.filter_by(id=id).first()
    logging.info(f'Empresa encontrada. ID: {empresa.id} | Nome: {empresa.nome_fantasia}')
    empresa.aprovado = True

    db.session.add(empresa)
    db.session.commit()
    flash('Empresa aprovada com sucesso!')
    logging.info(f'Empresa Aprovada!')

    # Enviar email de aprovação
    enviou = enviar_email_cadastro_aprovado(empresa.email, empresa.nome_fantasia)
    if enviou:
        flash(f'Um email de confirmação foi enviado para: {empresa.email}')
    else:
        flash(f'Erro ao enviar email de confirmação para: {empresa.email}', 'error')

    return redirect( url_for('listar_empresas_pendentes') )

def enviar_email_cadastro_aprovado(destinatario_email, nome_fantasia):
    """Envia um email informando que o cadastro da empresa foi aprovado."""
    try:
        msg = Message(
            subject='Cadastro Aprovado - Fertecnica',
            recipients=[destinatario_email]
        )
        msg.body = f"""
Prezada(o) {nome_fantasia},

Informamos que o cadastro da sua empresa foi aprovado pela Fertecnica com sucesso!

Agora, você já pode utilizar o App para realizar as inspeções das suas máquinas.

Agradecemos o seu cadastro.

Atenciosamente,
Equipe Fertecnica
"""
        mail.send(msg)
        logging.info(f'Email de aprovação enviado para: {destinatario_email}')
        return True
    except Exception as e:
        logging.error(f'Erro ao enviar email de aprovação para {destinatario_email}: {e}')
        return False