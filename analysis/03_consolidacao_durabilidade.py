"""
03_consolidacao_durabilidade.py  — ESQUELETO
Durabilidade da ENTRADA de cada classe de foco: persistência ≥10 anos (dois
quinquênios) sem que o ganho seja neutralizado pelo balanço subsequente da
célula. Mesma MECÂNICA para nat/pas/tmp; SIGNIFICADOS diferentes (CAL-3):
  - nat: durabilidade ecológica (pousio vs regeneração de fato)
  - pas/tmp: permanência de USO (estabilidade fundiária/econômica) = CONSOLIDAÇÃO

Categorias por evento de entrada:
  - consolidado: persistiu >=10 anos
  - reconvertido/revertido: neutralizado antes
  - indeterminado: entrada recente (2015-2025), sem folga de observação

Por que é esqueleto: a durabilidade é medida por persistência LÍQUIDA NA CÉLULA
(o agregado não rastreia pixels). O critério exato de "neutralizado" precisa ser
o de estoque líquido da classe na célula — o mesmo erro do exercício anterior
(comparar perda bruta com ganho, gerando 96% de reconversão falso) NÃO pode se
repetir. O TODO central marca isso.

O que pode quebrar e como você perceberia:
 - Critério de neutralização por perda BRUTA da célula (errado): infla
   reconversão. Sintoma: >60-90% de reconversão em toda classe/bioma.
 - Não separar 'indeterminado' nos períodos recentes: subestima consolidação nos
   últimos 10 anos. Sintoma: queda artificial de consolidação em 2015-2025.
"""

from pathlib import Path
import pandas as pd

df = pd.read_parquet("../data/processed/mestre_tipologia.parquet")
df = df.sort_values(["cell_id", "periodo"]).reset_index(drop=True)

ANOS = [1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025]
PERIODOS = [f"{a}_{b}" for a, b in zip(ANOS[:-1], ANOS[1:])]

# entrada líquida da classe na célula por período (ganho - perda da própria classe)
for c in ["nat", "pas", "tmp"]:
    df[f"entrada_liq_{c}"] = df[f"ganho_abs_{c}"] - df[f"perda_abs_{c}"]

# --- TODO central: definir "persistiu >=10 anos" -----------------------------
# Para cada célula onde houve entrada líquida positiva no período t, verificar se
# o estoque da classe NÃO retornou ao patamar pré-entrada nos >=2 períodos
# seguintes (10 anos). Usar estoque_{c}_ini encadeado por célula (shift), NUNCA
# perda bruta da célula como proxy de reconversão.
#
# def classifica_durabilidade(sub):  # sub = série temporal de uma célula
#     ...
#     return 'consolidado' | 'revertido' | 'indeterminado'
#
# df['durab_pas'] = df.groupby('cell_id').apply(classifica_durabilidade_pas)...

print("ESQUELETO: preencher classifica_durabilidade por classe usando estoque "
      "líquido encadeado. Ver docs/decisoes.md CAL-3 e a nota de erro do "
      "exercício anterior (não usar perda bruta).")
