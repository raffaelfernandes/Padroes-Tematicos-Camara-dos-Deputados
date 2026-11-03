# Fase 5: RQ1 e RQ2

Tópicos: `topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet`. Proposições de deputados: 38502.

## RQ1: tópicos que ganham peso antes das eleições gerais

Métrica: fração dos deputados ativos na janela (abril a setembro) que apresentaram ao menos uma proposição do tópico. Controle: mesmos meses do ano anterior. Teste exato de Fisher com correção de Benjamini-Hochberg (α = 0.05). `razao_media`: contra a média dos anos sem eleição geral (sem 2020).

Deputados ativos (janela, controle): 2022 (323, 396); 2026 (403, 435).

### Sobem só em 2022 (1)

| topico | nome | taxa_ctrl_2022 | taxa_2022 | razao_2022 | p_aj_2022 | razao_media_2022 | taxa_ctrl_2026 | taxa_2026 | razao_2026 | p_aj_2026 | razao_media_2026 | padrao | mantém_no_núcleo | mantém_sem_massa |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 29 | planos, assistência saúde, saúde, privados assistência | 0.048 | 0.1796 | 3.743 | 0.0 | 3.708 | 0.0299 | 0.0521 | 1.744 | 0.49718 | 1.076 | sobe só em 2022 | True | True |

### Padrões por versão da análise de sensibilidade

| padrão | todas | nucleo | sem_massa |
| --- | --- | --- | --- |
| cai em uma | 1 | 2 | 2 |
| cai nas duas | 0 | 1 | 0 |
| estável | 64 | 61 | 61 |
| sobe só em 2022 | 1 | 1 | 1 |
| sobe só em 2026 | 0 | 1 | 2 |

### Contraste: eleição municipal de 2024 contra 2023 (8 maiores razões)

| topico | nome | taxa_ctrl_mun2024 | taxa_mun2024 | razao_mun2024 | p_aj_mun2024 |
| --- | --- | --- | --- | --- | --- |
| 52 | desastres, defesa civil, proteção defesa, clima | 0.0117 | 0.087 | 7.443 | 1e-05 |
| 0 | covid, coronavírus, pública, calamidade | 0.0911 | 0.2391 | 2.624 | 0.0 |
| 54 | inovação, desenvolvimento, pesquisa, tecnológica | 0.0234 | 0.0483 | 2.068 | 0.38911 |
| 29 | planos, assistência saúde, saúde, privados assistência | 0.0444 | 0.0773 | 1.741 | 0.38911 |
| 38 | apostas, quota fixa, quota, apostas quota | 0.0374 | 0.0628 | 1.68 | 0.46531 |
| 21 | cultural, reconhece, patrimônio, imaterial | 0.0491 | 0.0749 | 1.526 | 0.5747 |
| 41 | idosa, pessoa idosa, idoso, pessoa | 0.0467 | 0.0676 | 1.447 | 0.5747 |
| 51 | fgts, fundo garantia, garantia tempo, tempo serviço | 0.0257 | 0.0338 | 1.316 | 0.81887 |

## RQ2: assinaturas temáticas dos partidos

Partidos com pelo menos 100 proposições na legislatura. Log-odds com prior de Dirichlet (a0 = 500), partido contra o resto. `z_limitado`: cada proposição pesa min(1, C/n), em que n é a produção do deputado no partido e C o percentil 90 dessa produção (C = 49 na 56ª e 58 na 57ª). Assinatura = z_limitado positivo com p ajustado (BH, por partido) abaixo de 0.05 e z_bruto ≥ 1,96. `partidária`: pelo menos 3 deputados no tópico e nenhum com mais de 50%; senão `individual`.

### 56ª legislatura: três tópicos mais característicos de cada partido

