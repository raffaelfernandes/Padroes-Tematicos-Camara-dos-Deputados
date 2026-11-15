"""
seed.py

Sementes do TCC, num lugar só (15/11/2026).

Regra: tudo o que for executado a partir da troca do texto do embedding (versão sem fórmulas
legislativas) usa SEED = 130, inclusive o UMAP, as referências aleatórias, o bootstrap, as amostras
novas de anotação e as sementes do teste de estabilidade, que derivam dela. O que já foi executado e
não precisa ser refeito mantém a semente com que foi feito, registrada abaixo, para que ninguém mude
por engano e invalide uma anotação ou um resultado já usado.

Os scripts importam daqui; não defina sementes soltas nos scripts.
"""
import os
import random

import numpy as np

# ---------------------------------------------------------------------------------------------------
# Semente de tudo o que é (re)executado a partir de 15/11/2026
SEED = 130

# Teste de estabilidade: cinco execuções do UMAP, a principal (SEED) e as quatro seguintes
SEMENTES_ESTABILIDADE = [SEED + i for i in range(5)]          # 130, 131, 132, 133, 134

# ---------------------------------------------------------------------------------------------------
# Congeladas: amostras que já foram anotadas à mão. NÃO MUDAR (outra semente sorteia outras ementas e
# a anotação deixa de corresponder à amostra).
SEED_AMOSTRA_FORMULAICAS_DEV = 42      # fase1_investigacoes.py: 300 ementas de desenvolvimento do critério
SEED_AMOSTRA_FORMULAICAS_VAL = 7       # fase2_criterio_formulaicas.py: 100 ementas de validação
SEED_AMOSTRA_OUTLIERS = 130            # fase4_outliers.py amostrar: 100 outliers da análise de erros

# Executadas em 14/11/2026 e não reexecutadas: os baselines clássicos não dependem do texto do
# embedding (usam o texto_modelo), então seus modelos ficam como foram ajustados.
SEED_BASELINES = 42                    # extras/baselines_classicos.py: LDA, K-Means, SVD e UMAP do TF-IDF


def set_seed(seed: int = SEED) -> None:
    """Fixa as sementes globais (Python, NumPy e PyTorch). Os scripts passam a semente explicitamente
    a cada sorteio; esta função fica para quem rodar código interativo."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        torch.use_deterministic_algorithms(True, warn_only=True)
    except ImportError:
        pass
