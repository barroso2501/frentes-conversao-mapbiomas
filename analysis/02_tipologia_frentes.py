"""
02_tipologia_frentes.py  — ESQUELETO
Constrói, para cada classe de foco, os campos de frente/entrada por conjunção
(absoluta E relativa), replicando a lógica validada da nativa MAS com limiares e
denominadores CALIBRADOS POR CLASSE (ver docs/decisoes.md, CAL-1 e CAL-2).

Por que é esqueleto: os limiares (300 ha, 12%) foram calibrados na distribuição
da nativa. Pastagem (mancha pequena, dispersa) e agri temp (bloco grande,
concentrado) têm distribuições próprias. Você precisa OLHAR os quantis de cada
distribuição antes de fixar os pisos. Os TODO abaixo marcam onde isso entra.

O que pode quebrar e como você perceberia:
 - Reusar 300/12% cego: "frente de pastagem" superdimensiona manchas dispersas.
   Sintoma: contagem de frentes de pas absurdamente alta vs. nat/tmp.
 - Denominador de ganho = estoque inicial da própria classe: relativa explode em
   célula com pouco estoque inicial (franja). Sintoma: entrada_rel > 1 comum.
"""

from pathlib import Path
import pandas as pd

df = pd.read_parquet("../data/processed/mestre_fechada.parquet")

# --- perda e ganho ABSOLUTOS por classe de foco (ha) ------------------------
# perda de nat = tudo que saiu de nat para uso/água/nob (6 saídas)
PERDA = {
    "nat": ["ha_nat_pas", "ha_nat_tmp", "ha_nat_oag", "ha_nat_out", "ha_nat_agu", "ha_nat_nob"],
    "pas": ["ha_pas_nat", "ha_pas_tmp", "ha_pas_oag", "ha_pas_out", "ha_pas_agu", "ha_pas_nob"],
    "tmp": ["ha_tmp_nat", "ha_tmp_pas", "ha_tmp_oag", "ha_tmp_out", "ha_tmp_agu", "ha_tmp_nob"],
}
GANHO = {  # entradas (exceto nob->foco, que é termo de ajuste, não ganho real)
    "nat": ["ha_pas_nat", "ha_tmp_nat", "ha_oag_nat", "ha_out_nat", "ha_agu_nat"],
    "pas": ["ha_nat_pas", "ha_tmp_pas", "ha_oag_pas", "ha_out_pas", "ha_agu_pas"],
    "tmp": ["ha_nat_tmp", "ha_pas_tmp", "ha_oag_tmp", "ha_out_tmp", "ha_agu_tmp"],
}

for c in ["nat", "pas", "tmp"]:
    df[f"perda_abs_{c}"] = df[PERDA[c]].sum(axis=1)
    df[f"ganho_abs_{c}"] = df[GANHO[c]].sum(axis=1)
    # relativa da PERDA: sobre o estoque inicial da própria classe (defensável)
    df[f"perda_rel_{c}"] = df[f"perda_abs_{c}"] / df[f"estoque_{c}_ini"].replace(0, pd.NA)

# --- CAL-2: denominador da relativa de GANHO — DECIDIR POR CLASSE -----------
# TODO: para nat, o exercício anterior usou "estoque antrópico convertível".
#       para pas/tmp, NÃO usar estoque inicial da própria classe (franja).
#       Candidato: área conversível da célula, ou estoque nativo inicial.
#       Preencher DENOM_GANHO por classe depois de olhar as distribuições.
DENOM_GANHO = {
    "nat": None,   # TODO: estoque antrópico convertível inicial da célula
    "pas": None,   # TODO: área conversível OU estoque_nat_ini
    "tmp": None,   # TODO: idem
}

# --- CAL-1: limiares de frente por classe — CALIBRAR nas distribuições -------
# Rode primeiro este diagnóstico e olhe os quantis por classe/bioma:
print("=== Quantis de perda_abs e perda_rel por classe (para calibrar pisos) ===")
for c in ["nat", "pas", "tmp"]:
    q = df[[f"perda_abs_{c}", f"perda_rel_{c}"]].quantile([.5, .75, .9, .95, .99])
    print(f"\n-- {c} --\n{q}")

# TODO: substituir pelos pisos calibrados por classe (não reusar 300/12% cego)
LIMIARES = {
    "nat": {"abs": 300, "rel": 0.12},   # herdado — REVISAR mesmo p/ nat na grade hex
    "pas": {"abs": None, "rel": None},  # TODO calibrar
    "tmp": {"abs": None, "rel": None},  # TODO calibrar
}

# --- frente por conjunção (só roda para classes com limiar definido) --------
for c in ["nat", "pas", "tmp"]:
    lim = LIMIARES[c]
    if lim["abs"] is None or lim["rel"] is None:
        print(f"[pulando frente de {c}: limiar não calibrado]")
        continue
    df[f"frente_{c}"] = (
        (df[f"perda_abs_{c}"] > lim["abs"]) & (df[f"perda_rel_{c}"] > lim["rel"])
    )
    print(f"frente_{c}: {int(df[f'frente_{c}'].sum())} célula-períodos")

# --- frente terminal (exaustão) — só faz sentido claro para nat -------------
# TODO: decidir se o conceito de "terminal" (exaustão >0.70) transfere para
#       pas/tmp ou é exclusivo da nativa. Provavelmente exclusivo. Ver decisoes.md.

df.to_parquet("../data/processed/mestre_tipologia.parquet", index=False)
