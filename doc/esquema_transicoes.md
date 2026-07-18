# Esquema de transições dirigidas

Este é o coração do encoding. Diferente do exercício anterior (que media apenas
o saldo binário nativa↔antrópico), aqui medimos **fluxos dirigidos** origem→destino,
porque é a única forma de distinguir **expansão** (`nativa → uso`) de
**consolidação** (`pastagem → agricultura`, que **não** é frente de conversão).

O fluxo dirigido é **medido, não inferido**: no nível de pixel, "era nativa em
t0 e pastagem em t1" é um fato do cruzamento `t0 × t1`. Não há penalidade
inferencial de tabela subdeterminada — ao contrário de tentar recuperar o miolo
da matriz a partir das margens, o que é impossível.

## Códigos de classe (curtos, para nomes de banda)

| curto | classe | foco? |
|---|---|---|
| `nat` | vegetação natural | sim |
| `pas` | pastagem plantada | sim |
| `tmp` | agricultura temporária | sim |
| `oag` | outros agrícolas | não |
| `out` | outro | não |
| `agu` | água | não |
| `nob` | não observado (máscara) | — |

## Princípio: as três classes de foco tratadas de forma completa e simétrica

Cada classe de foco é decomposta em **entradas** e **saídas** para *todas* as
outras classes reais + máscara. Isso dá **fechamento por classe** (uma auditoria
independente por foco), além do fechamento global.

Transições necessárias = todos os pares ordenados que **tocam** pelo menos uma
classe de foco. Entre as 6 classes reais há 6×5 = 30 pares ordenados; os 6 que
**não** tocam foco (entre oag/out/agu) são resolvidos por delta de estoque, não
como banda. Sobram **24 bandas dirigidas** entre classes reais, mais **6 bandas
de fronteira com a máscara** (foco↔nob) = **30 bandas de área** por célula-período.

## As 30 bandas (nome de coluna = área em ha da transição na célula-período)

### Triângulo de foco (6) — expansão e consolidação
| banda | transição | leitura |
|---|---|---|
| `ha_nat_pas` | nativa → pastagem | **expansão** de pastagem sobre nativa |
| `ha_nat_tmp` | nativa → agri temp | **expansão** de agricultura sobre nativa |
| `ha_pas_tmp` | pastagem → agri temp | **consolidação** (intensificação; NÃO é frente) |
| `ha_pas_nat` | pastagem → nativa | reversão / regeneração a partir de pasto |
| `ha_tmp_nat` | agri temp → nativa | reversão / regeneração a partir de agricultura |
| `ha_tmp_pas` | agri temp → pastagem | des-intensificação / abandono para pasto |

### Saídas dos focos para não-focos (9) — fecham as PERDAS de cada foco
| banda | transição |
|---|---|
| `ha_nat_oag` | nativa → outros agrícolas (inclui silvicultura, perene, mosaico 21) |
| `ha_nat_out` | nativa → outro (urbano, mineração, infraestrutura, praia/duna) |
| `ha_nat_agu` | nativa → água (represamento, pulso hidrológico) |
| `ha_pas_oag` | pastagem → outros agrícolas |
| `ha_pas_out` | pastagem → outro |
| `ha_pas_agu` | pastagem → água |
| `ha_tmp_oag` | agri temp → outros agrícolas |
| `ha_tmp_out` | agri temp → outro |
| `ha_tmp_agu` | agri temp → água |

### Entradas dos focos vindas de não-focos (9) — fecham os GANHOS de cada foco
| banda | transição |
|---|---|
| `ha_oag_nat` | outros agrícolas → nativa |
| `ha_out_nat` | outro → nativa |
| `ha_agu_nat` | água → nativa |
| `ha_oag_pas` | outros agrícolas → pastagem |
| `ha_out_pas` | outro → pastagem |
| `ha_agu_pas` | água → pastagem |
| `ha_oag_tmp` | outros agrícolas → agri temp |
| `ha_out_tmp` | outro → agri temp |
| `ha_agu_tmp` | água → agri temp |

### Fronteira com a máscara (6) — assimétrica por construção
| banda | transição | tratamento |
|---|---|---|
| `ha_nat_nob` | nativa → não observado | **saída rastreada** (perda para observação) |
| `ha_pas_nob` | pastagem → não observado | saída rastreada |
| `ha_tmp_nob` | agri temp → não observado | saída rastreada |
| `ha_nob_nat` | não observado → nativa | **termo de ajuste** no fechamento |
| `ha_nob_pas` | não observado → pastagem | termo de ajuste |
| `ha_nob_tmp` | não observado → agri temp | termo de ajuste |

> **Assimetria da máscara.** `foco → nob` é rastreável: o pixel era da classe e
> saiu da observação — perda legítima. `nob → foco` **não tem origem definida**:
> um pixel que "aparece" vindo de no-data não tem classe anterior conhecida.
> Logo `nob → foco` **não** é ganho ecológico/produtivo; é termo de ajuste. Se
> o fechamento por célula não bater, é aqui que mora o resíduo — e por isso ele
> é nomeado, não diluído.

## Colunas adicionais por célula-período (estoque e derivadas)

Além das 30 bandas de área:

| coluna | definição |
|---|---|
| `estoque_nat_ini` | estoque de nativa no início do período (ha) |
| `estoque_pas_ini` | estoque de pastagem no início do período (ha) |
| `estoque_tmp_ini` | estoque de agri temp no início do período (ha) |
| `ha_valida` | área com transição observável na célula (todas as classes) |
| `cell_id` | identificador da célula (hex) |
| `periodo` | par de anos-marco (ex.: `1985_1990`) |

**Atenção:** `ha_valida` **não é** o denominador das taxas relativas. As
relativas usam o **estoque inicial da própria classe** (ou área conversível,
conforme a decisão por classe em `docs/decisoes.md`, item CAL-2). Usar
`perda / ha_valida` reintroduz o viés de célula grande e cheia.

## Encoding no GEE (nota de implementação)

O esquema anterior codificava mudança em `int8` (−2..+2). **Isso morre aqui** —
com 6 classes há 24+ transições e nenhum inteiro pequeno as representa. A
arquitetura correta é a que o projeto já usa para tabulação: **uma banda de área
por transição** (`ee.Image.pixelArea()` mascarada onde a transição ocorre, 0 no
resto), e `Reducer.sum()` sobre a grade → colunas planas, uma linha por célula.
Escala de 5 para 30 bandas sem mudança conceitual. Ver `gee/02_deteccao_mudanca.js`.

`ee.Image.pixelArea()` é obrigatório (não contagem de pixels): em EPSG:4326 o
pixel tem tamanho fixo em graus e a área real varia com a latitude (erro
sistemático crescente do Sul para o Norte se ignorado).
