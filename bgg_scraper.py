import csv
from bs4 import BeautifulSoup
import numpy as np
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
try:
    from googlesearch import search
except ImportError:
    print("No module named 'google' found")
from class_boardgames import Boardgames


#initialize necessary parameters
flag = int(input('How many board games do you want to retrieve from the list? '))
count, count_page, url_count, page = 0, 0, 0, 0
n_pages = flag//100 + 1
url = []
url.append('https://boardgamegeek.com/browse/boardgame/page/'+str(page+1)+'?sort=rank')

#write csv file    
f = open('Board_games.csv', 'w', encoding='UTF8', newline='')
header = ['Name', 'Board game url', 'BGG Rating', 'User rating', 'Total reviews', 'Max # players', 
     'Optimal # players', 'Min playing time', 'Max playing time', 'Minimum age', 'Weight/5', 'Min price', 'Skroutz url']
wr = csv.writer(f)
wr.writerow(header)

while count < flag:
    #retrieve the corresponding page from bgg site; each page contains 100 games
    if count//100 > page:
        page = page + 1
        url.append('https://boardgamegeek.com/browse/boardgame/page/'+str(page+1)+'?sort=rank')
        count_page = count_page%100

    html = requests.get(url[page])
    soup = BeautifulSoup(html.content, 'html.parser')
    results = soup('tr')[1:] #ignore the first entry

    #-----------retrieve data for each board game----------------------
    game_name = results[count_page].find(class_ = 'primary').text
    #get the shop url
    init_url = results[count_page].find(class_ = 'primary')['href']
    bgg_url = 'https://boardgamegeek.com'+ init_url
    #
    #get the rating of each game
    res_ratings = results[count_page].find_all(class_ = 'collection_bggrating')
    bgg_rating = float(res_ratings[0].text.split()[0])
    user_rating = float(res_ratings[1].text.split()[0])
    votes = int(res_ratings[2].text.split()[0])
    #
    #open bgg_url and retrieve extra attributes
    p = Boardgames(bgg_url)
    max_p = p._maxplayers()
    opt_p = p._players()
    min_t, max_t = p._playingtime()
    minage = p._minage()
    dif = p._weight()
    #
    #Perform a google search
    query = f'{game_name}' + ' ' + 'skroutz'
    try:
        first_option = True
        for web_url in search(query, tld="co.in", num=2, stop=2, pause=2):
            if 'keyphrase' not in web_url and first_option == True:
                first_option = False
                skroutz_url = web_url
                
        #get the corresponding price from skroutz.gr
        driver = webdriver.Chrome()
        driver.get(skroutz_url)
        html = requests.get(skroutz_url)
        price = driver.find_element(By.CLASS_NAME, 'dominant-price').text.split()[0].replace(',' , '.')        
    except:
        price = '-'
        skroutz_url = '-'
    #-----------------------------------------------------------------------
        
    #------------------Print the results in the csv file--------------------
    wr.writerow([game_name, bgg_url, bgg_rating, user_rating, votes, max_p,
    opt_p, min_t, max_t, minage, dif, price, skroutz_url])    
    #----------------------------------------------------------------------  
    
    count += 1
    count_page += 1



