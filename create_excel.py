import pandas as pd
import glob

excel_filename = "havi_koltesek_osszesites.xlsx"
csv_pattern = r"data\koltesek_*.csv"

# A mappában lévő összes CSV fájl megkeresése
csv_files = glob.glob(csv_pattern)

if not csv_files:
    print("Hiba: Nincsenek CSV fájlok a mappában.")
    exit()

try:
    # Az összes CSV fájl beolvasása és egy DataFrame-be fűzése
    all_dfs = [pd.read_csv(f) for f in csv_files]
    df = pd.concat(all_dfs, ignore_index=True)

    # Dátum oszlop átalakítása és hónap oszlop létrehozása
    df['Dátum'] = pd.to_datetime(df['Dátum'])
    df['Hónap'] = df['Dátum'].dt.strftime('%Y-%m')

    # Pivot tábla létrehozása a kívánt formátumban
    monthly_summary = df.pivot_table(
        values='Összeg',
        index='Hónap',
        columns='Kategória',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # A kívánt oszlop sorrend meghatározása
    columns = list(monthly_summary.columns)
    columns_to_move = ['Egyéb', 'Jóváírás']
    
    for col in columns_to_move:
        if col in columns:
            columns.remove(col)
            columns.append(col)
            
    # Az oszlopok sorrendjének beállítása
    monthly_summary = monthly_summary[columns]

    # Excel tábla mentése és formázása
    with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
        # A DataFrame mentése az 'Összesítés' nevű lapra
        monthly_summary.to_excel(writer, sheet_name='Összesítés', index=False)

        # Az Excel munkafüzet és munkalap objektumok elérése
        workbook = writer.book
        worksheet = writer.sheets['Összesítés']
        
        # Pénznem formátum létrehozása
        currency_format = workbook.add_format({'num_format': '#,##0 "Ft"'})
        
        # A pénznem formátum alkalmazása a releváns oszlopokra
        for col_num, value in enumerate(monthly_summary.columns):
            if value != 'Hónap':
                worksheet.set_column(col_num, col_num, 15, currency_format)

    print(f"Sikeresen generált Excel tábla: {excel_filename}")
    
except Exception as e:
    print(f"Hiba történt a fájl generálása során: {e}")