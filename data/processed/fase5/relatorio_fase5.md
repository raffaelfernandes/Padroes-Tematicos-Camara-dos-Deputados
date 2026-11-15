# Fase 5: RQ1 e RQ2

Tópicos: `topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet`. Proposições de deputados: 38502.

## RQ1: tópicos que ganham peso antes das eleições gerais

Métrica: fração dos deputados ativos na janela (abril a setembro) que apresentaram ao menos uma proposição do tópico. Controle: mesmos meses do ano anterior. Teste exato de Fisher com correção de Benjamini-Hochberg (α = 0.05). `razao_media`: contra a média dos anos sem eleição geral (sem 2020).

Deputados ativos (janela, controle): 2022 (323, 396); 2026 (403, 435).

### Sobem só em 2022 (1)

| topico | nome | taxa_ctrl_2022 | taxa_2022 | razao_2022 | p_aj_2022 | razao_media_2022 | taxa_ctrl_2026 | taxa_2026 | razao_2026 | p_aj_2026 | razao_media_2026 | padrao | mantém_no_núcleo | mantém_sem_massa |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30 | planos, saúde, assistência saúde, privados assistência | 0.0505 | 0.1796 | 3.555 | 0.0 | 3.667 | 0.0253 | 0.0496 | 1.963 | 0.41736 | 1.013 | sobe só em 2022 | True | True |

### Sobem só em 2026 (1)

| topico | nome | taxa_ctrl_2022 | taxa_2022 | razao_2022 | p_aj_2022 | razao_media_2022 | taxa_ctrl_2026 | taxa_2026 | razao_2026 | p_aj_2026 | razao_media_2026 | padrao | mantém_no_núcleo | mantém_sem_massa |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 54 | saneamento, saneamento básico, água, básico | 0.0278 | 0.0217 | 0.78 | 0.85505 | 0.648 | 0.0138 | 0.0571 | 4.138 | 0.0315 | 1.708 | sobe só em 2026 | False | True |

### Padrões por versão da análise de sensibilidade

| padrão | todas | nucleo | sem_massa |
| --- | --- | --- | --- |
| cai em uma | 2 | 3 | 2 |
| estável | 63 | 63 | 63 |
| sobe só em 2022 | 1 | 1 | 1 |
| sobe só em 2026 | 1 | 0 | 1 |

### Contraste: eleição municipal de 2024 contra 2023 (8 maiores razões)

| topico | nome | taxa_ctrl_mun2024 | taxa_mun2024 | razao_mun2024 | p_aj_mun2024 |
| --- | --- | --- | --- | --- | --- |
| 53 | desastres, defesa civil, proteção defesa, clima | 0.0164 | 0.0918 | 5.612 | 3e-05 |
| 65 | meio ambiente, ambientais, administrativas, lesivas | 0.0304 | 0.0821 | 2.704 | 0.01852 |
| 36 | apostas, quota fixa, quota, apostas quota | 0.0327 | 0.07 | 2.141 | 0.20126 |
| 0 | covid, coronavírus, calamidade, pública | 0.1215 | 0.2536 | 2.088 | 3e-05 |
| 19 | animais, animal, domésticos, animais domésticos | 0.0421 | 0.0749 | 1.78 | 0.25265 |
| 30 | planos, saúde, assistência saúde, privados assistência | 0.0491 | 0.0845 | 1.723 | 0.25265 |
| 15 | cultural, reconhece, patrimônio, imaterial | 0.0537 | 0.0797 | 1.483 | 0.41217 |
| 61 | crédito, financeiras, instituições, instituições financeiras | 0.0257 | 0.0362 | 1.41 | 0.6841 |

## RQ2: assinaturas temáticas dos partidos

Partidos com pelo menos 100 proposições na legislatura. Log-odds com prior de Dirichlet (a0 = 500), partido contra o resto. `z_limitado`: cada proposição pesa min(1, C/n), em que n é a produção do deputado no partido e C o percentil 90 dessa produção (C = 49 na 56ª e 58 na 57ª). Assinatura = z_limitado positivo com p ajustado (BH, por partido) abaixo de 0.05 e z_bruto ≥ 1,96. `partidária`: pelo menos 3 deputados no tópico e nenhum com mais de 50%; senão `individual`.

### 56ª legislatura: três tópicos mais característicos de cada partido

