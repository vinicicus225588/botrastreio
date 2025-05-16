import os
import json
from flask import Flask, request, jsonify
from twilio.rest import Client
from datetime import datetime

ENTREGAS_PATH = "db/entregas.json"

def salvar_entrega(numero_cliente, nome_cliente):
    nova_entrega = {
        "numero": numero_cliente,
        "nome": nome_cliente,
        "data_entrega": datetime.now().isoformat(),
        "mensagem_enviada": False
    }

    # Cria o arquivo se não existir
    if not os.path.exists(ENTREGAS_PATH):
        with open(ENTREGAS_PATH, 'w') as f:
            json.dump([], f)

    # Lê, adiciona e salva a nova entrega
    with open(ENTREGAS_PATH, 'r+') as f:
        entregas = json.load(f)
        entregas.append(nova_entrega)
        f.seek(0)
        json.dump(entregas, f, indent=4)

app = Flask(__name__)

# Credenciais da Twilio via variáveis de ambiente
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_WHATSAPP_FROM = f"whatsapp:{os.environ['TWILIO_WHATSAPP_FROM'].replace('whatsapp:', '')}"
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

            # Ajustar número para o formato correto com prefixo
            if not telefone.startswith("whatsapp:"):
                telefone = f"whatsapp:{telefone}"

            # Verificar se ambos são do mesmo canal (obrigatório pela Twilio)
            if not TWILIO_WHATSAPP_FROM.startswith("whatsapp:") or not telefone.startswith("whatsapp:"):
                return jsonify({"error": "From e To devem ser do mesmo canal (WhatsApp)"}), 400

            # Definir mensagem com base no status
            link = f"https://www.melhorrastreio.com.br/rastreio/{codigo}"
            mensagem = ""

            if status == "posted":
                mensagem = f"Oi {nome}, Aqui é o Dog Nerdson teclando, 🐶 tudo bem? Só te chamei para dizer que o seu pedido foi postado e tá com cheirinho de novidade! Aqui está o link para você rastrear direitinho: {link}, qualquer coisa chame a gente!"
            elif status == "out_for_delivery":
                mensagem = f"{nome}! Seu pedido acabou de sair para entrega! 🕺 Fique de orelha em pé e interfone ligado que motô tá chegando! 🚚💨 Rastreie: {link}"
            elif status == "delivered":
                mensagem = f"{nome}, missão cumprida! 😉📦 Seu pedido foi entregue com sucesso. Esperamos que amem tanto quanto a gente amou preparar. 😊 Veja aqui: {link}"
                  # 👇 Salvar para agendamento da mensagem de avaliação
                salvar_entrega(telefone.replace("whatsapp:", ""), nome)
            elif status == "in_transit":
                mensagem = f"{nome}, seu pedido DogNerd está quase aí! 🐶 Falta pouco pra ele aparecer latindo na sua porta 🤩. Link: {link}"
            else:
                return jsonify({"status": "Evento ignorado"}), 200

            # Enviar mensagem via WhatsApp com template
            client.messages.create(
                to=telefone,
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
