-- =============================================================================
-- Executive Sales & Customer Analytics — Queries Analíticas (SQLite)
-- Organizado pelas mesmas páginas do dashboard no Power BI.
-- Todas partem de fato_itens_venda (grão = item), considerando apenas
-- pedidos com status_pedido = 'Concluído' (pedidos cancelados são excluídos
-- da receita/lucro, mas poderiam ser analisados à parte para taxa de cancelamento).
-- =============================================================================

-- -----------------------------------------------------------------------------
-- VIEW BASE: uma linha por item de venda, já com receita/custo/lucro calculados
-- -----------------------------------------------------------------------------
DROP VIEW IF EXISTS vw_vendas;
CREATE VIEW vw_vendas AS
SELECT
    f.item_id,
    f.pedido_id,
    p.cliente_id,
    p.data_pedido,
    c.ano_mes,
    c.ano,
    c.mes,
    c.mes_nome,
    p.canal_venda,
    p.uf,
    p.estado,
    p.regiao,
    p.vendedor_id,
    v.nome_vendedor,
    v.time_comercial,
    p.status_pedido,
    f.produto_id,
    pr.nome_produto,
    pr.categoria,
    pr.subcategoria,
    pr.perfil_margem,
    f.quantidade,
    f.preco_unitario,
    f.desconto_percentual,
    f.custo_unitario,
    ROUND(f.preco_unitario * f.quantidade * (1 - f.desconto_percentual), 2) AS receita_liquida,
    ROUND(f.custo_unitario * f.quantidade, 2)                               AS custo_total,
    ROUND(f.preco_unitario * f.quantidade * (1 - f.desconto_percentual)
          - f.custo_unitario * f.quantidade, 2)                             AS lucro
FROM fato_itens_venda f
JOIN dim_pedidos   p  ON f.pedido_id = p.pedido_id
JOIN dim_produtos  pr ON f.produto_id = pr.produto_id
JOIN dim_calendario c ON date(p.data_pedido) = date(c.data)
LEFT JOIN dim_vendedores v ON p.vendedor_id = v.vendedor_id
WHERE p.status_pedido = 'Concluído';


-- =============================================================================
-- PÁGINA 1 — VISÃO EXECUTIVA
-- =============================================================================

-- KPIs gerais (receita, lucro, margem, ticket médio, nº pedidos, nº clientes)
SELECT
    ROUND(SUM(receita_liquida), 2)                         AS receita_total,
    ROUND(SUM(lucro), 2)                                   AS lucro_total,
    ROUND(SUM(lucro) * 100.0 / SUM(receita_liquida), 2)    AS margem_pct,
    COUNT(DISTINCT pedido_id)                              AS numero_pedidos,
    ROUND(SUM(receita_liquida) / COUNT(DISTINCT pedido_id), 2) AS ticket_medio,
    COUNT(DISTINCT cliente_id)                             AS numero_clientes
FROM vw_vendas;

-- Receita e lucro por mês
SELECT
    ano_mes,
    ROUND(SUM(receita_liquida), 2) AS receita,
    ROUND(SUM(lucro), 2)           AS lucro,
    ROUND(SUM(lucro) * 100.0 / SUM(receita_liquida), 2) AS margem_pct
FROM vw_vendas
GROUP BY ano_mes
ORDER BY ano_mes;

-- Receita acumulada (running total) por mês
WITH receita_mes AS (
    SELECT ano_mes, SUM(receita_liquida) AS receita
    FROM vw_vendas GROUP BY ano_mes
)
SELECT
    ano_mes,
    receita,
    SUM(receita) OVER (ORDER BY ano_mes) AS receita_acumulada
FROM receita_mes
ORDER BY ano_mes;

-- Meta x Realizado por mês
SELECT
    m.ano_mes,
    m.meta_receita,
    ROUND(COALESCE(r.receita, 0), 2) AS receita_realizada,
    ROUND(COALESCE(r.receita, 0) - m.meta_receita, 2) AS gap_absoluto,
    ROUND((COALESCE(r.receita, 0) / m.meta_receita - 1) * 100, 1) AS gap_pct
FROM fato_metas m
LEFT JOIN (
    SELECT ano_mes, SUM(receita_liquida) AS receita
    FROM vw_vendas GROUP BY ano_mes
) r ON m.ano_mes = r.ano_mes
ORDER BY m.ano_mes;


-- =============================================================================
-- PÁGINA 2 — CLIENTES
-- =============================================================================

-- Classificar cada cliente como Novo x Recorrente (mais de 1 pedido concluído)
WITH pedidos_cliente AS (
    SELECT cliente_id, COUNT(DISTINCT pedido_id) AS n_pedidos
    FROM vw_vendas GROUP BY cliente_id
)
SELECT
    CASE WHEN n_pedidos > 1 THEN 'Recorrente' ELSE 'Novo' END AS segmento,
    COUNT(*) AS qtd_clientes
