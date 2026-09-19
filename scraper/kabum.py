import json
from datetime import datetime

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Upgrade-Insecure-Requests": "1",
}


def scrape(url):
    resposta = requests.get(url, headers=HEADERS, timeout=30)
    resposta.raise_for_status()

    soup = BeautifulSoup(resposta.text, "html.parser")

    for bloco in soup.find_all("script", type="application/ld+json"):
        dados = json.loads(bloco.string)
        if dados.get("@type") == "Product":
            return {
                "nome": dados["name"],
                "preco": float(dados["offers"]["price"]),
                "coletado_em": datetime.now(),
            }

    raise ValueError(f"Preço não encontrado em {url}")