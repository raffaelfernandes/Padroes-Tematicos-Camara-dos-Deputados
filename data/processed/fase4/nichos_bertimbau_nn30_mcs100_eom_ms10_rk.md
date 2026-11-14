# Nichos dentro dos outliers: bertimbau_nn30_mcs100_eom_ms10_rk

UMAP (15 vizinhos, 5 dimensões, semente 42) e HDBSCAN (eom, min_samples 10) ajustados só nos 12704 textos únicos fora do núcleo. Versão analisada: tamanho mínimo 30.

## Sensibilidade ao tamanho mínimo de grupo

| tamanho mínimo | nichos | sem grupo | maior nicho (textos) | mediana (textos) |
| --- | --- | --- | --- | --- |
| 15 | 168 | 48.5% | 175 | 29 |
| 30 | 79 | 49.6% | 380 | 63 |
| 50 | 4 | 0.6% | 12388 | 93 |
| 100 | 2 | 0.6% | 12482 | 6314 |

Na versão analisada: 79 nichos com 6569 proposições (50.4% dos outliers com tema oficial); 6473 proposições sem grupo. Em média, 36% das proposições de um nicho foram reatribuídas ao mesmo tópico.

## Os 30 maiores nichos

| nicho | termos | proposicoes | topico_mais_parecido | similaridade | no_mesmo_topico_reatrib | tema_cedi_dominante | pureza_cedi | temas_para_80pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 75 | penal, código, código penal, código processo, processo penal | 385 | 1 (penal_código penal_crime) | 0.991 | 0.57 | Direito Penal e Processual Penal | 0.886 | 5 |
| 35 | consumidor, plataformas, serviços, digitais, defesa consumidor | 220 | 49 (telecomunicações_serviços_serviços telecomunicações) | 0.979 | 0.3 | Direito e Defesa do Consumidor | 0.686 | 8 |
| 23 | telecomunicações, serviços, serviços telecomunicações, serviços públicos, universalização | 199 | 17 (administração_administração pública_licitações) | 0.977 | 0.32 | Comunicações | 0.533 | 10 |
| 50 | sustentável, logística, carbono, cacau, programa | 192 | 52 (desastres_defesa civil_proteção defesa) | 0.974 | 0.25 | Meio Ambiente e Desenvolvimento Sustentável | 0.432 | 10 |
| 68 | mental, saúde mental, saúde, política, suicídio | 176 | 4 (saúde_único saúde_sistema único) | 0.969 | 0.35 | Saúde | 0.801 | 6 |
| 69 | criança, adolescente, criança adolescente, contra, crianças adolescentes | 166 | 6 (violência_doméstica_violência doméstica) | 0.983 | 0.36 | Direitos Humanos e Minorias | 0.831 | 5 |
| 77 | sistema único, único saúde, sus, saúde, único | 161 | 4 (saúde_único saúde_sistema único) | 0.982 | 0.38 | Saúde | 0.913 | 2 |
| 10 | entidades, lucrativos, organizações, sociedade civil, organizações sociedade | 148 | 17 (administração_administração pública_licitações) | 0.969 | 0.13 | Finanças Públicas e Orçamento | 0.419 | 7 |
| 21 | obrigatoriedade, eventos, casas, estabelecimentos, bares | 137 | 44 (estabelecimentos_obrigatoriedade_comerciais) | 0.983 | 0.32 | Direitos Humanos e Minorias | 0.562 | 9 |
| 54 | cultura, cultural, patrimônio, culturais, pronac | 136 | 54 (inovação_desenvolvimento_pesquisa) | 0.96 | 0.27 | Arte, Cultura e Religião | 0.941 | 5 |
| 31 | registros, registros públicos, utilidade pública, serviço voluntário, desapropriações | 135 | 63 (código penal_penal_código) | 0.955 | 0.19 | Administração Pública | 0.252 | 14 |
| 36 | combustíveis, veículos, postos, elétricos, veículos elétricos | 133 | 44 (estabelecimentos_obrigatoriedade_comerciais) | 0.974 | 0.25 | Energia, Recursos Hídricos e Minerais | 0.609 | 6 |
| 37 | transporte, animais, território, transporte animais, domésticos | 133 | 44 (estabelecimentos_obrigatoriedade_comerciais) | 0.964 | 0.19 | Viação, Transporte e Mobilidade | 0.474 | 9 |
| 52 | apreendidos, bens, destinação, lavagem, direitos valores | 132 | 17 (administração_administração pública_licitações) | 0.971 | 0.23 | Direito Penal e Processual Penal | 0.409 | 9 |
| 71 | pessoa, deficiência, síndrome, fibromialgia, pessoas | 129 | 20 (transtorno_autista_espectro) | 0.963 | 0.47 | Saúde | 0.682 | 6 |
| 41 | inteligência, inteligência artificial, artificial, dados, governança | 129 | 17 (administração_administração pública_licitações) | 0.967 | 0.47 | Administração Pública | 0.543 | 9 |
| 59 | dia, programa, selo empresa, empresa, selo | 120 | 50 (política_programa_agricultura) | 0.939 | 0.3 | Direitos Humanos e Minorias | 0.358 | 12 |
| 78 | único saúde, sistema único, saúde, único, sus | 110 | 4 (saúde_único saúde_sistema único) | 0.981 | 0.55 | Saúde | 0.982 | 2 |
| 42 | desaparecidas, pessoas desaparecidas, cadastro, delegacias, delegacias especializadas | 109 | 48 (violência_política_prevenção) | 0.969 | 0.4 | Defesa e Segurança | 0.743 | 6 |
| 19 | escolar, alimentação escolar, alimentação, programa alimentação, pnae | 103 | 9 (educação_ensino_diretrizes bases) | 0.974 | 0.45 | Educação | 0.893 | 5 |
| 22 | insalubridade, adicional, segurança, segurança privada, adicional insalubridade | 98 | 44 (estabelecimentos_obrigatoriedade_comerciais) | 0.975 | 0.13 | Trabalho e Emprego | 0.684 | 7 |
| 72 | educação, diretrizes bases, bases educação, ensino, bases | 97 | 9 (educação_ensino_diretrizes bases) | 0.977 | 0.53 | Educação | 0.99 | 2 |
| 1 | fies, financiamento, fundo financiamento, financiamento estudantil, estudantil | 96 | 31 (ensino_superior_instituições) | 0.959 | 0.46 | Educação | 0.979 | 4 |
| 3 | universidade, campus, instituto, autoriza poder, poder executivo | 93 | 58 (desenvolvimento_universidade_área) | 0.961 | 0.53 | Educação | 0.935 | 3 |
| 46 | auxílio emergencial, emergencial, auxílio, pagamento auxílio, emergencial trata | 89 | 28 (benefício_família_prestação continuada) | 0.96 | 0.26 | Previdência e Assistência Social | 0.584 | 5 |
| 43 | banco central, central brasil, central, financeiras, pix | 89 | 38 (apostas_quota fixa_quota) | 0.957 | 0.38 | Economia | 0.888 | 5 |
| 47 | disposições constitucionais, transitórias, constitucionais transitórias, ato disposições, constitucionais | 88 | 19 (militares_constituição_cargos) | 0.977 | 0.38 | Finanças Públicas e Orçamento | 0.659 | 8 |
| 9 | tecidos, órgãos tecidos, órgãos, corpo, partes corpo | 87 | 43 (parto_recém_neonatal) | 0.949 | 0.44 | Saúde | 0.966 | 4 |
| 55 | indígenas, povos, tradicionais, comunidades, povos indígenas | 82 | 50 (política_programa_agricultura) | 0.943 | 0.32 | Direitos Humanos e Minorias | 0.829 | 7 |
| 62 | crimes ambientais, ambientais, incêndio, crimes, pena | 78 | 1 (penal_código penal_crime) | 0.975 | 0.73 | Meio Ambiente e Desenvolvimento Sustentável | 0.923 | 2 |

