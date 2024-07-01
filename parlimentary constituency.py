import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the main page with constituencies
main_url = "https://results.eci.gov.in/PcResultGenJune2024/partywisewinresultState-369.htm"

# Make a request to the main page
response = requests.get(main_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the table containing constituency links
constituency_table = soup.find('table', class_='table table-striped table-bordered')
constituency_rows = constituency_table.find('tbody').find_all('tr')

# Prepare list to hold constituency data
constituencies = []

# Loop through each row to get constituency links and names
for row in constituency_rows:
    cols = row.find_all('td')
    constituency_name = cols[1].text.strip()
    constituency_link = cols[1].find('a')['href']
    constituencies.append((constituency_name, constituency_link))

print(f"Found {len(constituencies)} constituencies")

# Prepare lists to hold candidate data
all_data = []

# Base URL for constituency pages
base_url = "https://results.eci.gov.in/PcResultGenJune2024/"

# Loop through each constituency and scrape data
for constituency_name, constituency_link in constituencies:
    url = base_url + constituency_link
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all candidate boxes
    cand_boxes = soup.find_all('div', class_='cand-box')

    if not cand_boxes:
        print(f"No candidate boxes found for constituency: {constituency_name}")

    # Loop through each candidate box and extract information
    for box in cand_boxes:
        name = box.find('h5').text.strip()
        party = box.find('h6').text.strip()
        status = box.find('div', class_='status').div.text.strip()
        votes = box.find('div', class_='status').find_all('div')[1].text.split()[0].strip()

        # Check if the margin is present
        margin_span = box.find('div', class_='status').find_all('div')[1].find('span')
        margin = margin_span.text.strip() if margin_span else "N/A"

        # Append data to list
        all_data.append([constituency_name, name, party, status, votes, margin])

# Check if data was collected
if not all_data:
    print("No data was collected.")

# Create a DataFrame
columns = ['Parliamentary Constituency', 'Candidate Name', 'Party', 'Status', 'Votes', 'Margin']
df = pd.DataFrame(all_data, columns=columns)

# Save DataFrame to a CSV file
df.to_csv('election_results_with_constituencies.csv', index=False)

print("Data has been scraped and saved to 'election_results_with_constituencies.csv'")

