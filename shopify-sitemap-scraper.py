
import requests
from bs4 import BeautifulSoup
import random
import pandas as pd

# Fake a browser to bypass robot.txt exclusions
user_agents_list = [
    'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
]

URL = "https://blacksheepniagara.com/sitemap.xml"

# Section URL for handy usage later
def setURL(URL = URL):
  URL = URL
  return URL

def getDomain():
  domain_name = setURL().split('/')[2]
  return domain_name.split('.')[0]

# Does list link to XML children, or HTML pages?
def is_parent(loc):
  loc = setURL(loc).split('.')[-1]
  parent = 0
  if "xml" in loc : parent = 1
  return parent

print('Scraping:' + getDomain())

# Get XML data ready for parseing
xml_data = requests.get(URL, headers={'User-Agent': random.choice(user_agents_list)}).content

# Parse XML function
def scrape_sitemap(xml_data):
    
  # Initializing soup variable
    soup = BeautifulSoup(xml_data, 'xml')
    
  # Creating table columns to write CSV data
    df = pd.DataFrame(columns=['loc'])    

  # Iterating through loc tag and extracting text link
    all_items = soup.find_all('loc')
    items_length = len(all_items)
    
    for index, item in enumerate(all_items):
        loc = item.text

        if is_parent(loc) == 0:
          parse_children(loc)
        else:
          parse_parent(loc, index, items_length)


    return df

def csv_prep(link, index, items_length, df):
  # Adding extracted elements to rows in table
  row = {
      'loc': link
  }
  df = df._append(row, ignore_index=True)
  print(f'Appending row %s of %s' % (index+1, items_length))
  return 

# parse_children
def parse_parent(link, index, items_length):
  xml_data = requests.get(link, headers={'User-Agent': random.choice(user_agents_list)}).content
  df = scrape_sitemap(xml_data)
  csv_prep(link, index, items_length, df)
  

# parse_children
def parse_children(link):
  
  if "products" in link:
    # results = soup.find(id="shopify-section-article-template")
    print('is product')
  elif "pages" in link: 
    # results = soup.find(id="shopify-section-article-template")
    print('is page')
  elif "collections" in link: 
    # results = soup.find(id="shopify-section-article-template")
    print('is collection')
  elif "files" in link: 
    # results = soup.find(id="shopify-section-article-template")
    print('is file')
  elif "blogs" in link: 
    page = requests.get(link)
    soup = BeautifulSoup(page.content, "html.parser")   
    results = soup.find(id="shopify-section-article-template")
    blog_entries(results)

## Extract Blog Entries
def blog_entries(results):
  if results:
    page_elements = results.find_all("article", class_="article")
    for page_content in page_elements:
        title_element = page_content.find("h1")
        body_content = page_content.find("div", class_="rte")
        pub_date = page_content.find("time")
        print(title_element.text.strip())
        # print(body_content)
        # print(pub_date.text.strip())
        print()

## Create a CSV
df = scrape_sitemap(xml_data)
df.to_csv(getDomain()+'.csv')