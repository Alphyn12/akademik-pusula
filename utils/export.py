import pandas as pd
from typing import List, Dict

def generate_bibtex(df: pd.DataFrame) -> str:
    """Generate a valid BibTeX string from a DataFrame of search results."""
    bibtex_entries = []
    
    for _, row in df.iterrows():
        # Clean up some data
        authors = row.get("Yazarlar", "Unknown")
        # Bibtex expects authors separated by ' and '
        bib_authors = authors.replace(", ", " and ")
        
        year = str(row.get("Yıl", ""))
        title = str(row.get("Başlık", "Unknown")).replace("{", "").replace("}", "")
        source = str(row.get("Kaynak", "Unknown"))
        doi = str(row.get("DOI", ""))
        url = str(row.get("Link", ""))
        abstract = str(row.get("Özet", ""))
        
        # Create a citation key
        first_author = authors.split(",")[0].split(" ")[0].lower() if authors else "unknown"
        clean_year = year if year.isdigit() else "nd"
        cite_key = f"{first_author}{clean_year}"
        
        # Clean special chars from key
        cite_key = "".join(c for c in cite_key if c.isalnum())
        
        entry = [
            f"@article{{{cite_key},",
            f"  title={{ {title} }},",
            f"  author={{ {bib_authors} }},",
            f"  journal={{ {source} }},"
        ]
        
        if year.isdigit():
            entry.append(f"  year={{ {year} }},")
        if doi and doi != "-":
            entry.append(f"  doi={{ {doi} }},")
        if url and url != "-":
            entry.append(f"  url={{ {url} }},")
        if abstract and abstract != "Özet bulunamadı.":
            # Just a small snippet if it's too long, or the whole thing
            entry.append(f"  abstract={{ {abstract} }},")
            
        entry.append("}")
        bibtex_entries.append("\n".join(entry))
        
    return "\n\n".join(bibtex_entries)
