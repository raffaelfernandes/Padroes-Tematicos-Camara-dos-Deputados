# Comparação entre os três modelos

Proposições em comum: 40006. Coluna de tópico: `topico_alt_ctfidf` (formulaicas pelo c-TF-IDF).

## 1. Concordância entre as partições

ARI e NMI entre os tópicos de cada par de modelos; `topicos_a_com_par_jac50`: fração dos tópicos do modelo A cujo tópico mais parecido no modelo B tem Jaccard de pelo menos 0,5.

| modelo_a   | modelo_b   |   ARI |   NMI |   topicos_a_com_par_jac50 |   topicos_b_com_par_jac50 |   jaccard_mediano_a |   jaccard_mediano_b |
|:-----------|:-----------|------:|------:|--------------------------:|--------------------------:|--------------------:|--------------------:|
| BERTimbau  | Serafim    | 0.325 | 0.555 |                     0.224 |                     0.214 |               0.334 |               0.323 |
| BERTimbau  | e5         | 0.378 | 0.584 |                     0.343 |                     0.307 |               0.42  |               0.396 |
| Serafim    | e5         | 0.298 | 0.537 |                     0.186 |                     0.173 |               0.312 |               0.291 |

ARI com o e5 embaralhado (5 sementes): média 0.0001.

## 2. Fragmentação (tópicos para reunir 80% do tema)

| tema                             |   BERTimbau (67 tópicos) |   Serafim (70 tópicos) |   e5 (75 tópicos) |
|:---------------------------------|-------------------------:|-----------------------:|------------------:|
| Administração Pública            |                       26 |                     28 |                28 |
| Direitos Humanos e Minorias      |                       23 |                     28 |                27 |
| Indústria, Comércio e Serviços   |                       22 |                     22 |                25 |
| Finanças Públicas e Orçamento    |                       19 |                     20 |                23 |
| Direito Penal e Processual Penal |                        9 |                      7 |                11 |
| Homenagens e Datas Comemorativas |                        5 |                      5 |                 5 |
| Política, Partidos e Eleições    |                        5 |                      5 |                 6 |

Correlação de Spearman da fragmentação entre os modelos (todos os temas):

| index     |   BERTimbau |   Serafim |    e5 |
|:----------|------------:|----------:|------:|
| BERTimbau |       1     |     0.855 | 0.92  |
| Serafim   |       0.855 |     1     | 0.906 |
| e5        |       0.92  |     0.906 | 1     |

## 3. Pares de temas (razão sobre o acaso)

| tema_a                           | tema_b                                      |   lift_cedi |   BERTimbau |   Serafim |    e5 |
|:---------------------------------|:--------------------------------------------|------------:|------------:|----------:|------:|
| Direito Penal e Processual Penal | Direito e Justiça                           |        1.4  |        2.45 |      3.61 |  2.85 |
| Direito Penal e Processual Penal | Direitos Humanos e Minorias                 |        1.24 |        1.73 |      2.38 |  1.59 |
| Saúde                            | Trabalho e Emprego                          |        1.09 |        1.84 |      0.96 |  1.33 |
| Economia                         | Relações Internacionais e Comércio Exterior |        4.25 |        1.8  |      1.46 |  1.75 |
| Estrutura Fundiária              | Agricultura, Pecuária, Pesca e Extrativismo |       11.05 |        3.77 |      2.67 | 12.85 |
| Economia                         | Turismo                                     |        2.12 |        1.15 |      1.38 |  1.64 |
| Arte, Cultura e Religião         | Turismo                                     |        6.82 |        3.29 |      2.74 |  5.04 |

Pares com pelo menos 300 proposições em cada tema: 378.

Fração dos pares em que dois modelos divergem do CEDI no mesmo sentido (ambos aproximam ou ambos separam):

|   BERTimbau x Serafim |   BERTimbau x e5 |   Serafim x e5 |
|----------------------:|-----------------:|---------------:|
|                 0.854 |            0.799 |          0.759 |

Correlação (Pearson, log da razão) entre os modelos:

| index     |   BERTimbau |   Serafim |    e5 |
|:----------|------------:|----------:|------:|
| BERTimbau |       1     |     0.842 | 0.824 |
| Serafim   |       0.842 |     1     | 0.734 |
| e5        |       0.824 |     0.734 | 1     |

