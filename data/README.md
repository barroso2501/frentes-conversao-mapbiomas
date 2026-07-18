# Dados

Os dados grandes NÃO são versionados no git (ver `.gitignore`). Este README é o
dicionário de dados e o mapa de onde cada coisa vive.

## Estrutura

- `raw/` — CSVs exportados do GEE via Drive. **Não versionado.**
  - `grade_change_{a0}_{a1}.csv` — 30 colunas de área de transição por célula-período.
  - `estoque_ini_{a0}.csv` — estoque de nat/pas/tmp por célula no ano inicial.
  - Formato: separador `;`, decimal vírgula. Carregar com `analysis/lib/io.py`.
- `processed/` — derivados. **Não versionado.**
  - `mestre.parquet` — tabela mestre consolidada (script 00).
  - `mestre_fechada.parquet` — com resíduos de fechamento e flags (script 01).
  - `mestre_tipologia.parquet` — com frentes por classe (script 02).
- `reference/` — dados pequenos de apoio. **Versionado.**
  - `celula_bioma.csv` — cell_id → bioma (consolidar encoding se corrompido).
  - `legenda_col11.csv` — cópia da legenda oficial usada no remap (proveniência).

## Reconstrução

Todos os CSVs de `raw/` são reproduzíveis rodando a cadeia GEE (`gee/01→03b`).
Os `.parquet` de `processed/` são reproduzíveis rodando `analysis/00→02`.

## Onde os dados grandes vivem de fato

TODO: preencher (Google Drive / Zenodo / release do GitHub). Para o paper,
recomenda-se depositar a tabela mestre e os assets-chave num DOI (Zenodo) e citar.
