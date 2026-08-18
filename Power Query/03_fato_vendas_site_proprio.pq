// =============================================================================
// fato_Vendas_SiteProprio — origem: Dataset/raw/vendas_site_proprio_raw.csv
// Técnicas: tratamento de datas (ISO), tratamento de nulos, Merge
// =============================================================================
let
    Origem = Csv.Document(
        File.Contents("C:\Projeto\Dataset\raw\vendas_site_proprio_raw.csv"),
        [Delimiter=",", Columns=13, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    CabecalhoPromovido = Table.PromoteHeaders(Origem, [PromoteAllScalars=true]),
    TiposAlterados = Table.TransformColumnTypes(CabecalhoPromovido, {
        {"pedido_id", Int64.Type}, {"item_id", Int64.Type}, {"cliente_id", Int64.Type},
        {"produto_id", Int64.Type}, {"data_pedido", type date}, {"UF_Sigla", type text},
        {"canal_venda", type text}, {"vendedor_id", Int64.Type}, {"quantidade", Int64.Type},
        {"preco_unitario", type number}, {"desconto_percentual", type number},
        {"custo_unitario", type number}, {"status_pedido", type text}
    }),

    // Tratamento de nulos: pedidos sem desconto informado = 0% (não é ausência de dado,
    // é ausência de desconto aplicado)
    DescontoTratado = Table.ReplaceValue(
        TiposAlterados, null, 0, Replacer.ReplaceValue, {"desconto_percentual"}
    ),

    // Padroniza nome da coluna de estado para o mesmo nome usado na outra origem
    RenomeadoUF = Table.RenameColumns(DescontoTratado, {{"UF_Sigla", "uf"}}),

    // Merge com dim_Estados para trazer nome do estado e região
    MergeEstados = Table.NestedJoin(
        RenomeadoUF, {"uf"}, dim_Estados, {"uf"}, "EstadosInfo", JoinKind.LeftOuter
    ),
    EstadosExpandido = Table.ExpandTableColumn(
        MergeEstados, "EstadosInfo", {"estado", "regiao"}, {"estado", "regiao"}
    ),

    // Marca a origem para rastreabilidade (útil para auditoria pós-Append)
    ColunaOrigem = Table.AddColumn(EstadosExpandido, "origem_dado", each "Site Próprio (ERP)", type text),

    FiltraConcluidos = Table.SelectRows(ColunaOrigem, each true) // mantém cancelados também; o filtro de status é feito no DAX/medida
in
    FiltraConcluidos
