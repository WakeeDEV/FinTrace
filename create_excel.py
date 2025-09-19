import pandas as pd
import os

excel_filename = "havi_koltesek_osszesites.xlsx"
csv_filename = "koltesek.csv"

# Ellenőrzés, hogy a CSV fájl létezik-e
if not os.path.exists(csv_filename):
    print(f"Hiba: a(z) {csv_filename} fájl nem található.")
    exit()

try:
    # 1. A CSV fájl beolvasása
    df = pd.read_csv(csv_filename)

    # 2. A 'Dátum' oszlop átalakítása és hónap oszlop létrehozása
    df['Dátum'] = pd.to_datetime(df['Dátum'])
    df['Hónap'] = df['Dátum'].dt.strftime('%Y-%m')

    # 3. Pivot tábla létrehozása a kívánt formátumban
    monthly_summary = df.pivot_table(
        values='Összeg',
        index='Hónap',
        columns='Kategória',
        aggfunc='sum',
        fill_value=0  # Üres értékek feltöltése 0-val
    ).reset_index()

    # 4. Excel tábla mentése
    monthly_summary.to_excel(excel_filename, index=False, engine='openpyxl')

    print(f"Sikeresen generált Excel tábla: {excel_filename}")
    
except Exception as e:
    print(f"Hiba történt a fájl generálása során: {e}")