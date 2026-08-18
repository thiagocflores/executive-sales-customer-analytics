// =============================================================================
// dim_Calendario — gerada 100% via M (não depende de nenhum arquivo externo)
// Técnicas: colunas personalizadas de data, coluna condicional
// =============================================================================
let
    DataInicio = #date(2024, 1, 1),
    DataFim = #date(2025, 12, 31),
    QtdDias = Duration.Days(DataFim - DataInicio) + 1,
    ListaDatas = List.Dates(DataInicio, QtdDias, #duration(1, 0, 0, 0)),
    TabelaBase = Table.FromList(ListaDatas, Splitter.SplitByNothing(), {"data"}),
    TipoData = Table.TransformColumnTypes(TabelaBase, {{"data", type date}}),

    ColunaAno = Table.AddColumn(TipoData, "ano", each Date.Year([data]), Int64.Type),
    ColunaMes = Table.AddColumn(ColunaAno, "mes", each Date.Month([data]), Int64.Type),
    ColunaAnoMes = Table.AddColumn(ColunaMes, "ano_mes", each
        Text.From([ano]) & "-" & Text.PadStart(Text.From([mes]), 2, "0"), type text
    ),
    ColunaMesNome = Table.AddColumn(ColunaAnoMes, "mes_nome", each
        {"Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho",
         "Agosto","Setembro","Outubro","Novembro","Dezembro"}{[mes] - 1},
        type text
    ),
    ColunaTrimestre = Table.AddColumn(ColunaMesNome, "trimestre", each
        "T" & Text.From(Date.QuarterOfYear([data])), type text
    ),
    ColunaDiaSemana = Table.AddColumn(ColunaTrimestre, "dia_semana", each
        Date.DayOfWeekName([data], "pt-BR"), type text
    ),
    // Coluna condicional: sinaliza fim de semana (usada para excluir/analisar
    // padrão de compra fora do horário comercial)
    ColunaFimDeSemana = Table.AddColumn(ColunaDiaSemana, "fim_de_semana", each
        Date.DayOfWeek([data], Day.Monday) >= 5, type logical
    )
in
    ColunaFimDeSemana
