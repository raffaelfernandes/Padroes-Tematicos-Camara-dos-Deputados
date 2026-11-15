# Relatório da Fase 4

39952 proposições com tema oficial; 32 temas.

## BCubed estendido

P = precisão, R = recall, F = média harmônica. Leia P e R separados: "um cluster só" tem F alto sem significar nada.

| modelo | versao | granularidade | n_grupos | P | R | F |
| --- | --- | --- | --- | --- | --- | --- |
| referência | um cluster só | - | 1 | 0.244 | 0.963 | 0.389 |
| referência | cada proposição sozinha | - | 39952 | 1.0 | 0.0 | 0.0 |
| referência | teto: tema mais frequente do gabarito | - | 31 | 1.0 | 0.435 | 0.606 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por centroide | natural | 67 | 0.76 | 0.101 | 0.179 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por c-TF-IDF | natural | 67 | 0.76 | 0.101 | 0.179 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers como grupos unitários | natural | 13679 | 0.898 | 0.056 | 0.105 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por centroide | k32 | 33 | 0.563 | 0.118 | 0.195 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por c-TF-IDF | k32 | 33 | 0.563 | 0.118 | 0.195 |
| bertimbau_nn30_mcs100_eom_ms10_rk | aleatório, mesmos tamanhos (5 sementes) | natural | 67 | 0.245 | 0.026 | 0.046 |
| bertimbau_nn30_mcs100_eom_ms10_rk | aleatório, mesmos tamanhos (5 sementes) | k32 | 33 | 0.245 | 0.042 | 0.072 |
| e5_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por centroide | natural | 75 | 0.72 | 0.089 | 0.158 |
| e5_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por c-TF-IDF | natural | 75 | 0.722 | 0.09 | 0.16 |
| e5_nn30_mcs100_eom_ms10_rk | outliers como grupos unitários | natural | 13775 | 0.88 | 0.045 | 0.086 |
| e5_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por centroide | k32 | 33 | 0.489 | 0.12 | 0.193 |
| e5_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por c-TF-IDF | k32 | 33 | 0.49 | 0.121 | 0.195 |
| e5_nn30_mcs100_eom_ms10_rk | aleatório, mesmos tamanhos (5 sementes) | natural | 75 | 0.245 | 0.024 | 0.044 |
| e5_nn30_mcs100_eom_ms10_rk | aleatório, mesmos tamanhos (5 sementes) | k32 | 33 | 0.245 | 0.057 | 0.092 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers reatribuídos; formulaicas por centroide | natural | 70 | 0.711 | 0.1 | 0.175 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers reatribuídos; formulaicas por c-TF-IDF | natural | 70 | 0.71 | 0.1 | 0.175 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers como grupos unitários | natural | 12665 | 0.857 | 0.062 | 0.116 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers reatribuídos; formulaicas por centroide | k32 | 33 | 0.53 | 0.115 | 0.189 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers reatribuídos; formulaicas por c-TF-IDF | k32 | 33 | 0.53 | 0.115 | 0.189 |
| serafim_nn30_mcs100_eom_ms5_rk | aleatório, mesmos tamanhos (5 sementes) | natural | 70 | 0.245 | 0.025 | 0.045 |
| serafim_nn30_mcs100_eom_ms5_rk | aleatório, mesmos tamanhos (5 sementes) | k32 | 33 | 0.245 | 0.043 | 0.073 |

## Por tipo de proposição e formulaicas (versão principal)

| modelo | grupo | n | P_medio | R_medio |
| --- | --- | --- | --- | --- |
| bertimbau_nn30_mcs100_eom_ms10_rk | PL | 38137 | 0.762 | 0.103 |
| bertimbau_nn30_mcs100_eom_ms10_rk | PLP | 1586 | 0.733 | 0.068 |
| bertimbau_nn30_mcs100_eom_ms10_rk | PEC | 229 | 0.627 | 0.092 |
| bertimbau_nn30_mcs100_eom_ms10_rk | formulaicas | 493 | 0.62 | 0.098 |
| bertimbau_nn30_mcs100_eom_ms10_rk | não formulaicas | 39459 | 0.761 | 0.101 |
| e5_nn30_mcs100_eom_ms10_rk | PL | 38137 | 0.723 | 0.09 |
| e5_nn30_mcs100_eom_ms10_rk | PLP | 1586 | 0.68 | 0.059 |
| e5_nn30_mcs100_eom_ms10_rk | PEC | 229 | 0.449 | 0.051 |
| e5_nn30_mcs100_eom_ms10_rk | formulaicas | 493 | 0.389 | 0.044 |
| e5_nn30_mcs100_eom_ms10_rk | não formulaicas | 39459 | 0.724 | 0.089 |
| serafim_nn30_mcs100_eom_ms5_rk | PL | 38137 | 0.714 | 0.101 |
| serafim_nn30_mcs100_eom_ms5_rk | PLP | 1586 | 0.656 | 0.068 |
| serafim_nn30_mcs100_eom_ms5_rk | PEC | 229 | 0.597 | 0.093 |
| serafim_nn30_mcs100_eom_ms5_rk | formulaicas | 493 | 0.585 | 0.095 |
| serafim_nn30_mcs100_eom_ms5_rk | não formulaicas | 39459 | 0.712 | 0.1 |

