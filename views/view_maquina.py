import logging
from main import app, db
from flask import request, jsonify
from models import Maquina

# Configurando Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/maquina', methods=['POST'])
def criar_maquina():
    logging.info('Iniciando a criação de uma nova maquina.')
    try:
        data = request.get_json()
        logging.info(f'Dados recebidos: {data}')
        ## Validar Numero de Serie da Maquina na base da Fertecnica

        nova_maquina = Maquina(
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
    
    except Exception as e:
        logging.error(f'Erro ao criar maquina: {e}')
        db.session.rollback()
        return jsonify({'mensagem':f'Erro ao criar maquina: {e}'}), 500


@app.route('/maquina/<id>', methods=['GET'])
def consulta_maquina(id):
    logging.info(f'Iniciando consulta da Maquina ID: {id}.')
    maquina = Maquina.query.get(id)
    if maquina:
        return jsonify({
            'id': maquina.id,
            'nome': maquina.nome,
            'modelo': maquina.modelo,
            'numero_serie': maquina.numero_serie,
            'empresaId': maquina.empresaId
        }), 200
    return jsonify({'mensagem':'Maquina não encontrada'}), 404


@app.route('/maquina/empresa/<id>', methods=['GET'])
def consulta_maquina_empresa(id):
    logging.info(f'Iniciando consulta da Maquina da Empresa ID: {id}.')
    maquinas = Maquina.query.filter_by(empresaId=id)
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
    maquina = Maquina.query.get(id)
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
    maquina = Maquina.query.get(id)
    if maquina:
        db.session.delete(maquina)
        db.session.commit()
        return jsonify({'mensagem': 'Maquina deletada com sucesso!'}), 200
    
    return jsonify({'mensagem': 'Maquina não encontrada!'}), 404
