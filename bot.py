import asyncio
import requests
from telegram import Bot

TOKEN = "7961061028:AAGWm-kKUcGmYm5Z6K50-B1mge-yTU7642g"
CHAT_ID = "5998657823"

URL = "https://api-cs.casino.org/svc-evolution-game-events/api/bacbo?page=0&size=10&sort=data.settledAt,desc&duration=30&wheelResults=PlayerWon,BankerWon,Tie"

historial = []
senal_activa = None
gale = 0

# 📊 stats
greens = 0
rojas = 0
racha = 0

def convertir(resultado):
    if resultado == "PlayerWon":
        return "🔵"
    elif resultado == "BankerWon":
        return "🔴"
    elif resultado == "Tie":
        return "🟡"
    return None

def calcular_precision():
    total = greens + rojas
    if total == 0:
        return 0
    return int((greens / total) * 100)

def zona_mala(hist):
    if len(hist) >= 6:
        if hist[-6:] == ["🔵","🔴","🔵","🔴","🔵","🔴"]:
            return True
        if hist[-6:] == ["🔴","🔵","🔴","🔵","🔴","🔵"]:
            return True
    return False

async def enviar_senal(bot, color):
    texto = f"""
🧠 Analizando patrón avanzado...

🚨 SEÑAL CONFIRMADA 🚨

🎰 Bac Bo - Evolution  

👉 Espera que salga: 🔵  
🎯 Luego apuesta a: {color}  

📊 Confianza: ALTA  
🔒 Empate 10% (opcional)  
🔁 1 gale máximo  

📈 Precisión: {calcular_precision()}%  
🔥 Racha actual: {racha} greens
"""
    await bot.send_message(chat_id=CHAT_ID, text=texto)

async def enviar_green(bot, resultado):
    global greens, racha
    greens += 1
    racha += 1

    texto = f"""
🍀🍀🍀 GREEN!!! 🍀🍀🍀

🎯 RESULTADO: {resultado}

💰 Ganancia confirmada  
🔥 Seguimos sumando  

📊 Greens: {greens} | Rojas: {rojas}  
📈 Precisión: {calcular_precision()}%  
🔥 Racha: {racha}
"""
    await bot.send_message(chat_id=CHAT_ID, text=texto)

async def enviar_rojo(bot):
    global rojas, racha
    rojas += 1
    racha = 0

    texto = f"""
❌❌❌ PERDIDA ❌❌❌

📉 No se logró la entrada  
🔁 Reiniciando análisis  

📊 Greens: {greens} | Rojas: {rojas}  
📈 Precisión: {calcular_precision()}%
"""
    await bot.send_message(chat_id=CHAT_ID, text=texto)

# 🔥 NUEVA LÓGICA MEJORADA
def patron_fuerte(hist):

    # 1️⃣ RACHA
    if len(hist) >= 3:
        if hist[-3:] == ["🔴","🔴","🔴"]:
            return "🔵"
        if hist[-3:] == ["🔵","🔵","🔵"]:
            return "🔴"

    # 2️⃣ DOBLE TENDENCIA
    if len(hist) >= 4:
        if hist[-4:] == ["🔴","🔴","🔵","🔴"]:
            return "🔵"
        if hist[-4:] == ["🔵","🔵","🔴","🔵"]:
            return "🔴"

    # 3️⃣ BLOQUES
    if len(hist) >= 5:
        if hist[-5:] == ["🔴","🔴","🔵","🔵","🔴"]:
            return "🔵"
        if hist[-5:] == ["🔵","🔵","🔴","🔴","🔵"]:
            return "🔴"

    return None

async def main():
    global senal_activa, gale

    bot = Bot(token=TOKEN)

    await bot.send_message(chat_id=CHAT_ID, text="🔥 BOT PREMIUM ACTIVADO")

    while True:
        try:
            res = requests.get(URL)
            data = res.json()

            resultados = []

            for item in data:
                try:
                    r = item["data"]["result"]
                    resultado = (
                        r.get("wheelResult")
                        or r.get("winner")
                        or r.get("outcome")
                    )
                except:
                    continue

                convertido = convertir(resultado)
                if convertido:
                    resultados.append(convertido)

            if resultados:
                resultados = list(reversed(resultados))
                ultimo = resultados[-1]

                if len(historial) == 0 or historial[-1] != ultimo:
                    historial.append(ultimo)

                    print("Historial:", historial[-10:])

                    # 🚫 evitar zona mala
                    if zona_mala(historial):
                        print("Zona mala detectada ❌")
                        continue

                    # 🔥 detectar señal
                    if senal_activa is None:
                        entrada = patron_fuerte(historial)

                        if entrada:
                            senal_activa = entrada
                            gale = 0
                            await enviar_senal(bot, entrada)

                    # 🔥 resultado
                    if senal_activa:
                        if ultimo == senal_activa:
                            await enviar_green(bot, ultimo)
                            senal_activa = None
                            gale = 0

                        else:
                            if gale == 0:
                                gale = 1
                                await bot.send_message(
                                    chat_id=CHAT_ID,
                                    text="⚠️ GALE 1\n🔁 Aplicando recuperación"
                                )
                            else:
                                await enviar_rojo(bot)
                                senal_activa = None
                                gale = 0

        except Exception as e:
            print("Error:", e)

        await asyncio.sleep(5)

asyncio.run(main())