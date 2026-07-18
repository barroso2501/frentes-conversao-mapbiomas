/**
 * constantes.js — parâmetros e dicionários compartilhados por toda a cadeia GEE.
 *
 * Importe no Code Editor com:
 *   var K = require('users/SEU_USUARIO/frentes:gee/lib/constantes.js');
 * (ajuste o path do require ao seu repositório GEE; o require do GEE não usa
 *  caminhos relativos de disco, e sim o path do asset de script.)
 *
 * O que pode quebrar e como você perceberia:
 *  - Se alguém trocar CRS_TRANSFORM por scale:30 em qualquer redução, os números
 *    deixam de bater com a estatística oficial do MapBiomas. Sintoma: divergência
 *    de área que só aparece ao comparar com o oficial. Mantenha crsTransform.
 *  - Se um código-folha novo da Col 11 não estiver em nenhum bucket abaixo, ele
 *    cai em "não observado" (defaultValue 0) e some. Sintoma: a auditoria de
 *    valores únicos (script 01) acusa código imprevisto. NÃO ignore o aviso.
 */

// ---------------------------------------------------------------------------
// CRS e grade nativa do MapBiomas (pixel ~30 m em graus decimais)
// ---------------------------------------------------------------------------
exports.CRS = 'EPSG:4326';
exports.CRS_TRANSFORM = [
  0.000269494585235856472, 0, -180,
  0, -0.000269494585235856472, 90
];

// ---------------------------------------------------------------------------
// Fonte de cobertura
// ---------------------------------------------------------------------------
exports.ASSET_COBERTURA =
  'projects/mapbiomas-brazil/assets/LAND-COVER/COLLECTION-11/INTEGRATION/classification-ft';
exports.VERSAO = '0-4-13-w3y-5';           // versão terminal da cadeia (filtro w3y)
exports.ANOS_MARCO = [1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025];

// ---------------------------------------------------------------------------
// Reclassificação: código MapBiomas Col 11 -> código interno de 7 classes
//   1 nat | 2 pas | 3 tmp | 4 oag | 5 out | 6 agu | 0 = não observado (mascarado)
// Listas EXAUSTIVAS e NOMINAIS. Nada por exclusão. Ver docs/esquema_reclassificacao.md
// ---------------------------------------------------------------------------
exports.CLASSE = { NAT: 1, PAS: 2, TMP: 3, OAG: 4, OUT: 5, AGU: 6, NOB: 0 };

// Cada entrada: [lista de códigos MapBiomas] -> código interno
exports.REMAP = {
  nat: { codigos: [1, 3, 4, 5, 6, 7, 10, 11, 12, 13, 29, 32, 49, 50, 84], destino: 1 },
  pas: { codigos: [15],                                                    destino: 2 },
  tmp: { codigos: [19, 20, 39, 40, 41, 62],                                destino: 3 },
  oag: { codigos: [9, 21, 35, 36, 46, 47, 48],                             destino: 4 },
  out: { codigos: [22, 23, 24, 25, 30, 75, 91],                            destino: 5 },
  agu: { codigos: [26, 33, 31],                                            destino: 6 }
  // 27 e qualquer imprevisto -> 0 (defaultValue no remap) -> mascarado
};

// Constrói os dois vetores planos que ee.Image.remap() espera (from[], to[]).
exports.remapVetores = function () {
  var from = [];
  var to = [];
  var chaves = Object.keys(exports.REMAP);
  for (var i = 0; i < chaves.length; i++) {
    var grupo = exports.REMAP[chaves[i]];
    for (var j = 0; j < grupo.codigos.length; j++) {
      from.push(grupo.codigos[j]);
      to.push(grupo.destino);
    }
  }
  return { from: from, to: to };
};

// ---------------------------------------------------------------------------
// Transições dirigidas: as 30 bandas de área. Ver docs/esquema_transicoes.md
// Nome da banda = 'ha_<origem>_<destino>'. Cada uma é gerada como:
//   pixelArea onde (t0 == origem) E (t1 == destino), 0 no resto -> Reducer.sum por célula.
// A lista abaixo é a fonte única da verdade para nomes de banda/coluna.
// ---------------------------------------------------------------------------
exports.TRANSICOES = [
  // triângulo de foco (expansão e consolidação)
  { nome: 'ha_nat_pas', de: 1, para: 2 },
  { nome: 'ha_nat_tmp', de: 1, para: 3 },
  { nome: 'ha_pas_tmp', de: 2, para: 3 },
  { nome: 'ha_pas_nat', de: 2, para: 1 },
  { nome: 'ha_tmp_nat', de: 3, para: 1 },
  { nome: 'ha_tmp_pas', de: 3, para: 2 },
  // saídas dos focos para não-focos (fecham perdas)
  { nome: 'ha_nat_oag', de: 1, para: 4 },
  { nome: 'ha_nat_out', de: 1, para: 5 },
  { nome: 'ha_nat_agu', de: 1, para: 6 },
  { nome: 'ha_pas_oag', de: 2, para: 4 },
  { nome: 'ha_pas_out', de: 2, para: 5 },
  { nome: 'ha_pas_agu', de: 2, para: 6 },
  { nome: 'ha_tmp_oag', de: 3, para: 4 },
  { nome: 'ha_tmp_out', de: 3, para: 5 },
  { nome: 'ha_tmp_agu', de: 3, para: 6 },
  // entradas dos focos vindas de não-focos (fecham ganhos)
  { nome: 'ha_oag_nat', de: 4, para: 1 },
  { nome: 'ha_out_nat', de: 5, para: 1 },
  { nome: 'ha_agu_nat', de: 6, para: 1 },
  { nome: 'ha_oag_pas', de: 4, para: 2 },
  { nome: 'ha_out_pas', de: 5, para: 2 },
  { nome: 'ha_agu_pas', de: 6, para: 2 },
  { nome: 'ha_oag_tmp', de: 4, para: 3 },
  { nome: 'ha_out_tmp', de: 5, para: 3 },
  { nome: 'ha_agu_tmp', de: 6, para: 3 }
  // fronteira com a máscara (nob) é tratada separadamente no script 02,
  // pois exige lógica de máscara (não é comparação classe-a-classe simples):
  //   ha_nat_nob, ha_pas_nob, ha_tmp_nob  (saída rastreada)
  //   ha_nob_nat, ha_nob_pas, ha_nob_tmp  (termo de ajuste)
];

// Classes de foco (recebem tratamento simétrico completo na análise)
exports.FOCO = [1, 2, 3]; // nat, pas, tmp

// ---------------------------------------------------------------------------
// Paths de saída (ajuste ao seu projeto GEE)
// ---------------------------------------------------------------------------
exports.PREFIXO_RECLASS = 'projects/SEU_PROJETO/assets/mb11_cob7_';       // + ano
exports.PREFIXO_CHANGE  = 'projects/SEU_PROJETO/assets/mb11_change7_';     // + ano1_ano2
exports.GRADE_HEX       = 'projects/SEU_PROJETO/assets/grade_hex_20mil';   // definir resolução
exports.GRADE_QUAD      = 'projects/ee-barroso2501/assets/grade_20mil_ha'; // herdada (MAUP zoneamento)