## 4. Assinaturas partidárias (versão com todas as proposições)

|   legislatura | modelo    |   partidos |   partidos_com_assinatura |   assinaturas_partidarias |
|--------------:|:----------|-----------:|--------------------------:|--------------------------:|
|            56 | BERTimbau |         24 |                        11 |                        20 |
|            56 | Serafim   |         24 |                         9 |                        16 |
|            56 | e5        |         24 |                        11 |                        20 |
|            57 | BERTimbau |         20 |                         5 |                        20 |
|            57 | Serafim   |         20 |                         6 |                        19 |
|            57 | e5        |         20 |                         6 |                        18 |

Assinaturas partidárias do BERTimbau que reaparecem no outro modelo (mesmo partido, em um tópico que recebe pelo menos 20% das proposições do tópico do BERTimbau):

|   legislatura | modelo   |   assinaturas_bertimbau |   reaparecem_partidarias |   reaparecem_qualquer |
|--------------:|:---------|------------------------:|-------------------------:|----------------------:|
|            56 | Serafim  |                      20 |                       13 |                    14 |
|            56 | e5       |                      20 |                       15 |                    16 |
|            57 | Serafim  |                      20 |                       16 |                    16 |
|            57 | e5       |                      20 |                       13 |                    13 |

### 56ª legislatura, BERTimbau

| partido      | rotulo                                                                                                                                           |
|:-------------|:-------------------------------------------------------------------------------------------------------------------------------------------------|
| MDB          | Títulos de capital nacional                                                                                                                      |
| NOVO         | CLT e relações de trabalho; Normas para os entes federativos                                                                                     |
| PCDOB        | COVID e calamidade pública                                                                                                                       |
| PL           | Código Penal: crimes e penas                                                                                                                     |
| PP           | Energia elétrica; Denominação de rodovias                                                                                                        |
| PSD          | Micro e pequenas empresas                                                                                                                        |
| PSL          | Código Penal: crimes e penas; Armas de fogo; Execução penal; Código de Processo Penal; Ambiente digital e crianças; Segurança pública e polícias |
| PSOL         | COVID e calamidade pública; Prevenção à violência                                                                                                |
| PT           | COVID e calamidade pública; CLT e relações de trabalho                                                                                           |
| REPUBLICANOS | Defesa do consumidor                                                                                                                             |
| UNIÃO        | Patrimônio cultural imaterial                                                                                                                    |

### 56ª legislatura, Serafim

| partido      | rotulo                                                                                                                                                                                                            |
|:-------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MDB          | capital, título capital, título, confere                                                                                                                                                                          |
| PL           | penal, código penal, código, crime                                                                                                                                                                                |
| PP           | denomina, rodovia, viaduto, trecho                                                                                                                                                                                |
| PSD          | complementar, tributário, microempreendedor, mei                                                                                                                                                                  |
| PSL          | penal, código penal, código, crime; fogo, armas, arma, arma fogo; militares, segurança pública, segurança, cargos; código penal, penal, código, crime                                                             |
| PSOL         | covid, coronavírus, pandemia, emergência saúde                                                                                                                                                                    |
| PT           | covid, coronavírus, pandemia, emergência saúde; calamidade, calamidade pública, estado, estado calamidade; benefício, social, prestação continuada, benefício prestação; crédito, benefícios, desconto, operações |
| REPUBLICANOS | idosa, pessoa idosa, idoso, pessoa; consumidor, defesa consumidor, código defesa, defesa                                                                                                                          |
| UNIÃO        | reconhece, cultural, patrimônio, manifestação                                                                                                                                                                     |

### 56ª legislatura, e5

