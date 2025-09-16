Expense Tracker - SMS-based Expenditure Monitoring
A personalized Python script designed to automatically track monthly expenditures by processing bank transaction SMS notifications. This system automates the collection and categorization of transactions, saving them into a clean CSV file that can be easily imported into spreadsheet programs like Google Sheets for further analysis.

Features
Automated Data Collection: The script works with SMS backups stored in Google Drive, which can be automatically synced from your phone.
Intelligent Data Extraction: It uses regular expressions (regex) to extract key transaction data (date, amount, store name) from the text of the SMS messages.
Data Structuring: It transforms raw data into a structured CSV file, providing a perfect foundation for detailed analysis and visualization.
Scalable and Customizable: The script can be easily extended to support new SMS formats and transaction categories.

Installation
To run this project, you need the following Python libraries:

Bash
pip install pandas google-api-python-client google-auth-oauthlib

Usage
Google Cloud Platform Setup:
Create a new project in the Google Cloud Console.
Enable the Google Drive API.
Create "OAuth client ID" credentials for a "Desktop app" and download the credentials.json file, placing it in the same folder as your script.
Add your Google account to the "Test users" list on the OAuth consent screen.

Provide the Folder ID:
Create a folder on your Google Drive for the SMS backups and copy its unique ID from the URL.
Replace the value of the folder_id variable in your main.py file with this ID.

Run the Script:
Execute the script from your terminal: python main.py
The first time you run it, a browser window will open to request your permission to access your Google Drive.
After the script runs, a koltesek.csv file will be created in the root directory, containing your processed transaction data.

Example SMS Processing
The script is configured to process SMS messages with the following format (you may need to adjust the regex for your specific bank's messages):

XML

<sms protocol="0" address="+36302030000" date="1682141915110" type="1" subject="null" body="K&amp;H&#10;Hitelkàrtya&#10;Vàsàrlàs&#10;23/04/22 07:38&#10;3.609 HUF&#10;FAMILY SHOP GYOR HU&#10;VARGA TAMÁS&#10;Egyenleg: 212.825">
</sms>
The script extracts the store name (e.g., FAMILY SHOP GYOR HU) from the line following the amount.

Project Status and Future Plans
In Progress: Automatic categorization of transactions (e.g., mapping "FAMILY SHOP" to "Groceries").

Planned Features: Integrating data visualization directly into the script (e.g., generating charts to show spending trends).

License
This project is open-source and available under the MIT License.
