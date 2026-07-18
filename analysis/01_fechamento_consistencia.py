"""
01_fechamento_consistencia.py
Verificação de consistência da cadeia — o análogo local da verificação nacional
de 0,002% do exercício anterior, agora com TRÊS identidades por classe de foco.

Para cada classe de foco X (nat, pas, tmp) e cada célula-período:
    estoque_X_fim_previsto = estoque_X_ini + Σ(entradas de X) - Σ(saídas de X)
O resíduo por célula deve ser ~0 (ruído de ponto flutuante). Resíduo sistemático
e grande indica bug de encoding ou a fronteira com a máscara (nob) mal tratada.

ESTE SCRIPT TEM LÓGICA REAL E COMPLETA. É a sua rede de segurança: rode antes de
qualquer análise. Se não fechar, não confie na tipologia.

O que pode quebrar e como você perceberia:
 - Se `nob->foco` (termo de ajuste) for tratado como ganho comum, o resíduo
   concentra onde há muito no-data. O diagnóstico por bioma abaixo expõe isso.
 - Se faltar uma banda de entrada/saída no encoding, o resíduo é sistemático e
   do mesmo sinal. As somas por classe abaixo revelam qual lado desequilibra.
"""

from pathlib import Path
import pandas as pd

M = Path("../data/processed/mestre.parquet")
df = pd.read_parquet(M)

# --- entradas e saídas de cada classe de foco (nomes de banda = fonte da verdade)
ENTRADAS = {
    "nat": ["ha_pas_nat", "ha_tmp_nat", "ha_oag_nat", "ha_out_nat", "ha_agu_nat", "ha_nob_nat"],
    "pas": ["ha_nat_pas", "ha_tmp_pas", "ha_oag_pas", "ha_out_pas", "ha_agu_pas", "ha_nob_pas"],
    "tmp": ["ha_nat_tmp", "ha_pas_tmp", "ha_oag_tmp", "ha_out_tmp", "ha_agu_tmp", "ha_nob_tmp"],
}
SAIDAS = {
    "nat": ["ha_nat_pas", "ha_nat_tmp", "ha_nat_oag", "ha_nat_out", "ha_nat_agu", "ha_nat_nob"],
    "pas": ["ha_pas_nat", "ha_pas_tmp", "ha_pas_oag", "ha_pas_out", "ha_pas_agu", "ha_pas_nob"],
    "tmp": ["ha_tmp_nat", "ha_tmp_pas", "ha_tmp_oag", "ha_tmp_out", "ha_tmp_agu", "ha_tmp_nob"],
}


def variacao_liquida(df, classe):
    """entrada total - saída total da classe, por célula-período."""
    ent = df[ENTRADAS[classe]].sum(axis=1)
    sai = df[SAIDAS[classe]].sum(axis=1)
    return ent - sai


# --- identidade por classe: variação líquida deve casar com delta de estoque ---
# Nota: só temos estoque INICIAL por período. Para checar o fechamento completo
# precisamos do estoque inicial do período SEGUINTE como "estoque final". Fazemos
# isso encadeando períodos por célula.
df = df.sort_values(["cell_id", "periodo"]).reset_index(drop=True)

for classe in ["nat", "pas", "tmp"]:
    df[f"varliq_{classe}"] = variacao_liquida(df, classe)
    # estoque final observado = estoque inicial do próximo período (mesma célula)
    df[f"estoque_{classe}_fim_obs"] = (
        df.groupby("cell_id")[f"estoque_{classe}_ini"].shift(-1)
    )
    df[f"estoque_{classe}_fim_prev"] = (
        df[f"estoque_{classe}_ini"] + df[f"varliq_{classe}"]
    )
    df[f"residuo_{classe}"] = (
        df[f"estoque_{classe}_fim_obs"] - df[f"estoque_{classe}_fim_prev"]
    )

# --- relatório de fechamento -------------------------------------------------
# (o último período de cada célula não tem "próximo" e fica NaN — ignorado)
print("=== Fechamento por classe (resíduo em ha; esperado ~0) ===")
for classe in ["nat", "pas", "tmp"]:
    r = df[f"residuo_{classe}"].dropna()
    print(f"{classe}: n={len(r)} | média={r.mean():.4g} | "
          f"|resíduo| total={r.abs().sum():.4g} | "
          f"máx|resíduo|={r.abs().max():.4g}")

# --- onde o resíduo se concentra (diagnóstico da máscara) --------------------
if "bioma" in df.columns:
    print("\n=== |resíduo| total de nat por bioma (onde há no-data, concentra) ===")
    print(df.groupby("bioma")["residuo_nat"].apply(lambda s: s.abs().sum())
            .sort_values(ascending=False))

# flag de confiabilidade: célula-período com resíduo relevante (>0.5 ha, ajuste)
LIM = 0.5
df["flag_residuo"] = (
    df[["residuo_nat", "residuo_pas", "residuo_tmp"]].abs().max(axis=1) > LIM
)
print(f"\ncélula-períodos com flag de resíduo (>{LIM} ha):",
      int(df["flag_residuo"].sum()))
# essas flags se propagam à análise: permitem rodar tudo com e sem as suspeitas.

df.to_parquet("../data/processed/mestre_fechada.parquet", index=False)
