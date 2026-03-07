import pandas as pd
import timeit
import json

df = pd.DataFrame({
    "Başlık": ["Title " + str(i) for i in range(15)],
    "Özet": ["Abstract " + str(i) * 100 for i in range(15)],
    "Other": ["Someval" for i in range(15)]
})
df.index = [i * 2 for i in range(15)] # Custom index

def method_iterrows():
    items_to_rank = []
    for idx, row in df.iterrows():
        items_to_rank.append({
            "id": str(idx),
            "title": str(row.get("Başlık", "")),
            "abstract": str(row.get("Özet", ""))[:500]
        })
    return json.dumps(items_to_rank, ensure_ascii=False)

def method_todict_index():
    items_to_rank = []
    for idx, row in df.to_dict("index").items():
        items_to_rank.append({
            "id": str(idx),
            "title": str(row.get("Başlık", "")),
            "abstract": str(row.get("Özet", ""))[:500]
        })
    return json.dumps(items_to_rank, ensure_ascii=False)

print("iterrows:", timeit.timeit(method_iterrows, number=10000))
print("to_dict('index'):", timeit.timeit(method_todict_index, number=10000))

def method_todict_records():
    items_to_rank = []
    # to_dict('records') loses index, so we zip with index
    for idx, row in zip(df.index, df.to_dict("records")):
        items_to_rank.append({
            "id": str(idx),
            "title": str(row.get("Başlık", "")),
            "abstract": str(row.get("Özet", ""))[:500]
        })
    return json.dumps(items_to_rank, ensure_ascii=False)

def method_itertuples():
    items_to_rank = []
    for row in df.itertuples():
        # itertuples names attributes like row.Başlık, but row.get won't work.
        # getattr might be unsafe if column names have spaces or invalid python identifiers.
        pass

print("to_dict('records'):", timeit.timeit(method_todict_records, number=10000))

def method_zip_columns():
    items_to_rank = []
    # Using zip on columns directly avoids creating dictionaries entirely
    for idx, title, abstract in zip(df.index, df["Başlık"], df["Özet"]):
        items_to_rank.append({
            "id": str(idx),
            "title": str(title) if pd.notna(title) else "",
            "abstract": str(abstract)[:500] if pd.notna(abstract) else ""
        })
    return json.dumps(items_to_rank, ensure_ascii=False)

print("zip_columns:", timeit.timeit(method_zip_columns, number=10000))
