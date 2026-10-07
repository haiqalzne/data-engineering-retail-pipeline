SELECT p.product_line,
       SUM(f.quantity) AS units_sold,
       SUM(f.revenue_cents) AS revenue_cents
FROM fact_sales AS f
JOIN dim_product AS p ON p.product_id = f.product_id
GROUP BY p.product_line
ORDER BY revenue_cents DESC;