## O CEDI também agrupa os nichos?

| comparação | valor |
| --- | --- |
| pureza mediana pelo CEDI: nichos | 0.761 |
| pureza mediana pelo CEDI: grupos aleatórios dos mesmos tamanhos | 0.311 |
| pureza mediana pelo CEDI: 66 tópicos principais | 0.832 |
| precisão BCubed (só proposições em nichos): agrupadas pelos nichos | 0.704 |
| precisão BCubed (mesmas proposições): agrupadas pelos tópicos da reatribuição | 0.63 |
| precisão BCubed (mesmas proposições): nichos embaralhados | 0.278 |

## Como o CEDI classificou cada grupo

| grupo | proposicoes | temas por proposição | com 4 ou mais temas |
| --- | --- | --- | --- |
| núcleo do HDBSCAN | 26417 | 2.08 | 5.9% |
| outliers em nichos | 6569 | 2.25 | 8.7% |
| outliers sem grupo | 6473 | 2.29 | 9.5% |

### Temas mais sobre-representados no que ficou sem grupo (razão sobre o corpus)

| tema | % das classificações (sem grupo) | % das classificações (corpus) | razão |
| --- | --- | --- | --- |
| Administração Pública | 9.9 | 7.0 | 1.4 |
| Economia | 3.6 | 2.9 | 1.25 |
| Educação | 5.6 | 4.5 | 1.24 |
| Defesa e Segurança | 5.8 | 4.8 | 1.21 |
| Ciência, Tecnologia e Inovação | 1.5 | 1.3 | 1.18 |
| Cidades e Desenvolvimento Urbano | 2.2 | 1.9 | 1.17 |
| Agricultura, Pecuária, Pesca e Extrativismo | 1.8 | 1.6 | 1.14 |
| Turismo | 0.6 | 0.5 | 1.11 |
| Meio Ambiente e Desenvolvimento Sustentável | 4.0 | 3.6 | 1.1 |
| Direitos Humanos e Minorias | 13.5 | 12.9 | 1.05 |

### Temas mais sub-representados no que ficou sem grupo

| tema | % das classificações (sem grupo) | % das classificações (corpus) | razão |
| --- | --- | --- | --- |
| Viação, Transporte e Mobilidade | 3.0 | 3.6 | 0.83 |
| Previdência e Assistência Social | 2.2 | 2.6 | 0.82 |
| Esporte e Lazer | 1.1 | 1.4 | 0.79 |
| Política, Partidos e Eleições | 0.7 | 1.0 | 0.73 |
| Direito e Defesa do Consumidor | 1.8 | 2.9 | 0.64 |
| Homenagens e Datas Comemorativas | 1.1 | 3.1 | 0.34 |
