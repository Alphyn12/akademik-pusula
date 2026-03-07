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

def method_todict_records():
    items_to_rank = []
    # Using zip with to_dict('records') handles missing columns gracefully with row.get()
    for idx, row in zip(df.index, df.to_dict("records")):
        items_to_rank.append({
            "id": str(idx),
            "title": str(row.get("Başlık", "")),
            "abstract": str(row.get("Özet", ""))[:500]
        })
    return json.dumps(items_to_rank, ensure_ascii=False)

# What if columns are missing?
df_missing = df.drop(columns=["Özet"])

def method_todict_records_missing():
    items_to_rank = []
    # Using zip with to_dict('records') handles missing columns gracefully with row.get()
    for idx, row in zip(df_missing.index, df_missing.to_dict("records")):
        items_to_rank.append({
            "id": str(idx),
            "title": str(row.get("Başlık", "")),
            "abstract": str(row.get("Özet", ""))[:500]
        })
    return json.dumps(items_to_rank, ensure_ascii=False)

print("df with columns:")
print("iterrows:", timeit.timeit(method_iterrows, number=10000))
print("to_dict('records'):", timeit.timeit(method_todict_records, number=10000))

print("\ndf missing 'Özet':")
print("to_dict('records'):", timeit.timeit(method_todict_records_missing, number=10000))
