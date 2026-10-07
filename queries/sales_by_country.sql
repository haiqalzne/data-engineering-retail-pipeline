SELECT c.country,
       SUM(f.quantity) AS units_sold,
       SUM(f.revenue_cents) AS revenue_cents
FROM fact_sales AS f
JOIN dim_customer AS c ON c.customer_id = f.customer_id
GROUP BY c.country
ORDER BY revenue_cents DESC;
