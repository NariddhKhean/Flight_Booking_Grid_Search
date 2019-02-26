from oauth2client.service_account import ServiceAccountCredentials as Creds
from gspread import authorize

import requests
import json
import csv
import os

def poll_skyscanner_from_sessions(sessions, headers, creds_path, x, y, config):
    """Calls the SkyScanner API to request the cheapest return flights from
    Sydney International Airport to Wellington International Airport from a
    nested list of SkyScanner API sessions IDs.

    Args:
        sessions (list): Cryptographic keys representing the session IDs for
        the SkyScanner API.
        headers (dict): The key and content type needed for interacting with
        the SkyScanner API.
        creds_path (path): Absolute path to credentials.json.
        x (int): x-coordinate in the Google Sheet to start updating from.
        y (int): y-coordinate in the Google Sheet to start updating from.
        config (dict): Loaded from config.json.

    Returns:
        A nested list representing the AUD value of the cheapest return
        flights for the corresponding days.

    """

    # Access Google Sheets
    scope  = ['https://spreadsheets.google.com/feeds',
              'https://www.googleapis.com/auth/drive']
    creds  = Creds.from_json_keyfile_name(creds_path, scope)
    client = authorize(creds)

    # Read Spreadsheet
    sheet = client.open(config['spreadsheet']).worksheet(config['worksheet'])

    for i_arr in range(len(sessions)):
        for i_dep in range(len(sessions[0])):

            # Create URLs
            get_url = 'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/uk2/v1.0/{}?sortType=price&sortOrder=asc&stops=0'.format(sessions[i_arr][i_dep])

            # Poll Session results
            with requests.get(get_url, headers=headers) as r:
                response = r.json()

            # Quote Age
            if i_arr == 0 and i_dep == 0:
                quote_age = response['Itineraries'][0]['PricingOptions'][0]['QuoteAgeInMinutes']
                print('\n---\n\nQuote Age: {}hrs {}mins'.format(quote_age//60, quote_age%60))

            # Data Extraction
            output_price = response['Itineraries'][0]['PricingOptions'][0]['Price']

            # DEBUGGING
            print('\nSession Key: "{}"'.format(response['SessionKey']))
            print('  {} to {}'.format(response['Query']['OutboundDate'], response['Query']['InboundDate']))
            print('  Best Price: ${}'.format(output_price))

            # Update Google Sheet
            sheet.update_cell(i_arr + y, i_dep + x, output_price)

if __name__ == '__main__':

    # Load config.json
    with open('config.json', 'r') as file:
        config = json.load(file)

    # Paths
    working_directory = os.path.join(os.path.expanduser('~'), 'Documents')
    sessions_csv_path = os.path.join(working_directory, 'sessions.csv')

    # Create Header with Key
    with open('credentials.json', 'r') as file:
        credentials = json.load(file)
    headers = {"X-RapidAPI-Key": credentials['X-RapidAPI-Key'],
               "Content-Type": "application/x-www-form-urlencoded"}

    # Read Sessions from sessions.csv
    sessions_csv_path = os.path.join(working_directory, 'sessions.csv')
    with open(sessions_csv_path, 'r', newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        sessions_read = [row for row in csv_reader]

    # Poll SkyScanner Sessions
    poll_skyscanner_from_sessions(sessions=sessions_read,
                                  headers=headers,
                                  creds_path=credentials['drive-creds'],
                                  x=1, y=1,
                                  config=config)