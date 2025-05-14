import os
import json
from flask import Flask, request, jsonify
from twilio.rest import Client

app = Flask(__name__)

# Autenticação Twilio
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

# ✅ NOVO ENDPOINT para o Melhor Envio testar
@app.route("/webhook/melhorenvio", methods=["POST"])
def melhorenvio_webhook():
    return jsonify({"status": "ok"}), 200

# Rota para receber o webhook do Bling (ou do Melhor Envio depois)
@app.route("/webhook/rastreio", methods=["POST"])
def webhook_rastreio():
    data = request.get_json()

    try:
        nome = data["cliente"]["nome"]
        telefone = data["cliente"]["telefone"]
        codigo_rastreio = data["pedido"]["codigo_rastreio"]
    except KeyError:
        return jsonify({"error": "Formato de JSON inválido"}), 400

    # Link personalizado
    link = f"https://www.melhorrastreio.com.br/rastreio/{codigo_rastreio}"

    # Enviar mensagem via WhatsApp
    try:
        message = client.messages.create(
            from_="whatsapp:+553192148615",  # seu número oficial
            to=f"whatsapp:{telefone}",
            content_sid="HXb5baa88abf382bb9fbdfaef284a1408c",  # ID do seu template
            content_variables=json.dumps({
                "1": nome,
                "2": link
            })
        )
        return jsonify({"status": "Mensagem enviada", "sid": message.sid}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()
