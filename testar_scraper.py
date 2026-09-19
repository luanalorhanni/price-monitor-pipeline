from scraper.kabum import scrape

URL = "https://www.kabum.com.br/produto/593863/water-cooler-husky-glacier-iluminacao-argb-240mm-amd-e-intel-preto-hwt600pt"

resultado = scrape(URL)

print("nome :", resultado["nome"])
print("preco:", resultado["preco"])
print("data :", resultado["coletado_em"])