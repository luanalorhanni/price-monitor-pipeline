from scraper.db import get_connection

with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO price_monitor.products (name, url, store)
            VALUES (%s, %s, %s)
            ON CONFLICT (url) DO NOTHING
            RETURNING id
            """,
            ("Water Cooler Husky Glacier HWT600PT", "https://www.kabum.com.br/produto/593863/water-cooler-husky-glacier-iluminacao-argb-240mm-amd-e-intel-preto-hwt600pt", "Kabum"),
        )
        print(cur.fetchone())
    conn.commit()