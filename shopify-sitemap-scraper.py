
import requests
from bs4 import BeautifulSoup
import random
import pandas as pd

def request_xml(guid):
  user_agents_list = [
      'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
  ]

  xml_data = requests.get(guid, headers={'User-Agent': random.choice(user_agents_list)}).content
  return xml_data

## Extract Blog Entries
def blog_entries(index, items_length, link, results):
  if results:
    page_elements = results.find_all("article", class_="article")
    for page_content in page_elements:
      # Set variables
      title = page_content.find("h1").text.strip()
      bodyContent = page_content.find("div", class_="rte")
      pubDate = page_content.find("time")

      # Format object
      row = {
          'link': link,
          'title': title,
          'pubDate': pubDate.text.strip(),
          'bodyContent': bodyContent
      }
    return bodyContent

def parse_guid(index, items_length, guid, slug):
    guid_page_content = request_xml(guid)
    soup = BeautifulSoup(guid_page_content, "html.parser")   
    results = soup.find(id=slug)
    guid_data = blog_entries(index, items_length, guid, results)
    return guid_data

def parse_xml(xml_config, xml_data):
  # Initializing soup variable
    soup = BeautifulSoup(xml_data, 'xml')

  # Creating column for table
    df = pd.DataFrame(columns=['guid', 'title', 'pubDate', 'body'])

  # Iterating through item tag and extracting elements
    all_items = soup.find_all('url')
    items_length = len(all_items)
    
    for index, item in enumerate(all_items):
        guid = item.find('loc').text
        image = item.find('image')
        guid_data = parse_guid(index, items_length, guid, 'shopify-section-article-template')
        title =  item.find('image:title')
        body = guid_data
        pub_date = item.find('lastmod').text

       # Adding extracted elements to rows in table
        row = {
            'guid': guid,
            'title': title,
            'pubDate': pub_date,
            'body': body
        }

        df = df._append(row, ignore_index=True)
        print(f'Appending row %s of %s' % (index+1, items_length))

    return df

## Initiate scrape & write data to CSV when complete

class xmlConfig:
  guid = 'https://blacksheepniagara.com/sitemap_blogs_1.xml'
  blog = True
  collection = False
  page = True
  file = False

xml_config = xmlConfig()

df = parse_xml(
  xml_config,
  request_xml(getattr(xml_config, 'guid'))
)
df.to_csv('shopify.csv')


