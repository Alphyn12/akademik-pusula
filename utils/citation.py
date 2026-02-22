def format_apa_7(authors_str: str, year: str, title: str, source: str, doi: str) -> str:
    """
    Format citation in approximate APA 7th edition style 
    based on available data.
    """
    if not authors_str or authors_str == "Bilinmiyor":
        authors_formatted = "Yazar Bilinmiyor"
    else:
        authors_list = [a.strip() for a in authors_str.split(',')]
        if len(authors_list) > 20:
            authors_formatted = ", ".join(authors_list[:19]) + ", ... " + authors_list[-1]
        elif len(authors_list) >= 3:
            # Simple "et al." approximation if list is too long, 
            # though APA 7 lists up to 20 authors.
            # We'll just list them out up to 5 for brevity in UI, then use vd. (et al.)
            if len(authors_list) > 5:
                authors_formatted = ", ".join(authors_list[:5]) + " vd."
            else:
                if len(authors_list) == 1:
                    authors_formatted = authors_list[0]
                else:
                    authors_formatted = ", ".join(authors_list[:-1]) + " & " + authors_list[-1]
        else:
            if len(authors_list) == 1:
                authors_formatted = authors_list[0]
            else:
                authors_formatted = " & ".join(authors_list)
                
    year_formatted = f"({year})" if str(year).isdigit() else "(Tarih Yok)"
    
    apa_text = f"{authors_formatted}. {year_formatted}. {title}. {source}."
    if doi and doi != "-":
        apa_text += f" https://doi.org/{doi}"
        
    return apa_text
