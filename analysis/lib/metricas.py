"""
metricas.py — limiares e cálculos de métrica relativa por classe.
Fonte única dos parâmetros calibrados. NÃO espalhe números mágicos pelos scripts.

O que pode quebrar e como você perceberia:
 - Se um limiar ficar None e for usado, a função levanta erro explícito em vez de
   rodar com valor errado silenciosamente. É proposital.
"""

# Limiares de frente por classe (CALIBRAR — ver docs/decisoes.md CAL-1).
# 'abs' em ha; 'rel' em fração do denominador da classe.
LIMIARES_FRENTE = {
    "nat": {"abs": 300, "rel": 0.12},   # herdado; revisar na grade hex
    "pas": {"abs": None, "rel": None},  # TODO calibrar na distribuição de pas
    "tmp": {"abs": None, "rel": None},  # TODO calibrar na distribuição de tmp
}

# Limiar de exaustão para frente terminal (provavelmente só nat).
EXAUSTAO_TERMINAL = 0.70

# Durabilidade: nº de períodos (quinquênios) para "consolidado".
PERIODOS_DURAVEL = 2  # 10 anos


def exige(valor, nome):
    if valor is None:
        raise ValueError(f"Parâmetro '{nome}' não calibrado (None). "
                         f"Ver docs/decisoes.md.")
    return valor