| partido      | rotulo                                                                                                                                                                                                                                                             |
|:-------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| MDB          | capital, título capital, confere, título                                                                                                                                                                                                                           |
| NOVO         | trabalho, consolidação, consolidação trabalho, clt; eleitoral, eleições, partidos, partidos políticos                                                                                                                                                              |
| PCDOB        | covid, coronavírus, pandemia, pública                                                                                                                                                                                                                              |
| PL           | penal, código penal, código, crime                                                                                                                                                                                                                                 |
| PP           | denomina, rodovia, viaduto, trecho                                                                                                                                                                                                                                 |
| PSB          | covid, coronavírus, pandemia, pública                                                                                                                                                                                                                              |
| PSD          | pequeno, pequeno porte, complementar, mei                                                                                                                                                                                                                          |
| PSL          | penal, código penal, código, crime; fogo, armas, arma, arma fogo; código, código penal, penal, crime; execução penal, execução, penal, prisional; criminosas, organizações criminosas, criminosa, terrorismo; militares, bombeiros, bombeiros militares, segurança |
| PSOL         | covid, coronavírus, pandemia, pública                                                                                                                                                                                                                              |
| PT           | covid, coronavírus, pandemia, pública; trabalho, consolidação, consolidação trabalho, clt                                                                                                                                                                          |
| REPUBLICANOS | consumidor, defesa consumidor, código defesa, defesa; violência, mulheres, mulher, doméstica; idosa, pessoa idosa, pessoa, idoso                                                                                                                                   |

### 57ª legislatura, BERTimbau

| partido   | rotulo                                                                                                                                                                                                                            |
|:----------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| NOVO      | Finanças públicas e repasses                                                                                                                                                                                                      |
| PL        | Código Penal: crimes e penas; Armas de fogo; Segurança pública e polícias; Terrorismo e organizações criminosas; Execução penal; Código de Processo Penal; Terras, mineração e meio ambiente; Esporte; Licitações e administração |
| PODE      | Animais domésticos                                                                                                                                                                                                                |
| PSOL      | Desastres e defesa civil; Heróis e Heroínas da Pátria; Violência doméstica; CLT e relações de trabalho                                                                                                                            |
| PT        | Heróis e Heroínas da Pátria; Universidades e campi; Violência doméstica; CLT e relações de trabalho; Datas comemorativas                                                                                                          |

### 57ª legislatura, Serafim

| partido   | rotulo                                                                                                                                                                                                                                                                      |
|:----------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PCDOB     | piso salarial, piso, salarial, enfermagem                                                                                                                                                                                                                                   |
| PL        | penal, código penal, código, crime; fogo, armas, arma, arma fogo; militares, segurança pública, segurança, cargos; imóveis, imóvel, casa, programa casa                                                                                                                     |
| PODE      | animais, animal, tratos, maus tratos                                                                                                                                                                                                                                        |
| PSOL      | clima, mudança clima, climática, mudança; pátria, heróis, livro heróis, livro; ambiental, ambientais, meio ambiente, ambiente; violência, mulher, doméstica, violência doméstica                                                                                            |
| PT        | trabalho, consolidação, consolidação trabalho, clt; dia, conscientização, anualmente, dia dia; cultura, culturais, cultural, pronac; pátria, heróis, livro heróis, livro; universidade, autoriza poder, autoriza, campus; violência, mulher, doméstica, violência doméstica |
| UNIÃO     | animais, animal, tratos, maus tratos; penal, código penal, código, crime; transtorno, autista, espectro, espectro autista                                                                                                                                                   |

### 57ª legislatura, e5

| partido   | rotulo                                                                                                                                                                                                                                                                             |
|:----------|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PL        | fogo, armas, arma, arma fogo; penal, código penal, código, crime; militares, bombeiros, bombeiros militares, segurança; criminosas, organizações criminosas, criminosa, terrorismo; execução penal, execução, penal, prisional; código, código penal, penal, crime                 |
| PODE      | animais, animal, domésticos, animais domésticos                                                                                                                                                                                                                                    |
| PP        | capital, título capital, confere, título; rodovia, denomina, trecho, viaduto                                                                                                                                                                                                       |
| PSOL      | pátria, heróis, livro heróis, livro; condenadas, nomeação, crimes, contra                                                                                                                                                                                                          |
| PT        | violência, mulheres, mulher, doméstica; pátria, heróis, livro heróis, livro; universidade, campus, autoriza poder, autoriza; trabalho, consolidação, consolidação trabalho, clt; dia, conscientização, anualmente, dia dia; profissão, exercício, regulamenta, exercício profissão |
| UNIÃO     | animais, maus tratos, tratos, maus                                                                                                                                                                                                                                                 |
