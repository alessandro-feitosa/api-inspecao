import logging
from main import app, db, token_auth
from flask import request, jsonify
from models import Usuarios, Empresas

# Configurando Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/usuario/autenticar', methods=['POST'])
@token_auth.login_required
def autenticarUsuario():
    data = request.get_json()
    logging.info(f'Dados recebidos: {data}')
    login = data['login']
    senha = data['senha']

    usuario = Usuarios.query.filter_by(login=login).first()
    if usuario:
        logging.info(f'Usuario encontrado!')
        empresa = Empresas.query.get(usuario.empresaId)
        if empresa:
            logging.info(f'Empresa encontrada {empresa}')
            if empresa.aprovado == False:
                return jsonify({'mensagem':'Empresa esperando aprovaçao'}), 403
            
            if usuario and usuario.check_password(senha):
                return jsonify({
                    'id': usuario.id,
                    'empresaId': usuario.empresaId,
                    'nome': usuario.nome,
                    'cpf': usuario.cpf,
                    'email': usuario.email,
                    'login': usuario.login,
                    'perfil': usuario.perfil
                }), 200
        else:
            return jsonify({'mensagem':'Empresa não encontrada'}), 404
    else:
        return jsonify({'mensagem':'Usuario não encontrado'}), 404
    

@app.route('/usuario', methods=['POST'])
def criar_usuario():
    logging.info('Iniciando a criação de um novo usuario.')
    try:
        data = request.get_json()
        logging.info(f'Dados recebidos: {data}')

        login = data['login']
        senha = data['senha']

        ## Validar campos de Login e Senha
        if not login or not senha:
            return jsonify({'mensagem':'Login e Senha são obrigatorios'})
        
        ## Validar se já existe algum Usuario com esse login cadastrado
        if Usuarios.query.filter_by(login=login).first():
            return jsonify({'mensagem':'Login ja existe!'})

        novo_usuario = Usuarios(
            id = data['id'],
            empresaId = data['empresaId'],
            nome = data['nome'],
            cpf = data['cpf'],
            email = data['email'],
            login = login,
            perfil = data['perfil'],
            sincronizado = False,
            ativo = True,
        )
        novo_usuario.set_password(senha)
        logging.info(f'Dados do Novo Usuario: {novo_usuario}')
        db.session.add(novo_usuario)
        db.session.commit()
        logging.info(f'Operador criado com sucesso. ID: {novo_usuario.id}')
        return jsonify({'mensagem':'Usuario criado com sucesso!'}), 201
    
    except Exception as e:
        logging.error(f'Erro ao criar operador: {e}')
        db.session.rollback()
        return jsonify({'mensagem':f'Erro ao criar operador: {e}'}), 500


@app.route('/usuario/<id>', methods=['GET'])
def consulta_operador(id):
    logging.info(f'Iniciando consulta do Operador ID: {id}.')
    usuario = Usuarios.query.get(id)
    if usuario:
        return jsonify({
            'id': usuario.id,
            'nome': usuario.nome,
            'cpf': usuario.cpf,
            'email': usuario.email,
            'login': usuario.login,
            'perfil': usuario.perfil,
            'empresaId': usuario.empresaId,
            'ativo': 'ATIVO' if usuario.ativo else 'INATIVO',
        }), 200
    return jsonify({'mensagem':'Operador não encontrada'}), 404


@app.route('/usuario/empresa/<id>', methods=['GET'])
def consulta_operador_empresa(id):
    logging.info(f'Iniciando consulta dos Operadores da Empresa ID: {id}.')
    listaUsuarios = Usuarios.query.filter_by(empresaId=id)
    resultado = []
    for usuario in listaUsuarios:
        resultado.append({
            'id': usuario.id,
            'nome': usuario.nome,
            'cpf': usuario.cpf,
            'email': usuario.email,
            'login': usuario.login,
            'perfil': usuario.perfil,
            'empresaId': usuario.empresaId
        })
    return jsonify(resultado), 200


@app.route('/usuario/<id>', methods=['PUT'])
def atualizar_operador(id):
    logging.info(f'Iniciando atualizacao do Usuario ID: {id}.')
    usuario = Usuarios.query.get(id)
    if usuario:
        data = request.get_json()
        usuario.nome = data.get('nome', usuario.nome)
        usuario.cpf = data.get('cpf', usuario.cpf)
        usuario.email = data.get('email', usuario.email)
        usuario.empresaId = data.get('empresaId', usuario.empresaId)
        db.session.commit()
        return jsonify({'mensagem':'Usuario atualizado com sucesso!'}), 200
    
    return jsonify({'mensagem':'Usuario não encontrada'}), 404

@app.route('/usuario/<id>', methods=['DELETE'])
def deletar_operador(id):
    logging.info(f'Iniciando remocao do Usuario ID: {id}.')
    usuario = Usuarios.query.get(id)
    if usuario:
        usuario.ativo = False
        usuario.sincronizado = False
        db.session.commit()
        return jsonify({'mensagem': 'Usuario inativado com sucesso!'}), 200
    
    return jsonify({'mensagem': 'Usuario não encontrada!'}), 404
