Frentes de conversão e dinâmica de uso — MapBiomas Coleção 11
Análise da dinâmica de frentes de conversão da vegetação nativa e de expansão/consolidação de pastagem e agricultura temporária no Brasil, 1985–2025, a partir da Coleção 11 do MapBiomas.

O trabalho traz granularidade temporal agrupada (janelas quinquenais, não anuais) e granularidade espacial em grade hexagonal, sob controle explícito de MAUP (Modifiable Areal Unit Problem) espacial e temporal, para qualificar consolidação, expansão e as transições dirigidas entre vegetação nativa, pastagem e agricultura.

Este repositório é a continuação e o aprofundamento de uma análise anterior (esquema de 3 classes, grade quadrada de 20 mil ha). O que muda aqui: 7 classes de cobertura, transições dirigidas (não apenas margens), três classes de foco tratadas simetricamente (nativa, pastagem, agri temporária), grade hexagonal multi-resolução e teste de MAUP como parte do argumento, não como apêndice.


O que a análise responde
Onde e quando a vegetação nativa é convertida, e para qual destino (pastagem, agricultura temporária, outros usos agrícolas, outros usos, água).
Onde há expansão de uso sobre a nativa vs. consolidação de uso já estabelecido (a via pastagem → agricultura temporária, que não é frente de conversão e não pode ser somada a ela).
Onde há reversão (regeneração a partir de pastagem ou de agricultura) e qual a sua durabilidade.
Se essas respostas são robustas ao recorte espacial (tamanho e forma da célula) e temporal (largura e fase da janela).
O que a análise NÃO faz (limites por construção)
Não mede transições intra-quinquenais: a janela de 5 anos mede saldo líquido; conversão seguida de reversão dentro da mesma janela aparece como estabilidade. O filtro temporal de 3 anos (w3y) na origem já suprime transições sub-trienais. Toda afirmação de "via de conversão" é via líquida na janela, nunca instantânea. Ver docs/limitacoes.md.
Não rastreia pixels individuais ao longo do tempo — o agregado é por célula. "Consolidação" é persistência líquida na célula, não do pixel.
Não separa o que a Coleção 11 não separou (ex.: parte do Mosaico de Usos, código 21). Ver o tratamento em docs/esquema_reclassificacao.md.


Estrutura do repositório
frentes-conversao-mapbiomas/

├── docs/            Metodologia, decisões congeladas, plano de MAUP, limitações

├── gee/             Google Earth Engine (JavaScript): reclassificação → mudança → tabulação

├── data/            Dados (grandes ignorados pelo git; ver data/README.md)

├── analysis/        Python: tabela mestre, fechamento, tipologia, MAUP, figuras

├── figures/         Figuras geradas para o paper

├── paper/           Manuscrito e outline

└── notebooks/       Exploração (opcional)
Ordem de leitura recomendada (para um colaborador ou revisor)
docs/metodologia.md — a cadeia completa, da fonte às análises.
docs/esquema_reclassificacao.md — as 7 classes (tabela código→classe).
docs/esquema_transicoes.md — as bandas de transição dirigida e a nomenclatura.
docs/decisoes.md — o log de decisões metodológicas (por que o método tem a forma que tem).
docs/maup_plano.md — o desenho dos testes de robustez espacial e temporal.
docs/limitacoes.md — as fragilidades estruturais, abertas.


Cadeia de processamento (visão geral)
Estágio
Ferramenta
Entrada
Saída
1. Reclassificação
GEE
Col 11 classification-ft
9 rasters de 7 classes (anos-marco)
2. Detecção de mudança dirigida
GEE
9 rasters reclassificados
8 rasters de transição (pares quinquenais)
3. Tabulação por célula (hex) + estoque
GEE
rasters de mudança + grade hex
CSVs célula×transição + estoque por classe
4. Análise
Python
tabela mestre
fechamento, tipologia, MAUP, figuras


Toda a cadeia GEE opera na grade nativa do MapBiomas (EPSG:4326, pixel ~30 m em graus decimais), via crsTransform — nunca scale: 30, que força reprojeção e desalinha da estatística oficial. Ver gee/lib/constantes.js.


Reprodutibilidade
Fonte: Col 11 classification-ft, versão 0-4-13-w3y-5 (filtro temporal de 3 anos aplicado na origem).
Assets, versões e proveniência: registrados em docs/metodologia.md §9.
Ambiente Python: requirements.txt.
Dados grandes (rasters, CSVs de exportação, tabela mestre): não versionados no git — ver data/README.md para onde vivem e como reconstruí-los.
Como citar
Ver CITATION.cff.
Licença
Código sob MIT (ver LICENSE). Os dados MapBiomas seguem a licença do próprio MapBiomas (CC-BY-SA) — cite a coleção conforme orientação oficial.
