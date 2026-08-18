// =============================================================================
// dim_Clientes — origem: Dataset/raw/clientes_raw.csv
// Técnicas: Limpeza de texto (Trim/Clean/Proper), tratamento de datas, Merge
// =============================================================================
let
    Origem = Csv.Document(
        File.Contents("C:\Projeto\Dataset\raw\clientes_raw.csv"),
        [Delimiter=",", Columns=9, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    CabecalhoPromovido = Table.PromoteHeaders(Origem, [PromoteAllScalars=true]),
    TiposAlterados = Table.TransformColumnTypes(CabecalhoPromovido, {
        {"cliente_id", Int64.Type}, {"nome_cliente", type text}, {"email", type text},
        {"telefone", type text}, {"cidade", type text}, {"uf", type text},
        {"cep", type text}, {"data_cadastro", type date}, {"canal_aquisicao", type text}
    }),

    // Limpeza: remove espaços extras nas pontas e caracteres não imprimíveis,
    // e padroniza a capitalização (o cadastro cru vem com nomes em CAIXA ALTA
    // aleatoriamente e cidades em minúsculo aleatoriamente)
    NomeLimpo = Table.TransformColumns(TiposAlterados, {
        {"nome_cliente", each Text.Proper(Text.Trim(Text.Clean(_))), type text}
    }),
    CidadeLimpa = Table.TransformColumns(NomeLimpo, {
        {"cidade", each Text.Proper(Text.Trim(_)), type text}
    }),
    EmailPadronizado = Table.TransformColumns(CidadeLimpa, {
        {"email", each Text.Trim(Text.Lower(_)), type text}
    }),

    // Merge com dim_Estados para trazer "estado" (nome completo) e "regiao"
    // a partir da sigla (uf) — evita repetir essa lógica em toda consulta
    MergeEstados = Table.NestedJoin(
        EmailPadronizado, {"uf"}, dim_Estados, {"uf"}, "EstadosInfo", JoinKind.LeftOuter
    ),
    EstadosExpandido = Table.ExpandTableColumn(
        MergeEstados, "EstadosInfo", {"estado", "regiao"}, {"estado", "regiao"}
    ),

    // Coluna condicional: classifica o tempo de casa do cliente
    ColunaCondicional = Table.AddColumn(EstadosExpandido, "tempo_de_base", each
        let dias = Duration.Days(DateTime.LocalNow() - DateTimeZone.RemoveZone(DateTimeZone.From([data_cadastro])))
        in if dias > 365 then "Mais de 1 ano" else if dias > 180 then "6 a 12 meses" else "Menos de 6 meses",
        type text
    ),

    OrdemFinal = Table.SelectColumns(ColunaCondicional, {
        "cliente_id","nome_cliente","email","telefone","cidade","uf","cep","estado","regiao",
        "data_cadastro","canal_aquisicao","tempo_de_base"
    })
in
    OrdemFinal

// Observação: substitua o caminho em File.Contents pelo local onde os CSVs
// estiverem salvos na sua máquina. "dim_Estados" refere-se à consulta
// carregada a partir de Dataset/dim_estados.csv (mesmo padrão de importação).
