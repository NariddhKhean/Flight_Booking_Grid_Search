import datetime
import requests
import json
import csv
import os

def create_skyscanner_sessions(departure_start_date, departure_count,
                               arrival_start_date, arrival_count,
                               headers, config):
    """Generates a nested list of crytographic session IDs from the SkyScanner
    API, based on a given range of departure and arrival dates.

    Args:
        departure_start_date (datetime.date): The starting date of the range
        of dates to query, for the departure flights.
        departure_count (int): The number of days in the range of dates to
        query, for the departure flights.
        arrival_start_date (datetime.date): The starting date of the range
        of dates to query, for the arrival flights.
        arrival_count (int): The number of days in the range of dates to
        query, for the arrival flights.
        headers (dict): The key and content type needed for interacting with
        the SkyScanner API.
        config (dict): Loaded from config.json.

    Returns:
        A nested list of cryptographic keys representing the session IDs for
        the SkyScanner API.

    """

    # Define Date Ranges
    departure_dates = [departure_start_date+(i*datetime.timedelta(days=1))
                       for i in range(departure_count)]
    arrival_dates   = [arrival_start_date+(i*datetime.timedelta(days=1))
                       for i in range(arrival_count)]

    # Create Output Sessions
    output_sessions = []

    for i_arv, date_arr in list(enumerate(arrival_dates)):
        output_sessions.append([])
        for date_dep in departure_dates:

            # Session Parameters
            url    = 'https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/pricing/v1.0'
            params = {
                'country': config['country'],
                'currency': config['currency'],
                'locale': config['locale'],
                'originPlace': config['originPlace'],
                'destinationPlace': config['destinationPlace'],
                'adults': config['adults'],
                'cabinClass': config['cabinClass'],
                'outboundDate': date_dep.isoformat(),
                'inboundDate': date_arr.isoformat(),
            }
            # Create Sessions and Extract IDs
            with requests.post(url, data=params, headers=headers) as r:
                session_id = r.headers['Location'].split('/')[-1]
                output_sessions[i_arv].append(session_id)

            print('\nCreated Session ID for {} to {}.\n  "{}"'
                  .format(date_dep, date_arr, session_id))

    return output_sessions

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

    # Create SkyScanner Sessions
    departure_start_date = datetime.date(year=config['dep-year'],
                                         month=config['dep-month'],
                                         day=config['dep-day'])
    arrival_start_date   = datetime.date(year=config['arr-year'],
                                         month=config['arr-month'],
                                         day=config['arr-day'])
    sessions_write = create_skyscanner_sessions(
        departure_start_date=departure_start_date,
        departure_count=config['dep-count'],
        arrival_start_date=arrival_start_date,
        arrival_count=config['arr-count'],
        headers=headers,
        config=config)

    # Write Sessions to sessions.csv
    with open(sessions_csv_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(sessions_write)