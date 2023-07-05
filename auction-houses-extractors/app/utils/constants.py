import os

# Artsy API constants
ARTSY_API_URL = 'https://api.artsy.net/api/'
ARTSY_API_HEADERS = {
        'Accept': 'application/vnd.artsy-v2+json',
        'X-Xapp-Token': 'eyJhbGciOiJIUzI1NiJ9.eyJyb2xlcyI6IiIsInN1YmplY3RfYXBwbGljYXRpb24iOiI2NDE5OWY5OTM4MWJkNjAwMGJkMTdkMGMiLCJleHAiOjE2ODA2MTg1NTQsImlhdCI6MTY4MDAxMzc1NCwiYXVkIjoiNjQxOTlmOTkzODFiZDYwMDBiZDE3ZDBjIiwiaXNzIjoiR3Jhdml0eSIsImp0aSI6IjY0MjJmOWJhMzQyYTVhMDAwYjNhMjU5NSJ9.IXgzYxWkJJkPvTKoZ_8vHAYW7LuDaAH3L6LRnd5vrxk' 
    }

# MongoDB constants

# Sotheby's constants
EMAIL = "christian@fynt.io"
SOTHEBYS_PASSWORD = "t#3u!%h9Up!JSZb"

# Artsy constants
artsys_last_page_url = os.getenv("artsys_last_page_url")
artsys_last_item_id = os.getenv("artsys_last_item_id")

def set_artsys_page_url(value):
    os.environ["artsys_last_page_url"] = str(value)