# Importing beatifulsoup
from bs4 import BeautifulSoup
import requests
from lxml import etree
import re
import pandas as pd

categories = ['Paintings', 'Photography', 'Drawings',
              'Sculpture', 'Digital', 'Prints']

category = categories[0]


# Aparentemente, há 250 páginas para iterar
def get_artworks_links(category, style):
    page = 1
    links = []
    already_in_list = []
    while True:
        print('page: ', page)
        saatchi_url = 'https://www.saatchiart.com'
        url = saatchi_url + '/' + category + '/' + style + '?hitsPerPage=100&page='+str(page)

        # Getting the dom object
        user_agent = {'User-agent': 'Mozilla/5.0'}
        response  = requests.get(url, headers = user_agent)
        soup = BeautifulSoup(response.text, "html.parser")
        dom = etree.HTML(str(soup))

        # Getting the links
        a_elements = dom.xpath('//div[@data-type="artwork-info"]/p/a')
        for a in a_elements:
            link = saatchi_url+a.attrib['href']
            links.append(link)

        # Getting the next page
        next_button = dom.xpath('//div[@data-section="pagination"]/a[@aria-label="Pagination next"]')[0]
        if next_button.attrib['rel'] == 'nofollow':
            break
        page += 1
        
    return links


def get_artwork_info(url):
    # Getting the dom object
    user_agent = {'User-agent': 'Mozilla/5.0'}
    response  = requests.get(url, headers = user_agent)
    soup = BeautifulSoup(response.text, "html.parser")
    dom = etree.HTML(str(soup))
    
    # Fill the artwork_info dictionary with the artwork information
    artwork_info = {}
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
        if info_value.text == None:
            value = ', '.join([element.text for element in info_value])
        else:
            value = info_value.text
        artwork_info[info_key.text.replace(':', '')] = value

    return artwork_info


def get_artworks_info(category):
    links = get_artworks_links(category)
    print('Artworks links collected: ', len(links))
    artworks_info = []
    for link in links:
        artworks_info.append(get_artwork_info(link))
    return artworks_info