| partido | n_partido | deputados_partido | topico | nome | n | lift | z_bruto | z_limitado | z_nucleo | deputados_no_topico | maior_autor | maior_autor_pct | assinatura |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AVANTE | 176 | 9 | 21 | cultural, reconhece, patrimônio, imaterial | 6 | 6.686 | 2.73 | 2.24 | 1.51 | 1 | Pastor Sargento Isidório | 1.0 |  |
| AVANTE | 176 | 9 | 0 | covid, coronavírus, pública, calamidade | 37 | 1.624 | 1.8 | 1.64 | 1.47 | 7 | André Janones | 0.324 |  |
| AVANTE | 176 | 9 | 17 | administração, administração pública, licitações, pública | 7 | 1.941 | 0.95 | 1.0 | 0.93 | 5 | Tito | 0.429 |  |
| CIDADANIA | 361 | 10 | 34 | execução penal, execução, penal, progressão regime | 8 | 2.018 | 1.36 | 1.53 | 1.6 | 5 | Alex Manente | 0.375 |  |
| CIDADANIA | 361 | 10 | 61 | radiodifusão, emissoras, serviço radiodifusão, sons | 5 | 2.623 | 1.47 | 1.12 | -0.34 | 2 | Marcelo Calero | 0.6 |  |
| CIDADANIA | 361 | 10 | 20 | transtorno, autista, espectro, transtorno espectro | 6 | 1.694 | 0.87 | 1.05 | 1.14 | 5 | Paula Belmonte | 0.333 |  |
| DEM | 755 | 33 | 30 | denomina, rodovia, viaduto, trecho | 13 | 2.048 | 2.12 | 1.81 | 1.75 | 5 | Efraim Filho | 0.308 |  |
| DEM | 755 | 33 | 2 | civil, processo civil, código civil, processo | 48 | 1.436 | 2.13 | 1.43 | 1.86 | 12 | Geninho Zuliani | 0.312 |  |
| DEM | 755 | 33 | 50 | política, programa, agricultura, agricultura familiar | 9 | 2.052 | 1.75 | 1.4 | 0.47 | 6 | Tereza Cristina | 0.222 |  |
| MDB | 884 | 42 | 14 | capital, título capital, título, município | 21 | 2.615 | 3.76 | 4.38 | 4.43 | 13 | Alceu Moreira | 0.19 | partidária |
| MDB | 884 | 42 | 2 | civil, processo civil, código civil, processo | 131 | 3.345 | 12.54 | 3.36 | 2.42 | 11 | Carlos Bezerra | 0.771 | individual |
| MDB | 884 | 42 | 36 | aeronáutica, brasileiro aeronáutica, código brasileiro, aéreo | 16 | 2.155 | 2.6 | 2.17 | 1.57 | 10 | Carlos Bezerra | 0.312 |  |
| NOVO | 235 | 8 | 8 | trabalho, consolidação, consolidação trabalho, clt | 26 | 4.686 | 5.04 | 5.23 | 4.12 | 7 | Lucas Gonzalez | 0.462 | partidária |
| NOVO | 235 | 8 | 17 | administração, administração pública, licitações, pública | 20 | 4.151 | 4.02 | 4.04 | 4.14 | 3 | Adriana Ventura | 0.7 | individual |
| NOVO | 235 | 8 | 37 | tributário, tributária, código tributário, débitos | 14 | 5.228 | 3.93 | 3.9 | 1.96 | 3 | Alexis Fonteyne | 0.571 | individual |
| PATRIOTA | 221 | 7 | 26 | animais, animal, domésticos, cães | 28 | 11.114 | 8.43 | 6.28 | 4.99 | 1 | Fred Costa | 1.0 | individual |
| PATRIOTA | 221 | 7 | 57 | maus tratos, tratos, maus, animais | 11 | 13.459 | 5.69 | 4.23 | 3.59 | 2 | Fred Costa | 0.909 | individual |
| PATRIOTA | 221 | 7 | 9 | educação, ensino, diretrizes bases, bases educação | 15 | 2.241 | 1.87 | 1.74 | 1.66 | 4 | Pastor Eurico | 0.467 |  |
| PCDOB | 212 | 9 | 0 | covid, coronavírus, pública, calamidade | 66 | 2.406 | 4.82 | 4.8 | 4.18 | 8 | Perpétua Almeida | 0.318 | partidária |
| PCDOB | 212 | 9 | 31 | ensino, superior, instituições, estudantes | 8 | 2.772 | 1.69 | 1.56 | 0.72 | 4 | Márcio Jerry | 0.375 |  |
| PCDOB | 212 | 9 | 11 | profissão, exercício, regulamentação, profissional | 11 | 2.172 | 1.5 | 1.53 | 1.28 | 5 | Alice Portugal | 0.273 |  |
| PDT | 941 | 31 | 15 | eleitoral, eleições, partidos, políticos | 42 | 2.0 | 3.94 | 2.88 | 2.18 | 15 | Pompeo de Mattos | 0.333 |  |
| PDT | 941 | 31 | 12 | previdência, previdência social, social, benefícios | 32 | 2.099 | 3.63 | 2.16 | 2.15 | 16 | Pompeo de Mattos | 0.438 |  |
| PDT | 941 | 31 | 17 | administração, administração pública, licitações, pública | 30 | 1.556 | 2.09 | 1.86 | 1.48 | 16 | Mário Heringer | 0.133 |  |
| PL | 1054 | 86 | 1 | penal, código penal, crime, crimes | 108 | 1.648 | 4.84 | 4.81 | 4.01 | 33 | Lincoln Portela | 0.194 | partidária |
| PL | 1054 | 86 | 30 | denomina, rodovia, viaduto, trecho | 21 | 2.369 | 3.47 | 2.64 | 2.52 | 12 | Júnior Mano | 0.143 |  |
| PL | 1054 | 86 | 35 | fogo, armas, arma, arma fogo | 20 | 1.979 | 2.69 | 2.57 | 2.05 | 13 | Loester Trutis | 0.2 |  |
| PODE | 769 | 19 | 58 | desenvolvimento, universidade, área, estado | 16 | 3.41 | 4.09 | 2.31 | 1.58 | 5 | José Nelto | 0.438 |  |
| PODE | 769 | 19 | 41 | idosa, pessoa idosa, idoso, pessoa | 13 | 1.988 | 2.03 | 1.53 | 1.5 | 6 | Roberto de Lucena | 0.308 |  |
| PODE | 769 | 19 | 2 | civil, processo civil, código civil, processo | 45 | 1.321 | 1.59 | 1.19 | 0.71 | 10 | José Medeiros | 0.289 |  |
| PP | 1050 | 55 | 30 | denomina, rodovia, viaduto, trecho | 24 | 2.726 | 4.3 | 4.09 | 4.02 | 11 | Schiavinato | 0.25 | partidária |
| PP | 1050 | 55 | 16 | energia, elétrica, energia elétrica, concessionárias | 39 | 2.05 | 4.0 | 3.77 | 4.01 | 18 | Eduardo da Fonte | 0.231 | partidária |
| PP | 1050 | 55 | 14 | capital, título capital, título, município | 22 | 2.308 | 3.44 | 2.82 | 2.9 | 10 | Jerônimo Goergen | 0.273 |  |
| PROS | 267 | 15 | 4 | saúde, único saúde, sistema único, sus | 19 | 2.718 | 2.81 | 2.33 | 2.58 | 5 | Boca Aberta | 0.474 |  |
| PROS | 267 | 15 | 64 | rodovias, rodovias federais, pedágio, federais | 7 | 5.24 | 2.87 | 2.2 | 2.14 | 3 | Boca Aberta | 0.714 |  |
| PROS | 267 | 15 | 27 | transporte, passageiros, mobilidade, mobilidade urbana | 9 | 2.262 | 1.54 | 1.31 | 1.33 | 4 | Boca Aberta | 0.444 |  |
| PSB | 1145 | 40 | 31 | ensino, superior, instituições, estudantes | 32 | 2.051 | 3.65 | 3.84 | 2.14 | 15 | Danilo Cabral | 0.188 | partidária |
| PSB | 1145 | 40 | 0 | covid, coronavírus, pública, calamidade | 190 | 1.282 | 3.49 | 3.84 | 3.16 | 30 | Mauro Nazif | 0.089 | partidária |
| PSB | 1145 | 40 | 40 | pátria, heróis, livro heróis, livro | 12 | 2.442 | 2.76 | 2.67 | 2.31 | 7 | Alessandro Molon | 0.333 |  |
| PSC | 232 | 14 | 16 | energia, elétrica, energia elétrica, concessionárias | 11 | 2.619 | 1.94 | 1.95 | 2.03 | 5 | Glaustin Fokus | 0.545 |  |
| PSC | 232 | 14 | 26 | animais, animal, domésticos, cães | 7 | 2.649 | 1.55 | 1.92 | 1.69 | 3 | Leonardo Gadelha | 0.571 |  |
| PSC | 232 | 14 | 1 | penal, código penal, crime, crimes | 24 | 1.662 | 1.55 | 1.53 | 1.12 | 7 | Paulo Eduardo Martins | 0.375 |  |
| PSD | 861 | 58 | 32 | pequeno, pequeno porte, microempresas, porte | 21 | 2.259 | 3.16 | 2.94 | 1.45 | 10 | Otto Alencar Filho | 0.476 |  |
| PSD | 861 | 58 | 27 | transporte, passageiros, mobilidade, mobilidade urbana | 23 | 1.792 | 2.38 | 2.38 | 1.15 | 12 | Francisco Jr. | 0.13 |  |
| PSD | 861 | 58 | 3 | dia, conscientização, anualmente, dia dia | 37 | 1.552 | 2.29 | 2.09 | 2.16 | 20 | Francisco Jr. | 0.189 |  |
| PSDB | 1428 | 37 | 16 | energia, elétrica, energia elétrica, concessionárias | 40 | 1.547 | 2.59 | 3.18 | 2.53 | 15 | Edna Henrique | 0.225 |  |
| PSDB | 1428 | 37 | 39 | adolescente, criança adolescente, criança, estatuto criança | 20 | 1.538 | 1.79 | 1.89 | 1.4 | 8 | Alexandre Frota | 0.35 |  |
| PSDB | 1428 | 37 | 56 | união, distrito, estados, estados distrito | 10 | 1.296 | 0.75 | 1.85 | 1.69 | 8 | Carlos Sampaio | 0.2 |  |
| PSL | 1843 | 58 | 1 | penal, código penal, crime, crimes | 197 | 1.719 | 7.83 | 7.6 | 6.81 | 44 | Sanderson | 0.086 | partidária |
| PSL | 1843 | 58 | 59 | penal, penal código, código penal, código | 46 | 3.731 | 8.33 | 7.02 | 6.31 | 19 | Sanderson | 0.217 | partidária |
| PSL | 1843 | 58 | 35 | fogo, armas, arma, arma fogo | 54 | 3.052 | 7.85 | 7.0 | 6.12 | 25 | Sanderson | 0.13 | partidária |
| PSOL | 213 | 11 | 0 | covid, coronavírus, pública, calamidade | 74 | 2.685 | 5.82 | 5.55 | 4.86 | 8 | Fernanda Melchionna | 0.351 | partidária |
| PSOL | 213 | 11 | 6 | violência, doméstica, violência doméstica, mulher | 18 | 3.189 | 2.97 | 3.25 | 1.78 | 8 | Talíria Petrone | 0.333 | partidária |
| PSOL | 213 | 11 | 28 | benefício, família, prestação continuada, bolsa | 9 | 3.496 | 2.24 | 2.19 | 1.64 | 4 | Fernanda Melchionna | 0.444 |  |
| PT | 1604 | 58 | 0 | covid, coronavírus, pública, calamidade | 373 | 1.797 | 12.55 | 10.9 | 9.48 | 44 | Rejane Dias | 0.126 | partidária |
| PT | 1604 | 58 | 8 | trabalho, consolidação, consolidação trabalho, clt | 66 | 1.742 | 4.32 | 4.06 | 3.54 | 27 | Rubens Otoni | 0.273 | partidária |
| PT | 1604 | 58 | 65 | petróleo, gás, gás natural, natural | 18 | 1.965 | 2.69 | 2.44 | 2.65 | 15 | Gleisi Hoffmann | 0.111 |  |
| PTB | 434 | 13 | 16 | energia, elétrica, energia elétrica, concessionárias | 15 | 1.912 | 1.82 | 1.75 | 1.73 | 7 | Pedro Augusto Bezerra | 0.267 |  |
| PTB | 434 | 13 | 58 | desenvolvimento, universidade, área, estado | 6 | 2.262 | 1.45 | 1.5 | 1.45 | 4 | Wilson Santiago | 0.333 |  |
| PTB | 434 | 13 | 32 | pequeno, pequeno porte, microempresas, porte | 9 | 1.917 | 1.4 | 1.43 | 1.22 | 5 | Eduardo Costa | 0.333 |  |
| PV | 324 | 4 | 57 | maus tratos, tratos, maus, animais | 13 | 10.838 | 6.15 | 2.68 | 2.28 | 3 | Célio Studart | 0.846 |  |
| PV | 324 | 4 | 26 | animais, animal, domésticos, cães | 37 | 10.018 | 10.15 | 2.54 | 2.4 | 1 | Célio Studart | 1.0 |  |
| PV | 324 | 4 | 56 | união, distrito, estados, estados distrito | 7 | 4.0 | 2.49 | 2.45 | 1.99 | 3 | Professor Israel Batista | 0.571 |  |
| REPUBLICANOS | 1025 | 53 | 22 | consumidor, defesa consumidor, código defesa, defesa | 32 | 2.013 | 3.48 | 3.48 | 3.36 | 14 | Márcio Marinho | 0.188 | partidária |
| REPUBLICANOS | 1025 | 53 | 33 | esporte, esportivas, atletas, futebol | 27 | 2.287 | 3.78 | 2.85 | 2.77 | 12 | Julio Cesar Ribeiro | 0.444 |  |
| REPUBLICANOS | 1025 | 53 | 41 | idosa, pessoa idosa, idoso, pessoa | 18 | 2.071 | 2.67 | 2.75 | 2.23 | 12 | Ossesio Silva | 0.222 |  |
| SOLIDARIEDADE | 255 | 15 | 52 | desastres, defesa civil, proteção defesa, clima | 4 | 6.28 | 2.37 | 2.23 | 2.03 | 2 | Zé Silva | 0.75 |  |
| SOLIDARIEDADE | 255 | 15 | 22 | consumidor, defesa consumidor, código defesa, defesa | 8 | 2.026 | 1.22 | 1.37 | 1.0 | 4 | Lucas Vergilio | 0.5 |  |
| SOLIDARIEDADE | 255 | 15 | 24 | deficiência, pessoa deficiência, pessoa, pessoas deficiência | 8 | 2.227 | 1.4 | 1.31 | 1.94 | 4 | Aureo Ribeiro | 0.5 |  |
| UNIÃO | 279 | 61 | 21 | cultural, reconhece, patrimônio, imaterial | 10 | 7.02 | 4.18 | 3.97 | 3.84 | 6 | Ney Leprevost | 0.5 | partidária |
| UNIÃO | 279 | 61 | 24 | deficiência, pessoa deficiência, pessoa, pessoas deficiência | 12 | 3.05 | 2.5 | 2.63 | 2.91 | 6 | Geninho Zuliani | 0.583 |  |
| UNIÃO | 279 | 61 | 29 | planos, assistência saúde, saúde, privados assistência | 10 | 3.113 | 2.32 | 2.39 | 2.5 | 10 | Pedro Lucas Fernandes | 0.1 |  |