| partido | n_partido | deputados_partido | topico | nome | n | lift | z_bruto | z_limitado | z_nucleo | deputados_no_topico | maior_autor | maior_autor_pct | assinatura |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AVANTE | 176 | 9 | 15 | cultural, reconhece, patrimônio, imaterial | 6 | 5.683 | 2.46 | 2.0 | 1.72 | 1 | Pastor Sargento Isidório | 1.0 |  |
| AVANTE | 176 | 9 | 0 | covid, coronavírus, calamidade, pública | 39 | 1.64 | 1.9 | 1.73 | 1.17 | 7 | André Janones | 0.333 |  |
| AVANTE | 176 | 9 | 29 | denomina, rodovia, viaduto, trecho | 5 | 3.156 | 1.42 | 1.25 | 1.18 | 3 | Greyce Elias | 0.6 |  |
| CIDADANIA | 361 | 10 | 33 | execução penal, execução, penal, pena | 8 | 1.776 | 1.1 | 1.33 | 1.53 | 5 | Alex Manente | 0.375 |  |
| CIDADANIA | 361 | 10 | 22 | transtorno, autista, espectro, transtorno espectro | 6 | 1.824 | 1.0 | 1.28 | 1.4 | 5 | Carmen Zanotto | 0.333 |  |
| CIDADANIA | 361 | 10 | 31 | estabelecimentos, obrigatoriedade, segurança, eventos | 8 | 1.552 | 0.84 | 1.18 | 0.18 | 4 | Joceval Rodrigues | 0.5 |  |
| DEM | 755 | 33 | 46 | resíduos, resíduos sólidos, sólidos, política resíduos | 13 | 2.098 | 2.2 | 1.96 | 1.61 | 5 | David Soares | 0.308 |  |
| DEM | 755 | 33 | 3 | civil, processo civil, código civil, processo | 49 | 1.542 | 2.57 | 1.9 | 1.48 | 13 | Geninho Zuliani | 0.327 |  |
| DEM | 755 | 33 | 29 | denomina, rodovia, viaduto, trecho | 13 | 1.911 | 1.93 | 1.64 | 1.63 | 5 | Geninho Zuliani | 0.308 |  |
| MDB | 884 | 42 | 11 | capital, título capital, título, confere | 20 | 2.43 | 3.38 | 4.0 | 3.85 | 12 | Alceu Moreira | 0.2 | partidária |
| MDB | 884 | 42 | 3 | civil, processo civil, código civil, processo | 129 | 3.466 | 12.77 | 3.37 | 1.82 | 11 | Carlos Bezerra | 0.783 | individual |
| MDB | 884 | 42 | 42 | universidade, campus, autoriza poder, desenvolvimento | 14 | 2.052 | 2.29 | 2.81 | 2.33 | 10 | Mara Rocha | 0.143 |  |
| NOVO | 235 | 8 | 5 | trabalho, consolidação, consolidação trabalho, clt | 27 | 4.336 | 4.87 | 4.99 | 4.62 | 7 | Lucas Gonzalez | 0.444 | partidária |
| NOVO | 235 | 8 | 60 | tributário, código tributário, tributária, receita brasil | 12 | 7.627 | 4.55 | 4.52 | 3.74 | 3 | Alexis Fonteyne | 0.75 | individual |
| NOVO | 235 | 8 | 32 | administração, administração pública, licitações, transparência | 17 | 5.519 | 4.51 | 4.49 | 3.16 | 3 | Adriana Ventura | 0.765 | individual |
| PATRIOTA | 221 | 7 | 19 | animais, animal, domésticos, animais domésticos | 28 | 9.181 | 7.69 | 5.77 | 4.02 | 2 | Fred Costa | 0.964 | individual |
| PATRIOTA | 221 | 7 | 50 | tratos, maus tratos, maus, animais | 12 | 13.575 | 5.97 | 4.44 | 3.35 | 2 | Fred Costa | 0.917 | individual |
| PATRIOTA | 221 | 7 | 7 | educação, ensino, diretrizes bases, bases educação | 17 | 2.689 | 2.47 | 2.36 | 1.66 | 4 | Pastor Eurico | 0.529 |  |
| PCDOB | 212 | 9 | 0 | covid, coronavírus, calamidade, pública | 66 | 2.304 | 4.6 | 4.61 | 4.13 | 8 | Perpétua Almeida | 0.318 | partidária |
| PCDOB | 212 | 9 | 13 | profissão, exercício, exercício profissão, profissional | 10 | 2.408 | 1.62 | 1.57 | 1.05 | 6 | Alice Portugal | 0.3 |  |
| PCDOB | 212 | 9 | 64 | terrorismo, criminosas, organizações, organizações criminosas | 3 | 3.55 | 1.28 | 1.28 | 1.12 | 2 | Márcio Jerry | 0.667 |  |
| PDT | 941 | 31 | 12 | previdência, previdência social, social, benefícios | 31 | 2.164 | 3.75 | 2.25 | 1.85 | 15 | Pompeo de Mattos | 0.419 |  |
| PDT | 941 | 31 | 62 | radiodifusão, emissoras, serviço radiodifusão, sons | 11 | 2.388 | 2.45 | 1.95 | 1.31 | 6 | Eduardo Bismarck | 0.364 |  |
| PDT | 941 | 31 | 26 | ensino, superior, educação, estudantes | 30 | 1.628 | 2.3 | 1.91 | 2.44 | 14 | Pompeo de Mattos | 0.2 |  |
| PL | 1054 | 86 | 1 | código penal, penal, crime, código | 105 | 1.495 | 3.87 | 3.92 | 3.36 | 32 | Lincoln Portela | 0.21 | partidária |
| PL | 1054 | 86 | 33 | execução penal, execução, penal, pena | 25 | 1.896 | 2.81 | 2.9 | 0.93 | 11 | Capitão Augusto | 0.36 |  |
| PL | 1054 | 86 | 34 | fogo, arma, armas, arma fogo | 21 | 2.095 | 2.98 | 2.9 | 2.55 | 14 | Loester Trutis | 0.19 |  |
| PODE | 769 | 19 | 42 | universidade, campus, autoriza poder, desenvolvimento | 16 | 2.701 | 3.3 | 1.76 | 1.75 | 6 | José Nelto | 0.438 |  |
| PODE | 769 | 19 | 43 | idosa, pessoa idosa, idoso, pessoa | 10 | 2.097 | 1.93 | 1.35 | 1.74 | 3 | Roberto de Lucena | 0.5 |  |
| PODE | 769 | 19 | 1 | código penal, penal, crime, código | 66 | 1.288 | 1.8 | 1.26 | 1.14 | 11 | José Medeiros | 0.258 |  |
| PP | 1050 | 55 | 16 | energia, elétrica, energia elétrica, concessionárias | 41 | 2.131 | 4.31 | 4.04 | 3.39 | 17 | Eduardo da Fonte | 0.244 | partidária |
| PP | 1050 | 55 | 29 | denomina, rodovia, viaduto, trecho | 24 | 2.544 | 4.03 | 3.82 | 3.9 | 11 | Beto Rosado | 0.25 | partidária |
| PP | 1050 | 55 | 11 | capital, título capital, título, confere | 22 | 2.258 | 3.34 | 2.72 | 2.78 | 11 | Jerônimo Goergen | 0.273 |  |
| PROS | 267 | 15 | 20 | transporte, passageiros, mobilidade, coletivo | 13 | 2.899 | 2.44 | 2.1 | 1.05 | 6 | Boca Aberta | 0.462 |  |
| PROS | 267 | 15 | 2 | saúde, único saúde, sistema único, sus | 22 | 2.118 | 2.26 | 1.97 | 2.0 | 7 | Boca Aberta | 0.409 |  |
| PROS | 267 | 15 | 36 | apostas, quota fixa, quota, apostas quota | 4 | 5.769 | 2.27 | 1.73 | 0.32 | 2 | Boca Aberta | 0.75 |  |
| PSB | 1145 | 40 | 0 | covid, coronavírus, calamidade, pública | 191 | 1.235 | 2.98 | 3.18 | 3.44 | 30 | Mauro Nazif | 0.094 |  |
| PSB | 1145 | 40 | 66 | improbidade, improbidade administrativa, administrativa, ato improbidade | 21 | 2.473 | 3.7 | 2.8 | 1.55 | 7 | Rodrigo Agostinho | 0.571 |  |
| PSB | 1145 | 40 | 26 | ensino, superior, educação, estudantes | 34 | 1.515 | 2.17 | 2.58 | 1.99 | 17 | Danilo Cabral | 0.176 |  |
| PSC | 232 | 14 | 16 | energia, elétrica, energia elétrica, concessionárias | 11 | 2.59 | 1.91 | 1.9 | 1.55 | 5 | Glaustin Fokus | 0.545 |  |
| PSC | 232 | 14 | 51 | telecomunicações, serviços, telefonia, móvel | 5 | 3.0 | 1.49 | 1.59 | 0.44 | 3 | Leonardo Gadelha | 0.6 |  |
| PSC | 232 | 14 | 24 | consumidor, defesa consumidor, código defesa, defesa | 8 | 2.447 | 1.51 | 1.57 | 0.34 | 3 | Glaustin da Fokus | 0.375 |  |
| PSD | 861 | 58 | 44 | pequeno porte, pequeno, complementar, porte | 26 | 2.538 | 4.06 | 3.79 | 3.18 | 12 | Otto Alencar Filho | 0.269 | partidária |
| PSD | 861 | 58 | 20 | transporte, passageiros, mobilidade, coletivo | 24 | 1.661 | 2.09 | 2.16 | 1.68 | 13 | Francisco Jr. | 0.125 |  |
| PSD | 861 | 58 | 63 | rodovias, pedágio, rodovias federais, federais | 7 | 2.25 | 1.8 | 2.12 | -0.04 | 4 | Hugo Leal | 0.571 |  |
| PSDB | 1428 | 37 | 16 | energia, elétrica, energia elétrica, concessionárias | 39 | 1.492 | 2.33 | 2.82 | 2.55 | 16 | Alexandre Frota | 0.205 |  |
| PSDB | 1428 | 37 | 14 | complementar, constituição, recursos, fiscal | 45 | 1.212 | 1.21 | 2.52 | 2.63 | 17 | Alexandre Frota | 0.267 |  |
| PSDB | 1428 | 37 | 2 | saúde, único saúde, sistema único, sus | 80 | 1.44 | 3.11 | 2.26 | 1.39 | 18 | Alexandre Frota | 0.45 |  |
| PSL | 1843 | 58 | 1 | código penal, penal, crime, código | 236 | 1.923 | 10.45 | 9.82 | 8.87 | 46 | Sanderson | 0.127 | partidária |
| PSL | 1843 | 58 | 34 | fogo, arma, armas, arma fogo | 53 | 3.032 | 7.69 | 6.81 | 6.28 | 26 | Sanderson | 0.151 | partidária |
| PSL | 1843 | 58 | 33 | execução penal, execução, penal, pena | 58 | 2.52 | 6.77 | 6.0 | 4.71 | 25 | Sanderson | 0.121 | partidária |
| PSOL | 213 | 11 | 0 | covid, coronavírus, calamidade, pública | 78 | 2.711 | 6.09 | 5.82 | 5.21 | 9 | Fernanda Melchionna | 0.321 | partidária |
| PSOL | 213 | 11 | 40 | violência, prevenção, adolescentes, crianças | 8 | 6.483 | 3.27 | 3.27 | 2.05 | 5 | Talíria Petrone | 0.5 | partidária |
| PSOL | 213 | 11 | 27 | benefício, prestação continuada, benefício prestação, assistência social | 10 | 4.043 | 2.66 | 2.63 | 2.17 | 4 | Fernanda Melchionna | 0.5 |  |
| PT | 1604 | 58 | 0 | covid, coronavírus, calamidade, pública | 388 | 1.791 | 12.82 | 11.14 | 9.0 | 45 | Rejane Dias | 0.126 | partidária |
| PT | 1604 | 58 | 5 | trabalho, consolidação, consolidação trabalho, clt | 72 | 1.694 | 4.29 | 4.12 | 3.76 | 29 | Rubens Otoni | 0.25 | partidária |
| PT | 1604 | 58 | 15 | cultural, reconhece, patrimônio, imaterial | 17 | 1.767 | 2.23 | 2.35 | 2.07 | 13 | Maria do Rosário | 0.176 |  |
| PTB | 434 | 13 | 58 | selo, selo empresa, programa, amiga | 5 | 2.738 | 1.63 | 1.76 | 0.83 | 4 | Dra. Soraya Manato | 0.4 |  |
| PTB | 434 | 13 | 16 | energia, elétrica, energia elétrica, concessionárias | 15 | 1.891 | 1.78 | 1.69 | 1.78 | 7 | Eduardo Costa | 0.267 |  |
| PTB | 434 | 13 | 42 | universidade, campus, autoriza poder, desenvolvimento | 8 | 2.39 | 1.78 | 1.63 | 1.67 | 5 | Wilson Santiago | 0.375 |  |
| PV | 324 | 4 | 19 | animais, animal, domésticos, animais domésticos | 43 | 9.616 | 10.79 | 2.63 | 2.38 | 1 | Célio Studart | 1.0 |  |
| PV | 324 | 4 | 57 | união, estados distrito, distrito, estados | 8 | 4.259 | 2.79 | 2.44 | 2.29 | 3 | Professor Israel Batista | 0.5 |  |
| PV | 324 | 4 | 50 | tratos, maus tratos, maus, animais | 12 | 9.25 | 5.49 | 1.92 | 1.95 | 2 | Célio Studart | 0.917 |  |
| REPUBLICANOS | 1025 | 53 | 24 | consumidor, defesa consumidor, código defesa, defesa | 32 | 2.213 | 3.94 | 3.95 | 4.43 | 14 | Márcio Marinho | 0.188 | partidária |
| REPUBLICANOS | 1025 | 53 | 39 | esporte, atletas, esportivas, futebol | 23 | 2.575 | 3.97 | 3.02 | 2.53 | 8 | Julio Cesar Ribeiro | 0.522 |  |
| REPUBLICANOS | 1025 | 53 | 40 | violência, prevenção, adolescentes, crianças | 12 | 2.017 | 2.1 | 2.3 | 1.95 | 7 | Rosangela Gomes | 0.25 |  |
| SOLIDARIEDADE | 255 | 15 | 25 | deficiência, pessoa deficiência, pessoa, pessoas deficiência | 9 | 2.451 | 1.66 | 1.65 | 1.61 | 4 | Aureo Ribeiro | 0.444 |  |
| SOLIDARIEDADE | 255 | 15 | 53 | desastres, defesa civil, proteção defesa, clima | 3 | 4.538 | 1.67 | 1.51 | 0.46 | 2 | Zé Silva | 0.667 |  |
| SOLIDARIEDADE | 255 | 15 | 61 | crédito, financeiras, instituições, instituições financeiras | 5 | 2.841 | 1.44 | 1.37 | 1.6 | 3 | Augusto Coutinho | 0.4 |  |
| UNIÃO | 279 | 61 | 15 | cultural, reconhece, patrimônio, imaterial | 10 | 5.967 | 3.8 | 3.59 | 3.67 | 6 | Ney Leprevost | 0.5 | partidária |
| UNIÃO | 279 | 61 | 30 | planos, saúde, assistência saúde, privados assistência | 10 | 3.168 | 2.37 | 2.41 | 2.49 | 10 | José Rocha | 0.1 |  |
| UNIÃO | 279 | 61 | 25 | deficiência, pessoa deficiência, pessoa, pessoas deficiência | 10 | 2.486 | 1.84 | 2.02 | 2.38 | 5 | Geninho Zuliani | 0.6 |  |

