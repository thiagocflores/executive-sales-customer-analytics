# -*- coding: utf-8 -*-
"""
Gerador de dataset fictício - Executive Sales & Customer Analytics
Simula 24 meses de operação de um e-commerce brasileiro, com padrões
propositalmente embutidos para gerar insights de negócio reais:
 - SP concentra ~38-40% da receita mas com desconto médio maior (margem menor)
 - Produtos "isca" (alto volume, margem baixíssima)
 - Clientes recorrentes com ticket médio ~35% maior
 - Canais de aquisição com qualidade de cliente muito diferente
 - Sazonalidade (Black Friday, Natal, Dia das Mães)
"""
import numpy as np
import pandas as pd
from faker import Faker
import random
import sqlite3
import json
import os
from datetime import date

random.seed(42)
np.random.seed(42)
fake = Faker("pt_BR")
Faker.seed(42)

import unicodedata
import re

def strip_accents(texto):
    """Remove acentos/cedilha - usado só para gerar e-mails (que não existem
    com acento/cedilha na vida real)."""
    nfkd = unicodedata.normalize("NFD", texto)
    return "".join(c for c in nfkd if unicodedata.category(c) != "Mn")

def gerar_email(primeiro_nome, sobrenome):
    p = re.sub(r"[^a-z]", "", strip_accents(primeiro_nome).lower())
    s = re.sub(r"[^a-z]", "", strip_accents(sobrenome).lower())
    formato = random.choice([
        f"{p}.{s}", f"{p}{s}", f"{p[0]}.{s}",
        f"{p}.{s}{random.randint(1,99)}", f"{p}{random.randint(1,999)}",
        f"{p}.{s[:3]}",
    ])
    dominio = random.choices(
        ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com.br", "icloud.com"],
        weights=[52, 20, 14, 9, 5]
    )[0]
    return f"{formato}@{dominio}"

# Cidades reais por UF (capital + principais municípios), com peso maior para a capital
CIDADES_POR_UF = {
    "SP": ["São Paulo","Campinas","Guarulhos","Santo André","São Bernardo do Campo","Osasco","Sorocaba","Ribeirão Preto","São José dos Campos","Santos"],
    "RJ": ["Rio de Janeiro","Niterói","Duque de Caxias","Nova Iguaçu","São Gonçalo","Petrópolis","Volta Redonda","Campos dos Goytacazes"],
    "MG": ["Belo Horizonte","Uberlândia","Contagem","Juiz de Fora","Betim","Montes Claros","Uberaba"],
    "RS": ["Porto Alegre","Caxias do Sul","Pelotas","Canoas","Santa Maria","Gravataí"],
    "PR": ["Curitiba","Londrina","Maringá","Ponta Grossa","Cascavel","Foz do Iguaçu"],
    "SC": ["Florianópolis","Joinville","Blumenau","Chapecó","Itajaí","Criciúma"],
    "BA": ["Salvador","Feira de Santana","Vitória da Conquista","Camaçari","Itabuna","Ilhéus"],
    "PE": ["Recife","Jaboatão dos Guararapes","Olinda","Caruaru","Petrolina"],
    "CE": ["Fortaleza","Caucaia","Juazeiro do Norte","Sobral","Maracanaú"],
    "DF": ["Brasília","Taguatinga","Ceilândia","Águas Claras","Sobradinho"],
    "GO": ["Goiânia","Aparecida de Goiânia","Anápolis","Rio Verde","Luziânia"],
    "ES": ["Vitória","Vila Velha","Serra","Cariacica","Linhares"],
    "MT": ["Cuiabá","Várzea Grande","Rondonópolis","Sinop"],
    "MS": ["Campo Grande","Dourados","Três Lagoas","Corumbá"],
    "PA": ["Belém","Ananindeua","Santarém","Marabá"],
    "AM": ["Manaus","Parintins","Itacoatiara"],
    "MA": ["São Luís","Imperatriz","Caxias","Timon"],
}

# DDD real por UF (principais códigos de área)
DDD_POR_UF = {
    "SP": ["11","12","13","14","15","16","17","18","19"], "RJ": ["21","22","24"],
    "MG": ["31","32","33","34","35","37","38"], "RS": ["51","53","54","55"],
    "PR": ["41","42","43","44","45","46"], "SC": ["47","48","49"],
    "BA": ["71","73","74","75","77"], "PE": ["81","87"], "CE": ["85","88"],
    "DF": ["61"], "GO": ["62","64"], "ES": ["27","28"], "MT": ["65","66"],
    "MS": ["67"], "PA": ["91","93","94"], "AM": ["92","97"], "MA": ["98","99"],
}

