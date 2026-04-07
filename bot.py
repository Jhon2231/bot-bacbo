import requests
import time
import os

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL_TELEGRAM = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
API_URL = "https://api-cs.casino.org/svc-evolution-game-events/api/bacbo?page=0&size=20&sort=data.settledAt,desc"

historial = []
ultimo_id = None

greens = 0
rojos = 0

MAX_GALE = 1
senal_actual = None
gale_actual = 0


# =========================
# 📩 TELEGRAM
# =========================
def enviar_mensaje(texto):
    requests.post(URL_TELEGRAM, data={
        "chat_id": CHAT_ID,
        "text": texto
    })


# =========================
# 🧠 ANALISIS PRO
# =========================
def analizar_pro():
    if len(historial) < 6:
        return None

    ultimos = historial[-6:]

    rojos_count = ultimos.count("🔴")
    azules_count = ultimos.count("🔵")

    # 🚫 EVITAR CAOS (alternancia total)
    alternando = True
    for i in range(len(ultimos) - 1):
        if ultimos[i] == ultimos[i + 1]:
            alternando = False
            break

    if alternando:
        return None

    # 🔥 RACHA FUERTE
    if ultimos[-1] == ultimos[-2] == ultimos[-3]:
        return "contrario"

    # 📈 TENDENCIA
    if rojos_count >= 4:
        return "rojo"

    if azules_count >= 4:
        return "azul"

    # ⚡ RUPTURA
    if ultimos[-2] == ultimos[-3] == ultimos[-4] and ultimos[-1] != ultimos[-2]:
        return "continuar"

    return None


# =========================
# 🎯 SEÑAL
# =========================
def generar_senal_pro():
    analisis = analizar_pro()

    if not analisis:
        return None

    ultimo = historial[-1]

    if analisis == "contrario":
        return "🔵" if ultimo == "🔴" else "🔴"

    if analisis == "continuar":
        return ultimo

    if analisis == "rojo":
        return "🔴"

    if analisis == "azul":
        return "🔵"

    return None


# =========================
# 🚫 FILTRO EXTRA
# =========================
def filtro_calidad():
    if len(historial) < 6:
        return False

    ultimos = historial[-6:]

    # 3 vs 3 = inestable
    if ultimos.count("🔴") == 3 and ultimos.count("🔵") == 3:
        return False

    return True


# =========================
# 🧾 MENSAJES (TUS DISEÑOS)
# =========================
def mensaje_senal(color):
    return f"""
✅ ENTRADA CONFIRMADA ✅

🎰 Juego: Bac Bo - Evolution
💣 INGRESAR DESPUÉS: 🔵
🔥 APUESTA EN: {color}

🔒 PROTEGER EMPATE con 10% (Opcional)

🔁 MÁXIMO {MAX_GALE} GALE
"""


def mensaje_green():
    return f"""
🍀🍀🍀 GREEN!!! 🍀🍀🍀

✅ RESULTADO: COLOR 🔴/🟠

¡Hemos acertado de nuevo!
"""


def mensaje_red():
    return f"""
❌ RED ❌

Seguimos con gestión.
"""


def mensaje_stats():
    total = greens + rojos
    porcentaje = (greens / total * 100) if total > 0 else 0

    return f"""
🚀 Resultados hasta el momento:
🟢 {greens} 🔴 {rojos}

🎯 Asertividad {porcentaje:.2f}%
"""


# =========================
# 📡 API BAC BO
# =========================
def obtener_resultados():
    try:
        res = requests.get(API_URL).json()
        juegos = res["content"]

        resultados = []

        for juego in juegos:
            game_id = juego["id"]

            player = juego["data"]["playerScore"]
            banker = juego["data"]["bankerScore"]

            if player > banker:
                color = "🔵"
            elif banker > player:
                color = "🔴"
            else:
                continue  # ignorar empate

            resultados.append((game_id, color))

        return resultados[::-1]

    except Exception as e:
        print("Error API:", e)
        return []


# =========================
# 🚀 LOOP PRINCIPAL
# =========================
def main():
    global ultimo_id, historial
    global greens, rojos
    global senal_actual, gale_actual

    print("Bot PRO corriendo...")

    while True:
        resultados = obtener_resultados()

        for game_id, color in resultados:

            if game_id == ultimo_id:
                continue

            ultimo_id = game_id
            historial.append(color)

            print("Nuevo resultado:", color)

            # =========================
            # 🎯 EVALUAR SEÑAL ACTIVA
            # =========================
            if senal_actual:
                if color == senal_actual:
                    greens += 1
                    enviar_mensaje(mensaje_green())
                    enviar_mensaje(mensaje_stats())
                    senal_actual = None
                    gale_actual = 0
                else:
                    gale_actual += 1

                    if gale_actual > MAX_GALE:
                        rojos += 1
                        enviar_mensaje(mensaje_red())
                        enviar_mensaje(mensaje_stats())
                        senal_actual = None
                        gale_actual = 0

            # =========================
            # 🧠 NUEVA SEÑAL (PRO)
            # =========================
            if not senal_actual:
                if filtro_calidad():
                    nueva = generar_senal_pro()

                    if nueva:
                        senal_actual = nueva
                        enviar_mensaje(mensaje_senal(senal_actual))

        time.sleep(5)


# =========================
# ▶️ START
# =========================
if __name__ == "__main__":
    main()
