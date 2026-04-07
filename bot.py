import requests
import time
import os
import random

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

historial = []

wins = 0
losses = 0
racha = 0
max_racha = 0

ultimo_envio = 0

# ---------------- TELEGRAM ----------------
def enviar_telegram(msg):
    try:
        requests.post(URL, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except:
        print("Error enviando")

# ---------------- RESULTADOS ----------------
def obtener_resultado():
    return random.choice(["🔵", "🔴", "🟡"])

# ---------------- FILTRO INTELIGENTE ----------------
def detectar_senal(hist):
    filtrado = [x for x in hist if x != "🟡"]

    if len(filtrado) < 5:
        return None

    ult = filtrado[-5:]

    # 🔥 1. DOBLE FUERTE
    if ult[-1] == ult[-2] == ult[-3]:
        return ult[-1]

    # 🔥 2. PATRÓN ROMPIMIENTO
    if ult[-3] == ult[-2] and ult[-1] != ult[-2]:
        return ult[-1]

    # 🔥 3. ALTERNANCIA CONTROLADA
    if ult[-1] != ult[-2] and ult[-2] != ult[-3] and ult[-3] != ult[-4]:
        return ult[-1]

    return None

# ---------------- MENSAJES ----------------
def mensaje_analisis():
    return "⚠️ Analizando mercado... esperando oportunidad clara"

def mensaje_entrada(color):
    contra = "🔴" if color == "🔵" else "🔵"

    return f"""🎯 ENTRADA CONFIRMADA

🎰 Bac Bo - Evolution

📥 ENTRAR DESPUÉS DE: {contra}
🔥 APOSTAR: {color}

🛡 Proteger empate 10%
♻️ Máximo 1 GALE
"""

def mensaje_green(color):
    return f"🍀 GREEN 🍀 Resultado: {color} / 🟡"

def mensaje_red():
    return "❌ RED"

def mensaje_gale():
    return "⚠️ GALE 1"

# ---------------- LOOP ----------------
en_jugada = False
senal_actual = None
gale = 0
contador_analisis = 0

enviar_telegram("🚀 BOT VIP ACTIVO")

while True:
    resultado = obtener_resultado()
    historial.append(resultado)

    print(historial[-10:])

    # 🔍 MENSAJE DE ANALISIS CADA 1 MIN
    contador_analisis += 1
    if contador_analisis >= 6 and not en_jugada:
        enviar_telegram(mensaje_analisis())
        contador_analisis = 0

    if not en_jugada:
        senal = detectar_senal(historial)
        tiempo_actual = time.time()

        # ⏱ mínimo 3–5 minutos entre señales
        if senal and (tiempo_actual - ultimo_envio > 240):
            enviar_telegram(mensaje_entrada(senal))

            en_jugada = True
            senal_actual = senal
            gale = 0
            ultimo_envio = tiempo_actual

    else:
        if resultado == senal_actual or resultado == "🟡":
            enviar_telegram(mensaje_green(senal_actual))

            wins += 1
            racha += 1
            if racha > max_racha:
                max_racha = racha

            en_jugada = False

        else:
            gale += 1

            if gale == 1:
                enviar_telegram(mensaje_gale())
            else:
                enviar_telegram(mensaje_red())
                losses += 1
                racha = 0
                en_jugada = False

    time.sleep(10)
