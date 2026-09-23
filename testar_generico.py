from scraper.generico import extrair, scrape, PrecoNaoEncontrado

CASOS = {
    "json-ld": '<script type="application/ld+json">{"@type":"Product","name":"Teclado X","offers":{"price":249.9}}</script>',
    "json-ld em @graph": '<script type="application/ld+json">{"@graph":[{"@type":"BreadcrumbList"},{"@type":"Product","name":"Mouse Y","offers":{"price":"89,90"}}]}</script>',
    "open-graph": '<meta property="og:title" content="Fone W"><meta property="product:price:amount" content="159.90">',
    "microdata": '<span itemprop="name">Cadeira V</span><span itemprop="price">R$ 1.299,00</span>',
    "json quebrado + og": '<script type="application/ld+json">{ isso nao e json }</script><meta property="og:title" content="Webcam U"><meta property="og:price:amount" content="210">',
    "sem preco": "<html><title>Qualquer</title><body>nada</body></html>",
}

for nome, html in CASOS.items():
    try:
        r = extrair(html)
        print(f"{nome:22} {r['estrategia']:11} R$ {r['preco']:>8.2f}  {r['nome']}")
    except PrecoNaoEncontrado:
        print(f"{nome:22} PrecoNaoEncontrado (esperado)")

print()
print(scrape("https://www.kabum.com.br/produto/593863/water-cooler-husky-glacier-iluminacao-argb-240mm-amd-e-intel-preto-hwt600pt"))