FROM pedidos_cliente
GROUP BY segmento;

-- Ticket médio por segmento (Novo x Recorrente) — comprova o insight do ticket 35% maior
WITH pedidos_cliente AS (
    SELECT cliente_id, COUNT(DISTINCT pedido_id) AS n_pedidos
    FROM vw_vendas GROUP BY cliente_id
),
ticket_pedido AS (
    SELECT v.pedido_id, v.cliente_id, SUM(v.receita_liquida) AS receita_pedido
    FROM vw_vendas v GROUP BY v.pedido_id, v.cliente_id
)
SELECT
    CASE WHEN pc.n_pedidos > 1 THEN 'Recorrente' ELSE 'Novo' END AS segmento,
    ROUND(AVG(tp.receita_pedido), 2) AS ticket_medio
FROM ticket_pedido tp
JOIN pedidos_cliente pc ON tp.cliente_id = pc.cliente_id
GROUP BY segmento;

-- Ticket médio por cliente (top clientes por ticket médio)
SELECT
    cliente_id,
    COUNT(DISTINCT pedido_id) AS n_pedidos,
    ROUND(SUM(receita_liquida), 2) AS receita_total,
    ROUND(SUM(receita_liquida) / COUNT(DISTINCT pedido_id), 2) AS ticket_medio
FROM vw_vendas
GROUP BY cliente_id
ORDER BY ticket_medio DESC
LIMIT 20;

-- Curva ABC de clientes (classe A = geram até 80% da receita acumulada,
-- B = até 95%, C = restante)
WITH receita_cliente AS (
    SELECT cliente_id, SUM(receita_liquida) AS receita
    FROM vw_vendas GROUP BY cliente_id
),
ranked AS (
    SELECT
        cliente_id, receita,
        SUM(receita) OVER (ORDER BY receita DESC) AS receita_acumulada,
        SUM(receita) OVER ()                       AS receita_total
    FROM receita_cliente
)
SELECT
    cliente_id,
    receita,
    ROUND(receita_acumulada * 100.0 / receita_total, 2) AS pct_acumulado,
    CASE
        WHEN receita_acumulada * 1.0 / receita_total <= 0.80 THEN 'A'
        WHEN receita_acumulada * 1.0 / receita_total <= 0.95 THEN 'B'
        ELSE 'C'
    END AS classe_abc
FROM ranked
ORDER BY receita DESC;

-- Top 20 clientes por receita (com classificação VIP: top 10% por receita)
WITH receita_cliente AS (
    SELECT cliente_id, SUM(receita_liquida) AS receita, COUNT(DISTINCT pedido_id) AS n_pedidos
    FROM vw_vendas GROUP BY cliente_id
)
SELECT
    cliente_id,
    receita,
    n_pedidos,
    NTILE(10) OVER (ORDER BY receita DESC) AS decil  -- decil 1 = top 10% (VIP)
FROM receita_cliente
ORDER BY receita DESC
LIMIT 20;


-- =============================================================================
-- PÁGINA 3 — PRODUTOS
-- =============================================================================

-- Produtos mais vendidos (quantidade)
SELECT nome_produto, categoria, SUM(quantidade) AS qtd_vendida,
       ROUND(SUM(receita_liquida), 2) AS receita
FROM vw_vendas
GROUP BY nome_produto, categoria
ORDER BY qtd_vendida DESC
LIMIT 15;

-- Produtos mais lucrativos (lucro total)
SELECT nome_produto, categoria, ROUND(SUM(lucro), 2) AS lucro_total,
       ROUND(SUM(lucro) * 100.0 / SUM(receita_liquida), 2) AS margem_pct
FROM vw_vendas
GROUP BY nome_produto, categoria
ORDER BY lucro_total DESC
LIMIT 15;

-- Produtos com maior desconto médio
SELECT nome_produto, categoria,
       ROUND(AVG(desconto_percentual) * 100, 1) AS desconto_medio_pct,
       SUM(quantidade) AS qtd_vendida
FROM vw_vendas
GROUP BY nome_produto, categoria
ORDER BY desconto_medio_pct DESC
LIMIT 15;

-- *** Insight-chave: produtos que vendem muito mas lucram pouco ***
-- (top 15 em volume, ordenados pela menor margem)
WITH top_volume AS (
    SELECT nome_produto, categoria,
           SUM(quantidade) AS qtd_vendida,
           SUM(receita_liquida) AS receita,
           SUM(lucro) AS lucro
    FROM vw_vendas
    GROUP BY nome_produto, categoria
    ORDER BY qtd_vendida DESC
    LIMIT 15
)
SELECT
    nome_produto, categoria, qtd_vendida,
    ROUND(receita, 2) AS receita,
    ROUND(lucro * 100.0 / receita, 2) AS margem_pct
FROM top_volume
ORDER BY margem_pct ASC;


-- =============================================================================
-- PÁGINA 4 — GEOGRAFIA
-- =============================================================================

