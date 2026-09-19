import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return psycopg.connect(
        host="localhost",
        port=5432,
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

def listar_produtos(store=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            if store:
                cur.execute(
                    "SELECT id, url FROM price_monitor.products "
                    "WHERE active AND store = %s",
                    (store,),
                )
            else:
                cur.execute(
                    "SELECT id, url FROM price_monitor.products WHERE active"
                )
            return cur.fetchall()


def salvar_preco(product_id, preco, coletado_em):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO price_monitor.price_history
                    (product_id, price, collected_at)
                VALUES (%s, %s, %s)
                """,
                (product_id, preco, coletado_em),
            )
        conn.commit()