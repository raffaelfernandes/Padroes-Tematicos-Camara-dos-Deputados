# Os tópicos se organizam pela lei citada?

Proposições que citam alguma lei identificável na ementa: 20654 (51.6%). Leis distintas: 1332. Mais citadas: DL 2848 (1656); L 9503 (707); DL 5452 (640); L 9394 (601); L 8069 (559); L 8078 (464); L 11340 (435); L 10406 (371).

## Pureza de lei citada por tópico

Fração das proposições (entre as que citam lei) que citam a lei mais comum do seu tópico. `topicos_com_lei_dominante`: tópicos com pelo menos 30 proposições que citam lei e em que uma lei responde por mais da metade delas.

| modelo    |   pureza_lei |   pureza_lei_acaso |   topicos |   topicos_com_lei_dominante |   fracao_proposicoes_nesses_topicos |
|:----------|-------------:|-------------------:|----------:|----------------------------:|------------------------------------:|
| BERTimbau |        0.453 |              0.08  |        67 |                          21 |                               0.322 |
| Serafim   |        0.365 |              0.08  |        70 |                          13 |                               0.15  |
| e5        |        0.459 |              0.081 |        75 |                          23 |                               0.326 |

## A lei citada antecipa o tema oficial?

Pares de proposições que citam a mesma lei e dividem algum tema oficial: 95.9%. Pares quaisquer: 24.2%.

## BCubed nas ementas com e sem lei citada

| subconjunto    |   proposicoes | modelo    |     P |     R |   P_acaso |
|:---------------|--------------:|:----------|------:|------:|----------:|
| sem lei citada |         19325 | BERTimbau | 0.737 | 0.089 |     0.263 |
| sem lei citada |         19325 | Serafim   | 0.707 | 0.078 |     0.262 |
| sem lei citada |         19325 | e5        | 0.707 | 0.081 |     0.263 |
| com lei citada |         20627 | BERTimbau | 0.788 | 0.131 |     0.25  |
| com lei citada |         20627 | Serafim   | 0.724 | 0.134 |     0.25  |
| com lei citada |         20627 | e5        | 0.744 | 0.117 |     0.25  |

## BERTimbau: tópicos em que uma lei responde por mais da metade das citações

|   topico_alt_ctfidf | lei_mais_comum   |   fracao |   citam_lei |
|--------------------:|:-----------------|---------:|------------:|
|                  52 | L 8036           |     0.87 |         144 |
|                   6 | L 9503           |     0.85 |         774 |
|                  34 | L 10826          |     0.84 |         256 |
|                  30 | L 9656           |     0.82 |         288 |
|                  49 | L 8069           |     0.8  |         255 |
|                  24 | L 8078           |     0.79 |         446 |
|                  65 | L 9605           |     0.78 |         149 |
|                  50 | L 9605           |     0.76 |         140 |
|                   7 | L 9394           |     0.75 |         648 |
|                  43 | L 10741          |     0.73 |         164 |
|                  46 | L 12305          |     0.7  |          79 |
|                   5 | DL 5452          |     0.7  |         852 |
|                  37 | L 7565           |     0.69 |         151 |
|                  41 | DL 3689          |     0.67 |         308 |
|                   1 | DL 2848          |     0.65 |        2122 |
|                  25 | L 13146          |     0.63 |         385 |
|                  44 | LC 123           |     0.59 |         284 |
|                  33 | L 7210           |     0.59 |         355 |
|                  10 | L 11340          |     0.58 |         626 |
|                  51 | L 9472           |     0.54 |         113 |
|                  22 | L 12764          |     0.53 |         289 |