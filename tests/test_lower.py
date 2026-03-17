import logging

def test():
    q = "Hilmi Kuşçu"
    yazar = "HİLMİ KUŞÇU"
    
    q_lower = q.lower()
    yazar_lower = yazar.lower()
    
    print(f"q_lower: {q_lower!r}")
    print(f"yazar_lower: {yazar_lower!r}")
    
    print(f"Match standard python lower: {q_lower in yazar_lower}")
    
    # Custom lower
    def tr_lower(text):
        return text.replace('İ', 'i').replace('I', 'ı').lower()
        
    print(f"Match custom tr_lower: {tr_lower(q) in tr_lower(yazar)}")

test()
