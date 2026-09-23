from scraper.coletor import coletar
from scraper.db import get_connection, salvar_preco
from scraper.lojas import detectar_loja, normalizar

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

def cadastrar_produto(url_bruta):
    url = normalizar(url_bruta)
    loja = detectar_loja(url)

    dados = coletar(url, loja)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO price_monitor.products (name, url, store)
                VALUES (%s, %s, %s)
                ON CONFLICT (url) DO UPDATE SET active = TRUE
                RETURNING id
                """,
                (dados["nome"], url, loja),
            )
            product_id = cur.fetchone()[0]
        conn.commit()

    salvar_preco(product_id, dados["preco"], dados["coletado_em"])

    return f"Monitorando: {dados['nome']} — R$ {dados['preco']:.2f} ({loja})"