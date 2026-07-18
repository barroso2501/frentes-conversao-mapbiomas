# Nota metodológica — cadeia completa

Descreve a cadeia de processamento da Coleção 11 do MapBiomas às análises de
frentes de conversão e dinâmica de uso. Registra assets, esquemas, parâmetros e
— deliberadamente — as decisões metodológicas e onde cada uma pode falhar.

Detalhamento das decisões: `decisoes.md`. Esquema de classes:
`esquema_reclassificacao.md`. Transições: `esquema_transicoes.md`. Robustez:
`maup_plano.md`. Fragilidades: `limitacoes.md`.

## 1. Visão geral da cadeia

| Estágio | Entrada | Saída |
|---|---|---|
| 1. Reclassificação | Col 11 `classification-ft` | 9 rasters de 7 classes (anos-marco) |
| 2. Detecção de mudança dirigida | 9 rasters reclassificados | 8 rasters de transição (pares quinquenais) |
| 3. Tabulação por célula (hex) + estoque | rasters de mudança + grade hex | CSVs célula×transição + estoque por classe |
| 4. Análise | tabela mestre consolidada | fechamento, tipologia, MAUP, figuras |

Toda a cadeia GEE opera na grade nativa do MapBiomas (EPSG:4326, pixel ~30 m em
graus decimais), sem reamostragem, via `crsTransform` — nunca `scale`. Parâmetros
em `gee/lib/constantes.js`.

## 2. Fonte de dados

- **Cobertura:** Col 11 `INTEGRATION/classification-ft`, versão `0-4-13-w3y-5`
  (filtro temporal de 3 anos aplicado na origem; sufixo `w3y`). 49 tiles, bandas
  `classification_1985`…`classification_2025`. Filtro por versão via
  `ee.Filter.eq('version', …)` + `.mosaic()`.
- **Anos-marco:** 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025 (9 anos,
  8 pares quinquenais).
- **Grade:** hexagonal — **decisão de resolução/tipo aberta** (ver maup_plano.md).
  Migração da grade quadrada de 20 mil ha do exercício anterior, que passa a
  servir de comparação de zoneamento no MAUP espacial.

## 3. Estágio 1 — Reclassificação (7 classes)

Ver `esquema_reclassificacao.md` para a tabela completa código→classe e os
parâmetros de remap (`defaultValue=0`, `updateMask`, `uint8`,
`pyramidingPolicy:'mode'`). Assets `mb11_cob7_{ano}`.

**Auditoria obrigatória antes de congelar:** inventário de valores únicos de
pixel no `classification-ft` ao longo dos 9 anos-marco, confirmando que todo
código observado cai em exatamente um balde (e que 14/18 não ocorrem no raster).

## 4. Estágio 2 — Detecção de mudança dirigida

Para cada par sequencial de anos-marco (8 pares), cruza-se pixel a pixel as
classes reclassificadas e tabula-se **área por transição dirigida** — 30 bandas
(ver `esquema_transicoes.md`). Abandona o encoding `int8 −2..+2` do exercício
anterior (insuficiente para 6 classes). Arquitetura: uma banda de
`ee.Image.pixelArea()` por transição, `Reducer.sum()` sobre a grade.

Máscara de validade `t0.mask().and(t1.mask())`: a transição só é computada onde
ambos os anos têm dado. Pixel válido num ano e no-data no outro tem transição
indefinida — tratá-lo como estabilidade injetaria falsa estabilidade.

## 5. Estágio 3 — Tabulação por célula e estoque

Sobre a grade hex, tabula-se a área de cada transição por célula-período (30
colunas) + estoque inicial de nat/pas/tmp por célula-período. `ee.Image.pixelArea()`,
não contagem. Saída: CSVs `grade_change_{periodo}.csv` + `estoque_{periodo}.csv`.

**Atenção de leitura dos CSVs do GEE:** separador `;` e decimal vírgula (`,`) —
colunas numéricas vêm como texto e precisam de conversão explícita ao carregar
(tratado em `analysis/lib/io.py`).

## 6. Estágio 4 — Tabela mestre e análises

Consolida os 8 CSVs de mudança + estoque + camadas auxiliares (bioma, grade) numa
tabela mestre (43.436-equivalente de células × 8 períodos, ajustado à grade hex).

**Fechamento (três identidades por classe + global):** para cada classe de foco,
`estoque_t1 = estoque_t0 + Σentradas − Σsaídas` por célula. Mais o Σ global de
variações líquidas ≈ 0. Análogo local à verificação nacional de 0,002% do
exercício anterior. Se não fechar, o resíduo mora na fronteira com a máscara
(`nob→foco`) e é nomeado, não diluído. Implementado em
`analysis/01_fechamento_consistencia.py`.

**Tipologia** (`analysis/02_tipologia_frentes.py`): frente ativa por conjunção
(absoluta ∧ relativa), frente terminal por exaustão, com **limiares recalibrados
por classe** (ver decisoes.md CAL-1) e **denominador relativo decidido por classe**
(CAL-2).

**Durabilidade/consolidação** (`analysis/03_consolidacao_durabilidade.py`):
persistência ≥10 anos, com justificativa ecológica (nativa) ou de permanência de
uso (pas/tmp) — mesma mecânica, significados distintos (CAL-3).

**MAUP** (`analysis/04_maup_espacial.py`, `05_maup_temporal.py`): ver maup_plano.md.

## 7. Reprodutibilidade — artefatos

| Artefato | Identificação |
|---|---|
| Cobertura fonte | Col 11 `classification-ft`, versão `0-4-13-w3y-5` |
| Rasters reclassificados | `mb11_cob7_{ano}` (9 anos-marco) |
| Rasters de mudança | `mb11_change7_{ano1}_{ano2}` (8 pares, 30 bandas) |
| Tabelas por célula | `grade_change_{periodo}.csv` (8) + `estoque_{periodo}.csv` |
| Tabela mestre | `data/processed/mestre.parquet` |
| Grade | hex (tipo/resolução a definir) + quadrada 20 mil ha (comparação) |

Cada asset de saída carrega metadados de proveniência (versão fonte, esquema de
agregação, legenda, decisões de flag).
