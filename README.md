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
│   └── extras/concentracao_autores.py
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
| 4. Avaliação BCubed | a fazer | tópicos e `temas_long` | | G4 |
| 5. RQ1 e RQ2 | a fazer | tópicos, datas e partidos | | G5 |

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
   uv run python src/fase2_texto_modelo.py --base data/processed/base_proposicoes_20261027.parquet --n-chars 500
   ```
   Com os PDFs já baixados, acrescente `--sem-download`.

### Fase 3: embeddings e clustering

6. **Gerar os embeddings na GPU** (uma vez por modelo; só textos únicos).
   ```powershell
   uv run python src/fase3_embeddings.py --base data/processed/base_fase2_20261029.parquet
   ```
7. **Rodar a grade do HDBSCAN** (só métricas intrínsecas; o `codTema` não é lido).
   ```powershell
   uv run python src/fase3_clustering.py grade --modelo bertimbau --base data/processed/base_fase2_20261029.parquet
   ```
8. **Ajustar a configuração escolhida** e gerar a leitura qualitativa dos tópicos.
   ```powershell
   uv run python src/fase3_clustering.py final --modelo bertimbau --base data/processed/base_fase2_20261029.parquet --nn 15 --mcs 50 --metodo leaf
   ```
   Troque `--nn`, `--mcs` e `--metodo` pela configuração escolhida na grade. Para o e5, rode só a configuração vencedora e uma variação.

### Extras

- `src/extras/concentracao_autores.py`: confere a produção dos autores com mais proposições por partido e ano.

## Arquivos em uso

| Artefato | Arquivo atual | Observação |
| --- | --- | --- |
| Base da Fase 1 | `data/processed/base_proposicoes_20261027.parquet` | 40.006 proposições |
| Temas oficiais (formato longo) | `data/processed/temas_long_20261027.parquet` | gabarito do BCubed |
| Base da Fase 2 | `data/processed/base_fase2_20261029.parquet` | trecho do inteiro teor com 500 caracteres |
| Base da Fase 2 (alternativa) | `data/processed/base_fase2_20261028.parquet` | trecho com 1.000 caracteres, para análise de sensibilidade |
| Anotação de desenvolvimento | `anotacoes/formulaicas_desenvolvimento.csv` | 300 ementas |
| Anotação de validação | `anotacoes/formulaicas_validacao.csv` | 100 ementas |

## Portões já aprovados

- **G1 (27/10/2026):** 40.006 proposições; cobertura de `codTema` de 99,9%; partido na data da proposição confirmado; concentração de autoria identificada (dois deputados somam 2.348 proposições).
- **G2 (28/10/2026):** critério de formulaicas com precisão e recall de 1,00 na amostra de validação; 493 formulaicas (1,23%), todas resolvidas (27 pela `ementaDetalhada`, 466 pelo inteiro teor); 38.945 textos únicos.

## Reprodutibilidade

- Data de corte: 30/09/2026. Data do download: sufixo `AAAAMMDD` de cada arquivo gerado.
- Seeds: `src/seed.py` define 130 como seed global. As amostras de anotação usaram 42 (desenvolvimento) e 7 (validação), e o UMAP da Fase 3 usa 42. Esses valores ficam registrados aqui e não devem mudar depois de usados.
- Versões das bibliotecas: `uv.lock`. Os embeddings guardam modelo, versões e dispositivo em `emb_<modelo>.json`.

## Convenções

- Nunca editar arquivos em `data/raw/`.
- Anotações humanas só em `anotacoes/`, com nome que diga o papel (desenvolvimento ou validação).
- Arquivos gerados levam o sufixo de data `AAAAMMDD`; ao atualizar uma etapa, atualize a tabela "Arquivos em uso".
- Versões superadas vão para `_arquivo_antigo/`, sem apagar.
