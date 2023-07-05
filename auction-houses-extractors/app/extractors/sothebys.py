from bs4 import BeautifulSoup
import requests
import logging


SOTHEBYS_POST_DATA = {
        'email': "christian@fynt.io",
        'password': "t#3u!%h9Up!JSZb"
}

LOGIN_URL = "https://accounts.sothebys.com/login?state=hKFo2SBDMDAyRy1OM3hJMHZlVTFsYnh0ZWRmS3ZidHF6a2Rob6FupWxvZ2luo3RpZNkgVGRETllveV9UaER6c3g1UU9IbFZCU1NpSXpEb2xVN1ajY2lk2SBNMGVnaDhwOE5zd2RHTTZYNTNqcDEyOGEyYlRPSE4yRQ&client=M0egh8p8NswdGM6X53jp128a2bTOHN2E&protocol=oauth2&audience=https%3A%2F%2Fcustomer.api.sothebys.com&language=en&redirect_uri=https%3A%2F%2Fwww.sothebys.com%2Fapi%2Fauth0callback%3Flanguage%3Den%26resource%3DfromHeader%26src%3D&response_type=code&scope=openid%20email%20offline_access&ui_locales=en"

# with requests.Session() as s:
    # LOG IN TO SOTHEBY'S
    # result = s.post(LOGIN_URL, data = SOTHEBYS_POST_DATA, headers = dict(referer = LOGIN_URL))
    # print('logged in successfully')

url = "https://www.sothebys.com/" # en/artists/jean-michel-basquiat"
print('getting the page')
result = requests.get(url)
print('got the page')
result = BeautifulSoup(result.content, 'html.parser')
print(result.h1())
