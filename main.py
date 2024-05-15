import argparse
import requests
import pandas as pd
import datetime

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--asins', type=str, required=True, help='Comma-delimited list of ASINs')
    parser.add_argument('--isos', type=str, required=True, help='Comma-delimited list of ISOs')
    parser.add_argument('--cookie-source', default='EU', type=str, required=True, choices=['EU', 'US', 'FE'], help='Cookie source')
    parser.add_argument('--cookie', type=str, required=True, help='Cookie string')
    parser.add_argument('--start-date', type=str, default='2023-01-22', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, default=None, help='End date (YYYY-MM-DD)')
    return parser.parse_args()

def get_weekend_dates(start_date, end_date):
    while start_date.weekday() != 5:
        start_date += datetime.timedelta(days=1)
    weekend_dates = []
    while start_date <= end_date:
        weekend_dates.append(start_date.strftime("%Y-%m-%d"))
        start_date += datetime.timedelta(days=7)
    return weekend_dates

def clean_dataframe(df):
    df.replace(to_replace=["'", '"'], value='', regex=True, inplace=True)
    return df

def fetch_data(asin, iso, date, cookie, endpoint):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Cookie": cookie,
    }
    payload = {
        "filterSelections": [
            {"id": "asin", "value": asin, "valueType": "ASIN"},
            {"id": "reporting-range", "value": "weekly", "valueType": None},
            {"id": "weekly-week", "value": date, "valueType": "weekly"}
        ],
        "reportId": "query-performance-asin-report-table",
        "reportOperations": [
            {
                "ascending": True,
                "pageNumber": 1,
                "pageSize": 100,
                "reportId": "query-performance-asin-report-table",
                "reportType": "TABLE",
                "sortByColumnId": "qp-asin-query-rank"
            }
        ],
        "selectedCountries": [iso.lower()],
        "viewId": "query-performance-asin-view"
    }
    # print("using following data", endpoint, headers, payload)
    response = requests.post(endpoint, headers=headers, json=payload)
    if response.status_code == 200:
        response_json = response.json()
        if response_json['reportsV2'][0]['totalItems'] == 0:
            return None
        rows = response_json["reportsV2"][0]["rows"]
        df = pd.DataFrame(rows)
        df['ISO2'] = iso
        df['ASIN'] = asin
        df['Date'] = date
        return clean_dataframe(df)
    elif response.status_code == 400:
        print(f"No data available for {asin}, {iso}, {date}")
    else:
        raise Exception(f"Request failed with status code: {response.status_code}")

def main():
    args = get_args()
    asins = args.asins.split(',')
    isos = args.isos.split(',')
    cookie = args.cookie
    cookie_source = args.cookie_source
    if args.start_date:
        start_date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d').date()
    else:
        start_date = datetime.date(2023, 1, 22)  # Introduction Date of SQP

    if args.end_date:
        end_date = datetime.datetime.strptime(args.end_date, '%Y-%m-%d').date()
    else:
        today = datetime.date.today()
        end_date = today - datetime.timedelta(days=today.weekday() + 2)

    weekend_dates = get_weekend_dates(start_date, end_date)

    print("fetching data for", asins, "requested isos:", isos, "cookie source:",cookie_source)

    endpoints = {
        'EU': 'https://sellercentral.amazon.de/api/brand-analytics/v1/dashboard/query-performance/reports?stck=EU&mons_redirect=stck_reroute',
        'US': 'https://sellercentral.amazon.com/api/brand-analytics/v1/dashboard/query-performance/reports?stck=EU&mons_redirect=stck_reroute',
        'FE': 'https://sellercentral.amazon.com.au/api/brand-analytics/v1/dashboard/query-performance/reports?stck=EU&mons_redirect=stck_reroute'
    }
    endpoint = endpoints[cookie_source]

    all_data = pd.DataFrame()
    for iso in isos:
        for asin in asins:
            for date in weekend_dates:
                try:
                    df = fetch_data(asin, iso, date, cookie, endpoint)
                    print("sucessfully requested data for", asin, iso, date)
                    if df is not None:
                        all_data = pd.concat([all_data, df], ignore_index=True)
                except Exception as e:
                    print(f"Error fetching data for {asin}, {iso}, {date}: {e}")


    if not all_data.empty:
        all_data.to_excel('output.xlsx', index=False)
    else:
        print("No data found.")

if __name__ == '__main__':
    main()