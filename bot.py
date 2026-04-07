import requests
import time
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL_TELEGRAM = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
API_URL = "https://api-cs.casino.org/svc-evolution-game-events/api/bacbo?page=0&size=20&sort=data.settledAt,desc"

# 🔐 HEADERS para evitar bloqueo
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

historial = []
ultimo_resultado = None
ultimo_envio = 0
ya_iniciado = False
ultimo_mensaje_detectando = 0

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
    except Exception as e:
        print("Error enviando mensaje:", e)

# ---------------- API SEGURA ----------------
def obtener():
    try:
        r = requests.get(API_URL, headers=HEADERS, timeout=10)

        if r.status_code != 200:
            print("Error API:", r.status_code)
            return []

        data = r.json()

        if "data" not in data:
            print("Formato inesperado:", data)
            return []

        return data["data"]

    except Exception as e:
        print("Error obteniendo datos:", e)
        return []

def procesar(data):
    lista = []

    for r in data:
        try:
            res = r["data"]["winner"]

            if res == "PlayerWon":
                lista.append("🔵")
            elif res == "BankerWon":
                lista.append("🔴")
            else:
                lista.append("🟡")

        except:
            continue

    return lista[::-1]

# ---------------- DETECTOR ----------------
def detectar(hist):
    filtrado = [x for x in hist if x != "🟡"]

    if len(filtrado) < 6:
        return None

    ult = filtrado[-6:]

    # 🔥 tendencia fuerte
    if ult[-1] == ult[-2] == ult[-3]:
        return ult[-1]

    # 🔥 cambio de patrón
    if ult[-3] == ult[-2] and ult[-1] != ult[-2]:
        return ult[-1]

    return None

# ---------------- MENSAJES ----------------
def msg_entrada(color):
    contra = "🔴" if color == "🔵" else "🔵"

    return f"""✅ ENTRADA CONFIRMADA ✅

🎰 Bac Bo - Evolution

🧨 INGRESAR DESPUÉS: {contra}
🔥 APOSTAR EN: {color}

🔒 Empate 10% (Opcional)
🔁 Máx 1 GALE
"""

def msg_green(color):
    return f"""🍀 GREEN 🍀

Resultado: {color} / 🟡
"""

def msg_red():
    return "❌ RED"

def msg_gale():
    return "⚠️ GALE 1"

def msg_stats():
    total = wins + losses

    if total == 0:
        return

    porcentaje = (wins / total) * 100

    enviar(f"""📊 STATS

🟢 {wins}   🔴 {losses}
🎯 {porcentaje:.2f}%
🔥 Racha: {racha}
""")

# ---------------- LOOP ----------------
en_jugada = False
senal = None
gale = 0

while True:
    try:
        if not ya_iniciado:
            enviar("🚀 BOT BAC BO PRO ACTIVADO")
            ya_iniciado = True

        data = obtener()

        if not data:
            time.sleep(5)
            continue

        historial = procesar(data)

        if not historial:
            time.sleep(5)
            continue

        ultimo = historial[-1]

        # evitar duplicados
        if ultimo == ultimo_resultado:
            time.sleep(5)
            continue

        ultimo_resultado = ultimo

        print("Historial:", historial[-10:])

        tiempo = time.time()

        # 🔎 MENSAJE DETECTANDO (cada 60s)
        if tiempo - ultimo_mensaje_detectando > 60 and not en_jugada:
            enviar("🔎 Detectando señal...")
            ultimo_mensaje_detectando = tiempo

        # 🎯 ENTRADA
        if not en_jugada:
            posible = detectar(historial)

            if posible and (tiempo - ultimo_envio > 180):
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

        # 📈 STATS cada 5
        if (wins + losses) > 0 and (wins + losses) % 5 == 0:
            msg_stats()

        time.sleep(5)

    except Exception as e:
        print("Error general:", e)
        time.sleep(10)