## Formulaicas: centroide x c-TF-IDF

| modelo | versao | n | P_medio | R_medio |
| --- | --- | --- | --- | --- |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por centroide | 493 | 0.62 | 0.098 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por c-TF-IDF | 493 | 0.622 | 0.096 |
| e5_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por centroide | 493 | 0.389 | 0.044 |
| e5_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por c-TF-IDF | 493 | 0.587 | 0.089 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers reatribuídos; formulaicas por centroide | 493 | 0.585 | 0.095 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers reatribuídos; formulaicas por c-TF-IDF | 493 | 0.57 | 0.093 |

## bertimbau_nn30_mcs100_eom_ms10_rk

- Pares apensada e principal: 10437; 96.3% compartilham tema oficial.
- No mesmo tópico (natural): 68.8% (acaso: 2.7%).
- No mesmo tópico (k32): 69.2% (acaso: 4.4%).

- Dispersão: 2460 proposições (6.2%) dividem tema com o resto do tópico menos do que o acaso prevê para elas.
- Pureza mediana dos tópicos: 85%; tópicos com pureza abaixo de 50%: 6 de 67.

Temas mais fragmentados (n ≥ 300):

| tema | n | n_topicos | topicos_para_80pct | entropia_norm | maior_topico_pct |
| --- | --- | --- | --- | --- | --- |
| Administração Pública | 6022 | 67 | 26 | 0.866 | 0.092 |
| Direitos Humanos e Minorias | 11076 | 67 | 23 | 0.848 | 0.086 |
| Indústria, Comércio e Serviços | 3808 | 64 | 22 | 0.833 | 0.094 |
| Relações Internacionais e Comércio Exterior | 374 | 50 | 18 | 0.828 | 0.158 |
| Cidades e Desenvolvimento Urbano | 1648 | 62 | 17 | 0.799 | 0.116 |
| Economia | 2488 | 64 | 18 | 0.794 | 0.158 |
| Finanças Públicas e Orçamento | 6075 | 67 | 19 | 0.783 | 0.13 |
| Defesa e Segurança | 4139 | 67 | 16 | 0.765 | 0.171 |

Tópicos menos puros (n ≥ 150):

| topico | nome | n | tema_dominante | pureza | temas_para_80pct |
| --- | --- | --- | --- | --- | --- |
| 17 | política, desenvolvimento, programa, inovação | 1070 | Finanças Públicas e Orçamento | 0.297 | 11 |
| 31 | estabelecimentos, obrigatoriedade, segurança, eventos | 551 | Indústria, Comércio e Serviços | 0.345 | 10 |
| 28 | internet, dados, digitais, dados pessoais | 786 | Comunicações | 0.429 | 10 |
| 42 | universidade, campus, autoriza poder, desenvolvimento | 250 | Economia | 0.468 | 8 |
| 58 | selo, selo empresa, programa, amiga | 220 | Educação | 0.477 | 9 |
| 18 | terras, conservação, áreas, ambiental | 753 | Meio Ambiente e Desenvolvimento Sustentável | 0.479 | 9 |
| 59 | telecomunicações, infraestrutura, universalização, serviços telecomuni | 179 | Comunicações | 0.553 | 11 |
| 54 | saneamento, saneamento básico, água, básico | 268 | Energia, Recursos Hídricos e Minerais | 0.597 | 7 |

## e5_nn30_mcs100_eom_ms10_rk

- Pares apensada e principal: 10437; 96.3% compartilham tema oficial.
- No mesmo tópico (natural): 66.5% (acaso: 2.5%).
- No mesmo tópico (k32): 67.5% (acaso: 5.9%).

- Dispersão: 3446 proposições (8.6%) dividem tema com o resto do tópico menos do que o acaso prevê para elas.
- Pureza mediana dos tópicos: 82%; tópicos com pureza abaixo de 50%: 5 de 75.

Temas mais fragmentados (n ≥ 300):

