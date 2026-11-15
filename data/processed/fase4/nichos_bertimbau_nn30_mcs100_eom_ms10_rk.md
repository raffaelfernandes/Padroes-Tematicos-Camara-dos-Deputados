# Nichos dentro dos outliers: bertimbau_nn30_mcs100_eom_ms10_rk

UMAP (15 vizinhos, 5 dimensões, semente 130) e HDBSCAN (eom, min_samples 10) ajustados só nos 12736 textos únicos fora do núcleo. Versão analisada: tamanho mínimo 30.

## Sensibilidade ao tamanho mínimo de grupo

| tamanho mínimo | nichos | sem grupo | maior nicho (textos) | mediana (textos) |
| --- | --- | --- | --- | --- |
| 15 | 160 | 44.4% | 249 | 32 |
| 30 | 86 | 45.8% | 314 | 61 |
| 50 | 2 | 0.4% | 12592 | 6341 |
| 100 | 24 | 36.6% | 2192 | 166 |

Na versão analisada: 86 nichos com 7101 proposições (54.1% dos outliers com tema oficial); 6019 proposições sem grupo. Em média, 39% das proposições de um nicho foram reatribuídas ao mesmo tópico.

## Os 30 maiores nichos

| nicho | termos | proposicoes | topico_mais_parecido | similaridade | no_mesmo_topico_reatrib | tema_cedi_dominante | pureza_cedi | temas_para_80pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 71 | crédito, operações, operações crédito, rural, crédito rural | 317 | 61 (crédito_financeiras_instituições) | 0.974 | 0.29 | Economia | 0.625 | 9 |
| 81 | penal, crimes, código, código penal, pena | 316 | 1 (código penal_penal_crime) | 0.991 | 0.63 | Direito Penal e Processual Penal | 0.946 | 4 |
| 44 | cultura, indígenas, cultural, povos, tradicionais | 302 | 17 (política_desenvolvimento_programa) | 0.968 | 0.27 | Arte, Cultura e Religião | 0.626 | 8 |
| 65 | consumidor, fraudes, digitais, financeiras, plataformas | 247 | 28 (internet_dados_digitais) | 0.981 | 0.3 | Direito e Defesa do Consumidor | 0.628 | 7 |
| 74 | criança, adolescente, criança adolescente, estatuto criança, código penal | 223 | 1 (código penal_penal_crime) | 0.967 | 0.5 | Direito Penal e Processual Penal | 0.807 | 5 |
| 33 | medicamentos, sanitária, vigilância sanitária, vigilância, uso | 180 | 35 (produtos_alimentos_bebidas) | 0.971 | 0.35 | Saúde | 0.939 | 4 |
| 55 | doméstica, violência doméstica, situação, mulheres, familiar | 159 | 10 (violência_doméstica_violência doméstica) | 0.973 | 0.42 | Direitos Humanos e Minorias | 0.906 | 6 |
| 48 | programa, vulnerabilidade, situação, situação vulnerabilidade, digital | 156 | 17 (política_desenvolvimento_programa) | 0.975 | 0.25 | Direitos Humanos e Minorias | 0.615 | 9 |
| 69 | veículos, transporte, passageiros, instalação, obrigatoriedade | 155 | 31 (estabelecimentos_obrigatoriedade_segurança) | 0.981 | 0.25 | Viação, Transporte e Mobilidade | 0.6 | 8 |
| 47 | sociedades, economia mista, mista, economia, participação | 153 | 32 (administração_administração pública_licitações) | 0.958 | 0.16 | Administração Pública | 0.523 | 6 |
| 61 | inteligência, dados, governança, transparência, inteligência artificial | 145 | 28 (internet_dados_digitais) | 0.965 | 0.38 | Administração Pública | 0.676 | 9 |
| 57 | mental, saúde mental, saúde, prevenção, suicídio | 144 | 2 (saúde_único saúde_sistema único) | 0.972 | 0.47 | Saúde | 0.778 | 5 |
| 39 | tribunais, república, deputados, presidentes, tribunais contas | 134 | 9 (segurança pública_segurança_militares) | 0.969 | 0.19 | Administração Pública | 0.761 | 7 |
| 41 | preconceito, raça, discriminação, cor, raça cor | 128 | 64 (terrorismo_criminosas_organizações) | 0.955 | 0.53 | Direitos Humanos e Minorias | 0.891 | 6 |
| 64 | microempresas, pequeno, pequeno porte, empresas pequeno, microempresas empresas | 115 | 44 (pequeno porte_pequeno_complementar) | 0.958 | 0.65 | Indústria, Comércio e Serviços | 0.861 | 4 |
| 40 | advogados, ordem advogados, advogados brasil, advocacia, ordem | 110 | 3 (civil_processo civil_código civil) | 0.934 | 0.51 | Trabalho e Emprego | 0.682 | 5 |
| 27 | registros públicos, registros, serviço voluntário, passaporte, acrescentando | 110 | 39 (esporte_atletas_esportivas) | 0.905 | 0.19 | Direitos Humanos e Minorias | 0.355 | 13 |
| 34 | estabelecimentos, restaurantes, supermercados, bares, similares | 109 | 31 (estabelecimentos_obrigatoriedade_segurança) | 0.974 | 0.28 | Indústria, Comércio e Serviços | 0.789 | 5 |
| 76 | educação, ensino, deficiência, habilidades, bases educação | 108 | 7 (educação_ensino_diretrizes bases) | 0.967 | 0.49 | Educação | 0.898 | 3 |
| 85 | cacau, energética, carbono, produção, sustentável | 101 | 17 (política_desenvolvimento_programa) | 0.982 | 0.36 | Meio Ambiente e Desenvolvimento Sustentável | 0.505 | 8 |
| 9 | alimentos, alimentar, alimentar nutricional, nutricional, segurança alimentar | 101 | 17 (política_desenvolvimento_programa) | 0.955 | 0.46 | Agricultura, Pecuária, Pesca e Extrativismo | 0.525 | 7 |
| 59 | entidades, complementar, lucrativos, beneficentes, benefícios | 98 | 60 (tributário_código tributário_tributária) | 0.967 | 0.2 | Finanças Públicas e Orçamento | 0.867 | 7 |
| 1 | fies, financiamento, fundo financiamento, financiamento estudantil, estudantil | 92 | 26 (ensino_superior_educação) | 0.952 | 0.51 | Educação | 0.989 | 4 |
| 14 | estágio, horas, jornada, estágio estudantes, adicional | 92 | 26 (ensino_superior_educação) | 0.962 | 0.25 | Trabalho e Emprego | 0.554 | 5 |
| 7 | tecidos, órgãos tecidos, sangue, órgãos, corpo | 91 | 2 (saúde_único saúde_sistema único) | 0.934 | 0.41 | Saúde | 0.901 | 6 |
| 73 | internação, estatuto criança, adolescente, criança adolescente, criança | 91 | 49 (adolescente_criança adolescente_criança) | 0.964 | 0.4 | Direitos Humanos e Minorias | 0.835 | 3 |
| 23 | assédio, prevenção, sexual, crianças, eventos | 86 | 48 (crianças adolescentes_crianças_adolescentes) | 0.974 | 0.37 | Direitos Humanos e Minorias | 0.791 | 8 |
| 26 | saúde, cirurgia, único saúde, sistema único, reparadora | 83 | 2 (saúde_único saúde_sistema único) | 0.974 | 0.69 | Saúde | 0.964 | 2 |
| 18 | manutenção desenvolvimento, educação, manutenção, desenvolvimento educação, fundeb | 82 | 7 (educação_ensino_diretrizes bases) | 0.951 | 0.33 | Educação | 0.963 | 4 |
| 58 | imposto renda, contribuição, débitos, imposto, receita | 81 | 60 (tributário_código tributário_tributária) | 0.978 | 0.25 | Finanças Públicas e Orçamento | 0.938 | 6 |

