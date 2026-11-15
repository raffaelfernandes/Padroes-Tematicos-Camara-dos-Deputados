# Os tópicos se organizam pela lei citada?

Proposições que citam alguma lei identificável na ementa: 20654 (51.6%). Leis distintas: 1332. Mais citadas: DL 2848 (1656); L 9503 (707); DL 5452 (640); L 9394 (601); L 8069 (559); L 8078 (464); L 11340 (435); L 10406 (371).

## Pureza de lei citada por tópico

Fração das proposições (entre as que citam lei) que citam a lei mais comum do seu tópico. `topicos_com_lei_dominante`: tópicos com pelo menos 30 proposições que citam lei e em que uma lei responde por mais da metade delas.

| modelo    |   pureza_lei |   pureza_lei_acaso |   topicos |   topicos_com_lei_dominante |   fracao_proposicoes_nesses_topicos |
|:----------|-------------:|-------------------:|----------:|----------------------------:|------------------------------------:|
| BERTimbau |        0.454 |              0.081 |        66 |                          21 |                               0.325 |
| Serafim   |        0.371 |              0.081 |        72 |                          13 |                               0.153 |
| e5        |        0.381 |              0.081 |        60 |                          16 |                               0.228 |

## A lei citada antecipa o tema oficial?

Pares de proposições que citam a mesma lei e dividem algum tema oficial: 95.9%. Pares quaisquer: 24.2%.

## BCubed nas ementas com e sem lei citada

| subconjunto    |   proposicoes | modelo    |     P |     R |   P_acaso |
|:---------------|--------------:|:----------|------:|------:|----------:|
| sem lei citada |         19325 | BERTimbau | 0.721 | 0.086 |     0.263 |
| sem lei citada |         19325 | Serafim   | 0.686 | 0.083 |     0.262 |
| sem lei citada |         19325 | e5        | 0.66  | 0.085 |     0.262 |
| com lei citada |         20627 | BERTimbau | 0.78  | 0.129 |     0.25  |
| com lei citada |         20627 | Serafim   | 0.737 | 0.131 |     0.25  |
| com lei citada |         20627 | e5        | 0.672 | 0.135 |     0.25  |

## BERTimbau: tópicos em que uma lei responde por mais da metade das citações

|   topico_alt_ctfidf | lei_mais_comum   |   fracao |   citam_lei |
|--------------------:|:-----------------|---------:|------------:|
|                  29 | L 9656           |     0.87 |         270 |
|                  35 | L 10826          |     0.86 |         247 |
|                  57 | L 9605           |     0.83 |         155 |
|                   5 | L 9503           |     0.8  |         838 |
|                  51 | L 8036           |     0.79 |         159 |
|                  39 | L 8069           |     0.76 |         325 |
|                  22 | L 8078           |     0.76 |         486 |
|                  42 | DL 3689          |     0.75 |         301 |
|                   8 | DL 5452          |     0.75 |         798 |
|                   9 | L 9394           |     0.71 |         682 |
|                  34 | L 7210           |     0.7  |         289 |
|                  47 | L 12305          |     0.67 |          82 |
|                   1 | DL 2848          |     0.63 |        2071 |
|                  24 | L 13146          |     0.63 |         398 |
|                  59 | DL 2848          |     0.6  |         163 |
|                  36 | L 7565           |     0.58 |         183 |
|                  41 | L 10741          |     0.57 |         214 |
|                  32 | LC 123           |     0.54 |         234 |
|                  49 | L 9472           |     0.53 |         137 |
|                  63 | DL 2848          |     0.53 |         163 |
|                   6 | L 11340          |     0.52 |         755 |