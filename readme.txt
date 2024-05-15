# SQP Fetcher

This script fetches Search Query Performance (SQP) data from Amazon's Brand Analytics API for specified ASINs, ISOs, and date range.

## Requirements

- Python 3.6+
- packages in the requirements.txt file

Install the required packages using:

pip install -r requirements.txt

You also need a cookie string to authenticate the API requests. You can get this string by logging into your Amazon Seller Central account, opening the Network tab in the Developer Tools of your browser, and copying the value of the cookie from any request to the Brand Analytics API.

Step by step:

1. Open following page and login: https://sellercentral.amazon.de/brand-analytics/dashboard/query-performance?view-id=query-performance-asin-view&country-id=us
2. Open Developer Tools by pressing F12 (or right click and inspect in chrome) and go to the Network tab
3. Reload the page, filter for xhr requests and click on either of the following requests: dashboard, reports
4. Scroll down to the Request Headers and copy the entire cookie string. Be careful not to copy any other characters before or after the cookie string.
5. Now that you have obtained the cookie, you can open a command prompt in the downloaded folder and run the command

## Usage

Run the script with the following command-line arguments:

python main.py --asins ASIN1,ASIN2,... --isos ISO1,ISO2,... --cookie-source COOKIE_SOURCE --cookie COOKIE_STRING [--start-date START_DATE] [--end-date END_DATE]


- `--asins`: Comma-delimited list of ASINs (required)
- `--isos`: Comma-delimited list of ISOs (required)
- `--cookie`: Cookie string (required)
- `--cookie-source`: Cookie source (optional, choices: 'EU', 'US', 'FE', deault: 'EU')
- `--start-date`: Start date in YYYY-MM-DD format (optional, default: '2023-01-22')
- `--end-date`: End date in YYYY-MM-DD format (optional, default: previous Saturday)

Example:

python main.py --asins B07X6HLRMG,B07X6C9RMG --isos DE,US --cookie-source EU --cookie "cookie_string_here" --start-date 2023-01-22 --end-date 2023-04-01


## Output

The script will fetch SQP data for the specified ASINs, ISOs, and date range, and save the results to an Excel file named `output.xlsx`.
