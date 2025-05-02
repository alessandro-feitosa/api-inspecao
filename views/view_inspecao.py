import logging
from main import app, db, mail, token_auth
from flask import request, jsonify
from models import Inspecao, Maquinas, Empresas, Usuarios, Defeitos
from datetime import datetime
from flask_mail import Message
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER,TA_LEFT
from reportlab.lib import colors
from io import BytesIO

# Configurando Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/maquina/inspecao', methods=['POST'])
@token_auth.login_required
def criar_inspecao():
    logging.info('Iniciando a criação de uma nova Inspecao.')
    try:
        data = request.get_json()
        logging.info(f'Dados recebidos: {data}')

        # Formato esperado da data vinda do App (ajuste conforme necessário)
        data_format = '%d/%m/%Y'  # Exemplo: '2025-04-08'
        # Se a data vier com hora também, ajuste o formato: '%Y-%m-%d %H:%M:%S'

        try:
            data_inspecao_obj = datetime.strptime(data['dataInspecao'], data_format).date()
        except ValueError:
            logging.error(f"Erro ao converter data: {data['dataInspecao']} não corresponde ao formato {data_format}")
            return jsonify({'mensagem': f'Formato de data inválido. Esperado: {data_format}'}), 400

        nova_inspecao = Inspecao(
            id = data['id'],
            maquinaId = data['maquinaId'],
            usuarioId = data['usuarioId'],
            dataInspecao = data_inspecao_obj,
            horasDeOperacao = data['horasDeOperacao'],
            horasEmCarga = data['horasEmCarga'],
            temperaturaOleo = data['temperaturaOleo'],
            pressaoOleo = data['pressaoOleo'],
            pressaoFiltroAr = data['pressaoFiltroAr'],
            temperaturaSaidaAr = data['temperaturaSaidaAr'],
            temperaturaEntradaAgua = data['temperaturaEntradaAgua'],
            temperaturaSaidaAgua = data['temperaturaSaidaAgua'],
            pressaoSeparadorArOleo = data['pressaoSeparadorArOleo'],
            pressaoSaidaCompressor = data['pressaoSaidaCompressor'],
            temperaturaPontoOrvalho = data['temperaturaPontoOrvalho'],
            dreno = data.get('dreno'),
            limpeza = data.get('limpeza')
        )
        logging.info(f'Dados da Nova Inspeçao: {nova_inspecao}')
        defeitos = data.get('defeito')
        if defeitos:
            logging.info(f'Defeitos encontrados para a Inspeçao da Maquina {nova_inspecao.maquinaId} do dia {nova_inspecao.dataInspecao}')
            logging.info(f'Defeitos: {defeitos}')
            for defeito in defeitos:
                novo_defeito = Defeitos(
                    id = defeito.get('id'),
                    inspecaoId = nova_inspecao.id,
                    status = defeito.get('status'),
                    desvioAnomalia = defeito.get('desvioAnomalia'),
                    causaAnomalia = defeito.get('causaAnomalia'),
                    acaoCorretiva = defeito.get('acaoCorretiva'),
                    responsavel = defeito.get('responsavel'),
                    sincronizado = False if defeito.get('sincronizado') == None else True
                )
                db.session.add(novo_defeito)
        else:
            logging.info(f'Nenhum defeito foi reportado para a Inspeçao da Maquina {nova_inspecao.maquinaId} do dia {nova_inspecao.dataInspecao}')

        logging.info(f'Dados da Nova Inspecao: {nova_inspecao}')
        db.session.add(nova_inspecao)
        db.session.commit()
        logging.info(f'Inspecao criada com sucesso. ID: {nova_inspecao.id}')

        # ## Encontra a Maquina pelo maquinaId. E acha a Empresa pela Maquina.
        maquina = Maquinas.query.filter_by(id=nova_inspecao.maquinaId).first()
        usuario = Usuarios.query.filter_by(id=nova_inspecao.usuarioId).first()
        empresa = Empresas.query.filter_by(id=maquina.empresaId).first()

        if empresa:
            logging.info('Preparando dados para montar o email da inspeçao')
            titulo_email = f'Nova Inspecao Cadastrada - Maquina {maquina.modelo} - Serie {maquina.numero_serie} - Dia {nova_inspecao.dataInspecao.strftime('%d/%m/%Y')}'
            titulo_pdf = f'Inspecao_Maquina_{maquina.numero_serie}_{nova_inspecao.dataInspecao.strftime('%d_%m_%Y')}'

            pdf_buffer = criar_pdf_inspecao(nova_inspecao, maquina, usuario.nome)
            enviou = enviar_email_inspecao(empresa.email, empresa.nome_fantasia, pdf_buffer, titulo_email, titulo_pdf)

            if enviou:
                logging.info(f'Email com PDF enviado com sucesso para {empresa.email}')
            else:
                logging.info('Erro ao enviar email com PDF.')
        else:
            logging.info('Empresa associada à máquina não encontrada, email não enviado.')

        return jsonify({'mensagem':'Inspecao criada com sucesso!'}), 201
    
    except Exception as e:
        logging.error(f'Erro ao criar Inspecao: {e}')
        db.session.rollback()
        return jsonify({'mensagem':f'Erro ao criar Inspecao: {e}'}), 500


