import logging

def test_string():
    query = "Hilmi Kuşçu"
    tr_query1 = query.replace('i', 'İ').replace('ı', 'I').upper()
    print("Test 1:", tr_query1)

    query2 = "Cem Çetinarslan "
    tr_query2 = query2.strip().replace('i', 'İ').replace('ı', 'I').upper()
    print("Test 2:", tr_query2)

test_string()
