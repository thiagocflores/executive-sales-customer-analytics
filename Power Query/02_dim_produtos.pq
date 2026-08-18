// =============================================================================
// dim_Produtos — origem: Dataset/raw/produtos_raw.csv
// Técnicas: tratamento de nulos, limpeza de texto, coluna condicional,
//           coluna personalizada (calculada)
// =============================================================================
let
    Origem = Csv.Document(
        File.Contents("C:\Projeto\Dataset\raw\produtos_raw.csv"),
        [Delimiter=",", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    CabecalhoPromovido = Table.PromoteHeaders(Origem, [PromoteAllScalars=true]),
    TiposAlterados = Table.TransformColumnTypes(CabecalhoPromovido, {
        {"produto_id", Int64.Type}, {"nome_produto", type text}, {"categoria", type text},
        {"subcategoria", type text}, {"preco_custo", type number}, {"preco_lista", type number}
    }),

    // Limpeza: remove espaços duplicados dentro do nome do produto
    // (troca 2+ espaços por 1 único espaço)
    NomeLimpo = Table.TransformColumns(TiposAlterados, {
        {"nome_produto", each Text.Combine(List.Select(Text.Split(_, " "), each _ <> ""), " "), type text}
    }),

    // Correção manual, um por um: só 3 produtos ficaram sem subcategoria no
    // cadastro original (produto_id 3, 31 e 52) — em vez de um rótulo
    // genérico, aqui é atribuído o valor correto de cada um, na mão,
    // porque dá pra saber pelo nome do produto qual é a subcategoria certa
    SubcategoriaTratada = Table.AddColumn(NomeLimpo, "subcategoria_corrigida", each
        if [produto_id] = 3 then "Áudio"                    // Fone com Fio Preto
        else if [produto_id] = 31 then "Cozinha"             // Conjunto de Facas
        else if [produto_id] = 52 then "Outdoor"             // Mochila Impermeável Azul
        else [subcategoria]
    ),
    RemoverSubcategoriaAntiga = Table.RemoveColumns(SubcategoriaTratada, {"subcategoria"}),
    SubcategoriaTratadaFinal = Table.RenameColumns(RemoverSubcategoriaAntiga, {{"subcategoria_corrigida", "subcategoria"}}),

    // Coluna personalizada: margem estimada em % (preço lista vs. custo)
    ColunaMargem = Table.AddColumn(SubcategoriaTratadaFinal, "margem_estimada_pct", each
        Number.Round(([preco_lista] - [preco_custo]) / [preco_lista] * 100, 1), type number
    ),

    // Coluna condicional: faixa de preço, usada para filtros rápidos no relatório
    ColunaFaixaPreco = Table.AddColumn(ColunaMargem, "faixa_preco", each
        if [preco_lista] < 60 then "Até R$ 60"
        else if [preco_lista] < 150 then "R$ 60 a R$ 150"
        else "Acima de R$ 150",
        type text
    ),

    // Coluna condicional: sinaliza produtos de margem crítica (< 15%) —
    // alimenta diretamente a página de Insights ("produtos que vendem muito
    // e lucram pouco")
    ColunaAlertaMargem = Table.AddColumn(ColunaFaixaPreco, "alerta_margem_baixa", each
        if [margem_estimada_pct] < 15 then "⚠ Margem crítica" else "OK",
        type text
    )
in
    ColunaAlertaMargem
