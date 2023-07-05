from extractors import artsy, christies
from utils import constants
from analysis import data_from_mongo
from infra import mongo

import os

def main():
    # MONGO
    # mongo.clean_mongo_data('artists')
    # mongo.clean_mongo_data('last_items')
    
    # ARTSY
    # artsy.extract_artsy_data('artists')
    
    # CHRISTIE'S
    # christies.get_auctions_links(2022, 2023)
    christies.get_lots_from_auction('https://www.christies.com/en/auction/important-americana-29081/')


if __name__ == '__main__':
    main()