-- Criação do schema principal
CREATE SCHEMA IF NOT EXISTS price_monitor;

-- Tabela de produtos monitorados
CREATE TABLE IF NOT EXISTS price_monitor.products (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(255)        NOT NULL,
    url         TEXT                NOT NULL UNIQUE,
    store       VARCHAR(50)         NOT NULL, -- 'mercadolivre' ou 'amazon'
    active      BOOLEAN             DEFAULT TRUE,
    created_at  TIMESTAMP           DEFAULT NOW()
);

-- Tabela de histórico de preços
CREATE TABLE IF NOT EXISTS price_monitor.price_history (
    id          SERIAL PRIMARY KEY,
    product_id  INT                 NOT NULL REFERENCES price_monitor.products(id),
    price       NUMERIC(10, 2)      NOT NULL,
    collected_at TIMESTAMP          DEFAULT NOW()
);

-- Index para acelerar consultas de histórico por produto
CREATE INDEX IF NOT EXISTS idx_price_history_product_id
    ON price_monitor.price_history(product_id);

CREATE INDEX IF NOT EXISTS idx_price_history_collected_at
    ON price_monitor.price_history(collected_at);

-- View auxiliar: preço atual e menor preço histórico por produto
CREATE OR REPLACE VIEW price_monitor.vw_product_prices AS
SELECT
    p.id,
    p.name,
    p.store,
    p.url,
    latest.price                            AS current_price,
    historical.min_price                    AS min_price_ever,
    historical.avg_price                    AS avg_price,
    ROUND(
        ((latest.price - historical.min_price) / historical.min_price) * 100, 2
    )                                       AS pct_above_min,
    latest.collected_at                     AS last_collected_at
FROM price_monitor.products p

JOIN LATERAL (
    SELECT price, collected_at
    FROM price_monitor.price_history
    WHERE product_id = p.id
    ORDER BY collected_at DESC
    LIMIT 1
) latest ON TRUE

JOIN LATERAL (
    SELECT
        MIN(price) AS min_price,
        AVG(price) AS avg_price
    FROM price_monitor.price_history
    WHERE product_id = p.id
) historical ON TRUE

WHERE p.active = TRUE;
