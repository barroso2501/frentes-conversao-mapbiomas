"""
05_maup_temporal.py  — NOTA + ESQUELETO
Robustez ao recorte temporal. LEIA docs/maup_plano.md antes.

ATENÇÃO — CUSTO: este teste NÃO pode ser feito a partir dos produtos quinquenais.
Os rasters de mudança já colapsaram o tempo em janelas de 5 anos. Testar largura
(4/5/6 anos) e fase (deslocamento dos cortes) exige VOLTAR AO RASTER ANUAL da
Col 11 e re-binar, sobre um SUBCONJUNTO representativo (não o Brasil anual).

Decisão a tomar ANTES de codar (registrar em docs/decisoes.md):
  - Se o paper AFIRMA robustez temporal ou faz claim sobre TIMING de frentes:
    pagar o teste -> gerar rasters de mudança anuais no subconjunto, re-binar em
    larguras e fases, repetir a tipologia, comparar.
  - Se o paper só RECONHECE o MAUP temporal como limitação: não codar; declarar
    em limitacoes.md. (Mas um revisor pode exigir o teste se houver claim de
    timing — então melhor decidir cedo.)

Fluxo se for pago (esqueleto):
  1) GEE: reclassificar (script 01) para TODOS os anos do subconjunto, não só
     marcos. Gerar mudanças ano-a-ano.
  2) re-binar em janelas [largura x fase], somando as transições anuais.
  3) rodar 02_tipologia por combinação de janela.
  4) comparar: as métricas-chave e a ordenação de biomas mudam com largura/fase?
"""

print("MAUP temporal: decisão de custo pendente. Ver docs/maup_plano.md e "
      "docs/decisoes.md antes de implementar. Exige reprocessamento ANUAL "
      "sobre subconjunto — não sai dos produtos quinquenais.")
