import pandas as pd


b = pd.read_parquet("data/processed/base_proposicoes_20261027.parquet")
b["ano"] = b["dataApresentacao"].dt.year


print(b["autor1_nome"].value_counts().head(10))
print(b[b["autor1_nome"].isin(["Amom Mandel", "Duda Ramos"])]
      .groupby(["autor1_nome", "autor1_partido", "ano"]).size())