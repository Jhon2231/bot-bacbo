import requests
import time
import os
import random

TOKEN = os.getenv("7961061028:AAGWm-kKUcGmYm5Z6K50-B1mge-yTU7642g")
CHAT_ID = os.getenv("5998657823")

URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

historial = []

# 📊 ESTADÍSTICAS
wins = 0
losses = 0
racha = 0
max_racha = 0

# ---------------- TELEGRAM ----------------
def enviar_telegram(msg):
    requests.post(URL, data={
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "HTML"
    })

# ---------------- API (SIMULADA) ----------------
def obtener_resultado():
    return random.choice(["🔵", "🔴", "🟡"])

# ---------------- DETECTOR ----------------
def detectar_senal(hist):
    if len(hist) < 4:
        return None

    # repetición
    if hist[-1] == hist[-2]:
        return hist[-1]

    # alternancia
    if hist[-1] != hist[-2] and hist[-2] != hist[-3]:
        return hist[-1]

    # rompimiento
    if hist[-3] == hist[-2] and hist[-1] != hist[-2]:
        return hist[-1]

    # extra para más actividad 😈
    if random.random() < 0.3:
        return hist[-1]

    return None

# ---------------- MENSAJES ----------------
def mensaje_detectando():
    return """⚠️ DETECTANDO OPORTUNIDAD

🎰 Bac Bo - Evolution
📊 Analizando mercado...
"""

def mensaje_entrada(color):
    contra = "🔴" if color == "🔵" else "🔵"

    return f"""✅ ENTRADA CONFIRMADA ✅

🎰 Juego: Bac Bo - Evolution

📥 ENTRAR DESPUÉS DE: {contra}
🎯 APOSTAR: {color}

🔒 PROTEGER EMPATE 10% (Opcional)

🔁 MÁXIMO 1 GALE
"""

def mensaje_green(color):
    return f"""🍀🍀🍀 GREEN!!! 🍀🍀🍀

✅ RESULTADO: {color} / 🟡

¡Hemos acertado de nuevo! 💰
"""

def mensaje_gale():
    return "⚠️ GALE 1"

def mensaje_stats():
    total = wins + losses
    if total == 0:
        return

    porcentaje = (wins / total) * 100

    enviar_telegram(f"""🚀 RESULTADOS

🟢 {wins}   🔴 {losses}

🎯 Acierto: {porcentaje:.2f}%
🔥 Racha actual: {racha}
💰 Mejor racha: {max_racha}
""")

# ---------------- LOOP ----------------
en_jugada = False
senal_actual = None
gale = 0
contador_stats = 0
contador_analisis = 0

while True:
    resultado = obtener_resultado()
    historial.append(resultado)

    print("Historial:", historial[-10:])

    # 🔥 MENSAJE DE ANALISIS
    contador_analisis += 1
    if contador_analisis >= 6 and not en_jugada:
        enviar_telegram("⚠️ Analizando mercado... esperando oportunidad perfecta")
        contador_analisis = 0

    # 🎯 DETECTAR
    if not en_jugada:
        senal = detectar_senal(historial)

        if senal:
            enviar_telegram(mensaje_detectando())
            time.sleep(1)
            enviar_telegram(mensaje_entrada(senal))

            en_jugada = True
            senal_actual = senal
            gale = 0

    # 📊 RESULTADO
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
                losses += 1
                racha = 0
                en_jugada = False

    # 📈 STATS
    contador_stats += 1
    if contador_stats >= 5:
        mensaje_stats()
        contador_stats = 0

    time.sleep(5)
