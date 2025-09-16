from __future__ import print_function
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseDownload
import process_xml_content

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

# Itt kell megadni a Google Drive-mappa azonosítóját.
folder_id = '10PDoNkeLunRZtjrimYLQAEnXNDbZBUh2'

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
        process_xml_content.process_xml_content(xml_content)