Assinaturas por partido na 56ª legislatura:

| partido | individual | partidária |
| --- | --- | --- |
| MDB | 1 | 1 |
| NOVO | 2 | 2 |
| PATRIOTA | 2 | 0 |
| PCDOB | 0 | 1 |
| PL | 0 | 1 |
| PP | 0 | 2 |
| PSD | 0 | 1 |
| PSL | 0 | 6 |
| PSOL | 0 | 2 |
| PT | 0 | 2 |
| REPUBLICANOS | 0 | 1 |
| UNIÃO | 0 | 1 |

### 57ª legislatura: três tópicos mais característicos de cada partido

| partido | n_partido | deputados_partido | topico | nome | n | lift | z_bruto | z_limitado | z_nucleo | deputados_no_topico | maior_autor | maior_autor_pct | assinatura |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AVANTE | 194 | 9 | 31 | estabelecimentos, obrigatoriedade, segurança, eventos | 7 | 2.597 | 1.42 | 1.5 | 0.6 | 3 | Pastor Sargento Isidório | 0.714 |  |
| AVANTE | 194 | 9 | 42 | universidade, campus, autoriza poder, desenvolvimento | 4 | 4.478 | 1.75 | 1.48 | 1.41 | 2 | Greyce Elias | 0.5 |  |
| AVANTE | 194 | 9 | 9 | segurança pública, segurança, militares, pública | 11 | 2.069 | 1.36 | 1.43 | 2.0 | 4 | Pastor Sargento Isidório | 0.636 |  |
| CIDADANIA | 748 | 5 | 32 | administração, administração pública, licitações, transparência | 22 | 1.986 | 2.64 | 1.28 | 0.89 | 4 | Amom Mandel | 0.818 |  |
| CIDADANIA | 748 | 5 | 52 | fgts, fundo garantia, garantia tempo, tempo serviço | 4 | 1.359 | 0.51 | 1.19 | 1.13 | 2 | Any Ortiz | 0.5 |  |
| CIDADANIA | 748 | 5 | 60 | tributário, código tributário, tributária, receita brasil | 4 | 1.359 | 0.49 | 1.12 | 0.75 | 2 | Any Ortiz | 0.5 |  |
| MDB | 1853 | 56 | 55 | programa casa, casa, casa vida, vida | 18 | 2.109 | 3.02 | 3.13 | 2.19 | 9 | Duda Ramos | 0.278 |  |
| MDB | 1853 | 56 | 18 | terras, conservação, áreas, ambiental | 51 | 1.44 | 2.52 | 2.49 | 1.87 | 14 | Lucio Mosquini | 0.373 |  |
| MDB | 1853 | 56 | 2 | saúde, único saúde, sistema único, sus | 141 | 1.198 | 2.15 | 2.16 | 1.57 | 32 | Duda Ramos | 0.355 |  |
| NOVO | 184 | 5 | 14 | complementar, constituição, recursos, fiscal | 21 | 5.851 | 4.83 | 3.94 | 3.51 | 4 | Adriana Ventura | 0.429 | partidária |
| NOVO | 184 | 5 | 32 | administração, administração pública, licitações, transparência | 14 | 5.142 | 3.58 | 2.63 | 1.26 | 2 | Adriana Ventura | 0.857 |  |
| NOVO | 184 | 5 | 0 | covid, coronavírus, calamidade, pública | 16 | 2.949 | 2.46 | 2.29 | 2.12 | 3 | Marcel van Hattem | 0.625 |  |
| PCDOB | 162 | 10 | 13 | profissão, exercício, exercício profissão, profissional | 13 | 6.266 | 3.76 | 3.31 | nan | 4 | Alice Portugal | 0.462 |  |
| PCDOB | 162 | 10 | 2 | saúde, único saúde, sistema único, sus | 20 | 1.945 | 1.63 | 1.68 | nan | 4 | Enfermeira Rejane | 0.7 |  |
| PCDOB | 162 | 10 | 4 | dia, conscientização, anualmente, dia dia | 11 | 2.794 | 1.83 | 1.5 | nan | 6 | Daiana Santos | 0.273 |  |
| PDT | 1351 | 21 | 0 | covid, coronavírus, calamidade, pública | 71 | 1.783 | 4.52 | 3.0 | 2.53 | 11 | Pompeo de Mattos | 0.408 |  |
| PDT | 1351 | 21 | 53 | desastres, defesa civil, proteção defesa, clima | 21 | 1.914 | 2.68 | 2.42 | 1.67 | 6 | Duda Salabert | 0.429 |  |
| PDT | 1351 | 21 | 46 | resíduos, resíduos sólidos, sólidos, política resíduos | 14 | 2.167 | 2.6 | 2.02 | 2.07 | 6 | Marcos Tavares | 0.429 |  |
| PL | 3782 | 131 | 1 | código penal, penal, crime, código | 401 | 1.659 | 11.39 | 8.8 | 7.27 | 78 | Cabo Gilberto Silva | 0.112 | partidária |
| PL | 3782 | 131 | 34 | fogo, arma, armas, arma fogo | 102 | 3.253 | 11.79 | 7.61 | 6.88 | 25 | Marcos Pollon | 0.422 | partidária |
| PL | 3782 | 131 | 9 | segurança pública, segurança, militares, pública | 212 | 2.047 | 11.14 | 7.31 | 6.14 | 47 | Cabo Gilberto Silva | 0.137 | partidária |
| PODE | 1358 | 32 | 19 | animais, animal, domésticos, animais domésticos | 55 | 2.109 | 5.11 | 3.57 | 2.84 | 9 | Bruno Ganem | 0.418 | partidária |
| PODE | 1358 | 32 | 9 | segurança pública, segurança, militares, pública | 58 | 1.558 | 3.13 | 2.58 | 2.07 | 11 | Sargento Portugal | 0.776 |  |
| PODE | 1358 | 32 | 22 | transtorno, autista, espectro, transtorno espectro | 46 | 1.378 | 1.98 | 2.55 | 2.02 | 15 | Bruno Ganem | 0.37 |  |
| PP | 1574 | 72 | 11 | capital, título capital, título, confere | 44 | 1.818 | 3.69 | 2.56 | 2.51 | 24 | Evair Vieira de Melo | 0.205 |  |
| PP | 1574 | 72 | 29 | denomina, rodovia, viaduto, trecho | 20 | 2.153 | 3.2 | 2.36 | 2.48 | 15 | Afonso Hamm | 0.15 |  |
| PP | 1574 | 72 | 44 | pequeno porte, pequeno, complementar, porte | 25 | 1.656 | 2.33 | 2.09 | 1.71 | 16 | Mauricio Neves | 0.24 |  |
| PRD | 218 | 9 | 53 | desastres, defesa civil, proteção defesa, clima | 10 | 5.667 | 3.38 | 2.44 | 1.66 | 2 | Pedro Aihara | 0.8 |  |
| PRD | 218 | 9 | 58 | selo, selo empresa, programa, amiga | 5 | 3.754 | 1.76 | 1.74 | 0.18 | 3 | Ribeiro Neto | 0.6 |  |
| PRD | 218 | 9 | 43 | idosa, pessoa idosa, idoso, pessoa | 6 | 3.056 | 1.61 | 1.64 | 1.58 | 2 | Ribeiro Neto | 0.667 |  |
| PSB | 1029 | 20 | 15 | cultural, reconhece, patrimônio, imaterial | 20 | 1.09 | 0.33 | 2.22 | 2.31 | 7 | Eriberto Medeiros | 0.4 |  |
| PSB | 1029 | 20 | 30 | planos, saúde, assistência saúde, privados assistência | 44 | 4.412 | 8.62 | 2.2 | -0.67 | 2 | Duarte Jr. | 0.545 |  |
| PSB | 1029 | 20 | 26 | ensino, superior, educação, estudantes | 25 | 1.373 | 1.38 | 2.17 | 0.8 | 9 | Tabata Amaral | 0.28 |  |
| PSD | 1348 | 72 | 15 | cultural, reconhece, patrimônio, imaterial | 41 | 1.708 | 3.12 | 2.57 | 2.37 | 10 | Nitinho | 0.439 |  |
| PSD | 1348 | 72 | 36 | apostas, quota fixa, quota, apostas quota | 27 | 1.653 | 2.39 | 2.35 | 2.47 | 19 | Hugo Leal | 0.111 |  |
| PSD | 1348 | 72 | 29 | denomina, rodovia, viaduto, trecho | 16 | 2.017 | 2.55 | 2.27 | 1.93 | 11 | Hugo Leal | 0.188 |  |
| PSDB | 294 | 25 | 11 | capital, título capital, título, confere | 14 | 3.091 | 2.77 | 2.39 | 2.15 | 10 | Luciano Vieira | 0.214 |  |
| PSDB | 294 | 25 | 0 | covid, coronavírus, calamidade, pública | 20 | 2.305 | 2.46 | 2.17 | 2.53 | 13 | Adolfo Viana | 0.15 |  |
| PSDB | 294 | 25 | 10 | violência, doméstica, violência doméstica, mulher | 16 | 1.876 | 1.63 | 1.66 | 2.14 | 5 | Lêda Borges | 0.688 |  |
| PSOL | 528 | 14 | 53 | desastres, defesa civil, proteção defesa, clima | 19 | 4.444 | 5.02 | 5.22 | 3.3 | 9 | Erika Hilton | 0.263 | partidária |
| PSOL | 528 | 14 | 38 | heróis, pátria, livro heróis, livro | 17 | 4.954 | 5.1 | 4.5 | 4.42 | 6 | Tarcísio Motta | 0.353 | partidária |
| PSOL | 528 | 14 | 10 | violência, doméstica, violência doméstica, mulher | 35 | 2.286 | 3.78 | 3.69 | 1.15 | 9 | Erika Hilton | 0.2 | partidária |
| PT | 1856 | 75 | 38 | heróis, pátria, livro heróis, livro | 29 | 2.4 | 4.44 | 4.03 | 3.82 | 19 | Helder Salomão | 0.172 | partidária |
| PT | 1856 | 75 | 42 | universidade, campus, autoriza poder, desenvolvimento | 21 | 2.457 | 3.92 | 3.45 | 3.45 | 9 | Pedro Uczai | 0.238 | partidária |
| PT | 1856 | 75 | 10 | violência, doméstica, violência doméstica, mulher | 78 | 1.448 | 3.17 | 3.43 | 2.87 | 29 | Delegada Adriana Accorsi | 0.167 | partidária |
| PV | 214 | 7 | 7 | educação, ensino, diretrizes bases, bases educação | 16 | 2.287 | 1.96 | 1.79 | 1.08 | 5 | Clodoaldo Magalhães | 0.312 |  |
| PV | 214 | 7 | 26 | ensino, superior, educação, estudantes | 7 | 1.847 | 0.94 | 1.01 | 1.13 | 4 | Bacelar | 0.571 |  |
| PV | 214 | 7 | 2 | saúde, único saúde, sistema único, sus | 25 | 1.839 | 1.85 | 0.93 | 1.17 | 4 | Clodoaldo Magalhães | 0.84 |  |
| REDE | 152 | 6 | 5 | trabalho, consolidação, consolidação trabalho, clt | 14 | 3.337 | 2.41 | 2.3 | nan | 2 | Heloísa Helena | 0.571 |  |
| REDE | 152 | 6 | 55 | programa casa, casa, casa vida, vida | 3 | 4.283 | 1.34 | 1.35 | nan | 2 | Lucas Abrahao | 0.667 |  |
| REDE | 152 | 6 | 22 | transtorno, autista, espectro, transtorno espectro | 10 | 2.675 | 1.62 | 1.33 | nan | 2 | Heloísa Helena | 0.9 |  |
| REPUBLICANOS | 2214 | 76 | 16 | energia, elétrica, energia elétrica, concessionárias | 37 | 1.285 | 1.48 | 2.13 | 0.97 | 22 | Marcelo Crivella | 0.108 |  |
| REPUBLICANOS | 2214 | 76 | 24 | consumidor, defesa consumidor, código defesa, defesa | 48 | 1.276 | 1.67 | 1.97 | 2.75 | 23 | Amom Mandel | 0.292 |  |
| REPUBLICANOS | 2214 | 76 | 43 | idosa, pessoa idosa, idoso, pessoa | 36 | 1.811 | 3.45 | 1.92 | 1.05 | 11 | Amom Mandel | 0.361 |  |
| SOLIDARIEDADE | 368 | 13 | 17 | política, desenvolvimento, programa, inovação | 23 | 1.708 | 1.8 | 2.8 | 0.74 | 4 | Ribeiro Neto | 0.652 |  |
| SOLIDARIEDADE | 368 | 13 | 13 | profissão, exercício, exercício profissão, profissional | 11 | 2.336 | 1.93 | 2.05 | 2.13 | 4 | Vanderlan Alves | 0.636 |  |
| SOLIDARIEDADE | 368 | 13 | 2 | saúde, único saúde, sistema único, sus | 29 | 1.241 | 0.83 | 1.48 | 1.48 | 7 | Ribeiro Neto | 0.345 |  |
| UNIÃO | 2317 | 88 | 50 | tratos, maus tratos, maus, animais | 27 | 2.017 | 3.53 | 2.98 | 2.9 | 8 | Delegado Matheus Laiola | 0.481 |  |
| UNIÃO | 2317 | 88 | 1 | código penal, penal, crime, código | 212 | 1.432 | 5.46 | 2.75 | 2.58 | 44 | Kim Kataguiri | 0.222 |  |
| UNIÃO | 2317 | 88 | 19 | animais, animal, domésticos, animais domésticos | 60 | 1.349 | 2.31 | 2.57 | 1.19 | 16 | Delegado Matheus Laiola | 0.233 |  |

