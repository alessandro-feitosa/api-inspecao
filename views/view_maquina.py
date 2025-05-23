import logging
from main import app, db
from flask import request, jsonify
from models import Maquinas
from helpers import validar_api_fertecnica

# Configurando Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/maquina', methods=['POST'])
def criar_maquina():
    logging.info('Iniciando a criação de uma nova maquina.')
    try:
        data = request.get_json()
        logging.info(f'Dados recebidos: {data}')
        ## Validar se Numero de Serie já exite no Banco de Dados
        numero_serie = data['numero_serie']
        if Maquinas.query.filter_by(numero_serie=numero_serie).first():
            return jsonify({'mensagem':'Numero de Serie da Maquina ja cadastrado na Base.'}), 400

        ## Validar Numero de Serie da Maquina na base da Fertecnica
        ## if(validar_api_fertecnica("", numero_serie) != True):
        ##     return jsonify({'mensagem':'Numero de Serie não cadastrado na Fertecnica.'}), 400

        nova_maquina = Maquinas(
            id = data['id'],
            nome = data['nome'],
            modelo = data['modelo'],
            numero_serie = data['numero_serie'],
            empresaId = data['empresaId']
        )
        logging.info(f'Dados da Nova Maquina: {nova_maquina}')
        db.session.add(nova_maquina)
        db.session.commit()
        logging.info(f'Maquina criada com sucesso. ID: {nova_maquina.id}')
        return jsonify({'mensagem':'Maquina criada com sucesso!'}), 201
    
    except KeyError as e:
        logging.error(f'Chave de validaçao ausente ou incorreta: {e}')
        db.session.rollback()
        return jsonify({'mensagem': f'Erro: Campo obrigatório ausente: {e}'}), 400
    except Exception as e:
        logging.error(f'Erro ao criar maquina: {e}')
        db.session.rollback()
        return jsonify({'mensagem': f'Erro ao criar maquina: {e}'}), 400


@app.route('/maquina/<id>', methods=['GET'])
def consulta_maquina(id):
    logging.info(f'Iniciando consulta da Maquina ID: {id}.')
    maquina = Maquinas.query.get(id)
    if maquina:
        return jsonify({
            'id': maquina.id,
            'nome': maquina.nome,
            'modelo': maquina.modelo,
            'numero_serie': maquina.numero_serie,
            'empresaId': maquina.empresaId,
            'ativo': 'ATIVO' if maquina.ativo else 'INATIVO'
        }), 200
    return jsonify({'mensagem':'Maquina não encontrada'}), 404


@app.route('/maquina/empresa/<id>', methods=['GET'])
def consulta_maquina_empresa(id):
    logging.info(f'Iniciando consulta da Maquina da Empresa ID: {id}.')
    maquinas = Maquinas.query.filter_by(empresaId=id)
    resultado = []
    for maquina in maquinas:
        resultado.append({
            'id': maquina.id,
            'nome': maquina.nome,
            'modelo': maquina.modelo,
            'numero_serie': maquina.numero_serie,
            'empresaId': maquina.empresaId
        })
    return jsonify(resultado), 200


@app.route('/maquina/<id>', methods=['PUT'])
def atualizar_maquina(id):
    logging.info(f'Iniciando atualizacao da Maquina ID: {id}.')
    maquina = Maquinas.query.get(id)
    if maquina:
        data = request.get_json()
        maquina.nome = data.get('nome', maquina.nome)
        maquina.modelo = data.get('modelo', maquina.modelo)
        maquina.numero_serie = data.get('numero_serie', maquina.numero_serie)
        maquina.empresaId = data.get('empresaId', maquina.empresaId)
        db.session.commit()
        return jsonify({'mensagem':'Maquina atualizada com sucesso!'}), 200
    
    return jsonify({'mensagem':'Maquina não encontrada'}), 404

@app.route('/maquina/<id>', methods=['DELETE'])
def deletar_maquina(id):
    logging.info(f'Iniciando remocao da Maquina ID: {id}.')
    maquina = Maquinas.query.get(id)
    if maquina:
        maquina.ativo = False
        maquina.sincronizado = False
        db.session.commit()
        return jsonify({'mensagem': 'Maquina deletada com sucesso!'}), 200
    
    return jsonify({'mensagem': 'Maquina não encontrada!'}), 404
