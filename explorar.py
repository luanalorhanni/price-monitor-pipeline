import requests

URL = "https://www.kabum.com.br/produto/593863/water-cooler-husky-glacier-iluminacao-argb-240mm-amd-e-intel-preto-hwt600pt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

resp = requests.get(URL, headers=HEADERS, timeout=20)
print("status:", resp.status_code)
print("tamanho:", len(resp.text))

with open("pagina.html", "w", encoding="utf-8") as f:
    f.write(resp.text)