Assinaturas por partido na 56ª legislatura:

| partido | individual | partidária |
| --- | --- | --- |
| MDB | 1 | 1 |
| NOVO | 2 | 1 |
| PATRIOTA | 2 | 0 |
| PCDOB | 0 | 1 |
| PL | 0 | 1 |
| PP | 0 | 2 |
| PSB | 0 | 2 |
| PSL | 0 | 8 |
| PSOL | 0 | 2 |
| PT | 0 | 2 |
| REPUBLICANOS | 0 | 1 |
| UNIÃO | 0 | 1 |

### 57ª legislatura: três tópicos mais característicos de cada partido

| partido | n_partido | deputados_partido | topico | nome | n | lift | z_bruto | z_limitado | z_nucleo | deputados_no_topico | maior_autor | maior_autor_pct | assinatura |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| AVANTE | 194 | 9 | 58 | desenvolvimento, universidade, área, estado | 4 | 5.722 | 2.06 | 1.79 | 1.58 | 2 | Greyce Elias | 0.5 |  |
| AVANTE | 194 | 9 | 11 | profissão, exercício, regulamentação, profissional | 10 | 2.96 | 1.96 | 1.63 | 1.4 | 2 | Bruno Farias | 0.8 |  |
| AVANTE | 194 | 9 | 19 | militares, constituição, cargos, bombeiros | 8 | 2.368 | 1.37 | 1.3 | 1.55 | 3 | Pastor Sargento Isidório | 0.75 |  |
| CIDADANIA | 748 | 5 | 63 | código penal, penal, código, crimes | 4 | 1.128 | 0.22 | 1.4 | 0.91 | 3 | Any Ortiz | 0.5 |  |
| CIDADANIA | 748 | 5 | 54 | inovação, desenvolvimento, pesquisa, tecnológica | 40 | 3.323 | 6.32 | 1.17 | 0.37 | 2 | Amom Mandel | 0.975 |  |
| CIDADANIA | 748 | 5 | 51 | fgts, fundo garantia, garantia tempo, tempo serviço | 4 | 1.233 | 0.35 | 1.1 | 1.13 | 2 | Any Ortiz | 0.5 |  |
| MDB | 1853 | 56 | 18 | ambiental, terras, conservação, áreas | 62 | 1.463 | 2.86 | 2.93 | 1.73 | 18 | Lucio Mosquini | 0.371 |  |
| MDB | 1853 | 56 | 60 | programa casa, casa, casa vida, vida | 16 | 1.955 | 2.55 | 2.7 | 2.38 | 8 | Hildo Rocha | 0.312 |  |
| MDB | 1853 | 56 | 50 | política, programa, agricultura, agricultura familiar | 49 | 1.65 | 3.36 | 2.1 | 3.03 | 16 | Duda Ramos | 0.51 |  |
| NOVO | 184 | 5 | 37 | tributário, tributária, código tributário, débitos | 11 | 6.644 | 3.74 | 3.43 | 2.52 | 3 | Gilson Marques | 0.545 | individual |
| NOVO | 184 | 5 | 25 | complementar, recursos, fiscal, municípios | 16 | 5.577 | 4.05 | 3.22 | 2.44 | 4 | Adriana Ventura | 0.5 | partidária |
| NOVO | 184 | 5 | 17 | administração, administração pública, licitações, pública | 20 | 4.768 | 4.11 | 2.88 | 2.24 | 2 | Adriana Ventura | 0.85 |  |
| PCDOB | 162 | 10 | 11 | profissão, exercício, regulamentação, profissional | 19 | 6.741 | 4.8 | 4.3 | nan | 5 | Enfermeira Rejane | 0.474 | partidária |
| PCDOB | 162 | 10 | 3 | dia, conscientização, anualmente, dia dia | 13 | 2.728 | 1.95 | 1.67 | nan | 7 | Daiana Santos | 0.308 |  |
| PCDOB | 162 | 10 | 31 | ensino, superior, instituições, estudantes | 6 | 3.19 | 1.52 | 1.45 | nan | 4 | Alice Portugal | 0.5 |  |
| PDT | 1351 | 21 | 0 | covid, coronavírus, pública, calamidade | 66 | 2.004 | 5.22 | 3.15 | 2.06 | 9 | Pompeo de Mattos | 0.455 |  |
| PDT | 1351 | 21 | 13 | produtos, medicamentos, alimentos, comercialização | 37 | 1.405 | 1.89 | 2.12 | 1.53 | 10 | Marcos Tavares | 0.324 |  |
| PDT | 1351 | 21 | 52 | desastres, defesa civil, proteção defesa, clima | 19 | 1.72 | 2.13 | 1.95 | 2.4 | 5 | Duda Salabert | 0.474 |  |
| PL | 3782 | 131 | 1 | penal, código penal, crime, crimes | 421 | 1.656 | 11.69 | 8.77 | 7.68 | 80 | Cabo Gilberto Silva | 0.105 | partidária |
| PL | 3782 | 131 | 35 | fogo, armas, arma, arma fogo | 107 | 3.291 | 12.16 | 7.84 | 5.32 | 25 | Marcos Pollon | 0.393 | partidária |
| PL | 3782 | 131 | 46 | segurança pública, segurança, pública, fundo segurança | 92 | 1.992 | 6.97 | 6.05 | 3.85 | 39 | Capitão Alden | 0.13 | partidária |
| PODE | 1358 | 32 | 19 | militares, constituição, cargos, bombeiros | 41 | 1.736 | 3.22 | 2.63 | 2.7 | 8 | Sargento Portugal | 0.756 |  |
| PODE | 1358 | 32 | 26 | animais, animal, domésticos, cães | 44 | 1.831 | 3.67 | 2.44 | 2.04 | 9 | Duda Ramos | 0.364 |  |
| PODE | 1358 | 32 | 64 | rodovias, rodovias federais, pedágio, federais | 10 | 1.947 | 1.85 | 2.27 | 2.04 | 6 | Bruno Ganem | 0.5 |  |
| PP | 1574 | 72 | 20 | transtorno, autista, espectro, transtorno espectro | 64 | 1.485 | 2.98 | 2.72 | 1.92 | 23 | Marx Beltrão | 0.188 |  |
| PP | 1574 | 72 | 14 | capital, título capital, título, município | 42 | 1.867 | 3.77 | 2.54 | 2.99 | 22 | Evair Vieira de Melo | 0.214 |  |
| PP | 1574 | 72 | 30 | denomina, rodovia, viaduto, trecho | 20 | 2.19 | 3.24 | 2.39 | 2.21 | 15 | Afonso Hamm | 0.15 |  |
| PRD | 218 | 9 | 52 | desastres, defesa civil, proteção defesa, clima | 10 | 5.598 | 3.37 | 2.52 | 2.28 | 2 | Pedro Aihara | 0.8 |  |
| PRD | 218 | 9 | 41 | idosa, pessoa idosa, idoso, pessoa | 8 | 2.566 | 1.56 | 1.6 | 1.42 | 3 | Ribeiro Neto | 0.5 |  |
| PRD | 218 | 9 | 48 | violência, política, prevenção, combate | 6 | 2.67 | 1.41 | 1.29 | 0.55 | 3 | Marreca Filho | 0.5 |  |
| PSB | 1029 | 20 | 31 | ensino, superior, instituições, estudantes | 22 | 1.845 | 2.48 | 2.76 | 1.17 | 8 | Jonas Donizette | 0.227 |  |
| PSB | 1029 | 20 | 29 | planos, assistência saúde, saúde, privados assistência | 42 | 4.584 | 8.62 | 2.35 | -0.62 | 2 | Duarte Jr. | 0.571 |  |
| PSB | 1029 | 20 | 21 | cultural, reconhece, patrimônio, imaterial | 19 | 1.114 | 0.4 | 2.19 | 2.25 | 7 | Eriberto Medeiros | 0.368 |  |
| PSD | 1348 | 72 | 38 | apostas, quota fixa, quota, apostas quota | 28 | 1.891 | 3.04 | 2.96 | 2.9 | 19 | Hugo Leal | 0.107 |  |
| PSD | 1348 | 72 | 21 | cultural, reconhece, patrimônio, imaterial | 40 | 1.789 | 3.36 | 2.7 | 2.65 | 9 | Nitinho | 0.45 |  |
| PSD | 1348 | 72 | 16 | energia, elétrica, energia elétrica, concessionárias | 26 | 1.359 | 1.41 | 2.44 | 2.42 | 13 | Domingos Neto | 0.154 |  |
| PSDB | 294 | 25 | 14 | capital, título capital, título, município | 13 | 3.091 | 2.67 | 2.27 | 1.92 | 9 | Luciano Vieira | 0.231 |  |
| PSDB | 294 | 25 | 0 | covid, coronavírus, pública, calamidade | 16 | 2.23 | 2.09 | 1.9 | 2.02 | 10 | Adolfo Viana | 0.188 |  |
| PSDB | 294 | 25 | 6 | violência, doméstica, violência doméstica, mulher | 21 | 1.72 | 1.63 | 1.75 | 1.59 | 8 | Lêda Borges | 0.619 |  |
| PSOL | 528 | 14 | 52 | desastres, defesa civil, proteção defesa, clima | 19 | 4.39 | 5.0 | 5.31 | 3.16 | 8 | Erika Hilton | 0.316 | partidária |
| PSOL | 528 | 14 | 40 | pátria, heróis, livro heróis, livro | 17 | 5.111 | 5.22 | 4.6 | 4.4 | 6 | Tarcísio Motta | 0.353 | partidária |
| PSOL | 528 | 14 | 6 | violência, doméstica, violência doméstica, mulher | 45 | 2.053 | 3.78 | 3.78 | 2.64 | 9 | Erika Hilton | 0.244 | partidária |
| PT | 1856 | 75 | 40 | pátria, heróis, livro heróis, livro | 29 | 2.476 | 4.62 | 4.19 | 4.05 | 19 | Helder Salomão | 0.172 | partidária |
| PT | 1856 | 75 | 8 | trabalho, consolidação, consolidação trabalho, clt | 68 | 1.551 | 3.49 | 4.15 | 3.52 | 28 | Lindbergh Farias | 0.103 | partidária |
| PT | 1856 | 75 | 6 | violência, doméstica, violência doméstica, mulher | 101 | 1.311 | 2.68 | 3.29 | 3.05 | 33 | Delegada Adriana Accorsi | 0.168 | partidária |
| PV | 214 | 7 | 9 | educação, ensino, diretrizes bases, bases educação | 14 | 1.879 | 1.38 | 1.37 | 1.29 | 5 | Luciano Amaral | 0.286 |  |
| PV | 214 | 7 | 54 | inovação, desenvolvimento, pesquisa, tecnológica | 6 | 1.739 | 0.77 | 1.31 | -0.32 | 3 | Bacelar | 0.5 |  |
| PV | 214 | 7 | 31 | ensino, superior, instituições, estudantes | 6 | 2.414 | 1.25 | 1.25 | 0.69 | 4 | Bacelar | 0.5 |  |
| REDE | 152 | 6 | 60 | programa casa, casa, casa vida, vida | 4 | 5.977 | 1.96 | 1.92 | 2.08 | 3 | Lucas Abrahao | 0.5 |  |
| REDE | 152 | 6 | 26 | animais, animal, domésticos, cães | 8 | 2.972 | 1.61 | 1.68 | 0.82 | 3 | Heloísa Helena | 0.625 |  |
| REDE | 152 | 6 | 65 | petróleo, gás, gás natural, natural | 3 | 6.567 | 1.81 | 1.58 | 1.19 | 2 | Heloísa Helena | 0.667 |  |
| REPUBLICANOS | 2214 | 76 | 22 | consumidor, defesa consumidor, código defesa, defesa | 57 | 1.436 | 2.71 | 2.99 | 2.61 | 23 | Amom Mandel | 0.228 |  |
| REPUBLICANOS | 2214 | 76 | 62 | concursos, concursos públicos, públicos, concurso | 14 | 1.703 | 1.89 | 1.89 | 0.45 | 12 | Amom Mandel | 0.214 |  |
| REPUBLICANOS | 2214 | 76 | 27 | transporte, passageiros, mobilidade, mobilidade urbana | 39 | 1.239 | 1.31 | 1.8 | 1.1 | 21 | Fred Linhares | 0.154 |  |
| SOLIDARIEDADE | 368 | 13 | 50 | política, programa, agricultura, agricultura familiar | 14 | 2.375 | 2.24 | 3.03 | 0.85 | 3 | Ribeiro Neto | 0.786 |  |
| SOLIDARIEDADE | 368 | 13 | 4 | saúde, único saúde, sistema único, sus | 27 | 1.642 | 1.81 | 2.41 | 1.95 | 7 | Ribeiro Neto | 0.407 |  |
| SOLIDARIEDADE | 368 | 13 | 56 | união, distrito, estados, estados distrito | 5 | 3.4 | 1.91 | 1.76 | 1.27 | 3 | Vanderlan Alves | 0.6 |  |
| UNIÃO | 2317 | 88 | 63 | código penal, penal, código, crimes | 27 | 2.489 | 4.61 | 3.84 | 4.51 | 9 | Delegado Matheus Laiola | 0.556 | individual |
| UNIÃO | 2317 | 88 | 57 | maus tratos, tratos, maus, animais | 27 | 2.053 | 3.65 | 2.65 | 2.4 | 8 | Delegado Matheus Laiola | 0.444 |  |
| UNIÃO | 2317 | 88 | 26 | animais, animal, domésticos, cães | 54 | 1.316 | 2.0 | 2.62 | 2.11 | 16 | Delegado Matheus Laiola | 0.259 |  |

Assinaturas por partido na 57ª legislatura:

| partido | individual | partidária |
| --- | --- | --- |
| NOVO | 1 | 1 |
| PCDOB | 0 | 1 |
| PL | 0 | 8 |
| PSOL | 0 | 3 |
| PT | 0 | 3 |
| UNIÃO | 1 | 0 |

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
