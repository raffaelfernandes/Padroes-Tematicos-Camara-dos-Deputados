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
| e5_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por centroide | natural | 60 | 0.662 | 0.09 | 0.158 |
| e5_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por c-TF-IDF | natural | 60 | 0.665 | 0.09 | 0.158 |
| e5_nn30_mcs100_eom_ms10_ro | outliers como grupos unitários | natural | 12357 | 0.812 | 0.056 | 0.104 |
| e5_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por centroide | k32 | 33 | 0.513 | 0.123 | 0.198 |
| e5_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por c-TF-IDF | k32 | 33 | 0.516 | 0.122 | 0.197 |
| e5_nn30_mcs100_eom_ms10_ro | aleatório, mesmos tamanhos (5 sementes) | natural | 60 | 0.245 | 0.033 | 0.058 |
| e5_nn30_mcs100_eom_ms10_ro | aleatório, mesmos tamanhos (5 sementes) | k32 | 33 | 0.245 | 0.064 | 0.101 |
| serafim_nn30_mcs100_eom_ms5_ro | outliers reatribuídos; formulaicas por centroide | natural | 72 | 0.711 | 0.08 | 0.144 |
| serafim_nn30_mcs100_eom_ms5_ro | outliers reatribuídos; formulaicas por c-TF-IDF | natural | 72 | 0.711 | 0.081 | 0.145 |
| serafim_nn30_mcs100_eom_ms5_ro | outliers como grupos unitários | natural | 14122 | 0.869 | 0.048 | 0.092 |
| serafim_nn30_mcs100_eom_ms5_ro | outliers reatribuídos; formulaicas por centroide | k32 | 32 | 0.483 | 0.097 | 0.162 |
| serafim_nn30_mcs100_eom_ms5_ro | outliers reatribuídos; formulaicas por c-TF-IDF | k32 | 32 | 0.483 | 0.098 | 0.162 |
| serafim_nn30_mcs100_eom_ms5_ro | aleatório, mesmos tamanhos (5 sementes) | natural | 72 | 0.245 | 0.019 | 0.036 |
| serafim_nn30_mcs100_eom_ms5_ro | aleatório, mesmos tamanhos (5 sementes) | k32 | 32 | 0.245 | 0.041 | 0.071 |

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
| e5_nn30_mcs100_eom_ms10_ro | PL | 38137 | 0.663 | 0.09 |
| e5_nn30_mcs100_eom_ms10_ro | PLP | 1586 | 0.649 | 0.076 |
| e5_nn30_mcs100_eom_ms10_ro | PEC | 229 | 0.566 | 0.092 |
| e5_nn30_mcs100_eom_ms10_ro | formulaicas | 493 | 0.305 | 0.101 |
| e5_nn30_mcs100_eom_ms10_ro | não formulaicas | 39459 | 0.666 | 0.089 |
| serafim_nn30_mcs100_eom_ms5_ro | PL | 38137 | 0.714 | 0.081 |
| serafim_nn30_mcs100_eom_ms5_ro | PLP | 1586 | 0.657 | 0.056 |
| serafim_nn30_mcs100_eom_ms5_ro | PEC | 229 | 0.591 | 0.076 |
| serafim_nn30_mcs100_eom_ms5_ro | formulaicas | 493 | 0.587 | 0.073 |
| serafim_nn30_mcs100_eom_ms5_ro | não formulaicas | 39459 | 0.713 | 0.08 |

## Formulaicas: centroide x c-TF-IDF

| modelo | versao | n | P_medio | R_medio |
| --- | --- | --- | --- | --- |
| bertimbau_nn30_mcs100_eom_ms10 | outliers reatribuídos; formulaicas por centroide | 493 | 0.547 | 0.083 |
| bertimbau_nn30_mcs100_eom_ms10 | outliers reatribuídos; formulaicas por c-TF-IDF | 493 | 0.611 | 0.087 |
| bertimbau_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por centroide | 493 | 0.54 | 0.084 |
| bertimbau_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por c-TF-IDF | 493 | 0.618 | 0.09 |
| e5_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por centroide | 493 | 0.305 | 0.101 |
| e5_nn30_mcs100_eom_ms10_ro | outliers reatribuídos; formulaicas por c-TF-IDF | 493 | 0.584 | 0.096 |
| serafim_nn30_mcs100_eom_ms5_ro | outliers reatribuídos; formulaicas por centroide | 493 | 0.587 | 0.073 |
| serafim_nn30_mcs100_eom_ms5_ro | outliers reatribuídos; formulaicas por c-TF-IDF | 493 | 0.585 | 0.084 |

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

## e5_nn30_mcs100_eom_ms10_ro

- Pares apensada e principal: 10437; 96.3% compartilham tema oficial.
- No mesmo tópico (natural): 55.8% (acaso: 3.4%).
- No mesmo tópico (k32): 58.2% (acaso: 6.6%).

- Dispersão: 4278 proposições (10.7%) dividem tema com o resto do tópico menos do que o acaso prevê para elas.
- Pureza mediana dos tópicos: 85%; tópicos com pureza abaixo de 50%: 4 de 60.

