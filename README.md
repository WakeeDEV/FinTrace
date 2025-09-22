K&H Bank Transaction Tracker

This Python script automatically processes bank SMS notifications by downloading them from Google Drive, then saves monthly, categorized spending data into CSV and Excel files. Its purpose is to provide a simple and transparent way to track personal finances.

Features
The script offers the following key features:
- Automatic Data Processing: It connects to your Google Drive to download and extract transaction data (amount, store name, transaction type) from bank SMS notifications.
- Categorization: It automatically categorizes transactions based on built-in keywords (e.g., Shopping, Fuel, Entertainment).
- Monthly Data Storage: Transactions are saved into separate CSV files for each month, preventing data from being overwritten.
- Duplicate Prevention: It only appends new, unprocessed transactions to existing monthly CSV files, ensuring clean data.
- Excel Summary: It generates a comprehensive Excel file with a monthly spending summary, categorized and formatted for easy analysis.

Prerequisites
To run the script, you'll need the following:

- Python 3.6 or a newer version
- A Google Drive folder containing your SMS archive files (in .xml format)
- The required Python libraries: pandas, openpyxl, XlsxWriter, google-api-python-client, google-auth-httplib2, google-auth-oauthlib

Installation
- Clone the repository to your local machine
- Install the necessary Python libraries:
    pip install -r requirements.txt
- Google Drive API Setup
    Go to the Google Cloud Console.
    Create a new project.
    Enable the Google Drive API for your project.
    Navigate to the "Credentials" section and click "Create Credentials" > "OAuth client ID".
    Select "Desktop app" as the application type.
    Click "Download JSON" and save the file as credentials.json in the same folder as your Python scripts.

Usage
- Place your credentials.json file in the same directory as the script.
- Create a config.json file in the same directory with your specific bank and Google Drive folder details. An example is provided below.

JSON
{
  "google_drive_folder_id": "YOUR_FOLDER_ID",
  "bank_sms_number": "+36302030000",
  "store_categories": {
    "Tankolás / Autó": ["OMV", "SHELL", "MOL", "TOTAL"],
    "Élelmiszer": ["SPAR", "LIDL", "ALDI"],
    "Rezsiköltség": ["EON", "DIGI", "VODAFONE"],
    "Utazás / Szórakozás": ["SIMPLEPAY", "JEGYHU", "CINEMACITY", "DUMASZINHAZ"],
    "Jóváírás": ["TRANSFER", "ATUTALAS"],
    "Egyéb": ["UNKNOWN", "ISMERETLEN"]
  },
  "ignored_keywords": [ "egyenleg", "felhasznalhato" ]
}

- Run the main script from your terminal:

The first time you run the script, a browser window will open to authorize access to your Google Drive. After successful authorization, a token.json file will be created. The script will use this file for all future runs.

The script will now automatically download and process the XML files from your Google Drive folder, generating the CSV and Excel summary files.

Contributing
Pull requests and bug reports are welcome. If you'd like to suggest an improvement or a new feature, feel free to open an issue or create a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for more details.