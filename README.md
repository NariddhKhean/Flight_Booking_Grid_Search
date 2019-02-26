# Flight_Booking_Grid_Search

Query the _Skyscanner API_ for the cheapest return flights within a range of departure and arrival dates, and document results on a _Google Sheets_ spreadsheet for comparison.

### Background
I'm travelling to New Zealand for a conference in April, 2019. And being the dead-broke student that I am, I started to use websites like _[Google Flights](https://www.google.com/flights?hl=en)_ and _[Skyscanner](https://www.skyscanner.com.au/)_ to find a cheap ticket. The duration of the conference is set, but I don't mind arriving a little early or leave a little later, if it means I could save a bit of money.

The problem is, the aforementioned web apps only allow a search based on a single departure date combined with a single arrival date. So, if someone like me, who isn't too fussy about exact dates, wants to find the best price with a few days of leeway, the only option is to change the two dates manually and run the search over and over. Not only is this manual as all hell, but you'll also need to note down the prices for each combination of departure and arrival dates to compare them all at the end.

> _"There's gotta be a better way!"_
>
> \- Every daytime television commercial ever.

As it turns out, _Skyscanner_ has an API, which is free through _[Rapid API](https://rapidapi.com/)_.

## Getting Started

### Prerequisites

To use the _Skyscanner API_, you'll need a 'X-RapidAPI-Key', which is free if you sign up for an account with _Rapid API_. You can do this with your _GitHub_ account. After signing up, search for the _[Skyscanner API](https://rapidapi.com/skyscanner/api/skyscanner-flight-search)_, and have a play around with searching for flights in the browser. Refer to the [documentation](https://rapidapi.com/skyscanner/api/skyscanner-flight-search/details) for a step-by-step guide.

Copy your 'X-RapidAPI-Key' and save to a file called `credentials.json` in your project folder, as shown below:
```json
{
  "X-RapidAPI-Key": "<YOUR KEY GOES HERE>"
}
```
The next step is to create a _Google Sheet_ spreadsheet to display the table of prices. Create a new spreadsheet, name both the spreadsheet and the worksheet, and add those names to the `config.json` file:
```json
{
  "spreadsheet": "<SPREADSHEET NAME>",
  "worksheet": "<WORKSHEET NAME>",
}
```
To communicate with the spreadsheet, set up the _[Google Sheets API](https://developers.google.com/sheets/api)_ and _[Google Drive API](https://developers.google.com/drive/)_ with the following steps:

1. Navigate to your _[Google API Manager](https://console.developers.google.com/)_, and create a new project

2. Give the project a name, and click 'Create'

3. Go to the newly create project's dashboard, and click 'Enable APIs and Services'

4. Search for 'Google Sheets API', and enable it to the project

5. Do the same for the 'Google Drive API'

6. Click 'Create Credentials'

7. Select the following options for creating your credentials:

| Question | Selection |
| -------- | --------- |
| _Which API are you using?_ | Google Drive API |
| _Where will you be calling the API from?_ | Web server (e.g. node.js, Tomcat) |
| _What data will you be accessing?_ | Application data |
| _Are you planning to use this API with App Engine or Compute Engine?_ | No, I'm not using them |

8. Click 'What credentials do I need?'

9. Give the service account a name and set it's role as 'Project - Editor'

10. Click 'Continue', download the `<PROJECT ID>.json` file, and add it to the project folder

11. Add `<PROJECT ID>.json` to the `credentials.json` file
    ```json
    {
      "X-RapidAPI-Key": "<YOUR KEY GOES HERE>",
      "drive-creds": "<PROJECT ID>.json"
    }
    ```

12. Open the downloaded `<PROJECT ID>.json` file in a text editor (shown below), find the "client_email" key, can copy it's value to your clipboard
    ```json
    {
      "type": "service_account",
      "project_id": "<PROJECT ID>",
      "private_key_id": "<PRIVATE KEY ID>",
      "private_key": "<PRIVATE KEY>",
      "client_email": "<SERVICE ACCOUNT NAME>@<PROJECT ID>.iam.gserviceaccount.com",
      "client_id": "<CLIENT ID>",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "<CLIENT URL>"
    }
    ```

13. Go back to the _Google Sheets_ spreadsheet, and share the document to the copied email address

Finally, you need to install a couple of python packages to tie all these bits and pieces together: _oauth2client_ and _gspread_. You can do so using pip:
```
pip install oauth2client
```
```
pip install gspread
```
Alternatively, refer to their respective documentation (_[oauth2client](https://github.com/googleapis/oauth2client)_, _[gspread](https://github.com/burnash/gspread)_).

## Usage

### `config.json`
| Variable           | Description |
| ------------------ | -------- |
| `spreadsheet`      | Name of _Google Sheets_ spreadsheet. |
| `worksheet`        | Name of _Google Sheets_ worksheet. |
| `country`          | Your [market country](https://skyscanner.github.io/slate/#markets) (3-letter currency code). |
| `currency`         | The [currency](https://skyscanner.github.io/slate/#currencies) you want the prices in. |
| `locale`           | The [locale](https://skyscanner.github.io/slate/#locales) you want the results in. |
| `originPlace`      | Departure [airport code](https://skyscanner.github.io/slate/#places). |
| `destinationPlace` | Arrival [airport code](https://skyscanner.github.io/slate/#places). |
| `adults`           | Number of adult passengers (16+ years). Must be between 1 and 8. |
| `cabinClass`       | The cabin class. Can be “economy”, “premiumeconomy”, “business”, or “first”. |
| `dep-year`         | Year of first departure flight. |
| `dep-month`        | Month of first departure flight. |
| `dep-day`          | Day of first departure flight. |
| `dep-count`        | The number of days to search through for departure flight. |
| `arr-year`         | Year of first arrival flight. |
| `arr-month`        | Month of first arrival flight. |
| `arr-day`          | Day of first arrival flight. |
| `arr-count`        | The number of days to search through for arrival flight. |

### `create_sessions.py`
`create_sessions.py` generates a nested list of session IDs from the SkyScanner API, based on a given range of departure and arrival dates, and saves it as a .csv file.

### `search_flights.py`
`search_flights.py` calls the SkyScanner API to request the cheapest return flights from a nested list of SkyScanner API sessions IDs.

> Note: Before running `search_flights.py`, wait around 5 minutes after running `create_sessions.py`, otherwise you may get an error.
