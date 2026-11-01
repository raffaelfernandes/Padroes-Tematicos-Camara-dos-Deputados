# Relatório da Fase 4

39952 proposições com tema oficial; 32 temas.

## BCubed estendido

P = precisão, R = recall, F = média harmônica. Leia P e R separados: "um cluster só" tem F alto sem significar nada.

| modelo | versao | granularidade | n_grupos | P | R | F |
| --- | --- | --- | --- | --- | --- | --- |
| referência | um cluster só | - | 1 | 0.244 | 0.963 | 0.389 |
| referência | cada proposição sozinha | - | 39952 | 1.0 | 0.0 | 0.0 |
| referência | teto: tema mais frequente do gabarito | - | 31 | 1.0 | 0.435 | 0.606 |
| bertimbau_nn30_mcs100_eom_ms10 | outliers reatribuídos; formulaicas por centroide | natural | 66 | 0.734 | 0.086 | 0.154 |
| bertimbau_nn30_mcs100_eom_ms10 | outliers reatribuídos; formulaicas por c-TF-IDF | natural | 66 | 0.734 | 0.086 | 0.154 |
| bertimbau_nn30_mcs100_eom_ms10 | outliers como grupos unitários | natural | 13601 | 0.893 | 0.055 | 0.104 |
| bertimbau_nn30_mcs100_eom_ms10 | outliers reatribuídos; formulaicas por centroide | k32 | 33 | 0.545 | 0.102 | 0.172 |
| bertimbau_nn30_mcs100_eom_ms10 | outliers reatribuídos; formulaicas por c-TF-IDF | k32 | 33 | 0.546 | 0.102 | 0.172 |
| bertimbau_nn30_mcs100_eom_ms10 | aleatório, mesmos tamanhos (5 sementes) | natural | 66 | 0.245 | 0.022 | 0.04 |
| bertimbau_nn30_mcs100_eom_ms10 | aleatório, mesmos tamanhos (5 sementes) | k32 | 33 | 0.245 | 0.038 | 0.065 |
| bertimbau_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por centroide | natural | 66 | 0.743 | 0.089 | 0.159 |
| bertimbau_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por c-TF-IDF | natural | 66 | 0.745 | 0.089 | 0.16 |
| bertimbau_nn30_mcs100_eom_ms10_ro | outliers como grupos unitários | natural | 13601 | 0.893 | 0.055 | 0.104 |
| bertimbau_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por centroide | k32 | 33 | 0.554 | 0.105 | 0.177 |
| bertimbau_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por c-TF-IDF | k32 | 33 | 0.555 | 0.105 | 0.177 |
| bertimbau_nn30_mcs100_eom_ms10_ro | aleatório, mesmos tamanhos (5 sementes) | natural | 66 | 0.245 | 0.022 | 0.041 |
| bertimbau_nn30_mcs100_eom_ms10_ro | aleatório, mesmos tamanhos (5 sementes) | k32 | 33 | 0.245 | 0.038 | 0.065 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por centroide | natural | 66 | 0.746 | 0.098 | 0.173 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por c-TF-IDF | natural | 66 | 0.747 | 0.098 | 0.173 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers como grupos unitários | natural | 13601 | 0.893 | 0.055 | 0.104 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por centroide | k32 | 33 | 0.569 | 0.112 | 0.186 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por c-TF-IDF | k32 | 33 | 0.569 | 0.112 | 0.187 |
| bertimbau_nn30_mcs100_eom_ms10_rk | aleatório, mesmos tamanhos (5 sementes) | natural | 66 | 0.245 | 0.025 | 0.045 |
| bertimbau_nn30_mcs100_eom_ms10_rk | aleatório, mesmos tamanhos (5 sementes) | k32 | 33 | 0.245 | 0.038 | 0.066 |
| e5_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por centroide | natural | 60 | 0.658 | 0.097 | 0.169 |
| e5_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por c-TF-IDF | natural | 60 | 0.661 | 0.097 | 0.169 |
| e5_nn30_mcs100_eom_ms10_rk | outliers como grupos unitários | natural | 12357 | 0.812 | 0.056 | 0.104 |
| e5_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por centroide | k32 | 33 | 0.519 | 0.131 | 0.21 |
| e5_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por c-TF-IDF | k32 | 33 | 0.521 | 0.131 | 0.209 |
| e5_nn30_mcs100_eom_ms10_rk | aleatório, mesmos tamanhos (5 sementes) | natural | 60 | 0.245 | 0.035 | 0.061 |
| e5_nn30_mcs100_eom_ms10_rk | aleatório, mesmos tamanhos (5 sementes) | k32 | 33 | 0.245 | 0.067 | 0.105 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers reatribuídos; formulaicas por centroide | natural | 72 | 0.707 | 0.089 | 0.159 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers reatribuídos; formulaicas por c-TF-IDF | natural | 72 | 0.707 | 0.09 | 0.159 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers como grupos unitários | natural | 14122 | 0.869 | 0.048 | 0.092 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers reatribuídos; formulaicas por centroide | k32 | 32 | 0.49 | 0.105 | 0.173 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers reatribuídos; formulaicas por c-TF-IDF | k32 | 32 | 0.491 | 0.105 | 0.173 |
| serafim_nn30_mcs100_eom_ms5_rk | aleatório, mesmos tamanhos (5 sementes) | natural | 72 | 0.245 | 0.022 | 0.041 |
| serafim_nn30_mcs100_eom_ms5_rk | aleatório, mesmos tamanhos (5 sementes) | k32 | 32 | 0.245 | 0.042 | 0.072 |

