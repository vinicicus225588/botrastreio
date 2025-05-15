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

# Rota de validação e processamento do Melhor Envio
@app.route("/webhook/melhorenvio", methods=["GET", "POST"])
def webhook_melhorenvio():
    if request.method == "GET":
        return jsonify({"status": "Webhook do Melhor Envio ativo"}), 200

    if request.method == "POST":
        try:
            payload = request.get_json()
            if not payload:
                return jsonify({"error": "JSON vazio ou inválido"}), 400

            # Extração de dados relevantes
            pedido_id = payload.get("order", {}).get("id")
            codigo = payload.get("tracking", {}).get("code")
            status = payload.get("tracking", {}).get("status")
            cliente = payload.get("order", {}).get("customer", {})
            nome = cliente.get("name")
            telefone = cliente.get("phone")

            # Verificação básica
            if not all([codigo, status, telefone, nome]):
                return jsonify({"error": "Dados incompletos no webhook"}), 400

            # Geração do link personalizado
            link = f"https://www.melhorrastreio.com.br/rastreio/{codigo}"

            # Envio de WhatsApp com dados
            message = client.messages.create(
                to=f"whatsapp:{telefone}",
                from_=TWILIO_WHATSAPP_FROM,
                content_sid=TWILIO_TEMPLATE_SID,
                content_variables=json.dumps({
                    "1": nome,
                    "2": link
                })
            )

            return jsonify({"status": "Mensagem enviada", "sid": message.sid}), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Webhook alternativo manual (via Bling)
@app.route('/webhook/rastreio', methods=['POST'])
def webhook_rastreio():
    data = request.get_json()

    try:
        nome = data["cliente"]["nome"]
        telefone = data["cliente"]["telefone"]
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
