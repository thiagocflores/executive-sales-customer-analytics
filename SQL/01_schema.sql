-- =============================================================================
-- Executive Sales & Customer Analytics — Schema (SQLite)
-- Modelo dimensional (estrela): 1 tabela fato + dimensões
-- =============================================================================

DROP TABLE IF EXISTS fato_itens_venda;
DROP TABLE IF EXISTS fato_metas;
DROP TABLE IF EXISTS dim_pedidos;
DROP TABLE IF EXISTS dim_clientes;
DROP TABLE IF EXISTS dim_produtos;
DROP TABLE IF EXISTS dim_vendedores;
DROP TABLE IF EXISTS dim_estados;
DROP TABLE IF EXISTS dim_calendario;

-- Dimensão Calendário -----------------------------------------------------
CREATE TABLE dim_calendario (
    data            TEXT PRIMARY KEY,   -- YYYY-MM-DD
    ano             INTEGER NOT NULL,
    mes             INTEGER NOT NULL,
    mes_nome        TEXT NOT NULL,
    ano_mes         TEXT NOT NULL,       -- YYYY-MM
    trimestre       TEXT NOT NULL,
    dia_semana      TEXT NOT NULL,
    fim_de_semana   INTEGER NOT NULL     -- 0/1
);

-- Dimensão Estados ----------------------------------------------------------
CREATE TABLE dim_estados (
    uf      TEXT PRIMARY KEY,
    estado  TEXT NOT NULL,
    regiao  TEXT NOT NULL
);

-- Dimensão Clientes -----------------------------------------------------------
CREATE TABLE dim_clientes (
    cliente_id       INTEGER PRIMARY KEY,
    nome_cliente     TEXT NOT NULL,
    email            TEXT,
    telefone         TEXT,
    cidade           TEXT,
    uf               TEXT REFERENCES dim_estados(uf),
    cep              TEXT,
    estado           TEXT,
    regiao           TEXT,
    data_cadastro    TEXT NOT NULL,
    canal_aquisicao  TEXT NOT NULL
);

-- Dimensão Produtos -----------------------------------------------------------
CREATE TABLE dim_produtos (
    produto_id      INTEGER PRIMARY KEY,
    nome_produto    TEXT NOT NULL,
    categoria       TEXT NOT NULL,
    subcategoria    TEXT NOT NULL,
    preco_custo     REAL NOT NULL,
    preco_lista     REAL NOT NULL,
    perfil_margem   TEXT   -- atracao_flagship / atracao / regular / premium / clearance
);

-- Dimensão Vendedores / Time Comercial ----------------------------------------
CREATE TABLE dim_vendedores (
    vendedor_id     INTEGER PRIMARY KEY,
    nome_vendedor   TEXT NOT NULL,
    time_comercial  TEXT NOT NULL   -- Key Account / Marketplace / Loja Própria
);

-- Dimensão Pedidos (grão = pedido) --------------------------------------------
CREATE TABLE dim_pedidos (
    pedido_id       INTEGER PRIMARY KEY,
    cliente_id      INTEGER REFERENCES dim_clientes(cliente_id),
    data_pedido     TEXT NOT NULL,
    canal_venda     TEXT NOT NULL,     -- Site Próprio / Marketplace / Aplicativo
    uf              TEXT REFERENCES dim_estados(uf),
    estado          TEXT,
    regiao          TEXT,
    vendedor_id     INTEGER REFERENCES dim_vendedores(vendedor_id),
    status_pedido   TEXT NOT NULL      -- Concluído / Cancelado
);

-- Fato Itens de Venda (grão = item do pedido) --------------------------------
CREATE TABLE fato_itens_venda (
    item_id              INTEGER PRIMARY KEY,
    pedido_id            INTEGER REFERENCES dim_pedidos(pedido_id),
    produto_id            INTEGER REFERENCES dim_produtos(produto_id),
    quantidade            INTEGER NOT NULL,
    preco_unitario        REAL NOT NULL,
    desconto_percentual   REAL NOT NULL,
    custo_unitario        REAL NOT NULL
);

-- Fato Metas (grão = mês) -----------------------------------------------------
CREATE TABLE fato_metas (
    ano_mes        TEXT PRIMARY KEY,
    meta_receita   REAL NOT NULL
);

CREATE INDEX idx_pedidos_cliente ON dim_pedidos(cliente_id);
CREATE INDEX idx_pedidos_data ON dim_pedidos(data_pedido);
CREATE INDEX idx_itens_pedido ON fato_itens_venda(pedido_id);
CREATE INDEX idx_itens_produto ON fato_itens_venda(produto_id);

-- Observação: as tabelas já são populadas pelo script Python (gerar_dataset.py)
-- diretamente via pandas.to_sql(). Este arquivo documenta o schema equivalente
-- e serve para recriar o banco manualmente, se necessário.