-- Receita, lucro e ticket médio por estado
SELECT
    estado, uf, regiao,
    ROUND(SUM(receita_liquida), 2) AS receita,
    ROUND(SUM(lucro), 2)           AS lucro,
    ROUND(SUM(lucro) * 100.0 / SUM(receita_liquida), 2) AS margem_pct,
    COUNT(DISTINCT pedido_id)      AS n_pedidos,
    ROUND(SUM(receita_liquida) / COUNT(DISTINCT pedido_id), 2) AS ticket_medio,
    ROUND(SUM(receita_liquida) * 100.0 /
          (SELECT SUM(receita_liquida) FROM vw_vendas), 2) AS pct_receita_total
FROM vw_vendas
GROUP BY estado, uf, regiao
ORDER BY receita DESC;

-- Receita e margem por região (comparação com a média nacional)
SELECT
    regiao,
    ROUND(SUM(receita_liquida), 2) AS receita,
    ROUND(SUM(lucro) * 100.0 / SUM(receita_liquida), 2) AS margem_pct
FROM vw_vendas
GROUP BY regiao
ORDER BY receita DESC;


-- =============================================================================
-- PÁGINA 5 — COMERCIAL
-- =============================================================================

-- Ranking por categoria
SELECT categoria, ROUND(SUM(receita_liquida),2) AS receita,
       ROUND(SUM(lucro),2) AS lucro,
       ROUND(SUM(lucro)*100.0/SUM(receita_liquida),2) AS margem_pct
FROM vw_vendas GROUP BY categoria ORDER BY receita DESC;

-- Ranking por subcategoria
SELECT categoria, subcategoria, ROUND(SUM(receita_liquida),2) AS receita,
       ROUND(SUM(lucro)*100.0/SUM(receita_liquida),2) AS margem_pct
FROM vw_vendas GROUP BY categoria, subcategoria ORDER BY receita DESC;

-- Ranking por canal de venda
SELECT canal_venda, ROUND(SUM(receita_liquida),2) AS receita,
       COUNT(DISTINCT pedido_id) AS n_pedidos,
       ROUND(SUM(receita_liquida)/COUNT(DISTINCT pedido_id),2) AS ticket_medio
FROM vw_vendas GROUP BY canal_venda ORDER BY receita DESC;

-- Ranking por representante/vendedor
SELECT nome_vendedor, time_comercial,
       ROUND(SUM(receita_liquida),2) AS receita,
       ROUND(SUM(lucro),2) AS lucro,
       COUNT(DISTINCT pedido_id) AS n_pedidos
FROM vw_vendas GROUP BY nome_vendedor, time_comercial ORDER BY receita DESC;

-- Comparativo Ano Atual x Ano Anterior por mês (equivalente ao DATEADD/SAMEPERIODLASTYEAR do DAX)
SELECT
    mes, mes_nome,
    SUM(CASE WHEN ano = 2024 THEN receita_liquida ELSE 0 END) AS receita_2024,
    SUM(CASE WHEN ano = 2025 THEN receita_liquida ELSE 0 END) AS receita_2025,
    ROUND(
        (SUM(CASE WHEN ano = 2025 THEN receita_liquida ELSE 0 END)
         / NULLIF(SUM(CASE WHEN ano = 2024 THEN receita_liquida ELSE 0 END), 0) - 1) * 100, 1
    ) AS crescimento_pct
FROM vw_vendas
GROUP BY mes, mes_nome
ORDER BY mes;


-- =============================================================================
-- PÁGINA 6 — INSIGHTS (consultas de apoio para os cards de texto)
-- =============================================================================

-- Margem de SP vs margem nacional
SELECT
    (SELECT ROUND(SUM(lucro)*100.0/SUM(receita_liquida),2) FROM vw_vendas WHERE estado='São Paulo') AS margem_sp,
    (SELECT ROUND(SUM(lucro)*100.0/SUM(receita_liquida),2) FROM vw_vendas) AS margem_nacional,
    (SELECT ROUND(SUM(receita_liquida)*100.0/(SELECT SUM(receita_liquida) FROM vw_vendas),1)
       FROM vw_vendas WHERE estado='São Paulo') AS pct_receita_sp;

-- Recorrência por canal de aquisição (via clientes)
WITH pedidos_cliente AS (
    SELECT cliente_id, COUNT(DISTINCT pedido_id) AS n_pedidos FROM vw_vendas GROUP BY cliente_id
)
SELECT
    dc.canal_aquisicao,
    COUNT(*) AS n_clientes,
    ROUND(AVG(CASE WHEN pc.n_pedidos > 1 THEN 1.0 ELSE 0 END) * 100, 1) AS pct_recorrencia
FROM dim_clientes dc
JOIN pedidos_cliente pc ON dc.cliente_id = pc.cliente_id
GROUP BY dc.canal_aquisicao
ORDER BY pct_recorrencia;
