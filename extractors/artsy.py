# external modules
import requests
import os
import logging
import json
# project modules
from utils import constants
from infra import gcp

logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

# Argument data_type is a string that can whether be 'artists' or 'artworks'
def extract_artsy_data(data_type):
    # inform the time of the extraction
    logging.info("Starting extraction of %s data", data_type)

    if gcp.file_exists('art_data_files', 'artsy_'+data_type+'_info.json'):
        last_id_and_url = get_last_page_and_item(data_type)
        print(last_id_and_url)
        page_url = get_last_page_and_item(data_type)['artsy_last_'+data_type+'_page_url']
        last_id = get_last_page_and_item(data_type)['artsy_last_'+data_type+'_id']
        logging.info("last id: ", last_id, "last page url: ", page_url)
        # Won't start collecting data until last imported item is found
        start_collecting = False
    else:
        logging.info("Database is empty")
        last_id = ""
        page_url = last_page_url = constants.ARTSY_API_URL + data_type
        # create json file for last page and item
        json.dump({}, open('./temporary-files/artsy_'+data_type+'_last_items.json', 'w'))
        set_last_page_and_item(data_type, last_id, page_url)
        # Start collecting data right away
        start_collecting = True

    # request data from artsy api
    req = requests.get(page_url, headers=constants.ARTSY_API_HEADERS)
    logging.info("API request ok")
    
    # Boolean used to break the loop at the last page
    isLast = False

    # List of new items to be added
    new_items = []
    try:
        # Loop through pages of data
        while not isLast:
            reqjson = req.json()
            # Iterate through items in page
            for item in reqjson['_embedded'][data_type]:
                id = item['id']
                logging.info("id: %s", id)
                # If start_collecting is false, check if item id matches last imported id
                if not start_collecting:
                    # If item id matches last imported id, start collecting new items
                    if id == last_id:
                        start_collecting = True
                    pass
                else:
                    # Insert item in new items list
                    new_items.append(item)
                # Circuit breaker to stop loop at last page
                if 'next' not in reqjson['_links']:
                    logging.info("last page reached")
                    isLast = True
                    break
            # Get next page to be iterated over
            page_url = reqjson['_links']['next']['href']
            req = requests.get(page_url, headers=constants.ARTSY_API_HEADERS)

        # After looping over pages, check if there are new items to be added
        if len(new_items) == 0:
            logging.info("No new items to be added")
        else:
            # save new_items in json file
            json.dump(new_items, open('./temporary-files/artsy_'+data_type+'_info.json', 'w'))
            gcp.store_file_in_gcs('art_data_files', './temporary-files/artsy_'+data_type+'_info.json', 'artsy_'+data_type+'_info.json')
            logging.info(str(len(new_items)) + " new items inserted in gcloud")

    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        print(e)
    finally: 
        print(last_id, last_page_url)
        # Update last page and item in gcp json file
        set_last_page_and_item(data_type, last_id, last_page_url)


# Gets the last page and item for a given data base
def get_last_page_and_item(data_type):
    last_items = gcp.retrieve_file_from_gcs('art_data_files', 'artsy_'+data_type+'_last_items.json', './temporary-files/artsy_'+data_type+'_last_items.json')
    return last_items

# Sets the last page and item for a given data base
def set_last_page_and_item(data_type, last_id, last_page_url):
    last_items = {}
    last_items['artsy_last_'+data_type+'_id'] = last_id
    last_items['artsy_last_'+data_type+'_page_url'] = last_page_url
    print(last_items)
    # save last_items in json file named 'artsy_'+data_type+'_last_items.json'
    json.dump(last_items, open('artsy_'+data_type+'_last_items.json', 'w'))
    gcp.store_file_in_gcs('art_data_files', './temporary-files/artsy_'+data_type+'_last_items.json', 'artsy_'+data_type+'_last_items.json')
    
