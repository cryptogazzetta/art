from bs4 import BeautifulSoup
import requests
import json

# Get all the lots from an auction
def get_lots_from_auction(auction_link):
    url = auction_link + 'browse-lots?loadall=true'
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')

    # Extracting the json data from the page content
    # The first part of the JSON brings the params of an API call. We could use it instead
    data = str(soup).split('window.chrComponents.lots = ')[1].split('</script>')[0][:-7]
    json_data = json.loads(data)
    
    # Filling lots list with data from json
    lots = []
    for lot in json_data['data']['lots']:
        print(lot['title_primary_txt'])
        lots.append(lot)
    print(str(len(lots)) + " lots found")

    return lots


## Get all the auction links
# years: 1998-2023
def get_auctions_links(year_start, year_end):
    
    #Step 1. Generating first level urls, for month 1-12, year 1998-2023, possible page range: 1-3
    url_list=[]
    for i in range(1,13):
        for j in range (year_start, year_end):
            urll='http://www.christies.com/results/?month='+str(i)+'&year='+str(j)+'&locations=&scids=&action=paging&initialpageload=false'
            url_list.append(urll)
    print(str(len(url_list)) + " urls generated")

    #Step 2. Filling links list with all the auction links
    links=[]
    for url in url_list:
        try:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            # Data is in a script tag. We extract all scripts and then find the one with the data
            auctions = soup.find_all("a", class_="chr-event-tile__title")

            for auction in auctions:
                link = auction['href']
                links.append(auction['href'])
        except Exception as e:
            print(e)
            continue
    
    print(str(len(links)) + " auction links found")
    return links