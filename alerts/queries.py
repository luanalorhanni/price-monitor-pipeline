QUEDA_DE_PRECO = """
WITH ultima AS (
    SELECT DISTINCT ON (product_id)
           product_id, price, collected_at
    FROM price_monitor.price_history
    ORDER BY product_id, collected_at DESC
),
anteriores AS (
    SELECT h.product_id, MIN(h.price) AS min_anterior
    FROM price_monitor.price_history h
    JOIN ultima u ON u.product_id = h.product_id
    WHERE h.collected_at < u.collected_at
    GROUP BY h.product_id
)
SELECT p.name,
       p.store,
       p.url,
       u.price                                         AS preco_atual,
       a.min_anterior,
       ROUND((1 - u.price / a.min_anterior) * 100, 2)   AS queda_pct
FROM price_monitor.products p
JOIN ultima     u ON u.product_id = p.id
JOIN anteriores a ON a.product_id = p.id
WHERE p.active
  AND u.price <= a.min_anterior * (1 - %s / 100.0)
"""