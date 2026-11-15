# Padrões temáticos em proposições da Câmara dos Deputados

Código do TCC de Raffael Fernandes (Ciência da Computação, UFPI): modelagem neural de tópicos (BERTopic) sobre as ementas de PL, PEC e PLP apresentados na Câmara dos Deputados entre 01/02/2019 (início da 56ª Legislatura) e 30/09/2026, com comparação contra a classificação temática oficial (`codTema`) pelo BCubed estendido.

Todos os comandos abaixo são executados **a partir desta pasta (`code/`)**, com `uv run python src/<script>.py`. Os caminhos padrão dos scripts (`data/raw`, `data/processed`) são relativos a ela.

## Estrutura

```
code/
├── README.md
├── pyproject.toml, uv.lock, .python-version
├── src/                              scripts, com prefixo da fase
│   ├── seed.py                       seed global (130)
│   ├── fase1_montar_base.py
│   ├── fase1_investigacoes.py
│   ├── fase2_criterio_formulaicas.py
│   ├── fase2_texto_modelo.py
│   ├── fase3_embeddings.py
│   ├── fase3_clustering.py
│   ├── fase4_avaliacao.py
│   ├── fase4_outliers.py
│   ├── texto_referencias.py          remove números e datas de referências legais do texto do embedding
│   └── extras/                       concentracao_autores.py, exportar_painel.py
├── anotacoes/                        gabaritos humanos (versionados; não regenerar)
├── data/                             fora do git, exceto os relatórios .md
│   ├── raw/                          arquivos baixados da Câmara (nunca editar)
│   └── processed/                    bases, embeddings, resultados e relatórios
├── notebooks/
├── outputs/figs, outputs/tables      figuras e tabelas da monografia
└── _arquivo_antigo/                  versões superadas (fora do git)
```

## Ambiente

