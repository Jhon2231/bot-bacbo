import requests
import time
import os
import random

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = f"https://api.telegram.org/bot{TOKEN}"

historial = []

ultimo_envio = 0

# ---------------- TELEGRAM ----------------
def enviar_telegram(msg):
    r = requests.post(f"{URL}/sendMessage", data={
        "chat_id": CHAT_ID,
        "text": msg
    })
    return r.json()

def borrar_mensaje(message_id):
    requests.post(f"{URL}/deleteMessage", data={
        "chat_id": CHAT_ID,
        "message_id": message_id
    })

# ---------------- RESULTADOS ----------------
def obtener_resultado():
    return random.choice(["🔵", "🔴", "🟡"])

# ---------------- DETECTOR ----------------
def detectar_pre_senal(hist):
    filtrado = [x for x in hist if x != "🟡"]

    if len(filtrado) < 4:
        return None

    # posible patrón
    if filtrado[-1] == filtrado[-2]:
        return filtrado[-1]

    return None

def confirmar_senal(hist, color):
    filtrado = [x for x in hist if x != "🟡"]

    if len(filtrado) < 5:
        return False

    # confirmación fuerte
    if filtrado[-1] == color:
        return True

    return False

# ---------------- MENSAJES ----------------
def msg_detectando():
    return "⚠️ Detectando oportunidad..."

def msg_entrada(color):
    contra = "🔴" if color == "🔵" else "🔵"
    return f"""🎯 ENTRADA CONFIRMADA

🎰 Bac Bo

📥 Entrar después de: {contra}
🔥 Apostar: {color}

🛡 Proteger empate
♻️ 1 gale
"""

# ---------------- LOOP ----------------
en_jugada = False
pre_senal = None
msg_id = None

while True:
    resultado = obtener_resultado()
    historial.append(resultado)

    print(historial[-10:])

    if not en_jugada:

        # detectar posible señal
        posible = detectar_pre_senal(historial)

        if posible and not pre_senal:
            res = enviar_telegram(msg_detectando())
            msg_id = res["result"]["message_id"]
            pre_senal = posible

        # confirmar señal
        if pre_senal:
            if confirmar_senal(historial, pre_senal):
                enviar_telegram(msg_entrada(pre_senal))
                en_jugada = True
                pre_senal = None

            else:
                # si ya pasaron ciclos y no confirma → borrar
                if len(historial) > 6:
                    borrar_mensaje(msg_id)
                    pre_senal = None

    else:
        # simulación resultado
        if resultado == pre_senal or resultado == "🟡":
            enviar_telegram("🍀 GREEN")
            en_jugada = False
        else:
            enviar_telegram("❌ RED")
            en_jugada = False

    time.sleep(10)
