# 📊 Executive Sales & Customer Analytics — Dashboard Power BI

Dashboard executivo de vendas construído em Power BI, com 6 páginas cobrindo desempenho financeiro, comportamento de clientes, produtos, geografia e insights automatizados. Projeto de portfólio focado em storytelling analítico, modelagem em DAX e identidade visual customizada.

![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=flat&logo=powerbi&logoColor=black)
![DAX](https://img.shields.io/badge/DAX-Power%20Query%20%26%20Modeling-0575B4?style=flat)
![Status](https://img.shields.io/badge/status-conclu%C3%ADdo-brightgreen)

---

## 🖼️ Preview

> Adicione aqui os prints de cada página (recomendado: exportar como PNG direto do Power BI Desktop, uma imagem por página, salvas em `docs/screenshots/`).

```
docs/screenshots/01-visao-executiva.png
docs/screenshots/02-clientes.png
docs/screenshots/03-produtos.png
docs/screenshots/04-geografia.png
docs/screenshots/05-comercial.png
docs/screenshots/06-insights.png
```

---

## 📁 Estrutura do dashboard

O relatório é dividido em 6 páginas, cada uma com um foco analítico específico:

### 1. Visão Executiva
Painel de KPIs no topo (cards) seguido de três visuais de tendência temporal:
- **Receita e Lucro por Mês** — gráfico combinado (colunas + linha)
- **Receita Acumulada por Mês** — gráfico de área
- **Receita x Meta por Mês** — colunas agrupadas comparando realizado vs. meta

### 2. Clientes
Foco em comportamento e valor do cliente:
- **Clientes Novos x Clientes Recorrentes** — donut chart
- **Ticket Médio x Cliente** — gráfico de barras
- **% Receita Acumulada x Cliente** — curva de Pareto (área)
- Tabela detalhada de clientes

### 3. Produtos
Análise de performance por produto:
- **Quantidade Vendida por Produto**
- **Lucro Total por Produto**
- **Desconto Médio % por Produto**
- **Quantidade Vendida e Margem de Lucro % por Produto** — scatter chart (quadrantes de performance)

### 4. Geografia
Distribuição espacial das vendas:
- **Ticket Médio por Estado**
- Gráficos de barras complementares por região
- Tabela detalhada + botão de ação (drill-through)

### 5. Comercial
Visão do desempenho comercial/canal de vendas, com gráficos de barras horizontais e navegação via botão de ação.

### 6. Insights
Página de destaques automatizados em formato de cards narrativos:
- **Produto de Atenção**
- **Destaque Geográfico**
- **Recorrência**
- **Canal**

Todas as páginas incluem segmentadores (slicers) para filtragem interativa por período, produto, cliente, etc.

---

## 🎨 Identidade visual

Tema customizado (**"Simplifica"**) aplicado a todo o relatório, com paleta de cores própria para garantir consistência visual e legibilidade entre os visuais.

---

## 🛠️ Tecnologias e técnicas utilizadas

- **Power BI Desktop** — modelagem e construção do relatório
- **Power Query (M)** — transformação e limpeza de dados
- **DAX** — medidas calculadas (KPIs, % acumulado, comparação com meta, etc.)
- **Modelagem de dados** — relacionamento entre tabelas fato/dimensão
- **Tema customizado** — paleta de cores própria (JSON theme)

---

## 🚀 Como usar

1. Baixe o arquivo [`vendas.pbix`](./vendas.pbix)
2. Abra no **Power BI Desktop** (versão 2.128 ou superior)
3. Caso o arquivo esteja conectado a uma fonte de dados externa, atualize as credenciais em *Transformar Dados → Configurações da Fonte de Dados*

---

## 👤 Autor

**Thiago** — BI Analyst / Desenvolvedor Freelancer
Projeto desenvolvido como peça de portfólio, com foco no mercado brasileiro.

---

## 📄 Licença

Este projeto está licenciado sob a licença MIT — veja o arquivo [LICENSE](./LICENSE) para mais detalhes.
