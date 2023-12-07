
import requests
from bs4 import BeautifulSoup
import random
import pandas as pd

##############################################
# Python XML Scraper
# - Features
# -- Parse and write Shopify blogEntries
# - Next up
# -- Parse and write Shopify desired types based on config
#############################################

##############################################
# SCRIPT CONFIG
# - must be top-level sitemap.xml for Shopify
# - pages and blogs cases only, no files or collections yet
##############################################

class xmlConfig:
  guid = 'https://shopifysite.com/sitemap.xml'
  blog = True
  collection = False
  page = True
  file = False

##############################################
# FUNCTIONAL LOGIC
##############################################

# Configure, Execute, and Complete script actions
def init():
  
  # Name it nice
  guid = getattr(xmlConfig(), 'guid')

  ## Parse source xml to DataFrame table, passing configs
  df = parse_sitemap(
    request_xml(guid)
  )

  ## Write the DataFrame table to local csv
  df.to_csv('shopify.csv')

def parse_sitemap(xml_data):

  # Creating column shape for table
  df = pd.DataFrame(columns=['guid', 'title', 'pubDate', 'body'])

  # Initializing soup variable for top level XML
  soup = BeautifulSoup(xml_data, 'xml')
  all_submaps = soup.find_all('sitemap')
  submaps_items_length = len(all_submaps)

  for index, item in enumerate(all_submaps):
    submap_guid = item.find('loc').text
    parseSubmap = False

    if ('blog' in submap_guid and getattr(xmlConfig(), 'blog')) : parseSubmap = True
    if ('page' in submap_guid and getattr(xmlConfig(), 'page')) : parseSubmap = True

    if parseSubmap:
      df = parse_xml(
        request_xml(submap_guid),
        df
      )

  return df

# Read and structure XML results as DataFrame for csv export
def parse_xml(xml_data, df):
 
  # Initializing soup variable for child level XML
  soup = BeautifulSoup(xml_data, 'xml')

  # Iterating through item tag and extracting elements
  all_items = soup.find_all('url')
  items_length = len(all_items)
  
  for index, item in enumerate(all_items):
    guid = item.find('loc').text
    title =  item.find('image:title')
    body = parse_guid(index, items_length, guid)
    pub_date = item.find('lastmod').text

    # Adding extracted elements to rows in table
    row = {
        'guid': guid,
        'title': title,
        'pubDate': pub_date,
        'body': getattr(body,'body')
    }

    df = df._append(row, ignore_index=True)
    print(f'Appending row %s of %s' % (index+1, items_length))

  return df

# Return XML structure from remote host server through browser simulation
def request_xml(guid):
  user_agents_list = [
      'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
  ]
  xml_data = requests.get(guid, headers={'User-Agent': random.choice(user_agents_list)}).content
  return xml_data

# Structre HTML response of sitemap link results
def parse_guid(index, items_length, guid):
  guid_page_content = request_xml(guid)
  soup = BeautifulSoup(guid_page_content, "html.parser")   
  
  ## Determine desired data
  guid_data = None
  if 'blog' in guid and getattr(xmlConfig(), 'blog'):
    results = soup.find(id='shopify-section-article-template')
    guid_data = blog_entries(index, items_length, guid, results)

  if 'page' in guid and getattr(xmlConfig(), 'page'):
    results = soup.find(id='PageContainer')
    guid_data = pages_entries(index, items_length, guid, results)

  return guid_data

## Structure Blog Entries
def blog_entries(index, items_length, link, results):
  if results:
    page_elements = results.find_all("article", class_="article")
    for page_content in page_elements:
      # Set variables
      # title = page_content.find("h1").text.strip()
      # bodyContent = page_content.find("div", class_="rte")
      # pubDate = page_content.find("time")
      print(page_content.find("div", class_="rte"))
      # Format object
      class row: 
        datatype = 'blog'
        body = page_content.find("div", class_="rte")

    return row()

## Structure Page Data
def pages_entries(index, items_length, link, results):
  if results:
    page_elements = results.find_all("div", class_="wrapper")
    for page_content in page_elements:
      
      # Format object
      class row: 
        datatype = 'page'
        body = page_content.find("div", class_="rte")
        
    return row()

## Onward, you crafty thing!
init()