## Por tipo de proposição e formulaicas (versão principal)

| modelo | grupo | n | P_medio | R_medio |
| --- | --- | --- | --- | --- |
| bertimbau_nn30_mcs100_eom_ms10 | PL | 38137 | 0.735 | 0.087 |
| bertimbau_nn30_mcs100_eom_ms10 | PLP | 1586 | 0.729 | 0.059 |
| bertimbau_nn30_mcs100_eom_ms10 | PEC | 229 | 0.596 | 0.079 |
| bertimbau_nn30_mcs100_eom_ms10 | formulaicas | 493 | 0.547 | 0.083 |
| bertimbau_nn30_mcs100_eom_ms10 | não formulaicas | 39459 | 0.736 | 0.086 |
| bertimbau_nn30_mcs100_eom_ms10_ro | PL | 38137 | 0.745 | 0.09 |
| bertimbau_nn30_mcs100_eom_ms10_ro | PLP | 1586 | 0.729 | 0.061 |
| bertimbau_nn30_mcs100_eom_ms10_ro | PEC | 229 | 0.597 | 0.085 |
| bertimbau_nn30_mcs100_eom_ms10_ro | formulaicas | 493 | 0.54 | 0.084 |
| bertimbau_nn30_mcs100_eom_ms10_ro | não formulaicas | 39459 | 0.746 | 0.089 |
| bertimbau_nn30_mcs100_eom_ms10_rk | PL | 38137 | 0.748 | 0.099 |
| bertimbau_nn30_mcs100_eom_ms10_rk | PLP | 1586 | 0.735 | 0.066 |
| bertimbau_nn30_mcs100_eom_ms10_rk | PEC | 229 | 0.615 | 0.09 |
| bertimbau_nn30_mcs100_eom_ms10_rk | formulaicas | 493 | 0.551 | 0.094 |
| bertimbau_nn30_mcs100_eom_ms10_rk | não formulaicas | 39459 | 0.749 | 0.098 |
| e5_nn30_mcs100_eom_ms10_rk | PL | 38137 | 0.659 | 0.098 |
| e5_nn30_mcs100_eom_ms10_rk | PLP | 1586 | 0.642 | 0.076 |
| e5_nn30_mcs100_eom_ms10_rk | PEC | 229 | 0.53 | 0.093 |
| e5_nn30_mcs100_eom_ms10_rk | formulaicas | 493 | 0.309 | 0.103 |
| e5_nn30_mcs100_eom_ms10_rk | não formulaicas | 39459 | 0.662 | 0.097 |
| serafim_nn30_mcs100_eom_ms5_rk | PL | 38137 | 0.71 | 0.091 |
| serafim_nn30_mcs100_eom_ms5_rk | PLP | 1586 | 0.66 | 0.06 |
| serafim_nn30_mcs100_eom_ms5_rk | PEC | 229 | 0.569 | 0.08 |
| serafim_nn30_mcs100_eom_ms5_rk | formulaicas | 493 | 0.588 | 0.079 |
| serafim_nn30_mcs100_eom_ms5_rk | não formulaicas | 39459 | 0.709 | 0.09 |

