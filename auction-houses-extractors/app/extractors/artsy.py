# external modules
import requests
import os
import pymongo
import logging
# project modules
from infra import mongo
from utils import constants

logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

# Argument data_type is a string that can whether be 'artists' or 'artworks'
def extract_artsy_data(data_type):
    # inform the time of the extraction
    logging.info("Starting extraction of %s data", data_type)
    
    try:
        # Connect to respective database on mongo
        database = mongo.get_mongo_db(data_type)

        # If database is empty, start collecting data from first page
        if database.count_documents({}) == 0:
            logging.info("Database is empty")
            # Get first page url
            page_url = constants.ARTSY_API_URL + data_type
            last_id = ""
            set_last_page_and_item(data_type, last_id, page_url)
            print(get_last_page_and_item(data_type))
            # Start collecting data right away
            start_collecting = True
        
        # If database is not empty, check for the url of last page imported
        else:
            page_url = get_last_page_and_item(data_type)['last_page_url']
            print("last page url: " + str(page_url))
            # Get id of last item imported
            last_id = get_last_page_and_item(data_type)['last_id']
            print("last id: " + str(last_id))
            # Won't start collecting data until last imported item is found
            start_collecting = False

        print("url of the first page to be iterated over : "+ str(page_url))
        # request data from artsy api
        req = requests.get(page_url, headers=constants.ARTSY_API_HEADERS)
        logging.info("API request ok")
        
        # Boolean used to break the loop at the last page
        isLast = False
        # FOR TESTING ONLY Iteration page counter used during testing
        n_page = 1
        # FOR TESTING ONLY Number of pages to be iterated over
        pages = 100

        # List of new items to be added
        new_items = []

        # Loop through pages of data
        # FOR TESTING ONLY: n_page and pages
        while(not isLast and n_page<=pages):
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
                        print("ready to start collecting")
                    pass
                else:
                    # Insert item in new items list
                    new_items.append(item)
                # Circuit breaker to stop loop at last page
                if 'next' not in reqjson['_links']:
                    isLast = True
                    break
            # FOR TESTING ONLY Increment page counter
            n_page += 1
            if n_page<=pages:
                # Get next page to be iterated over
                page_url = reqjson['_links']['next']['href']
                req = requests.get(page_url, headers=constants.ARTSY_API_HEADERS)

        # After looping over pages, check if there are new items to be added
        if len(new_items) == 0:
            print("No new items to be added")
        else:
            # Insert new data in mongo
            database.insert_many(new_items)
            print(str(len(new_items)) + " new items inserted in mongo")
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
    finally: 
        # Update last page and item in mongo document
        update_last__page_and_item(data_type, id, page_url)
        print("last id: %s, last page: %s", get_last_page_and_item(data_type)['last_id'], get_last_page_and_item(data_type)['last_page_url'])


# Gets the last page and item for a given data base
def get_last_page_and_item(data_type):
    last_items = mongo.get_mongo_db('last_items')
    return last_items.find_one({'database': 'artsy_'+data_type})

# Sets the last page and item for a given data base
def set_last_page_and_item(data_type, id, page_url):
    last_items = mongo.get_mongo_db('last_items')
    last_items.insert_one({'database': 'artsy_'+data_type, 'last_id': id, 'last_page_url': page_url})

# Updates the last page and item for a given data base
def update_last__page_and_item(data_type, id, page_url):
    last_items = mongo.get_mongo_db('last_items')
    last_items.update_one({'database': 'artsy_'+data_type}, {'$set':{'last_id': id, 'last_page_url': page_url}})