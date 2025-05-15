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

# Rota pública para checagem
@app.route('/', methods=['GET'])
def index():
    return "DogNerd webhook está online 🐶📦", 200

# Rota de validação do webhook do Melhor Envio (agora aceita GET e POST)
@app.route("/webhook/melhorenvio", methods=["GET", "POST"])
def validar_webhook_melhorenvio():
    return jsonify({"status": "Webhook do Melhor Envio ativo"}), 200

# Webhook de rastreio (Bling ou Melhor Envio)
@app.route('/webhook/rastreio', methods=['POST'])
def webhook_rastreio():
    data = request.get_json()

    try:
        nome = data["cliente"]["nome"]
        telefone = data["cliente"]["telefone"]  # deve estar no formato +55...
        codigo_rastreio = data["pedido"]["codigo_rastreio"]

        link = f"https://www.melhorrastreio.com.br/rastreio/{codigo_rastreio}"

        message = client.messages.create(
            to=f"whatsapp:{telefone}",
            from_=TWILIO_WHATSAPP_FROM,
            content_sid=TWILIO_TEMPLATE_SID,
            content_variables=json.dumps({
                "1": nome,
                "2": link
            })
        )

        return jsonify({"status": "ok", "sid": message.sid}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
