# Plano de MAUP — robustez espacial e temporal

O MAUP (Modifiable Areal Unit Problem) é tratado aqui como **parte do argumento**,
não como apêndice. Ele tem **dois eixos independentes** — trocar quadrado por
hexágono, sozinho, **não é** um teste de MAUP; é uma única realização de zoneamento.

```
MAUP = eixo ESCALA (tamanho da célula) × eixo ZONEAMENTO (forma/orientação/offset)
```

O teste é considerado bem-sucedido se as conclusões **qualitativas** (ordenação
de biomas, existência dos regimes de frente ativa/terminal, direção das relações
expansão↔consolidação) **sobrevivem** à variação de escala e zoneamento. Se
sobrevivem, isso **é** o resultado de robustez e entra no paper.

---

## MAUP espacial

### Eixo ZONEAMENTO (mais barato — usa dados já existentes)

Você **já tem** a grade quadrada de 20 mil ha do exercício anterior. Ela vira a
comparação de zoneamento de graça:

- Comparar as distribuições de `perda_abs`, `perda_rel`, e as contagens de frente
  (ativa/terminal) e de transições dirigidas entre **grade quadrada ↔ grade
  hexagonal de área equivalente** (~20 mil ha).
- Métrica de concordância: correlação de rank das células por bioma, e
  estabilidade das contagens de tipologia (quantas células mudam de classe entre
  as duas malhas).

### Eixo ESCALA (requer ≥3 resoluções de hexágono)

- Gerar a grade hexagonal em **pelo menos 3 resoluções** (ex.: ~5 mil, ~20 mil,
  ~80 mil ha).
- Reprocessar a tabulação (Estágio 3) em cada resolução — a reclassificação e a
  detecção de mudança (Estágios 1–2) **não** mudam; só a tabulação por célula.
- Reportar como frente_ativa/terminal e as proporções de transição se movem com
  a escala.

#### Decisão de grade hexagonal — **aberta**, ver opções

Duas opções, com trade-offs reais. **Não assumida — decidir antes de gerar.**

**Opção A — H3 (Uber), hierárquico aperture-7.**
- *Prós:* resoluções aninhadas nativas (cada nível ~7× a área do mais fino),
  ideal para o eixo escala; cell_id determinístico (índice H3), sem depender de
  `@row_number` do QGIS (que é frágil e não reproduzível); bibliotecas maduras
  (`h3-py`, `h3` no GEE via bibliotecas de terceiros ou pré-computado).
- *Contras:* as resoluções H3 **não batem** 20 mil ha exatamente. Áreas médias
  aproximadas: **res 5 ≈ 252 km² (~25,2 mil ha)**, **res 6 ≈ 36 km² (~3,6 mil ha)**,
  **res 4 ≈ 1.770 km²**. Nenhuma casa 20 mil ha. Ou se aceita as áreas nativas do
  H3 (e a comparação com a quadrada de 20 mil ha vira aproximada), ou se usa H3
  só para o eixo escala e a quadrada para o zoneamento.
- *Verificar:* áreas médias exatas por resolução na latitude do Brasil — os
  números acima são globais aproximados.

**Opção B — grade hexagonal equal-area customizada.**
- *Prós:* controla o tamanho exato (pode casar 20 mil ha com a quadrada);
  comparação de zoneamento fica limpa.
- *Contras:* sem hierarquia aninhada nativa (as 3 resoluções de escala não são
  subdivisões exatas umas das outras); cell_id precisa ser gerado e versionado
  com cuidado; mais trabalho de construção (QGIS/PostGIS/`geopandas`).

**Recomendação:** H3 para o eixo escala (aproveita a hierarquia) + a grade
quadrada existente para o eixo zoneamento. Registrar a escolha e a área média
efetiva de cada resolução no metadado da grade. **Confirmar a decisão antes de
gerar os assets.**

---

## MAUP temporal — **custo alto, dimensionar antes de prometer**

Os produtos são quinquenais (rasters de anos-marco). **Testar a janela temporal
exige voltar ao raster anual e re-binar — não dá para fazer a partir dos marcos.**

Dois sub-eixos:

- **Largura** da janela: 4, 5, 6 anos.
- **Fase** (offset dos cortes): deslocar o início dos cortes. Uma frente que ativa
  em 1989 e satura em 1993 é cortada ao meio pela grade temporal quinquenal
  herdada dos anos-marco MapBiomas.

**Custo:** reprocessar a reclassificação e a detecção de mudança em resolução
**anual** sobre um **subconjunto representativo** de células/biomas (não o Brasil
inteiro anual). É a peça mais cara do plano.

**Decisão a tomar cedo:**

- Se o paper **afirma** robustez ao recorte temporal ou faz claim sobre *timing*
  de frentes → **pagar** o teste (subconjunto anual).
- Se o paper apenas **reconhece** o MAUP temporal como limitação → barato e
  honesto, mas um revisor pode exigir o teste caso haja qualquer afirmação sobre
  quando as frentes ocorrem.

Registrar a decisão em `docs/decisoes.md` quando tomada.

---

## Saídas esperadas do MAUP (para o paper)

- Tabela/figura de estabilidade das contagens de tipologia entre malhas (zoneamento).
- Curva de sensibilidade das métricas-chave à escala (3 resoluções).
- Se feito: sensibilidade à largura e fase temporal no subconjunto.
- Uma frase de veredito por eixo: robusto / robusto com ressalva / sensível.
