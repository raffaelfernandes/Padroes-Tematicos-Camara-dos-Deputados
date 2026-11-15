"""
fase3_embeddings.py

Gera os embeddings dos textos únicos da Fase 2 na GPU e salva em .npy.
Roda uma vez por modelo; depois disso, todo o resto da Fase 3 usa os arquivos salvos.

Uso:
    uv run python src/fase3_embeddings.py --base data/processed/base_fase2_AAAAMMDD.parquet
    uv run python src/fase3_embeddings.py --base ... --modelos bertimbau        # só um modelo

Saídas em data/processed/embeddings:
    textos_unicos.parquet     id_texto_unico -> texto_modelo (a ordem das linhas = ordem dos vetores)
    emb_bertimbau.npy         (n_textos x 1024), normalizado (L2)
    emb_e5.npy                (n_textos x 1024), normalizado (L2)
    emb_<modelo>.json         metadados: tempo, dispositivo, % de textos truncados, versões
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from seed import SEED

MODELOS = {
    # nome: (repositório no Hugging Face, prefixo do texto)
    "bertimbau": ("neuralmind/bert-large-portuguese-cased", ""),
    # O e5 foi treinado com prefixos; "query: " é o indicado para tarefas simétricas como agrupamento.
    "e5": ("intfloat/multilingual-e5-large", "query: "),
    # Serafim 335M: o próprio BERTimbau Large ajustado para similaridade de frases (NLI + STS,
    # PT-PT e PT-BR). Comparar com o bertimbau isola o efeito desse ajuste. Sem prefixo.
    "serafim": ("PORTULAN/serafim-335m-portuguese-pt-sentence-encoder", ""),
    # Serafim 900M (base Albertina PT-PT). Opcional, mais lento.
    "serafim900": ("PORTULAN/serafim-900m-portuguese-pt-sentence-encoder", ""),
}


def cos_medio_aleatorio(emb: np.ndarray, n: int = 20000, seed: int = SEED) -> float:
    """Cosseno médio entre pares aleatórios de textos. Perto de 1 = espaço "achatado"
    (anisotrópico), em que tudo parece parecido com tudo e o HDBSCAN acha menos regiões densas."""
    rng = np.random.default_rng(seed)
    i, j = rng.integers(0, len(emb), n), rng.integers(0, len(emb), n)
    m = i != j
    return float((emb[i[m]] * emb[j[m]]).sum(1).mean())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True, type=Path)
    ap.add_argument("--saida", default="data/processed/embeddings", type=Path)
    ap.add_argument("--modelos", nargs="+", default=["bertimbau", "e5"], choices=list(MODELOS))
    ap.add_argument("--so-diagnostico", action="store_true",
                    help="não gera nada; só calcula o cosseno médio dos embeddings já salvos")
    ap.add_argument("--max-tokens", type=int, default=256,
                    help="textos maiores são truncados; o script informa quantos foram")
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--refazer", action="store_true")
    a = ap.parse_args()
    a.saida.mkdir(parents=True, exist_ok=True)

    if a.so_diagnostico:
        for nome in a.modelos:
            f = a.saida / f"emb_{nome}.npy"
            if f.exists():
                print(f"{nome:<11} cosseno médio entre pares aleatórios: {cos_medio_aleatorio(np.load(f)):.3f}")
            else:
                print(f"{nome:<11} (sem {f.name})")
        return

    import torch
    from sentence_transformers import SentenceTransformer

    if torch.cuda.is_available():
        device = "cuda"
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = "cpu"
        print("ATENÇÃO: CUDA não disponível, rodando em CPU (vai demorar bem mais). "
              "Confira a instalação do torch com suporte a CUDA.")

    base = pd.read_parquet(a.base)
    if "texto_embedding" not in base.columns:          # bases antigas da Fase 2
        base["texto_embedding"] = base["texto_modelo"]
    base = base[["id_texto_unico", "texto_modelo", "texto_embedding"]]
    u = (base.drop_duplicates("id_texto_unico")
             .sort_values("id_texto_unico")
             .reset_index(drop=True))
    if not (u["id_texto_unico"].to_numpy() == np.arange(len(u))).all():
        raise SystemExit("id_texto_unico não é sequencial (0..n-1). Rode a Fase 2 de novo.")
    u.to_parquet(a.saida / "textos_unicos.parquet", index=False)
    md5 = hashlib.md5("\x1e".join(u["texto_embedding"].fillna("")).encode("utf-8")).hexdigest()
    print(f"{len(u)} textos únicos (assinatura {md5[:8]})")

    for nome in a.modelos:
        destino = a.saida / f"emb_{nome}.npy"
        if destino.exists() and not a.refazer:
            meta_path = a.saida / f"emb_{nome}.json"
            antigo = json.loads(meta_path.read_text(encoding="utf-8")).get("md5_textos") if meta_path.exists() else None
            if antigo == md5:
                print(f"[{nome}] já existe para estes textos, pulando")
                continue
            raise SystemExit(f"[{nome}] os embeddings salvos foram gerados para outros textos "
                             f"(a base da Fase 2 mudou). Rode de novo com --refazer.")
        repo, prefixo = MODELOS[nome]
        print(f"\n[{nome}] carregando {repo}")
        modelo = SentenceTransformer(repo, device=device)
        modelo.max_seq_length = a.max_tokens
        if device == "cuda":
            modelo.half()

        textos = [prefixo + t for t in u["texto_embedding"].fillna("")]
        n_tok = np.array([len(x) for x in modelo.tokenizer(textos, add_special_tokens=True)["input_ids"]])
        trunc = float((n_tok > a.max_tokens).mean())
        print(f"[{nome}] tokens por texto: mediana {np.median(n_tok):.0f}, p99 {np.percentile(n_tok, 99):.0f}; "
              f"truncados: {trunc:.2%}")

        t0 = time.time()
        emb = modelo.encode(textos, batch_size=a.batch, show_progress_bar=True,
                            normalize_embeddings=True, convert_to_numpy=True)
        seg = time.time() - t0
        emb = emb.astype(np.float32)
        if not np.isfinite(emb).all():
            raise SystemExit(f"[{nome}] embeddings com NaN/inf. Rode de novo sem half() (edite o script).")
        np.save(destino, emb)
        cos = cos_medio_aleatorio(emb)
        print(f"[{nome}] cosseno médio entre pares aleatórios: {cos:.3f}")

        meta = {
            "modelo": repo, "prefixo": prefixo, "md5_textos": md5, "base": str(a.base), "n_textos": int(emb.shape[0]), "dim": int(emb.shape[1]),
            "max_tokens": a.max_tokens, "pct_truncados": round(trunc, 4),
            "mediana_tokens": float(np.median(n_tok)), "segundos": round(seg, 1),
            "dispositivo": torch.cuda.get_device_name(0) if device == "cuda" else "cpu",
            "fp16": device == "cuda", "torch": torch.__version__,
            "sentence_transformers": __import__("sentence_transformers").__version__,
            "data": time.strftime("%Y-%m-%d %H:%M"), "cos_medio_pares_aleatorios": round(cos, 4),
        }
        (a.saida / f"emb_{nome}.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[{nome}] {emb.shape} salvo em {destino} ({seg / 60:.1f} min)")

        del modelo
        if device == "cuda":
            torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
