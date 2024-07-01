import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the results page (example URL, please replace with actual URL)
url = "https://results.eci.gov.in/AcResultGenJune2024/candidateswise-S01136.htm"

# Make a request to the website
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all candidate boxes
cand_boxes = soup.find_all('div', class_='cand-box')

# Prepare lists to hold data
data = []

# Loop through each candidate box and extract information
for box in cand_boxes:
    name = box.find('h5').text.strip()
    party = box.find('h6').text.strip()
    status = box.find('div', class_='status').div.text.strip()
    votes = box.find('div', class_='status').find_all('div')[1].contents[0].strip()
    margin = box.find('div', class_='status').find_all('div')[1].span.text.strip()

    data.append([name, party, status, votes, margin])

# Create a DataFrame
df = pd.DataFrame(data, columns=['Candidate Name', 'Party', 'Status', 'Votes', 'Margin'])

# Save DataFrame to a CSV file
df.to_csv('election_results.csv', index=False)

print("Data has been scraped and saved to 'assemblyelection_results.csv'")
