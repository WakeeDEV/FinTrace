import os
import json
import io
import re
import pandas as pd
import xml.etree.ElementTree as ET
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

import process_xml_content

# Ellenőrizd, hogy létezik-e a konfigurációs fájl
if not os.path.exists('config.json'):
    print("Hiba: a config.json fájl nem található.")
    exit()

# A konfigurációs fájl beolvasása
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# A beállítások lekérése a JSON fájlból
folder_id = config['google_drive_folder_id']
bank_sms_number = config['bank_sms_number']

# Ha a 'token.json' fájl már létezik, az engedélyek automatikusan betöltődnek.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('drive', 'v3', credentials=creds)

results = service.files().list(
    q=f"'{folder_id}' in parents and mimeType='text/xml'",
    fields="nextPageToken, files(id, name)").execute()
items = results.get('files', [])

if not items:
    print('Nincsenek fájlok a mappában.')
else:
    for item in items:
        file_id = item['id']
        file_name = item['name']
        print(f"Feldolgozás alatt: {file_name}")

        # A fájl tartalmának letöltése
        request = service.files().get_media(fileId=file_id)
        file_stream = io.BytesIO()
        downloader = MediaIoBaseDownload(file_stream, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        file_stream.seek(0)
        xml_content = file_stream.read().decode('utf-8')
        
        # A letöltött tartalom feldolgozása
        process_xml_content.process_xml_content(xml_content, bank_sms_number)