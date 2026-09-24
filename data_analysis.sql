USE ecommerce_analytics;

-- 1. Total delivered revenue
SELECT ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered';

-- 2. Monthly revenue
SELECT DATE_FORMAT(o.order_date, '%Y-%m') AS month,
       ROUND(SUM(oi.quantity * oi.unit_price),2) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY month
ORDER BY month;

-- 3. Top 10 customers
SELECT c.customer_id, c.name,
       ROUND(SUM(oi.quantity * oi.unit_price),2) AS revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id, c.name
ORDER BY revenue DESC
LIMIT 10;

-- 4. Revenue by category
SELECT p.category,
       ROUND(SUM(oi.quantity * oi.unit_price),2) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY p.category
ORDER BY revenue DESC;

-- 5. Repeat customers
SELECT customer_id, COUNT(DISTINCT order_id) AS orders
FROM orders
WHERE status = 'Delivered'
GROUP BY customer_id
HAVING COUNT(DISTINCT order_id) > 1;

-- 6. Average order value
SELECT ROUND(SUM(oi.quantity * oi.unit_price) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered';

-- 7. Cancellation and return rates
SELECT status,
       COUNT(*) AS orders,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_orders
FROM orders
GROUP BY status;

-- 8. Top products
SELECT p.product_id, p.product_name, p.category,
       SUM(oi.quantity) AS units_sold,
       ROUND(SUM(oi.quantity * oi.unit_price),2) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status = 'Delivered'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY revenue DESC
LIMIT 10;

-- 9. Revenue by city
SELECT c.city, ROUND(SUM(oi.quantity * oi.unit_price),2) AS revenue
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY c.city
ORDER BY revenue DESC;

-- 10. Customer RFM base
SELECT c.customer_id, c.name,
       DATEDIFF('2026-01-01', MAX(o.order_date)) AS recency_days,
       COUNT(DISTINCT o.order_id) AS frequency,
       ROUND(SUM(oi.quantity * oi.unit_price),2) AS monetary
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id, c.name;
