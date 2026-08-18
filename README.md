# Executive Sales & Customer Analytics

![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=flat&logo=powerbi&logoColor=black)
![DAX](https://img.shields.io/badge/DAX-0B2545?style=flat)
![Power Query](https://img.shields.io/badge/Power%20Query-M-217346?style=flat)
![SQL](https://img.shields.io/badge/SQL-SQLite-4479A1?style=flat&logo=sqlite&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)

Dashboard executivo de e-commerce construído em **Power BI**, com pipeline de
dados em **Power Query (M)**, **SQL (SQLite)** e modelagem em **DAX**.
Projeto de portfólio — dataset fictício, mas com padrões de negócio
propositalmente realistas (ver seção [Sobre os dados](#sobre-os-dados)).

> 📎 O `Dashboard.pbix` já vem pronto neste repositório. O restante dos
> arquivos (dataset, SQL, código M, medidas DAX) documenta como ele foi
> construído, passo a passo — útil tanto pra quem quer entender as decisões
> tomadas quanto pra quem quer reconstruir o pipeline do zero.


---

## 1. Problema de negócio

Você é o(a) Analista de BI de um e-commerce. O CEO chega com perguntas de
gestão, não de relatório:

- Como estão as vendas?
- Estamos lucrando de verdade, ou só faturando?
- Quais clientes realmente valem a pena reter?
- O marketing está trazendo cliente bom ou só cliente barato?
- Quais produtos deveríamos parar de vender (ou pelo menos parar de promover)?
- Onde, exatamente, estamos deixando dinheiro na mesa?

O objetivo deste projeto não é "fazer um dashboard bonito" — é responder a
essas seis perguntas com dado, de um jeito que um CEO leia em 5 minutos.

---

## 2. Arquitetura da solução

```
CSV brutos (2 origens de vendas)  ──▶  Power Query (M)  ──▶  Modelo Estrela (Power BI)
        │                                    │                        │
        │                                    ▼                        ▼
        └──────────────▶ SQLite (SQL) ◀── mesmas regras de       Medidas DAX
                          negócio, em                              │
                          camada de consulta                       ▼
                                                              6 páginas do
                                                              dashboard
```

- **SQL (SQLite)** — camada de consulta/exploração: schema normalizado
  (`dim_pedidos` + `fato_itens_venda`) e as queries que respondem a cada
  pergunta do CEO antes mesmo de abrir o Power BI. Útil para validar
  hipóteses rapidamente e documentar a lógica de negócio em SQL puro.
- **Power Query (M)** — camada de ingestão: limpa e padroniza duas origens
  de vendas com formatos diferentes (simulando Site Próprio x Marketplace)
  e monta o modelo final "achatado" para o Power BI.
- **DAX** — camada semântica: ~45 medidas organizadas por página, cobrindo
  desde KPIs simples até curva ABC, ranking dinâmico e textos de insight
  gerados automaticamente a partir do modelo.

Ver `DAX/00_modelo_e_relacionamentos.md` para o detalhe do porquê dessa
divisão entre SQL normalizado e Power Query "achatado".

---

## 3. Estrutura do dashboard

| Página | O que responde |
|---|---|
| **1. Visão Executiva** | Receita, lucro, margem, ticket médio, pedidos, clientes, meta x realizado, receita acumulada |
| **2. Clientes** | Novos x recorrentes, ticket médio por cliente, clientes VIP, curva ABC, Top 20 |
| **3. Produtos** | Mais vendidos, mais lucrativos, maior desconto, e o cruzamento-chave: alto volume + baixa margem |
| **4. Geografia** | Receita, lucro e ticket médio por estado, num mapa e comparado à média nacional |
| **5. Comercial** | Ranking por categoria, subcategoria, canal de venda e vendedor/representante |
| **6. Insights** | Texto analítico — não é "mais um gráfico", é a conclusão de negócio de cada página anterior |

---

## 4. Principais insights (calculados sobre o dataset deste repositório)

> Reprodutíveis em `Dataset/insights_calculados.json` e nas queries de
> `SQL/02_queries_analiticas.sql` (seção "PÁGINA 6 — INSIGHTS").

1. **São Paulo concentra receita, mas não é o estado mais rentável.**
   SP responde por **32,2% da receita**, porém opera com margem de
   **30,9%** — cerca de **5,3 pontos percentuais abaixo** da margem
   nacional (36,2%). O volume de SP está mascarando uma rentabilidade
   inferior, provavelmente puxada por desconto médio mais agressivo
   (mercado mais competitivo).

2. **O produto mais vendido é o que menos lucra.**
   "Carregador Turbo USB-C 20W" é o item de maior volume do catálogo
   (530 unidades no período), mas roda com margem de apenas **13,2%** —
   bem abaixo da margem média do negócio. Ele provavelmente cumpre um
   papel de "produto de entrada" (traz gente para o carrinho), mas não
   deveria ser tratado como prioridade de giro sem essa ressalva.

3. **Cliente recorrente vale mais — e não é pouco.**
   O ticket médio de clientes recorrentes é **33,7% maior** que o de
   clientes novos (R$ 412 vs. R$ 308). Isso justifica investir em
   retenção (e-mail, programa de fidelidade) com o mesmo rigor que se
   investe em aquisição.

4. **Nem todo canal de aquisição traz o mesmo tipo de cliente.**
   Clientes vindos de **Instagram Ads** recompram em apenas 78,8% dos
   casos, contra **95,7%** dos clientes vindos de **Indicação**.
   Instagram Ads pode estar otimizado para volume de primeira compra,
   não para valor de longo prazo — vale revisar o mix de investimento
   em mídia com essa lente, e não só pelo CAC da primeira venda.

---

## 5. Decisões tomadas (e por quê)

- **Duas origens de vendas em vez de uma só.** Simulei o pedido vindo de
  "Site Próprio" (ERP, datas ISO, UF como sigla) e de "Marketplace"
  (planilha do parceiro, datas BR, desconto informado em R$, colunas com
  nomes completamente diferentes). Isso obriga a demonstrar Merge e Append
  de verdade, no cenário mais comum de e-commerce que vende em mais de um
  canal.
- **Fato "achatada" no Power BI, mas normalizada no SQL.** A camada SQL
  mantém `dim_pedidos` separada de `fato_itens_venda` (modelagem
  tradicional). Na camada Power Query, decidi achatar os atributos do
  pedido direto na fato final — menos uma tabela para relacionar, mais
  performático, e é o padrão mais comum em modelos DAX de mercado.
- **Relacionamento bidirecional só entre `fato_Metas` e `dim_Calendario`.**
  É a única exceção ao padrão "1 pra muitos" porque `fato_Metas` está no
  grão mês, e não no grão dia. Decisão documentada em
  `DAX/00_modelo_e_relacionamentos.md` em vez de deixar implícita.
- **Pedidos cancelados ficam no modelo, mas fora das medidas de receita.**
  Em vez de filtrar cancelamento já no Power Query (o que "esconderia" o
  dado), o filtro `status_pedido = "Concluído"` fica dentro de cada medida
  DAX/SQL. Isso permite, no futuro, adicionar uma medida de taxa de
  cancelamento sem precisar reimportar nada.
- **Curva ABC e "Cliente VIP" calculados dinamicamente (RANKX), não
  como coluna fixa.** Assim a classificação se recalcula sozinha
  conforme o usuário filtra por período, canal ou estado — em vez de
  ficar presa a um corte feito uma vez no Power Query.

---

## 6. Como o `.pbix` foi montado

O `Dashboard.pbix` já está pronto neste repositório — não precisa refazer
nada pra visualizar. O passo a passo abaixo documenta como ele foi
construído, caso você queira entender as decisões ou reconstruir do zero:

1. **Gerar/atualizar o dataset** (opcional — o repositório já vem com os
   dados gerados em `Dataset/`):
   ```bash
   cd Dataset/scripts
   pip install faker pandas numpy
   python gerar_dataset_fake.py
   ```
2. **Abrir o Power BI Desktop** → Obter Dados → escolher **SQLite**
   (`Dataset/ecommerce.db`) *ou* importar os CSVs limpos direto de
   `Dataset/*.csv` — os dois caminhos chegam no mesmo resultado.
3. **Para reproduzir o pipeline de limpeza do zero** (opcional, mas é o
   que demonstra o domínio de Power Query): use os CSVs de
   `Dataset/raw/` e cole o código de cada arquivo em `Power Query/*.pq`
   no Editor Avançado, na ordem indicada no `Power Query/README.md`.
4. **Relacionamentos**: seguir exatamente `DAX/00_modelo_e_relacionamentos.md`.
5. **Medidas**: criar uma tabela vazia `_Medidas` e colar o conteúdo de
   cada arquivo `DAX/0X_*.dax` (um `Nova Medida` por bloco).
6. **Montar as 6 páginas** seguindo a seção [3](#3-estrutura-do-dashboard)
   e a paleta documentada em `Imagens/README.md`.
7. Exportar os prints finais para `Imagens/` e salvar o `.pbix` na raiz do
   repositório.

---

## 7. Sobre os dados

O dataset é **100% fictício**, gerado via `Dataset/scripts/gerar_dataset_fake.py`
com `Faker` (localizado pt_BR) + regras de negócio propositalmente
embutidas (sazonalidade de Black Friday/Natal, diferença de desconto por
estado, diferença de recorrência por canal de aquisição etc.) para que os
insights da página 6 sejam **genuínos**, calculados sobre o dado gerado —
não escritos "de fora para dentro". Período simulado: Jan/2024 a Dez/2025.
650 clientes cadastrados (627 com pelo menos um pedido concluído),
53 produtos, 2.461 pedidos concluídos, receita total de R$ 1.003.941.

Cuidado extra foi tomado na qualidade dos dados de clientes, para evitar os
erros mais comuns de dataset sintético:
- **Nomes sem título/prefixo** (nada de "Dr.", "Sra." etc. — usa
  `first_name` + `last_name`, não o `name()` completo do Faker).
- **E-mails plausíveis**: sem acento, sem cedilha, sem o nome completo
  "vazando" com título — gerados a partir do nome já sem acentuação, com
  variação de formato (`nome.sobrenome`, `n.sobrenome`, `nome123` etc.) e
  distribuição de domínio realista para o Brasil (Gmail > Hotmail >
  Outlook > Yahoo > iCloud).
- **Cidade coerente com o estado**: lista de municípios reais por UF
  (capital + principais cidades), em vez de uma cidade genérica sem
  relação com o estado do cliente.
- **Telefone com DDD real** do estado do cliente, e **CEP com o prefixo
  numérico correto** da região dos Correios (ex.: CEPs de SP começam com
  0/1, do RS com 9, etc.) — não são endereços reais, mas seguem o padrão
  de numeração real.

---

## 8. Estrutura do repositório

```
Executive-Sales-Analytics/
├── README.md                      <- este arquivo
├── Dashboard.pbix                 <- montar seguindo a seção 6
├── Dataset/
│   ├── ecommerce.db                (SQLite, dados já limpos)
│   ├── dim_*.csv, fato_*.csv        (CSVs limpos, prontos para importar)
│   ├── insights_calculados.json     (números exatos usados na página 6)
│   ├── raw/                         (CSVs "sujos", para praticar Power Query)
│   └── scripts/                     (geração do dataset fictício)
├── SQL/
│   ├── 01_schema.sql
│   └── 02_queries_analiticas.sql
├── Power Query/
│   ├── README.md
│   └── 01 a 06_*.pq
├── DAX/
│   ├── 00_modelo_e_relacionamentos.md
│   └── 01 a 07_*.dax
└── Imagens/
    └── README.md
```

---

## 9. Ferramentas

Power BI · Power Query (M) · DAX · SQL (SQLite) · Python (Pandas, Faker) —
usado apenas para gerar o dataset fictício, não faz parte do pipeline de BI.
