import re
import os.path
import pandas as pd
import xml.etree.ElementTree as ET

def process_xml_content(xml_content):
    root = ET.fromstring(xml_content)
    data = []

    for sms in root.findall('sms'):
        # Ellenőrizd, hogy az SMS a banktól jön-e
        # A telefonos bankok SMS-száma eltérhet, szükség esetén módosítsd!
        if sms.get('address') == '+36302030000': 
            body = sms.get('body')
            
            # Keresd a tranzakciós adatokat a szövegben
            # A minta most már a \n karaktert keresi
            amount_match = re.search(r'(-?\d{1,3}(?:\.\d{3})* HUF)', body)
            store_match = re.search(r'HUF\n(.+?)\n', body)
            
            if amount_match:
                # Az összeg és a bolt nevének kinyerése
                amount = float(amount_match.group(1).replace(' HUF', '').replace('.', ''))
                store_name = store_match.group(1).strip() if store_match else 'Ismeretlen bolt'
                
                # A dátum kinyerése az `date` attribútumból és konvertálása
                date_timestamp = int(sms.get('date')) / 1000
                date = pd.to_datetime(date_timestamp, unit='s')

                data.append([date.strftime('%Y-%m-%d'), store_name, amount])

    # DataFrame elkészítése és mentése CSV-be
    df = pd.DataFrame(data, columns=['Dátum', 'Bolt', 'Összeg'])
    
    if not os.path.exists('koltesek.csv'):
        df.to_csv('koltesek.csv', index=False, mode='w', encoding='utf-8-sig')
    else:
        df.to_csv('koltesek.csv', index=False, mode='a', header=False, encoding='utf-8-sig')
    
    print("Adatok sikeresen feldolgozva és elmentve.")