# 1º dígito do CEP real por região dos Correios (0=SP capital/regiao,1=SP interior,
# 2=RJ/ES,3=MG,4=BA/SE,5=PE/AL/PB/RN,6=CE/PI/MA/PA/AM/AC/RR/AP/RO,7=DF/GO/TO/MT/MS,8=PR/SC,9=RS)
CEP_PREFIXO_POR_UF = {
    "SP": "0", "RJ": "2", "ES": "2", "MG": "3", "BA": "4", "PE": "5", "CE": "6",
    "DF": "7", "GO": "7", "MT": "7", "MS": "7", "PR": "8", "SC": "8", "RS": "9",
    "PA": "6", "AM": "6", "MA": "6",
}

def cidade_realista(uf):
    lista = CIDADES_POR_UF.get(uf, ["Cidade Não Informada"])
    pesos = [0.42] + [0.58 / (len(lista) - 1)] * (len(lista) - 1) if len(lista) > 1 else [1.0]
    return np.random.choice(lista, p=pesos)

def telefone_realista(uf):
    ddd = random.choice(DDD_POR_UF.get(uf, ["11"]))
    return f"({ddd}) 9{random.randint(1000,9999)}-{random.randint(1000,9999)}"

def cep_realista(uf):
    prefixo = CEP_PREFIXO_POR_UF.get(uf, "0")
    resto = "".join(str(random.randint(0,9)) for _ in range(4))
    sufixo = "".join(str(random.randint(0,9)) for _ in range(3))
    return f"{prefixo}{resto}-{sufixo}"


