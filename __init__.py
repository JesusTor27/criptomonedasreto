import logging
import requests
import os
import azure.functions as func
from telegram import Bot

# Configuración
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)

# Variables globales para guardar último precio
last_prices = {}

# Función Azure con TimerTrigger
def main(mytimer: func.TimerRequest) -> None:
    logging.info("⏰ Ejecutando función de criptomonedas cada minuto...")

    try:
        # API pública (CoinGecko en COP)
        url = "https://api.coingecko.com/api/v3/simple/price"
        cryptos = ["bitcoin", "solana", "ripple"]  # BTC, SOL, XRP
        params = {"ids": ",".join(cryptos), "vs_currencies": "cop"}
        resp = requests.get(url, params=params)
        data = resp.json()

        mensajes = []
        for nombre, simbolo in [("bitcoin", "BTC"), ("solana", "SOL"), ("ripple", "XRP")]:
            precio = data[nombre]["cop"]

            # Variación
            tendencia = "➖ estable"
            variacion = 0
            if nombre in last_prices:
                variacion = ((precio - last_prices[nombre]) / last_prices[nombre]) * 100
                if variacion > 0.5:
                    tendencia = "⬆️ sube"
                elif variacion < -0.5:
                    tendencia = "⬇️ baja"

            # Guardamos precio actual
            last_prices[nombre] = precio

            # Armamos mensaje
            mensajes.append(f"{simbolo}: ${precio:,.0f} COP | {variacion:.2f}% | {tendencia}")

        # Enviar a Telegram
        mensaje_final = "\n".join(mensajes)
        bot.send_message(chat_id=CHAT_ID, text=f"📊 Cotizaciones Criptos:\n{mensaje_final}")

    except Exception as e:
        logging.error(f"❌ Error en la función: {e}")
