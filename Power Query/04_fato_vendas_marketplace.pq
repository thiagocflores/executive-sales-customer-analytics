// =============================================================================
// fato_Vendas_Marketplace — origem: Dataset/raw/vendas_marketplace_raw.csv
// Técnicas: tratamento de datas (formato BR dd/mm/aaaa), conversão de unidade
//           (desconto em R$ -> %), renomeação/harmonização de colunas, Merge
// =============================================================================
let
    Origem = Csv.Document(
        File.Contents("C:\Projeto\Dataset\raw\vendas_marketplace_raw.csv"),
        [Delimiter=",", Columns=13, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    CabecalhoPromovido = Table.PromoteHeaders(Origem, [PromoteAllScalars=true]),

    // A data vem como texto "dd/mm/aaaa" — não pode usar type date direto
    // (o Power Query assumiria cultura en-US e inverteria dia/mês). Usa-se
    // Date.FromText informando explicitamente a cultura pt-BR.
    DataConvertida = Table.TransformColumns(CabecalhoPromovido, {
        {"Data_Venda_BR", each Date.FromText(_, "pt-BR"), type date}
    }),

    TiposAlterados = Table.TransformColumnTypes(DataConvertida, {
        {"ID_Pedido", Int64.Type}, {"ID_Item", Int64.Type}, {"ID_Cliente", Int64.Type},
        {"ID_Produto", Int64.Type}, {"Estado_Extenso", type text}, {"Canal", type text},
        {"ID_Vendedor", Int64.Type}, {"Qtd", Int64.Type}, {"Preco_Unit", type number},
        {"Custo_Unit", type number}, {"Status", type text}, {"Desconto_Reais", type number}
    }),

    // Essa origem informa o desconto em R$ por item, não em percentual.
    // Precisamos converter para % para ficar no mesmo padrão da outra origem:
    // desconto_percentual = desconto_em_reais / (preco_unitario * quantidade)
    ColunaDescontoPct = Table.AddColumn(TiposAlterados, "desconto_percentual", each
        if [Preco_Unit] * [Qtd] = 0 then 0 else [Desconto_Reais] / ([Preco_Unit] * [Qtd]),
        type number
    ),

    // Merge com dim_Estados usando o NOME por extenso (essa origem não traz a sigla)
    MergeEstados = Table.NestedJoin(
        ColunaDescontoPct, {"Estado_Extenso"}, dim_Estados, {"estado"}, "EstadosInfo", JoinKind.LeftOuter
    ),
    EstadosExpandido = Table.ExpandTableColumn(MergeEstados, "EstadosInfo", {"uf", "regiao"}, {"uf", "regiao"}),

    // Renomeia todas as colunas para o padrão do modelo (mesmo nome da outra origem)
    Renomeado = Table.RenameColumns(EstadosExpandido, {
        {"ID_Pedido", "pedido_id"}, {"ID_Item", "item_id"}, {"ID_Cliente", "cliente_id"},
        {"ID_Produto", "produto_id"}, {"Estado_Extenso", "estado"}, {"Canal", "canal_venda"},
        {"ID_Vendedor", "vendedor_id"}, {"Qtd", "quantidade"}, {"Preco_Unit", "preco_unitario"},
        {"Custo_Unit", "custo_unitario"}, {"Status", "status_pedido"}, {"Data_Venda_BR", "data_pedido"}
    }),

    ColunaOrigem = Table.AddColumn(Renomeado, "origem_dado", each "Marketplace (planilha do parceiro)", type text),

    OrdemFinal = Table.SelectColumns(ColunaOrigem, {
        "pedido_id","item_id","cliente_id","produto_id","data_pedido","uf","estado","regiao",
        "canal_venda","vendedor_id","quantidade","preco_unitario","desconto_percentual",
        "custo_unitario","status_pedido","origem_dado"
    })
in
    OrdemFinal