Temas mais fragmentados (n ≥ 300):

| tema | n | n_topicos | topicos_para_80pct | entropia_norm | maior_topico_pct |
| --- | --- | --- | --- | --- | --- |
| Direitos Humanos e Minorias | 11076 | 59 | 22 | 0.865 | 0.118 |
| Relações Internacionais e Comércio Exterior | 374 | 49 | 18 | 0.842 | 0.112 |
| Finanças Públicas e Orçamento | 6075 | 57 | 19 | 0.833 | 0.117 |
| Trabalho e Emprego | 5248 | 58 | 21 | 0.832 | 0.13 |
| Administração Pública | 6022 | 60 | 19 | 0.815 | 0.12 |
| Indústria, Comércio e Serviços | 3808 | 57 | 19 | 0.812 | 0.134 |
| Defesa e Segurança | 4139 | 58 | 18 | 0.806 | 0.133 |
| Economia | 2488 | 55 | 15 | 0.796 | 0.105 |

Tópicos menos puros (n ≥ 150):

| topico | nome | n | tema_dominante | pureza | temas_para_80pct |
| --- | --- | --- | --- | --- | --- |
| 8 | política, programa, cria, incentivo | 1760 | Direitos Humanos e Minorias | 0.297 | 13 |
| 0 | ementa, código, programa, penal | 4370 | Direitos Humanos e Minorias | 0.299 | 14 |
| 58 | digitais, plataformas, transparência, plataformas digitais | 366 | Comunicações | 0.369 | 10 |
| 3 | rural, ambiental, rurais, recursos | 1804 | Meio Ambiente e Desenvolvimento Sustentável | 0.389 | 12 |
| 51 | sul, grande sul, rio grande, grande | 269 | Finanças Públicas e Orçamento | 0.532 | 10 |
| 44 | transporte, obrigatoriedade, aplicativos, veículos | 425 | Viação, Transporte e Mobilidade | 0.539 | 9 |
| 15 | produtos, bebidas, alimentos, resíduos | 926 | Indústria, Comércio e Serviços | 0.553 | 9 |
| 18 | previdência, previdência social, social, benefícios | 824 | Previdência e Assistência Social | 0.562 | 7 |

## serafim_nn30_mcs100_eom_ms5_ro

- Pares apensada e principal: 10437; 96.3% compartilham tema oficial.
- No mesmo tópico (natural): 62.9% (acaso: 2.0%).
- No mesmo tópico (k32): 63.4% (acaso: 4.3%).

- Dispersão: 3101 proposições (7.8%) dividem tema com o resto do tópico menos do que o acaso prevê para elas.
- Pureza mediana dos tópicos: 79%; tópicos com pureza abaixo de 50%: 7 de 72.

Temas mais fragmentados (n ≥ 300):

| tema | n | n_topicos | topicos_para_80pct | entropia_norm | maior_topico_pct |
| --- | --- | --- | --- | --- | --- |
| Direitos Humanos e Minorias | 11076 | 72 | 32 | 0.9 | 0.084 |
| Administração Pública | 6022 | 72 | 31 | 0.891 | 0.071 |
| Relações Internacionais e Comércio Exterior | 374 | 53 | 22 | 0.868 | 0.115 |
| Trabalho e Emprego | 5248 | 71 | 27 | 0.849 | 0.108 |
| Indústria, Comércio e Serviços | 3808 | 68 | 25 | 0.843 | 0.135 |
| Finanças Públicas e Orçamento | 6075 | 69 | 23 | 0.839 | 0.088 |
| Direito e Justiça | 990 | 63 | 23 | 0.836 | 0.115 |
| Ciência, Tecnologia e Inovação | 1097 | 65 | 23 | 0.816 | 0.155 |

Tópicos menos puros (n ≥ 150):

| topico | nome | n | tema_dominante | pureza | temas_para_80pct |
| --- | --- | --- | --- | --- | --- |
| 48 | revoga, constituição, registro, registros | 753 | Administração Pública | 0.228 | 16 |
| 8 | cria, política, desenvolvimento, programa | 1387 | Meio Ambiente e Desenvolvimento Sustentável | 0.299 | 13 |
| 20 | rural, imóveis, rurais, agrária | 626 | Agricultura, Pecuária, Pesca e Extrativismo | 0.318 | 9 |
| 23 | alimentação, alimentos, alimentação escolar, escolar | 386 | Direitos Humanos e Minorias | 0.373 | 8 |
| 6 | calamidade, calamidade pública, estado calamidade, estado | 974 | Saúde | 0.374 | 12 |
| 47 | prazo, prorrogar, prazos, prorroga | 413 | Finanças Públicas e Orçamento | 0.421 | 10 |
| 34 | água, saneamento, saneamento básico, básico | 369 | Meio Ambiente e Desenvolvimento Sustentável | 0.461 | 8 |
| 25 | segurança, obrigatoriedade, escolas, ensino | 726 | Defesa e Segurança | 0.514 | 8 |
