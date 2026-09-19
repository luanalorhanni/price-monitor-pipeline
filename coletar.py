from scraper.db import listar_produtos, salvar_preco
from scraper.kabum import scrape

for product_id, url in listar_produtos("kabum"):
    dados = scrape(url)
    salvar_preco(product_id, dados["preco"], dados["coletado_em"])
    print(f"[ok] id={product_id} R$ {dados['preco']} - {dados['nome'][:45]}")