@app.route('/maquina/inspecao/<id>', methods=['GET'])
@token_auth.login_required
def consulta_inspecao(id):
    logging.info(f'Iniciando consulta da Maquina ID: {id}.')
    inspecao = Inspecao.query.get(id)
    if inspecao:
        defeitos = Defeitos.query.filter_by(inspecaoId=id)
        listaDefeitos = []
        if defeitos:
            for defeito in defeitos:
                listaDefeitos.append({
                    'id': defeito.id,
                    'status': defeito.status,
                    'desvioAnomalia': defeito.desvioAnomalia,
                    'causaAnomalia': defeito.causaAnomalia,
                    'acaoCorretiva': defeito.acaoCorretiva,
                    'responsavel': defeito.responsavel
                })
        else:
            logging.info(f'Nao existem defeitos para essa inspecao')

        return jsonify({
            "id": inspecao.id,
            "maquinaId": inspecao.maquinaId,
            "usuarioId": inspecao.usuarioId,
            "dataInspecao": inspecao.dataInspecao.strftime('%d/%m/%Y'),
            "horasDeOperacao": inspecao.horasDeOperacao,
            "horasEmCarga": inspecao.horasEmCarga,
            "temperaturaOleo": inspecao.temperaturaOleo,
            "pressaoOleo": inspecao.pressaoOleo,
            "pressaoFiltroAr": inspecao.pressaoFiltroAr,
            "temperaturaSaidaAr": inspecao.temperaturaSaidaAr,
            "temperaturaEntradaAgua": inspecao.temperaturaEntradaAgua,
            "temperaturaSaidaAgua": inspecao.temperaturaSaidaAgua,
            "pressaoSeparadorArOleo": inspecao.pressaoSeparadorArOleo,
            "pressaoSaidaCompressor": inspecao.pressaoSaidaCompressor,
            "temperaturaPontoOrvalho": inspecao.temperaturaPontoOrvalho,
            "dreno": inspecao.dreno,
            "limpeza": inspecao.limpeza,
            "observacao": inspecao.observacao,
            "defeito": listaDefeitos
        }), 200
    return jsonify({'mensagem':'Inspecao não encontrada'}), 404


@app.route('/maquina/<id>/inspecoes', methods=['GET'])
def consulta_maquina_inspecoes(id):
    logging.info(f'Iniciando consulta da Maquina da Empresa ID: {id}.')
    inspecoes = Inspecao.query.filter_by(maquinaId=id)
    resultado = []
    for inspecao in inspecoes:
        defeitos = Defeitos.query.filter_by(inspecaoId=inspecao.id)
        listaDefeitos = []
        if defeitos:
            for defeito in defeitos:
                listaDefeitos.append({
                    'id': defeito.id,
                    'status': defeito.status,
                    'desvioAnomalia': defeito.desvioAnomalia,
                    'causaAnomalia': defeito.causaAnomalia,
                    'acaoCorretiva': defeito.acaoCorretiva,
                    'responsavel': defeito.responsavel
                })
        else:
            logging.info(f'Nao existem defeitos para essa inspecao')

        resultado.append({
            "id": inspecao.id,
            "maquinaId": inspecao.maquinaId,
            "usuarioId": inspecao.usuarioId,
            "dataInspecao": inspecao.dataInspecao.strftime('%d/%m/%Y'),
            "horasDeOperacao": inspecao.horasDeOperacao,
            "horasEmCarga": inspecao.horasEmCarga,
            "temperaturaOleo": inspecao.temperaturaOleo,
            "pressaoOleo": inspecao.pressaoOleo,
            "pressaoFiltroAr": inspecao.pressaoFiltroAr,
            "temperaturaSaidaAr": inspecao.temperaturaSaidaAr,
            "temperaturaEntradaAgua": inspecao.temperaturaEntradaAgua,
            "temperaturaSaidaAgua": inspecao.temperaturaSaidaAgua,
            "pressaoSeparadorArOleo": inspecao.pressaoSeparadorArOleo,
            "pressaoSaidaCompressor": inspecao.pressaoSaidaCompressor,
            "temperaturaPontoOrvalho": inspecao.temperaturaPontoOrvalho,
            "dreno": inspecao.dreno,
            "limpeza": inspecao.limpeza,
            "observacao": inspecao.observacao,
            "defeito": listaDefeitos
        })
    return jsonify(resultado), 200