## Formulaicas: centroide x c-TF-IDF

| modelo | versao | n | P_medio | R_medio |
| --- | --- | --- | --- | --- |
| bertimbau_nn30_mcs100_eom_ms10 | outliers reatribuídos; formulaicas por centroide | 493 | 0.547 | 0.083 |
| bertimbau_nn30_mcs100_eom_ms10 | outliers reatribuídos; formulaicas por c-TF-IDF | 493 | 0.611 | 0.087 |
| bertimbau_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por centroide | 493 | 0.54 | 0.084 |
| bertimbau_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por c-TF-IDF | 493 | 0.618 | 0.09 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por centroide | 493 | 0.551 | 0.094 |
| bertimbau_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por c-TF-IDF | 493 | 0.622 | 0.096 |
| e5_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por centroide | 493 | 0.309 | 0.103 |
| e5_nn30_mcs100_eom_ms10_rk | outliers reatribuídos; formulaicas por c-TF-IDF | 493 | 0.584 | 0.106 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers reatribuídos; formulaicas por centroide | 493 | 0.588 | 0.079 |
| serafim_nn30_mcs100_eom_ms5_rk | outliers reatribuídos; formulaicas por c-TF-IDF | 493 | 0.578 | 0.09 |

## bertimbau_nn30_mcs100_eom_ms10

- Pares apensada e principal: 10437; 96.3% compartilham tema oficial.
- No mesmo tópico (natural): 66.4% (acaso: 2.2%).
- No mesmo tópico (k32): 66.7% (acaso: 3.9%).

- Dispersão: 2535 proposições (6.3%) dividem tema com o resto do tópico menos do que o acaso prevê para elas.
- Pureza mediana dos tópicos: 85%; tópicos com pureza abaixo de 50%: 8 de 66.

Temas mais fragmentados (n ≥ 300):

| tema | n | n_topicos | topicos_para_80pct | entropia_norm | maior_topico_pct |
| --- | --- | --- | --- | --- | --- |
| Administração Pública | 6022 | 65 | 27 | 0.878 | 0.105 |
| Indústria, Comércio e Serviços | 3808 | 64 | 25 | 0.859 | 0.101 |
| Direitos Humanos e Minorias | 11076 | 66 | 24 | 0.858 | 0.091 |
| Relações Internacionais e Comércio Exterior | 374 | 50 | 18 | 0.853 | 0.12 |
| Cidades e Desenvolvimento Urbano | 1648 | 59 | 20 | 0.848 | 0.095 |
| Economia | 2488 | 62 | 20 | 0.828 | 0.107 |
| Finanças Públicas e Orçamento | 6075 | 64 | 22 | 0.821 | 0.113 |
| Trabalho e Emprego | 5248 | 64 | 23 | 0.814 | 0.148 |

Tópicos menos puros (n ≥ 150):

