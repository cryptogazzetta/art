# External modules
from bs4 import BeautifulSoup
import requests
from lxml import etree
import re
import pandas as pd
import logging
import csv
import os
# Project modules
import gcp

categories = ['Paintings', 'Photography', 'Drawings',
              'Sculpture', 'Digital', 'Prints']

category = categories[0]

# Aparentemente, há 250 páginas para iterar
def get_artworks_links(category, style):
    page = 1
    links = []

    # Check if the file exists in GCS
    if gcp.file_exists('art_data', 'artworks_links.txt'):
        # Retrieve the existing file from GCS
        gcp.retrieve_file_from_gcs('art_data', 'artworks_links.txt', 'artworks_links.txt')
        # Read the existing links from the file
        with open('artworks_links.txt', 'r') as file:
            already_in_list = [line.strip() for line in file]
    else:
        already_in_list = []

    while True:
        print('page:', page)
        saatchi_url = 'https://www.saatchiart.com'
        url = f'{saatchi_url}/{category}/{style}?hitsPerPage=100&page={page}'

        # Getting the dom object
        user_agent = {'User-agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=user_agent)
        soup = BeautifulSoup(response.text, "html.parser")
        dom = etree.HTML(str(soup))

        # Getting the links
        a_elements = dom.xpath('//div[@data-type="artwork-info"]/p/a')
        for a in a_elements:
            link = saatchi_url + a.attrib['href']
            if link not in already_in_list:
                links.append(link)
                already_in_list.append(link)

        # Getting the next page
        next_button = dom.xpath('//div[@data-section="pagination"]/a[@aria-label="Pagination next"]')[0]
        if next_button.attrib['rel'] == 'nofollow':
            break
        page += 1

    # Store the updated links in GCS
    with open('artworks_links.txt', 'a') as file:
        for link in links:
            file.write(link + '\n')
    gcp.store_file_in_gcs('art_data', 'artworks_links.txt', 'artworks_links.txt')

    # Remove the local file
    os.remove('artworks_links.txt')

    return links


def get_artwork_info(url, bucket_name, gcs_file_name):
    # Check if artworks_info.csv file exists in GCP
    if gcp.file_exists(bucket_name, gcs_file_name):
        # Retrieve the existing file from GCS
        local_file_path = "artworks_info.csv"
        gcp.retrieve_file_from_gcs(bucket_name, gcs_file_name, local_file_path)
        
        # Check for duplicates
        with open(local_file_path, "r") as file:
            reader = csv.DictReader(file)
            existing_urls = [row["url"] for row in reader]

        if url in existing_urls:
            print(f"Artwork info for {url} already exists. Skipping...")
            return None

    # Getting the dom object
    user_agent = {'User-agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=user_agent)
    soup = BeautifulSoup(response.text, "html.parser")
    dom = etree.HTML(str(soup))
    
    # Fill the artwork_info dictionary with the artwork information
    artwork_info = {}
    artwork_info['url'] = url
    artwork_info['title'] = dom.xpath('//h1[@data-type="title-text"]')[0].text
    artwork_info['img'] = dom.xpath('//div[@data-type="image"]/img')[0].attrib['src']
    artwork_info['artist'] = dom.xpath('//a[@data-type="profile"]')[0].text
    artwork_info['artist_link'] = dom.xpath('//a[@data-type="profile"]')[0].attrib['href']
    artwork_info['country'] = dom.xpath('//p[@data-type="country"]')[0].text
    artwork_info['price'] = re.sub(r'[^0-9]', '', dom.xpath('//div[@class="krw7aj-0 uyv957-3 kpRguR bGUIw"]')[0].text)
    artwork_info['views'] = dom.xpath('//div[@data-type="views"]')[0].text
    artwork_info['favorite'] = dom.xpath('//div[@data-type="favorite"]')[0].text
    artwork_info['description'] = dom.xpath('//p[@data-type="description"]')[0].text

    # Getting artwork info from accordion sections
    info_keys = dom.xpath('///div[@data-type="accordion-sub-section"]/p/span[@data-type="accordion-sub-header"]')
    info_values = dom.xpath('///div[@data-type="accordion-sub-section"]/p/*[@data-type="accordion-sub-value"]')
    for info_key, info_value in zip(info_keys, info_values):
        if info_value.text is None:
            value = ', '.join([element.text for element in info_value])
        else:
            value = info_value.text
        artwork_info[info_key.text.replace(':', '')] = value

    # Store the artwork info in the CSV file
    with open(local_file_path, "a") as file:
        writer = csv.DictWriter(file, fieldnames=artwork_info.keys())
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(artwork_info)
    gcp.store_file_in_gcs(bucket_name, local_file_path, gcs_file_name)
    
    return artwork_info



def get_all_artworks_info(category):
    links = get_artworks_links(category)
    print('Artworks links collected: ', len(links))
    artworks_info = []
    for link in links:
        try:
            artwork_info = get_artwork_info(link)
            artworks_info.append(artwork_info)
        except Exception as Argument:
            logging.exception("Error occurred while extracting artwork info")
    return artworks_info
