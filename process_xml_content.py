import re
import os.path
import pandas as pd
import xml.etree.ElementTree as ET


def get_category(transaction_type, store_name, mapping):
    if transaction_type == 'Jóváírás':
        return transaction_type
    else:
        for category, keywords in mapping.items():
            for keyword in keywords:
                if keyword.upper() in store_name.upper():
                    return category
        return "Egyéb"


def get_sms_data(sms_text:str):
    simplified_text = sms_text.replace('\n', ' ').replace("K&H mobilinfo * 1 BANKSZLA HUF", '').replace("VARGA TAMÅS", 'STREND').replace("Felhasznàlhatò összeg:", 'STREND').strip()

    # A tranzakció típusának meghatározása
    transaction_type = 'Egyéb'
    if 'Vàsàrlàs' in simplified_text:
        transaction_type = 'Vásárlás'
    elif 'Terhelés' in simplified_text:
        transaction_type = 'Terhelés'
    elif 'Jòvàìràs' in simplified_text:
        transaction_type = 'Jóváírás'

    amount_value = 0.0
    store_name = 'Ismeretlen partner'
    
    # Keresés a tranzakció összegére, ami a legutolsó
    amount_match = re.search(r'(-?\d{1,3}(?:\.\d{3})*)\s*HUF', simplified_text, re.IGNORECASE)
    if amount_match:
        amount_value = abs(float(amount_match.group(1).replace('.', '').replace(',', '.')))
        
        # A partner nevének kinyerése tranzakció típusa alapján
        store_match = re.search(r'HUF\s+(.+?)\s*STREND', simplified_text, re.IGNORECASE)
        if store_match:
            store_name = store_match.group(1).strip()

    return amount_value, store_name, transaction_type


def process_xml_content(xml_content, bank_sms_nr, store_categories, ignored_keywords):
    root = ET.fromstring(xml_content)
    data = []

    for sms in root.findall('sms'):
        # Ellenőrzés, hogy az SMS a banktól jön-e
        if sms.get('address') == bank_sms_nr: 
            body = sms.get('body')
            amount, store, transaction = get_sms_data(body)
            
            if amount and store and transaction != 'Egyéb':        
                # Ellenőrzés, hogy az SMS tartalmazza-e a figyelmen kívül hagyandó kulcsszavakat
                if any(kw.lower() in store.lower() for kw in ignored_keywords):
                    # print(f"Figyelmen kívül hagyva a tranzakció: {store_name}...")
                    continue  # Ugrás a következő SMS-re a ciklusban

                # A kategória hozzárendelése a bolt neve alapján
                category = get_category(transaction, store, store_categories)
                
                # A dátum kinyerése az `date` attribútumból és konvertálása
                date_timestamp = int(sms.get('date')) / 1000
                date = pd.to_datetime(date_timestamp, unit='s')

                data.append([date.strftime('%Y-%m-%d'), transaction, store, amount, category])

    # DataFrame elkészítése és mentése CSV-be
    df = pd.DataFrame(data, columns=['Dátum', 'Tranzakció', 'Bolt', 'Összeg', 'Kategória'])

    # Ha a DataFrame üres, nincs mit menteni
    if df.empty:
        print("Nincs feldolgozható tranzakció a fájlban.")
        return

    # Hónap oszlop létrehozása a dátumból a YYYY-MM formátummal
    df['Hónap'] = pd.to_datetime(df['Dátum']).dt.strftime('%Y-%m')

    # Adatok csoportosítása hónap szerint
    grouped_by_month = df.groupby('Hónap')

    # Iterálás a hónapok felett és a havi adatok mentése külön CSV-fájlokba
    for month, month_df in grouped_by_month:
        filename = rf'data\koltesek_{month}.csv'

        # A felesleges 'Hónap' oszlop eltávolítása a mentés előtt
        month_df = month_df.drop(columns=['Hónap'])
        
        # Ellenőrizd, hogy a fájl már létezik-e
        if os.path.exists(filename):
            # Ha létezik, olvasd be a tartalmát
            existing_df = pd.read_csv(filename)
            
            # Találja meg a hiányzó sorokat
            # A duplikációk elkerülése érdekében egy egyedi kulcsot hozunk létre
            existing_df['unique_id'] = existing_df['Dátum'].astype(str) + existing_df['Bolt'].astype(str) + existing_df['Összeg'].astype(str)
            month_df['unique_id'] = month_df['Dátum'].astype(str) + month_df['Bolt'].astype(str) + month_df['Összeg'].astype(str)

            new_rows = month_df[~month_df['unique_id'].isin(existing_df['unique_id'])]
            
            # Ha vannak új sorok, fűzd hozzá őket a meglévő fájlhoz
            if not new_rows.empty:
                # Törölje a segéd oszlopot a mentés előtt
                new_rows = new_rows.drop(columns=['unique_id'])
                new_rows.to_csv(filename, mode='a', header=False, index=False, encoding='utf-8-sig')
                print(f"Hozzáadva {len(new_rows)} új sor a(z) {filename} fájlhoz.")
            else:
                print(f"Nincs új sor a(z) {filename} fájlban.")
                
        else:
            # Ha a fájl nem létezik, egyszerűen hozd létre
            month_df.to_csv(filename, mode='w', index=False, encoding='utf-8-sig')
            print(f"Adatok sikeresen elmentve: {filename}")