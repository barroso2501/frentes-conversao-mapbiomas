# Outline do manuscrito

## Posicionamento — o que é novo (e o que não é)

A literatura de consolidação de fronteira pasto→lavoura no Cerrado/Amazônia via
MapBiomas já é densa (linha Zalles, Souza et al./MapBiomas, estudos de MATOPIBA).
**O hexágono não é a novidade.** A contribuição é a combinação:

1. **Expansão e consolidação como leituras de uma mesma matriz de transição
   dirigida** por célula e janela — com `pasto→lavoura` explicitamente separado
   de conversão de nativa (não somado a ela).
2. **Durabilidade da reversão diferenciada por origem** (pasto vs lavoura) e por
   bioma.
3. **MAUP espacial e temporal como parte do argumento**, não apêndice — a
   robustez ao recorte é reportada, não assumida.
4. **Frente por conjunção** (absoluta ∧ relativa) + regime terminal ancorado
   empiricamente, e o **resultado negativo** da assinatura da Reserva Legal.

Vender por (3) e (1): controle de MAUP + separação medida expansão/consolidação.

## Estrutura

### 1. Introdução
- Frentes de conversão e a fronteira agropecuária brasileira; lacuna: granularidade
  temporal agrupada + espacial sob controle de MAUP; a distinção expansão vs
  consolidação raramente é *medida* (mais frequentemente inferida de margens).

### 2. Dados e métodos
- 2.1 Fonte: Col 11, versão terminal; grade nativa via crsTransform.
- 2.2 Esquema de 7 classes (tabela); foco nat/pas/tmp; contexto oag/out/agu/nob.
- 2.3 Transições dirigidas (30 bandas); por que fluxo e não margem.
- 2.4 Grade hexagonal (H3 vs equal-area — justificar a escolha).
- 2.5 Tipologia: frente por conjunção, terminal, durabilidade; limiares por classe.
- 2.6 Verificação de consistência (fechamento por classe + global).
- 2.7 Desenho de MAUP (zoneamento, escala, temporal).

### 3. Resultados
- 3.1 Padrão nacional e por bioma da conversão de nativa por destino.
- 3.2 Expansão (nativa→pasto, nativa→lavoura) vs consolidação (pasto→lavoura):
  onde cada regime domina, no tempo e no espaço.
- 3.3 Reversão e durabilidade por origem e bioma.
- 3.4 Robustez: MAUP espacial (e temporal, se pago). Veredito por eixo.
- 3.5 Diagnóstico do mosaico (21) por bioma — escopo de validade da narrativa.

### 4. Discussão
- Onde a leitura pasto↔lavoura é robusta e onde é cauta (Caatinga/21; Pampa/
  fronteira campo↔pastagem).
- Limite líquido-na-janela; o que o produto não vê (turnover sub-quinquenal).
- Comparabilidade (e incomparabilidade) com PRODES e produtos florestais.

### 5. Conclusão

## Alvos de periódico (a decidir)
- *Land Use Policy*, *Remote Sensing of Environment*, *Journal of Environmental
  Management*, *Land*, *Perspectives in Ecology and Conservation*. Escolher pelo
  peso relativo entre método (RSE) e implicação de política (LUP).

## Figuras planejadas (ver figures/)
1. Fluxograma da cadeia (7 classes → transições → tipologia).
2. Mapa hexagonal de regime dominante por célula (expansão/consolidação/reversão/estável).
3. Séries temporais por bioma: nativa→pasto, nativa→lavoura, pasto→lavoura.
4. MAUP: curva de sensibilidade à escala; concordância quad↔hex.
5. Durabilidade da reversão por origem e bioma.
6. Diagnóstico do mosaico (21) por bioma.
