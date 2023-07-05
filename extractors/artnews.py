# External modules
from bs4 import BeautifulSoup
import requests
from collections import defaultdict
from lxml import etree
# Project modules
import utils.string_handle as string_handle

user_agent = {'User-agent': 'Mozilla/5.0'}

topics = ['news', 'market', 'reviews', 'artists']

def get_articles(topic):
    base_url = 'https://www.artnews.com/c/art-news/'+topic+'/page/'
    
    articles_info = []
    page = 1
    while page <= 2:
        # Getting the dom object
        print('page', page)
        url = base_url + str(page)
        response = requests.get(url, headers=user_agent)
        soup = BeautifulSoup(response.text, "html.parser")

        article_cards = soup.find_all('div', class_='lrv-a-grid lrv-a-cols3')

        for article_card in article_cards:
            article_info = {}            
            title = article_card.find('a', class_='c-title__link lrv-a-unstyle-link u-color-brand-primary:hover')
            article_info['title'] = string_handle.remove_unicode(title.text)
            article_info['summary'] = article_card.find('p', class_='c-dek  lrv-u-font-weight-light lrv-u-font-size-16 lrv-u-font-size-18@desktop-xl a-hidden@mobile-max lrv-u-margin-a-00')
            article_info['href'] = title.get('href')
            article_info['timestamp'] = string_handle.remove_unicode(article_card.find('time').text)
            articles_info.append(article_info)

        # Check if it's the last page
        buttons = soup.find_all('span', class_='c-button__inner')
        buttons_text = [button.text.strip() for button in buttons]
        if (page==1 or 'Next' in buttons_text):
            page += 1
        else:
            print('last page')
            break
    
    return articles_info

# print(get_articles('news'))

url = 'https://www.artnews.com/c/art-news/news/'
response = requests.get(url, headers=user_agent)
soup = BeautifulSoup(response.text, "html.parser")
dom = etree.HTML(str(soup))

summary = dom.xpath('//p[@class="c-dek  lrv-u-font-weight-light lrv-u-font-size-16 lrv-u-font-size-18@desktop-xl a-hidden@mobile-max lrv-u-margin-a-00"]')
# summary = soup.find('p', class_='c-dek  lrv-u-font-weight-light lrv-u-font-size-16 lrv-u-font-size-18@desktop-xl a-hidden@mobile-max lrv-u-margin-a-00')
print(summary)