| topico | nome | n | tema_dominante | pureza | temas_para_80pct |
| --- | --- | --- | --- | --- | --- |
| 44 | estabelecimentos, obrigatoriedade, instalação, segurança | 509 | Indústria, Comércio e Serviços | 0.33 | 10 |
| 50 | política, programa, agricultura, cria | 617 | Direitos Humanos e Minorias | 0.334 | 12 |
| 33 | esporte, atletas, esportivas, futebol | 844 | Esporte e Lazer | 0.353 | 15 |
| 54 | inovação, desenvolvimento, programa, pesquisa | 654 | Finanças Públicas e Orçamento | 0.394 | 11 |
| 7 | internet, digitais, dados, crianças | 1266 | Direitos Humanos e Minorias | 0.412 | 10 |
| 60 | programa, programa casa, casa, casa vida | 343 | Direitos Humanos e Minorias | 0.423 | 9 |
| 58 | universidade, área, estado, desenvolvimento | 242 | Economia | 0.442 | 8 |
| 19 | militares, constituição, cargos, bombeiros | 752 | Administração Pública | 0.465 | 10 |

## bertimbau_nn30_mcs100_eom_ms10_ro

- Pares apensada e principal: 10437; 96.3% compartilham tema oficial.
- No mesmo tópico (natural): 64.1% (acaso: 2.3%).
- No mesmo tópico (k32): 64.5% (acaso: 3.9%).

- Dispersão: 2806 proposições (7.0%) dividem tema com o resto do tópico menos do que o acaso prevê para elas.
- Pureza mediana dos tópicos: 84%; tópicos com pureza abaixo de 50%: 6 de 66.

Temas mais fragmentados (n ≥ 300):

| tema | n | n_topicos | topicos_para_80pct | entropia_norm | maior_topico_pct |
| --- | --- | --- | --- | --- | --- |
| Direitos Humanos e Minorias | 11076 | 66 | 24 | 0.866 | 0.097 |
| Administração Pública | 6022 | 66 | 26 | 0.857 | 0.14 |
| Relações Internacionais e Comércio Exterior | 374 | 51 | 18 | 0.85 | 0.11 |
| Economia | 2488 | 62 | 19 | 0.834 | 0.115 |
| Indústria, Comércio e Serviços | 3808 | 63 | 22 | 0.833 | 0.113 |
| Cidades e Desenvolvimento Urbano | 1648 | 60 | 19 | 0.828 | 0.103 |
| Finanças Públicas e Orçamento | 6075 | 65 | 21 | 0.814 | 0.117 |
| Trabalho e Emprego | 5248 | 65 | 22 | 0.8 | 0.154 |

Tópicos menos puros (n ≥ 150):

| topico | nome | n | tema_dominante | pureza | temas_para_80pct |
| --- | --- | --- | --- | --- | --- |
| 50 | política, programa, agricultura, incentivo | 745 | Agricultura, Pecuária, Pesca e Extrativismo | 0.303 | 12 |
| 44 | estabelecimentos, obrigatoriedade, instalação, comerciais | 912 | Indústria, Comércio e Serviços | 0.33 | 11 |
| 54 | inovação, desenvolvimento, pesquisa, tecnológica | 487 | Ciência, Tecnologia e Inovação | 0.421 | 10 |
| 7 | internet, digitais, crianças, crianças adolescentes | 1348 | Direitos Humanos e Minorias | 0.435 | 10 |
| 19 | militares, constituição, cargos, bombeiros | 949 | Administração Pública | 0.443 | 11 |
| 58 | universidade, desenvolvimento, estado, área | 286 | Economia | 0.448 | 9 |
| 18 | terras, ambiental, áreas, conservação | 845 | Meio Ambiente e Desenvolvimento Sustentável | 0.518 | 10 |
| 53 | saneamento, água, saneamento básico, básico | 277 | Energia, Recursos Hídricos e Minerais | 0.57 | 7 |

## bertimbau_nn30_mcs100_eom_ms10_rk

- Pares apensada e principal: 10437; 96.3% compartilham tema oficial.
- No mesmo tópico (natural): 66.6% (acaso: 2.6%).
- No mesmo tópico (k32): 66.9% (acaso: 4.0%).

