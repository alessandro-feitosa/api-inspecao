import logging
from main import mail
from flask_mail import Message


def enviar_email_para_aprovacao(destinatario_email, nome_usuario, empresa):
    """Envia um email informando que uma nova empresa foi cadastrada e precisa de aprovaçao"""
    try:
        msg = Message(
            subject='Nova Empresa Cadastrada - Pendente de Aprovação',
            recipients=[destinatario_email]
        )
        msg.body = f"""
Prezada(o) {nome_usuario},

Informamos que a empresa {empresa.razao_social}, CNPJ: {empresa.cnpj} foi cadastrada pelo App Inspeções Diárias e está pendente de aprovação.

Clique no link abaixo para aprovar essa empresa.
http://192.168.15.144:5000/empresa/pendentes

Atenciosamente,
Equipe Fertecnica
"""
        mail.send(msg)
        logging.info(f'Email para Aprovação de Empresa Pendente Enviado para {destinatario_email} com sucesso.')
        return True
    except Exception as e:
        logging.error(f'Erro ao enviar email para aprovação de empresa nova pendente para {destinatario_email}: {e}')

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