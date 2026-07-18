# Limitações estruturais

Apresentadas abertamente. Cada uma anota **o que é**, **em que direção enviesa**,
e **o que fazer a respeito** (mitigar, escopar, ou apenas declarar).

## 1. Mudança líquida, não bruta (MAUP temporal por construção)
Janelas de 5 anos medem saldo. Conversão seguida de reversão dentro da mesma
janela aparece como estabilidade. O filtro `w3y` na origem já suprime transições
sub-trienais.
**Direção do viés:** subestima turnover; empurra durabilidade da reversão para o
lado conservador.
**O que fazer:** toda afirmação de "via de conversão" é *via líquida na janela*.
Se o paper afirmar timing, pagar o MAUP temporal (ver maup_plano.md).

## 2. Agregado por célula não rastreia pixels
"Consolidação" e "durabilidade" são persistência líquida **na célula**, não do
pixel. Uma célula pode ter ganho num canto e perda em outro que se cancelam.
**O que fazer:** nomear a métrica como persistência líquida na célula; não afirmar
persistência de pixel específico.

## 3. Mosaico de Usos (21) — resíduo na interface nativa↔uso
A Col 11 reatribuiu ~2/3 do 21 da Col 10 a pas/tmp; o resíduo é mosaico de
pequena propriedade e transição uso–natural, e mora justamente na fronteira que
o paper estuda.
**Direção do viés:** frentes pas/tmp podem subestimar dinâmica de fronteira onde
21 é alto (suspeitos: Caatinga, franjas de Mata Atlântica).
**O que fazer:** quantificar `nativa↔21` e área de 21 por bioma; escopar a
narrativa pas/tmp de acordo. Análise obrigatória em `analysis/04_maup_espacial.py`
(bloco de diagnóstico do 21).

## 4. Fronteira nativa ↔ pastagem em biomas abertos
A discriminação campo-natural (11, 12) vs. pastagem-plantada (15) é fraqueza
conhecida do MapBiomas no Pampa e no campo cerrado. Antes, ruído absorvido em
"estabilidade nativa". Agora alimenta diretamente `ha_nat_pas`.
**Direção do viés:** pode fabricar "expansão de pastagem" que é oscilação de
rótulo do produto.
**O que fazer:** tratar como limitação de primeira ordem; reportar Pampa/campo
cerrado à parte; considerar restringir claims fortes de pas aos biomas onde a
fronteira 11/12↔15 é robusta.

## 5. Definição ampla de vegetação nativa
Inclui formações campestres, savânicas e naturais não florestais. Adequada à
pergunta multi-bioma, mas incomparável a PRODES e produtos centrados em floresta
sem alinhamento de definições.
**O que fazer:** declarar; não comparar números diretamente com PRODES.

## 6. Assimetria da máscara (não observado)
`foco→nob` é perda rastreável; `nob→foco` não tem origem definida.
**O que fazer:** `nob→foco` entra como termo de ajuste no fechamento, não como
ganho; resíduo do fechamento por célula concentra-se aqui e é nomeado.

## 7. Dominância amazônica na amostra
A Amazônia é ~50% das células; todo agregado nacional é fortemente influenciado
por ela.
**O que fazer:** todas as análises por bioma ou normalizadas.

## 8. Unidade territorial categórica (se reutilizada)
Regime fundiário por predominância, não fração. Composições são robustas;
inferência intra-célula não.

## 9. Confiança assimétrica entre biomas na durabilidade
O limiar de 10 anos distingue pousio de regeneração nos biomas florestais, mas é
mais permissivo nos abertos (Pampa/Caatinga), onde turnover rápido pode fazer
parte da "consolidação" ser oscilação de uso.
