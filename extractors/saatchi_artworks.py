# External modules
from bs4 import BeautifulSoup
import requests
from lxml import etree
import logging
import csv
import os
# Project modules
import infra.gcp as gcp
import utils.string_handle as string_handle
import utils.csv_handle as csv_handle

categories = ['Paintings', 'Photography', 'Drawings',
              'Sculpture', 'Digital', 'Prints']

paintings_styles = ['Abstract', 'Fine-Art', 'Modern', 'Abstract-Expressionism',
                   'Expressionism', 'Figurative', 'Impressionism', 'Realism',
                   'Conceptual', 'Minimalism', 'Portraiture', 'Pop-Art', 'Surrealism',
                   'Illustration', 'Art-Deco', 'Street-Art', 'Photorealism', 'Folk',
                   'Cubism', 'Documentary', 'Dada']

category = categories[0]


def get_artworks_links(category, style):
    page = 1
    links = []

    # Check if the file exists in GCS
    if gcp.file_exists('art_data_files', 'saatchi_artworks_links.txt'):
        # Retrieve the existing file from GCS
        gcp.retrieve_file_from_gcs('art_data_files', 'saatchi_artworks_links.txt', 'saatchi_artworks_links.txt')
        # Read the existing links from the file
        with open('saatchi_artworks_links.txt', 'r', encoding="utf-8") as file:
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
    with open('saatchi_artworks_links.txt', 'a', encoding="utf-8") as file:
        for link in links:
            file.write(link + '\n')
    gcp.store_file_in_gcs('art_data_files', 'saatchi_artworks_links.txt', 'saatchi_artworks_links.txt')

    # Remove the local file
    os.remove('saatchi_artworks_links.txt')

    return links


def get_artwork_info(url):

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
    artwork_info['views'] = dom.xpath('//div[@data-type="views"]')[0].text
    artwork_info['favorite'] = dom.xpath('//div[@data-type="favorite"]')[0].text
    artwork_info['description'] = dom.xpath('//p[@data-type="description"]')[0].text
    artwork_info['sale_status'] = dom.xpath('//div[@data-type="original"]')[0].get('data-status')
    try:
        if artwork_info['sale_status'] == 'soldOut':
            artwork_info['price'] = string_handle.get_number(str(dom.xpath('//div[@data-type="original"]/span/text()')))
        else:
            artwork_info['price'] = string_handle.get_number(dom.xpath('//div[@data-type="original"]/div/div')[0].text)
    except:
        artwork_info['price'] = None

    # Getting artwork info from accordion sections
    info_keys = dom.xpath('///div[@data-type="accordion-sub-section"]/p/span[@data-type="accordion-sub-header"]')
    info_values = dom.xpath('///div[@data-type="accordion-sub-section"]/p/*[@data-type="accordion-sub-value"]')
    for info_key, info_value in zip(info_keys, info_values):
        if info_value.text is None:
            value = ', '.join([element.text for element in info_value])
        else:
            value = info_value.text
        artwork_info[info_key.text.replace(':', '')] = value
    
    return artwork_info


def get_all_artworks_info(bucket_name, links_gcs_file_name, info_gcs_file_name, failed_urls_gcs_file_name):
    links_local_file_path = links_gcs_file_name
    info_local_file_path = info_gcs_file_name

    # If some artworks have already been stored, retrieve the existing info_gcs_file_name file
    if gcp.file_exists(bucket_name, info_gcs_file_name):
        gcp.retrieve_file_from_gcs(bucket_name, info_gcs_file_name, info_local_file_path)
        existing_artworks_info = csv_handle.csv_to_dict_list(info_local_file_path)
    else:
        # If no artworks have been stored yet, create an empty list
      existing_artworks_info = []

    # Retrieve the .txt file with links
    gcp.retrieve_file_from_gcs(bucket_name, links_gcs_file_name, links_local_file_path)
    with open(links_local_file_path, "r", encoding="utf-8") as file:
        urls = [line.strip() for line in file]

    artworks_info = []
    failed_artworks = []
    batch_size = 200  # Number of artworks to store in each batch

    for url in urls:
        try:
            artwork_info = get_artwork_info(url)
            artworks_info.append(artwork_info)

            if len(artworks_info) % batch_size == 0:
                store_artworks_info_csv_in_gcs(artworks_info + existing_artworks_info, bucket_name, info_gcs_file_name)
                logging.info('Batch stored!')

        except Exception as e:
            logging.exception("Error occurred while extracting artwork info")
            failed_artworks.append({'url': url, 'error': str(e)})

    # Store any remaining artworks_info after the loop ends
    if artworks_info:
        store_artworks_info_csv_in_gcs(artworks_info + existing_artworks_info, bucket_name, info_gcs_file_name)
        logging.info('Remaining artworks stored!')

    # Store the failed_artworks_urls in GCS
    if failed_artworks:
        store_failed_urls_in_gcs(bucket_name, failed_urls_gcs_file_name, failed_artworks)

    return artworks_info, failed_artworks


def store_failed_urls_in_gcs(bucket_name, failed_urls_gcs_file_name, failed_artworks):
    # Check if the failed_urls_gcs_file_name file already exists
    if gcp.file_exists(bucket_name, failed_urls_gcs_file_name):
        # Download the existing file
        gcp.retrieve_file_from_gcs(bucket_name, failed_urls_gcs_file_name, "saatchi_failed_urls.csv")
        existing_urls = csv_handle.csv_to_list("saatchi_failed_urls.csv")

        # Append new URLs and error codes without duplicates
        for artwork in failed_artworks:
            url = artwork['url']
            error = artwork['error']
            if url not in existing_urls:
                existing_urls.append({'url': url, 'error': error})

        # Write the updated data to the CSV file
        csv_handle.list_to_csv(existing_urls, "saatchi_failed_urls.csv")
    else:
        # Create a new file and store the failed URLs
        csv_handle.list_to_csv([artwork['url'] for artwork in failed_artworks], "saatchi_failed_urls.csv")

    # Upload the file to GCS
    gcp.store_file_in_gcs(bucket_name, "saatchi_failed_urls.csv", failed_urls_gcs_file_name)
    os.remove("saatchi_failed_urls.csv")


def store_artworks_info_csv_in_gcs(artworks_info, bucket_name, info_gcs_file_name):
    info_local_file_path = info_gcs_file_name
    csv_handle.dict_list_to_csv(artworks_info, info_local_file_path)
    # Store the local file in GCS
    gcp.store_file_in_gcs(bucket_name, info_local_file_path, info_gcs_file_name)
    os.remove(info_local_file_path)
