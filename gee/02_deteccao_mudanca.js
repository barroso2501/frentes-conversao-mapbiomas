/**
 * 02_deteccao_mudanca.js
 * Estágio 2 — para cada par de anos-marco, gera as 30 bandas de área de
 * transição dirigida (ver docs/esquema_transicoes.md).
 *
 * Ideia central (diferente do exercício anterior, que usava int8 -2..+2):
 *   para cada transição origem->destino, cria-se uma banda de área que vale
 *   pixelArea onde (t0 == origem) E (t1 == destino), e 0 no resto. Ao somar por
 *   célula (script 03), cada banda vira uma coluna plana de hectares.
 *
 * O que pode quebrar e como você perceberia:
 *  - Sem máscara de validade: pixel válido num ano e no-data no outro seria
 *    contado como transição espúria. Sintoma: áreas de transição infladas em
 *    bordas de tiles. A máscara `valido` abaixo previne isso.
 *  - pixelArea em EPSG:4326 sem crsTransform coerente: área varia com latitude.
 *    Sintoma: soma de bandas != área da célula. O bloco de sanidade acusa.
 *  - Esquecer as bandas de máscara (nob): o fechamento por classe (análise) não
 *    bate. Sintoma: resíduo grande e sistemático no script de fechamento.
 */

var K = require('users/SEU_USUARIO/frentes:gee/lib/constantes.js');

var area = ee.Image.pixelArea().divide(10000); // m² -> hectares

// gera as 30 bandas para um par (ano0, ano1)
function bandasTransicao(ano0, ano1) {
  var t0 = ee.Image(K.PREFIXO_RECLASS + ano0).select('cobertura');
  var t1 = ee.Image(K.PREFIXO_RECLASS + ano1).select('cobertura');

  // máscara de validade: só computa onde AMBOS os anos têm dado
  var valido = t0.mask().and(t1.mask());

  var bandas = [];

  // (1) as 24 transições classe-a-classe entre classes reais que tocam foco
  K.TRANSICOES.forEach(function (tr) {
    var ocorre = t0.eq(tr.de).and(t1.eq(tr.para)).and(valido);
    bandas.push(area.updateMask(ocorre).unmask(0).rename(tr.nome));
  });

  // (2) fronteira com a máscara — 6 bandas, lógica de máscara (não classe-a-classe)
  // saída rastreada: era foco em t0 e virou no-data em t1
  K.FOCO.forEach(function (c, i) {
    var nomeSai = ['ha_nat_nob', 'ha_pas_nob', 'ha_tmp_nob'][i];
    var saiu = t0.eq(c).and(t1.mask().not()).and(t0.mask());
    bandas.push(area.updateMask(saiu).unmask(0).rename(nomeSai));

    // termo de ajuste: era no-data em t0 e "apareceu" como foco em t1
    var nomeEnt = ['ha_nob_nat', 'ha_nob_pas', 'ha_nob_tmp'][i];
    var apareceu = t0.mask().not().and(t1.eq(c)).and(t1.mask());
    bandas.push(area.updateMask(apareceu).unmask(0).rename(nomeEnt));
  });

  return ee.Image.cat(bandas).set({
    periodo: ano0 + '_' + ano1,
    fonte_versao: K.VERSAO,
    n_bandas: bandas.length
  });
}

// --- bloco de sanidade: numa janela pequena, as áreas fazem sentido? --------
var teste = bandasTransicao(2015, 2020);
var janela = ee.Geometry.Rectangle([-52, -14, -50, -12]); // Cerrado central
print('SANIDADE — soma de área por banda numa janela do Cerrado (ha):',
  teste.reduceRegion({
    reducer: ee.Reducer.sum(),
    geometry: janela,
    crs: K.CRS, crsTransform: K.CRS_TRANSFORM,
    maxPixels: 1e12, tileScale: 4
  }));
// Esperado: ha_nat_pas e ha_nat_tmp dominantes; reversões menores; nob residual.

// --- exporta os 8 pares ------------------------------------------------------
for (var i = 0; i < K.ANOS_MARCO.length - 1; i++) {
  var a0 = K.ANOS_MARCO[i];
  var a1 = K.ANOS_MARCO[i + 1];
  var img = bandasTransicao(a0, a1);
  Export.image.toAsset({
    image: img,
    description: 'mb11_change7_' + a0 + '_' + a1,
    assetId: K.PREFIXO_CHANGE + a0 + '_' + a1,
    crs: K.CRS,
    crsTransform: K.CRS_TRANSFORM,
    region: ee.Geometry.Rectangle([-74, -34, -34, 6]),
    maxPixels: 1e13,
    pyramidingPolicy: { '.default': 'mean' } // bandas de ÁREA: mean é ok (contínuo)
  });
}
