import pandas as pd
import glob

excel_filename = "monthly_spending_summary.xlsx"
csv_pattern = r"data\koltesek_*.csv"

# Find all CSV files in the specified folder
csv_files = glob.glob(csv_pattern)

if not csv_files:
    print("Error: No CSV files found in the folder.")
    exit()

try:
    # Read all CSV files and concatenate them into a single DataFrame
    all_dfs = [pd.read_csv(f) for f in csv_files]
    df = pd.concat(all_dfs, ignore_index=True)

    # Convert 'Dátum' to datetime and create a 'Hónap' (Month) column
    df['Dátum'] = pd.to_datetime(df['Dátum'])
    df['Hónap'] = df['Dátum'].dt.strftime('%Y-%m')

    # Create a pivot table in the desired format
    monthly_summary = df.pivot_table(
        values='Összeg',
        index='Hónap',
        columns='Kategória',
        aggfunc='sum',
        fill_value=0
    ).reset_index()

    # Define the desired column order
    # Move the 'Egyéb' and 'Jóváírás' columns to the end
    columns = list(monthly_summary.columns)
    columns_to_move = ['Egyéb', 'Jóváírás']
    
    for col in columns_to_move:
        if col in columns:
            columns.remove(col)
            columns.append(col)
            
    # Set the new column order
    monthly_summary = monthly_summary[columns]

    # Save and format the Excel file
    with pd.ExcelWriter(excel_filename, engine='xlsxwriter') as writer:
        # Save the DataFrame to a sheet named 'Summary'
        monthly_summary.to_excel(writer, sheet_name='Summary', index=False)

        # Get the workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Summary']
        
        # Create a currency format
        currency_format = workbook.add_format({'num_format': '#,##0 "Ft"'})
        
        # Apply the currency format to the relevant columns
        for col_num, value in enumerate(monthly_summary.columns):
            if value != 'Hónap':
                worksheet.set_column(col_num, col_num, 15, currency_format)

    print(f"Successfully generated Excel table: {excel_filename}")
    
except Exception as e:
    print(f"An error occurred during file generation: {e}")