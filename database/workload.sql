-- =========================================================
-- INTELLIGENT SQL QUERY PROFILER
-- OFFICIAL BASELINE WORKLOAD
-- =========================================================


-- Q001: Equality filter on foreign-key column
SELECT *
FROM orders
WHERE customer_id = 845;


-- Q002: Equality filter on status
SELECT *
FROM orders
WHERE status = 'Completed';


-- Q003: Recent date range
SELECT *
FROM orders
WHERE order_date >= (
    SELECT MAX(order_date) - INTERVAL '30 days'
    FROM orders
);


-- Q004: Multiple predicates
SELECT *
FROM orders
WHERE customer_id = 845
  AND status = 'Completed';


-- Q005: Date + amount range
SELECT *
FROM orders
WHERE order_date >= (
    SELECT MAX(order_date) - INTERVAL '90 days'
    FROM orders
)
AND total_amount > 1000;


-- Q006: Customer / Order JOIN
SELECT
    o.order_id,
    c.name,
    c.city,
    o.total_amount
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
WHERE c.city = 'Mumbai';


-- Q007: Product category filter
SELECT *
FROM products
WHERE category_id = 1;


-- Q008: Product price range
SELECT *
FROM products
WHERE price BETWEEN 1000 AND 3000;


-- Q009: Order Items / Products JOIN
SELECT
    oi.order_id,
    p.product_name,
    oi.quantity,
    oi.unit_price
FROM order_items oi
JOIN products p
    ON oi.product_id = p.product_id
WHERE p.category_id = 1;


-- Q010: ORDER BY + LIMIT
SELECT *
FROM orders
ORDER BY order_date DESC
LIMIT 20;


-- Q011: GROUP BY customer
SELECT
    customer_id,
    COUNT(*) AS order_count
FROM orders
GROUP BY customer_id;


-- Q012: GROUP BY + status filter
SELECT
    customer_id,
    SUM(total_amount) AS total_spent
FROM orders
WHERE status = 'Completed'
GROUP BY customer_id;


-- Q013: Payment status filter
SELECT *
FROM payments
WHERE status = 'Successful';


-- Q014: Shipment status filter
SELECT *
FROM shipments
WHERE delivery_status = 'In Transit';


-- Q015: Customer segment + Order JOIN
SELECT
    c.customer_id,
    c.name,
    COUNT(o.order_id) AS number_of_orders,
    SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o
    ON c.customer_id = o.customer_id
WHERE c.segment = 'Corporate'
GROUP BY
    c.customer_id,
    c.name
ORDER BY total_spent DESC
LIMIT 20;