- Dispersão: 2842 proposições (7.1%) dividem tema com o resto do tópico menos do que o acaso prevê para elas.
- Pureza mediana dos tópicos: 84%; tópicos com pureza abaixo de 50%: 5 de 66.

Temas mais fragmentados (n ≥ 300):

| tema | n | n_topicos | topicos_para_80pct | entropia_norm | maior_topico_pct |
| --- | --- | --- | --- | --- | --- |
| Administração Pública | 6022 | 66 | 27 | 0.868 | 0.117 |
| Direitos Humanos e Minorias | 11076 | 66 | 22 | 0.845 | 0.112 |
| Relações Internacionais e Comércio Exterior | 374 | 51 | 17 | 0.838 | 0.123 |
| Indústria, Comércio e Serviços | 3808 | 64 | 22 | 0.828 | 0.111 |
| Cidades e Desenvolvimento Urbano | 1648 | 61 | 19 | 0.825 | 0.12 |
| Economia | 2488 | 61 | 19 | 0.824 | 0.137 |
| Finanças Públicas e Orçamento | 6075 | 65 | 21 | 0.804 | 0.131 |
| Turismo | 469 | 43 | 15 | 0.787 | 0.211 |

Tópicos menos puros (n ≥ 150):

| topico | nome | n | tema_dominante | pureza | temas_para_80pct |
| --- | --- | --- | --- | --- | --- |
| 7 | internet, digitais, proteção, dados | 1489 | Direitos Humanos e Minorias | 0.39 | 10 |
| 44 | estabelecimentos, obrigatoriedade, comerciais, instalação | 506 | Indústria, Comércio e Serviços | 0.421 | 10 |
| 19 | militares, constituição, cargos, bombeiros | 836 | Administração Pública | 0.432 | 11 |
| 54 | inovação, desenvolvimento, pesquisa, tecnológica | 424 | Ciência, Tecnologia e Inovação | 0.455 | 10 |
| 50 | política, programa, agricultura, agricultura familiar | 452 | Agricultura, Pecuária, Pesca e Extrativismo | 0.473 | 11 |
| 18 | ambiental, terras, conservação, áreas | 883 | Meio Ambiente e Desenvolvimento Sustentável | 0.545 | 10 |
| 58 | desenvolvimento, universidade, área, estado | 202 | Economia | 0.554 | 7 |
| 13 | produtos, medicamentos, alimentos, comercialização | 753 | Saúde | 0.607 | 6 |

## e5_nn30_mcs100_eom_ms10_rk

- Pares apensada e principal: 10437; 96.3% compartilham tema oficial.
- No mesmo tópico (natural): 58.6% (acaso: 3.6%).
- No mesmo tópico (k32): 61.1% (acaso: 6.9%).

- Dispersão: 4204 proposições (10.5%) dividem tema com o resto do tópico menos do que o acaso prevê para elas.
- Pureza mediana dos tópicos: 83%; tópicos com pureza abaixo de 50%: 4 de 60.

Temas mais fragmentados (n ≥ 300):

| tema | n | n_topicos | topicos_para_80pct | entropia_norm | maior_topico_pct |
| --- | --- | --- | --- | --- | --- |
| Relações Internacionais e Comércio Exterior | 374 | 47 | 20 | 0.883 | 0.11 |
| Direitos Humanos e Minorias | 11076 | 59 | 21 | 0.851 | 0.117 |
| Finanças Públicas e Orçamento | 6075 | 56 | 19 | 0.835 | 0.114 |
| Administração Pública | 6022 | 60 | 20 | 0.83 | 0.112 |
| Trabalho e Emprego | 5248 | 58 | 20 | 0.825 | 0.138 |
| Indústria, Comércio e Serviços | 3808 | 57 | 19 | 0.812 | 0.119 |
| Defesa e Segurança | 4139 | 57 | 17 | 0.798 | 0.121 |
| Economia | 2488 | 55 | 14 | 0.782 | 0.104 |

Tópicos menos puros (n ≥ 150):

