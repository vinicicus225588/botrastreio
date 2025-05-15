import os
import json
from flask import Flask, request, jsonify
from twilio.rest import Client

app = Flask(__name__)

# Credenciais da Twilio via variáveis de ambiente
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_WHATSAPP_FROM = os.environ['TWILIO_WHATSAPP_FROM']
TWILIO_TEMPLATE_SID = os.environ['TWILIO_TEMPLATE_SID']

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Rota de verificação simples
@app.route('/', methods=['GET'])
def index():
    return "DogNerd webhook está online 🐶📦", 200

# Webhook principal do Melhor Envio
@app.route("/webhook/melhorenvio", methods=["GET", "POST"])
def webhook_melhorenvio():
    if request.method == "GET":
        return jsonify({"status": "Webhook do Melhor Envio ativo"}), 200

    if request.method == "POST":
        try:
            payload = request.get_json()

            # Extrair dados importantes
            codigo = payload.get("tracking", {}).get("code")
            status = payload.get("tracking", {}).get("status")
            cliente = payload.get("order", {}).get("customer", {})
            nome = cliente.get("name")
            telefone = cliente.get("phone")

            # Verificar se temos os dados essenciais
            if not all([codigo, status, nome, telefone]):
                return jsonify({"error": "Dados incompletos"}), 400

            # Definir mensagem com base no status
            link = f"https://www.melhorrastreio.com.br/rastreio/{codigo}"
            mensagem = ""

            if status == "posted":
                mensagem = f"Oi {nome}, Aqui é o Dog Nerdson teclando, 🐶 tudo bem? Só te chamei para dizer que o seu pedido foi postado e tá com cheirinho de novidade! Aqui está o link para você rastrear direitinho: {link}, qualquer coisa chame a gente! "
            elif status == "out_for_delivery":
                mensagem = f"{nome}! Seu pedido acabou de sair para entrega! 🕺 Fique de orelha em pé e interfone ligado que motô tá chegando! 🚚💨 Rastreie: {link}"
            elif status == "delivered":
                mensagem = f"{nome}, missão cumprida! 😉📦 Seu pedido foi entregue com sucesso. Esperamos que amem tanto quanto a gente amou preparar. 😊 Veja aqui: {link}"
            elif status == "in_transit":
                # Aqui, como não temos a cidade no payload, você pode adicionar lógica extra se quiser
                mensagem = f"{nome}, seu pedido DogNerd está quase aí! 🐶 Falta pouco pra ele aparecer latindo na sua porta 🤩. Link: {link}"
            else:
                return jsonify({"status": "Evento ignorado"}), 200  # Não envia para outros eventos

            # Enviar mensagem via WhatsApp
            client.messages.create(
                to=f"whatsapp:{telefone}",
                from_=TWILIO_WHATSAPP_FROM,
                content_sid=TWILIO_TEMPLATE_SID,
                content_variables=json.dumps({
                    "1": nome,
                    "2": link,
                    "3": mensagem
                })
            )

            return jsonify({"status": f"Mensagem enviada para status: {status}"}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
