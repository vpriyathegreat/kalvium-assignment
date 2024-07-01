import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

# Main URL for party-wise results
main_url = "https://results.eci.gov.in/AcResultGenJune2024/partywiseresult-S18.htm"

# Make a request to the main page
response = requests.get(main_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the table containing party-wise results
party_results = []

table = soup.find('div', class_='rslt-table teble-responsive').find('table')
rows = table.find('tbody').find_all('tr')

# Extracting party-wise results
for row in rows:
    columns = row.find_all('td')
    party = columns[0].text.strip()
    won_link = columns[1].find('a')
    won = won_link.text.strip() if won_link else columns[1].text.strip()
    won_url = urljoin(main_url, won_link['href']) if won_link else None
    leading = columns[2].text.strip()
    total = columns[3].text.strip()

    party_results.append({
        'Party': party,
        'Won': won,
        'Leading': leading,
        'Total': total,
        'Won URL': won_url
    })

# Prepare lists to hold candidate data
all_data = []

# Scraping detailed candidate data from each party's won URL
for party in party_results:
    if party['Won URL']:
        try:
            response = requests.get(party['Won URL'])
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the table containing constituency links
            constituency_table = soup.find('table', class_='table table-striped table-bordered')
            constituency_rows = constituency_table.find('tbody').find_all('tr')

            # Loop through each row to get constituency links and names
            constituencies = []
            for row in constituency_rows:
                cols = row.find_all('td')
                if len(cols) > 1:
                    constituency_name = cols[1].text.strip()
                    constituency_link = cols[1].find('a')['href']
                    constituencies.append((constituency_name, constituency_link))

            # Loop through each constituency and scrape data
            for constituency_name, constituency_link in constituencies:
                url = urljoin(party['Won URL'], constituency_link)
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all candidate boxes
                cand_boxes = soup.find_all('div', class_='cand-box')

                if not cand_boxes:
                    print(f"No candidate boxes found for constituency: {constituency_name}")

                # Loop through each candidate box and extract information
                for box in cand_boxes:
                    name = box.find('h5').text.strip()
                    party_name = box.find('h6').text.strip()
                    status = box.find('div', class_='status').div.text.strip()
                    votes = box.find('div', class_='status').find_all('div')[1].text.split()[0].strip()

                    # Check if the margin is present
                    margin_span = box.find('div', class_='status').find_all('div')[1].find('span')
                    margin = margin_span.text.strip() if margin_span else "N/A"

                    # Append data to list
                    all_data.append([constituency_name, name, party_name, status, votes, margin])

        except Exception as e:
            print(f"Error scraping data for {party['Party']}: {e}")

# Check if data was collected
if not all_data:
    print("No data was collected.")

# Create a DataFrame
columns = ['assembly Constituency', 'Candidate Name', 'Party', 'Status', 'Votes', 'Margin']
df = pd.DataFrame(all_data, columns=columns)

# Save DataFrame to a CSV file
df.to_csv('odelection_results_with_constituencies.csv', index=False)

print("Data has been scraped and saved to 'odelection_results_with_constituencies.csv'")
