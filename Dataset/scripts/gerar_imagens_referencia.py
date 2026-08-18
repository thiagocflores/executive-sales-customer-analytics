# -*- coding: utf-8 -*-
"""Gera imagens de REFERÊNCIA de estilo/paleta (não são screenshots reais do
Power BI — servem como guia visual de como montar os gráficos no relatório)."""
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

DB = "/home/claude/Executive-Sales-Analytics/Dataset/ecommerce.db"
OUT = "/home/claude/Executive-Sales-Analytics/Imagens"

# Paleta pedida no briefing
BG = "#F7F8FA"        # fundo claro
AZUL_ESCURO = "#0B2545"
VERDE_LUCRO = "#1E7B34"
VERMELHO_PREJUIZO = "#B3261E"
CINZA_TEXTO = "#3C4858"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "#D9DCE1",
    "axes.labelcolor": CINZA_TEXTO,
    "text.color": CINZA_TEXTO,
    "xtick.color": CINZA_TEXTO,
    "ytick.color": CINZA_TEXTO,
})

conn = sqlite3.connect(DB)
q = """
SELECT c.ano_mes,
       SUM(f.preco_unitario*f.quantidade*(1-f.desconto_percentual)) receita,
       SUM(f.preco_unitario*f.quantidade*(1-f.desconto_percentual) - f.custo_unitario*f.quantidade) lucro
FROM fato_itens_venda f
JOIN dim_pedidos p ON f.pedido_id = p.pedido_id
JOIN dim_calendario c ON date(p.data_pedido) = date(c.data)
WHERE p.status_pedido = 'Concluído'
GROUP BY c.ano_mes ORDER BY c.ano_mes
"""
df = pd.read_sql(q, conn)

# ---------------------------------------------------------------------------
# Gráfico 1: Receita x Lucro por mês
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 5), facecolor=BG)
ax.set_facecolor(BG)
x = range(len(df))
ax.bar(x, df["receita"], color=AZUL_ESCURO, width=0.55, label="Receita", zorder=3)
ax.plot(x, df["lucro"], color=VERDE_LUCRO, marker="o", linewidth=2.5, label="Lucro", zorder=4)
ax.set_xticks(list(x))
ax.set_xticklabels(df["ano_mes"], rotation=45, ha="right", fontsize=8)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, p: f"R$ {v/1000:.0f}k"))
ax.set_title("Receita e Lucro por Mês", fontsize=14, fontweight="bold", color=AZUL_ESCURO, loc="left")
ax.grid(axis="y", color="#E3E6EA", linewidth=0.8, zorder=0)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.legend(frameon=False, loc="upper left")
plt.tight_layout()
plt.savefig(f"{OUT}/referencia_receita_lucro_mensal.png", dpi=150, facecolor=BG)
plt.close()

# ---------------------------------------------------------------------------
# Gráfico 2: Curva ABC de clientes
# ---------------------------------------------------------------------------
qc = """
SELECT cliente_id, SUM(preco_unitario*quantidade*(1-desconto_percentual)) receita
FROM fato_itens_venda f JOIN dim_pedidos p ON f.pedido_id=p.pedido_id
WHERE p.status_pedido='Concluído' GROUP BY cliente_id ORDER BY receita DESC
"""
cli = pd.read_sql(qc, conn)
cli["acumulado_pct"] = cli["receita"].cumsum() / cli["receita"].sum()
cli["cliente_pct"] = (pd.Series(range(1, len(cli)+1)) / len(cli))

fig, ax = plt.subplots(figsize=(9, 5), facecolor=BG)
ax.set_facecolor(BG)
ax.plot(cli["cliente_pct"]*100, cli["acumulado_pct"]*100, color=AZUL_ESCURO, linewidth=2.5)
ax.axhline(80, color=VERMELHO_PREJUIZO, linestyle="--", linewidth=1, alpha=0.7)
ax.axhline(95, color="#C77700", linestyle="--", linewidth=1, alpha=0.7)
ax.fill_between(cli["cliente_pct"]*100, 0, cli["acumulado_pct"]*100, color=AZUL_ESCURO, alpha=0.08)
ax.set_xlabel("% de Clientes (ordenado por receita)")
ax.set_ylabel("% de Receita Acumulada")
ax.set_title("Curva ABC de Clientes", fontsize=14, fontweight="bold", color=AZUL_ESCURO, loc="left")
ax.grid(color="#E3E6EA", linewidth=0.8)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)
ax.text(72, 82, "Linha A (80%)", fontsize=8, color=VERMELHO_PREJUIZO)
ax.text(72, 96.5, "Linha B (95%)", fontsize=8, color="#C77700")
plt.tight_layout()
plt.savefig(f"{OUT}/referencia_curva_abc_clientes.png", dpi=150, facecolor=BG)
plt.close()

print("Imagens de referência geradas.")