Assinaturas por partido na 57ª legislatura:

| partido | individual | partidária |
| --- | --- | --- |
| NOVO | 0 | 1 |
| PL | 0 | 9 |
| PODE | 0 | 1 |
| PSOL | 0 | 4 |
| PT | 1 | 5 |

### Partido e ano em que um deputado passa de 50% das proposições do partido

| partido | ano | total_partido_ano | maior_autor | n_maior_autor | pct | acima_50pct |
| --- | --- | --- | --- | --- | --- | --- |
| AVANTE | 2019 | 52 | Pastor Sargento Isidório | 30 | 0.577 | True |
| CIDADANIA | 2020 | 103 | Paula Belmonte | 58 | 0.563 | True |
| CIDADANIA | 2023 | 73 | Amom Mandel | 51 | 0.699 | True |
| CIDADANIA | 2024 | 104 | Amom Mandel | 80 | 0.769 | True |
| CIDADANIA | 2025 | 541 | Amom Mandel | 515 | 0.952 | True |
| MDB | 2021 | 360 | Carlos Bezerra | 229 | 0.636 | True |
| MDB | 2025 | 927 | Duda Ramos | 568 | 0.613 | True |
| NOVO | 2023 | 56 | Adriana Ventura | 33 | 0.589 | True |
| PATRIOTA | 2023 | 61 | Pedro Aihara | 37 | 0.607 | True |
| PDT | 2025 | 513 | Marcos Tavares | 269 | 0.524 | True |
| PODE | 2026 | 684 | Duda Ramos | 450 | 0.658 | True |
| PRD | 2024 | 81 | Pedro Aihara | 55 | 0.679 | True |
| PRD | 2025 | 52 | Pedro Aihara | 34 | 0.654 | True |
| PSB | 2025 | 270 | Jonas Donizette | 152 | 0.563 | True |
| PSB | 2026 | 240 | Jonas Donizette | 122 | 0.508 | True |
| PSDB | 2020 | 500 | Alexandre Frota | 291 | 0.582 | True |
| PSDB | 2021 | 405 | Alexandre Frota | 217 | 0.536 | True |
| PSDB | 2022 | 190 | Alexandre Frota | 137 | 0.721 | True |
| PV | 2019 | 217 | Célio Studart | 186 | 0.857 | True |
| PV | 2020 | 65 | Célio Studart | 44 | 0.677 | True |
| PV | 2024 | 65 | Clodoaldo Magalhães | 47 | 0.723 | True |
| REDE | 2026 | 107 | Heloísa Helena | 70 | 0.654 | True |
| REPUBLICANOS | 2026 | 923 | Amom Mandel | 556 | 0.602 | True |
| SOLIDARIEDADE | 2024 | 71 | Aureo Ribeiro | 43 | 0.606 | True |
| SOLIDARIEDADE | 2025 | 91 | Aureo Ribeiro | 60 | 0.659 | True |