OUT_RAW = "/home/claude/Executive-Sales-Analytics/Dataset/raw"
OUT_CLEAN = "/home/claude/Executive-Sales-Analytics/Dataset"
os.makedirs(OUT_RAW, exist_ok=True)
os.makedirs(OUT_CLEAN, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. DIMENSÃO ESTADOS / REGIÃO
# ---------------------------------------------------------------------------
estados = [
    ("SP", "São Paulo", "Sudeste", 0.38),
    ("RJ", "Rio de Janeiro", "Sudeste", 0.13),
    ("MG", "Minas Gerais", "Sudeste", 0.09),
    ("RS", "Rio Grande do Sul", "Sul", 0.07),
    ("PR", "Paraná", "Sul", 0.06),
    ("SC", "Santa Catarina", "Sul", 0.045),
    ("BA", "Bahia", "Nordeste", 0.055),
    ("PE", "Pernambuco", "Nordeste", 0.035),
    ("CE", "Ceará", "Nordeste", 0.03),
    ("DF", "Distrito Federal", "Centro-Oeste", 0.03),
    ("GO", "Goiás", "Centro-Oeste", 0.025),
    ("ES", "Espírito Santo", "Sudeste", 0.02),
    ("MT", "Mato Grosso", "Centro-Oeste", 0.012),
    ("MS", "Mato Grosso do Sul", "Centro-Oeste", 0.011),
    ("PA", "Pará", "Norte", 0.012),
    ("AM", "Amazonas", "Norte", 0.009),
    ("MA", "Maranhão", "Nordeste", 0.008),
]
df_estados = pd.DataFrame(estados, columns=["uf", "estado", "regiao", "peso"])
df_estados["peso"] = df_estados["peso"] / df_estados["peso"].sum()

# Desconto médio "estrutural" por estado -> SP tem concorrência mais forte = desconto maior
desconto_base_estado = {uf: 0.06 for uf in df_estados["uf"]}
desconto_base_estado["SP"] = 0.19
desconto_base_estado["RJ"] = 0.10
desconto_base_estado["DF"] = 0.05

# ---------------------------------------------------------------------------
# 2. DIMENSÃO CALENDÁRIO (24 meses: 2024-01 a 2025-12)
# ---------------------------------------------------------------------------
datas = pd.date_range("2024-01-01", "2025-12-31", freq="D")
meses_pt = ["Janeiro","Fevereiro","Março","Abril","Maio","Junho","Julho",
            "Agosto","Setembro","Outubro","Novembro","Dezembro"]
df_calendario = pd.DataFrame({"data": datas})
df_calendario["ano"] = df_calendario["data"].dt.year
df_calendario["mes"] = df_calendario["data"].dt.month
df_calendario["mes_nome"] = df_calendario["mes"].apply(lambda m: meses_pt[m-1])
df_calendario["ano_mes"] = df_calendario["data"].dt.strftime("%Y-%m")
df_calendario["trimestre"] = "T" + df_calendario["data"].dt.quarter.astype(str)
df_calendario["dia_semana"] = df_calendario["data"].dt.day_name()
df_calendario["fim_de_semana"] = df_calendario["data"].dt.dayofweek >= 5

# Peso de sazonalidade por mês (Black Friday=Nov, Natal=Dez, Dia das Maes=Mai)
peso_sazonal = {1:0.8,2:0.75,3:0.85,4:0.85,5:1.15,6:0.9,7:0.85,8:0.85,
                 9:0.9,10:1.0,11:2.3,12:1.7}

# ---------------------------------------------------------------------------
# 3. DIMENSÃO PRODUTOS
# ---------------------------------------------------------------------------
categorias = {
    "Eletrônicos": ["Áudio", "Acessórios de Celular", "Informática", "Smart Home"],
    "Moda": ["Feminina", "Masculina", "Calçados"],
    "Casa e Decoração": ["Cozinha", "Organização", "Decoração"],
    "Beleza": ["Skincare", "Maquiagem", "Perfumaria"],
    "Esporte e Lazer": ["Fitness", "Outdoor"],
}

nomes_produto_base = {
    "Áudio": ["Fone Bluetooth", "Caixa de Som Portátil", "Fone com Fio", "Soundbar Compacta"],
    "Acessórios de Celular": ["Carregador Turbo USB-C 20W", "Capinha Silicone", "Película 3D", "Cabo USB-C 1m", "Suporte Veicular"],
    "Informática": ["Mouse Sem Fio", "Teclado Mecânico", "Hub USB-C", "Webcam HD"],
    "Smart Home": ["Lâmpada Inteligente", "Tomada Wi-Fi", "Fita LED RGB"],
    "Feminina": ["Vestido Midi", "Blusa Básica", "Calça Alfaiataria", "Saia Plissada"],
    "Masculina": ["Camisa Social", "Bermuda Sarja", "Camiseta Básica", "Jaqueta Corta-Vento"],
    "Calçados": ["Tênis Casual", "Sandália Conforto", "Sapatênis"],
    "Cozinha": ["Jogo de Panelas", "Air Fryer", "Liquidificador", "Conjunto de Facas"],
    "Organização": ["Caixa Organizadora", "Cabide Multiuso Kit", "Organizador de Gaveta"],
    "Decoração": ["Quadro Decorativo", "Luminária de Mesa", "Vaso Cerâmica", "Almofada Decorativa"],
    "Skincare": ["Sérum Vitamina C", "Protetor Solar FPS 60", "Hidratante Facial"],
    "Maquiagem": ["Base Líquida", "Paleta de Sombras", "Máscara de Cílios"],
    "Perfumaria": ["Perfume 100ml", "Body Splash", "Kit Perfumaria"],
    "Fitness": ["Kit Halteres", "Tapete de Yoga", "Elástico de Resistência"],
    "Outdoor": ["Garrafa Térmica", "Mochila Impermeável", "Barraca Camping 2p"],
}

produtos = []
pid = 1
for cat, subs in categorias.items():
    for sub in subs:
        base_names = nomes_produto_base[sub]
        for nome in base_names:
            # perfil de margem
            if nome == "Carregador Turbo USB-C 20W":
                perfil = "atracao_flagship"
            elif nome in ["Capinha Silicone", "Cabo USB-C 1m"]:
                perfil = "atracao"
            elif nome in ["Fone Bluetooth", "Camiseta Básica", "Vestido Midi"]:
                perfil = "clearance"  # alto desconto
            elif random.random() < 0.18:
                perfil = "premium"
            else:
                perfil = "regular"

            preco_custo = round(np.random.uniform(15, 220), 2)
            if perfil == "atracao_flagship":
                margem_alvo = np.random.uniform(0.03, 0.05)
                peso_volume = np.random.uniform(7.0, 8.0)
            elif perfil == "atracao":
                margem_alvo = np.random.uniform(0.05, 0.10)
                peso_volume = np.random.uniform(3.0, 4.5)
            elif perfil == "premium":
                margem_alvo = np.random.uniform(0.45, 0.65)
                peso_volume = np.random.uniform(0.4, 0.9)
            elif perfil == "clearance":
                margem_alvo = np.random.uniform(0.15, 0.25)
                peso_volume = np.random.uniform(1.8, 2.6)
            else:
                margem_alvo = np.random.uniform(0.20, 0.40)
                peso_volume = np.random.uniform(0.8, 1.8)

            preco_lista = round(preco_custo / (1 - margem_alvo), 2)
            # variação de nome (algumas cores/modelos) + extra espaço proposital em alguns (para PQ)
            # variação de nome coerente com a categoria (roupa/calçado leva P/M/G,
            # eletrônico leva cor, perfumaria/cozinha não leva variante boba)
            if sub in ["Feminina", "Masculina", "Calçados"]:
                variante = random.choice(["", " P", " M", " G", " P/M/G"])
            elif cat == "Eletrônicos" or sub in ["Fitness", "Outdoor", "Organização"]:
                variante = random.choice(["", " Preto", " Branco", " Azul", " 2ª Geração"])
            elif sub in ["Skincare", "Maquiagem", "Perfumaria", "Cozinha"]:
                variante = ""
            else:
                variante = random.choice(["", " Preto", " Branco", " Azul"])
            nome_completo = f"{nome}{variante}"
            produtos.append({
                "produto_id": pid, "nome_produto": nome_completo, "categoria": cat,
                "subcategoria": sub, "preco_custo": preco_custo, "preco_lista": preco_lista,
                "perfil_margem": perfil, "peso_volume": peso_volume,
            })
            pid += 1

df_produtos = pd.DataFrame(produtos)

# ---------------------------------------------------------------------------
# 4. DIMENSÃO CLIENTES
# ---------------------------------------------------------------------------
canais_aquisicao = {
    "Instagram Ads":   {"peso": 0.30, "p_recorrente": 0.15, "mult_ticket": 0.85},
    "Facebook Ads":    {"peso": 0.20, "p_recorrente": 0.18, "mult_ticket": 0.90},
    "Google Ads":      {"peso": 0.18, "p_recorrente": 0.27, "mult_ticket": 1.00},
    "Orgânico/Busca":  {"peso": 0.16, "p_recorrente": 0.35, "mult_ticket": 1.05},
    "Indicação":       {"peso": 0.08, "p_recorrente": 0.48, "mult_ticket": 1.20},
    "Email Marketing": {"peso": 0.08, "p_recorrente": 0.50, "mult_ticket": 1.15},
}
canais_nomes = list(canais_aquisicao.keys())
canais_pesos = [canais_aquisicao[c]["peso"] for c in canais_nomes]

N_CLIENTES = 650
clientes = []
for i in range(1, N_CLIENTES + 1):
    uf = np.random.choice(df_estados["uf"], p=df_estados["peso"])
    canal = np.random.choice(canais_nomes, p=canais_pesos)
    # 55% da base já existia desde o início (fundação da loja em Jan-Mar/2024),
    # o restante entra gradualmente ao longo do período (crescimento de base)
    if random.random() < 0.55:
        data_cadastro = fake.date_between(start_date=date(2024,1,1), end_date=date(2024,3,31))
    else:
        data_cadastro = fake.date_between(start_date=date(2024,4,1), end_date=date(2025,10,1))

    # Nome sem títulos/prefixos (Dr., Sra. etc.) — usa first_name + last_name
    # em vez de fake.name(), que às vezes injeta prefixo
    primeiro_nome = fake.first_name()
    sobrenome = fake.last_name()
    nome_cli = f"{primeiro_nome} {sobrenome}"

    email = gerar_email(primeiro_nome, sobrenome)
    cidade = cidade_realista(uf)
    telefone = telefone_realista(uf)
    cep = cep_realista(uf)

    clientes.append({
        "cliente_id": i, "nome_cliente": nome_cli, "email": email,
        "telefone": telefone, "cidade": cidade, "uf": uf, "cep": cep,
        "data_cadastro": data_cadastro, "canal_aquisicao": canal,
    })
df_clientes = pd.DataFrame(clientes)
df_clientes = df_clientes.merge(df_estados[["uf","estado","regiao"]], on="uf", how="left")

# probabilidade de recorrência e multiplicador de ticket por cliente (herdado do canal)
df_clientes["p_recorrente"] = df_clientes["canal_aquisicao"].map(lambda c: canais_aquisicao[c]["p_recorrente"])
df_clientes["mult_ticket_canal"] = df_clientes["canal_aquisicao"].map(lambda c: canais_aquisicao[c]["mult_ticket"])

# ---------------------------------------------------------------------------
# 5. VENDEDORES / REPRESENTANTES (canal comercial - contas-chave / marketplace)
# ---------------------------------------------------------------------------
vendedores = [
    (1, "Ana Beatriz Souza", "Key Account"), (2, "Carlos Eduardo Lima", "Key Account"),
    (3, "Fernanda Rocha", "Marketplace"), (4, "João Pedro Alves", "Marketplace"),
    (5, "Marina Costa", "Loja Própria"), (6, "Rafael Nogueira", "Loja Própria"),
]
df_vendedores = pd.DataFrame(vendedores, columns=["vendedor_id","nome_vendedor","time_comercial"])

canais_venda = ["Site Próprio", "Marketplace", "Aplicativo"]

# ---------------------------------------------------------------------------
# 6. PEDIDOS + ITENS (fato)
# ---------------------------------------------------------------------------
meses_lista = df_calendario["ano_mes"].unique().tolist()
mes_para_peso = {}
for am in meses_lista:
    ano, mes = int(am[:4]), int(am[5:7])
    boost_2025 = 1.12 if ano == 2025 else 1.0  # leve crescimento ano a ano
    mes_para_peso[am] = peso_sazonal[mes] * boost_2025

N_PEDIDOS = 3400
pedidos_rows = []
itens_rows = []
pedido_id = 1
item_id = 1

# distribuir pedidos entre clientes: uns nunca compram de novo, outros recompram
compras_por_cliente = {cid: [] for cid in df_clientes["cliente_id"]}

meses_pesos_arr = np.array([mes_para_peso[m] for m in meses_lista])
meses_pesos_arr = meses_pesos_arr / meses_pesos_arr.sum()

produtos_pesos = df_produtos["peso_volume"].values
produtos_pesos = produtos_pesos / produtos_pesos.sum()

# peso dinâmico de seleção de cliente: comeca uniforme (1.0); depois da 1a compra,
# passa a refletir a propensao de recompra do canal de aquisicao (p_recorrente)
client_ids_arr = df_clientes["cliente_id"].values
client_weight = pd.Series(1.0, index=client_ids_arr)
p_recorrente_map = df_clientes.set_index("cliente_id")["p_recorrente"]

for n in range(N_PEDIDOS):
    ano_mes = np.random.choice(meses_lista, p=meses_pesos_arr)
    ano, mes = int(ano_mes[:4]), int(ano_mes[5:7])
    dia = np.random.randint(1, 28)
    data_pedido = pd.Timestamp(year=ano, month=mes, day=dia)

    # distribuição por estado já está embutida na base de clientes (cada cliente tem 1 uf fixo).
    # o peso de seleção reflete a propensão de recompra do canal de aquisição de cada cliente
    w = client_weight.values
    w = w / w.sum()
    cid = np.random.choice(client_ids_arr, p=w)
    cliente = df_clientes.loc[df_clientes["cliente_id"] == cid].iloc[0]
    # pedido so conta se for depois do cadastro
    if pd.Timestamp(cliente["data_cadastro"]) > data_pedido:
        continue

    n_pedidos_anteriores = len(compras_por_cliente[cid])
    eh_recorrente = n_pedidos_anteriores > 0

    uf = cliente["uf"]
    canal_venda = np.random.choice(canais_venda, p=[0.55, 0.35, 0.10])
    vendedor = df_vendedores.sample(1).iloc[0]["vendedor_id"]

    n_itens = np.random.choice([1,2,3,4], p=[0.45,0.32,0.16,0.07])
    prods_escolhidos = np.random.choice(df_produtos["produto_id"], size=n_itens, replace=False, p=produtos_pesos)

    desconto_medio_estado = desconto_base_estado[uf]

    for prod_id in prods_escolhidos:
        prod = df_produtos.loc[df_produtos["produto_id"] == prod_id].iloc[0]
        qtd = np.random.choice([1,2,3], p=[0.7,0.22,0.08])

        # cliente recorrente compra ticket ~35% maior (via ajuste de preco efetivo/qtd)
        mult_recorrente = 1.35 if eh_recorrente else 1.0
        mult_canal = cliente["mult_ticket_canal"]

        preco_unit = prod["preco_lista"]

        # desconto: base do estado + variação por perfil de produto
        desconto_pct = desconto_medio_estado + np.random.uniform(-0.03, 0.05)
        if prod["perfil_margem"] == "clearance":
            desconto_pct += np.random.uniform(0.08, 0.13)
        desconto_pct = max(0, min(desconto_pct, 0.45))

        fator_valor = mult_recorrente * mult_canal
        preco_final_unit = round(preco_unit * fator_valor, 2)

        itens_rows.append({
            "item_id": item_id, "pedido_id": pedido_id, "produto_id": prod_id,
            "quantidade": int(qtd), "preco_unitario": preco_final_unit,
            "desconto_percentual": round(desconto_pct, 4),
            "custo_unitario": prod["preco_custo"],
        })
        item_id += 1

    pedidos_rows.append({
        "pedido_id": pedido_id, "cliente_id": cid, "data_pedido": data_pedido,
        "canal_venda": canal_venda, "uf": uf, "vendedor_id": vendedor,
        "status_pedido": np.random.choice(["Concluído","Concluído","Concluído","Cancelado"], p=[0.90,0.0,0.0,0.10]) if False else np.random.choice(["Concluído","Cancelado"], p=[0.93,0.07]),
    })
    compras_por_cliente[cid].append(pedido_id)
    # atualiza peso: uma vez que o cliente já comprou, sua chance de ser sorteado de novo
    # passa a refletir a propensao de recompra do canal (clientes de canais bons repetem mais)
    client_weight.loc[cid] = 0.15 + 2.6 * p_recorrente_map.loc[cid]
    pedido_id += 1

df_pedidos = pd.DataFrame(pedidos_rows)
df_itens = pd.DataFrame(itens_rows)

# ---------------------------------------------------------------------------
# 7. METAS MENSAIS (meta x realizado)
# ---------------------------------------------------------------------------
receita_real_mes = (
    df_itens.merge(df_pedidos[["pedido_id","data_pedido","status_pedido"]], on="pedido_id")
    .query("status_pedido == 'Concluído'")
)
receita_real_mes["receita_liquida"] = (
    receita_real_mes["preco_unitario"] * receita_real_mes["quantidade"] * (1 - receita_real_mes["desconto_percentual"])
)
receita_real_mes["ano_mes"] = receita_real_mes["data_pedido"].dt.strftime("%Y-%m")
receita_mensal = receita_real_mes.groupby("ano_mes")["receita_liquida"].sum().reset_index()

metas = []
for i, row in receita_mensal.iterrows():
    fator_meta = np.random.uniform(0.90, 1.10)
    metas.append({"ano_mes": row["ano_mes"], "meta_receita": round(row["receita_liquida"] * fator_meta, 2)})
df_metas = pd.DataFrame(metas)

# ===========================================================================
# 8. SALVAR VERSÕES "CRUAS" (com inconsistências) PARA POWER QUERY TRABALHAR
# ===========================================================================
# 8.1 Clientes cru: espaços extras, texto maiusculo aleatorio
df_clientes_raw = df_clientes.copy()
df_clientes_raw["nome_cliente"] = df_clientes_raw["nome_cliente"].apply(
    lambda x: f"  {x.upper()}  " if random.random() < 0.25 else x)
df_clientes_raw["cidade"] = df_clientes_raw["cidade"].apply(
    lambda x: x.lower() if random.random() < 0.3 else x)
df_clientes_raw = df_clientes_raw[["cliente_id","nome_cliente","email","telefone","cidade","uf",
                                    "cep","data_cadastro","canal_aquisicao"]]
df_clientes_raw.to_csv(f"{OUT_RAW}/clientes_raw.csv", index=False)

# 8.2 Produtos cru: subcategoria nula em alguns, nomes com espaços duplos
df_produtos_raw = df_produtos.copy()
df_produtos_raw.loc[df_produtos_raw.sample(frac=0.05, random_state=1).index, "subcategoria"] = None
df_produtos_raw["nome_produto"] = df_produtos_raw["nome_produto"].apply(
    lambda x: x.replace(" ", "  ", 1) if random.random() < 0.1 else x)
df_produtos_raw = df_produtos_raw[["produto_id","nome_produto","categoria","subcategoria",
                                    "preco_custo","preco_lista"]]
df_produtos_raw.to_csv(f"{OUT_RAW}/produtos_raw.csv", index=False)

# 8.3 Pedidos: SPLIT em duas "origens" para demonstrar APPEND no Power Query
fato = df_itens.merge(df_pedidos, on="pedido_id", how="left")
fato = fato.merge(df_estados[["uf","estado"]], on="uf", how="left")

split_point = int(len(fato) * 0.62)
fato_shuffled = fato.sample(frac=1, random_state=7).reset_index(drop=True)
origem_a = fato_shuffled.iloc[:split_point].copy()   # "site próprio" - export do ERP
origem_b = fato_shuffled.iloc[split_point:].copy()   # "marketplace" - export de planilha do parceiro

# Origem A: datas em formato ISO, UF como sigla, alguns nulos em desconto
origem_a_out = origem_a[["pedido_id","item_id","cliente_id","produto_id","data_pedido",
                          "uf","canal_venda","vendedor_id","quantidade","preco_unitario",
                          "desconto_percentual","custo_unitario","status_pedido"]].copy()
origem_a_out["data_pedido"] = pd.to_datetime(origem_a_out["data_pedido"]).dt.strftime("%Y-%m-%d")
mask_null_desc = origem_a_out.sample(frac=0.04, random_state=2).index
origem_a_out.loc[mask_null_desc, "desconto_percentual"] = None
origem_a_out.rename(columns={"uf": "UF_Sigla"}, inplace=True)
origem_a_out.to_csv(f"{OUT_RAW}/vendas_site_proprio_raw.csv", index=False)

# Origem B: datas em formato BR (dd/mm/yyyy), estado por extenso, colunas em outra ordem/nome,
# preço e desconto embutidos de forma diferente (desconto em R$ ao invés de %)
origem_b_out = origem_b[["pedido_id","item_id","cliente_id","produto_id","data_pedido",
                          "estado","canal_venda","vendedor_id","quantidade","preco_unitario",
                          "desconto_percentual","custo_unitario","status_pedido"]].copy()
origem_b_out["Data_Venda_BR"] = pd.to_datetime(origem_b_out["data_pedido"]).dt.strftime("%d/%m/%Y")
origem_b_out["Desconto_Reais"] = (origem_b_out["preco_unitario"] * origem_b_out["quantidade"] *
                                   origem_b_out["desconto_percentual"]).round(2)
origem_b_out = origem_b_out.drop(columns=["data_pedido", "desconto_percentual"])
origem_b_out = origem_b_out.rename(columns={
    "estado": "Estado_Extenso", "pedido_id": "ID_Pedido", "item_id": "ID_Item",
    "cliente_id": "ID_Cliente", "produto_id": "ID_Produto", "canal_venda": "Canal",
    "vendedor_id": "ID_Vendedor", "quantidade": "Qtd", "preco_unitario": "Preco_Unit",
    "custo_unitario": "Custo_Unit", "status_pedido": "Status",
})
origem_b_out.to_csv(f"{OUT_RAW}/vendas_marketplace_raw.csv", index=False)

df_vendedores.to_csv(f"{OUT_RAW}/vendedores_raw.csv", index=False)
df_estados.drop(columns=["peso"]).to_csv(f"{OUT_RAW}/dim_estados_raw.csv", index=False)
df_metas.to_csv(f"{OUT_RAW}/metas_raw.csv", index=False)

# ===========================================================================
# 9. VERSÕES LIMPAS / MODELADAS (equivalente ao resultado do Power Query)
#    -> usadas para popular o SQLite e alimentar o modelo estrela no Power BI
# ===========================================================================
df_clientes_clean = df_clientes[["cliente_id","nome_cliente","email","telefone","cidade","uf","cep",
                                  "estado","regiao","data_cadastro","canal_aquisicao"]].copy()
df_clientes_clean["data_cadastro"] = pd.to_datetime(df_clientes_clean["data_cadastro"])

df_produtos_clean = df_produtos[["produto_id","nome_produto","categoria","subcategoria",
                                  "preco_custo","preco_lista","perfil_margem"]].copy()

df_pedidos_clean = df_pedidos.merge(df_estados[["uf","estado","regiao"]], on="uf", how="left")
df_pedidos_clean["data_pedido"] = pd.to_datetime(df_pedidos_clean["data_pedido"])
df_pedidos_clean = df_pedidos_clean[["pedido_id","cliente_id","data_pedido","canal_venda",
                                      "uf","estado","regiao","vendedor_id","status_pedido"]]

df_itens_clean = df_itens.copy()

df_calendario_clean = df_calendario[["data","ano","mes","mes_nome","ano_mes","trimestre",
                                      "dia_semana","fim_de_semana"]].copy()

df_metas_clean = df_metas.copy()

# salvar CSVs limpos (Dataset/ -> prontos para importar no Power BI)
df_clientes_clean.to_csv(f"{OUT_CLEAN}/dim_clientes.csv", index=False)
df_produtos_clean.to_csv(f"{OUT_CLEAN}/dim_produtos.csv", index=False)
df_pedidos_clean.to_csv(f"{OUT_CLEAN}/dim_pedidos.csv", index=False)
df_itens_clean.to_csv(f"{OUT_CLEAN}/fato_itens_venda.csv", index=False)
df_calendario_clean.to_csv(f"{OUT_CLEAN}/dim_calendario.csv", index=False)
df_vendedores.to_csv(f"{OUT_CLEAN}/dim_vendedores.csv", index=False)
df_estados.drop(columns=["peso"]).to_csv(f"{OUT_CLEAN}/dim_estados.csv", index=False)
df_metas_clean.to_csv(f"{OUT_CLEAN}/fato_metas.csv", index=False)

# ===========================================================================
# 10. BANCO SQLITE
# ===========================================================================
db_path = f"{OUT_CLEAN}/ecommerce.db"
if os.path.exists(db_path):
    os.remove(db_path)
conn = sqlite3.connect(db_path)
df_clientes_clean.to_sql("dim_clientes", conn, index=False)
df_produtos_clean.to_sql("dim_produtos", conn, index=False)
df_pedidos_clean.to_sql("dim_pedidos", conn, index=False)
df_itens_clean.to_sql("fato_itens_venda", conn, index=False)
df_calendario_clean.to_sql("dim_calendario", conn, index=False)
df_vendedores.to_sql("dim_vendedores", conn, index=False)
df_estados.drop(columns=["peso"]).to_sql("dim_estados", conn, index=False)
df_metas_clean.to_sql("fato_metas", conn, index=False)
conn.commit()

# ===========================================================================
# 11. CALCULAR INSIGHTS REAIS (para README e página de Insights)
# ===========================================================================
q = """
SELECT f.*, p.data_pedido, p.uf, p.estado, p.canal_venda, p.status_pedido, p.cliente_id,
       pr.nome_produto, pr.categoria, pr.subcategoria, pr.perfil_margem, pr.preco_custo
FROM fato_itens_venda f
JOIN dim_pedidos p ON f.pedido_id = p.pedido_id
JOIN dim_produtos pr ON f.produto_id = pr.produto_id
WHERE p.status_pedido = 'Concluído'
"""
full = pd.read_sql(q, conn)
full["receita_liquida"] = full["preco_unitario"] * full["quantidade"] * (1 - full["desconto_percentual"])
full["custo_total"] = full["custo_unitario"] * full["quantidade"]
full["lucro"] = full["receita_liquida"] - full["custo_total"]

receita_total = full["receita_liquida"].sum()
lucro_total = full["lucro"].sum()
margem_geral = lucro_total / receita_total

por_estado = full.groupby("estado").agg(receita=("receita_liquida","sum"), lucro=("lucro","sum")).reset_index()
por_estado["margem"] = por_estado["lucro"] / por_estado["receita"]
por_estado["pct_receita"] = por_estado["receita"] / receita_total
sp = por_estado[por_estado["estado"]=="São Paulo"].iloc[0]

por_produto = full.groupby("nome_produto").agg(
    receita=("receita_liquida","sum"), lucro=("lucro","sum"),
    qtd=("quantidade","sum")).reset_index()
por_produto["margem"] = por_produto["lucro"] / por_produto["receita"]
top_volume_baixa_margem = por_produto.sort_values("qtd", ascending=False).head(15)
# entre os mais vendidos, destaca o de maior volume que também tem margem baixa (<18%)
candidatos_isca = top_volume_baixa_margem[top_volume_baixa_margem["margem"] < 0.18]
produto_isca = (candidatos_isca if len(candidatos_isca) else top_volume_baixa_margem).sort_values("qtd", ascending=False).iloc[0]

# recorrência: cliente com >1 pedido concluido
pedidos_por_cliente = full.groupby("cliente_id")["pedido_id"].nunique()
clientes_recorrentes = set(pedidos_por_cliente[pedidos_por_cliente > 1].index)
full["eh_recorrente"] = full["cliente_id"].isin(clientes_recorrentes)
ticket_pedido = full.groupby(["pedido_id","eh_recorrente"])["receita_liquida"].sum().reset_index()
ticket_medio_recorrente = ticket_pedido[ticket_pedido["eh_recorrente"]]["receita_liquida"].mean()
ticket_medio_novo = ticket_pedido[~ticket_pedido["eh_recorrente"]]["receita_liquida"].mean()
diff_ticket_pct = (ticket_medio_recorrente / ticket_medio_novo - 1) * 100

# canal de aquisição x recorrência (via clientes)
cli_canal = df_clientes_clean.set_index("cliente_id")["canal_aquisicao"]
full["canal_aquisicao"] = full["cliente_id"].map(cli_canal)
clientes_unicos = full[["cliente_id","canal_aquisicao"]].drop_duplicates()
clientes_unicos["recorrente"] = clientes_unicos["cliente_id"].isin(clientes_recorrentes)
canal_recorrencia = clientes_unicos.groupby("canal_aquisicao")["recorrente"].mean().sort_values()

insights = {
    "receita_total": round(receita_total, 2),
    "lucro_total": round(lucro_total, 2),
    "margem_geral_pct": round(margem_geral * 100, 2),
    "sp_pct_receita": round(sp["pct_receita"] * 100, 1),
    "sp_margem_pct": round(sp["margem"] * 100, 1),
    "margem_geral_comparacao_pct": round(margem_geral * 100, 1),
    "produto_isca_nome": produto_isca["nome_produto"],
    "produto_isca_margem_pct": round(produto_isca["margem"] * 100, 1),
    "produto_isca_qtd": int(produto_isca["qtd"]),
    "ticket_medio_recorrente": round(ticket_medio_recorrente, 2),
    "ticket_medio_novo": round(ticket_medio_novo, 2),
    "diff_ticket_pct": round(diff_ticket_pct, 1),
    "pior_canal_recorrencia": canal_recorrencia.index[0],
    "pior_canal_recorrencia_pct": round(canal_recorrencia.iloc[0] * 100, 1),
    "melhor_canal_recorrencia": canal_recorrencia.index[-1],
    "melhor_canal_recorrencia_pct": round(canal_recorrencia.iloc[-1] * 100, 1),
    "n_clientes": int(df_clientes_clean.shape[0]),
    "n_pedidos_concluidos": int(full["pedido_id"].nunique()),
    "n_produtos": int(df_produtos_clean.shape[0]),
    "periodo": "Jan/2024 a Dez/2025",
}

with open(f"{OUT_CLEAN}/insights_calculados.json", "w", encoding="utf-8") as f:
    json.dump(insights, f, ensure_ascii=False, indent=2)

conn.close()
print(json.dumps(insights, ensure_ascii=False, indent=2))
print("\nOK - dataset gerado com sucesso.")
