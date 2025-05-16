import json
import os
from datetime import datetime, timedelta
from utils import enviar_mensagem_avaliacao, esta_no_horario_comercial

ENTREGAS_PATH = "db/entregas.json"

def carregar_entregas():
    if not os.path.exists(ENTREGAS_PATH):
        return []
    with open(ENTREGAS_PATH, 'r') as f:
        return json.load(f)

def salvar_entregas(entregas):
    with open(ENTREGAS_PATH, 'w') as f:
        json.dump(entregas, f, indent=4)

def processar_envio_avaliacoes():
    entregas = carregar_entregas()
    alterado = False

    for entrega in entregas:
        if entrega.get("mensagem_enviada"):
            continue

        try:
            data_entrega = datetime.fromisoformat(entrega["data_entrega"])
        except Exception as e:
            print(f"Erro ao converter data: {e}")
            continue

        if datetime.now() >= data_entrega + timedelta(days=1):
            if esta_no_horario_comercial():
                try:
                    numero = f"whatsapp:{entrega['numero']}"
                    nome = entrega.get("nome", "amigo")  # fallback se não tiver nome
                    enviar_mensagem_avaliacao(numero, nome)
                    entrega["mensagem_enviada"] = True
                    alterado = True
                    print(f"Mensagem enviada para {numero}")
                except Exception as e:
                    print(f"Erro ao enviar para {entrega['numero']}: {e}")

    if alterado:
        salvar_entregas(entregas)

if __name__ == "__main__":
    processar_envio_avaliacoes()
