import requests, re, csv, time
from urllib.parse import quote_plus

# Constants
SPREADSHEET_ID = "1s4J3f-swHIY-F2-u_wmigAzt1N4Zg8uJdUcGgXLOUjk"
SHEET_NAME = "Sheet1"
CREDENTIALS_PATH = "credential.json"

FILTER_OUT = ["google", "gstatic", "schema", "example", "ggpht"]
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.(?!png|jpg|gif|jpeg)[a-zA-Z]{2,}", re.IGNORECASE)
URL_REGEX = re.compile(r"https?:\/\/[^\/\s]+\/[^\"'\s]+")

# Main list to store [url, email]
final_data = []

def user_input_query():
    return input("Enter your query (use + between words): ").strip()

def fetch_google_maps_results(query):
    search_url = f"https://www.google.com/maps/search/{query}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    print(f"Fetching Google Maps results for: {query}")
    res = requests.get(search_url, headers=headers)
    return res.text

def extract_links(html):
    urls = re.findall(URL_REGEX, html)
    filtered = [url for url in urls if not any(bad in url for bad in FILTER_OUT)]
    return list(set(filtered))  # Remove duplicates

def extract_emails_from_url(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        emails = re.findall(EMAIL_REGEX, res.text)
        return emails
    except:
        return []

def scrape_emails(urls):
    seen_emails = set()
    for url in urls:
        emails = extract_emails_from_url(url)
        for email in emails:
            if email not in seen_emails:
                seen_emails.add(email)
                final_data.append([url, email])
        time.sleep(1)
    return final_data

def send_to_google_sheet(spreadsheet_id, sheet_name, credentials_json_path, data):
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_file(credentials_json_path, scopes=scopes)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    sheet.clear()
    sheet.append_row(["URL", "Email"])
    for row in data:
        sheet.append_row(row)
    print("✅ Sent to Google Sheet.")

# -------- RUN SCRIPT -------- #
if __name__ == "__main__":
    with open("working.txt", "w") as f:
        data = f.readlines()
    for i in data:
        query = str(i)
        html = fetch_google_maps_results(query)
        urls = extract_links(html)
        print(f"Found {len(urls)} candidate URLs...")

        data = scrape_emails(urls)
        print(f"✅ Scraped {len(data)} unique emails.")

        send_to_google_sheet(SPREADSHEET_ID, SHEET_NAME, CREDENTIALS_PATH, data)
