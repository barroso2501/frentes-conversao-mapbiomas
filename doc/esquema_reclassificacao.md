# Esquema de reclassificação — 7 classes

Reclassificação da legenda completa da Coleção 11 em 7 classes de cobertura,
de forma **exaustiva e nominal**: nenhuma classe é atribuída por exclusão.
Qualquer código não previsto cai em "não observado / sem dado" e é isolado na
auditoria de valores únicos de pixel (§ Auditoria), nunca somado silenciosamente
a uma categoria.

## Tabela código → classe

| Classe de saída | Código interno | Códigos MapBiomas Col 11 |
|---|---|---|
| **Vegetação natural** | `1` (nat) | 1, 3, 4, 5, 6, 7, 10, 11, 12, 13, 29, 32, 49, 50, 84 |
| **Pastagem plantada** | `2` (pas) | 15 |
| **Agricultura temporária** | `3` (tmp) | 19, 20, 39, 40, 41, 62 |
| **Outros agrícolas** | `4` (oag) | 9, 21, 35, 36, 46, 47, 48 |
| **Outro** | `5` (out) | 22, 23, 24, 25, 30, 75, 91 |
| **Água** | `6` (agu) | 26, 33, 31 |
| **Não observado** | `masked` (nob) | 27 + qualquer código imprevisto |

> **Verificar contra o LEIA-ME da Col 11 antes de congelar em produção:**
> - Códigos-pai agregados **14** (Agropecuária) e **18** (Agricultura) existem na
>   legenda hierárquica mas **não ocorrem no raster integrado** (`classification-ft`).
>   Confirmado pelo autor; sem prejuízo ao remap. A auditoria de valores únicos
>   confirma isso de forma independente.
> - Confirmar que a Col 11 não introduziu **código-folha novo** (beta de cultivo,
>   etc.) fora destas listas. Um código-folha novo não mapeado cai em "não
>   observado" sem aviso — mesmo modo de falha que a arquitetura exaustiva foi
>   feita para pegar.

## Classes de foco vs. classes de contexto

As três primeiras classes são **foco** — recebem tratamento analítico simétrico
e completo (entrada e saída, tipologia de frente, durabilidade):

- **Vegetação natural** (nat)
- **Pastagem plantada** (pas)
- **Agricultura temporária** (tmp)

As demais são **contexto** — entram como **estoque dinâmico** e nas identidades
de **fechamento por célula**, mas **não** viram objeto de tipologia:

- **Outros agrícolas** (oag), **Outro** (out), **Água** (agu), **Não observado** (nob).

Essa separação preserva a recuperação de "nativa → uso agropecuário total"
(pas + tmp + oag) para comparabilidade com a estatística oficial de agropecuária
do MapBiomas, sem contaminar essa soma com urbano/mineração/infraestrutura
(que ficam em `out`).

## Decisões de agregação registradas

- **Vegetação natural inclui formações campestres, savânicas e naturais não
  florestais** (11, 12, 29, 32, etc.), não apenas floresta. Adequado à pergunta
  (frentes em todos os biomas), mas exige cuidado ao comparar com PRODES e
  produtos centrados em floresta. Ver `docs/limitacoes.md`.
- **Afloramento rochoso (29)** e **apicum (32)** seguem sua posição hierárquica
  sob "Vegetação Herbácea ou Arbustiva" → vegetação natural.
- **Praia/duna (23)** está sob "Área não Vegetada" → `out`.
- **Aquicultura (31)** → água.
- **Silvicultura (9)** → `outros agrícolas`. É uso plantado, não frente de
  conversão de nativa. **Mas** `nativa → 9` (eucalipto/pinus sobre nativa,
  vetor real no Cerrado/MG/BA e no Pampa) continua sendo **perda de nativa** na
  contabilidade — ver `esquema_transicoes.md`, saída `ha_nat_oag`.
- **Lavoura perene (36, 35, 46, 47, 48)** → `outros agrícolas`. Regional; não é
  foco, mas contabilizado como destino da nativa.

## O Mosaico de Usos (código 21) — nota crítica de escopo

O código 21 (Mosaico de Usos) é uso agropecuário onde a Col 10 **não separou**
pastagem de agricultura. Dois fatos mudam o peso desta classe na Col 11:

1. A **Coleção 11 reatribuiu ~2/3 do mosaico da Col 10** para pastagem (15) e
   agricultura nas classes-folha. Ou seja, a maior parte do sinal agropecuário
   que antes ficava trancado em 21 agora está **dentro** das classes de foco
   (pas, tmp) — exatamente onde se quer. O problema de "medir uma minoria da
   agropecuária" encolhe de primeira-ordem para residual.

2. O que **restou** no 21 concentra-se em **mosaicos de pequenas propriedades e
   áreas em transição uso–natural**. Consequência analítica: o resíduo do 21
   mora **na interface nativa↔uso**, que é o objeto do trabalho. Portanto
   `nativa ↔ 21` (bandas `ha_nat_oag` e `ha_oag_nat`) pode capturar **dinâmica de
   fronteira incipiente** bucketada em "outros agrícolas" e fora da tipologia.

**Ação de verificação (barata, obrigatória antes de afirmar):** quantificar
`nativa ↔ 21` como fluxo dirigido e a área de 21 **por bioma e por ano-marco**.
Se pequeno e difuso → vira frase de limitação. Se concentrado (suspeitos:
Caatinga, franjas de Mata Atlântica de pequena propriedade) → reportar que ali
a fronteira tem um componente "transicional indiferenciado" que a tipologia
nat/pas/tmp não resolve. Ver `analysis/04_maup_espacial.py` e `docs/limitacoes.md`.

## Parâmetros técnicos do remap (GEE)

- `defaultValue = 0` (não observado) → `updateMask(neq(0))` remove esses pixels;
  ficam como no-data, **nunca** como uso.
- Saída em `uint8`, banda única com o código interno (1–6).
- `pyramidingPolicy: 'mode'` — **obrigatório** para categórico. A política padrão
  `mean` inventa valores intermediários nos zooms baixos.
- Assets salvos como `mb11_cob7_{ano}` para os 9 anos-marco (1985, 1990, …, 2025).
- Cada asset carrega metadados de proveniência (versão fonte, esquema de
  agregação, legenda, data).