## O CEDI também agrupa os nichos?

| comparação | valor |
| --- | --- |
| pureza mediana pelo CEDI: nichos | 0.755 |
| pureza mediana pelo CEDI: grupos aleatórios dos mesmos tamanhos | 0.312 |
| pureza mediana pelo CEDI: 66 tópicos principais | 0.858 |
| precisão BCubed (só proposições em nichos): agrupadas pelos nichos | 0.725 |
| precisão BCubed (mesmas proposições): agrupadas pelos tópicos da reatribuição | 0.641 |
| precisão BCubed (mesmas proposições): nichos embaralhados | 0.289 |

## Como o CEDI classificou cada grupo

| grupo | proposicoes | temas por proposição | com 4 ou mais temas |
| --- | --- | --- | --- |
| núcleo do HDBSCAN | 26340 | 2.07 | 5.7% |
| outliers em nichos | 7101 | 2.25 | 8.4% |
| outliers sem grupo | 6019 | 2.34 | 10.5% |

### Temas mais sobre-representados no que ficou sem grupo (razão sobre o corpus)

| tema | % das classificações (sem grupo) | % das classificações (corpus) | razão |
| --- | --- | --- | --- |
| Ciência, Tecnologia e Inovação | 1.9 | 1.3 | 1.48 |
| Administração Pública | 9.7 | 7.0 | 1.38 |
| Direito e Justiça | 1.6 | 1.2 | 1.36 |
| Comunicações | 2.3 | 2.0 | 1.17 |
| Economia | 3.4 | 2.9 | 1.17 |
| Defesa e Segurança | 5.6 | 4.8 | 1.16 |
| Cidades e Desenvolvimento Urbano | 2.2 | 1.9 | 1.15 |
| Direitos Humanos e Minorias | 14.1 | 12.9 | 1.09 |
| Direito Penal e Processual Penal | 6.4 | 6.0 | 1.06 |
| Educação | 4.7 | 4.5 | 1.05 |

### Temas mais sub-representados no que ficou sem grupo

| tema | % das classificações (sem grupo) | % das classificações (corpus) | razão |
| --- | --- | --- | --- |
| Esporte e Lazer | 1.1 | 1.4 | 0.84 |
| Arte, Cultura e Religião | 1.5 | 1.8 | 0.84 |
| Trabalho e Emprego | 4.8 | 6.1 | 0.79 |
| Viação, Transporte e Mobilidade | 2.7 | 3.6 | 0.75 |
| Direito e Defesa do Consumidor | 2.0 | 2.9 | 0.7 |
| Homenagens e Datas Comemorativas | 0.8 | 3.1 | 0.25 |
