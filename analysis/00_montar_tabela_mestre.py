"""
00_montar_tabela_mestre.py
Consolida os 8 CSVs de transição + os 8 CSVs de estoque inicial + a camada de
bioma numa única tabela mestre (uma linha por célula-período).

ESQUELETO com lógica real de junção. Ajuste os caminhos e o merge de bioma ao
seu arquivo de referência.

O que pode quebrar e como você perceberia:
 - Estoque e mudança de períodos desalinhados: se juntar estoque do ano errado,
   o fechamento (script 01) não bate. Aqui a chave de junção é (cell_id, período)
   com o estoque do ANO INICIAL do período — confira o mapeamento abaixo.
 - Células faltando em um período: a mestre fica menor que n_células*8. O check
   final avisa.
"""

from pathlib import Path
import pandas as pd
from lib.io import ler_muitos, ler_csv_gee

RAW = Path("../data/raw")
REF = Path("../data/reference")
OUT = Path("../data/processed")
OUT.mkdir(parents=True, exist_ok=True)

# --- 1) mudança: concatena os 8 períodos -----------------------------------
mudanca = ler_muitos("grade_change_*.csv", RAW)

# --- 2) estoque inicial: concatena e mapeia ano_ini -> período --------------
estoque = ler_muitos("estoque_ini_*.csv", RAW)
# cada período "a0_a1" usa o estoque do ano a0
estoque = estoque.rename(columns={"ano_ini": "_ano_ini"})
# constrói a coluna 'periodo' a partir do ano inicial (a0 -> "a0_a1")
ANOS = [1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025]
prox = {a0: f"{a0}_{a1}" for a0, a1 in zip(ANOS[:-1], ANOS[1:])}
estoque["periodo"] = estoque["_ano_ini"].astype(int).map(prox)
estoque = estoque.drop(columns=["_ano_ini"]).rename(columns={
    "estoque_nat": "estoque_nat_ini",
    "estoque_pas": "estoque_pas_ini",
    "estoque_tmp": "estoque_tmp_ini",
})

# --- 3) junta mudança + estoque por (cell_id, periodo) ----------------------
mestre = mudanca.merge(estoque, on=["cell_id", "periodo"], how="left")

# --- 4) camada de bioma (uma vez por célula) --------------------------------
# TODO: apontar para seu arquivo de bioma por cell_id (consolidar encoding se
# vier corrompido, como no exercício anterior — "Amazônia" fatiada).
try:
    bioma = ler_csv_gee(REF / "celula_bioma.csv")[["cell_id", "bioma"]]
    mestre = mestre.merge(bioma, on="cell_id", how="left")
except FileNotFoundError:
    print("AVISO: celula_bioma.csv ausente — mestre sem coluna 'bioma'.")

# --- 5) checagem de completude ----------------------------------------------
n_cel = mestre["cell_id"].nunique()
n_per = mestre["periodo"].nunique()
print(f"células: {n_cel} | períodos: {n_per} | linhas: {len(mestre)} "
      f"| esperado: {n_cel * n_per}")
if len(mestre) != n_cel * n_per:
    print("AVISO: linhas != células*períodos — há célula-período faltando.")

mestre.to_parquet(OUT / "mestre.parquet", index=False)
print("tabela mestre salva em", OUT / "mestre.parquet")
