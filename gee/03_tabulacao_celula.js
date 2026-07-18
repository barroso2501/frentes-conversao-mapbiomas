/**
 * 03_tabulacao_celula.js
 * Estágio 3 — soma as 30 bandas de transição por célula da grade hexagonal,
 * para cada período. Uma linha por célula; uma coluna por banda.
 *
 * Arquitetura: colunas planas via Reducer.sum() com grupos = células. Evita o
 * grouped reducer que gera lista aninhada e CSV difícil de desempilhar.
 *
 * O que pode quebrar e como você perceberia:
 *  - cell_id não único ou ausente: a junção por período (na análise) falha ou
 *    duplica linhas. Sintoma: contagem de linhas != n_células. Garanta cell_id
 *    único na grade antes do upload.
 *  - reduceRegions estourando memória: para grade nacional, LOTEIE por faixa de
 *    cell_id (ver LOTE abaixo) e concatene os CSVs na análise.
 *  - Grade hex ainda não definida: ver docs/maup_plano.md — a resolução/tipo
 *    (H3 vs equal-area custom) é decisão aberta. Este script assume um asset de
 *    grade com um campo 'cell_id' inteiro/único.
 */

var K = require('users/SEU_USUARIO/frentes:gee/lib/constantes.js');

var grade = ee.FeatureCollection(K.GRADE_HEX); // precisa ter campo 'cell_id'

// tabula UM período
function tabulaPeriodo(ano0, ano1) {
  var img = ee.Image(K.PREFIXO_CHANGE + ano0 + '_' + ano1);

  // soma todas as bandas de área por célula
  var somas = img.reduceRegions({
    collection: grade,
    reducer: ee.Reducer.sum(),
    crs: K.CRS,
    crsTransform: K.CRS_TRANSFORM,
    tileScale: 4
  });

  // mantém só cell_id + as colunas de área (descarta geometria no export)
  return somas.map(function (f) {
    return f.set('periodo', ano0 + '_' + ano1);
  });
}

// --- LOTE (opcional): para grade nacional, exporte por faixa de cell_id ------
// var LOTE = { min: 0, max: 10000 };
// grade = grade.filter(ee.Filter.and(
//   ee.Filter.gte('cell_id', LOTE.min), ee.Filter.lt('cell_id', LOTE.max)));

// --- exporta os 8 períodos ---------------------------------------------------
for (var i = 0; i < K.ANOS_MARCO.length - 1; i++) {
  var a0 = K.ANOS_MARCO[i];
  var a1 = K.ANOS_MARCO[i + 1];
  Export.table.toDrive({
    collection: tabulaPeriodo(a0, a1),
    description: 'grade_change_' + a0 + '_' + a1,
    fileFormat: 'CSV',
    selectors: ['cell_id', 'periodo'].concat(
      K.TRANSICOES.map(function (t) { return t.nome; })
    ).concat(
      ['ha_nat_nob', 'ha_pas_nob', 'ha_tmp_nob',
       'ha_nob_nat', 'ha_nob_pas', 'ha_nob_tmp']
    )
  });
}
