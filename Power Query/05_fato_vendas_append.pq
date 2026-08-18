// =============================================================================
// fato_ItensVenda (final) — Append de fato_Vendas_SiteProprio + fato_Vendas_Marketplace
// Técnicas: Append (Anexar Consultas), coluna personalizada, coluna condicional
// =============================================================================
let
    // Garante que as duas origens tenham exatamente as mesmas colunas, na mesma
    // ordem, antes do Append (boa prática para evitar colunas "Column1, Column2")
    ColunasPadrao = {
        "pedido_id","item_id","cliente_id","produto_id","data_pedido","uf","estado","regiao",
        "canal_venda","vendedor_id","quantidade","preco_unitario","desconto_percentual",
        "custo_unitario","status_pedido","origem_dado"
    },
    SiteProprio = Table.SelectColumns(fato_Vendas_SiteProprio, ColunasPadrao),
    Marketplace = Table.SelectColumns(fato_Vendas_Marketplace, ColunasPadrao),

    // Append (Anexar Consultas) — uma única tabela fato consolidada
    Consolidado = Table.Combine({SiteProprio, Marketplace}),

    // Coluna personalizada: receita líquida e lucro do item (grão = item)
    ColunaReceita = Table.AddColumn(Consolidado, "receita_liquida", each
        Number.Round([preco_unitario] * [quantidade] * (1 - [desconto_percentual]), 2), type number
    ),
    ColunaLucro = Table.AddColumn(ColunaReceita, "lucro", each
        Number.Round([receita_liquida] - ([custo_unitario] * [quantidade]), 2), type number
    ),

    // Coluna condicional: faixa de desconto aplicado (usada na página de Produtos)
    ColunaFaixaDesconto = Table.AddColumn(ColunaLucro, "faixa_desconto", each
        if [desconto_percentual] >= 0.15 then "Alto (≥15%)"
        else if [desconto_percentual] >= 0.05 then "Médio (5–15%)"
        else "Baixo (<5%)",
        type text
    ),

    // Remove pedidos cancelados diretamente na consulta (alternativa a filtrar
    // só no DAX) — aqui optamos por MANTER e deixar o filtro para as medidas,
    // para permitir uma futura análise de taxa de cancelamento
    TipoFinal = Table.TransformColumnTypes(ColunaFaixaDesconto, {{"data_pedido", type date}})
in
    TipoFinal
