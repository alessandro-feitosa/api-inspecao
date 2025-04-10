import logging
from main import app, db
from flask import request, jsonify
from models import Operador

# Configurando Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/operador', methods=['POST'])
def criar_operador():
    logging.info('Iniciando a criação de um novo operador.')
    try:
        data = request.get_json()
        logging.info(f'Dados recebidos: {data}')

        nova_operador = Operador(
            id = data['id'],
            nome = data['nome'],
            cpf = data['cpf'],
            empresaId = data['empresaId']
        )
        logging.info(f'Dados do novo Operador: {nova_operador}')
        db.session.add(nova_operador)
        db.session.commit()
        logging.info(f'Operador criado com sucesso. ID: {nova_operador.id}')
        return jsonify({'mensagem':'Operador criado com sucesso!'}), 201
    
    except Exception as e:
        logging.error(f'Erro ao criar operador: {e}')
        db.session.rollback()
        return jsonify({'mensagem':f'Erro ao criar operador: {e}'}), 500


@app.route('/operador/<id>', methods=['GET'])
def consulta_operador(id):
    logging.info(f'Iniciando consulta do Operador ID: {id}.')
    operador = Operador.query.get(id)
    if operador:
        return jsonify({
            'id': operador.id,
            'nome': operador.nome,
            'cpf': operador.cpf,
            'empresaId': operador.empresaId
        }), 200
    return jsonify({'mensagem':'Operador não encontrada'}), 404


@app.route('/operador/empresa/<id>', methods=['GET'])
def consulta_operador_empresa(id):
    logging.info(f'Iniciando consulta dos Operadores da Empresa ID: {id}.')
    operadores = Operador.query.filter_by(empresaId=id)
    resultado = []
    for operador in operadores:
        resultado.append({
            'id': operador.id,
            'nome': operador.nome,
            'cpf': operador.cpf,
            'empresaId': operador.empresaId
        })
    return jsonify(resultado), 200


@app.route('/operador/<id>', methods=['PUT'])
def atualizar_operador(id):
    logging.info(f'Iniciando atualizacao do Operador ID: {id}.')
    operador = Operador.query.get(id)
    if operador:
        data = request.get_json()
        operador.nome = data.get('nome', operador.nome)
        operador.cpf = data.get('cpf', operador.cpf)
        operador.empresaId = data.get('empresaId', operador.empresaId)
        db.session.commit()
        return jsonify({'mensagem':'Operador atualizado com sucesso!'}), 200
    
    return jsonify({'mensagem':'Operador não encontrada'}), 404

@app.route('/operador/<id>', methods=['DELETE'])
def deletar_operador(id):
    logging.info(f'Iniciando remocao do Operador ID: {id}.')
    operador = Operador.query.get(id)
    if operador:
        db.session.delete(operador)
        db.session.commit()
        return jsonify({'mensagem': 'Operador deletado com sucesso!'}), 200
    
    return jsonify({'mensagem': 'Operador não encontrada!'}), 404
