import requests
import time
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL_TELEGRAM = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
API_URL = "https://api-cs.casino.org/svc-evolution-game-events/api/bacbo?page=0&size=20&sort=data.settledAt,desc"

historial = []
ultimo_resultado = None
ultimo_envio = 0
ya_iniciado = False

# 📊 STATS
wins = 0
losses = 0
racha = 0

# ---------------- TELEGRAM ----------------
def enviar(msg):
    try:
        requests.post(URL_TELEGRAM, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except:
        print("Error enviando mensaje")

# ---------------- API SEGURA ----------------
def obtener():
    try:
        r = requests.get(API_URL, timeout=10)
        data = r.json()
        return data.get("data", [])
    except:
        print("Error obteniendo datos")
        return []

def procesar(data):
    lista = []
    for r in data:
        res = r["data"]["winner"]

        if res == "PlayerWon":
            lista.append("🔵")
        elif res == "BankerWon":
            lista.append("🔴")
        else:
            lista.append("🟡")

    return lista[::-1]

# ---------------- DETECTOR ----------------
def detectar(hist):
    filtrado = [x for x in hist if x != "🟡"]

    if len(filtrado) < 6:
        return None

    ult = filtrado[-6:]

    # 🔥 patrón fuerte
    if ult[-1] == ult[-2] == ult[-3]:
        return ult[-1]

    # 🔥 rompimiento
    if ult[-3] == ult[-2] and ult[-1] != ult[-2]:
        return ult[-1]

    return None

# ---------------- MENSAJES ----------------
def msg_entrada(color):
    contra = "🔴" if color == "🔵" else "🔵"

    return f"""✅ ENTRADA CONFIRMADA ✅

🎰 Juego: Bac Bo - Evolution

🧨 INGRESAR DESPUÉS: {contra}
🔥 APOSTAR EN: {color}

🔒 PROTEGER EMPATE con 10% (Opcional)

🔁 MÁXIMO 1 GALE
"""

def msg_green(color):
    return f"""🍀🍀🍀 GREEN!!! 🍀🍀🍀

✅ RESULTADO: COLOR {color} / 🟡

¡Hemos acertado de nuevo!
"""

def msg_red():
    return "❌❌❌ RED ❌❌❌"

def msg_gale():
    return "⚠️ GALE 1"

def msg_stats():
    total = wins + losses
    if total == 0:
        return

    porcentaje = (wins / total) * 100

    enviar(f"""🚀 Resultados hasta el momento:

🟢 {wins}   🔴 {losses}

🎯 Asertividad {porcentaje:.2f}%
🔥 Racha actual: {racha}
""")

# ---------------- LOOP ----------------
en_jugada = False
senal = None
gale = 0

while True:
    try:
        # 🔥 SOLO UNA VEZ
        if not ya_iniciado:
            enviar("🚀 BOT BAC BO VIP ACTIVADO")
            ya_iniciado = True

        data = obtener()
        historial = procesar(data)

        if not historial:
            time.sleep(5)
            continue

        ultimo = historial[-1]

        # 🔥 detectar solo resultado nuevo
        if ultimo == ultimo_resultado:
            time.sleep(5)
            continue

        ultimo_resultado = ultimo

        print(historial[-10:])

        tiempo = time.time()

        # 🎯 ENTRADA
        if not en_jugada:
            posible = detectar(historial)

            if posible and (tiempo - ultimo_envio > 240):
                enviar(msg_entrada(posible))

                en_jugada = True
                senal = posible
                gale = 0
                ultimo_envio = tiempo

        # 📊 RESULTADO
        else:
            if ultimo == senal or ultimo == "🟡":
                enviar(msg_green(senal))

                wins += 1
                racha += 1
                en_jugada = False

            else:
                gale += 1

                if gale == 1:
                    enviar(msg_gale())
                else:
                    enviar(msg_red())

                    losses += 1
                    racha = 0
                    en_jugada = False

        # 📈 STATS cada 5 operaciones
        if (wins + losses) > 0 and (wins + losses) % 5 == 0:
            msg_stats()

        time.sleep(5)

    except Exception as e:
        print("Error:", e)
        time.sleep(10)
