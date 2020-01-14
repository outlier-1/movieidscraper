import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class GoogleAPI:
    SCOPES = {
        0: 'https://www.googleapis.com/auth/spreadsheets.readonly',
        1: 'https://www.googleapis.com/auth/spreadsheets',
    }

    def __init__(self, permission=1):
        self.credentials = None
        self.spreadsheetID = None
        self.service = None
        self.authenticated = False
        self.scopes = self.SCOPES[permission]

    def authenticate(self, credential_file='credentials.json'):
        # If valid credentials available, read it from token file
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.credentials = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credential_file, self.scopes)
                self.credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.credentials, token)
        self.authenticated = True

    def start_spreadsheet_service(self):
        self.service = build('sheets', 'v4', credentials=self.credentials)

    def create_spreadsheet(self, title='empty_spreadsheet'):
        if not self.authenticated:
            raise ConnectionError('Authentication Failed.')

        if self.service is None:
            self.start_spreadsheet_service()

        spreadsheet = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = self.service.spreadsheets().create(body=spreadsheet,
                                                         fields='spreadsheetId').execute()
        self.spreadsheetID = spreadsheet.get('spreadsheetId')
        return self.spreadsheetID

    def update_spreadsheet(self, spreadsheet_id, range, values):
        if not self.authenticated:
            raise ConnectionError('Authentication Failed.')

        if self.service is None:
            self.start_spreadsheet_service()

        body = {
            'values': values
        }
        result = self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range,
            valueInputOption='RAW', body=body).execute()
        return result.get('updatedCells')

    def append_spreadsheet(self, spreadsheet_id, range, values):
        if not self.authenticated:
            raise ConnectionError('Authentication Failed.')

        if self.service is None:
            self.start_spreadsheet_service()

        # How the input data should be interpreted.
        value_input_option = 'RAW'

        # How the input data should be inserted.
        insert_data_option = 'INSERT_ROWS'

        value_range_body = {
            "values": values
        }

        request = self.service.spreadsheets().values().append(spreadsheetId=spreadsheet_id,
                                                              range=range,
                                                              valueInputOption=value_input_option,
                                                              insertDataOption=insert_data_option,
                                                              body=value_range_body)
        response = request.execute()
        return response
