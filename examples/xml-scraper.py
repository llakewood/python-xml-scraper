
import requests
from bs4 import BeautifulSoup
import random
import pandas as pd

user_agents_list = [
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
]

URL = "https://rss.nytimes.com/services/xml/rss/nyt/US.xml"
xml_data = requests.get(URL, headers={'User-Agent': random.choice(user_agents_list)}).content

def parse_xml(xml_data):
  # Initializing soup variable
    soup = BeautifulSoup(xml_data, 'xml')

  # Creating column for table
    df = pd.DataFrame(columns=['guid', 'title', 'pubDate', 'description'])

  # Iterating through item tag and extracting elements
    all_items = soup.find_all('item')
    items_length = len(all_items)
    
    for index, item in enumerate(all_items):
        guid = item.find('guid').text
        title = item.find('title').text
        pub_date = item.find('pubDate').text
        description = item.find('description').text

       # Adding extracted elements to rows in table
        row = {
            'guid': guid,
            'title': title,
            'pubDate': pub_date,
            'description': description
        }

        df = df._append(row, ignore_index=True)
        print(f'Appending row %s of %s' % (index+1, items_length))

    return df

## Create a CSV
df = parse_xml(xml_data)
df.to_csv('news.csv')