| tema | n | n_topicos | topicos_para_80pct | entropia_norm | maior_topico_pct |
| --- | --- | --- | --- | --- | --- |
| Relações Internacionais e Comércio Exterior | 374 | 61 | 25 | 0.872 | 0.126 |
| Direitos Humanos e Minorias | 11076 | 74 | 27 | 0.851 | 0.073 |
| Administração Pública | 6022 | 75 | 28 | 0.83 | 0.149 |
| Direito e Justiça | 990 | 54 | 19 | 0.821 | 0.133 |
| Indústria, Comércio e Serviços | 3808 | 71 | 25 | 0.819 | 0.124 |
| Finanças Públicas e Orçamento | 6075 | 71 | 23 | 0.818 | 0.103 |
| Defesa e Segurança | 4139 | 71 | 22 | 0.814 | 0.118 |
| Trabalho e Emprego | 5248 | 74 | 24 | 0.805 | 0.179 |

Tópicos menos puros (n ≥ 150):

| topico | nome | n | tema_dominante | pureza | temas_para_80pct |
| --- | --- | --- | --- | --- | --- |
| 24 | programa, selo, cria, selo empresa | 701 | Direitos Humanos e Minorias | 0.297 | 14 |
| 0 | política, programa, rural, desenvolvimento | 2741 | Meio Ambiente e Desenvolvimento Sustentável | 0.356 | 12 |
| 58 | câmeras, segurança, instalação, obrigatoriedade | 236 | Defesa e Segurança | 0.398 | 10 |
| 47 | constituição, transitórias, disposições constitucionais, regulamenta | 406 | Administração Pública | 0.401 | 12 |
| 13 | código, código penal, penal, crime | 803 | Direito Penal e Processual Penal | 0.482 | 10 |
| 42 | tecidos, órgãos, doação, órgãos tecidos | 286 | Saúde | 0.503 | 7 |
| 53 | universidade, campus, autoriza poder, autoriza | 186 | Educação | 0.527 | 7 |
| 69 | condenadas, nomeação, crimes, contra | 203 | Administração Pública | 0.552 | 8 |

## serafim_nn30_mcs100_eom_ms5_rk

- Pares apensada e principal: 10437; 96.3% compartilham tema oficial.
- No mesmo tópico (natural): 69.9% (acaso: 2.6%).
- No mesmo tópico (k32): 70.3% (acaso: 4.5%).

- Dispersão: 3218 proposições (8.1%) dividem tema com o resto do tópico menos do que o acaso prevê para elas.
- Pureza mediana dos tópicos: 79%; tópicos com pureza abaixo de 50%: 5 de 70.

Temas mais fragmentados (n ≥ 300):

| tema | n | n_topicos | topicos_para_80pct | entropia_norm | maior_topico_pct |
| --- | --- | --- | --- | --- | --- |
| Relações Internacionais e Comércio Exterior | 374 | 55 | 22 | 0.868 | 0.094 |
| Administração Pública | 6022 | 70 | 28 | 0.862 | 0.11 |
| Saúde | 8247 | 68 | 26 | 0.859 | 0.127 |
| Direitos Humanos e Minorias | 11076 | 70 | 28 | 0.849 | 0.163 |
| Educação | 3850 | 68 | 22 | 0.822 | 0.145 |
| Finanças Públicas e Orçamento | 6075 | 67 | 20 | 0.811 | 0.097 |
| Economia | 2488 | 60 | 18 | 0.801 | 0.15 |
| Indústria, Comércio e Serviços | 3808 | 68 | 22 | 0.801 | 0.128 |

Tópicos menos puros (n ≥ 150):

| topico | nome | n | tema_dominante | pureza | temas_para_80pct |
| --- | --- | --- | --- | --- | --- |
| 10 | desenvolvimento, inovação, programa, política | 1082 | Finanças Públicas e Orçamento | 0.336 | 11 |
| 13 | imóveis, imóvel, casa, programa casa | 860 | Direito Civil e Processual Civil | 0.349 | 9 |
| 8 | calamidade, calamidade pública, estado, estado calamidade | 1006 | Finanças Públicas e Orçamento | 0.383 | 11 |
| 26 | alimentação, alimentos, alimentação escolar, escolar | 385 | Educação | 0.392 | 7 |
| 44 | prazo, prorrogar, prorroga, prorrogar prazo | 344 | Finanças Públicas e Orçamento | 0.468 | 10 |
| 15 | militares, segurança pública, segurança, cargos | 974 | Administração Pública | 0.505 | 7 |
| 48 | universidade, autoriza poder, autoriza, campus | 205 | Educação | 0.507 | 7 |
| 34 | água, saneamento, saneamento básico, básico | 332 | Energia, Recursos Hídricos e Minerais | 0.512 | 8 |
