import re
import os.path
import pandas as pd
import xml.etree.ElementTree as ET

def get_category(store_name, mapping):
    for category, keywords in mapping.items():
        for keyword in keywords:
            if keyword.upper() in store_name.upper():
                return category
    return "Egyéb"

def process_xml_content(xml_content, bank_sms_nr, store_categories, ignored_keywords):
    root = ET.fromstring(xml_content)
    data = []

    for sms in root.findall('sms'):
        # Ellenőrzés, hogy az SMS a banktól jön-e
        if sms.get('address') == bank_sms_nr: 
            body = sms.get('body')
            
            # Tranzakciós adatok keresése a szövegben
            amount_match = re.search(r'(-?\d{1,3}(?:\.\d{3})* HUF)', body)
            store_match = re.search(r'HUF\n(.+?)\n', body)
            
            if amount_match:
                # Az összeg és a bolt nevének kinyerése
                amount = float(amount_match.group(1).replace(' HUF', '').replace('.', ''))
                store_name = store_match.group(1).strip() if store_match else 'Ismeretlen bolt'
                
                # Ellenőrzés, hogy az SMS tartalmazza-e a figyelmen kívül hagyandó kulcsszavakat
                if any(kw.lower() in store_name.lower() for kw in ignored_keywords):
                    print(f"Figyelmen kívül hagyva a tranzakció: {store_name}...")
                    continue  # Ugrás a következő SMS-re a ciklusban

                # A kategória hozzárendelése a bolt neve alapján
                category = get_category(store_name, store_categories)
                
                # A dátum kinyerése az `date` attribútumból és konvertálása
                date_timestamp = int(sms.get('date')) / 1000
                date = pd.to_datetime(date_timestamp, unit='s')

                data.append([date.strftime('%Y-%m-%d'), store_name, amount, category])

    # DataFrame elkészítése és mentése CSV-be
    df = pd.DataFrame(data, columns=['Dátum', 'Bolt', 'Összeg', 'Katekória'])
    
    if not os.path.exists('koltesek.csv'):
        df.to_csv('koltesek.csv', index=False, mode='w', encoding='utf-8-sig')
    else:
        df.to_csv('koltesek.csv', index=False, mode='a', header=False, encoding='utf-8-sig')
    
    print("Adatok sikeresen feldolgozva és elmentve.")