Python 3.12 com [uv](https://docs.astral.sh/uv/). O `pyproject.toml` já aponta o `torch` para o índice com CUDA (cu128).

```powershell
uv sync
uv run python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

O teste deve imprimir `True` e o nome da GPU. Máquina usada: RTX 3050 Laptop (6 GB), i7-13650HX, 32 GB de RAM.

## Fluxo da pesquisa

| Fase | Script | Lê | Gera | Portão |
| --- | --- | --- | --- | --- |
| 1. Coleta e base | `fase1_montar_base.py` | arquivos anuais da Câmara (baixa sozinho) | `data/raw/*`, `base_proposicoes_*.parquet`, `temas_long_*`, `autores_long_*`, `relatorio_coleta_*.md` | G1 |
| 1. Investigações | `fase1_investigacoes.py` | base e temas | `investigacoes/investigacoes_g1.md`, `duplicatas_discordantes.csv`, amostra para anotar | G1 |
| 2. Critério de formulaicas | `fase2_criterio_formulaicas.py` | amostras anotadas em `anotacoes/` | métricas no terminal | G2 |
| 2. Texto do modelo | `fase2_texto_modelo.py` | base da Fase 1 e PDFs do inteiro teor (baixa sozinho) | `base_fase2_*.parquet`, `relatorio_fase2_*.md`, `inteiro_teor_amostra_*.csv` | G2 |
| 3. Embeddings | `fase3_embeddings.py` | `base_fase2_*.parquet` | `embeddings/textos_unicos.parquet`, `emb_<modelo>.npy` | G3 |
| 3. Clustering | `fase3_clustering.py` | embeddings e base da Fase 2 | `fase3/runs_log.csv`, `umap_*.npy`, modelo, `topicos_*.parquet`, `leitura_topicos_*.md` | G3 |
| 4. Outliers | `fase4_outliers.py` | base, `temas_long`, tópicos e embeddings | perfil e qualidade da reatribuição, amostra de anotação em `anotacoes/`, resumo da anotação | G4 |
| 4. Avaliação | `fase4_avaliacao.py` | base da Fase 2, `temas_long`, tópicos da Fase 3 | `fase4/relatorio_fase4.md`, `bcubed_resultados.csv`, fragmentação, convergência, dispersão, heatmap, `casos_*.md` | G4 |
| 5. RQ1 e RQ2 | `fase5_rqs.py` | base da Fase 2 e tópicos | `fase5/relatorio_fase5.md`, `rq1_*.csv`, `rq1_serie_mensal_*.csv`, `rq2_*_leg56/57.csv`, `rq2_concentracao.csv` | G5 |

## Comandos em ordem

### Fase 1: coleta e caracterização do corpus

1. **Baixar os arquivos e montar a base.** Baixa `proposicoes`, `proposicoesTemas` e `proposicoesAutores` de 2019 a 2026, filtra PL, PEC e PLP no recorte e junta por id. O arquivo do ano corrente é sempre baixado de novo, então a data do download é a data de corte efetiva.
   ```powershell
   uv run python src/fase1_montar_base.py
   uv run python src/fase1_montar_base.py --sem-download   # reaproveita data/raw
   ```
2. **Rodar as investigações do G1.** Picos de volume, ementas idênticas, partido da época, formulaicas, campo `relevancia`, apensadas e referências do BCubed.
   ```powershell
   uv run python src/fase1_investigacoes.py --base data/processed/base_proposicoes_20261027.parquet --temas data/processed/temas_long_20261027.parquet
   ```
   Ele também gera uma `amostra_formulaicas.csv` nova em `data/processed/investigacoes/`. A amostra já anotada fica protegida em `anotacoes/`.

### Fase 2: ementas formulaicas e texto do modelo

3. **Avaliar o critério na amostra de desenvolvimento** (300 ementas usadas para construir a regra).
   ```powershell
   uv run python src/fase2_criterio_formulaicas.py avaliar anotacoes/formulaicas_desenvolvimento.csv
   ```
4. **Validar o critério na amostra nova** (100 ementas não usadas no ajuste). Estes são os números que vão para a monografia.
   ```powershell
   uv run python src/fase2_criterio_formulaicas.py validar anotacoes/formulaicas_validacao.csv --gabarito anotacoes/formulaicas_validacao_gabarito_regra.csv --base data/processed/base_proposicoes_20261027.parquet
   ```
   Para gerar outra amostra de validação: `uv run python src/fase2_criterio_formulaicas.py amostrar --base ... --excluir anotacoes/formulaicas_desenvolvimento.csv anotacoes/formulaicas_validacao.csv`.
5. **Montar o texto que vai para o modelo.** Aplica o critério, usa a `ementaDetalhada` ou baixa o inteiro teor das formulaicas e cria `texto_modelo`, `fonte_texto` e `id_texto_unico`.
   ```powershell
   uv run python src/fase2_texto_modelo.py --base data/processed/base_proposicoes_20261027.parquet --sem-download
   ```
   Padrões: trecho de 500 caracteres do início da **justificação** do inteiro teor (`--parte articulado` usa o articulado sem as fórmulas legislativas) e ementas em caixa alta normalizadas para minúsculas. Também cria a coluna `texto_embedding`, igual ao `texto_modelo` mas sem números e datas de referências legais (`src/texto_referencias.py`); é esse texto que entra no modelo de embedding, e o `texto_modelo` fica legível para a leitura dos tópicos. Sem os PDFs baixados, retire `--sem-download`.

### Fase 3: embeddings e clustering

6. **Gerar os embeddings na GPU** (uma vez por modelo; só textos únicos).
   ```powershell
   uv run python src/fase3_embeddings.py --base data/processed/base_fase2_AAAAMMDD.parquet --refazer
   ```
   O script guarda uma assinatura dos textos. Se a base da Fase 2 mudar, ele se recusa a reaproveitar embeddings antigos e pede `--refazer`.
   Modelos disponíveis em `--modelos`: `bertimbau`, `e5`, `serafim` (Serafim 335M, o BERTimbau Large ajustado para similaridade de frases) e `serafim900`. O cosseno médio entre pares aleatórios fica no `emb_<modelo>.json`; para calcular só essa medida nos embeddings já salvos, use `--so-diagnostico`.
7. **Rodar a grade do HDBSCAN** (só métricas intrínsecas; o `codTema` não é lido). UMAP e HDBSCAN usam só as ementas substantivas; as formulaicas entram no passo 8.
   ```powershell
   uv run python src/fase3_clustering.py grade --modelo bertimbau --base data/processed/base_fase2_20261029.parquet
   ```
   Para testar só algumas combinações: `--nn 30 --mcs 50 100 --metodos eom --min-samples padrao 5 10`. Feche o `runs_log.csv` antes de rodar, porque o script acrescenta linhas nele.
8. **Ajustar a configuração escolhida** e gerar a leitura qualitativa dos tópicos.
   ```powershell
   uv run python src/fase3_clustering.py final --modelo bertimbau --base data/processed/base_fase2_20261029.parquet --nn 15 --mcs 50 --metodo leaf
   ```
   Troque `--nn`, `--mcs`, `--metodo` e `--min-samples` pela configuração escolhida na grade. O modelo é ajustado nas ementas substantivas. Os outliers são reatribuídos pelo voto dos 15 vizinhos mais próximos do núcleo do HDBSCAN no espaço original dos embeddings, com peso igual à similaridade (padrão desde 01/11; sufixo `_rk`; colunas `sim_centroide` e `consenso_knn` como medidas de confiança). Alternativas mantidas para comparação: `--reatribuicao original` (centroide do núcleo, sufixo `_ro`) e `--reatribuicao umap` (`reduce_outliers` no espaço do UMAP, sem sufixo). As formulaicas recebem o tópico pelo centroide e pelo c-TF-IDF (coluna `origem_topico` no parquet de saída).

### Fase 4: avaliação contra a classificação oficial

9. **Avaliar os dois modelos** (BCubed estendido, referências, tipos de proposição, apensadas, desvios e casos).
   ```powershell
   uv run python src/fase4_avaliacao.py --base data/processed/base_fase2_20261101.parquet --temas data/processed/temas_long_20261027.parquet --topicos data/processed/fase3/topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet data/processed/fase3/topicos_e5_nn30_mcs100_eom_ms10_rk.parquet data/processed/fase3/topicos_serafim_nn30_mcs100_eom_ms5_rk.parquet
   ```
   Leia primeiro `data/processed/fase4/relatorio_fase4.md` e depois os `casos_*.md` para escolher os estudos de caso. O `heatmap_*.html` abre no navegador.
10. **Analisar os outliers.** `metricas` gera o perfil e a qualidade da reatribuição (concordância temática com o núcleo do tópico, por faixa de similaridade e contra um tópico aleatório). `amostrar` sorteia a amostra de análise de erros (semente 130) em `anotacoes/`, com o catálogo de tópicos. `resumir` lê a planilha anotada e calcula as proporções com intervalo de Wilson (e o kappa, se houver um segundo anotador).
   ```powershell
   uv run python src/fase4_outliers.py metricas --base data/processed/base_fase2_20261101.parquet --temas data/processed/temas_long_20261027.parquet --topicos data/processed/fase3/topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet
   uv run python src/fase4_outliers.py resumir --anotada anotacoes/outliers_analise_erros.csv
   ```
   Não rode `amostrar` de novo: a amostra já foi anotada.
   Nichos dentro dos outliers (UMAP e HDBSCAN ajustados só nas proposições fora do núcleo, com tamanho mínimo 30) e comparação com o CEDI:
   ```powershell
   uv run python src/fase4_nichos.py --base data/processed/base_fase2_20261101.parquet --temas data/processed/temas_long_20261027.parquet --topicos data/processed/fase3/topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet
   ```
   Teste de robustez com mais de um tópico por proposição (BCubed estendido com sobreposição):
   ```powershell
   uv run python src/fase4_multitopico.py --base data/processed/base_fase2_20261101.parquet --temas data/processed/temas_long_20261027.parquet --topicos data/processed/fase3/topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet
   ``` Códigos e regras de decisão em `anotacoes/outliers_analise_erros_codigos.json` e no documento de cuidados da escrita.

### Fase 5: perguntas de pesquisa

11. **RQ1 (picos pré-eleitorais) e RQ2 (assinaturas partidárias)**, cada uma em três versões: todas as proposições, só o núcleo do HDBSCAN e sem os dois autores de produção em massa.
   ```powershell
   uv run python src/fase5_rqs.py --base data/processed/base_fase2_20261101.parquet --topicos data/processed/fase3/topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet
   ```
   Figuras da monografia (PDF e PNG em `outputs/figs/`; precisa de `uv add matplotlib` uma vez):
   ```powershell
   uv run python src/fase5_figuras.py
   ```
   RQ1: fração dos deputados ativos em abril a setembro de 2022 e 2026 que propuseram sobre cada tópico, contra os mesmos meses do ano anterior (Fisher com Benjamini-Hochberg) e contra a média dos anos sem eleição geral (sem 2020); 2024 contra 2023 como contraste municipal. RQ2: log-odds com prior de Dirichlet (Monroe, Colaresi e Quinn, 2008), partido contra o resto, por legislatura, com peso limitado por deputado (cada proposição pesa min(1, C/n), C = percentil 90 da produção por deputado). Assinatura partidária exige pelo menos 3 deputados no tópico e nenhum com mais de 50%.

### Extras

- `src/extras/concentracao_autores.py`: confere a produção dos autores com mais proposições por partido e ano.
- `src/extras/exportar_painel.py`: gera `data/processed/fase4/painel_dados.json`, com os dados do painel interativo dos resultados.
- `src/extras/robustez_modelos.py`: compara os três modelos no BCubed (tabela lado a lado, IC por bootstrap, teto das apensadas e variação com cinco sementes do UMAP). Saídas em `data/processed/fase4/robustez/`.
- `src/extras/comparar_modelos.py`: refaz com o Serafim e o e5 a fragmentação, os pares de temas e as assinaturas partidárias, e mede a concordância entre as partições (ARI, NMI e correspondência de tópicos). Saídas em `data/processed/fase4/comparacao_modelos/` (`relatorio.md` e CSVs). Rodar com `uv run python src/extras/comparar_modelos.py`.
- `src/extras/baselines_classicos.py`: LDA, TF-IDF com K-Means e TF-IDF no mesmo pipeline do BERTopic, avaliados como o modelo principal (BCubed, acaso com os mesmos tamanhos, apensadas, NPMI). Saídas em `data/processed/fase4/baselines/`.
- `src/extras/leis_citadas.py`: mede quanto os tópicos se organizam pela lei citada na ementa e o BCubed nas ementas com e sem lei citada. Saída em `data/processed/fase4/leis_citadas.md`.
- `src/extras/sensibilidade_rq2.py`: refaz as assinaturas partidárias com outros valores de a0 e do percentil do peso. Saída em `data/processed/fase5/sensibilidade_rq2.md`.
- `src/extras/figura_topicos_temas.py`: heatmap dos 15 maiores tópicos contra os temas oficiais (`outputs/figs/fig_topicos_temas.pdf`).
- `src/extras/inconsistencias_cedi.py`: sorteia pares (proposição, tema) isolados na vizinhança semântica e controles para anotação cega (`amostrar`) e resume a anotação (`resumir`). Planilha em `anotacoes/cedi_inconsistencias.csv`.
- `src/extras/avaliacao_humana.py`: teste de intrusão de ementas com tópicos do BERTimbau e do LDA misturados (`gerar`) e resumo das respostas (`resumir`). Caderno em `anotacoes/avaliacao_humana.xlsx`.

## Arquivos em uso

| Artefato | Arquivo atual | Observação |
| --- | --- | --- |
| Base da Fase 1 | `data/processed/base_proposicoes_20261027.parquet` | 40.006 proposições |
| Temas oficiais (formato longo) | `data/processed/temas_long_20261027.parquet` | gabarito do BCubed |
| Base da Fase 2 | `data/processed/base_fase2_20261101.parquet` | justificação do inteiro teor, caixa normalizada, `texto_embedding` sem números de lei |
| Base da Fase 2 (alternativa) | `data/processed/base_fase2_20261028.parquet` | trecho com 1.000 caracteres, para análise de sensibilidade |
| Tópicos (modelo principal) | `data/processed/fase3/topicos_bertimbau_nn30_mcs100_eom_ms10_rk.parquet` | BERTimbau Large, outliers reatribuídos pelos 15 vizinhos do núcleo no espaço original |
| Tópicos (versões anteriores) | `data/processed/fase3/topicos_bertimbau_nn30_mcs100_eom_ms10.parquet` e `..._ro.parquet` | reatribuição pelo `reduce_outliers` no UMAP e pelo centroide no espaço original, para comparação |
| Tópicos (comparação) | `data/processed/fase3/topicos_e5_nn30_mcs100_eom_ms10_rk.parquet`, `topicos_serafim_nn30_mcs100_eom_ms5_rk.parquet` | multilingual-e5-large e Serafim 335M |
| Anotação de desenvolvimento | `anotacoes/formulaicas_desenvolvimento.csv` | 300 ementas |
| Anotação de validação | `anotacoes/formulaicas_validacao.csv` | 100 ementas |
| Análise de erros dos outliers | `anotacoes/outliers_analise_erros.csv` (+ `_OCULTO.csv`, `_codigos.json`, `_catalogo_topicos.md`) | 100 outliers, semente 130 |

## Portões já aprovados

- **G1 (27/10/2026):** 40.006 proposições; cobertura de `codTema` de 99,9%; partido na data da proposição confirmado; concentração de autoria identificada (dois deputados somam 2.348 proposições).
- **G2 (28/10/2026):** critério de formulaicas com precisão e recall de 1,00 na amostra de validação; 493 formulaicas (1,23%), todas resolvidas (27 pela `ementaDetalhada`, 466 pelo inteiro teor); 38.942 textos únicos na versão com trecho de 500 caracteres (38.945 na de 1.000).
- **Embeddings (29/10/2026):** BERTimbau Large e multilingual-e5-large em fp16, cerca de 2,3 minutos cada; 0,35% e 0,09% dos textos truncados em 256 tokens.

## Histórico de decisões da Fase 3

- **Rodada 1 (29 e 30/10/2026)**, guardada em `data/processed/fase3/rodada1_20261030/` e `data/processed/embeddings/rodada1_20261029/`. Configuração escolhida: nn30, mcs100, eom, min_samples 10 (76 tópicos, 28,7% de outliers). Problemas encontrados na leitura: 128 das 132 ementas em caixa alta formaram um tópico só delas (66), e 432 das 466 formulaicas com texto do inteiro teor formaram dois tópicos de formato (48 e 49), porque o trecho do articulado é quase igual em todos os projetos.
- **Rodada 2 (30/10/2026):** com as correções, os tópicos de formato sumiram, mas a atribuição das formulaicas pelo centroide ficou fraca no BERTimbau (ex.: tópico de internet recebeu formulaicas sobre postos de combustível e cachês). Causa provável: a ementa formulaica na frente da justificação. A partir daqui, o texto dessas proposições é só a justificação.
- **Rodada 3 (30/10 a 01/11/2026):** com só a justificação no texto das formulaicas, o BERTimbau passou a atribuí-las bem; o e5 concentrou 48% delas num tópico genérico. Os dois modelos, e mais o e5, agruparam ementas pelo número da lei citada (ex.: Leis 12.865, 12.830, 12.852 e 12.850, sem relação de assunto, no mesmo tópico). Pureza da faixa numérica por tópico: 0,64 (BERTimbau) e 0,75 (e5), contra 0,10 com tópicos embaralhados. Correção: o embedding passa a usar o texto sem números e datas de referências legais.
- **Rodada 4 (01/11/2026), sem números de lei no embedding:** a pureza por faixa de número de lei caiu para 0,55 (BERTimbau) e 0,44 (e5). O e5 formou um tópico genérico de 4.290 proposições com ementas do tipo "Altera a Lei, para..." e jogou nele 73% das formulaicas. O BERTimbau não formou tópico desse tipo e espalhou as formulaicas (o tópico que mais recebeu ficou com 14%).
- **Portão G3 (01/11/2026): aprovado com o BERTimbau Large** (nn30, mcs100, eom, min_samples 10): 66 tópicos, 33,1% de outliers antes da reatribuição, maior tópico com 5,6%, NPMI 0,439, diversidade 0,84, nenhum tópico dominado por um único autor (grade refeita em 03/11 com os embeddings finais; a medição de 01/11, com os embeddings anteriores, tinha dado 64 tópicos, 31,2%, NPMI 0,429 e diversidade 0,844). O e5 (mesma configuração: 60 tópicos, 29,9%, NPMI 0,435, diversidade 0,791) fica como comparação. Pendências para a Fase 4: atribuição das formulaicas ainda imperfeita (tópicos 9 e 54 receberam muitas fora do assunto) e tópicos de "institui política ou programa" (1 e 45).
- **Fase 4 (01/11/2026), BERTimbau:** P 0,734 e R 0,086 contra 0,245 e 0,022 do aleatório com os mesmos tamanhos; 66,4% dos pares apensada e principal no mesmo tópico (acaso: 2,2%); pureza mediana dos tópicos de 85%. Precisão média por origem: núcleo do HDBSCAN 0,793, reatribuídos pelo reduce_outliers 0,622, formulaicas 0,547 (centroide) e 0,611 (c-TF-IDF). Decisão: formulaicas pelo c-TF-IDF na versão principal, com as duas estratégias relatadas.
- **Serafim (01/11/2026):** teste controlado com o Serafim 335M (BERTimbau Large ajustado para similaridade de frases). Critério fixado antes: reduzir os outliers em 5 pontos sem piorar o BCubed. O espaço ficou bem menos achatado (cosseno médio entre pares aleatórios de 0,352, contra 0,805 do BERTimbau e 0,909 do e5), mas a melhor configuração (mcs100, ms5) teve 72 tópicos, 34,4% de outliers e NPMI 0,380. Não passou; fica como comparação. Os três modelos ficam entre 30% e 35% de outliers, o que indica que a taxa vem do corpus.
- **Análise de erros dos outliers (01/11/2026):** 100 outliers anotados. Motivo: nicho 44%, híbrida 38%, borda 17%, ementa vaga 1%. Reatribuição: adequada 11%, parcial 48%, inadequada 41%. Concordância com o núcleo: 0,837 no núcleo, 0,641 nos reatribuídos, 0,248 com tópico aleatório; de 0,48 a 0,82 do quinto menos ao mais parecido. Quando o espaço original e o UMAP discordam, a escolha do espaço original foi preferida em 62% dos casos (26% quando concordam). Primeira decisão: reatribuir pelo centroide do núcleo no espaço original (sufixo `_ro`).
- **Reatribuição por vizinhos (01/11/2026):** a versão `_ro` melhorou o BCubed (P 0,734 para 0,745; R 0,086 para 0,089) e a concordância dos outliers com o núcleo (0,641 para 0,666), mas piorou a validação pelas apensadas (66,5% para 64,3% dos pares no mesmo tópico): quando apensada e principal eram ambas outliers, o centroide as separava mais que o UMAP (38,8% contra 56,4% juntas). O voto dos k vizinhos do núcleo no espaço original foi melhor que as duas versões em todas as medidas, de forma estável em k (com k = 15: P 0,747, R 0,098, concordância 0,685, apensadas 66,7%). Na amostra anotada, ele troca 33 das 41 reatribuições inadequadas e mantém 9 das 11 adequadas; quando vai para o "outro tópico próximo", o anotador tinha preferido esse tópico em 26 de 39 casos. Decisão final: `--reatribuicao knn` com k = 15 (sufixo `_rk`).
- **Correções (30/10/2026):** normalização da caixa alta; trecho da justificação no lugar do articulado; ajuste do modelo só nas ementas substantivas, com as formulaicas atribuídas pelo centroide mais próximo; tag do arquivo passa a incluir o `min_samples`.

## Reprodutibilidade

- Data de corte: 30/09/2026. Data do download: sufixo `AAAAMMDD` de cada arquivo gerado.
- Seeds: `src/seed.py` define 130 como seed global. As amostras de anotação das formulaicas usaram 42 (desenvolvimento) e 7 (validação), a análise de erros dos outliers usou 130, e o UMAP da Fase 3 usa 42. Esses valores ficam registrados aqui e não devem mudar depois de usados.
- Versões das bibliotecas: `uv.lock`. Os embeddings guardam modelo, versões e dispositivo em `emb_<modelo>.json`.

## Convenções

- Nunca editar arquivos em `data/raw/`.
- Anotações humanas só em `anotacoes/`, com nome que diga o papel (desenvolvimento ou validação).
- Arquivos gerados levam o sufixo de data `AAAAMMDD`; ao atualizar uma etapa, atualize a tabela "Arquivos em uso".
- Versões superadas vão para `_arquivo_antigo/`, sem apagar.
