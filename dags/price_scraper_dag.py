from datetime import datetime, timedelta

from airflow.sdk import dag, task


@dag(
    dag_id="price_scraper",
    start_date=datetime(2026, 9, 1),
    schedule=timedelta(hours=3),
    catchup=False,
    tags=["price-monitor"],
)
def price_scraper():

    @task
    def coletar_kabum():
        from scraper.db import listar_produtos, salvar_preco
        from scraper.kabum import scrape

        coletados = 0
        for product_id, url in listar_produtos("kabum"):
            dados = scrape(url)
            salvar_preco(product_id, dados["preco"], dados["coletado_em"])
            print(f"id={product_id} -> R$ {dados['preco']}")
            coletados += 1
        return coletados

    coletar_kabum()


price_scraper()