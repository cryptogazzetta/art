# External modules
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import json
import logging
# Project modules
from utils import string_handle, csv_handle
from infra import gcp

url = 'https://www.saatchiart.com/javieraestrada'

def get_artist_info(url, driver):
    driver.get(url)

    artist_info ={}
    # Get basic info
    artist_info['name'] = driver.find_element(By.XPATH, '//h1[@data-type="user-name"]').text
    artist_info['link'] = url
    artist_info['location'] = driver.find_element(By.XPATH, '//p[@data-type="user-location"]').text
    artist_info['followers_count'] = string_handle.get_number(driver.find_element(By.XPATH, '//div[@data-type="user-following"]/span[@data-type="count"]').text)
    artist_info['artworks_count'] = string_handle.get_number(driver.find_element(By.XPATH, '//a[@data-type="view-artwork-button"]').text)
    try_view_more_button(driver, '//div[@data-type="badges"]/button[@data-type="view-more-button"]')
    badges_elements = driver.find_elements(By.XPATH, '//div[@data-type="badge"]/p[@data-type="title"]')
    artist_info['badges'] = [badge_element.text for badge_element in badges_elements]
    # Get data from about section (info, education, exhibitions)
    about_nav_tabs = driver.find_elements(By.XPATH, '//ul[@data-type="nav-tabs"]/li')
    for nav_tab in about_nav_tabs:
        nav_tab.find_element(By.XPATH, '//button[@data-type="nav-tab"]').click()
        try_view_more_button(driver, '//div[@data-type="info"]/button[@data-type="view-more-button"]')
        tab_content = driver.find_element(By.XPATH, '//p[@data-type="info-text"]').text
        artist_info[nav_tab.text] = tab_content

    return artist_info


def get_all_artists_info(bucket_name, gcs_artists_info_name, gcs_artworks_info_name):
    local_artworks_info_path = gcs_artworks_info_name
    gcp.retrieve_file_from_gcs(bucket_name, gcs_artworks_info_name, local_artworks_info_path)
    df = pd.read_csv(local_artworks_info_path)
    artist_links = list(set(df['artist_link'].tolist()))

    driver = webdriver.Chrome()

    artists_info = []
    for artist_link in artist_links[:200]:
        try:
            artist_info = get_artist_info(artist_link, driver)
            artists_info.append(artist_info)
        except:
            logging.exception(f"Error getting artist info from {artist_link}")

    driver.quit()

    # Store the list of dictionaries as a JSON file
    artists_info_json = json.dumps(artists_info)
    store_string_as_file_in_gcs(bucket_name, gcs_artists_info_name, artists_info_json)


def store_string_as_file_in_gcs(bucket_name, gcs_file_name, string):
    local_file_path = gcs_file_name
    with open(local_file_path, "w", encoding="utf-8") as file:
        file.write(string)
    gcp.store_file_in_gcs(bucket_name, gcs_file_name, local_file_path)


def try_view_more_button(driver, button_xpath):
    try:
        driver.find_element(By.XPATH, button_xpath).click()
    except Exception as e:
        logging.exception(f"Error occurred while clicking 'view more' button in {button_xpath}")