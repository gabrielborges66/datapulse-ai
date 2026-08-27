-- 1. Top 10 produtos por receita
SELECT
    product,
    SUM(revenue) AS revenue,
    SUM(margin) AS margin,
    SUM(quantity) AS quantity
FROM sales
GROUP BY product
ORDER BY revenue DESC
LIMIT 10;

-- 2. Receita por canal
SELECT
    channel,
    SUM(revenue) AS revenue,
    COUNT(DISTINCT order_id) AS orders,
    AVG(revenue) AS average_order_value
FROM sales
GROUP BY channel
ORDER BY revenue DESC;

-- 3. Receita por região
SELECT
    region,
    SUM(revenue) AS revenue
FROM sales
GROUP BY region
ORDER BY revenue DESC;

-- 4. Margem por categoria
SELECT
    category,
    SUM(revenue) AS revenue,
    SUM(margin) AS margin,
    ROUND(SUM(margin) * 100.0 / NULLIF(SUM(revenue), 0), 2) AS margin_rate
FROM sales
GROUP BY category
ORDER BY margin DESC;

-- 5. Clientes com maior receita
SELECT
    customer_id,
    SUM(revenue) AS revenue,
    COUNT(DISTINCT order_id) AS orders
FROM sales
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 20;
