"""
04_maup_espacial.py  — ESQUELETO
Robustez espacial em dois eixos (ver docs/maup_plano.md):
  A) ZONEAMENTO: grade quadrada 20 mil ha (herdada) vs. hexagonal de área
     equivalente. Barato — usa dados já existentes.
  B) ESCALA: >=3 resoluções de hexágono (ex.: ~5k, ~20k, ~80k ha).
Mais o DIAGNÓSTICO DO MOSAICO (21), que blinda a narrativa pas/tmp (CLS-2).

Por que é esqueleto: exige as tabelas mestre de MÚLTIPLAS grades, que só existem
depois de rodar a cadeia GEE (Estágio 3) em cada resolução. Aqui fica a estrutura
de comparação e as métricas de concordância.

O que pode quebrar e como você perceberia:
 - Comparar contagens absolutas entre grades de tamanhos diferentes (sem
   normalizar): parece que tudo muda. Compare PROPORÇÕES e ordenações, não
   contagens brutas. Ver métricas abaixo.
"""

from pathlib import Path
import pandas as pd

PROC = Path("../data/processed")

# --- A) ZONEAMENTO: quad vs hex de área equivalente -------------------------
# TODO: carregar mestre_tipologia de cada grade
# quad = pd.read_parquet(PROC / "mestre_tipologia_quad.parquet")
# hex_ = pd.read_parquet(PROC / "mestre_tipologia_hex20k.parquet")
#
# Métricas de concordância (por bioma):
#  - correlação de rank (Spearman) das células por perda_rel/expansão
#  - estabilidade das proporções de tipologia (% frente_nat, % consolidação pas...)
#  - quantas células mudam de classe de tipologia entre as malhas
print("ZONEAMENTO: comparar proporções de tipologia e ordenação por bioma "
      "entre grade quadrada e hexagonal de ~20 mil ha.")

# --- B) ESCALA: curva de sensibilidade em >=3 resoluções --------------------
# TODO: para cada resolução hex, computar as métricas-chave (frente por classe,
#       proporção expansão vs consolidação) e montar a curva vs. tamanho de célula.
#       Conclusão qualitativa: a ordenação de biomas e a existência dos regimes
#       sobrevivem? Se sim -> robusto.
print("ESCALA: montar curva das métricas-chave vs. tamanho de célula (3 resoluções).")

# --- DIAGNÓSTICO DO MOSAICO (21) — obrigatório antes de afirmar pas/tmp ------
# 21 está em 'outros agrícolas' (oag). O resíduo do 21 mora na interface
# nativa<->uso. Quantificar quanto da dinâmica de fronteira passa por oag:
#
#   fluxo_oag_fronteira = ha_nat_oag + ha_oag_nat   (proxy da transição via 21)
#   por bioma, comparar com  ha_nat_pas + ha_nat_tmp + ha_pas_nat + ha_tmp_nat
#
# Se fluxo_oag_fronteira for material (ex.: >15-20%) em algum bioma (suspeitos:
# Caatinga, franjas de Mata Atlântica), a narrativa pas/tmp ali é INCOMPLETA e
# precisa de ressalva explícita. Ver docs/limitacoes.md item 3.
df = pd.read_parquet(PROC / "mestre_tipologia.parquet")
if "bioma" in df.columns:
    df["fluxo_oag_front"] = df["ha_nat_oag"] + df["ha_oag_nat"]
    df["fluxo_foco_front"] = (df["ha_nat_pas"] + df["ha_nat_tmp"]
                              + df["ha_pas_nat"] + df["ha_tmp_nat"])
    diag = df.groupby("bioma")[["fluxo_oag_front", "fluxo_foco_front"]].sum()
    diag["frac_oag"] = diag["fluxo_oag_front"] / (
        diag["fluxo_oag_front"] + diag["fluxo_foco_front"])
    print("\n=== Diagnóstico do mosaico (21): fração da fronteira via 'oag' por bioma ===")
    print(diag.sort_values("frac_oag", ascending=False))
    print("\nBiomas com frac_oag alta -> escopar/ressalvar a narrativa pas/tmp.")
