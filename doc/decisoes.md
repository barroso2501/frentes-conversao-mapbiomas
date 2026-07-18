# Log de decisões metodológicas

Registro das escolhas entre alternativas defensáveis, com o teste crítico
aplicado antes de registrar. Cada decisão anota **o que foi escolhido**, **a
alternativa rejeitada**, e **o que um revisor cético atacaria**. Formato
inspirado em ADR (Architecture Decision Record).

---

## ARQ — Arquitetura de encoding

### ARQ-1. Fluxos dirigidos, não apenas margens
**Escolha:** medir transições origem→destino (30 bandas), não somente entrada/
saída líquida por classe (margens).
**Rejeitado:** três bases paralelas de margens (nativa, pasto, tmp) combinadas
por cruzamento booleano.
**Por quê:** margens não distinguem `pasto→tmp` (consolidação) de
`nativa→pasto + tmp→nativa` (mesma assinatura de margem, processo oposto). O
miolo da matriz é irrecuperável a partir das margens (inferência ecológica
subdeterminada). O fluxo dirigido é medido no cruzamento de pixel, sem custo
inferencial.
**Ataque do revisor:** "vocês afirmam *via* de conversão a partir de agregado
por célula." Resposta: a via é medida no pixel; o agregado por célula soma vias
medidas, não infere. **Ressalva que permanece:** é via *líquida na janela*,
nunca instantânea (ver LIM temporal).

### ARQ-2. Simetria plena das três classes de foco
**Escolha:** decompor nativa, pastagem e agri temporária de forma completa
(entrada e saída para todas as classes), gerando **fechamento por classe**.
**Rejeitado:** decompor só a nativa; pasto/tmp com "triângulo + resíduo agregado".
**Por quê:** com resíduo agregado, uma queda de pastagem não explicada por
`pas→tmp` nem `pas→nat` não seria atribuível (pas→silvicultura? pas→urbano?) —
reintroduz a ambiguidade margem-vs-fluxo só para pasto. Simetria plena custa
~9 bandas a mais e compra três identidades de conservação independentes.
**Ataque do revisor:** nenhum estrutural; o custo é largura de tabela.

### ARQ-3. Classes de contexto entram no fechamento, não na tipologia
**Escolha:** outros_agri, outro, água e não-obs entram como estoque dinâmico e
na identidade de conservação por célula, mas **não** viram frente/durabilidade.
**Por quê:** são informativos mas não são o foco. Contudo `nativa→contexto` é
**perda real de nativa** e precisa ser contabilizada (senão o denominador da
perda encolhe silenciosamente e regride frente ao número oficial).
**Ataque do revisor:** "silvicultura e perene não são marginais." Correto —
por isso `nativa→oag` é destino contabilizado, e a área de oag por bioma é
reportada (ver CLS-2).

---

## CLS — Esquema de classes

### CLS-1. Sete classes (ver esquema_reclassificacao.md)
**Escolha:** nat / pas / tmp / oag / out / agu / nob.
**Ataque do revisor:** "vegetação natural" ampla demais (inclui campo/savana).
Resposta: adequado à pergunta multi-bioma; incomparável a PRODES sem alinhamento
— declarado em limitações.

### CLS-2. Mosaico de Usos (21) em "outros agrícolas"
**Escolha:** 21 → oag (contexto), não redistribuído.
**Por quê:** a Col 11 já reatribuiu ~2/3 do 21 da Col 10 para pas/tmp; o resíduo
é mosaico de pequena propriedade e transição uso–natural. Qualquer redistribuição
do resíduo seria inventada.
**Ataque do revisor:** o resíduo de 21 mora na interface nativa↔uso — o objeto do
paper — e some da tipologia. **Ação obrigatória:** quantificar `nativa↔21` e
área de 21 por bioma antes de afirmar; escopar a narrativa pas/tmp onde 21 for
alto. Ver limitacoes.md.

### CLS-3. Terminologia "natural" vs "nativa"
**Pendência:** o esquema diz "Vegetação natural"; a métrica de estoque e o doc
anterior dizem "nativa". **Padronizar um dos dois** em todo o repositório e paper
antes de congelar. Recomendação: "vegetação nativa" (consistente com o histórico
do projeto e com a literatura MapBiomas).

---

## CAL — Calibração (pendências de execução, não de arquitetura)

### CAL-1. Limiares de frente recalibrados por classe
**Decisão:** os pisos `(perda_abs > 300 ha) E (perda_rel > 12%)` foram calibrados
na distribuição da **nativa**. Pastagem (mancha pequena, dispersa) e agri temp
(bloco grande, concentrado — MATOPIBA) têm distribuições distintas. **Cada frente
recebe seus próprios limiares**, calibrados na própria distribuição e justificados
no paper. Não reusar 300/12% cego.

### CAL-2. Denominador da relativa por classe
**Decisão pendente, explícita por classe.** Para *perda*, denominador = estoque
inicial da própria classe. Para *ganho/entrada* (ex.: "frente de pastagem"),
usar estoque inicial da própria classe **estoura** em célula com pouco estoque
inicial (artefato de franja). Denominador honesto provável = **área conversível
da célula** ou **estoque nativo inicial**. Decidir e registrar por classe antes
de rodar a tipologia.

### CAL-3. Durabilidade: mesmo teste, justificativas diferentes
**Decisão:** o teste de persistência ≥10 anos (dois quinquênios) transfere
estruturalmente para pas/tmp, mas **muda de significado**: na nativa é ecológico
(pousio vs regeneração); em pas/tmp é permanência de uso (estabilidade
fundiária/econômica). Escrever as justificativas separadamente. **Consolidação
de pas/tmp = durabilidade da entrada dessas classes.**

---

## NOM — Nomenclatura e valência

### NOM-1. Nomes de campo neutros
**Decisão:** não reusar `frente`/`regen` nas três classes. Ganho de nativa é
recuperação (valência positiva); ganho de pasto/tmp é expansão de uso (negativa/
neutra). Usar `entrada`/`saída` ou `ganho`/`perda` por classe; deixar a valência
para a interpretação, nunca para o rótulo do campo. "Regeneração de pastagem"
numa tabela faz o revisor desconfiar do resto do paper.

---

## Herdadas do exercício anterior (mantidas, ver metodologia.md)

- `crsTransform` em vez de `scale` (evita reprojeção e desalinhamento do oficial).
- Reclassificação exaustiva-nominal com auditoria do resíduo.
- `pixelArea()` em vez de contagem.
- Frente ativa por **conjunção** (absoluta ∧ relativa), não limiar único.
- Frente terminal pelo limiar de exaustão 0,70 (ancorado empiricamente).
- **Hipótese da Reserva Legal testada e refutada** — o freio da conversão no
  nível de célula é geográfico, não jurídico. Resultado negativo publicável.
