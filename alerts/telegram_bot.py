import os

import requests
from dotenv import load_dotenv

from alerts.queries import QUEDA_DE_PRECO
from scraper.db import get_connection

load_dotenv()


def buscar_quedas(threshold_pct):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(QUEDA_DE_PRECO, (threshold_pct,))
            return cur.fetchall()


def enviar_mensagem(texto):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    resposta = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": texto, "parse_mode": "HTML"},
        timeout=20,
    )
    resposta.raise_for_status()


def verificar_e_alertar():
    threshold = float(os.getenv("ALERT_THRESHOLD_PCT", "10"))
    quedas = buscar_quedas(threshold)

    for nome, loja, url, preco_atual, min_anterior, queda_pct in quedas:
        enviar_mensagem(
            f"📉 <b>Queda de {queda_pct}%</b>\n\n"
            f"{nome}\n"
            f"<b>R$ {preco_atual}</b> (antes R$ {min_anterior})\n"
            f"Loja: {loja}\n\n"
            f"{url}"
        )

    return len(quedas)