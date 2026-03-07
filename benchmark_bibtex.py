import time
import pandas as pd
from utils.export import generate_bibtex

def benchmark():
    # Create dummy dataframe
    data = []
    for i in range(100000):
        data.append({
            "Yazarlar": f"Author {i}, Coauthor {i}",
            "Yıl": str(2000 + (i % 24)),
            "Başlık": f"Title of paper {i} {{with braces}}",
            "Kaynak": f"Journal {i}",
            "DOI": f"10.1234/doi_{i}",
            "Link": f"http://example.com/{i}",
            "Özet": f"Abstract for {i}"
        })
    df = pd.DataFrame(data)

    start = time.perf_counter()
    res = generate_bibtex(df)
    end = time.perf_counter()

    print(f"Time taken for 100000 rows: {end - start:.4f} seconds")

if __name__ == '__main__':
    benchmark()
