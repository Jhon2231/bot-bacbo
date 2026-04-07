import requests
import time
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

API_URL = "https://api-cs.casino.org/svc-evolution-game-events/api/bacbo?page=0&size=20&sort=data.settledAt,desc"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

ultimo_resultado = None
ultimo_envio = 0
ultimo_detectando = 0

historial = []

# STATS
wins = 0
losses = 0
racha = 0

# ---------------- TELEGRAM ----------------
def enviar(msg):
    try:
        requests.post(URL, data={
            "chat_id": CHAT_ID,
            "text": msg
        })
    except:
        print("Error telegram")

# ---------------- API ----------------
def obtener():
    try:
        r = requests.get(API_URL, headers=HEADERS, timeout=10)
        data = r.json()
        return data
    except:
        print("Error API")
        return []

def procesar(data):
    lista = []

    for r in data:
        try:
            res = r["result"]["outcome"]

            if res == "PlayerWon":
                lista.append("🔵")
            elif res == "BankerWon":
                lista.append("🔴")
            else:
                lista.append("🟡")

        except:
            continue

    return lista[::-1]

# ---------------- DETECTOR PRO ----------------
def detectar(hist):
    filtrado = [x for x in hist if x != "🟡"]

    if len(filtrado) < 8:
        return None

    ult = filtrado[-8:]

    # 🔥 tendencia fuerte (4 seguidos)
    if ult[-1] == ult[-2] == ult[-3] == ult[-4]:
        return ult[-1]

    # 🔥 patrón tipo AA BB
    if ult[-4] == ult[-3] and ult[-2] == ult[-1] and ult[-3] != ult[-2]:
        return ult[-1]

    # 🔥 rompimiento real
    if ult[-3] == ult[-2] and ult[-1] != ult[-2]:
        return ult[-1]

    return None

# ---------------- MENSAJES ----------------
def msg_detectando():
    return "🔎 Detectando señal..."

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

✅ RESULTADO: {color} / 🟡
"""

def msg_red():
    return "❌❌❌ RED ❌❌❌"

def msg_gale():
    return "⚠️ GALE 1"

# ---------------- LOOP ----------------
en_jugada = False
senal = None
gale = 0

while True:
    try:
        data = obtener()

        if not data:
            time.sleep(5)
            continue

        historial = procesar(data)

        if not historial:
            time.sleep(5)
            continue

        ultimo = historial[-1]

        if ultimo == ultimo_resultado:
            time.sleep(5)
            continue

        ultimo_resultado = ultimo

        print(historial[-10:])

        tiempo = time.time()

        # detectar (sin spam)
        if tiempo - ultimo_detectando > 60 and not en_jugada:
            enviar(msg_detectando())
            ultimo_detectando = tiempo

        # ENTRADA
        if not en_jugada:
            posible = detectar(historial)

            if posible and (tiempo - ultimo_envio > 180):
                enviar(msg_entrada(posible))

                en_jugada = True
                senal = posible
                gale = 0
                ultimo_envio = tiempo

        # RESULTADO
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

        time.sleep(5)

    except Exception as e:
        print("Error:", e)
        time.sleep(10)
