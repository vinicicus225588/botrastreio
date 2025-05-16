from datetime import datetime
from twilio.rest import Client
import os

def esta_no_horario_comercial():
    hora_atual = datetime.now().hour
    return 9 <= hora_atual < 19

def enviar_mensagem_avaliacao(numero_cliente, nome_cliente):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    from_whatsapp_number = os.environ['TWILIO_WHATSAPP_FROM']

    client = Client(account_sid, auth_token)

    mensagem = (
        f"🐾 Oi {nome_cliente}! Tudo bem? Aqui é a equipe de Experiência da DogNerd!\n\n"
        "A gente espera de coração que você e seu doguinho tenham amado os recebidos! 🐶💜 Ele ficou confortável e feliz? Conta pra gente!\n"
        "Se quiser tirar dúvidas ou compartilhar o que achou, é só responder por aqui — estamos sempre por perto.\n\n"
        "Ah! E se puder deixar uma avaliação rapidinha no link abaixo, vai ajudar muuuito outros pets a nos encontrarem também:\n"
        "👉 https://g.page/r/CUm7rdTSAHlSEBM/review\n\n"
        "Muito obrigado, viu? Nos vemos em breve! ✨🐾"
    )

    client.messages.create(
        from_=f'whatsapp:{from_whatsapp_number}',
        to=numero_cliente,
        body=mensagem
    )