| topico | nome | n | tema_dominante | pureza | temas_para_80pct |
| --- | --- | --- | --- | --- | --- |
| 8 | política, programa, cria, incentivo | 1519 | Direitos Humanos e Minorias | 0.288 | 13 |
| 0 | ementa, código, programa, penal | 4313 | Direitos Humanos e Minorias | 0.3 | 14 |
| 3 | rural, ambiental, recursos, áreas | 2023 | Meio Ambiente e Desenvolvimento Sustentável | 0.384 | 12 |
| 58 | transparência, digitais, plataformas, artificial | 212 | Direito e Defesa do Consumidor | 0.387 | 10 |
| 51 | sul, grande sul, rio grande, grande | 205 | Finanças Públicas e Orçamento | 0.532 | 9 |
| 18 | previdência, previdência social, social, benefícios | 782 | Previdência e Assistência Social | 0.556 | 7 |
| 44 | transporte, aplicativos, passageiros, entrega | 272 | Viação, Transporte e Mobilidade | 0.566 | 8 |
| 20 | internet, crianças, adolescentes, crianças adolescentes | 947 | Direitos Humanos e Minorias | 0.583 | 9 |

## serafim_nn30_mcs100_eom_ms5_rk

- Pares apensada e principal: 10437; 96.3% compartilham tema oficial.
- No mesmo tópico (natural): 65.7% (acaso: 2.3%).
- No mesmo tópico (k32): 66.1% (acaso: 4.4%).

- Dispersão: 3159 proposições (7.9%) dividem tema com o resto do tópico menos do que o acaso prevê para elas.
- Pureza mediana dos tópicos: 80%; tópicos com pureza abaixo de 50%: 7 de 72.

Temas mais fragmentados (n ≥ 300):

| tema | n | n_topicos | topicos_para_80pct | entropia_norm | maior_topico_pct |
| --- | --- | --- | --- | --- | --- |
| Administração Pública | 6022 | 72 | 29 | 0.886 | 0.074 |
| Direitos Humanos e Minorias | 11076 | 72 | 31 | 0.882 | 0.107 |
| Relações Internacionais e Comércio Exterior | 374 | 57 | 21 | 0.852 | 0.128 |
| Finanças Públicas e Orçamento | 6075 | 68 | 24 | 0.841 | 0.082 |
| Trabalho e Emprego | 5248 | 71 | 25 | 0.839 | 0.109 |
| Indústria, Comércio e Serviços | 3808 | 69 | 24 | 0.83 | 0.139 |
| Direito e Justiça | 990 | 60 | 22 | 0.819 | 0.153 |
| Economia | 2488 | 67 | 22 | 0.819 | 0.146 |

Tópicos menos puros (n ≥ 150):

| topico | nome | n | tema_dominante | pureza | temas_para_80pct |
| --- | --- | --- | --- | --- | --- |
| 48 | constituição, registro, registros públicos, registros | 493 | Direito Civil e Processual Civil | 0.272 | 14 |
| 8 | desenvolvimento, cria, política, programa | 1369 | Meio Ambiente e Desenvolvimento Sustentável | 0.294 | 12 |
| 20 | rural, imóveis, agrária, rurais | 636 | Agricultura, Pecuária, Pesca e Extrativismo | 0.324 | 9 |
| 6 | calamidade, calamidade pública, estado calamidade, estado | 1098 | Finanças Públicas e Orçamento | 0.366 | 11 |
| 23 | alimentação, alimentos, alimentação escolar, escolar | 391 | Direitos Humanos e Minorias | 0.381 | 8 |
| 34 | água, saneamento, saneamento básico, básico | 380 | Meio Ambiente e Desenvolvimento Sustentável | 0.437 | 9 |
| 47 | prazo, prorrogar, prorroga, prazos | 332 | Finanças Públicas e Orçamento | 0.476 | 10 |
| 42 | entidades, renda, imposto, imposto renda | 482 | Finanças Públicas e Orçamento | 0.539 | 9 |
