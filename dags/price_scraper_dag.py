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
    def coletar_precos():
        from scraper.coletor import coletar
        from scraper.db import listar_produtos, salvar_preco

        sucessos, falhas = 0, []

        for product_id, url, loja in listar_produtos():
            try:
                dados = coletar(url, loja)
                salvar_preco(product_id, dados["preco"], dados["coletado_em"])
                print(f"ok    id={product_id} {loja} R$ {dados['preco']} via {dados['estrategia']}")
                sucessos += 1
            except Exception as erro:
                falhas.append(product_id)
                print(f"FALHA id={product_id} {url} -> {type(erro).__name__}: {erro}")

        print(f"resumo: {sucessos} sucesso(s), {len(falhas)} falha(s) {falhas}")

        if falhas and sucessos == 0:
            raise RuntimeError("todas as coletas falharam")

        return sucessos

    @task
    def alertar():
        from alerts.telegram_bot import verificar_e_alertar

        enviados = verificar_e_alertar()
        print(f"alertas enviados: {enviados}")
        return enviados

    coletar_precos() >> alertar()


price_scraper()