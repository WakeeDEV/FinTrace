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

    # Determine the transaction type
    transaction_type = 'Egyéb'
    if 'Vàsàrlàs' in simplified_text:
        transaction_type = 'Vásárlás'
    elif 'Terhelés' in simplified_text:
        transaction_type = 'Terhelés'
    elif 'Jòvàìràs' in simplified_text:
        transaction_type = 'Jóváírás'

    amount_value = 0.0
    store_name = 'Ismeretlen partner'
    
    # Search for the transaction amount, which is the last one
    amount_match = re.search(r'(-?\d{1,3}(?:\.\d{3})*)\s*HUF', simplified_text, re.IGNORECASE)
    if amount_match:
        amount_value = abs(float(amount_match.group(1).replace('.', '').replace(',', '.')))
        
        # Extract the partner's name based on the transaction type
        store_match = re.search(r'HUF\s+(.+?)\s*STREND', simplified_text, re.IGNORECASE)
        if store_match:
            store_name = store_match.group(1).strip()

    return amount_value, store_name, transaction_type


def process_xml_content(xml_content, bank_sms_nr, store_categories, ignored_keywords):
    root = ET.fromstring(xml_content)
    data = []

    for sms in root.findall('sms'):
        # Check if the SMS is from the bank
        if sms.get('address') == bank_sms_nr: 
            body = sms.get('body')
            amount, store, transaction = get_sms_data(body)
            
            if amount and store and transaction != 'Egyéb':      
                # Check if the SMS contains ignored keywords
                if any(kw.lower() in store.lower() for kw in ignored_keywords):
                    # print(f"Ignoring transaction: {store_name}...")
                    continue  # Skip to the next SMS in the loop

                # Assign a category based on the store name
                category = get_category(transaction, store, store_categories)
                
                # Extract date from the 'date' attribute and convert it
                date_timestamp = int(sms.get('date')) / 1000
                date = pd.to_datetime(date_timestamp, unit='s')

                data.append([date.strftime('%Y-%m-%d'), transaction, store, amount, category])

    # Create DataFrame and save to CSV
    df = pd.DataFrame(data, columns=['Dátum', 'Tranzakció', 'Bolt', 'Összeg', 'Kategória'])

    # If the DataFrame is empty, there is nothing to save
    if df.empty:
        print("No processable transactions in the file.")
        return

    # Create a month column from the date with YYYY-MM format
    df['Hónap'] = pd.to_datetime(df['Dátum']).dt.strftime('%Y-%m')

    # Group data by month
    grouped_by_month = df.groupby('Hónap')

    # Iterate through the months and save monthly data to separate CSV files
    for month, month_df in grouped_by_month:
        filename = rf'data\koltesek_{month}.csv'

        # Remove the unnecessary 'Hónap' column before saving
        month_df = month_df.drop(columns=['Hónap'])
        
        # Check if the file already exists
        if os.path.exists(filename):
            # If it exists, read its content
            existing_df = pd.read_csv(filename)
            
            # Find the missing rows
            # Create a unique key to prevent duplicates
            existing_df['unique_id'] = existing_df['Dátum'].astype(str) + existing_df['Bolt'].astype(str) + existing_df['Összeg'].astype(str)
            month_df['unique_id'] = month_df['Dátum'].astype(str) + month_df['Bolt'].astype(str) + month_df['Összeg'].astype(str)

            new_rows = month_df[~month_df['unique_id'].isin(existing_df['unique_id'])]
            
            # If there are new rows, append them to the existing file
            if not new_rows.empty:
                # Drop the helper column before saving
                new_rows = new_rows.drop(columns=['unique_id'])
                new_rows.to_csv(filename, mode='a', header=False, index=False, encoding='utf-8-sig')
                print(f"Added {len(new_rows)} new rows to {filename}.")
            else:
                print(f"No new rows in {filename}.")
                
        else:
            # If the file does not exist, simply create it
            month_df.to_csv(filename, mode='w', index=False, encoding='utf-8-sig')
            print(f"Data successfully saved: {filename}")