@app.route('/maquina/inspecao/<id>', methods=['PUT'])
def atualizar_inspecao(id):
    logging.info(f'Iniciando atualizacao da Inspecao ID: {id}.')
    inspecao = Inspecao.query.get(id)
    if inspecao:
        data = request.get_json()

        inspecao.maquinaId = data.get('maquinaId', inspecao.maquinaId)
        inspecao.usuarioId = data.get('usuarioId', inspecao.usuarioId)
        inspecao.dataInspecao = data.get('dataInspecao', inspecao.dataInspecao)
        inspecao.horasDeOperacao = data.get('horasDeOperacao', inspecao.horasDeOperacao)
        inspecao.horasEmCarga = data.get('horasEmCarga', inspecao.horasEmCarga)
        inspecao.temperaturaOleo = data.get('temperaturaOleo', inspecao.temperaturaOleo)
        inspecao.pressaoOleo = data.get('pressaoOleo', inspecao.pressaoOleo)
        inspecao.pressaoFiltroAr = data.get('pressaoFiltroAr', inspecao.pressaoFiltroAr)
        inspecao.temperaturaSaidaAr = data.get('temperaturaSaidaAr', inspecao.temperaturaSaidaAr)
        inspecao.temperaturaEntradaAgua = data.get('temperaturaEntradaAgua', inspecao.temperaturaEntradaAgua)
        inspecao.temperaturaSaidaAgua = data.get('temperaturaSaidaAgua', inspecao.temperaturaSaidaAgua)
        inspecao.pressaoSeparadorArOleo = data.get('pressaoSeparadorArOleo', inspecao.pressaoSeparadorArOleo)
        inspecao.pressaoSaidaCompressor = data.get('pressaoSaidaCompressor', inspecao.pressaoSaidaCompressor)
        inspecao.temperaturaPontoOrvalho = data.get('temperaturaPontoOrvalho', inspecao.temperaturaPontoOrvalho)
        inspecao.dreno = data.get('dreno', inspecao.dreno)
        inspecao.limpeza = data.get('limpeza', inspecao.limpeza)
        inspecao.status = data.get('status', inspecao.status)
        inspecao.desvioAnomalia = data.get('desvioAnomalia', inspecao.desvioAnomalia)
        inspecao.causaAnomalia = data.get('causaAnomalia', inspecao.causaAnomalia)
        inspecao.acaoCorretiva = data.get('acaoCorretiva', inspecao.acaoCorretiva)
        inspecao.responsave = data.get('responsave', inspecao.responsave)
        db.session.commit()
        return jsonify({'mensagem':'Inspecao atualizada com sucesso!'}), 200
    
    return jsonify({'mensagem':'Inspecao não encontrada'}), 404

@app.route('/maquina/inspecao/<id>', methods=['DELETE'])
def deletar_inspecao(id):
    logging.info(f'Iniciando remocao da Inspecao ID: {id}.')
    inspecao = Inspecao.query.get(id)
    if inspecao:
        db.session.delete(inspecao)
        db.session.commit()
        return jsonify({'mensagem': 'Inspecao deletada com sucesso!'}), 200
    
    return jsonify({'mensagem': 'Inspecao não encontrada!'}), 404


