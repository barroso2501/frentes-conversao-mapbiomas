/**
 * 01_reclassificacao.js
 * Estágio 1 — reclassifica a Col 11 em 7 classes, para os 9 anos-marco.
 *
 * O que este script faz, em blocos:
 *  A) carrega o mosaico da versão terminal da Col 11;
 *  B) para cada ano-marco, remapeia os códigos MapBiomas -> 7 classes internas;
 *  C) roda uma AUDITORIA de valores únicos (garante que nada cai em "sem dado"
 *     por engano) antes de exportar;
 *  D) exporta cada raster reclassificado como asset.
 *
 * O que pode quebrar e como você perceberia:
 *  - Versão errada da coleção: renderiza com buracos sem dar erro. Sintoma: área
 *    nacional muito abaixo do esperado. Confira K.VERSAO.
 *  - Código-folha novo fora do REMAP: cai em 0 (mascarado) e some. Sintoma: o
 *    print da auditoria (bloco C) lista um código que não está em nenhum bucket.
 *  - pyramidingPolicy diferente de 'mode': valores intermediários aparecem em
 *    zoom baixo. Sintoma: classes "fantasma" ao inspecionar o asset com zoom out.
 */

var K = require('users/SEU_USUARIO/frentes:gee/lib/constantes.js');

// --- A) mosaico da versão terminal -----------------------------------------
var colecao = ee.ImageCollection(K.ASSET_COBERTURA)
  .filter(ee.Filter.eq('version', K.VERSAO))
  .mosaic();

// --- vetores de remap (from[], to[]) a partir do dicionário central ---------
var v = K.remapVetores();

// função que reclassifica UM ano-marco
function reclassificaAno(ano) {
  var banda = 'classification_' + ano;
  var original = colecao.select(banda);

  // remap com defaultValue 0 = "não observado"; depois mascara os zeros
  var reclass = original
    .remap(v.from, v.to, 0)          // qualquer código imprevisto -> 0
    .updateMask(original.remap(v.from, v.to, 0).neq(0))
    .rename('cobertura')
    .uint8();

  return reclass.set({
    ano: ano,
    fonte_versao: K.VERSAO,
    esquema: '7 classes: 1 nat 2 pas 3 tmp 4 oag 5 out 6 agu',
    data_processamento: ee.Date(Date.now())
  });
}

// --- C) AUDITORIA: quais códigos MapBiomas aparecem no raster? --------------
// Rode isto ANTES de exportar. Compare a lista impressa com a união de todos os
// códigos em K.REMAP. Qualquer código presente aqui e ausente lá vira "sem dado".
var anoAudit = 2020; // um ano com uso consolidado costuma expor todos os códigos
var histograma = colecao.select('classification_' + anoAudit).reduceRegion({
  reducer: ee.Reducer.frequencyHistogram(),
  geometry: ee.Geometry.Rectangle([-74, -34, -34, 6]), // bbox Brasil aproximada
  crs: K.CRS,
  crsTransform: K.CRS_TRANSFORM,
  maxPixels: 1e13,
  bestEffort: true,       // amostra se necessário; para auditoria completa, tile a mão
  tileScale: 4
});
print('AUDITORIA — códigos presentes em ' + anoAudit + ' (chaves do histograma):',
      histograma);
// TODO: compare manualmente as chaves com K.REMAP. Se a coleção for grande demais
// para bestEffort, rode a auditoria por tile e una os resultados.

// --- D) exporta os 9 anos-marco --------------------------------------------
K.ANOS_MARCO.forEach(function (ano) {
  var img = reclassificaAno(ano);
  Export.image.toAsset({
    image: img,
    description: 'mb11_cob7_' + ano,
    assetId: K.PREFIXO_RECLASS + ano,
    crs: K.CRS,
    crsTransform: K.CRS_TRANSFORM,   // NUNCA scale:30 — ver constantes.js
    region: ee.Geometry.Rectangle([-74, -34, -34, 6]),
    maxPixels: 1e13,
    pyramidingPolicy: { '.default': 'mode' } // obrigatório p/ categórico
  });
});
