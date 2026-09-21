from scraper.db import get_connection

RESUMO = """
SELECT name, store, url, current_price, min_price_ever,
       avg_price, pct_above_min, last_collected_at
FROM price_monitor.vw_product_prices
ORDER BY name
"""


def buscar_resumo():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(RESUMO)
            colunas = [descricao[0] for descricao in cur.description]
            return [dict(zip(colunas, linha)) for linha in cur.fetchall()]