def criar_pdf_inspecao(inspecao, maquina, nome_operador, watermark_text=None):
    """Cria um PDF formatado com os detalhes da inspeção e defeitos em tabelas."""
    logging.info('Cria um PDF formatado com os detalhes da inspeção e defeitos em tabelas')
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['h1'],
        alignment=TA_CENTER
    )

    watermark_style = ParagraphStyle(
        name='Watermark',
        fontSize=120,
        textColor=colors.grey,
        alignment=TA_LEFT,
        rotation=45 # Opcional: rotaciona a marca d'água
    )

    def add_watermark(canvas, doc, watermark_text=None):
        if watermark_text:
            canvas.saveState()
            canvas.setFillColor(colors.grey, alpha=0.7) # Defina o valor de alpha aqui (ex: 0.3 para transparente)
            canvas.setFont(watermark_style.fontName, watermark_style.fontSize)
            text_width = canvas.stringWidth(watermark_text, watermark_style.fontName, watermark_style.fontSize)
            text_height = watermark_style.fontSize
            x = (doc.width + doc.leftMargin) / 2.0
            y = (doc.height + doc.bottomMargin) / 2.0
            canvas.translate(x, y)
            canvas.rotate(watermark_style.rotation)
            canvas.drawCentredString(0, 0, watermark_text)
            canvas.restoreState()

    elements = []
    elements.append(Paragraph(f"Detalhes da Inspeção - Dia {inspecao.dataInspecao.strftime('%d/%m/%Y')}", title_style))
    elements.append(Spacer(1, 12))
    logging.info('Preenchendo dados da Tabela Inspeçao')
    # Tabela de Detalhes da Inspeção
    data_inspecao = [
        ["Campo", "Valor"],
        ["Inspeçao", inspecao.id],
        ["Modelo Máquina", maquina.modelo],
        ["Número de Série", maquina.numero_serie],
        ["Operador", nome_operador],
        ["Data da Inspeção", inspecao.dataInspecao.strftime('%d/%m/%Y')],
        ["Horas de Operação", inspecao.horasDeOperacao],
        ["Horas em Carga", inspecao.horasEmCarga],
        ["Temperatura Óleo", inspecao.temperaturaOleo],
        ["Pressão Óleo", inspecao.pressaoOleo],
        ["Pressão Filtro Ar", inspecao.pressaoFiltroAr],
        ["Temperatura Saída Ar", inspecao.temperaturaSaidaAr],
        ["Temperatura Entrada Água", inspecao.temperaturaEntradaAgua],
        ["Temperatura Saída Água", inspecao.temperaturaSaidaAgua],
        ["Pressão Separador Ar/Óleo", inspecao.pressaoSeparadorArOleo],
        ["Pressão Saída Compressor", inspecao.pressaoSaidaCompressor],
        ["Temperatura Ponto Orvalho", inspecao.temperaturaPontoOrvalho],
        ["Dreno", "Sim" if inspecao.dreno else "Não"],
        ["Limpeza", "Sim" if inspecao.limpeza else "Não"],
        ["Observaçao", inspecao.observacao if inspecao.observacao else "Nenhuma"]
    ]
    table_inspecao = Table(data_inspecao)
    table_inspecao.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
    ]))
    elements.append(table_inspecao)
    elements.append(Spacer(1, 12))
    
    defeitos = Defeitos.query.filter_by(inspecaoId=inspecao.id)
    # Tabela de Defeitos (se houver)
    if defeitos:
        logging.info(f'Preenchendo dados da Tabela Defeitos: {defeitos}')
        elements.append(Paragraph("Defeitos Encontrados:", styles['h2']))
        elements.append(Spacer(1, 5))
        data_defeitos = [
            ["Status", "Desvio/Anomalia", "Causa", "Ação Corretiva", "Responsável"]
        ]
        for defeito in defeitos:
            
            data_defeitos.append([
                defeito.status,
                defeito.desvioAnomalia,
                defeito.causaAnomalia,
                defeito.acaoCorretiva,
                defeito.responsavel
            ])

        table_defeitos = Table(data_defeitos)
        table_defeitos.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightyellow),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (2, 1), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ]))
        elements.append(table_defeitos)
    else:
        elements.append(Paragraph("Nenhum defeito encontrado nesta inspeção.", styles['normal']))

    logging.info('Tabelas e Elementos do PDF criados')
    #doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark) # Adiciona a função de marca d'água ao build

    ## Na chamada do doc.build:
    doc.build(elements, onFirstPage=lambda c, d: add_image_watermark(c, d, "F:\Projetos\Apps\Inspeçao Diaria Maquinas\logo_fertecnica.jpg"), 
              onLaterPages=lambda c, d: add_image_watermark(c, d, "F:\Projetos\Apps\Inspeçao Diaria Maquinas\logo_fertecnica.jpg"))
    buffer.seek(0)
    return buffer

def add_image_watermark(canvas, doc, image_path):
    canvas.saveState()
    img = Image(image_path, width=200, height=100) # Ajuste o tamanho conforme necessário
    img.drawOn(canvas, (doc.width - 250), (doc.height - 150)) # Ajuste a posição conforme necessário
    canvas.restoreState()

def enviar_email_inspecao(destinatario_email, nome_fantasia, pdf_buffer, titulo_email, nome_pdf):
    """Envia um email com o PDF da inspeção em anexo."""
    try:
        logging.info('Iniciando preparaçao do email')
        msg = Message(
            subject=titulo_email,
            recipients=[destinatario_email],
            body=f"""
Prezada(o) {nome_fantasia},

Informamos que uma nova inspeção foi cadastrada no sistema Fertecnica para uma de suas máquinas.

Os detalhes da inspeção estão anexos a este email em formato PDF.

Atenciosamente,
Equipe Fertecnica
"""
        )
        msg.attach(f'{nome_pdf}.pdf', 'application/pdf', pdf_buffer.read())
        mail.send(msg)
        logging.info(f'Email de nova inspeção enviado para: {destinatario_email}: {nome_pdf}')
        return True
    except Exception as e:
        logging.error(f'Erro ao enviar email da inspeção {nome_pdf} para {destinatario_email}: {e}')
        return False