/**
 * 03b_estoque.js
 * Estágio 3 (complemento) — estoque de cada classe de foco (nat, pas, tmp) por
 * célula, no INÍCIO de cada período. Necessário para:
 *   - denominador das taxas relativas (perda_rel, entrada_rel) por classe;
 *   - as três identidades de fechamento por classe (estoque_t1 = estoque_t0 + ...).
 *
 * Lê a MESMA definição de classe dos rasters reclassificados (não redefine).
 *
 * O que pode quebrar e como você perceberia:
 *  - Estoque lido de definição diferente da usada na mudança: o fechamento não
 *    bate. Sintoma: resíduo sistemático no script de fechamento. Este script
 *    usa exatamente os assets mb11_cob7_{ano}, então a definição é idêntica.
 */

var K = require('users/SEU_USUARIO/frentes:gee/lib/constantes.js');

var grade = ee.FeatureCollection(K.GRADE_HEX);
var area = ee.Image.pixelArea().divide(10000); // ha

// estoque das 3 classes de foco num ano
function estoqueAno(ano) {
  var cob = ee.Image(K.PREFIXO_RECLASS + ano).select('cobertura');
  return ee.Image.cat([
    area.updateMask(cob.eq(K.CLASSE.NAT)).unmask(0).rename('estoque_nat'),
    area.updateMask(cob.eq(K.CLASSE.PAS)).unmask(0).rename('estoque_pas'),
    area.updateMask(cob.eq(K.CLASSE.TMP)).unmask(0).rename('estoque_tmp')
  ]);
}

// exporta o estoque no início de cada período (usa o ano0 de cada par)
for (var i = 0; i < K.ANOS_MARCO.length - 1; i++) {
  var a0 = K.ANOS_MARCO[i];
  var somas = estoqueAno(a0).reduceRegions({
    collection: grade,
    reducer: ee.Reducer.sum(),
    crs: K.CRS, crsTransform: K.CRS_TRANSFORM, tileScale: 4
  }).map(function (f) { return f.set('ano_ini', a0); });

  Export.table.toDrive({
    collection: somas,
    description: 'estoque_ini_' + a0,
    fileFormat: 'CSV',
    selectors: ['cell_id', 'ano_ini', 'estoque_nat', 'estoque_pas', 'estoque_tmp']
  });
}
