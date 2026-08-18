# Modelo de Dados — Star Schema

## Tabelas

| Tabela | Grão | Origem (Power Query) |
|---|---|---|
| `fato_ItensVenda` | 1 linha por item de pedido | `05_fato_vendas_append.pq` |
| `fato_Metas` | 1 linha por mês | `Dataset/fato_metas.csv` (import direto) |
| `dim_Clientes` | 1 linha por cliente | `01_dim_clientes.pq` |
| `dim_Produtos` | 1 linha por produto | `02_dim_produtos.pq` |
| `dim_Estados` | 1 linha por UF | `Dataset/dim_estados.csv` (import direto) |
| `dim_Vendedores` | 1 linha por vendedor | `Dataset/dim_vendedores.csv` (import direto) |
| `dim_Calendario` | 1 linha por dia (2024-01-01 a 2025-12-31) | `06_dim_calendario.pq` |

## Decisão de modelagem: por que a fato ficou "achatada"?

No banco SQL (camada de origem), os pedidos ficam normalizados em
`dim_pedidos` (grão = pedido) + `fato_itens_venda` (grão = item), separando
atributos do pedido (cliente, canal, UF, vendedor, status) dos atributos do
item (produto, quantidade, preço, desconto).

No Power Query, optamos por **achatar** esses atributos diretamente na
tabela fato final (`fato_ItensVenda` já traz `cliente_id`, `uf`, `canal_venda`,
`vendedor_id`, `status_pedido`, `data_pedido`). Isso simplifica o modelo do
Power BI (menos uma tabela para relacionar) e é o padrão mais comum em
modelos de BI voltados a analytics — a normalização "de livro-texto" faz
mais sentido na camada transacional (SQL) do que na camada analítica.

## Relacionamentos

```
dim_Calendario (1)  ────────< fato_ItensVenda (*)      via data (data_pedido)
dim_Clientes   (1)  ────────< fato_ItensVenda (*)      via cliente_id
dim_Produtos   (1)  ────────< fato_ItensVenda (*)      via produto_id
dim_Estados    (1)  ────────< fato_ItensVenda (*)      via uf
dim_Vendedores (1)  ────────< fato_ItensVenda (*)      via vendedor_id
fato_Metas     (1)  ─ ⇄ ────< dim_Calendario  (*)      via ano_mes  (⚠ ver nota abaixo)
```

Todas unidirecionais (filtro de "1" para "muitos"), **exceto** a relação
`fato_Metas` ↔ `dim_Calendario`, que precisa ser **bidirecional**: como
`fato_Metas` está no grão mês (não no grão dia), o lado "1" da relação é a
própria `fato_Metas`, e não a `dim_Calendario`. Sem o cross-filter
bidirecional, um slicer de mês colocado na `dim_Calendario` não conseguiria
filtrar a meta. Essa é uma decisão consciente e documentada — em modelos
maiores, o ideal seria criar uma `dim_Mes` própria para evitar relações
bidirecionais, mas para este projeto o impacto de performance é irrelevante.

## Tabela de medidas

Todas as medidas DAX (arquivos `01_*.dax` a `07_*.dax`) foram criadas dentro
de uma tabela auxiliar vazia chamada **`_Medidas`** (boa prática: mantém as
medidas organizadas fora das tabelas de dados, facilitando a navegação no
painel de campos).
