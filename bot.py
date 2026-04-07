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
detectando = False


# =========================
# 📩 TELEGRAM
# =========================
def enviar_mensaje(texto):
    requests.post(URL_TELEGRAM, data={
        "chat_id": CHAT_ID,
        "text": texto
    })


# =========================
# 🧠 ANALISIS PRO (BALANCEADO)
# =========================
def analizar_pro():
    if len(historial) < 4:
        return None

    ultimos = historial[-4:]

    rojos_count = ultimos.count("🔴")
    azules_count = ultimos.count("🔵")

    # 🔥 Racha
    if ultimos[-1] == ultimos[-2] == ultimos[-3]:
        return "contrario"

    # 📈 Tendencia
    if rojos_count >= 3:
        return "rojo"

    if azules_count >= 3:
        return "azul"

    # ⚡ Alternancia (suave)
    if ultimos[-1] != ultimos[-2]:
        return "continuar"

    return None


# =========================
# 🎯 GENERAR SEÑAL
# =========================
def generar_senal_pro():
    analisis = analizar_pro()

    # fallback inteligente
    if not analisis:
        ultimos = historial[-3:]
        if ultimos.count("🔴") > ultimos.count("🔵"):
            return "🔴"
        else:
            return "🔵"

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
# ⚠️ DETECTAR OPORTUNIDAD
# =========================
def detectar_oportunidad():
    if len(historial) < 3:
        return False

    ultimos = historial[-3:]

    # 2 iguales → posible racha
    if ultimos[-1] == ultimos[-2]:
        return True

    # ruptura
    if ultimos[-3] == ultimos[-2] and ultimos[-1] != ultimos[-2]:
        return True

    return False


# =========================
# 🧾 MENSAJES (ESTILO TUYO)
# =========================
def mensaje_detectando():
    return f"""
⚠️ DETECTANDO POSIBLE OPORTUNIDAD

🎰 Juego: Bac Bo - Evolution
"""


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
                continue

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
    global senal_actual, gale_actual, detectando

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
            # 🎯 EVALUAR SEÑAL
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
            # 👀 DETECTANDO
            # =========================
            if not senal_actual and not detectando:
                if detectar_oportunidad():
                    detectando = True
                    enviar_mensaje(mensaje_detectando())

            # =========================
            # 🎯 GENERAR ENTRADA
            # =========================
            if not senal_actual:
                nueva = generar_senal_pro()

                if nueva:
                    senal_actual = nueva
                    gale_actual = 0
                    detectando = False
                    enviar_mensaje(mensaje_senal(senal_actual))

        time.sleep(5)


# =========================
# ▶️ START
# =========================
if __name__ == "__main__":
    main()
